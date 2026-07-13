"""Monitoring helpers for Codex ML."""

from __future__ import annotations

from .prometheus_metrics import CodexMetricsRegistry, metrics_enabled
from .system_metrics import SystemMetricsLogger

__all__ = [
    "CodexMetricsRegistry",
    "SystemMetricsLogger",
    "get_metrics_text",
    "metrics_enabled",
    "metrics_endpoint_fastapi",
]


def _metrics_endpoint_fastapi_wrapper(
    registry: object | None = None,
) -> object:
    """Graceful wrapper for metrics_endpoint_fastapi when FastAPI is unavailable."""
    try:
        from .metrics_export import metrics_endpoint_fastapi

        return metrics_endpoint_fastapi(registry)
    except ImportError:
        # FastAPI not available - return text metrics directly
        from .metrics_export import get_metrics_text

        return get_metrics_text(registry)


def __getattr__(name: str) -> object:
    """Lazy-load metrics_export to avoid prometheus_client import in core profile."""
    if name == "get_metrics_text":
        from .metrics_export import get_metrics_text

        globals()[name] = get_metrics_text
        return get_metrics_text
    elif name == "metrics_endpoint_fastapi":
        globals()[name] = _metrics_endpoint_fastapi_wrapper
        return _metrics_endpoint_fastapi_wrapper
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
