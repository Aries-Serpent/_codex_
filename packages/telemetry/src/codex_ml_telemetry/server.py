"""Prometheus HTTP exporter."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def start_metrics_server(port: int = 8000, addr: str = "127.0.0.1") -> bool:
    """Start a Prometheus endpoint, returning false when support is unavailable."""

    try:
        from prometheus_client import start_http_server
    except ImportError:
        logger.warning("prometheus-client is not installed; metrics server unavailable")
        return False

    try:
        start_http_server(port, addr)
    except OSError as exc:
        logger.error("failed to start metrics server: %s", exc)
        return False
    return True
