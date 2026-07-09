"""
Server Module

This module provides functionality for server.

Usage:
    from telemetry.server import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import logging
from typing import Optional

try:  # optional dependency
    from prometheus_client import start_http_server

    _HAS_PROM = True
except (ConnectionError, TimeoutError):  # pragma: no cover - optional
    start_http_server = None
    _HAS_PROM = False

logger = logging.getLogger(__name__)


def start_metrics_server(port: int = 8000, addr: str = "127.0.0.1") -> Optional[bool]:
    """Start a Prometheus metrics server if ``prometheus_client`` is available.

    Returns ``True`` if the server started, ``False`` if the dependency is missing.

    Note: The default address binds to localhost for safer defaults. For container
    or cluster deployments that require external scraping, explicitly pass
    addr="0.0.0.0".
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
