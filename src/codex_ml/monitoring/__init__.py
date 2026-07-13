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


def __getattr__(name: str) -> object:
    """Lazy-load metrics_export to avoid prometheus_client import in core profile."""
    if name in ("get_metrics_text", "metrics_endpoint_fastapi"):
        from .metrics_export import get_metrics_text, metrics_endpoint_fastapi

        globals()[name] = locals()[name]
        return locals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
