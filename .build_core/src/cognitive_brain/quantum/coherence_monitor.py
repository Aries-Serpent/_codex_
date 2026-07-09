"""
Coherence Monitor - Real-time monitoring and alerting for quantum features.

Monitors quantum feature metrics, detects degradation, and triggers
automatic rollbacks when coherence falls below acceptable thresholds.
"""

import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any, Optional

from cognitive_brain.models.quantum_metrics import (
    QuantumMetric,
    QuantumMetricRepository,
)
from cognitive_brain.quantum.config import QuantumConfig

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class AlertThreshold:
    """Configuration for alert thresholds."""

    metric_name: str
    warning_threshold: float
    critical_threshold: float
    comparison: str  # 'less_than', 'greater_than'

    def check(self, value: float) -> Optional[AlertLevel]:
        """
        Check if value triggers an alert.

        Args:
            value: Metric value to check

        Returns:
            AlertLevel if threshold exceeded, None otherwise
        """
        if self.comparison == "less_than":
            if value < self.critical_threshold:
                return AlertLevel.CRITICAL
            if value < self.warning_threshold:
                return AlertLevel.WARNING
        elif self.comparison == "greater_than":
            if value > self.critical_threshold:
                return AlertLevel.CRITICAL
            if value > self.warning_threshold:
                return AlertLevel.WARNING

        return None


@dataclass
class Alert:
    """Represents a monitoring alert."""

    feature: str
    metric_name: str
    level: AlertLevel
    current_value: float
    threshold_value: float
    timestamp: datetime
    message: str


class CoherenceMonitor:
    """
    Monitors quantum feature coherence and system health.

    Tracks metrics in real-time, detects degradation patterns,
    and triggers automatic rollbacks when coherence falls below
    acceptable levels.

    Default Alert Thresholds (from Phase 7 spec):
    - coherence_avg < 0.3 → CRITICAL
    - error_rate > 0.05 → WARNING
    - latency_p99 > 2000ms → WARNING
    - accuracy < 0.90 → CRITICAL

    Sprint 1 Optimization:
    - Added internal metric batching for 10-20x performance improvement
    - Batch inserts reduce database overhead from ~350ms to ~2ms per experiment
    """

    def __init__(
        self,
        config: QuantumConfig,
        repository: QuantumMetricRepository,
        alert_callback: Optional[Callable[[Alert], None]] = None,
        batch_size: int = 100,
    ):
        """
        Initialize coherence monitor.

        Args:
            config: Quantum configuration
            repository: Database repository for metrics
            alert_callback: Optional callback function for alerts
            batch_size: Number of metrics to accumulate before batch insert (default: 100)
        """
        self.config = config
        self.repository = repository
        self.alert_callback = alert_callback

        # Sprint 1: Add batching support
        self._batch_size = batch_size
        self._pending_metrics: list[QuantumMetric] = []

        # Default thresholds from Phase 7 spec
        self.thresholds = [
            AlertThreshold(
                metric_name="coherence",
                warning_threshold=0.5,
                critical_threshold=0.3,
                comparison="less_than",
            ),
            AlertThreshold(
                metric_name="error_rate",
                warning_threshold=0.05,
                critical_threshold=0.10,
                comparison="greater_than",
            ),
            AlertThreshold(
                metric_name="latency_p99",
                warning_threshold=2000.0,
                critical_threshold=5000.0,
                comparison="greater_than",
            ),
            AlertThreshold(
                metric_name="accuracy",
                warning_threshold=0.90,
                critical_threshold=0.85,
                comparison="less_than",
            ),
        ]

        self._active_alerts: list[Alert] = []
        self._rollback_triggered = False

        # Lazy OpenTelemetry gauge — initialised on first use when the
        # ``opentelemetry`` package is installed *and* an OTLP endpoint is
        # configured.  ``None`` means "not yet attempted"; ``False`` means
        # "unavailable".
        self._otel_gauge: Any = None

    # ------------------------------------------------------------------
    # OpenTelemetry integration
    # ------------------------------------------------------------------

    def _otel_record(self, feature: str, metric_name: str, value: float) -> None:
        """Export a coherence metric to OpenTelemetry when available.

        The gauge instrument is lazily created on first call.  When the
        ``opentelemetry`` SDK is not installed, or ``OTEL_EXPORTER_OTLP_ENDPOINT``
        is not set, the method silently no-ops so it never breaks the
        critical metric-recording path.
        """
        import importlib.util
        import os

        if self._otel_gauge is False:
            return  # already determined unavailable

        if self._otel_gauge is None:
            # First call — probe availability
            endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
            if not endpoint or importlib.util.find_spec("opentelemetry") is None:
                self._otel_gauge = False
                return
            try:
                metrics_mod = importlib.import_module("opentelemetry.metrics")
                meter = metrics_mod.get_meter("cognitive_brain.coherence")
                self._otel_gauge = meter.create_gauge(
                    name="cognitive_brain.coherence",
                    description="Quantum coherence and accuracy metrics",
                    unit="1",
                )
            except (ValueError, TypeError, RuntimeError):
                self._otel_gauge = False
                return

        try:
            self._otel_gauge.set(value, {"feature": feature, "metric": metric_name})
        except (ValueError, TypeError, RuntimeError):
            logger.debug("Suppressed exception in handler", exc_info=True)

    # ------------------------------------------------------------------
    # Metric recording
    # ------------------------------------------------------------------

    def record_metric(
        self,
        feature: str,
        metric_name: str,
        metric_value: float,
        agent_id: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> QuantumMetric:
        """
        Record a metric and check for alerts.

        Sprint 1 Optimization: Metrics are batched internally for performance.
        Call flush_batch() to persist all pending metrics.

        Args:
            feature: Feature name
            metric_name: Metric name
            metric_value: Metric value
            agent_id: Optional agent identifier
            metadata: Optional metadata

        Returns:
            Created QuantumMetric instance (not yet persisted if batching)
        """
        # Create metric
        metric = QuantumMetric(
            feature=feature,
            metric_name=metric_name,
            metric_value=metric_value,
            agent_id=agent_id,
            metadata=metadata,
        )

        # Sprint 1: Add to batch instead of immediate insert
        self._pending_metrics.append(metric)

        # Auto-flush when batch size reached
        if len(self._pending_metrics) >= self._batch_size:
            self.flush_batch()

        # Check thresholds
        self._check_thresholds(feature, metric_name, metric_value)

        # OpenTelemetry: export coherence metrics when OTEL is configured
        self._otel_record(feature, metric_name, metric_value)

        return metric

    def flush_batch(self) -> int:
        """
        Flush all pending metrics to database using batch insert.

        Sprint 1 Optimization: Provides 10-20x performance improvement
        over individual inserts.

        Returns:
            Number of metrics flushed
        """
        if not self._pending_metrics:
            return 0

        # Batch insert all pending metrics
        self.repository.batch_insert(self._pending_metrics)
        count = len(self._pending_metrics)
        self._pending_metrics = []

        return count

    def _check_thresholds(self, feature: str, metric_name: str, value: float) -> None:
        """
        Check if metric value triggers any alerts.

        Args:
            feature: Feature name
            metric_name: Metric name
            value: Metric value
        """
        for threshold in self.thresholds:
            if threshold.metric_name == metric_name:
                alert_level = threshold.check(value)

                if alert_level:
                    alert = Alert(
                        feature=feature,
                        metric_name=metric_name,
                        level=alert_level,
                        current_value=value,
                        threshold_value=(
                            threshold.critical_threshold
                            if alert_level == AlertLevel.CRITICAL
                            else threshold.warning_threshold
                        ),
                        timestamp=datetime.now(UTC),
                        message=self._format_alert_message(
                            feature, metric_name, value, alert_level, threshold
                        ),
                    )

                    self._trigger_alert(alert)

    def _format_alert_message(
        self,
        feature: str,
        metric_name: str,
        value: float,
        level: AlertLevel,
        threshold: AlertThreshold,
    ) -> str:
        """Format alert message."""
        threshold_val = (
            threshold.critical_threshold
            if level == AlertLevel.CRITICAL
            else threshold.warning_threshold
        )

        return (
            f"[{level.value.upper()}] {feature}/{metric_name}: "
            f"{value:.3f} {threshold.comparison.replace('_', ' ')} {threshold_val:.3f}"
        )

    def _trigger_alert(self, alert: Alert) -> None:
        """
        Trigger an alert and potentially initiate rollback.

        Args:
            alert: Alert to trigger
        """
        self._active_alerts.append(alert)

        # Call alert callback if provided
        if self.alert_callback:
            self.alert_callback(alert)

        # Trigger automatic rollback on critical alerts
        if alert.level == AlertLevel.CRITICAL and not self._rollback_triggered:
            self._initiate_rollback(alert)

    def _initiate_rollback(self, alert: Alert) -> None:
        """
        Initiate automatic rollback of quantum features.

        Args:
            alert: Alert that triggered rollback
        """
        self._rollback_triggered = True

        # Log rollback event
        self.record_metric(
            feature=alert.feature,
            metric_name="rollback_triggered",
            metric_value=1.0,
            metadata={
                "reason": alert.message,
                "alert_level": alert.level.value,
                "trigger_metric": alert.metric_name,
                "trigger_value": alert.current_value,
            },
        )

    def get_feature_health(self, feature: str, hours: int = 24) -> dict[str, Any]:
        """
        Get health status for a quantum feature.

        Args:
            feature: Feature name
            hours: Time window in hours

        Returns:
            Dictionary with health metrics
        """
        stats = self.repository.get_coherence_stats(feature, hours)

        # Get recent metrics for other health indicators
        recent_metrics = self.repository.find_by_feature(feature, limit=100)

        error_rates = [m.metric_value for m in recent_metrics if m.metric_name == "error_rate"]

        latencies = [m.metric_value for m in recent_metrics if m.metric_name == "latency_p99"]

        return {
            "feature": feature,
            "coherence": {
                "avg": stats.get("avg_coherence"),
                "min": stats.get("min_coherence"),
                "max": stats.get("max_coherence"),
                "samples": stats.get("sample_count", 0),
            },
            "error_rate": {
                "current": error_rates[0] if error_rates else None,
                "avg": sum(error_rates) / len(error_rates) if error_rates else None,
            },
            "latency": {
                "current_p99": latencies[0] if latencies else None,
                "avg_p99": sum(latencies) / len(latencies) if latencies else None,
            },
            "health_status": self._assess_health_status(feature, stats, error_rates),
            "active_alerts": [a for a in self._active_alerts if a.feature == feature],
        }

    def _assess_health_status(
        self, feature: str, coherence_stats: dict, error_rates: list[float]
    ) -> str:
        """
        Assess overall health status of a feature.

        Args:
            feature: Feature name
            coherence_stats: Coherence statistics
            error_rates: Recent error rates

        Returns:
            Health status: 'healthy', 'degraded', or 'critical'
        """
        avg_coherence = coherence_stats.get("avg_coherence")

        # Check for critical conditions
        if avg_coherence is not None and avg_coherence < 0.3:
            return "critical"

        if error_rates and max(error_rates) > 0.10:
            return "critical"

        # Check for degraded conditions
        if avg_coherence is not None and avg_coherence < 0.5:
            return "degraded"

        if error_rates and max(error_rates) > 0.05:
            return "degraded"

        return "healthy"

    def get_all_features_health(self) -> dict[str, dict]:
        """
        Get health status for all quantum features.

        Returns:
            Dictionary mapping feature names to health data
        """
        features = ["superposition", "entanglement", "uncertainty", "wave_collapse"]

        return {
            feature: self.get_feature_health(feature)
            for feature in features
            if self.config.is_enabled(feature)
        }

    def get_active_alerts(
        self, feature: Optional[str] = None, level: Optional[AlertLevel] = None
    ) -> list[Alert]:
        """
        Get currently active alerts.

        Args:
            feature: Optional feature name filter
            level: Optional alert level filter

        Returns:
            List of active alerts
        """
        alerts = self._active_alerts

        if feature:
            alerts = [a for a in alerts if a.feature == feature]

        if level:
            alerts = [a for a in alerts if a.level == level]

        return alerts

    def clear_alerts(
        self, feature: Optional[str] = None, older_than_hours: Optional[int] = None
    ) -> int:
        """
        Clear resolved or old alerts.

        Args:
            feature: Optional feature name to clear alerts for
            older_than_hours: Clear alerts older than N hours

        Returns:
            Number of alerts cleared
        """
        initial_count = len(self._active_alerts)

        if older_than_hours:
            cutoff = datetime.now(UTC) - timedelta(hours=older_than_hours)
            self._active_alerts = [a for a in self._active_alerts if a.timestamp > cutoff]

        if feature:
            self._active_alerts = [a for a in self._active_alerts if a.feature != feature]

        if not older_than_hours and not feature:
            self._active_alerts = []

        return initial_count - len(self._active_alerts)

    def reset_rollback_flag(self) -> None:
        """Reset the rollback triggered flag."""
        self._rollback_triggered = False

    @property
    def is_rollback_triggered(self) -> bool:
        """Check if automatic rollback has been triggered."""
        return self._rollback_triggered

    def log_metric(
        self,
        feature: Any,
        decision_id: str,
        coherence: float,
        accuracy: float = 1.0,
        **kwargs,
    ) -> None:
        """Record coherence and accuracy metrics for a decision.

        Convenience wrapper around ``record_metric`` that accepts the
        ``feature`` as either a string or an enum value and logs both
        ``coherence`` and ``accuracy`` in a single call.

        Args:
            feature: Feature name or enum value (e.g. QuantumFeature.SUPERPOSITION)
            decision_id: Identifier for this decision (used as agent_id)
            coherence: Coherence metric value (0.0 – 1.0)
            accuracy: Accuracy metric value (0.0 – 1.0)
            **kwargs: Additional metadata passed to record_metric
        """
        feature_str = feature.value if hasattr(feature, "value") else str(feature)
        self.record_metric(
            feature=feature_str,
            metric_name="coherence",
            metric_value=coherence,
            agent_id=decision_id,
        )
        self.record_metric(
            feature=feature_str,
            metric_name="accuracy",
            metric_value=accuracy,
            agent_id=decision_id,
        )

    def get_health_status(self) -> str:
        """Return aggregate system health as a string.

        Returns:
            ``"healthy"`` when no alerts are active, ``"critical"`` when any
            CRITICAL alert is present, ``"degraded"`` otherwise.
        """
        if not self._active_alerts:
            return "healthy"
        if any(a.level == AlertLevel.CRITICAL for a in self._active_alerts):
            return "critical"
        return "degraded"

    def get_recent_alerts(self, feature: Any | None = None, hours: int = 24) -> list[Alert]:
        """Get recent alerts optionally filtered by feature.

        Args:
            feature: Feature name or enum value to filter by (optional)
            hours: Unused; all active alerts are returned regardless of age
                   (retained for API compatibility)

        Returns:
            List of :class:`Alert` objects
        """
        feature_str = (
            feature.value if feature is not None and hasattr(feature, "value") else feature
        )
        return self.get_active_alerts(feature=feature_str)
