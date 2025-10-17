"""Performance timing utilities for archive operations."""

from __future__ import annotations

import time
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class TimingMetrics:
    """Performance timing metrics."""

    action: str
    start_time: float
    end_time: float | None = None

    @property
    def duration_ms(self) -> float | None:
        """Return the duration in milliseconds."""

        if self.end_time is None:
            return None
        return (self.end_time - self.start_time) * 1000

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation."""

        return {
            "action": self.action,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": self.duration_ms,
        }


@contextmanager
def timer(action: str) -> Generator[TimingMetrics, None, None]:
    """Context manager for timing operations."""

    metrics = TimingMetrics(action=action, start_time=time.time())
    try:
        yield metrics
    finally:
        metrics.end_time = time.time()


def measure_decompression(func):
    """Decorator to measure decompression timing."""

    def wrapper(*args, **kwargs):  # type: ignore[override]
        with timer("decompress") as metrics:
            result = func(*args, **kwargs)
        if hasattr(result, "__dict__"):
            result._decompress_time_ms = metrics.duration_ms
        return result

    return wrapper
