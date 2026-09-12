"""Framework-neutral Prometheus rendering and HTTP serving."""

from __future__ import annotations

import logging
from typing import Any

try:
    from prometheus_client import REGISTRY, generate_latest, start_http_server
except ImportError:  # pragma: no cover - exercised in minimal installations
    REGISTRY = None
    generate_latest = None
    start_http_server = None

logger = logging.getLogger(__name__)


def render_prometheus(registry: Any = None) -> str:
    """Render a registry using the Prometheus text exposition format."""

    if generate_latest is None:
        return "# prometheus_client not installed\n"

    target = REGISTRY if registry is None else registry
    payload = generate_latest(target)
    return payload.decode("utf-8")


def start_metrics_server(port: int = 8000, addr: str = "127.0.0.1") -> bool:
    """Start a Prometheus endpoint, returning false when support is unavailable."""

    if start_http_server is None:
        logger.warning("prometheus-client is not installed; metrics server unavailable")
        return False

    try:
        start_http_server(port, addr)
    except OSError as exc:
        logger.error("failed to start metrics server: %s", exc)
        return False
    return True


__all__ = ["render_prometheus", "start_metrics_server"]
