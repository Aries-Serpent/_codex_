"""
Prometheus Metrics Module

This module provides functionality for prometheus metrics.

Usage:
    from monitoring.prometheus_metrics import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import os  # noqa: E402
import time  # noqa: E402
from collections.abc import Iterator  # noqa: E402
from contextlib import contextmanager  # noqa: E402

CollectorRegistry: type[_CollectorRegistry] | None
Counter: type[_Counter] | None
Gauge: type[_Gauge] | None
Histogram: type[_Histogram] | None

try:  # Optional dependency: prometheus-client
    from prometheus_client import CollectorRegistry as _CollectorRegistry
    from prometheus_client import Counter as _Counter
    from prometheus_client import Gauge as _Gauge
    from prometheus_client import Histogram as _Histogram

    CollectorRegistry = _CollectorRegistry
    Counter = _Counter
    Gauge = _Gauge
    Histogram = _Histogram
    _HAS_PROMETHEUS = True
except ImportError:  # pragma: no cover - optional dependency path
    CollectorRegistry = None

    Counter = Gauge = Histogram = None

    _HAS_PROMETHEUS = False


class _NoopMetric:
    """Fallback metric implementation used when prometheus-client is unavailable."""

    def __init__(self) -> None:
        self._value = 0.0

    def inc(self, amount: float = 1.0) -> None:  # pragma: no cover - trivial
        self._value += float(amount)

    def set(self, value: float) -> None:  # pragma: no cover - trivial
        self._value = float(value)

    def observe(self, value: float) -> None:  # pragma: no cover - trivial
        self._value = float(value)

    def labels(self, **_: str) -> _NoopMetric:  # pragma: no cover - trivial
        return self

    @contextmanager
    def time(self) -> Iterator[None]:  # pragma: no cover - trivial
        yield


class CodexMetricsRegistry:
    """Centralised Prometheus metrics for Codex training and inference."""

    def __init__(
        self,
        *,
        namespace: str = "codex_ml",
        registry: _CollectorRegistry | None = None,
    ) -> None:
        self.namespace = namespace
        self.registry = registry or (
            CollectorRegistry() if _HAS_PROMETHEUS and CollectorRegistry is not None else None
        )

        self.training_steps: _Counter | _NoopMetric
        self.training_loss: _Gauge | _NoopMetric
        self.training_duration_seconds: _Histogram | _NoopMetric
        self.inference_requests: _Counter | _NoopMetric
        self.inference_latency_seconds: _Histogram | _NoopMetric
        self.data_loading_duration_seconds: _Histogram | _NoopMetric
        self.active_sessions: _Gauge | _NoopMetric

        if not _HAS_PROMETHEUS or Counter is None or Gauge is None or Histogram is None:
            self.training_steps = _NoopMetric()
            self.training_loss = _NoopMetric()
            self.training_duration_seconds = _NoopMetric()
            self.inference_requests = _NoopMetric()
            self.inference_latency_seconds = _NoopMetric()
            self.data_loading_duration_seconds = _NoopMetric()
            self.active_sessions = _NoopMetric()
            return

        self.training_steps = Counter(
            f"{namespace}_training_steps_total",
            "Total training steps completed",
            registry=self.registry,
        )
        self.training_loss = Gauge(
            f"{namespace}_training_loss",
            "Current training loss",
            registry=self.registry,
        )
        self.training_duration_seconds = Histogram(
            f"{namespace}_training_duration_seconds",
            "Training loop duration in seconds",
            buckets=(1, 5, 10, 30, 60, 300),
            registry=self.registry,
        )
        self.inference_requests = Counter(
            f"{namespace}_inference_requests_total",
            "Total inference requests",
            labelnames=["endpoint"],
            registry=self.registry,
        )
        self.inference_latency_seconds = Histogram(
            f"{namespace}_inference_latency_seconds",
            "Inference request latency in seconds",
            labelnames=["endpoint"],
            buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 5.0),
            registry=self.registry,
        )
        self.data_loading_duration_seconds = Histogram(
            f"{namespace}_data_loading_duration_seconds",
            "Data loader iteration time in seconds",
            buckets=(0.1, 0.5, 1.0, 5.0, 10.0),
            registry=self.registry,
        )
        self.active_sessions = Gauge(
            f"{namespace}_active_sessions",
            "Number of active training or inference sessions",
            registry=self.registry,
        )

    def record_training_step(self, loss: float) -> None:
        """Increment the training step counter and update the latest loss."""

        self.training_steps.inc()
        self.training_loss.set(float(loss))

    def observe_training_duration(self, seconds: float) -> None:
        """Observe the duration of a training loop iteration."""

        self.training_duration_seconds.observe(max(0.0, float(seconds)))

    def record_inference(self, endpoint: str, latency_seconds: float) -> None:
        """Record an inference request for ``endpoint`` with the given latency."""

        metric = self.inference_requests
        metric.labels(endpoint=endpoint).inc()
        self.inference_latency_seconds.labels(endpoint=endpoint).observe(
            max(0.0, float(latency_seconds))
        )

    def observe_data_loading(self, seconds: float) -> None:
        """Record a data loading iteration duration."""

        self.data_loading_duration_seconds.observe(max(0.0, float(seconds)))

    @contextmanager
    def track_duration(self) -> Iterator[None]:
        """Context manager that records execution duration in ``training_duration``."""

        start = time.perf_counter()
        try:
            yield
        finally:
            self.observe_training_duration(time.perf_counter() - start)


def metrics_enabled() -> bool:
    """Return ``True`` when metrics collection should be enabled."""

    raw = os.getenv("CODEX_METRICS_ENABLED")
    if raw is None:
        return False
    return str(raw).strip().lower() in {"1", "true", "yes", "on"}


__all__ = ["CodexMetricsRegistry", "metrics_enabled"]
