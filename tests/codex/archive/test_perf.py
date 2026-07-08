"""
Tests for codex.archive.perf module.

This module contains tests for performance metrics utilities.
"""
import pytest
import time
        from codex.archive.perf import TimingMetrics
        from codex.archive.perf import TimingMetrics
        from codex.archive.perf import TimingMetrics
        from codex.archive.perf import TimingMetrics
        from codex.archive.perf import TimingMetrics
        from codex.archive.perf import timer
        from codex.archive.perf import timer
        from codex.archive.perf import timer
        from codex.archive.perf import measure_decompression
        from codex.archive.perf import measure_decompression
        from codex.archive.perf import measure_decompression
        from codex.archive.perf import measure_decompression



class TestTimingMetrics:
    """Tests for TimingMetrics dataclass."""

    def test_basic_creation(self):
        """Test TimingMetrics basic creation."""

        metrics = TimingMetrics(name="test_op", started_ns=time.perf_counter_ns())

        assert metrics.name == "test_op", "name is not valid"
        assert metrics.started_ns > 0, "started_ns must be greater than zero"
        assert metrics.finished_ns is None, "finished_ns is not valid"

    def test_duration_ms_before_stop(self):
        """Test duration_ms returns value before stop."""

        metrics = TimingMetrics(name="test", started_ns=time.perf_counter_ns())

        # Sleep a tiny bit to ensure some time passes
        time.sleep(0.001)

        duration = metrics.duration_ms

        assert duration > 0, "duration must be greater than zero"

    def test_stop(self):
        """Test stop method sets finished_ns."""

        metrics = TimingMetrics(name="test", started_ns=time.perf_counter_ns())

        assert metrics.finished_ns is None, "finished_ns is not valid"

        metrics.stop()

        assert metrics.finished_ns is not None, "finished_ns must be initialized"
        assert metrics.finished_ns >= metrics.started_ns, "finished_ns must be greater than zero"

    def test_duration_ms_after_stop(self):
        """Test duration_ms uses finished_ns after stop."""

        start = time.perf_counter_ns()
        metrics = TimingMetrics(name="test", started_ns=start)

        time.sleep(0.001)
        metrics.stop()

        duration1 = metrics.duration_ms
        time.sleep(0.001)
        duration2 = metrics.duration_ms

        # Duration should be fixed after stop
        assert duration1 == duration2, "duration1 is not valid"

    def test_to_dict(self):
        """Test to_dict method."""

        metrics = TimingMetrics(name="operation", started_ns=time.perf_counter_ns())
        metrics.stop()

        result = metrics.to_dict()

        assert result["name"] == "operation", "Result must not be empty"
        assert "duration_ms" in result, "Result must not be empty"
        assert isinstance(result["duration_ms"], float)


class TestTimer:
    """Tests for timer context manager."""

    def test_timer_basic(self):
        """Test timer context manager."""

        with timer("test_operation") as metrics:
            time.sleep(0.001)

        assert metrics.name == "test_operation", "name is not valid"
        assert metrics.finished_ns is not None, "finished_ns must be initialized"
        assert metrics.duration_ms > 0, "duration_ms must be greater than zero"

    def test_timer_metrics_accessible(self):
        """Test metrics are accessible during context."""

        with timer("op") as metrics:
            assert metrics.name == "op", "name is not valid"
            assert metrics.started_ns > 0, "started_ns must be greater than zero"

    def test_timer_stops_on_exception(self):
        """Test timer stops even on exception."""

        metrics = None

        try:
            with timer("failing_op") as metrics:
                raise ValueError("Test error")
        except ValueError:
            _ = None  # suppressed: no action needed

        assert metrics is not None, "metrics must be initialized"
        assert metrics.finished_ns is not None, "finished_ns must be initialized"


class TestMeasureDecompression:
    """Tests for measure_decompression decorator."""

    def test_decorator_preserves_function(self):
        """Test decorator preserves function behavior."""

        @measure_decompression("test_func")
        def add(a, b):
            """Add two numbers."""
            return a + b

        result = add(2, 3)

        assert result == 5, "Result must not be empty"

    def test_decorator_records_metrics(self):
        """Test decorator records timing metrics."""

        @measure_decompression()
        def test_func():
            time.sleep(0.001)
            return "done"

        result = test_func()

        assert result == "done", "Result must not be empty"
        assert hasattr(test_func, "last_metrics")
        assert test_func.last_metrics is not None, "last_metrics must be initialized"
        assert test_func.last_metrics.duration_ms > 0, "duration_ms must be greater than zero"

    def test_decorator_preserves_name(self):
        """Test decorator preserves function name."""

        @measure_decompression()
        def my_function():
            return True

        assert my_function.__name__ == "my_function", "__name__ is not valid"

    def test_decorator_custom_name(self):
        """Test decorator with custom metric name."""

        @measure_decompression("custom_metric")
        def some_func():
            return "result"

        some_func()

        assert some_func.last_metrics.name == "custom_metric", "name is not valid"
