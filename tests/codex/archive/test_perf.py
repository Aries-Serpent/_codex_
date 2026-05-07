"""
Tests for codex.archive.perf module.

This module contains tests for performance metrics utilities.
"""

import time


class TestTimingMetrics:
    """Tests for TimingMetrics dataclass."""

    def test_basic_creation(self):
        """Test TimingMetrics basic creation."""
        from codex.archive.perf import TimingMetrics

        metrics = TimingMetrics(
            name="test_op",
            started_ns=time.perf_counter_ns()
        )

        assert metrics.name == "test_op"
        assert metrics.started_ns > 0
        assert metrics.finished_ns is None

    def test_duration_ms_before_stop(self):
        """Test duration_ms returns value before stop."""
        from codex.archive.perf import TimingMetrics

        metrics = TimingMetrics(
            name="test",
            started_ns=time.perf_counter_ns()
        )

        # Sleep a tiny bit to ensure some time passes
        time.sleep(0.001)

        duration = metrics.duration_ms

        assert duration > 0

    def test_stop(self):
        """Test stop method sets finished_ns."""
        from codex.archive.perf import TimingMetrics

        metrics = TimingMetrics(
            name="test",
            started_ns=time.perf_counter_ns()
        )

        assert metrics.finished_ns is None

        metrics.stop()

        assert metrics.finished_ns is not None
        assert metrics.finished_ns >= metrics.started_ns

    def test_duration_ms_after_stop(self):
        """Test duration_ms uses finished_ns after stop."""
        from codex.archive.perf import TimingMetrics

        start = time.perf_counter_ns()
        metrics = TimingMetrics(name="test", started_ns=start)

        time.sleep(0.001)
        metrics.stop()

        duration1 = metrics.duration_ms
        time.sleep(0.001)
        duration2 = metrics.duration_ms

        # Duration should be fixed after stop
        assert duration1 == duration2

    def test_to_dict(self):
        """Test to_dict method."""
        from codex.archive.perf import TimingMetrics

        metrics = TimingMetrics(
            name="operation",
            started_ns=time.perf_counter_ns()
        )
        metrics.stop()

        result = metrics.to_dict()

        assert result["name"] == "operation"
        assert "duration_ms" in result
        assert isinstance(result["duration_ms"], float)


class TestTimer:
    """Tests for timer context manager."""

    def test_timer_basic(self):
        """Test timer context manager."""
        from codex.archive.perf import timer

        with timer("test_operation") as metrics:
            time.sleep(0.001)

        assert metrics.name == "test_operation"
        assert metrics.finished_ns is not None
        assert metrics.duration_ms > 0

    def test_timer_metrics_accessible(self):
        """Test metrics are accessible during context."""
        from codex.archive.perf import timer

        with timer("op") as metrics:
            assert metrics.name == "op"
            assert metrics.started_ns > 0

    def test_timer_stops_on_exception(self):
        """Test timer stops even on exception."""
        from codex.archive.perf import timer

        metrics = None

        try:
            with timer("failing_op") as metrics:
                raise ValueError("Test error")
        except ValueError:
            _ = None  # suppressed: no action needed

        assert metrics is not None
        assert metrics.finished_ns is not None


class TestMeasureDecompression:
    """Tests for measure_decompression decorator."""

    def test_decorator_preserves_function(self):
        """Test decorator preserves function behavior."""
        from codex.archive.perf import measure_decompression

        @measure_decompression("test_func")
        def add(a, b):
            """Add two numbers."""
            return a + b

        result = add(2, 3)

        assert result == 5

    def test_decorator_records_metrics(self):
        """Test decorator records timing metrics."""
        from codex.archive.perf import measure_decompression

        @measure_decompression()
        def test_func():
            time.sleep(0.001)
            return "done"

        result = test_func()

        assert result == "done"
        assert hasattr(test_func, 'last_metrics')
        assert test_func.last_metrics is not None
        assert test_func.last_metrics.duration_ms > 0

    def test_decorator_preserves_name(self):
        """Test decorator preserves function name."""
        from codex.archive.perf import measure_decompression

        @measure_decompression()
        def my_function():
            return True

        assert my_function.__name__ == "my_function"

    def test_decorator_custom_name(self):
        """Test decorator with custom metric name."""
        from codex.archive.perf import measure_decompression

        @measure_decompression("custom_metric")
        def some_func():
            return "result"

        some_func()

        assert some_func.last_metrics.name == "custom_metric"
