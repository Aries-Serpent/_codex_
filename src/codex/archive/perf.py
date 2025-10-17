"""Performance timing utilities for archive operations."""
from __future__ import annotations

import time
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Generator


@dataclass
class TimingMetrics:
    """Performance timing metrics."""

    action: str
    start_time: float
    end_time: float | None = None

    @property
    def duration_ms(self) -> float | None:
        """Get duration in milliseconds."""

        if self.end_time is None:
            return None
        return (self.end_time - self.start_time) * 1000

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""

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

    def wrapper(*args, **kwargs):
        with timer("decompress") as metrics:
            result = func(*args, **kwargs)
        if hasattr(result, "__dict__"):
            setattr(result, "_decompress_time_ms", metrics.duration_ms)
        return result

    return wrapper
