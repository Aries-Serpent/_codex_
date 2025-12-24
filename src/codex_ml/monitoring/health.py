"""Health-event logging helpers for offline regression monitoring."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Mapping, MutableMapping

from pydantic import BaseModel

__all__ = [
    "record_health_event",
    "health_log_path",
    "HEALTH_LOG_ENV",
    "DEFAULT_HEALTH_DIR",
    "HealthChecker",
    "HealthReport",
    "HealthStatus",
]

HEALTH_LOG_ENV = "CODEX_HEALTH_LOG_DIR"
DEFAULT_HEALTH_DIR = Path(".codex") / "health"

logger = logging.getLogger(__name__)


def _now() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _normalize(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(k): _normalize(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_normalize(v) for v in value]
    if isinstance(value, Path):
        return str(value)
    return value


def health_log_path(component: str) -> Path:
    root = os.getenv(HEALTH_LOG_ENV)
    candidates: list[Path] = []
    if root:
        candidates.append(Path(root).expanduser())
    if not candidates or candidates[-1] != DEFAULT_HEALTH_DIR:
        candidates.append(DEFAULT_HEALTH_DIR)

    safe_name = component.replace("/", "-")
    destination: Path | None = None
    last_error: tuple[Path, OSError] | None = None

    for base in candidates:
        destination = base / f"{safe_name}.ndjson"
        try:
            base.mkdir(parents=True, exist_ok=True)
        except OSError as exc:  # pragma: no cover - exercised in hostile fs envs
            last_error = (base, exc)
            continue
        else:
            return destination

    if last_error:
        base, exc = last_error
        logger.debug("Unable to prepare health log directory %s: %s", base, exc)
    return destination if destination is not None else DEFAULT_HEALTH_DIR / f"{safe_name}.ndjson"


def record_health_event(
    component: str,
    event: str,
    *,
    details: Mapping[str, Any] | None = None,
) -> Path:
    """Append a structured health record for ``component`` and return the log path."""

    payload: MutableMapping[str, Any] = {
        "timestamp": _now(),
        "component": component,
        "event": event,
    }
    if details:
        payload["details"] = _normalize(details)
    destination = health_log_path(component)
    try:
        with destination.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True) + "\n")
    except OSError as exc:  # pragma: no cover - exercised in hostile fs envs
        logger.debug("Unable to write health log to %s: %s", destination, exc)
    return destination


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthReport(BaseModel):
    status: HealthStatus
    timestamp: str
    checks: dict[str, str]
    message: str


class HealthChecker:
    """Composite dependency health checker for Codex services."""

    async def check_dependencies(self) -> HealthReport:
        checks: dict[str, str] = {}

        try:
            import torch

            checks["pytorch"] = "cuda" if torch.cuda.is_available() else "cpu"
        except ImportError as e:
            logger.debug(f"ImportError: {e}")
            logger.warning(f"ImportError: {e}", exc_info=True)
            checks["pytorch"] = "not_installed"

        data_dir = Path("./data")
        checks["data_directory"] = "ok" if data_dir.exists() else "missing"

        model_cache = Path(".hf_cache")
        checks["model_cache"] = "ok" if model_cache.exists() else "not_initialized"

        if all(value in {"ok", "cpu", "cuda"} for value in checks.values()):
            status = HealthStatus.HEALTHY
        elif any(value in {"missing", "not_initialized"} for value in checks.values()):
            status = HealthStatus.DEGRADED
        else:
            status = HealthStatus.UNHEALTHY

        return HealthReport(
            status=status,
            timestamp=datetime.utcnow().isoformat() + "Z",
            checks=checks,
            message=f"System is {status.value}",
        )
