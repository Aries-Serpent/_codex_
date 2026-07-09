"""Performance degradation monitor with configurable thresholds and alerting.

from codex.logging.structured_logger import logger
Monitors training metrics (loss, throughput, latency) and fires alerts
via TrainingAlertManager when anomalies exceed configured thresholds.
"""

from __future__ import annotations

import os
import statistics
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from codex.alerting import AlertEvent, AlertSeverity, TrainingAlertManager


@dataclass
class PerformanceThresholds:
    """Configurable thresholds for performance anomaly detection."""

    loss_spike_factor: float = 2.0  # alert if loss > baseline * factor
    throughput_drop_pct: float = 30.0  # alert if throughput drops > X%
    latency_spike_factor: float = 3.0  # alert if latency > baseline * factor
    window_size: int = 10  # number of recent samples for baseline
    min_samples: int = 3  # minimum samples before alerting

    @classmethod
    def from_env(cls) -> "PerformanceThresholds":
        """Load thresholds from environment variables with defaults."""
        return cls(
            loss_spike_factor=float(os.getenv("CODEX_PERF_LOSS_SPIKE_FACTOR", "2.0")),
            throughput_drop_pct=float(os.getenv("CODEX_PERF_THROUGHPUT_DROP_PCT", "30.0")),
            latency_spike_factor=float(os.getenv("CODEX_PERF_LATENCY_SPIKE_FACTOR", "3.0")),
            window_size=int(os.getenv("CODEX_PERF_WINDOW_SIZE", "10")),
            min_samples=int(os.getenv("CODEX_PERF_MIN_SAMPLES", "3")),
        )


@dataclass
class PerformanceSnapshot:
    """A point-in-time capture of training performance metrics."""

    epoch: int
    loss: float | None = None
    throughput: float | None = None  # samples/sec
    latency_ms: float | None = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"))
    metadata: dict[str, Any] = field(default_factory=dict)


class PerformanceMonitor:
    """Tracks training metrics and fires alerts on degradation.

    Usage::

        monitor = PerformanceMonitor(run_id="run-42")
        for epoch in range(1, epochs + 1):
            loss = train_one_epoch(...)
            anomalies = monitor.record(PerformanceSnapshot(epoch=epoch, loss=loss))
            if anomalies:
                logger.info("Degradation detected:", anomalies)
    """

    def __init__(
        self,
        alert_manager: TrainingAlertManager | None = None,
        thresholds: PerformanceThresholds | None = None,
        run_id: str = "",
    ) -> None:
        self._alert_manager = alert_manager or TrainingAlertManager.from_env()
        self._thresholds = thresholds or PerformanceThresholds.from_env()
        self._run_id = run_id
        self._history: list[PerformanceSnapshot] = []

    def record(self, snapshot: PerformanceSnapshot) -> list[str]:
        """Record a snapshot and return list of anomaly descriptions (empty = healthy)."""
        self._history.append(snapshot)
        anomalies = self._detect_anomalies(snapshot)
        if anomalies:
            self._fire_alert(snapshot, anomalies)
        return anomalies

    def _baseline(self, metric: str) -> float | None:
        """Compute rolling baseline mean from recent window (excluding latest)."""
        window = self._history[-(self._thresholds.window_size + 1) : -1]
        values = [getattr(s, metric) for s in window if getattr(s, metric) is not None]
        if len(values) < self._thresholds.min_samples:
            return None
        return statistics.mean(values)

    def _detect_anomalies(self, snapshot: PerformanceSnapshot) -> list[str]:
        anomalies: list[str] = []

        if snapshot.loss is not None:
            baseline = self._baseline("loss")
            if baseline and snapshot.loss > baseline * self._thresholds.loss_spike_factor:
                anomalies.append(
                    f"Loss spike: {snapshot.loss:.4f} > {baseline:.4f} × "
                    f"{self._thresholds.loss_spike_factor} (baseline)"
                )

        if snapshot.throughput is not None:
            baseline = self._baseline("throughput")
            if baseline and baseline > 0:
                drop_pct = (baseline - snapshot.throughput) / baseline * 100
                if drop_pct > self._thresholds.throughput_drop_pct:
                    anomalies.append(
                        f"Throughput drop: {drop_pct:.1f}% below baseline "
                        f"{baseline:.1f} samples/sec"
                    )

        if snapshot.latency_ms is not None:
            baseline = self._baseline("latency_ms")
            if baseline and snapshot.latency_ms > baseline * self._thresholds.latency_spike_factor:
                anomalies.append(
                    f"Latency spike: {snapshot.latency_ms:.1f}ms > {baseline:.1f}ms × "
                    f"{self._thresholds.latency_spike_factor}"
                )

        return anomalies

    def _fire_alert(self, snapshot: PerformanceSnapshot, anomalies: list[str]) -> None:
        try:
            event = AlertEvent(
                title=f"Performance Degradation — Epoch {snapshot.epoch}",
                message="\n".join(anomalies),
                severity=AlertSeverity.WARNING,
                run_id=self._run_id,
                epoch=snapshot.epoch,
                metadata={"timestamp": snapshot.timestamp, **snapshot.metadata},
            )
            self._alert_manager.alert(event)
        except Exception:
            pass  # alerting must never crash training

    @classmethod
    def from_env(cls, run_id: str = "") -> "PerformanceMonitor":
        """Create a PerformanceMonitor configured entirely from environment variables."""
        return cls(
            alert_manager=TrainingAlertManager.from_env(),
            thresholds=PerformanceThresholds.from_env(),
            run_id=run_id,
        )
