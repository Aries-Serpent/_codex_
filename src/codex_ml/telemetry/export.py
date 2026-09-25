"""Deprecated forwarding module for :mod:`codex_ml_telemetry` export helpers.

Scheduled for removal in ``codex-ml 0.5.0``.
"""

from __future__ import annotations

try:
    from codex_ml_telemetry import render_prometheus
except ModuleNotFoundError:  # pragma: no cover - optional standalone package
    from codex_ml.monitoring.metrics_export import get_metrics_text as _get_metrics_text

    def render_prometheus(registry=None):
        """Compatibility wrapper for monolith-only installations."""

        return _get_metrics_text(registry)


__all__ = ["render_prometheus"]
