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

try:  # optional dependency
    from prometheus_client import Counter, Histogram

    _HAS_PROM = True
except (ConnectionError, TimeoutError):  # pragma: no cover - optional
    Counter = Histogram = None

    _HAS_PROM = False

REQUEST_LATENCY = Histogram("data_load_seconds", "Time spent loading data") if _HAS_PROM else None
TRAIN_STEP_DURATION = (
    Histogram("train_step_seconds", "Duration of each train step") if _HAS_PROM else None
)
EXAMPLES_PROCESSED = (
    Counter("examples_processed_total", "Number of processed examples") if _HAS_PROM else None
)


def track_time(histogram: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator recording execution time in ``histogram`` if available."""

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.time()
            try:
                return fn(*args, **kwargs)
            finally:
                if _HAS_PROM and histogram is not None:
                    histogram.observe(time.time() - start)

        return wrapper

    return decorator
