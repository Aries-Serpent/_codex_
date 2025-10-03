"""Health-event logging helpers for offline regression monitoring."""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping, MutableMapping

__all__ = ["record_health_event", "health_log_path", "HEALTH_LOG_ENV", "DEFAULT_HEALTH_DIR"]

HEALTH_LOG_ENV = "CODEX_HEALTH_LOG_DIR"
DEFAULT_HEALTH_DIR = Path(".codex") / "health"


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
    if root:
        base = Path(root).expanduser()
    else:
        base = DEFAULT_HEALTH_DIR
    base.mkdir(parents=True, exist_ok=True)
    safe_name = component.replace("/", "-")
    return base / f"{safe_name}.ndjson"


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
    with destination.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")
    return destination
