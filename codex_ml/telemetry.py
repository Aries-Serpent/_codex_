"""Small observability primitives used by the training scripts."""

from __future__ import annotations

import contextlib
import time
from dataclasses import dataclass
from typing import Callable, Iterator, Optional

__all__ = ["Metric", "Counter", "Histogram", "EXAMPLES_PROCESSED", "TRAIN_STEP_DURATION", "track_time"]


@dataclass
class Metric:
    name: str
    description: str = ""

    def __bool__(self) -> bool:  # pragma: no cover - trivial
        return True


class Counter(Metric):
    def __post_init__(self) -> None:
        self.value = 0

    def inc(self, amount: int = 1) -> None:
        self.value += int(amount)


class Histogram(Metric):
    def __post_init__(self) -> None:
        self.values: list[float] = []

    def observe(self, value: float) -> None:
        self.values.append(float(value))


EXAMPLES_PROCESSED = Counter("train_examples", "Examples processed during training")
TRAIN_STEP_DURATION = Histogram("train_step_duration_seconds", "Time per optimisation step")


def track_time(metric: Histogram | Metric) -> Callable[[Callable[..., float]], Callable[..., float]]:
    """Decorator that records execution time in ``metric`` when supported."""

    def decorator(func: Callable[..., float]) -> Callable[..., float]:
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            duration = time.perf_counter() - start
            if hasattr(metric, "observe"):
                metric.observe(duration)  # type: ignore[call-arg]
            return result

        return wrapper

    return decorator


@contextlib.contextmanager
def timed(metric: Histogram | Metric) -> Iterator[None]:
    start = time.perf_counter()
    yield
    duration = time.perf_counter() - start
    if hasattr(metric, "observe"):
        metric.observe(duration)  # type: ignore[call-arg]
