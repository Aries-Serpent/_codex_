"""Tests for performance metrics and timing utilities."""

from __future__ import annotations

import time

import pytest

from codex.archive.perf import TimingMetrics, timer


class TestTimingMetrics:
    def test_timing_metrics_duration(self) -> None:
        metrics = TimingMetrics(action="test", start_time=0.0, end_time=1.0)
        assert metrics.duration_ms == 1000.0

    def test_timing_metrics_none_when_not_finished(self) -> None:
        metrics = TimingMetrics(action="test", start_time=0.0)
        assert metrics.duration_ms is None

    def test_timing_metrics_to_dict(self) -> None:
        metrics = TimingMetrics(action="test", start_time=0.0, end_time=1.0)
        metrics_dict = metrics.to_dict()
        assert metrics_dict["action"] == "test"
        assert metrics_dict["duration_ms"] == 1000.0


class TestTimerContext:
    def test_timer_tracks_duration(self) -> None:
        with timer("test") as metrics:
            time.sleep(0.02)
        assert metrics.duration_ms is not None
        assert metrics.duration_ms >= 20

    def test_timer_sets_end_time_on_exception(self) -> None:
        with pytest.raises(ValueError), timer("test") as metrics:
            raise ValueError("test error")
        assert metrics.end_time is not None
        assert metrics.duration_ms is not None

    def test_timer_multiple_instances(self) -> None:
        with timer("test1") as m1:
            time.sleep(0.01)
            with timer("test2") as m2:
                time.sleep(0.01)
        assert m1.duration_ms is not None
        assert m2.duration_ms is not None
        assert m1.duration_ms >= m2.duration_ms
