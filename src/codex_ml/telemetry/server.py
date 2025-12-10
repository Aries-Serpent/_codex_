from __future__ import annotations

import logging
from typing import Optional

try:  # optional dependency
    from prometheus_client import start_http_server

    _HAS_PROM = True
except Exception:  # pragma: no cover - optional
    start_http_server = None
    _HAS_PROM = False

logger = logging.getLogger(__name__)


def start_metrics_server(port: int = 8000, addr: str = "0.0.0.0") -> Optional[bool]:  # nosec B104 - Telemetry server intentionally binds to all interfaces for container/cluster deployments
    """Start a Prometheus metrics server if ``prometheus_client`` is available.

    Returns ``True`` if the server started, ``False`` if the dependency is missing.
    
    Note: The default address binds to all interfaces (0.0.0.0) for container and 
    cluster deployment scenarios where the metrics endpoint needs to be accessible
    from outside the container. For local-only access, pass addr="127.0.0.1".
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
