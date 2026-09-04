"""Callback utilities for training orchestration."""

from __future__ import annotations

from .base import (
    Callback,
    EvaluationCallback,
    LoggingCallback,
    merge_callback_results,
)
from .ndjson_logger import NDJSONLogger

try:  # pragma: no cover - optional monitoring dependency surface
    from .system_metrics import SystemMetricsCallback
except (ImportError, AttributeError):  # pragma: no cover - graceful fallback
    SystemMetricsCallback = None  # type: ignore[assignment]

__all__ = [
    "Callback",
    "EvaluationCallback",
    "LoggingCallback",
    "NDJSONLogger",
    "SystemMetricsCallback",
    "merge_callback_results",
]
