"""
Metrics Module

This module provides functionality for metrics.

Usage:
    from telemetry.metrics import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import time  # noqa: E402
from collections.abc import Callable  # noqa: E402
from functools import wraps  # noqa: E402
from typing import Any  # noqa: E402

try:
    from codex_ml_telemetry import (
        EXAMPLES_PROCESSED as _standalone_examples_processed,
    )
    from codex_ml_telemetry import (
        REQUEST_LATENCY as _standalone_request_latency,
    )
    from codex_ml_telemetry import (
        TRAIN_STEP_DURATION as _standalone_train_step_duration,
    )
    from codex_ml_telemetry import track_time as _standalone_track_time
except ImportError:  # pragma: no cover - standalone package is optional during migration
    _standalone_examples_processed = None
    _standalone_request_latency = None
    _standalone_train_step_duration = None
    _standalone_track_time = None

try:  # optional dependency
    from prometheus_client import Counter, Histogram

    _HAS_PROM = True
except ImportError:  # pragma: no cover - optional
    Counter = Histogram = None

    _HAS_PROM = False

if _standalone_request_latency is not None:
    REQUEST_LATENCY = _standalone_request_latency
    TRAIN_STEP_DURATION = _standalone_train_step_duration
    EXAMPLES_PROCESSED = _standalone_examples_processed
else:
    REQUEST_LATENCY = (
        Histogram("data_load_seconds", "Time spent loading data") if _HAS_PROM else None
    )
    TRAIN_STEP_DURATION = (
        Histogram("train_step_seconds", "Duration of each train step") if _HAS_PROM else None
    )
    EXAMPLES_PROCESSED = (
        Counter("examples_processed_total", "Number of processed examples") if _HAS_PROM else None
    )


def track_time(histogram: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator recording execution time in ``histogram`` if available."""

    if _standalone_track_time is not None:
        return _standalone_track_time(histogram)

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.time()
            try:
                return fn(*args, **kwargs)
            finally:
                if histogram is not None:
                    histogram.observe(time.time() - start)

        return wrapper

    return decorator
