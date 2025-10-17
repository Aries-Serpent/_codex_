"""Tests for performance metrics utilities."""
from __future__ import annotations

import time

from codex.archive.perf import TimingMetrics, timer


class TestTimingMetrics:
    """Test timing metrics dataclass."""

    def test_duration_calculation(self) -> None:
        metrics = TimingMetrics(action="test", start_time=0.0, end_time=1.0)
        assert metrics.duration_ms == 1000.0

    def test_duration_none_when_not_finished(self) -> None:
        metrics = TimingMetrics(action="test", start_time=0.0)
        assert metrics.duration_ms is None

    def test_to_dict(self) -> None:
        metrics = TimingMetrics(action="test", start_time=0.0, end_time=1.0)
        data = metrics.to_dict()
        assert data["action"] == "test"
        assert data["duration_ms"] == 1000.0


class TestTimerContext:
    """Test timer context manager."""

    def test_timer_tracks_duration(self) -> None:
        with timer("test") as metrics:
            time.sleep(0.02)
        assert metrics.duration_ms is not None
        assert metrics.duration_ms >= 20

    def test_timer_sets_end_time_on_exception(self) -> None:
        try:
            with timer("test") as metrics:
                raise ValueError("fail")
        except ValueError:
            pass
        assert metrics.end_time is not None
        assert metrics.duration_ms is not None

    def test_timer_nested(self) -> None:
        with timer("outer") as outer:
            time.sleep(0.01)
            with timer("inner") as inner:
                time.sleep(0.01)
        assert outer.duration_ms is not None
        assert inner.duration_ms is not None
        assert outer.duration_ms > inner.duration_ms
