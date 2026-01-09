"""
Comprehensive tests for RAG monitoring module.

Tests cover metrics tracking, statistics calculation, export formats,
thread safety, memory management, and edge cases.
Target: 90%+ coverage of src/codex/rag/monitoring.py
"""

import pytest
import time
import threading
import json
from collections import deque
from unittest.mock import patch, MagicMock

from src.codex.rag.monitoring import (
    MetricsConfig,
    MetricDataPoint,
    RAGMetrics,
    get_metrics,
    reset_metrics,
)


class TestMetricsConfig:
    """Test MetricsConfig validation and initialization."""

    def test_valid_config(self):
        """Test valid configuration initialization."""
        config = MetricsConfig(
            query_latency_window=100,
            embedding_throughput_window=200,
            index_build_time_window=50,
        )
        assert config.query_latency_window == 100
        assert config.embedding_throughput_window == 200
        assert config.index_build_time_window == 50
        assert config.MIN_WINDOW_SIZE == 10

    def test_default_config(self):
        """Test default configuration values."""
        config = MetricsConfig()
        assert config.query_latency_window == 1000
        assert config.embedding_throughput_window == 500
        assert config.index_build_time_window == 100

    def test_query_latency_window_validation(self):
        """Test minimum window size validation for query latency."""
        with pytest.raises(ValueError, match="statistically meaningful"):
            MetricsConfig(query_latency_window=5)

        with pytest.raises(ValueError, match="statistically meaningful"):
            MetricsConfig(query_latency_window=9)

        # Exactly at minimum should work
        config = MetricsConfig(query_latency_window=10)
        assert config.query_latency_window == 10

    def test_embedding_throughput_window_validation(self):
        """Test minimum window size validation for embedding throughput."""
        with pytest.raises(ValueError, match="statistically meaningful"):
            MetricsConfig(embedding_throughput_window=8)

        with pytest.raises(ValueError, match="statistically meaningful"):
            MetricsConfig(embedding_throughput_window=0)

    def test_index_build_time_window_validation(self):
        """Test minimum window size validation for index build time."""
        with pytest.raises(ValueError, match="statistically meaningful"):
            MetricsConfig(index_build_time_window=9)

        with pytest.raises(ValueError, match="statistically meaningful"):
            MetricsConfig(index_build_time_window=-1)


class TestMetricDataPoint:
    """Test MetricDataPoint dataclass."""

    def test_basic_data_point(self):
        """Test creating a basic data point."""
        dp = MetricDataPoint(timestamp=1234567890.0, value=100.5)
        assert dp.timestamp == 1234567890.0
        assert dp.value == 100.5
        assert dp.labels == {}

    def test_data_point_with_labels(self):
        """Test data point with custom labels."""
        labels = {"tenant_id": "test_tenant", "index_name": "test_index"}
        dp = MetricDataPoint(timestamp=1234567890.0, value=200.0, labels=labels)
        assert dp.labels == labels
        assert dp.labels["tenant_id"] == "test_tenant"


class TestRAGMetrics:
    """Test RAGMetrics tracking and statistics."""

    @pytest.fixture
    def metrics(self):
        """Create a fresh metrics instance for each test."""
        return RAGMetrics()

    @pytest.fixture
    def custom_metrics(self):
        """Create metrics with custom configuration."""
        config = MetricsConfig(
            query_latency_window=50,
            embedding_throughput_window=30,
            index_build_time_window=20,
        )
        return RAGMetrics(config=config)

    def test_initialization(self, metrics):
        """Test metrics initialization."""
        assert isinstance(metrics.query_latencies, deque)
        assert isinstance(metrics.index_sizes, dict)
        assert metrics.cache_stats == {"hits": 0, "misses": 0}
        assert isinstance(metrics.embedding_throughputs, deque)
        assert isinstance(metrics.query_counts, dict)
        assert isinstance(metrics.error_counts, dict)
        assert isinstance(metrics.index_build_times, deque)
        assert metrics.start_time > 0
        assert metrics.last_reset > 0

    def test_custom_config_initialization(self, custom_metrics):
        """Test initialization with custom configuration."""
        assert custom_metrics.config.query_latency_window == 50
        assert custom_metrics.query_latencies.maxlen == 50
        assert custom_metrics.embedding_throughputs.maxlen == 30
        assert custom_metrics.index_build_times.maxlen == 20

    def test_track_query_latency_basic(self, metrics):
        """Test basic query latency tracking."""
        metrics.track_query_latency(125.5)
        assert len(metrics.query_latencies) == 1
        assert metrics.query_latencies[0].value == 125.5
        assert "default" in metrics.query_counts
        assert metrics.query_counts["default"] == 1

    def test_track_query_latency_with_labels(self, metrics):
        """Test query latency tracking with labels."""
        metrics.track_query_latency(
            100.0, tenant_id="tenant1", index_name="index1", cache_hit=True
        )
        dp = metrics.query_latencies[0]
        assert dp.value == 100.0
        assert dp.labels["tenant_id"] == "tenant1"
        assert dp.labels["index_name"] == "index1"
        assert dp.labels["cache_hit"] == "True"
        assert metrics.query_counts["tenant1:index1"] == 1

    def test_track_multiple_queries(self, metrics):
        """Test tracking multiple queries."""
        for i in range(100):
            metrics.track_query_latency(float(i), tenant_id="tenant1", index_name="index1")
        assert len(metrics.query_latencies) == 100
        assert metrics.query_counts["tenant1:index1"] == 100

    def test_track_index_size(self, metrics):
        """Test index size tracking."""
        metrics.track_index_size(
            num_chunks=1000, size_mb=50.5, tenant_id="tenant1", index_name="index1"
        )
        key = "tenant1:index1"
        assert key in metrics.index_sizes
        assert metrics.index_sizes[key].value == 50.5
        assert metrics.index_sizes[key].labels["num_chunks"] == "1000"
        assert metrics.index_sizes[key].labels["tenant_id"] == "tenant1"

    def test_track_multiple_indices(self, metrics):
        """Test tracking multiple indices."""
        metrics.track_index_size(1000, 50.0, "tenant1", "index1")
        metrics.track_index_size(2000, 100.0, "tenant1", "index2")
        metrics.track_index_size(1500, 75.0, "tenant2", "index1")
        assert len(metrics.index_sizes) == 3
        assert metrics.index_sizes["tenant1:index1"].value == 50.0
        assert metrics.index_sizes["tenant1:index2"].value == 100.0
        assert metrics.index_sizes["tenant2:index1"].value == 75.0

    def test_track_cache_hit_rate(self, metrics):
        """Test cache hit rate tracking."""
        metrics.track_cache_hit_rate(hits=85, misses=15)
        assert metrics.cache_stats["hits"] == 85
        assert metrics.cache_stats["misses"] == 15

    def test_track_cache_zero_total(self, metrics):
        """Test cache tracking with zero total."""
        metrics.track_cache_hit_rate(hits=0, misses=0)
        assert metrics.cache_stats["hits"] == 0
        assert metrics.cache_stats["misses"] == 0

    def test_track_embedding_throughput(self, metrics):
        """Test embedding throughput tracking."""
        metrics.track_embedding_throughput(100.5)
        assert len(metrics.embedding_throughputs) == 1
        assert metrics.embedding_throughputs[0].value == 100.5

    def test_track_multiple_throughputs(self, metrics):
        """Test tracking multiple throughput measurements."""
        for i in range(50):
            metrics.track_embedding_throughput(float(i * 10))
        assert len(metrics.embedding_throughputs) == 50

    def test_track_index_build_time(self, metrics):
        """Test index build time tracking."""
        metrics.track_index_build_time(
            duration_seconds=10.5,
            tenant_id="tenant1",
            index_name="index1",
            num_files=100,
            num_chunks=1000,
        )
        assert len(metrics.index_build_times) == 1
        dp = metrics.index_build_times[0]
        assert dp.value == 10.5
        assert dp.labels["tenant_id"] == "tenant1"
        assert dp.labels["index_name"] == "index1"
        assert dp.labels["num_files"] == "100"
        assert dp.labels["num_chunks"] == "1000"

    def test_track_error(self, metrics):
        """Test error tracking."""
        metrics.track_error("index_not_found", "Index does not exist")
        assert metrics.error_counts["index_not_found"] == 1

        # Track same error type again
        metrics.track_error("index_not_found", "Another index missing")
        assert metrics.error_counts["index_not_found"] == 2

    def test_track_multiple_error_types(self, metrics):
        """Test tracking multiple error types."""
        metrics.track_error("index_not_found", "Error 1")
        metrics.track_error("query_timeout", "Error 2")
        metrics.track_error("index_not_found", "Error 3")
        assert metrics.error_counts["index_not_found"] == 2
        assert metrics.error_counts["query_timeout"] == 1

    def test_get_statistics_empty(self, metrics):
        """Test statistics with no data."""
        stats = metrics.get_statistics()
        assert stats["uptime_seconds"] > 0
        assert stats["query_latency"] == {}
        assert stats["cache"]["hits"] == 0
        assert stats["cache"]["misses"] == 0
        assert stats["cache"]["hit_rate"] == 0.0
        assert stats["embedding_throughput"] == {}
        assert stats["index_build_time"] == {}
        assert stats["index_count"] == 0
        assert stats["total_queries"] == 0
        assert stats["total_errors"] == 0

    def test_get_statistics_with_queries(self, metrics):
        """Test statistics with query data."""
        # Track known distribution
        for val in [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
            metrics.track_query_latency(float(val), tenant_id="tenant1", index_name="index1")

        stats = metrics.get_statistics()
        query_stats = stats["query_latency"]
        assert query_stats["count"] == 10
        assert query_stats["mean_ms"] == pytest.approx(55.0, abs=0.1)
        assert query_stats["median_ms"] == 60.0  # For even-length, picks upper middle
        assert query_stats["min_ms"] == 10.0
        assert query_stats["max_ms"] == 100.0
        assert query_stats["p95_ms"] > 0
        assert query_stats["p99_ms"] > 0

    def test_get_statistics_percentiles(self, metrics):
        """Test percentile calculations in statistics."""
        # Track 100 values
        for i in range(100):
            metrics.track_query_latency(float(i))

        stats = metrics.get_statistics()
        query_stats = stats["query_latency"]
        assert query_stats["p95_ms"] == pytest.approx(95.0, abs=1.0)
        assert query_stats["p99_ms"] == pytest.approx(99.0, abs=1.0)

    def test_get_statistics_cache(self, metrics):
        """Test cache statistics calculation."""
        metrics.track_cache_hit_rate(hits=70, misses=30)
        stats = metrics.get_statistics()
        assert stats["cache"]["hits"] == 70
        assert stats["cache"]["misses"] == 30
        assert stats["cache"]["hit_rate"] == pytest.approx(0.7, abs=0.01)

    def test_get_statistics_embedding_throughput(self, metrics):
        """Test embedding throughput statistics."""
        metrics.track_embedding_throughput(100.0)
        metrics.track_embedding_throughput(200.0)
        metrics.track_embedding_throughput(150.0)

        stats = metrics.get_statistics()
        emb_stats = stats["embedding_throughput"]
        assert emb_stats["mean_texts_per_sec"] == pytest.approx(150.0, abs=0.1)
        assert emb_stats["max_texts_per_sec"] == 200.0
        assert emb_stats["min_texts_per_sec"] == 100.0

    def test_get_statistics_index_build_time(self, metrics):
        """Test index build time statistics."""
        metrics.track_index_build_time(10.0, "t1", "i1", 100, 1000)
        metrics.track_index_build_time(20.0, "t1", "i2", 200, 2000)
        metrics.track_index_build_time(15.0, "t2", "i1", 150, 1500)

        stats = metrics.get_statistics()
        build_stats = stats["index_build_time"]
        assert build_stats["mean_seconds"] == pytest.approx(15.0, abs=0.1)
        assert build_stats["max_seconds"] == 20.0
        assert build_stats["min_seconds"] == 10.0

    def test_get_statistics_comprehensive(self, metrics):
        """Test comprehensive statistics with all metrics."""
        # Add various metrics
        metrics.track_query_latency(100.0, tenant_id="t1", index_name="i1")
        metrics.track_query_latency(200.0, tenant_id="t1", index_name="i1")
        metrics.track_index_size(1000, 50.0, "t1", "i1")
        metrics.track_index_size(2000, 100.0, "t1", "i2")
        metrics.track_cache_hit_rate(80, 20)
        metrics.track_embedding_throughput(150.0)
        metrics.track_index_build_time(12.0, "t1", "i1", 100, 1000)
        metrics.track_error("test_error", "Test error message")

        stats = metrics.get_statistics()
        assert stats["total_queries"] == 2
        assert stats["index_count"] == 2
        assert stats["total_errors"] == 1
        assert len(stats["error_breakdown"]) == 1

    def test_window_trimming(self, custom_metrics):
        """Test metrics window trimming for memory efficiency."""
        # custom_metrics has query_latency_window=50
        # Track more than window size
        for i in range(100):
            custom_metrics.track_query_latency(float(i), tenant_id="tenant1", index_name="index1")

        # Window should be trimmed to 50 most recent
        assert len(custom_metrics.query_latencies) == 50
        # First value should be 50 (0-49 were dropped)
        assert custom_metrics.query_latencies[0].value == 50.0
        # Last value should be 99
        assert custom_metrics.query_latencies[-1].value == 99.0

    def test_concurrent_query_tracking(self, metrics):
        """Test thread-safe concurrent query tracking."""

        def track_queries(thread_id):
            for i in range(100):
                metrics.track_query_latency(
                    float(i), tenant_id=f"tenant{thread_id}", index_name="index1"
                )

        threads = [threading.Thread(target=track_queries, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should have tracked 500 queries total
        assert len(metrics.query_latencies) == 500
        total_queries = sum(metrics.query_counts.values())
        assert total_queries == 500

    def test_concurrent_error_tracking(self, metrics):
        """Test thread-safe error tracking."""

        def track_errors():
            for i in range(50):
                metrics.track_error("test_error", f"Error {i}")

        threads = [threading.Thread(target=track_errors) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert metrics.error_counts["test_error"] == 200

    def test_export_prometheus_empty(self, metrics):
        """Test Prometheus export with no data."""
        output = metrics.export_prometheus()
        assert "rag_queries_total 0" in output
        assert "rag_errors_total" in output

    def test_export_prometheus_query_histogram(self, metrics):
        """Test Prometheus export with query histogram."""
        # Add queries at different latencies
        for val in [5, 15, 30, 75, 150, 300, 600, 1200, 3000]:
            metrics.track_query_latency(float(val))

        output = metrics.export_prometheus()
        assert "rag_query_latency_ms histogram" in output
        assert 'rag_query_latency_ms_bucket{le="10"}' in output
        assert 'rag_query_latency_ms_bucket{le="100"}' in output
        assert 'rag_query_latency_ms_bucket{le="+Inf"}' in output
        assert "rag_query_latency_ms_sum" in output
        assert "rag_query_latency_ms_count 9" in output

    def test_export_prometheus_cache(self, metrics):
        """Test Prometheus export with cache metrics."""
        metrics.track_cache_hit_rate(hits=85, misses=15)
        output = metrics.export_prometheus()
        assert "rag_cache_hit_rate gauge" in output
        assert "rag_cache_hit_rate 0.85" in output

    def test_export_prometheus_index_sizes(self, metrics):
        """Test Prometheus export with index sizes."""
        metrics.track_index_size(1000, 50.5, "tenant1", "index1")
        metrics.track_index_size(2000, 100.3, "tenant2", "index2")

        output = metrics.export_prometheus()
        assert "rag_index_size_mb gauge" in output
        assert 'tenant_id="tenant1"' in output
        assert 'tenant_id="tenant2"' in output
        assert "50.50" in output or "50.5" in output
        assert "100.30" in output or "100.3" in output

    def test_export_prometheus_embedding_throughput(self, metrics):
        """Test Prometheus export with embedding throughput."""
        metrics.track_embedding_throughput(100.0)
        metrics.track_embedding_throughput(200.0)

        output = metrics.export_prometheus()
        assert "rag_embedding_throughput_texts_per_sec gauge" in output
        assert "rag_embedding_throughput_texts_per_sec 150.00" in output

    def test_export_prometheus_errors(self, metrics):
        """Test Prometheus export with errors."""
        metrics.track_error("index_not_found", "Error 1")
        metrics.track_error("query_timeout", "Error 2")
        metrics.track_error("index_not_found", "Error 3")

        output = metrics.export_prometheus()
        assert "rag_errors_total counter" in output
        assert 'rag_errors_total{type="index_not_found"} 2' in output
        assert 'rag_errors_total{type="query_timeout"} 1' in output

    def test_export_cloudwatch_empty(self, metrics):
        """Test CloudWatch export with no data."""
        output = metrics.export_cloudwatch()
        assert output["Namespace"] == "Codex/RAG"
        assert isinstance(output["MetricData"], list)
        # Should have at least QueryCount and ErrorCount (both 0)
        metric_names = [m["MetricName"] for m in output["MetricData"]]
        assert "QueryCount" in metric_names
        assert "ErrorCount" in metric_names

    def test_export_cloudwatch_query_latency(self, metrics):
        """Test CloudWatch export with query latency."""
        for i in range(10):
            metrics.track_query_latency(float(i * 10))

        output = metrics.export_cloudwatch()
        query_metrics = [m for m in output["MetricData"] if m["MetricName"] == "QueryLatency"]
        assert len(query_metrics) == 1

        qm = query_metrics[0]
        assert qm["Unit"] == "Milliseconds"
        assert "StatisticValues" in qm
        assert qm["StatisticValues"]["SampleCount"] == 10
        assert qm["StatisticValues"]["Minimum"] == 0.0
        assert qm["StatisticValues"]["Maximum"] == 90.0

    def test_export_cloudwatch_cache(self, metrics):
        """Test CloudWatch export with cache metrics."""
        metrics.track_cache_hit_rate(hits=80, misses=20)

        output = metrics.export_cloudwatch()
        cache_metrics = [m for m in output["MetricData"] if m["MetricName"] == "CacheHitRate"]
        assert len(cache_metrics) == 1
        assert cache_metrics[0]["Value"] == 0.8
        assert cache_metrics[0]["Unit"] == "Percent"

    def test_export_cloudwatch_index_sizes(self, metrics):
        """Test CloudWatch export with index sizes."""
        metrics.track_index_size(1000, 50.5, "tenant1", "index1")

        output = metrics.export_cloudwatch()
        index_metrics = [m for m in output["MetricData"] if m["MetricName"] == "IndexSize"]
        assert len(index_metrics) == 1

        im = index_metrics[0]
        assert im["Value"] == 50.5
        assert im["Unit"] == "Megabytes"
        assert len(im["Dimensions"]) > 0

    def test_export_cloudwatch_embedding_throughput(self, metrics):
        """Test CloudWatch export with embedding throughput."""
        metrics.track_embedding_throughput(150.0)
        metrics.track_embedding_throughput(250.0)

        output = metrics.export_cloudwatch()
        emb_metrics = [
            m for m in output["MetricData"] if m["MetricName"] == "EmbeddingThroughput"
        ]
        assert len(emb_metrics) == 1
        assert emb_metrics[0]["Value"] == 200.0  # Average
        assert emb_metrics[0]["Unit"] == "Count/Second"

    def test_reset(self, metrics):
        """Test metrics reset functionality."""
        # Add various metrics
        metrics.track_query_latency(100.0)
        metrics.track_index_size(1000, 50.0, "t1", "i1")
        metrics.track_cache_hit_rate(80, 20)
        metrics.track_embedding_throughput(150.0)
        metrics.track_index_build_time(10.0, "t1", "i1", 100, 1000)
        metrics.track_error("test_error", "Test")

        # Verify data exists
        assert len(metrics.query_latencies) > 0
        assert len(metrics.index_sizes) > 0
        assert metrics.cache_stats["hits"] > 0
        assert len(metrics.embedding_throughputs) > 0
        assert len(metrics.index_build_times) > 0
        assert len(metrics.error_counts) > 0

        # Reset
        old_last_reset = metrics.last_reset
        time.sleep(0.01)  # Ensure time difference
        metrics.reset()

        # Verify all cleared
        assert len(metrics.query_latencies) == 0
        assert len(metrics.index_sizes) == 0
        assert metrics.cache_stats == {"hits": 0, "misses": 0}
        assert len(metrics.embedding_throughputs) == 0
        assert len(metrics.query_counts) == 0
        assert len(metrics.error_counts) == 0
        assert len(metrics.index_build_times) == 0
        assert metrics.last_reset > old_last_reset


class TestGlobalMetrics:
    """Test global metrics singleton pattern."""

    def test_get_metrics_singleton(self):
        """Test that get_metrics returns the same instance."""
        # Reset global state
        import src.codex.rag.monitoring as mon_module

        mon_module._global_metrics = None

        metrics1 = get_metrics()
        metrics2 = get_metrics()
        assert metrics1 is metrics2

    def test_get_metrics_thread_safe(self):
        """Test thread-safe singleton creation."""
        import src.codex.rag.monitoring as mon_module

        mon_module._global_metrics = None

        instances = []
        lock = threading.Lock()

        def get_instance():
            instance = get_metrics()
            with lock:
                instances.append(id(instance))

        threads = [threading.Thread(target=get_instance) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All instances should have the same ID
        assert len(set(instances)) == 1

    def test_reset_metrics_global(self):
        """Test resetting global metrics instance."""
        metrics = get_metrics()
        metrics.track_query_latency(100.0)
        assert len(metrics.query_latencies) > 0

        reset_metrics()
        assert len(metrics.query_latencies) == 0


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_single_data_point_statistics(self):
        """Test statistics with only one data point."""
        metrics = RAGMetrics()
        metrics.track_query_latency(100.0)

        stats = metrics.get_statistics()
        query_stats = stats["query_latency"]
        assert query_stats["count"] == 1
        assert query_stats["mean_ms"] == 100.0
        assert query_stats["median_ms"] == 100.0
        assert query_stats["min_ms"] == 100.0
        assert query_stats["max_ms"] == 100.0

    def test_zero_latency(self):
        """Test handling zero latency."""
        metrics = RAGMetrics()
        metrics.track_query_latency(0.0)

        stats = metrics.get_statistics()
        assert stats["query_latency"]["mean_ms"] == 0.0

    def test_negative_latency(self):
        """Test handling negative latency (edge case)."""
        metrics = RAGMetrics()
        metrics.track_query_latency(-10.0)  # Should still be tracked

        stats = metrics.get_statistics()
        assert stats["query_latency"]["count"] == 1
        assert stats["query_latency"]["min_ms"] == -10.0

    def test_very_large_latency(self):
        """Test handling very large latency values."""
        metrics = RAGMetrics()
        metrics.track_query_latency(1e9)  # 1 billion ms

        stats = metrics.get_statistics()
        assert stats["query_latency"]["max_ms"] == 1e9

    def test_empty_labels(self):
        """Test tracking with empty label values."""
        metrics = RAGMetrics()
        metrics.track_query_latency(100.0, tenant_id="", index_name="")

        dp = metrics.query_latencies[0]
        # Empty strings are still truthy in boolean context, so they should be added
        # But looking at the actual code, empty strings evaluate to False in Python
        # So labels won't be added if they're empty
        assert len(dp.labels) == 0  # Empty strings are not added as labels

    def test_cache_zero_misses(self):
        """Test cache statistics with zero misses."""
        metrics = RAGMetrics()
        metrics.track_cache_hit_rate(hits=100, misses=0)

        stats = metrics.get_statistics()
        assert stats["cache"]["hit_rate"] == 1.0

    def test_cache_zero_hits(self):
        """Test cache statistics with zero hits."""
        metrics = RAGMetrics()
        metrics.track_cache_hit_rate(hits=0, misses=100)

        stats = metrics.get_statistics()
        assert stats["cache"]["hit_rate"] == 0.0

    def test_percentile_with_few_samples(self):
        """Test percentile calculation with minimal samples."""
        metrics = RAGMetrics()
        # Track only 2 samples
        metrics.track_query_latency(10.0)
        metrics.track_query_latency(20.0)

        stats = metrics.get_statistics()
        query_stats = stats["query_latency"]
        # Should not crash, p95 and p99 should have reasonable values
        assert query_stats["p95_ms"] >= 0
        assert query_stats["p99_ms"] >= 0

    def test_unicode_in_labels(self):
        """Test handling Unicode characters in labels."""
        metrics = RAGMetrics()
        metrics.track_query_latency(
            100.0, tenant_id="tenant_日本語", index_name="index_€"
        )

        dp = metrics.query_latencies[0]
        assert "日本語" in dp.labels["tenant_id"]
        assert "€" in dp.labels["index_name"]

    def test_special_characters_in_error_types(self):
        """Test error tracking with special characters."""
        metrics = RAGMetrics()
        metrics.track_error("error:type/with-special.chars", "Test error")

        assert "error:type/with-special.chars" in metrics.error_counts
        assert metrics.error_counts["error:type/with-special.chars"] == 1
