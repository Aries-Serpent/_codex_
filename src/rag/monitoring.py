"""
RAG Monitoring and Telemetry - Real-time health monitoring for RAG pipeline.

This module provides comprehensive monitoring for:
- Operation latency tracking
- Timeout event detection and alerting
- Reliability metrics (success rate, error rate)
- Resource utilization tracking
- Circuit breaker state monitoring
- Performance degradation detection

PHASE 4D PLANSET 003: RAG Module Robustness
Authority: D-tier autonomous
Target Reliability: 99%+
"""

from __future__ import annotations

import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Monitoring constants
DEFAULT_WINDOW_SIZE = 300  # 5 minutes
DEFAULT_ALERT_THRESHOLD_TIMEOUT_RATE = 0.05  # 5% timeout rate
DEFAULT_ALERT_THRESHOLD_ERROR_RATE = 0.10  # 10% error rate
DEFAULT_ALERT_THRESHOLD_LATENCY_MS = 5000  # 5 seconds


@dataclass
class OperationMetric:
    """Metric for a single operation."""

    operation_type: str
    timestamp: float
    duration_ms: float
    success: bool
    timed_out: bool = False
    fallback_used: bool = False
    error_type: str = ""
    resource_usage: dict[str, Any] = field(default_factory=dict)


@dataclass
class WindowMetrics:
    """Aggregated metrics for a time window."""

    operation_type: str
    start_time: float
    end_time: float
    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    timed_out_operations: int = 0
    fallback_used_operations: int = 0
    total_duration_ms: float = 0.0
    min_duration_ms: float = float("inf")
    max_duration_ms: float = 0.0
    avg_duration_ms: float = 0.0
    p50_duration_ms: float = 0.0
    p95_duration_ms: float = 0.0
    p99_duration_ms: float = 0.0

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_operations == 0:
            return 1.0
        return self.successful_operations / self.total_operations

    @property
    def error_rate(self) -> float:
        """Calculate error rate."""
        return 1.0 - self.success_rate

    @property
    def timeout_rate(self) -> float:
        """Calculate timeout rate."""
        if self.total_operations == 0:
            return 0.0
        return self.timed_out_operations / self.total_operations

    @property
    def fallback_rate(self) -> float:
        """Calculate fallback usage rate."""
        if self.total_operations == 0:
            return 0.0
        return self.fallback_used_operations / self.total_operations


@dataclass
class HealthAlert:
    """Alert for health issue."""

    alert_type: str  # timeout_spike, high_error_rate, latency_degradation, etc.
    severity: str  # critical, warning, info
    operation_type: str
    message: str
    timestamp: float = field(default_factory=time.time)
    metric_value: float = 0.0
    threshold: float = 0.0


class RAGMonitor:
    """Central monitoring system for RAG operations."""

    def __init__(
        self,
        window_size: int = DEFAULT_WINDOW_SIZE,
        alert_timeout_rate: float = DEFAULT_ALERT_THRESHOLD_TIMEOUT_RATE,
        alert_error_rate: float = DEFAULT_ALERT_THRESHOLD_ERROR_RATE,
        alert_latency_ms: float = DEFAULT_ALERT_THRESHOLD_LATENCY_MS,
    ) -> None:
        """Initialize RAG monitor.

        Args:
            window_size: Time window in seconds for metrics aggregation
            alert_timeout_rate: Alert threshold for timeout rate
            alert_error_rate: Alert threshold for error rate
            alert_latency_ms: Alert threshold for latency in ms
        """
        self.window_size = window_size
        self.alert_timeout_rate = alert_timeout_rate
        self.alert_error_rate = alert_error_rate
        self.alert_latency_ms = alert_latency_ms

        # Storage for metrics and alerts
        self._metrics: deque[OperationMetric] = deque(maxlen=10000)
        self._alerts: deque[HealthAlert] = deque(maxlen=1000)
        self._window_cache: dict[str, WindowMetrics] = {}

        logger.info(
            "RAGMonitor initialized: window_size=%ds, "
            "alert_timeout_rate=%.1f%%, alert_error_rate=%.1f%%",
            window_size,
            alert_timeout_rate * 100,
            alert_error_rate * 100,
        )

    def record_metric(self, metric: OperationMetric) -> Optional[list[HealthAlert]]:
        """Record operation metric and check for alerts.

        Args:
            metric: Operation metric to record

        Returns:
            List of generated alerts (if any)
        """
        self._metrics.append(metric)

        # Invalidate window cache for this operation type
        if metric.operation_type in self._window_cache:
            del self._window_cache[metric.operation_type]

        # Check for alerts
        alerts = self._check_for_alerts(metric.operation_type)

        return alerts if alerts else None

    def _check_for_alerts(self, operation_type: str) -> list[HealthAlert]:
        """Check if alerts should be triggered for operation type."""
        alerts: list[HealthAlert] = []

        # Get current window metrics
        window = self._get_window_metrics(operation_type)

        # Check timeout rate
        if window.timeout_rate > self.alert_timeout_rate:
            alert = HealthAlert(
                alert_type="timeout_spike",
                severity="warning" if window.timeout_rate < 0.15 else "critical",
                operation_type=operation_type,
                message=f"Timeout rate elevated to {window.timeout_rate:.1%}",
                metric_value=window.timeout_rate,
                threshold=self.alert_timeout_rate,
            )
            alerts.append(alert)
            self._alerts.append(alert)

        # Check error rate
        if window.error_rate > self.alert_error_rate:
            alert = HealthAlert(
                alert_type="high_error_rate",
                severity="warning" if window.error_rate < 0.20 else "critical",
                operation_type=operation_type,
                message=f"Error rate elevated to {window.error_rate:.1%}",
                metric_value=window.error_rate,
                threshold=self.alert_error_rate,
            )
            alerts.append(alert)
            self._alerts.append(alert)

        # Check latency degradation
        if window.avg_duration_ms > self.alert_latency_ms:
            alert = HealthAlert(
                alert_type="latency_degradation",
                severity="info",
                operation_type=operation_type,
                message=f"Average latency elevated to {window.avg_duration_ms:.0f}ms",
                metric_value=window.avg_duration_ms,
                threshold=self.alert_latency_ms,
            )
            alerts.append(alert)
            self._alerts.append(alert)

        # Log alerts
        for alert in alerts:
            logger.warning(
                f"[{alert.severity.upper()}] {alert.alert_type}: {alert.message}"
            )

        return alerts

    def _get_window_metrics(self, operation_type: str) -> WindowMetrics:
        """Get aggregated metrics for operation within current window."""
        # Check cache
        if operation_type in self._window_cache:
            cached = self._window_cache[operation_type]
            if time.time() - cached.start_time < self.window_size:
                return cached

        # Rebuild from raw metrics
        now = time.time()
        window_start = now - self.window_size

        relevant_metrics = [
            m for m in self._metrics
            if m.operation_type == operation_type and m.timestamp >= window_start
        ]

        if not relevant_metrics:
            # Return empty window
            return WindowMetrics(
                operation_type=operation_type,
                start_time=window_start,
                end_time=now,
            )

        # Aggregate metrics
        durations = [m.duration_ms for m in relevant_metrics]
        window = WindowMetrics(
            operation_type=operation_type,
            start_time=window_start,
            end_time=now,
            total_operations=len(relevant_metrics),
            successful_operations=sum(1 for m in relevant_metrics if m.success),
            failed_operations=sum(1 for m in relevant_metrics if not m.success),
            timed_out_operations=sum(1 for m in relevant_metrics if m.timed_out),
            fallback_used_operations=sum(1 for m in relevant_metrics if m.fallback_used),
            total_duration_ms=sum(durations),
            min_duration_ms=min(durations) if durations else 0.0,
            max_duration_ms=max(durations) if durations else 0.0,
            avg_duration_ms=sum(durations) / len(durations) if durations else 0.0,
        )

        # Calculate percentiles
        sorted_durations = sorted(durations)
        if sorted_durations:
            window.p50_duration_ms = sorted_durations[len(sorted_durations) // 2]
            window.p95_duration_ms = sorted_durations[int(len(sorted_durations) * 0.95)]
            window.p99_duration_ms = sorted_durations[int(len(sorted_durations) * 0.99)]

        # Cache result
        self._window_cache[operation_type] = window

        return window

    def get_health_summary(self) -> dict[str, Any]:
        """Get overall health summary."""
        operation_types = set(m.operation_type for m in self._metrics)

        health_summary = {
            "timestamp": time.time(),
            "total_operations": len(self._metrics),
            "total_alerts": len(self._alerts),
            "recent_alerts": list(self._alerts)[-10:],  # Last 10 alerts
            "operations": {},
        }

        for op_type in operation_types:
            window = self._get_window_metrics(op_type)
            health_summary["operations"][op_type] = {
                "total_operations": window.total_operations,
                "success_rate": window.success_rate,
                "error_rate": window.error_rate,
                "timeout_rate": window.timeout_rate,
                "fallback_rate": window.fallback_rate,
                "avg_duration_ms": window.avg_duration_ms,
                "p95_duration_ms": window.p95_duration_ms,
                "p99_duration_ms": window.p99_duration_ms,
            }

        return health_summary

    def get_operation_health(self, operation_type: str) -> dict[str, Any]:
        """Get detailed health for specific operation type."""
        window = self._get_window_metrics(operation_type)

        return {
            "operation_type": operation_type,
            "window_seconds": self.window_size,
            "total_operations": window.total_operations,
            "successful_operations": window.successful_operations,
            "failed_operations": window.failed_operations,
            "timed_out_operations": window.timed_out_operations,
            "success_rate": window.success_rate,
            "error_rate": window.error_rate,
            "timeout_rate": window.timeout_rate,
            "fallback_rate": window.fallback_rate,
            "duration_ms": {
                "min": window.min_duration_ms,
                "max": window.max_duration_ms,
                "avg": window.avg_duration_ms,
                "p50": window.p50_duration_ms,
                "p95": window.p95_duration_ms,
                "p99": window.p99_duration_ms,
            },
        }

    def clear_metrics(self) -> None:
        """Clear accumulated metrics."""
        self._metrics.clear()
        self._window_cache.clear()
        logger.info("RAG monitor metrics cleared")


# Global monitor instance
_global_monitor: Optional[RAGMonitor] = None


def get_rag_monitor() -> RAGMonitor:
    """Get or create global RAG monitor instance."""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = RAGMonitor()
    return _global_monitor


def set_rag_monitor(monitor: RAGMonitor) -> None:
    """Set global RAG monitor instance."""
    global _global_monitor
    _global_monitor = monitor
