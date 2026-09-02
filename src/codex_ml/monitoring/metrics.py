"""Prometheus metrics export for observability."""

from __future__ import annotations

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

__all__ = [
    "MetricsCollector",
    "get_metrics_router",
    "record_latency",
    "record_request",
]

# Global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None


class MetricsCollector:
    """Collects and exposes Prometheus metrics.

    Uses prometheus_client if available, otherwise provides no-op fallbacks.
    """

    def __init__(self) -> None:
        """Initialize metrics collector."""
        self._prometheus_available = False
        self._request_counter: Any | None = None
        self._latency_histogram: Any | None = None
        self._error_counter: Any | None = None
        self._active_requests: Any | None = None

        try:
            from prometheus_client import Counter, Gauge, Histogram

            self._prometheus_available = True

            # Request counter
            self._request_counter = Counter(
                "codex_requests_total",
                "Total number of requests",
                ["method", "endpoint", "status"],
            )

            # Latency histogram
            self._latency_histogram = Histogram(
                "codex_request_latency_seconds",
                "Request latency in seconds",
                ["method", "endpoint"],
            )

            # Error counter
            self._error_counter = Counter(
                "codex_errors_total", "Total number of errors", ["type", "endpoint"]
            )

            # Active requests gauge
            self._active_requests = Gauge(
                "codex_active_requests", "Number of requests currently being processed"
            )

            logger.info("Prometheus metrics collector initialized")
        except ImportError as e:
            type(e).__name__
            logger.debug("ImportError: <ERROR_TYPE>")
            logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
            logger.warning(
                "prometheus_client not available. Install with: pip install prometheus-client"
            )

    @property
    def available(self) -> bool:
        """Check if Prometheus metrics are available."""
        return self._prometheus_available

    def record_request(self, method: str = "GET", endpoint: str = "/", status: int = 200) -> None:
        """Record a request.

        Args:
            method: HTTP method
            endpoint: Request endpoint/path
            status: HTTP status code
        """
        if not self._prometheus_available or self._request_counter is None:
            return

        try:
            self._request_counter.labels(method=method, endpoint=endpoint, status=str(status)).inc()
        except (ConnectionError, TimeoutError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.debug("Failed to record request metric: %s", e)

    def record_latency(self, duration: float, method: str = "GET", endpoint: str = "/") -> None:
        """Record request latency.

        Args:
            duration: Request duration in seconds
            method: HTTP method
            endpoint: Request endpoint/path
        """
        if not self._prometheus_available or self._latency_histogram is None:
            return

        try:
            self._latency_histogram.labels(method=method, endpoint=endpoint).observe(duration)
        except (ValueError, TypeError, RuntimeError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.debug("Failed to record latency metric: %s", e)

    def record_error(self, error_type: str, endpoint: str = "/") -> None:
        """Record an error.

        Args:
            error_type: Type/category of error
            endpoint: Endpoint where error occurred
        """
        if not self._prometheus_available or self._error_counter is None:
            return

        try:
            self._error_counter.labels(type=error_type, endpoint=endpoint).inc()
        except (ConnectionError, TimeoutError) as e:
            error_type = type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.debug("Failed to record error metric: %s", e)

    def inc_active_requests(self) -> None:
        """Increment active requests counter."""
        if self._prometheus_available and self._active_requests:
            self._active_requests.inc()

    def dec_active_requests(self) -> None:
        """Decrement active requests counter."""
        if self._prometheus_available and self._active_requests:
            self._active_requests.dec()


def get_metrics_collector() -> MetricsCollector:
    """Get or create global metrics collector instance."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


def record_request(method: str = "GET", endpoint: str = "/", status: int = 200) -> None:
    """Record a request (convenience function)."""
    collector = get_metrics_collector()
    collector.record_request(method, endpoint, status)


def record_latency(duration: float, method: str = "GET", endpoint: str = "/") -> None:
    """Record request latency (convenience function)."""
    collector = get_metrics_collector()
    collector.record_latency(duration, method, endpoint)


def get_metrics_router() -> Any:
    """Get FastAPI router with metrics endpoint.

    Returns:
        FastAPI APIRouter with /metrics endpoint.

    Raises:
        ImportError: If FastAPI is not installed.
    """
    try:
        from fastapi import APIRouter, Response
        from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
    except ImportError as e:
        type(e).__name__
        logger.debug("ImportError: <ERROR_TYPE>")
        logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
        raise ImportError(
            "FastAPI and prometheus_client are required for metrics endpoint. "
            "Install with: pip install fastapi prometheus-client"
        ) from e

    router = APIRouter(tags=["metrics"])

    # Initialize collector to ensure metrics are registered
    get_metrics_collector()

    @router.get("/metrics")
    async def metrics() -> Response:
        """Prometheus metrics endpoint."""
        try:
            metrics_output = generate_latest()
            return Response(content=metrics_output, media_type=CONTENT_TYPE_LATEST)
        except (ValueError, TypeError, RuntimeError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            # Security: Don't expose internal error details to clients
            logger.error("Failed to generate metrics: %s", e, exc_info=True)
            return Response(
                content="# Error generating metrics\n",
                media_type="text/plain",
                status_code=500,
            )

    return router
