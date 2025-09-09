from __future__ import annotations

import time
from functools import wraps
from typing import Any, Callable

try:  # optional dependency
    from prometheus_client import Counter, Histogram  # type: ignore
    _HAS_PROM = True
except Exception:  # pragma: no cover - optional
    Counter = Histogram = None  # type: ignore
    _HAS_PROM = False

REQUEST_LATENCY = Histogram("data_load_seconds", "Time spent loading data") if _HAS_PROM else None
TRAIN_STEP_DURATION = Histogram("train_step_seconds", "Duration of each train step") if _HAS_PROM else None
EXAMPLES_PROCESSED = Counter("examples_processed_total", "Number of processed examples") if _HAS_PROM else None


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
