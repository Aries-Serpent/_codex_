"""Performance metrics utilities."""

from __future__ import annotations

import time
from collections.abc import Callable, Generator
from contextlib import contextmanager
from dataclasses import dataclass
from typing import TypeVar

T = TypeVar("T")


@dataclass
class TimingMetrics:
    """Simple timing container."""

    name: str
    started_ns: int
    finished_ns: int | None = None

    @property
    def duration_ms(self) -> float:
        end = time.perf_counter_ns() if self.finished_ns is None else self.finished_ns
        return (end - self.started_ns) / 1_000_000

    def stop(self) -> None:
        self.finished_ns = time.perf_counter_ns()

    def to_dict(self) -> dict[str, float | str]:
        return {
            "name": self.name,
            "duration_ms": round(self.duration_ms, 3),
        }


@contextmanager
def timer(name: str) -> Generator[TimingMetrics, None, None]:
    """Context manager that measures duration in milliseconds."""

    metrics = TimingMetrics(name=name, started_ns=time.perf_counter_ns())
    try:
        yield metrics
    finally:
        metrics.stop()


def measure_decompression(
    name: str | None = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator that records execution timing on the wrapped callable."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        metric_name = name or func.__name__

        def wrapper(*args, **kwargs):  # type: ignore[override]
            with timer(metric_name) as metrics:
                result = func(*args, **kwargs)
            wrapper.last_metrics = metrics  # type: ignore[attr-defined]
            return result

        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.__module__ = func.__module__
        wrapper.last_metrics = None  # type: ignore[attr-defined]
        return wrapper  # type: ignore[return-value]

    return decorator
