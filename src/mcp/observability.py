"""MCP observability for metrics, tracing, and logging.

This module provides observability features including:
- Metrics collection and export
- Request tracing with context propagation
- Structured logging
- Performance monitoring
"""

import asyncio
import logging
import threading
import time
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass, field
from functools import wraps
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class MetricValue:
    """A single metric value with metadata."""

    name: str
    value: float
    labels: dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    metric_type: str = "gauge"  # gauge, counter, histogram


@dataclass
class TraceSpan:
    """A trace span for request tracking."""

    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    operation_name: str
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    tags: dict[str, Any] = field(default_factory=dict)
    logs: list[dict[str, Any]] = field(default_factory=list)
    status: str = "ok"

    @property
    def duration_ms(self) -> Optional[float]:
        """Get span duration in milliseconds."""
        if self.end_time is None:
            return None
        return (self.end_time - self.start_time) * 1000


class MetricsRegistry:
    """Registry for collecting and exporting metrics."""

    def __init__(self) -> None:
        """Initialize the metrics registry."""
        self._counters: dict[str, float] = {}
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = {}
        self._lock = threading.Lock()
        self._labels: dict[str, dict[str, str]] = {}

    def increment_counter(
        self, name: str, value: float = 1.0, labels: Optional[dict[str, str]] = None
    ) -> None:
        """Increment a counter metric.

        Args:
            name: Metric name.
            value: Amount to increment by.
            labels: Optional metric labels.
        """
        key = self._make_key(name, labels)
        with self._lock:
            self._counters[key] = self._counters.get(key, 0.0) + value
            if labels:
                self._labels[key] = labels

    def set_gauge(self, name: str, value: float, labels: Optional[dict[str, str]] = None) -> None:
        """Set a gauge metric value.

        Args:
            name: Metric name.
            value: Metric value.
            labels: Optional metric labels.
        """
        key = self._make_key(name, labels)
        with self._lock:
            self._gauges[key] = value
            if labels:
                self._labels[key] = labels

    def observe_histogram(
        self, name: str, value: float, labels: Optional[dict[str, str]] = None
    ) -> None:
        """Record an observation for a histogram metric.

        Args:
            name: Metric name.
            value: Observed value.
            labels: Optional metric labels.
        """
        key = self._make_key(name, labels)
        with self._lock:
            if key not in self._histograms:
                self._histograms[key] = []
            self._histograms[key].append(value)
            if labels:
                self._labels[key] = labels

    def _make_key(self, name: str, labels: Optional[dict[str, str]] = None) -> str:
        """Make a unique key for a metric with labels."""
        if not labels:
            return name
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"

    def _extract_metric_name(self, key: str) -> str:
        """Extract metric name from a key with labels.

        Args:
            key: Metric key that may contain labels in braces.

        Returns:
            The metric name without labels.
        """
        return key.split("{")[0]

    def get_all_metrics(self) -> list[MetricValue]:
        """Get all collected metrics.

        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []

        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(
                    MetricValue(name=name, value=value, labels=labels, metric_type="counter")
                )

            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(
                    MetricValue(name=name, value=value, labels=labels, metric_type="gauge")
                )

            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(
                        MetricValue(
                            name=f"{name}_count",
                            value=float(len(values)),
                            labels=labels,
                            metric_type="counter",
                        )
                    )
                    metrics.append(
                        MetricValue(
                            name=f"{name}_sum",
                            value=sum(values),
                            labels=labels,
                            metric_type="counter",
                        )
                    )

        return metrics

    def reset(self) -> None:
        """Reset all metrics (for testing)."""
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()
            self._labels.clear()


class Tracer:
    """Simple tracer for request tracing."""

    def __init__(self) -> None:
        """Initialize the tracer."""
        self._spans: list[TraceSpan] = []
        self._lock = threading.Lock()
        self._span_counter = 0

    def _generate_id(self) -> str:
        """Generate a unique ID."""
        with self._lock:
            self._span_counter += 1
            return f"span-{self._span_counter:08x}"

    def start_span(
        self,
        operation_name: str,
        trace_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
        tags: Optional[dict[str, Any]] = None,
    ) -> TraceSpan:
        """Start a new trace span.

        Args:
            operation_name: Name of the operation being traced.
            trace_id: Optional trace ID for correlation.
            parent_span_id: Optional parent span ID.
            tags: Optional span tags.

        Returns:
            A new TraceSpan instance.
        """
        span = TraceSpan(
            trace_id=trace_id or self._generate_id(),
            span_id=self._generate_id(),
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            tags=tags or {},
        )

        with self._lock:
            self._spans.append(span)

        return span

    def finish_span(self, span: TraceSpan, status: str = "ok") -> None:
        """Finish a trace span.

        Args:
            span: The span to finish.
            status: Final status of the span.
        """
        span.end_time = time.time()
        span.status = status

        logger.debug(
            "Span completed: %s (duration: %.2fms, status: %s)",
            span.operation_name,
            span.duration_ms or 0,
            span.status,
        )

    def add_log(self, span: TraceSpan, event: str, **kwargs: Any) -> None:
        """Add a log event to a span.

        Args:
            span: The span to add the log to.
            event: Log event name.
            **kwargs: Additional log fields.
        """
        span.logs.append({"timestamp": time.time(), "event": event, **kwargs})

    @contextmanager
    def trace(
        self,
        operation_name: str,
        trace_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
        tags: Optional[dict[str, Any]] = None,
    ):
        """Context manager for tracing an operation.

        Args:
            operation_name: Name of the operation.
            trace_id: Optional trace ID.
            parent_span_id: Optional parent span ID.
            tags: Optional span tags.

        Yields:
            The trace span.
        """
        span = self.start_span(
            operation_name, trace_id=trace_id, parent_span_id=parent_span_id, tags=tags
        )
        try:
            yield span
            self.finish_span(span, status="ok")
        except (ValueError, TypeError, RuntimeError) as e:
            logger.debug("Exception in trace context", exc_info=True)
            span.tags["error"] = True
            span.tags["error.message"] = str(e)
            self.finish_span(span, status="error")
            raise

    def get_spans(self, trace_id: Optional[str] = None) -> list[TraceSpan]:
        """Get collected spans.

        Args:
            trace_id: Optional filter by trace ID.

        Returns:
            list of trace spans.
        """
        with self._lock:
            if trace_id:
                return [s for s in self._spans if s.trace_id == trace_id]
            return list(self._spans)

    def clear(self) -> None:
        """Clear all collected spans (for testing)."""
        with self._lock:
            self._spans.clear()


class MCPMetrics:
    """Pre-defined MCP metrics."""

    def __init__(self, registry: MetricsRegistry) -> None:
        """Initialize MCP metrics.

        Args:
            registry: Metrics registry to use.
        """
        self._registry = registry

    def record_request(self, method: str, duration_ms: float, status: str = "success") -> None:
        """Record an MCP request.

        Args:
            method: RPC method name.
            duration_ms: Request duration in milliseconds.
            status: Request status.
        """
        labels = {"method": method, "status": status}
        self._registry.increment_counter("mcp_requests_total", labels=labels)
        self._registry.observe_histogram(
            "mcp_request_duration_ms", duration_ms, labels={"method": method}
        )

    def record_error(self, method: str, error_type: str) -> None:
        """Record an MCP error.

        Args:
            method: RPC method name.
            error_type: Type of error.
        """
        self._registry.increment_counter(
            "mcp_errors_total", labels={"method": method, "error_type": error_type}
        )

    def set_active_connections(self, count: int) -> None:
        """Set the number of active connections.

        Args:
            count: Number of active connections.
        """
        self._registry.set_gauge("mcp_active_connections", float(count))

    def record_tool_invocation(
        self, tool_name: str, duration_ms: float, status: str = "success"
    ) -> None:
        """Record a tool invocation.

        Args:
            tool_name: Name of the tool.
            duration_ms: Invocation duration in milliseconds.
            status: Invocation status.
        """
        labels = {"tool": tool_name, "status": status}
        self._registry.increment_counter("mcp_tool_invocations_total", labels=labels)
        self._registry.observe_histogram(
            "mcp_tool_duration_ms", duration_ms, labels={"tool": tool_name}
        )


def traced(operation_name: Optional[str] = None):
    """Decorator for tracing function execution.

    Args:
        operation_name: Optional operation name. Uses function name if not provided.

    Returns:
        Decorated function.
    """

    def decorator(func: Callable) -> Callable:
        op_name = operation_name or func.__name__

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with get_tracer().trace(op_name):
                return func(*args, **kwargs)

        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            with get_tracer().trace(op_name):
                return await func(*args, **kwargs)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return wrapper

    return decorator


# Global instances
_metrics_registry: Optional[MetricsRegistry] = None
_tracer: Optional[Tracer] = None
_mcp_metrics: Optional[MCPMetrics] = None


def get_metrics_registry() -> MetricsRegistry:
    """Get or create the global metrics registry."""
    global _metrics_registry
    if _metrics_registry is None:
        _metrics_registry = MetricsRegistry()
    return _metrics_registry


def get_tracer() -> Tracer:
    """Get or create the global tracer."""
    global _tracer
    if _tracer is None:
        _tracer = Tracer()
    return _tracer


def get_mcp_metrics() -> MCPMetrics:
    """Get or create the global MCP metrics."""
    global _mcp_metrics
    if _mcp_metrics is None:
        _mcp_metrics = MCPMetrics(get_metrics_registry())
    return _mcp_metrics


def reset_observability() -> None:
    """Reset all observability state (for testing)."""
    global _mcp_metrics
    if _metrics_registry:
        _metrics_registry.reset()
    if _tracer:
        _tracer.clear()
    _mcp_metrics = None
