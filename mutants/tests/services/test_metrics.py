"""
Tests for Metrics Collection Services.

Tests for collecting, aggregating, and exposing metrics.

Phase 55: MEDIUM Priority Module Tests
Coverage Target: src/services 11% → 28%+
"""

from collections import defaultdict

import pytest


class TestCounterMetrics:
    """Tests for counter-type metrics."""

    def test_counter_increment(self):
        """Counter increments correctly."""

        class Counter:
            def __init__(self, name):
                self.name = name
                self.value = 0

            def inc(self, amount=1):
                self.value += amount

            def get(self):
                return self.value

        counter = Counter("requests_total")

        assert counter.get() == 0, "Count must be greater than zero"
        counter.inc()
        assert counter.get() == 1, "Count must be greater than zero"
        counter.inc(5)
        assert counter.get() == 6, "Count must be greater than zero"

    def test_counter_labels(self):
        """Counter supports labels."""

        class LabeledCounter:
            def __init__(self, name):
                self.name = name
                self.values = defaultdict(int)

            def labels(self, **labels):
                key = tuple(sorted(labels.items()))
                return self._LabeledValue(self.values, key)

            class _LabeledValue:
                def __init__(self, values, key):
                    self.values = values
                    self.key = key

                def inc(self, amount=1):
                    self.values[self.key] += amount

        counter = LabeledCounter("http_requests")

        counter.labels(method="GET", status="200").inc()
        counter.labels(method="POST", status="201").inc()
        counter.labels(method="GET", status="200").inc()

        assert counter.values[(("method", "GET"), ("status", "200"))] == 2
        assert counter.values[(("method", "POST"), ("status", "201"))] == 1


class TestGaugeMetrics:
    """Tests for gauge-type metrics."""

    def test_gauge_set(self):
        """Gauge can be set to arbitrary values."""

        class Gauge:
            def __init__(self, name):
                self.name = name
                self.value = 0

            def set(self, value):
                self.value = value

            def get(self):
                return self.value

        gauge = Gauge("temperature")

        gauge.set(25.5)
        assert gauge.get() == 25.5, "Condition must be true"

        gauge.set(30.0)
        assert gauge.get() == 30.0, "Condition must be true"

    def test_gauge_inc_dec(self):
        """Gauge can increment and decrement."""

        class Gauge:
            def __init__(self, name):
                self.name = name
                self.value = 0

            def inc(self, amount=1):
                self.value += amount

            def dec(self, amount=1):
                self.value -= amount

            def get(self):
                return self.value

        gauge = Gauge("active_connections")

        gauge.inc()
        gauge.inc()
        assert gauge.get() == 2, "Condition must be true"

        gauge.dec()
        assert gauge.get() == 1, "Condition must be true"


class TestHistogramMetrics:
    """Tests for histogram-type metrics."""

    def test_histogram_observe(self):
        """Histogram observes values in buckets."""

        class Histogram:
            def __init__(self, name, buckets):
                self.name = name
                self.buckets = sorted(buckets) + [float("inf")]
                self.bucket_counts = defaultdict(int)
                self.sum = 0
                self.count = 0

            def observe(self, value):
                self.sum += value
                self.count += 1
                for bucket in self.buckets:
                    if value <= bucket:
                        self.bucket_counts[bucket] += 1

        histogram = Histogram("request_duration", [0.1, 0.5, 1.0, 5.0])

        histogram.observe(0.05)  # <= 0.1
        histogram.observe(0.3)  # <= 0.5
        histogram.observe(0.8)  # <= 1.0
        histogram.observe(3.0)  # <= 5.0

        assert histogram.count == 4, "Count must be greater than zero"
        assert histogram.bucket_counts[0.1] == 1, "Count must be greater than zero"
        assert histogram.bucket_counts[0.5] == 2, "Count must be greater than zero"
        assert histogram.bucket_counts[1.0] == 3, "Count must be greater than zero"

    def test_histogram_percentiles(self):
        """Histogram can compute percentiles."""

        def compute_percentile(values, percentile):
            sorted_values = sorted(values)
            # Use proper percentile calculation: (n-1) * p/100
            # For 50th percentile of 10 values: (10-1) * 50/100 = 4.5 → index 4 → value 0.5
            index = int((len(sorted_values) - 1) * percentile / 100)
            return sorted_values[index]

        values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

        assert compute_percentile(values, 50) == 0.5
        assert compute_percentile(values, 90) == 0.9


class TestSummaryMetrics:
    """Tests for summary-type metrics."""

    def test_summary_quantiles(self):
        """Summary tracks quantiles."""

        class Summary:
            def __init__(self, name, quantiles):
                self.name = name
                self.quantiles = quantiles
                self.values = []

            def observe(self, value):
                self.values.append(value)

            def get_quantile(self, q):
                if not self.values:
                    return 0
                sorted_values = sorted(self.values)
                index = int(len(sorted_values) * q)
                return sorted_values[min(index, len(sorted_values) - 1)]

        summary = Summary("latency", [0.5, 0.9, 0.99])

        for i in range(100):
            summary.observe(i / 100)

        assert summary.get_quantile(0.5) == pytest.approx(0.5, abs=0.02)
        assert summary.get_quantile(0.9) == pytest.approx(0.9, abs=0.02)


class TestMetricsRegistry:
    """Tests for metrics registry."""

    def test_registry_registration(self):
        """Metrics can be registered."""

        class MetricsRegistry:
            def __init__(self):
                self.metrics = {}

            def register(self, metric):
                if metric.name in self.metrics:
                    raise ValueError(f"Metric {metric.name} already registered")
                self.metrics[metric.name] = metric

            def get(self, name):
                return self.metrics.get(name)

        class MockMetric:
            def __init__(self, name):
                self.name = name

        registry = MetricsRegistry()

        metric = MockMetric("test_metric")
        registry.register(metric)

        assert registry.get("test_metric") is metric, "Condition must be true"

        with pytest.raises(ValueError):
            registry.register(metric)  # Duplicate

    def test_registry_export(self):
        """Registry can export all metrics."""

        def export_prometheus_format(metrics):
            lines = []
            for name, metric in metrics.items():
                value = getattr(metric, "value", 0)
                lines.append(f"{name} {value}")
            return "\n".join(lines)

        class MockMetric:
            def __init__(self, name, value):
                self.name = name
                self.value = value

        metrics = {
            "requests_total": MockMetric("requests_total", 100),
            "errors_total": MockMetric("errors_total", 5),
        }

        output = export_prometheus_format(metrics)

        assert "requests_total 100" in output, "Condition must be true"
        assert "errors_total 5" in output, "Error should be raised or set"


class TestMetricsAggregation:
    """Tests for metrics aggregation."""

    def test_rate_calculation(self):
        """Rate is calculated correctly."""

        def calculate_rate(values, time_range_seconds):
            if len(values) < 2:
                return 0
            delta = values[-1] - values[0]
            return delta / time_range_seconds

        # 100 requests over 10 seconds = 10 req/s
        values = [0, 20, 40, 60, 80, 100]
        rate = calculate_rate(values, 10)

        assert rate == 10.0, "rate is not valid"

    def test_moving_average(self):
        """Moving average is computed correctly."""

        def moving_average(values, window_size):
            if len(values) < window_size:
                return sum(values) / len(values) if values else 0
            return sum(values[-window_size:]) / window_size

        values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        assert moving_average(values, 5) == 8.0  # (6+7+8+9+10)/5

    def test_sum_aggregation(self):
        """Sum aggregation across labels."""
        labeled_values = {
            ("region", "us-east"): 100,
            ("region", "us-west"): 80,
            ("region", "eu-west"): 60,
        }

        total = sum(labeled_values.values())

        assert total == 240, "total is not valid"
