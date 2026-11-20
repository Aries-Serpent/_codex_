"""Persistent, idempotent execution state for Cognitive Brain routes."""

from __future__ import annotations

import hashlib
import json
import sqlite3
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
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA busy_timeout=10000")
        return connection

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
                    operation_id, idempotency_key, request_digest, state
                ) VALUES (?, ?, ?, 'executing')
                """,
                (claim.operation_id, claim.idempotency_key, claim.request_digest),
            )
        return claim

    def _finish(self, claim: RouteExecutionClaim, *, result: Any = None, error: str = "") -> None:
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(
                """
                UPDATE route_operations
                SET state = ?, result_json = ?, error = ?, updated_at = CURRENT_TIMESTAMP
                WHERE operation_id = ? AND state = 'executing'
                """,
                (
                    "completed" if not error else "failed",
                    json.dumps(result, allow_nan=False) if not error else None,
                    error,
                    claim.operation_id,
                ),
            )

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
