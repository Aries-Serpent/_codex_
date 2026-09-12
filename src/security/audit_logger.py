"""
Tamper-Evident Audit Logger

Implements a simple hash-chained NDJSON audit log:
Each event includes the SHA256 of the previous record to detect tampering.
"""

from __future__ import annotations

import hashlib
import json
import time
from collections.abc import Collection
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from codex_contracts import ContractValidationError, EventEnvelope

ACCEPTED_EVENT_SCHEMA_VERSIONS = frozenset({"1.0"})
_AUDIT_EVENT_KIND = "security.audit"
_AUDIT_EVENT_SOURCE = "security.audit_logger"
_ENVELOPE_MARKER_FIELDS = frozenset({"schema_version", "kind", "source", "payload"})


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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

    def _last_hash(self) -> str:
        if not self.path.exists():
            return "0" * 64
        lines = [ln for ln in self.path.read_text(encoding="utf-8").splitlines() if ln.strip()]
        if not lines:
            return "0" * 64
        last = json.loads(lines[-1])
        value = last.get("hash")
        return value if isinstance(value, str) else "0" * 64

    def append(self, event: dict[str, Any], *, ts: float | None = None) -> dict[str, Any]:
        prev = self._last_hash()
        event_ts = float(ts if ts is not None else time.time())
        envelope = EventEnvelope(
            kind=_AUDIT_EVENT_KIND,
            source=_AUDIT_EVENT_SOURCE,
            payload=event,
            emitted_at=datetime.fromtimestamp(event_ts, tz=timezone.utc).isoformat().replace(
                "+00:00", "Z"
            ),
        )
        payload: dict[str, Any] = {
            "ts": event_ts,
            "event": json.loads(envelope.to_json()),
            "prev_hash": prev,
        }
        record_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
        digest = _sha256_bytes(record_bytes)
        payload["hash"] = digest
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(payload, sort_keys=True) + "\n")
        return payload

    def verify_chain(self) -> bool:
        if not self.path.exists():
            return True
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
                json.dumps({k: rec[k] for k in rec if k != "hash"}, sort_keys=True).encode("utf-8")
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
                try:
                    EventEnvelope.from_json(
                        json.dumps(event),
                        accepted_versions=self.accepted_event_versions,
                    )
                except (ContractValidationError, TypeError, ValueError):
                    return False
            prev = hash_value
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
