"""
Metrics Export Module

This module provides functionality for metrics export.

Usage:
    from monitoring.metrics_export import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

try:  # Optional dependency for Prometheus integration
    from prometheus_client import REGISTRY, CollectorRegistry, generate_latest

    _HAS_PROMETHEUS = True
except (IOError, OSError):  # pragma: no cover - optional dependency path
    CollectorRegistry = None

    REGISTRY = None
    generate_latest = None
    _HAS_PROMETHEUS = False


def get_metrics_text(registry: CollectorRegistry | None = None) -> str:
    """Return metrics in Prometheus text exposition format."""

    if not _HAS_PROMETHEUS:
        return "# prometheus_client not installed\n"

    target = registry or REGISTRY
    payload = generate_latest(target)
    return payload.decode("utf-8")


async def metrics_endpoint_fastapi(
    registry: CollectorRegistry | None = None,
) -> object:
    """Async-compatible FastAPI handler returning metrics text."""

    text = get_metrics_text(registry)
    try:
        from fastapi import Response
    except (IOError, OSError):  # pragma: no cover - optional dependency path
        return text
    return Response(content=text, media_type="text/plain; version=0.0.4")


__all__ = ["get_metrics_text", "metrics_endpoint_fastapi"]
