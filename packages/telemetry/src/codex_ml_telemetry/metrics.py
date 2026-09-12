"""Prometheus metrics with a dependency-free fallback."""

from __future__ import annotations

import time
from collections.abc import Callable
from functools import wraps
from typing import Any, Protocol, TypeVar, cast

try:
    from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram
except ImportError:  # pragma: no cover - exercised in minimal installations
    CollectorRegistry = Counter = Gauge = Histogram = None  # type: ignore[assignment]

_F = TypeVar("_F", bound=Callable[..., Any])


class Metric(Protocol):
    """Small metric interface used by instrumentation callers."""

    def inc(self, amount: float = 1.0) -> None: ...

    def set(self, value: float) -> None: ...

    def observe(self, value: float) -> None: ...

    def labels(self, **labels: str) -> Metric: ...


class _NoopMetric:
    def inc(self, amount: float = 1.0) -> None:
        return None

    def set(self, value: float) -> None:
        return None

    def observe(self, value: float) -> None:
        return None

    def labels(self, **labels: str) -> _NoopMetric:
        return self


def _metric(factory: Any, *args: Any, **kwargs: Any) -> Metric:
    if factory is None:
        return _NoopMetric()
    return cast(Metric, factory(*args, **kwargs))


class MetricsRegistry:
    """Stable metrics surface shared by training, serving, and health processes."""

    def __init__(self, *, namespace: str = "codex_ml", registry: Any = None) -> None:
        self.registry = registry
        if CollectorRegistry is not None and self.registry is None:
            self.registry = CollectorRegistry()

        common = {"registry": self.registry} if self.registry is not None else {}
        self.model_accuracy = _metric(
            Gauge,
            f"{namespace}_model_accuracy",
            "Current model accuracy",
            ["model"],
            **common,
        )
        self.http_requests = _metric(
            Counter,
            f"{namespace}_http_requests_total",
            "HTTP requests processed",
            ["method", "endpoint", "status"],
            **common,
        )
        self.http_errors = _metric(
            Counter,
            f"{namespace}_http_errors_total",
            "HTTP requests that failed",
            ["method", "endpoint", "error_type"],
            **common,
        )
        self.active_models = _metric(
            Gauge,
            f"{namespace}_active_models",
            "Models currently loaded",
            **common,
        )


def track_time(histogram: Metric | None) -> Callable[[_F], _F]:
    """Record callable duration when a histogram is available."""

    def decorator(function: _F) -> _F:
        @wraps(function)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            started = time.perf_counter()
            try:
                return function(*args, **kwargs)
            finally:
                if histogram is not None:
                    histogram.observe(time.perf_counter() - started)

        return cast(_F, wrapper)

    return decorator


REQUEST_LATENCY = _metric(Histogram, "data_load_seconds", "Time spent loading data")
TRAIN_STEP_DURATION = _metric(Histogram, "train_step_seconds", "Duration of each train step")
EXAMPLES_PROCESSED = _metric(
    Counter,
    "examples_processed_total",
    "Number of processed examples",
)
