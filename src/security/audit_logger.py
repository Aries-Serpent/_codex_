"""
Tamper-Evident Audit Logger

Implements a simple hash-chained NDJSON audit log:
Each event includes the SHA256 of the previous record to detect tampering.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from collections.abc import Collection
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from codex_contracts import ContractValidationError, EventEnvelope

ACCEPTED_EVENT_SCHEMA_VERSIONS = frozenset({"1.0"})
_AUDIT_EVENT_KIND = "security.audit"
_AUDIT_EVENT_SOURCE = "security.audit_logger"
_ENVELOPE_MARKER_FIELDS = frozenset({"schema_version", "kind", "source", "payload"})


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@contextmanager
def _locked(lock_path: Path, *, exclusive: bool) -> Iterator[None]:
    """Hold a cross-process lock for an audit-log operation."""
    fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
    with os.fdopen(fd, "r+b", buffering=0) as lock_file:
        if os.name == "nt":
            import msvcrt

            lock_file.seek(0, os.SEEK_END)
            if lock_file.tell() == 0:
                lock_file.write(b"\0")
            lock_file.seek(0)
            msvcrt.locking(  # type: ignore[attr-defined]
                lock_file.fileno(),
                msvcrt.LK_LOCK,  # type: ignore[attr-defined]
                1,
            )
        else:
            import fcntl

            operation = fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH
            fcntl.flock(lock_file.fileno(), operation)
        try:
            yield
        finally:
            if os.name == "nt":
                lock_file.seek(0)
                msvcrt.locking(  # type: ignore[attr-defined]
                    lock_file.fileno(),
                    msvcrt.LK_UNLCK,  # type: ignore[attr-defined]
                    1,
                )
            else:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


@dataclass
class AuditLogger:
    path: Path

    def __init__(
        self,
        path: Path | None = None,
        log_dir: Path | None = None,
        *,
        accepted_event_versions: Collection[str] = ACCEPTED_EVENT_SCHEMA_VERSIONS,
    ):
        """Initialize audit logger with path or log_dir.

        Args:
            path: Direct path to log file (takes precedence)
            log_dir: Directory for audit logs (creates audit.log inside)
            accepted_event_versions: Envelope schema versions this reader accepts.
        """
        if isinstance(accepted_event_versions, (str, bytes)) or not accepted_event_versions:
            raise ValueError("accepted_event_versions must be a non-empty collection")
        self.accepted_event_versions = frozenset(accepted_event_versions)
        if path is not None:
            self.path = path
        elif log_dir is not None:
            self.path = log_dir / "audit.log"
        else:
            self.path = Path("logs/audit/audit.log")

    @property
    def _lock_path(self) -> Path:
        return self.path.with_name(f".{self.path.name}.lock")

    def log_event(self, event_type: str, resource: str, action: str, user: str) -> None:
        """Log a security audit event.

        Args:
            event_type: Type of security event
            resource: Resource being accessed
            action: Action performed
            user: User performing action
        """
        log_entry = {
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "event_type": event_type,
            "resource": resource,
            "action": action,
            "user": user,
        }
        self.append(log_entry)

    def _last_hash_unlocked(self) -> str:
        if not self.path.exists():
            return "0" * 64
        lines = [ln for ln in self.path.read_text(encoding="utf-8").splitlines() if ln.strip()]
        if not lines:
            return "0" * 64
        last = json.loads(lines[-1])
        value = last.get("hash")
        return value if isinstance(value, str) else "0" * 64

    def _last_hash(self) -> str:
        if not self.path.exists():
            return "0" * 64
        with _locked(self._lock_path, exclusive=False):
            return self._last_hash_unlocked()

    def append(self, event: dict[str, Any], *, ts: float | None = None) -> dict[str, Any]:
        event_ts = float(ts if ts is not None else time.time())
        envelope = EventEnvelope(
            kind=_AUDIT_EVENT_KIND,
            source=_AUDIT_EVENT_SOURCE,
            payload=event,
            emitted_at=datetime.fromtimestamp(event_ts, tz=timezone.utc).isoformat().replace(
                "+00:00", "Z"
            ),
        )
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with _locked(self._lock_path, exclusive=True):
            prev = self._last_hash_unlocked()
            payload: dict[str, Any] = {
                "ts": event_ts,
                "event": json.loads(envelope.to_json()),
                "prev_hash": prev,
            }
            record_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
            payload["hash"] = _sha256_bytes(record_bytes)
            line = json.dumps(payload, sort_keys=True).encode("utf-8") + b"\n"

            fd = os.open(self.path, os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o600)
            try:
                remaining = memoryview(line)
                while remaining:
                    written = os.write(fd, remaining)
                    if written == 0:
                        raise OSError("audit-log write made no progress")
                    remaining = remaining[written:]
                os.fsync(fd)
            finally:
                os.close(fd)
        return payload

    def verify_chain(self) -> bool:
        if not self.path.exists():
            return True
        try:
            with _locked(self._lock_path, exclusive=False):
                prev = "0" * 64
                for line in self.path.read_text(encoding="utf-8").splitlines():
                    if not line.strip():
                        continue
                    rec = json.loads(line)
                    if not isinstance(rec, dict):
                        return False
                    expected_prev = prev
                    if rec.get("prev_hash") != expected_prev:
                        return False
                    computed = _sha256_bytes(
                        json.dumps(
                            {k: rec[k] for k in rec if k != "hash"}, sort_keys=True
                        ).encode("utf-8")
                    )
                    hash_value = rec.get("hash")
                    if not isinstance(hash_value, str) or hash_value != computed:
                        return False
                    event = rec.get("event")
                    if not isinstance(event, dict):
                        return False
                    # A legacy payload may itself contain a ``schema_version`` key. Treat
                    # the record as an envelope only when the contract framing fields
                    # are present, then let EventEnvelope enforce its closed field set.
                    if _ENVELOPE_MARKER_FIELDS.issubset(event):
                        EventEnvelope.from_json(
                            json.dumps(event),
                            accepted_versions=self.accepted_event_versions,
                        )
                    prev = hash_value
        except (
            ContractValidationError,
            json.JSONDecodeError,
            KeyError,
            TypeError,
            UnicodeError,
            ValueError,
        ):
            return False
        return True


def log_audit_event(
    event_type: str,
    user: str,
    action: str,
    success: bool = True,
    log_dir: Path | None = None,
) -> None:
    """Helper function to log a structured audit event to file-based hash chain.

    This function logs security-relevant events to a file-based audit trail with
    hash chain integrity verification. For simple logger-based event logging,
    use src.security.core.log_security_event instead.

    Args:
        event_type: Type of security event (e.g., 'authentication')
        user: User performing the action
        action: Action performed (e.g., 'login')
        success: Whether the action was successful
        log_dir: Directory to store logs (optional)
    """
    logger = AuditLogger(log_dir=log_dir)
    event = {
        "type": event_type,
        "user": user,
        "action": action,
        "success": success,
    }
    logger.append(event)
