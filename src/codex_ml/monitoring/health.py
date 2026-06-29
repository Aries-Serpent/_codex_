"""Health-event logging helpers for offline regression monitoring."""

from __future__ import annotations

import json
import logging
import os
from collections.abc import Mapping, MutableMapping
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel

__all__ = [
    "DEFAULT_HEALTH_DIR",
    "HEALTH_LOG_ENV",
    "HealthChecker",
    "HealthReport",
    "HealthStatus",
    "health_log_path",
    "record_health_event",
]

HEALTH_LOG_ENV = "CODEX_HEALTH_LOG_DIR"
DEFAULT_HEALTH_DIR = Path(".codex") / "health"

logger = logging.getLogger(__name__)


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _normalize(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(k): _normalize(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_normalize(v) for v in value]
    if isinstance(value, Path):
        return str(value)
    return value


def health_log_path(component: str) -> Path:
    """Resolve the NDJSON log file path for a given *component*.

    Uses the ``CODEX_HEALTH_LOG_DIR`` environment variable when set; falls
    back to ``.codex/health``.  The chosen parent directory is created on
    first access; if creation fails the function falls back to the default
    directory path without raising.

    Args:
        component: Logical component name (e.g. ``"model_drift"``).  Forward
            slashes are replaced with hyphens to avoid accidental
            subdirectories.

    Returns:
        :class:`~pathlib.Path` to ``<log_dir>/<component>.ndjson``.
    """
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
        base, exc = last_error  # type: ignore[misc]
        logger.debug("Unable to prepare health log directory %s: %s", base, exc)  # type: ignore[misc]
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
    """Enumeration of possible system health states.

    Inherits from ``str`` so values serialise naturally to JSON / YAML.
    """

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthReport(BaseModel):
    """Structured result returned by :meth:`HealthChecker.check_dependencies`.

    Attributes:
        status: Overall health classification.
        timestamp: ISO-8601 UTC timestamp of the check.
        checks: Mapping of dependency name → status string (e.g.
            ``"ok"``, ``"missing"``, ``"cuda"``).
        message: Human-readable summary sentence.
    """

    status: HealthStatus
    timestamp: str
    checks: dict[str, str]
    message: str


class HealthChecker:
    """Composite dependency health checker for Codex services."""

    async def check_dependencies(self) -> HealthReport:
        """Run dependency probes and return a consolidated :class:`HealthReport`.

        Probes performed:

        * **pytorch** — checks whether ``torch`` is importable and whether
          CUDA is available.
        * **data_directory** — verifies that ``./data`` exists.
        * **model_cache** — verifies that ``.hf_cache`` exists.

        Returns:
            A :class:`HealthReport` reflecting the outcome of all checks.
        """
        checks: dict[str, str] = {}

        try:
            import torch

            checks["pytorch"] = "cuda" if torch.cuda.is_available() else "cpu"
        except ImportError as e:
            type(e).__name__
            logger.debug("ImportError: <ERROR_TYPE>")
            logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
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
            timestamp=datetime.now(UTC).isoformat(),
            checks=checks,
            message=f"System is {status.value}",
        )
