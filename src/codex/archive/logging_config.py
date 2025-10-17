"""Structured logging helpers used by archive commands."""

from __future__ import annotations

import json
import logging
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

from .config import LoggingConfig, PerformanceConfig
from .perf import TimingMetrics
from .util import append_evidence, redact_text_credentials

ISO_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
_STANDARD_FIELDS = {
    "name",
    "msg",
    "args",
    "levelname",
    "levelno",
    "pathname",
    "filename",
    "module",
    "exc_info",
    "exc_text",
    "stack_info",
    "lineno",
    "funcName",
    "created",
    "msecs",
    "relativeCreated",
    "thread",
    "threadName",
    "processName",
    "process",
}


@dataclass(slots=True)
class StructuredLogRecord:
    """Structured representation of a log record."""

    level: str
    message: str
    timestamp: str
    component: str
    extra: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "level": self.level,
            "message": self.message,
            "timestamp": self.timestamp,
            "component": self.component,
        }
        payload.update(self.extra)
        return payload

    def to_json(self) -> str:
        payload = {
            "level": self.level,
            "message": self.message,
            "timestamp": self.timestamp,
            "component": self.component,
            "extra": self.extra,
        }
        return json.dumps(payload, sort_keys=True)

    def to_text(self) -> str:
        extras = " ".join(f"{key}={value}" for key, value in sorted(self.extra.items()))
        if extras:
            return f"[{self.level}] {self.message} -- {extras}"
        return f"[{self.level}] {self.message}"


class StructuredFormatter(logging.Formatter):
    """Formatter that produces JSON or text payloads."""

    def __init__(self, *, fmt: str = "json", component: str = "archive") -> None:
        super().__init__()
        self.format_mode = fmt
        self.component = component

    def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        message = record.getMessage()
        timestamp = datetime.utcfromtimestamp(record.created).strftime(ISO_FORMAT)
        extra_fields = {k: getattr(record, k) for k in record.__dict__ if k not in _STANDARD_FIELDS}
        flattened_extra = dict(extra_fields)
        extra_payload = flattened_extra.pop("extra_fields", None)
        if isinstance(extra_payload, dict):
            flattened_extra.update(extra_payload)

        payload = StructuredLogRecord(
            level=record.levelname,
            message=message,
            timestamp=timestamp,
            component=self.component,
            extra=flattened_extra,
        )
        if self.format_mode == "json":
            return payload.to_json()
        return payload.to_text()


def setup_logging(
    config: LoggingConfig,
    *,
    logger_name: str = "codex.archive",
    stream: Any | None = None,
) -> logging.Logger:
    """Initialise a structured logger according to *config*."""

    logger = logging.getLogger(logger_name)
    level = getattr(logging, config.level.upper(), logging.INFO)
    logger.setLevel(level)
    handler = logging.StreamHandler(stream or sys.stderr)
    handler.setFormatter(StructuredFormatter(fmt=config.format, component=logger_name))
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def log_restore(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.utcnow().strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def export_configuration(config: LoggingConfig) -> dict[str, Any]:
    """Return a JSON serialisable representation of *config*."""

    payload = asdict(config)
    if config.evidence_file is not None:
        payload["evidence_file"] = str(config.evidence_file)
    return payload
