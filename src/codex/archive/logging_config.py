"""Structured logging configuration for archive operations."""
from __future__ import annotations

import json
import logging
import logging.handlers
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from .util import redact_url_credentials


@dataclass
class StructuredLogRecord:
    """Structured log record with metadata."""

    timestamp: str
    level: str
    action: str
    actor: str | None = None
    tombstone: str | None = None
    reason: str | None = None
    duration_ms: float | None = None
    backend: str | None = None
    url: str | None = None
    error: str | None = None
    extra: dict[str, Any] | None = None

    def to_json(self) -> str:
        """Convert to JSON string."""

        return json.dumps(self.to_dict(), sort_keys=True)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""

        record: dict[str, Any] = {
            "ts": self.timestamp,
            "level": self.level,
            "action": self.action,
        }
        if self.actor:
            record["actor"] = self.actor
        if self.tombstone:
            record["tombstone"] = self.tombstone
        if self.reason:
            record["reason"] = self.reason
        if self.duration_ms is not None:
            record["duration_ms"] = self.duration_ms
        if self.backend:
            record["backend"] = self.backend
        if self.url:
            record["url"] = self.url
        if self.error:
            record["error"] = self.error
        if self.extra:
            record.update(self.extra)
        return record


class StructuredFormatter(logging.Formatter):
    """Formatter for structured logging."""

    def __init__(self, format_type: Literal["json", "text"] = "json") -> None:
        super().__init__()
        self.format_type = format_type

    def format(self, record: logging.LogRecord) -> str:  # noqa: D401 - inherited docstring
        if self.format_type == "json":
            try:
                structured = StructuredLogRecord(
                    timestamp=datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
                    level=record.levelname.lower(),
                    action=record.getMessage(),
                    extra=getattr(record, "extra_fields", None),
                )
                return structured.to_json()
            except Exception:  # pragma: no cover - fallback path
                return super().format(record)
        timestamp = datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat()
        return f"[{timestamp}] {record.levelname:6s} {record.getMessage()}"


def setup_logging(
    level: Literal["debug", "info", "warn", "error"] = "info",
    format_type: Literal["json", "text"] = "json",
    log_file: str | None = None,
) -> logging.Logger:
    """Setup structured logging for archive operations."""

    logger = logging.getLogger("codex.archive")
    logger.setLevel(getattr(logging, level.upper()))
    logger.handlers.clear()

    formatter = StructuredFormatter(format_type=format_type)

    stream_handler = logging.StreamHandler(sys.stderr)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def log_restore(
    logger: logging.Logger,
    action: str,
    tombstone: str,
    actor: str,
    duration_ms: float | None = None,
    backend: str | None = None,
    url: str | None = None,
    error: str | None = None,
    reason: str | None = None,
) -> None:
    """Log a restore operation with structured context."""

    record = StructuredLogRecord(
        timestamp=datetime.now(tz=timezone.utc).isoformat(),
        level="error" if error or reason else "info",
        action=action,
        actor=actor,
        tombstone=tombstone,
        duration_ms=duration_ms,
        backend=backend,
        url=redact_url_credentials(url) if url else None,
        error=error,
        reason=reason,
    )
    if record.level == "error":
        logger.error(action)
    else:
        logger.info(action)
