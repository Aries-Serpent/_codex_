from __future__ import annotations

import logging
from typing import Optional

try:  # optional dependency
    from prometheus_client import start_http_server  # type: ignore
    _HAS_PROM = True
except Exception:  # pragma: no cover - optional
    start_http_server = None  # type: ignore
    _HAS_PROM = False

logger = logging.getLogger(__name__)


def start_metrics_server(port: int = 8000, addr: str = "0.0.0.0") -> Optional[bool]:
    """Start a Prometheus metrics server if ``prometheus_client`` is available.

    Returns ``True`` if the server started, ``False`` if the dependency is missing.
    """
    if not _HAS_PROM:
        logger.error("prometheus_client is not installed; metrics server unavailable")
        return False
    try:
        start_http_server(port, addr)
    except OSError as exc:  # pragma: no cover - defensive
        logger.error("failed to start metrics server: %s", exc)
        return False
    return True
