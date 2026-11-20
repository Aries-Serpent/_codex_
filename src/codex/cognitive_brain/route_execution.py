"""Persistent, idempotent execution state for Cognitive Brain routes."""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Literal, Mapping


class RouteExecutionConflict(RuntimeError):
    """Raised when a route cannot be safely executed or replayed."""


@dataclass(frozen=True, slots=True)
class RouteExecutionResult:
    """Durable result returned for a first execution or replay."""

    operation_id: str
    request_digest: str
    idempotency_key: str
    state: str
    result: Any
    replayed: bool


@dataclass(frozen=True, slots=True)
class RouteExecutionClaim:
    operation_id: str
    request_digest: str
    idempotency_key: str
    state: Literal["claimed", "replayed"] = "claimed"
    result: Any = None


class RouteExecutionStore:
    """SQLite-backed idempotency and reconciliation ledger for route execution."""

    def __init__(self, path: Path):
        self.path = path
        self.owner_id = uuid.uuid4().hex
        self.owner_pid = os.getpid()
        self.owner_start = self._process_start(self.owner_pid)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS route_operations (
                    operation_id TEXT PRIMARY KEY,
                    idempotency_key TEXT NOT NULL UNIQUE,
                    request_digest TEXT NOT NULL,
                    state TEXT NOT NULL,
                    result_json TEXT,
                    error TEXT,
                    owner_id TEXT,
                    owner_pid INTEGER,
                    owner_start TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """)
            columns = {
                row["name"] for row in connection.execute("PRAGMA table_info(route_operations)")
            }
            for name, declaration in (
                ("owner_id", "TEXT"),
                ("owner_pid", "INTEGER"),
                ("owner_start", "TEXT"),
            ):
                if name not in columns:
                    connection.execute(
                        f"ALTER TABLE route_operations ADD COLUMN {name} {declaration}"
                    )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA busy_timeout=10000")
        return connection

    @staticmethod
    def _process_start(pid: int) -> str:
        try:
            return Path(f"/proc/{pid}/stat").read_text(encoding="utf-8").split()[21]
        except (IndexError, OSError):
            return ""

    @classmethod
    def _owner_is_live(cls, row: Mapping[str, Any]) -> bool:
        try:
            owner_pid = row["owner_pid"]
            owner_start = row["owner_start"]
        except (KeyError, IndexError):
            return False
        if owner_pid is None or not owner_start:
            return False
        return cls._process_start(int(owner_pid)) == str(owner_start)

    @staticmethod
    def _canonical_request(request: Mapping[str, Any]) -> str:
        return json.dumps(request, sort_keys=True, separators=(",", ":"), allow_nan=False)

    @classmethod
    def request_digest(cls, request: Mapping[str, Any]) -> str:
        canonical = cls._canonical_request(request)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    @classmethod
    def claim_payload(cls, request: Mapping[str, Any]) -> RouteExecutionClaim:
        idempotency_key = str(request.get("idempotency_key", "")).strip()
        if not idempotency_key or len(idempotency_key) > 256:
            raise RouteExecutionConflict(
                "idempotency_key is required and must be <= 256 characters"
            )
        digest = cls.request_digest(request)
        return RouteExecutionClaim(
            operation_id=hashlib.sha256(f"{idempotency_key}:{digest}".encode()).hexdigest(),
            request_digest=digest,
            idempotency_key=idempotency_key,
        )

    def prepare(self, request: Mapping[str, Any]) -> RouteExecutionClaim:
        """Atomically claim a request or return its completed replay outcome."""
        claim = self.claim_payload(request)
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            existing = connection.execute(
                "SELECT * FROM route_operations WHERE idempotency_key = ?",
                (claim.idempotency_key,),
            ).fetchone()
            if existing is not None:
                if existing["request_digest"] != claim.request_digest:
                    raise RouteExecutionConflict(
                        "idempotency key already refers to a different request"
                    )
                if existing["state"] == "completed":
                    return RouteExecutionClaim(
                        operation_id=claim.operation_id,
                        request_digest=claim.request_digest,
                        idempotency_key=claim.idempotency_key,
                        state="replayed",
                        result=json.loads(existing["result_json"]),
                    )
                if existing["state"] == "failed":
                    raise RouteExecutionConflict("execution previously failed and requires review")
                raise RouteExecutionConflict("incomplete execution requires reconciliation")

            connection.execute(
                """
                INSERT INTO route_operations (
                    operation_id, idempotency_key, request_digest, state,
                    owner_id, owner_pid, owner_start
                ) VALUES (?, ?, ?, 'executing', ?, ?, ?)
                """,
                (
                    claim.operation_id,
                    claim.idempotency_key,
                    claim.request_digest,
                    self.owner_id,
                    self.owner_pid,
                    self.owner_start,
                ),
            )
        return claim

    def _finish(self, claim: RouteExecutionClaim, *, result: Any = None, error: str = "") -> None:
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            cursor = connection.execute(
                """
                UPDATE route_operations
                SET state = ?, result_json = ?, error = ?, updated_at = CURRENT_TIMESTAMP
                WHERE operation_id = ? AND state = 'executing' AND owner_id = ?
                """,
                (
                    "completed" if not error else "failed",
                    json.dumps(result, allow_nan=False) if not error else None,
                    error,
                    claim.operation_id,
                    self.owner_id,
                ),
            )
            if cursor.rowcount != 1:
                raise RouteExecutionConflict("operation finalization lost ownership")

    def incomplete_operations(self) -> list[dict[str, Any]]:
        """Return executing operations that require external-state reconciliation."""
        with self._connect() as connection:
            rows = connection.execute("""
                SELECT operation_id, idempotency_key, request_digest, state,
                       owner_id, owner_pid, owner_start, created_at, updated_at
                FROM route_operations
                WHERE state = 'executing'
                ORDER BY created_at, operation_id
                """).fetchall()
        public_fields = (
            "operation_id",
            "idempotency_key",
            "request_digest",
            "state",
            "created_at",
            "updated_at",
        )
        return [
            {field: row[field] for field in public_fields}
            for row in rows
            if not self._owner_is_live(row)
        ]

    def reconcile(self, operation_id: str, *, result: Any = None, error: str = "") -> None:
        """Resolve one interrupted operation only after its outcome is verified."""
        if not operation_id or (result is None and not error):
            raise RouteExecutionConflict("reconciliation requires a result or error")
        try:
            result_json = json.dumps(result, allow_nan=False) if not error else None
        except (TypeError, ValueError) as exc:
            raise RouteExecutionConflict("reconciliation result must be JSON serializable") from exc
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            current = connection.execute(
                "SELECT * FROM route_operations WHERE operation_id = ?",
                (operation_id,),
            ).fetchone()
            if current is None or current["state"] != "executing":
                raise RouteExecutionConflict("operation is not awaiting reconciliation")
            if self._owner_is_live(current):
                raise RouteExecutionConflict("operation is still owned by a live executor")
            cursor = connection.execute(
                """
                UPDATE route_operations
                SET state = ?, result_json = ?, error = ?, updated_at = CURRENT_TIMESTAMP
                WHERE operation_id = ? AND state = 'executing'
                """,
                (
                    "completed" if not error else "failed",
                    result_json,
                    error,
                    operation_id,
                ),
            )
            if cursor.rowcount != 1:
                raise RouteExecutionConflict("operation is not awaiting reconciliation")

    def execute(
        self,
        request: Mapping[str, Any],
        operation: Callable[[], Any],
    ) -> RouteExecutionResult:
        """Run one operation atomically by idempotency key or replay its result."""
        claim = self.prepare(request)
        if claim.state == "replayed":
            return RouteExecutionResult(
                operation_id=claim.operation_id,
                request_digest=claim.request_digest,
                idempotency_key=claim.idempotency_key,
                state="completed",
                result=claim.result,
                replayed=True,
            )

        try:
            result = operation()
        except Exception as exc:
            self._finish(claim, error=f"{type(exc).__name__}: {exc}")
            raise RouteExecutionConflict("execution failed and was recorded") from exc

        self._finish(claim, result=result)
        return RouteExecutionResult(
            operation_id=claim.operation_id,
            request_digest=claim.request_digest,
            idempotency_key=claim.idempotency_key,
            state="completed",
            result=result,
            replayed=False,
        )


__all__ = [
    "RouteExecutionClaim",
    "RouteExecutionConflict",
    "RouteExecutionResult",
    "RouteExecutionStore",
]
