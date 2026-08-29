"""
MCP Metrics - Telemetry and monitoring for MCP operations.

This module provides metrics collection for MCP adapter operations.

Author: Copilot Agent
Generated: 2025-12-24

Safeguards:
- Thread-safe metric collection
- Bounded metric history
- Defensive error handling
"""

from __future__ import annotations

import logging
import threading
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

# Configure logging
logger = logging.getLogger(__name__)

# Safeguards: Bounds
MAX_METRIC_HISTORY = 10000
MAX_LABEL_LENGTH = 100


@dataclass
class MetricPoint:
    """A single metric data point."""

    name: str
    value: float
    timestamp: str
    labels: dict[str, str] = field(default_factory=dict)


@dataclass
class MetricSummary:
    """Summary statistics for a metric."""

    name: str
    count: int
    total: float
    min_value: float
    max_value: float
    avg_value: float


class MetricCollector:
    """Thread-safe metric collector for MCP operations.

    Features:
    - Counter, gauge, and histogram metrics
    - Label support for dimensions
    - Export to various formats

    Safeguards:
    - Thread-safe operations
    - Bounded history to prevent memory issues
    """

    def __init__(self, max_history: int = MAX_METRIC_HISTORY) -> None:
        """Initialize the metric collector."""
        self._lock = threading.Lock()
        self._counters: dict[str, float] = defaultdict(float)
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = defaultdict(list)
        self._history: list[MetricPoint] = []
        self._max_history = max_history

        logger.info("MetricCollector initialized (max_history=%d)", max_history)

    def increment(
        self,
        name: str,
        value: float = 1.0,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Increment a counter metric.

        Args:
            name: Metric name.
            value: Value to add (default 1).
            labels: Optional dimension labels.
        """
        labels = labels or {}
        key = self._make_key(name, labels)

        with self._lock:
            self._counters[key] += value
            self._record_point(name, self._counters[key], labels)

    def set_gauge(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Set a gauge metric.

        Args:
            name: Metric name.
            value: Current value.
            labels: Optional dimension labels.
        """
        labels = labels or {}
        key = self._make_key(name, labels)

        with self._lock:
            self._gauges[key] = value
            self._record_point(name, value, labels)

    def observe(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Record a histogram observation.

        Args:
            name: Metric name.
            value: Observed value.
            labels: Optional dimension labels.
        """
        labels = labels or {}
        key = self._make_key(name, labels)

        with self._lock:
            self._histograms[key].append(value)
            # Bound histogram size (safeguard)
            if len(self._histograms[key]) > self._max_history:
                self._histograms[key] = self._histograms[key][-self._max_history :]
            self._record_point(name, value, labels)

    def _make_key(self, name: str, labels: dict[str, str]) -> str:
        """Create a unique key for a metric with labels."""
        if not labels:
            return name
        # Truncate labels (safeguard)
        truncated = {k[:MAX_LABEL_LENGTH]: v[:MAX_LABEL_LENGTH] for k, v in labels.items()}
        label_str = ",".join(f"{k}={v}" for k, v in sorted(truncated.items()))
        return f"{name}{{{label_str}}}"

    def _record_point(
        self,
        name: str,
        value: float,
        labels: dict[str, str],
    ) -> None:
        """Record a metric point to history."""
        point = MetricPoint(
            name=name,
            value=value,
            timestamp=datetime.now(timezone.utc).isoformat(),
            labels=labels,
        )
        self._history.append(point)

        # Bound history (safeguard)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history :]

    def get_counter(self, name: str, labels: dict[str, str] | None = None) -> float:
        """Get current counter value."""
        key = self._make_key(name, labels or {})
        with self._lock:
            return self._counters.get(key, 0.0)

    def get_gauge(self, name: str, labels: dict[str, str] | None = None) -> float:
        """Get current gauge value."""
        key = self._make_key(name, labels or {})
        with self._lock:
            return self._gauges.get(key, 0.0)

    def get_histogram_summary(
        self,
        name: str,
        labels: dict[str, str] | None = None,
    ) -> MetricSummary | None:
        """Get summary statistics for a histogram."""
        key = self._make_key(name, labels or {})
        with self._lock:
            values = self._histograms.get(key, [])
            if not values:
                return None
            return MetricSummary(
                name=name,
                count=len(values),
                total=sum(values),
                min_value=min(values),
                max_value=max(values),
                avg_value=sum(values) / len(values),
            )

    def get_all_metrics(self) -> dict[str, Any]:
        """Export all metrics."""
        with self._lock:
            return {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": {
                    k: {
                        "count": len(v),
                        "sum": sum(v),
                        "min": min(v) if v else 0,
                        "max": max(v) if v else 0,
                    }
                    for k, v in self._histograms.items()
                },
            }

    def reset(self) -> None:
        """Reset all metrics."""
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()
            self._history.clear()
        logger.info("Metrics reset")


class MCPMetrics:
    """High-level metrics for MCP operations.

    Pre-defined metrics for common MCP operations.
    """

    def __init__(self, collector: MetricCollector | None = None) -> None:
        """Initialize MCP metrics."""
        self.collector = collector or MetricCollector()

    def record_query(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        result_count: int = 0,
    ) -> None:
        """Record a query operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_queries_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe("mcp_query_duration_ms", duration_ms, labels=adapter_labels)
        self.collector.observe("mcp_query_results", result_count, labels=adapter_labels)

    def record_upsert(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        vector_count: int = 0,
    ) -> None:
        """Record an upsert operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_upserts_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe("mcp_upsert_duration_ms", duration_ms, labels=adapter_labels)
        self.collector.increment("mcp_vectors_upserted", vector_count, labels=adapter_labels)

    def record_error(self, adapter: str, error_type: str) -> None:
        """Record an error."""
        self.collector.increment(
            "mcp_errors_total", labels={"adapter": adapter, "error_type": error_type}
        )

    def set_connection_status(self, adapter: str, connected: bool) -> None:
        """Set connection status gauge."""
        self.collector.set_gauge(
            "mcp_connected", 1.0 if connected else 0.0, labels={"adapter": adapter}
        )

    def get_summary(self) -> dict[str, Any]:
        """Get a summary of MCP metrics."""
        return self.collector.get_all_metrics()
