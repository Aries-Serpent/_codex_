"""
Session Logger Module

This module provides functionality for session logger.

Usage:
    from logging.session_logger import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


import json  # noqa: E402
import os  # noqa: E402
import uuid  # noqa: E402
from collections.abc import Iterable, Mapping  # noqa: E402
from datetime import datetime, timedelta, timezone  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Any  # noqa: E402

from codex_ml.safety.redaction import SecretRedactor  # noqa: E402

DEFAULT_LOG_DIR = Path(".codex") / "logs"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class SessionLogger:
    """Structured NDJSON logger that annotates records with a session id."""

    def __init__(
        self,
        session_id: str | None = None,
        log_dir: Path | None = None,
        *,
        redactor: SecretRedactor | None = None,
        retention_days: int | None = None,
        max_history_files: int = 50,
    ) -> None:
        self.session_id = session_id or str(uuid.uuid4())
        self.log_dir = (log_dir or DEFAULT_LOG_DIR).expanduser()
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.session_file = self.log_dir / f"session_{self.session_id}.jsonl"
        self._redactor = redactor or SecretRedactor()
        self.retention_days = retention_days
        self.max_history_files = max_history_files
        self._prune_old_logs()

    def log_event(
        self,
        event_type: str,
        data: Mapping[str, Any] | None = None,
        *,
        role: str = "system",
    ) -> Path:
        payload: dict[str, Any] = {
            "timestamp": _utc_now(),
            "session_id": self.session_id,
            "role": role,
            "event_type": event_type,
        }
        if data:
            payload["data"] = self._redactor.redact_dict(dict(data))
        with self.session_file.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
        return self.session_file

    def log_error(
        self,
        error: Exception | str,
        *,
        context: Mapping[str, Any] | None = None,
        role: str = "system",
    ) -> Path:
        """Capture rich error context for self-correction workflows."""

        message = str(error)
        error_type = error.__class__.__name__ if isinstance(error, Exception) else "message"
        payload: dict[str, Any] = {"error_type": error_type, "message": message}
        if context:
            payload["context"] = self._redactor.redact_dict(dict(context))
        return self.log_event("error", payload, role=role)

    def _prune_old_logs(self) -> list[Path]:
        """Best-effort retention control to limit log bloat."""

        removed: list[Path] = []
        if not self.log_dir.exists():
            return removed

        retention_days = self.retention_days
        if retention_days is None:
            env_retention = os.getenv("CODEX_LOG_RETENTION_DAYS")
            if env_retention and env_retention.isdigit():
                retention_days = int(env_retention)
        cutoff: datetime | None = None
        if retention_days:
            cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)

        files = sorted(
            self.log_dir.glob("session_*.jsonl"),
            key=lambda p: p.stat().st_mtime,
        )
        to_remove: list[Path] = []
        if cutoff:
            for path in files:
                mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
                if mtime < cutoff:
                    to_remove.append(path)

        if len(files) - len(to_remove) > self.max_history_files:
            overflow = (len(files) - len(to_remove)) - self.max_history_files
            survivors = [p for p in files if p not in to_remove]
            to_remove.extend(survivors[:overflow])

        for path in to_remove:
            try:
                path.unlink()
                removed.append(path)
            except OSError as e:
                type(e).__name__
                logger.debug("OSError: <ERROR_TYPE>")
                logger.warning("OSError: <ERROR_TYPE>", exc_info=True)
                continue

        return removed

    def iter_events(self) -> Iterable[dict[str, Any]]:
        """Yield parsed events for downstream analyzers (best effort)."""

        if not self.session_file.exists():
            return
        with self.session_file.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    logger.debug("Exception caught, continuing", exc_info=True)
                    continue


__all__ = ["DEFAULT_LOG_DIR", "SessionLogger"]
