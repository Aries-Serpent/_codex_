"""
RAG Monitoring Module
Provides comprehensive monitoring and observability for RAG operations.

Tracks metrics for query latency, index size, cache performance, and embedding throughput.
Supports export to Prometheus and CloudWatch for production monitoring.
"""

import logging
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class MetricsConfig:
    """
    Configuration for RAG metrics tracking.

    Allows fine-tuning memory usage by configuring window sizes per metric type.
    Smaller window sizes reduce memory but provide less historical data.

    Notes:
        A minimum window size of ``MIN_WINDOW_SIZE`` samples is enforced for each
        metric. This heuristic avoids degenerate statistics (e.g., averages or
        percentiles computed over only a handful of points) while still allowing
        applications to choose larger windows when stricter statistical rigor is
        required. Increase the window sizes if you need tighter confidence
        intervals or more stable aggregates.
    """

    # Minimum number of samples required in a metric window to consider the
    # resulting aggregate statistics (mean, percentiles) minimally meaningful.
    # This is a heuristic default rather than a hard statistical guarantee and
    # can be adjusted by changing this constant if project requirements evolve.
    MIN_WINDOW_SIZE: int = 10

    query_latency_window: int = 1000
    embedding_throughput_window: int = 500
    index_build_time_window: int = 100

    def __post_init__(self) -> None:
        """Validate configuration."""
        if self.query_latency_window < self.MIN_WINDOW_SIZE:
            raise ValueError(
                f"query_latency_window must be >= {self.MIN_WINDOW_SIZE} to ensure "
                f"statistically meaningful metrics (current: {self.query_latency_window})"
            )
        if self.embedding_throughput_window < self.MIN_WINDOW_SIZE:
            raise ValueError(
                f"embedding_throughput_window must be >= {self.MIN_WINDOW_SIZE} to "
                f"ensure statistically meaningful metrics (current: {self.embedding_throughput_window})"  # noqa: E501
            )
        if self.index_build_time_window < self.MIN_WINDOW_SIZE:
            raise ValueError(
                f"index_build_time_window must be >= {self.MIN_WINDOW_SIZE} to "
                f"ensure statistically meaningful metrics (current: {self.index_build_time_window})"
            )


@dataclass
class MetricDataPoint:
    """Single data point for a metric."""

    timestamp: float
    value: float
    labels: dict[str, str] = field(default_factory=dict)


class RAGMetrics:
    """
    Centralized metrics tracking for RAG operations.

    Supports expanded context workflows (64k-512k tokens) with comprehensive
    observability for query performance, index health, cache efficiency,
    and embedding throughput.

    Features:
        - Prometheus-compatible metric export
        - CloudWatch integration
        - Rolling window statistics
        - Alerting thresholds

    Example:
        >>> metrics = RAGMetrics()
        >>> metrics.track_query_latency(125.5, tenant_id="customer_a")
        >>> metrics.track_cache_hit_rate(hits=85, misses=15)
        >>> prom_output = metrics.export_prometheus()
    """

    def __init__(
        self,
        config: Optional[MetricsConfig] = None,
        *,
        latency_threshold_ms: Optional[float] = None,
    ):
        """
        Initialize RAG metrics tracker.

        Args:
            config: Optional MetricsConfig for fine-tuning memory usage.
                   If None, uses default configuration.
            latency_threshold_ms: Convenience shorthand to set a query-latency
                alert threshold in milliseconds.  Stored on the instance for
                use by monitoring helpers.  Ignored when *config* is None and
                only influences ``self.latency_threshold_ms``.

        Memory Optimization:
            Uses configurable window sizes per metric type to reduce memory footprint.
            Default total memory ~500KB for 1000 query latencies.
        """
        self.config = config or MetricsConfig()
        self.latency_threshold_ms: Optional[float] = latency_threshold_ms

        # Metric storage (rolling windows with optimized sizes)
        self.query_latencies: deque = deque(maxlen=self.config.query_latency_window)
        self.index_sizes: dict[str, MetricDataPoint] = {}
        self.cache_stats: dict[str, int] = {"hits": 0, "misses": 0}
        self.embedding_throughputs: deque = deque(maxlen=self.config.embedding_throughput_window)

        # Additional metrics
        self.query_counts: dict[str, int] = {}
        self.error_counts: dict[str, int] = {}
        self.index_build_times: deque = deque(maxlen=self.config.index_build_time_window)

        # Timestamp tracking
        self.start_time = time.time()
        self.last_reset = time.time()

        logger.info(
            f"RAGMetrics initialized with config: "
            f"query_latency={self.config.query_latency_window}, "
            f"embedding_throughput={self.config.embedding_throughput_window}, "
            f"index_build_time={self.config.index_build_time_window}"
        )

    def track_query_latency(
        self,
        duration_ms: float,
        tenant_id: Optional[str] = None,
        index_name: Optional[str] = None,
        cache_hit: Optional[bool] = None,
    ) -> None:
        """
        Track query latency for performance monitoring.

        Args:
            duration_ms: Query duration in milliseconds
            tenant_id: Optional tenant identifier
            index_name: Optional index name
            cache_hit: Whether query was served from cache
        """
        labels = {}
        if tenant_id:
            labels["tenant_id"] = tenant_id
        if index_name:
            labels["index_name"] = index_name
        if cache_hit is not None:
            labels["cache_hit"] = str(cache_hit)

        data_point = MetricDataPoint(timestamp=time.time(), value=duration_ms, labels=labels)

        self.query_latencies.append(data_point)

        # Track query count
        key = f"{tenant_id}:{index_name}" if tenant_id and index_name else "default"
        self.query_counts[key] = self.query_counts.get(key, 0) + 1

        logger.debug(f"Query latency: {duration_ms:.2f}ms (labels={labels})")

    def track_index_size(
        self, num_chunks: int, size_mb: float, tenant_id: str, index_name: str
    ) -> None:
        """
        Track FAISS index size metrics.

        Args:
            num_chunks: Number of text chunks in index
            size_mb: Index size in megabytes
            tenant_id: Tenant identifier
            index_name: Index name
        """
        key = f"{tenant_id}:{index_name}"

        self.index_sizes[key] = MetricDataPoint(
            timestamp=time.time(),
            value=size_mb,
            labels={
                "tenant_id": tenant_id,
                "index_name": index_name,
                "num_chunks": str(num_chunks),
            },
        )

        logger.info(f"Index size tracked: {key} = {size_mb:.2f}MB ({num_chunks} chunks)")

    def track_cache_hit_rate(self, hits: int, misses: int) -> None:
        """
        Track cache hit rate for LRU cache performance.

        Args:
            hits: Number of cache hits
            misses: Number of cache misses
        """
        self.cache_stats["hits"] = hits
        self.cache_stats["misses"] = misses

        total = hits + misses
        hit_rate = hits / total if total > 0 else 0.0

        logger.info(f"Cache hit rate: {hit_rate:.2%} (hits={hits}, misses={misses})")

    def track_embedding_throughput(self, texts_per_sec: float) -> None:
        """
        Track embedding generation throughput.

        Args:
            texts_per_sec: Number of texts embedded per second
        """
        data_point = MetricDataPoint(timestamp=time.time(), value=texts_per_sec, labels={})

        self.embedding_throughputs.append(data_point)

        logger.debug(f"Embedding throughput: {texts_per_sec:.2f} texts/sec")

    def track_index_build_time(
        self,
        duration_seconds: float,
        tenant_id: str,
        index_name: str,
        num_files: int,
        num_chunks: int,
    ) -> None:
        """
        Track index build time for capacity planning.

        Args:
            duration_seconds: Build duration in seconds
            tenant_id: Tenant identifier
            index_name: Index name
            num_files: Number of files processed
            num_chunks: Number of chunks created
        """
        data_point = MetricDataPoint(
            timestamp=time.time(),
            value=duration_seconds,
            labels={
                "tenant_id": tenant_id,
                "index_name": index_name,
                "num_files": str(num_files),
                "num_chunks": str(num_chunks),
            },
        )

        self.index_build_times.append(data_point)

        logger.info(
            f"Index build: {tenant_id}:{index_name} completed in {duration_seconds:.2f}s "
            f"({num_files} files, {num_chunks} chunks)"
        )

    def track_error(self, error_type: str, error_message: str) -> None:
        """
        Track errors for alerting and debugging.

        Args:
            error_type: Type of error (e.g., "index_not_found", "query_timeout")
            error_message: Error message
        """
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1

        logger.warning(f"Error tracked: {error_type} - {error_message}")

    def get_statistics(self) -> dict[str, Any]:
        """
        Get comprehensive statistics summary.

        Returns:
            Dictionary with all current statistics
        """
        # Query latency stats
        if self.query_latencies:
            latencies = [dp.value for dp in self.query_latencies]
            latencies.sort()
            n = len(latencies)

            query_stats = {
                "count": n,
                "mean_ms": sum(latencies) / n,
                "median_ms": latencies[n // 2],
                "p95_ms": latencies[int(n * 0.95)] if n > 0 else 0,
                "p99_ms": latencies[int(n * 0.99)] if n > 0 else 0,
                "min_ms": min(latencies),
                "max_ms": max(latencies),
            }
        else:
            query_stats = {}

        # Cache stats
        total_cache = self.cache_stats["hits"] + self.cache_stats["misses"]
        cache_hit_rate = self.cache_stats["hits"] / total_cache if total_cache > 0 else 0.0

        # Embedding throughput stats
        if self.embedding_throughputs:
            throughputs = [dp.value for dp in self.embedding_throughputs]
            embedding_stats = {
                "mean_texts_per_sec": sum(throughputs) / len(throughputs),
                "max_texts_per_sec": max(throughputs),
                "min_texts_per_sec": min(throughputs),
            }
        else:
            embedding_stats = {}

        # Index build time stats
        if self.index_build_times:
            build_times = [dp.value for dp in self.index_build_times]
            build_stats = {
                "mean_seconds": sum(build_times) / len(build_times),
                "max_seconds": max(build_times),
                "min_seconds": min(build_times),
            }
        else:
            build_stats = {}

        return {
            "uptime_seconds": time.time() - self.start_time,
            "query_latency": query_stats,
            "cache": {
                "hits": self.cache_stats["hits"],
                "misses": self.cache_stats["misses"],
                "hit_rate": cache_hit_rate,
            },
            "embedding_throughput": embedding_stats,
            "index_build_time": build_stats,
            "index_count": len(self.index_sizes),
            "total_queries": sum(self.query_counts.values()),
            "total_errors": sum(self.error_counts.values()),
            "error_breakdown": self.error_counts,
        }

    def export_prometheus(self) -> str:
        """
        Export metrics in Prometheus text format.

        Returns:
            Prometheus-formatted metrics string
        """
        lines = []

        # Query latency histogram
        if self.query_latencies:
            lines.append("# HELP rag_query_latency_ms Query latency in milliseconds")
            lines.append("# TYPE rag_query_latency_ms histogram")

            # Calculate histogram buckets
            buckets = [10, 25, 50, 100, 250, 500, 1000, 2500, 5000]
            latencies = [dp.value for dp in self.query_latencies]

            for bucket in buckets:
                count = sum(1 for lat in latencies if lat <= bucket)
                lines.append(f'rag_query_latency_ms_bucket{{le="{bucket}"}} {count}')

            lines.append(f'rag_query_latency_ms_bucket{{le="+Inf"}} {len(latencies)}')
            lines.append(f"rag_query_latency_ms_sum {sum(latencies)}")
            lines.append(f"rag_query_latency_ms_count {len(latencies)}")

        # Cache hit rate
        total_cache = self.cache_stats["hits"] + self.cache_stats["misses"]
        if total_cache > 0:
            hit_rate = self.cache_stats["hits"] / total_cache
            lines.append("# HELP rag_cache_hit_rate Cache hit rate (0-1)")
            lines.append("# TYPE rag_cache_hit_rate gauge")
            lines.append(f"rag_cache_hit_rate {hit_rate:.4f}")

        # Index sizes
        if self.index_sizes:
            lines.append("# HELP rag_index_size_mb Index size in megabytes")
            lines.append("# TYPE rag_index_size_mb gauge")

            for _, data_point in self.index_sizes.items():
                labels = ",".join(f'{k}="{v}"' for k, v in data_point.labels.items())
                lines.append(f"rag_index_size_mb{{{labels}}} {data_point.value:.2f}")

        # Embedding throughput
        if self.embedding_throughputs:
            avg_throughput = sum(dp.value for dp in self.embedding_throughputs) / len(
                self.embedding_throughputs
            )
            lines.append(
                "# HELP rag_embedding_throughput_texts_per_sec Embedding generation throughput"
            )
            lines.append("# TYPE rag_embedding_throughput_texts_per_sec gauge")
            lines.append(f"rag_embedding_throughput_texts_per_sec {avg_throughput:.2f}")

        # Query counts
        lines.append("# HELP rag_queries_total Total number of queries")
        lines.append("# TYPE rag_queries_total counter")
        lines.append(f"rag_queries_total {sum(self.query_counts.values())}")

        # Error counts
        lines.append("# HELP rag_errors_total Total number of errors")
        lines.append("# TYPE rag_errors_total counter")
        for error_type, count in self.error_counts.items():
            lines.append(f'rag_errors_total{{type="{error_type}"}} {count}')

        return "\n".join(lines) + "\n"

    def export_cloudwatch(self) -> dict[str, Any]:
        """
        Export metrics in CloudWatch format.

        Returns:
            Dictionary compatible with CloudWatch PutMetricData API
        """
        metric_data = []
        timestamp = datetime.now(UTC)

        # Query latency metrics
        if self.query_latencies:
            latencies = [dp.value for dp in self.query_latencies]
            latencies.sort()
            n = len(latencies)

            metric_data.append(
                {
                    "MetricName": "QueryLatency",
                    "Timestamp": timestamp.isoformat(),
                    "Value": sum(latencies) / n,
                    "Unit": "Milliseconds",
                    "StatisticValues": {
                        "SampleCount": n,
                        "Sum": sum(latencies),
                        "Minimum": min(latencies),
                        "Maximum": max(latencies),
                    },
                }
            )

        # Cache hit rate
        total_cache = self.cache_stats["hits"] + self.cache_stats["misses"]
        if total_cache > 0:
            hit_rate = self.cache_stats["hits"] / total_cache
            metric_data.append(
                {
                    "MetricName": "CacheHitRate",
                    "Timestamp": timestamp.isoformat(),
                    "Value": hit_rate,
                    "Unit": "Percent",
                }
            )

        # Index sizes
        for _, data_point in self.index_sizes.items():
            metric_data.append(
                {
                    "MetricName": "IndexSize",
                    "Timestamp": timestamp.isoformat(),
                    "Value": data_point.value,
                    "Unit": "Megabytes",
                    "Dimensions": [{"Name": k, "Value": v} for k, v in data_point.labels.items()],
                }
            )

        # Embedding throughput
        if self.embedding_throughputs:
            avg_throughput = sum(dp.value for dp in self.embedding_throughputs) / len(
                self.embedding_throughputs
            )
            metric_data.append(
                {
                    "MetricName": "EmbeddingThroughput",
                    "Timestamp": timestamp.isoformat(),
                    "Value": avg_throughput,
                    "Unit": "Count/Second",
                }
            )

        # Query count
        metric_data.append(
            {
                "MetricName": "QueryCount",
                "Timestamp": timestamp.isoformat(),
                "Value": sum(self.query_counts.values()),
                "Unit": "Count",
            }
        )

        # Error count
        metric_data.append(
            {
                "MetricName": "ErrorCount",
                "Timestamp": timestamp.isoformat(),
                "Value": sum(self.error_counts.values()),
                "Unit": "Count",
            }
        )

        return {"Namespace": "Codex/RAG", "MetricData": metric_data}

    def reset(self) -> None:
        """Reset all metrics (useful for testing)."""
        self.query_latencies.clear()
        self.index_sizes.clear()
        self.cache_stats = {"hits": 0, "misses": 0}
        self.embedding_throughputs.clear()
        self.query_counts.clear()
        self.error_counts.clear()
        self.index_build_times.clear()
        self.last_reset = time.time()

        logger.info("Metrics reset")


# Global metrics instance with thread-safe singleton
_global_metrics: Optional[RAGMetrics] = None
_metrics_lock = threading.Lock()


def get_metrics() -> RAGMetrics:
    """
    Get global metrics instance (thread-safe singleton pattern).

    Returns:
        Global RAGMetrics instance

    Thread-Safe:
        Uses threading.Lock to ensure only one instance is created
        even when called from multiple threads simultaneously.
    """
    global _global_metrics
    if _global_metrics is None:
        with _metrics_lock:
            # Double-check locking pattern
            if _global_metrics is None:
                _global_metrics = RAGMetrics()
    return _global_metrics


def reset_metrics() -> None:
    """Reset global metrics instance."""
    if _global_metrics:
        _global_metrics.reset()
