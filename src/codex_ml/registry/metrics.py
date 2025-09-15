"""Metric registry facade."""

from __future__ import annotations

from codex_ml.metrics.registry import (
    get_metric,
    list_metrics,
    metric_registry,
    register_metric,
)

__all__ = ["metric_registry", "register_metric", "get_metric", "list_metrics"]
