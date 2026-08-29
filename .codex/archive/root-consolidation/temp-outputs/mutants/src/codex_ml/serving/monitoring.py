"""
Comprehensive monitoring and observability for inference server.

Provides Prometheus metrics, health checks, and distributed tracing.
"""

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from threading import Lock
from typing import Any, DefaultDict, Optional

logger = logging.getLogger(__name__)


@dataclass
class LatencyHistogram:
    """Histogram for latency tracking

    Tracks latency distribution across buckets for P50, P95, P99 calculation.
    """

    buckets: list[float]  # Bucket boundaries in milliseconds
    counts: dict[float, int] = field(default_factory=dict)  # Count per bucket
    total_count: int = 0
    total_sum: float = 0.0

    def __post_init__(self) -> None:
        """Initialize bucket counts"""
        if not self.counts:
            self.counts = {bucket: 0 for bucket in self.buckets}

    def observe(self, value_ms: float) -> None:
        """Record a latency observation

        Args:
            value_ms: Latency value in milliseconds
        """
        self.total_count += 1
        self.total_sum += value_ms

        # Find appropriate bucket
        for bucket in self.buckets:
            if value_ms <= bucket:
                self.counts[bucket] += 1
                break

    def get_percentile(self, percentile: float) -> float:
        """Calculate percentile value

        Args:
            percentile: Percentile to calculate (0.0-1.0)

        Returns:
            Percentile value in milliseconds
        """
        if self.total_count == 0:
            return 0.0

        target_count = int(self.total_count * percentile)
        cumulative = 0

        for bucket in sorted(self.buckets):
            cumulative += self.counts[bucket]
            if cumulative >= target_count:
                return bucket

        return self.buckets[-1] if self.buckets else 0.0

    def get_stats(self) -> dict[str, float]:
        """Get summary statistics"""
        return {
            "count": self.total_count,
            "sum": self.total_sum,
            "mean": self.total_sum / self.total_count if self.total_count > 0 else 0.0,
            "p50": self.get_percentile(0.50),
            "p95": self.get_percentile(0.95),
            "p99": self.get_percentile(0.99),
        }


class PrometheusMetrics:
    """Prometheus metrics collector for inference server

    Collects and exports metrics in Prometheus format.

    Metrics Categories:
    - Request metrics (count, latency, errors)
    - Model metrics (loads, cache hits, predictions)
    - Resource metrics (CPU, GPU, memory)
    - Circuit breaker metrics (state, failures, recoveries)
    """

    def __init__(self) -> None:
        """Initialize metrics collector"""
        self.lock = Lock()

        # Request metrics
        self.request_count: DefaultDict[str, int] = defaultdict(int)  # {method: count}
        self.request_latency: dict[str, LatencyHistogram] = {}  # {endpoint: LatencyHistogram}
        self.error_count: DefaultDict[str, int] = defaultdict(int)  # {error_type: count}

        # Model metrics
        self.model_load_count: DefaultDict[str, int] = defaultdict(int)  # {model_name: count}
        self.model_load_latency: dict[str, LatencyHistogram] = {}  # {model_name: LatencyHistogram}
        self.model_prediction_count: DefaultDict[str, int] = defaultdict(int)  # {model_name: count}
        self.model_prediction_latency: dict[str, LatencyHistogram] = (
            {}
        )  # {model_name: LatencyHistogram}
        self.model_cache_hits: int = 0
        self.model_cache_misses: int = 0

        # Resource metrics
        self.cpu_usage_percent: float = 0.0
        self.memory_usage_bytes: int = 0
        self.gpu_usage_percent: dict[int, float] = {}  # {device_id: percent}
        self.gpu_memory_bytes: dict[int, int] = {}  # {device_id: bytes}

        # Circuit breaker metrics
        self.circuit_breaker_state: dict[str, str] = {}  # {model_name: state}
        self.circuit_breaker_failures: DefaultDict[str, int] = defaultdict(
            int
        )  # {model_name: count}
        self.circuit_breaker_recoveries: DefaultDict[str, int] = defaultdict(
            int
        )  # {model_name: count}

        # Initialize histograms
        standard_buckets: list[float] = [
            5.0,
            10.0,
            25.0,
            50.0,
            100.0,
            250.0,
            500.0,
            1000.0,
            2500.0,
            5000.0,
            10000.0,
        ]
        self.request_latency["inference"] = LatencyHistogram(buckets=standard_buckets)
        self.request_latency["batch_inference"] = LatencyHistogram(buckets=standard_buckets)
        self.request_latency["health"] = LatencyHistogram(
            buckets=[1.0, 5.0, 10.0, 25.0, 50.0, 100.0]
        )

        logger.info("PrometheusMetrics initialized")

    def record_request(self, method: str, latency_ms: float, success: bool = True) -> None:
        """Record request metrics

        Args:
            method: HTTP method or endpoint name
            latency_ms: Request latency in milliseconds
            success: Whether request succeeded
        """
        with self.lock:
            self.request_count[method] += 1

            if method in self.request_latency:
                self.request_latency[method].observe(latency_ms)

            if not success:
                self.error_count[method] += 1

    def record_model_load(self, model_name: str, latency_ms: float, success: bool = True) -> None:
        """Record model loading metrics

        Args:
            model_name: Name of model
            latency_ms: Load time in milliseconds
            success: Whether load succeeded
        """
        with self.lock:
            if success:
                self.model_load_count[model_name] += 1

                if model_name not in self.model_load_latency:
                    self.model_load_latency[model_name] = LatencyHistogram(
                        buckets=[100.0, 500.0, 1000.0, 2000.0, 5000.0, 10000.0, 30000.0]
                    )

                self.model_load_latency[model_name].observe(latency_ms)
            else:
                self.error_count[f"model_load_{model_name}"] += 1

    def record_model_prediction(
        self, model_name: str, latency_ms: float, num_samples: int = 1
    ) -> None:
        """Record model prediction metrics

        Args:
            model_name: Name of model
            latency_ms: Prediction time in milliseconds
            num_samples: Number of samples predicted
        """
        with self.lock:
            self.model_prediction_count[model_name] += num_samples

            if model_name not in self.model_prediction_latency:
                self.model_prediction_latency[model_name] = LatencyHistogram(
                    buckets=[10.0, 25.0, 50.0, 100.0, 250.0, 500.0, 1000.0, 2500.0, 5000.0]
                )

            self.model_prediction_latency[model_name].observe(latency_ms)

    def record_cache_hit(self, hit: bool = True) -> None:
        """Record cache hit/miss

        Args:
            hit: True for cache hit, False for miss
        """
        with self.lock:
            if hit:
                self.model_cache_hits += 1
            else:
                self.model_cache_misses += 1

    def update_resource_metrics(
        self,
        cpu_percent: Optional[float] = None,
        memory_bytes: Optional[int] = None,
        gpu_usage: Optional[dict[int, float]] = None,
        gpu_memory: Optional[dict[int, int]] = None,
    ) -> None:
        """Update resource usage metrics

        Args:
            cpu_percent: CPU usage percentage
            memory_bytes: Memory usage in bytes
            gpu_usage: GPU usage by device ID
            gpu_memory: GPU memory by device ID
        """
        with self.lock:
            if cpu_percent is not None:
                self.cpu_usage_percent = cpu_percent
            if memory_bytes is not None:
                self.memory_usage_bytes = memory_bytes
            if gpu_usage is not None:
                self.gpu_usage_percent.update(gpu_usage)
            if gpu_memory is not None:
                self.gpu_memory_bytes.update(gpu_memory)

    def update_circuit_breaker_metrics(
        self, model_name: str, state: str, failure_count: int = 0
    ) -> None:
        """Update circuit breaker metrics

        Args:
            model_name: Name of model
            state: Circuit breaker state (closed/open/half_open)
            failure_count: Number of failures
        """
        with self.lock:
            old_state = self.circuit_breaker_state.get(model_name)
            self.circuit_breaker_state[model_name] = state
            self.circuit_breaker_failures[model_name] = failure_count

            # Track recoveries (transitions from open to closed)
            if old_state == "open" and state == "closed":
                self.circuit_breaker_recoveries[model_name] += 1

    def export_prometheus_format(self) -> str:
        """Export metrics in Prometheus text format

        Returns:
            Prometheus-formatted metrics string
        """
        lines = []

        # Request metrics
        lines.append("# HELP inference_requests_total Total number of inference requests")
        lines.append("# TYPE inference_requests_total counter")
        for method, count in self.request_count.items():
            lines.append(f'inference_requests_total{{method="{method}"}} {count}')

        # Request latency
        lines.append("# HELP inference_request_latency_milliseconds Request latency distribution")
        lines.append("# TYPE inference_request_latency_milliseconds histogram")
        for endpoint, hist in self.request_latency.items():
            stats = hist.get_stats()
            for bucket in hist.buckets:
                count = hist.counts[bucket]
                lines.append(
                    f'inference_request_latency_milliseconds_bucket{{endpoint="{endpoint}",le="{bucket}"}} {count}'  # noqa: E501
                )
            lines.append(
                f'inference_request_latency_milliseconds_count{{endpoint="{endpoint}"}} {stats["count"]}'  # noqa: E501
            )
            lines.append(
                f'inference_request_latency_milliseconds_sum{{endpoint="{endpoint}"}} {stats["sum"]}'  # noqa: E501
            )

        # Error metrics
        lines.append("# HELP inference_errors_total Total number of errors")
        lines.append("# TYPE inference_errors_total counter")
        for error_type, count in self.error_count.items():
            lines.append(f'inference_errors_total{{type="{error_type}"}} {count}')

        # Model metrics
        lines.append("# HELP model_loads_total Total number of model loads")
        lines.append("# TYPE model_loads_total counter")
        for model_name, count in self.model_load_count.items():
            lines.append(f'model_loads_total{{model="{model_name}"}} {count}')

        lines.append("# HELP model_predictions_total Total number of predictions")
        lines.append("# TYPE model_predictions_total counter")
        for model_name, count in self.model_prediction_count.items():
            lines.append(f'model_predictions_total{{model="{model_name}"}} {count}')

        # Cache metrics
        lines.append("# HELP model_cache_hits_total Total cache hits")
        lines.append("# TYPE model_cache_hits_total counter")
        lines.append(f"model_cache_hits_total {self.model_cache_hits}")

        lines.append("# HELP model_cache_misses_total Total cache misses")
        lines.append("# TYPE model_cache_misses_total counter")
        lines.append(f"model_cache_misses_total {self.model_cache_misses}")

        # Resource metrics
        lines.append("# HELP cpu_usage_percent CPU usage percentage")
        lines.append("# TYPE cpu_usage_percent gauge")
        lines.append(f"cpu_usage_percent {self.cpu_usage_percent}")

        lines.append("# HELP memory_usage_bytes Memory usage in bytes")
        lines.append("# TYPE memory_usage_bytes gauge")
        lines.append(f"memory_usage_bytes {self.memory_usage_bytes}")

        for device_id, usage in self.gpu_usage_percent.items():
            lines.append(f'gpu_usage_percent{{device="{device_id}"}} {usage}')

        for device_id, memory in self.gpu_memory_bytes.items():
            lines.append(f'gpu_memory_bytes{{device="{device_id}"}} {memory}')

        # Circuit breaker metrics
        lines.append(
            "# HELP circuit_breaker_state Circuit breaker state (0=closed, 1=half_open, 2=open)"
        )
        lines.append("# TYPE circuit_breaker_state gauge")
        state_map = {"closed": 0, "half_open": 1, "open": 2}
        for model_name, state in self.circuit_breaker_state.items():
            value = state_map.get(state, 0)
            lines.append(f'circuit_breaker_state{{model="{model_name}"}} {value}')

        lines.append("# HELP circuit_breaker_failures_total Circuit breaker failures")
        lines.append("# TYPE circuit_breaker_failures_total counter")
        for model_name, count in self.circuit_breaker_failures.items():
            lines.append(f'circuit_breaker_failures_total{{model="{model_name}"}} {count}')

        lines.append("# HELP circuit_breaker_recoveries_total Circuit breaker recoveries")
        lines.append("# TYPE circuit_breaker_recoveries_total counter")
        for model_name, count in self.circuit_breaker_recoveries.items():
            lines.append(f'circuit_breaker_recoveries_total{{model="{model_name}"}} {count}')

        return "\n".join(lines) + "\n"

    def get_summary(self) -> dict[str, Any]:
        """Get summary of all metrics

        Returns:
            Dictionary with metric summaries
        """
        with self.lock:
            cache_total = self.model_cache_hits + self.model_cache_misses
            cache_hit_rate = self.model_cache_hits / cache_total if cache_total > 0 else 0.0

            return {
                "requests": dict(self.request_count),
                "errors": dict(self.error_count),
                "models_loaded": dict(self.model_load_count),
                "predictions": dict(self.model_prediction_count),
                "cache_hit_rate": cache_hit_rate,
                "cpu_usage_percent": self.cpu_usage_percent,
                "memory_usage_mb": self.memory_usage_bytes / 1024 / 1024,
                "circuit_breakers": dict(self.circuit_breaker_state),
                "latency_stats": {
                    endpoint: hist.get_stats() for endpoint, hist in self.request_latency.items()
                },
            }


# Global metrics instance
_metrics = None


def get_metrics() -> PrometheusMetrics:
    """Get global metrics instance

    Returns:
        Global PrometheusMetrics instance
    """
    global _metrics
    if _metrics is None:
        _metrics = PrometheusMetrics()
    return _metrics
