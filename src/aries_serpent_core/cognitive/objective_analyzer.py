"""
Cognitive Brain - Objective Analyzer Module (Plan 3 Phase 3.1)

This module implements the Metric Analysis Engine for autonomous objective
adjustment based on real-time metrics, trends, and codebase state.

Features:
- Health indicator tracking (coverage, security, CI/CD, docs)
- Trend analysis (improving/degrading detection)
- Threshold breach detection
- Anomaly detection
- Correlation analysis
"""

import json
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


class MetricType(Enum):
    """
    Types of metrics tracked by the analyzer.

    Units for each metric:
    - COVERAGE: percentage (0-100), e.g., 75.0 for 75% coverage
    - SECURITY: count of vulnerabilities, e.g., 0 for no vulnerabilities
    - CI_CD: percentage pass rate (0-100), e.g., 95.0 for 95% pass rate
    - DOCUMENTATION: days since last update, e.g., 30 for 30 days old
    - BUILD_TIME: seconds, e.g., 300 for 5 minutes
    - SESSION_EFFECTIVENESS: percentage (0-100), e.g., 80.0 for 80% effective
    - TEST_SUCCESS_RATE: percentage (0-100), e.g., 100.0 for all tests passing
    """

    COVERAGE = "coverage"
    SECURITY = "security"
    CI_CD = "ci_cd"
    DOCUMENTATION = "documentation"
    BUILD_TIME = "build_time"
    SESSION_EFFECTIVENESS = "session_effectiveness"
    # Note: TEST_SUCCESS_RATE refers to test success percentage, not a password
    TEST_SUCCESS_RATE = "test_success_rate"


class TrendDirection(Enum):
    """Direction of metric trends."""

    IMPROVING = "improving"
    STABLE = "stable"
    DEGRADING = "degrading"
    UNKNOWN = "unknown"


class AlertSeverity(Enum):
    """Severity levels for metric alerts."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class MetricValue:
    """A single metric measurement."""

    metric_type: MetricType
    value: float
    timestamp: datetime
    context: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "metric_type": self.metric_type.value,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MetricValue":
        """Create from dictionary."""
        return cls(
            metric_type=MetricType(data["metric_type"]),
            value=data["value"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            context=data.get("context", {}),
        )


@dataclass
class MetricThreshold:
    """Threshold configuration for a metric."""

    metric_type: MetricType
    target: float
    warning_threshold: float
    critical_threshold: float
    comparison: str = "gte"  # gte (greater than or equal) or lte (less than or equal)

    def check_value(self, value: float) -> tuple[bool, AlertSeverity | None]:
        """
        Check if value breaches threshold.
        Returns (is_ok, severity) where severity is None if ok.
        """
        if self.comparison == "gte":
            if value >= self.target:
                return True, None
            if value >= self.warning_threshold:
                return False, AlertSeverity.WARNING
            return False, AlertSeverity.CRITICAL
        # lte
        if value <= self.target:
            return True, None
        if value <= self.warning_threshold:
            return False, AlertSeverity.WARNING
        return False, AlertSeverity.CRITICAL


@dataclass
class MetricAlert:
    """An alert generated from metric analysis."""

    metric_type: MetricType
    severity: AlertSeverity
    message: str
    current_value: float
    threshold_value: float
    timestamp: datetime
    acknowledged: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "metric_type": self.metric_type.value,
            "severity": self.severity.value,
            "message": self.message,
            "current_value": self.current_value,
            "threshold_value": self.threshold_value,
            "timestamp": self.timestamp.isoformat(),
            "acknowledged": self.acknowledged,
        }


@dataclass
class TrendAnalysis:
    """Result of trend analysis for a metric."""

    metric_type: MetricType
    direction: TrendDirection
    slope: float
    r_squared: float
    data_points: int
    period_days: int
    start_value: float
    end_value: float
    change_percent: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "metric_type": self.metric_type.value,
            "direction": self.direction.value,
            "slope": self.slope,
            "r_squared": self.r_squared,
            "data_points": self.data_points,
            "period_days": self.period_days,
            "start_value": self.start_value,
            "end_value": self.end_value,
            "change_percent": self.change_percent,
        }


@dataclass
class HealthReport:
    """Overall health report combining all metrics."""

    timestamp: datetime
    overall_status: str  # healthy, warning, critical
    metrics: dict[MetricType, float]
    alerts: list[MetricAlert]
    trends: list[TrendAnalysis]
    recommendations: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "overall_status": self.overall_status,
            "metrics": {k.value: v for k, v in self.metrics.items()},
            "alerts": [a.to_dict() for a in self.alerts],
            "trends": [t.to_dict() for t in self.trends],
            "recommendations": self.recommendations,
        }


class MetricStore:
    """Persistent storage for metric history."""

    def __init__(self, store_path: Path | None = None):
        """Initialize the metric store."""
        if store_path is None:
            store_path = Path(".codex/cognitive_brain/metric_store.json")
        self.store_path = store_path
        self._metrics: dict[str, list[dict[str, Any]]] = {}
        self._load()

    def _load(self) -> None:
        """Load metrics from file."""
        if self.store_path.exists():
            try:
                with open(self.store_path) as f:
                    self._metrics = json.load(f)
            except (OSError, json.JSONDecodeError):
                self._metrics = {}

    def _save(self) -> None:
        """Save metrics to file."""
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.store_path, "w") as f:
            json.dump(self._metrics, f, indent=2)

    def add_metric(self, metric: MetricValue) -> None:
        """Add a metric value to the store."""
        key = metric.metric_type.value
        if key not in self._metrics:
            self._metrics[key] = []
        self._metrics[key].append(metric.to_dict())
        self._save()

    def get_metrics(self, metric_type: MetricType, days: int = 30) -> list[MetricValue]:
        """Get metrics for a type within the specified days."""
        key = metric_type.value
        if key not in self._metrics:
            return []

        cutoff = datetime.now(timezone.utc).timestamp() - (days * 86400)
        result = []
        for data in self._metrics[key]:
            mv = MetricValue.from_dict(data)
            if mv.timestamp.timestamp() >= cutoff:
                result.append(mv)
        return sorted(result, key=lambda x: x.timestamp)

    def get_latest(self, metric_type: MetricType) -> MetricValue | None:
        """Get the most recent metric value."""
        metrics = self.get_metrics(metric_type, days=365)
        return metrics[-1] if metrics else None


class TrendAnalyzer:
    """Analyzes trends in metric data."""

    def __init__(self, min_data_points: int = 3):
        """Initialize the trend analyzer."""
        self.min_data_points = min_data_points

    def analyze(self, metrics: list[MetricValue], period_days: int = 7) -> TrendAnalysis | None:
        """
        Analyze the trend of a metric series.

        Uses linear regression to determine trend direction and strength.
        """
        if len(metrics) < self.min_data_points:
            return None

        # Filter to period
        now = datetime.now(timezone.utc)
        cutoff = now.timestamp() - (period_days * 86400)
        filtered = [m for m in metrics if m.timestamp.timestamp() >= cutoff]

        if len(filtered) < self.min_data_points:
            return None

        # Extract values and normalize timestamps
        start_ts = filtered[0].timestamp.timestamp()
        x_values = [(m.timestamp.timestamp() - start_ts) / 86400 for m in filtered]
        y_values = [m.value for m in filtered]

        # Calculate linear regression
        n = len(x_values)
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values, strict=False))
        sum_x2 = sum(x * x for x in x_values)

        # Slope and intercept
        denominator = n * sum_x2 - sum_x * sum_x
        slope = 0.0 if abs(denominator) < 1e-10 else (n * sum_xy - sum_x * sum_y) / denominator

        # R-squared (coefficient of determination)
        mean_y = sum_y / n
        ss_tot = sum((y - mean_y) ** 2 for y in y_values)
        ss_res = sum(
            (y - (slope * x + (sum_y - slope * sum_x) / n)) ** 2
            for x, y in zip(x_values, y_values, strict=False)
        )
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

        # Determine trend direction
        if abs(slope) < 0.01:
            direction = TrendDirection.STABLE
        elif slope > 0:
            direction = TrendDirection.IMPROVING
        else:
            direction = TrendDirection.DEGRADING

        # Calculate change percent
        start_value = filtered[0].value
        end_value = filtered[-1].value
        change_percent = (end_value - start_value) / start_value * 100 if start_value > 0 else 0.0

        return TrendAnalysis(
            metric_type=filtered[0].metric_type,
            direction=direction,
            slope=slope,
            r_squared=r_squared,
            data_points=len(filtered),
            period_days=period_days,
            start_value=start_value,
            end_value=end_value,
            change_percent=change_percent,
        )


class AnomalyDetector:
    """Detects anomalies in metric data."""

    def __init__(self, z_threshold: float = 2.0):
        """
        Initialize the anomaly detector.

        Args:
            z_threshold: Number of standard deviations for anomaly detection
        """
        self.z_threshold = z_threshold

    def detect(self, metrics: list[MetricValue]) -> list[MetricValue]:
        """
        Detect anomalies in the metric series.

        Returns a list of metric values that are anomalies.
        """
        if len(metrics) < 3:
            return []

        values = [m.value for m in metrics]
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        std_dev = math.sqrt(variance) if variance > 0 else 0

        if std_dev == 0:
            return []

        anomalies = []
        for metric in metrics:
            z_score = abs((metric.value - mean) / std_dev)
            if z_score > self.z_threshold:
                anomalies.append(metric)

        return anomalies


class CorrelationAnalyzer:
    """Analyzes correlations between metrics."""

    def analyze_correlation(
        self, metrics_a: list[MetricValue], metrics_b: list[MetricValue]
    ) -> float | None:
        """
        Calculate Pearson correlation coefficient between two metric series.

        Returns correlation coefficient (-1 to 1) or None if insufficient data.
        """
        if len(metrics_a) < 3 or len(metrics_b) < 3:
            return None

        # Align by timestamp (approximate matching)
        aligned_a = []
        aligned_b = []

        for ma in metrics_a:
            # Find closest metric in b
            closest = min(
                metrics_b,
                key=lambda mb: abs(ma.timestamp.timestamp() - mb.timestamp.timestamp()),
            )
            # Only match if within 1 hour
            if abs(ma.timestamp.timestamp() - closest.timestamp.timestamp()) < 3600:
                aligned_a.append(ma.value)
                aligned_b.append(closest.value)

        if len(aligned_a) < 3:
            return None

        # Calculate Pearson correlation
        n = len(aligned_a)
        mean_a = sum(aligned_a) / n
        mean_b = sum(aligned_b) / n

        numerator = sum(
            (a - mean_a) * (b - mean_b) for a, b in zip(aligned_a, aligned_b, strict=False)
        )
        sum_sq_a = sum((a - mean_a) ** 2 for a in aligned_a)
        sum_sq_b = sum((b - mean_b) ** 2 for b in aligned_b)

        denominator = math.sqrt(sum_sq_a * sum_sq_b)

        if denominator == 0:
            return 0.0

        return numerator / denominator


class ObjectiveAnalyzer:
    """
    Main class for analyzing codebase metrics and generating health reports.

    This is the core component of Plan 3 Phase 3.1: Metric Analysis Engine.
    """

    # Default thresholds
    DEFAULT_THRESHOLDS = {
        MetricType.COVERAGE: MetricThreshold(
            MetricType.COVERAGE,
            target=70.0,
            warning_threshold=60.0,
            critical_threshold=50.0,
            comparison="gte",
        ),
        MetricType.SECURITY: MetricThreshold(
            MetricType.SECURITY,
            target=0,
            warning_threshold=3,
            critical_threshold=10,
            comparison="lte",
        ),
        MetricType.CI_CD: MetricThreshold(
            MetricType.CI_CD,
            target=100.0,
            warning_threshold=95.0,
            critical_threshold=90.0,
            comparison="gte",
        ),
        MetricType.DOCUMENTATION: MetricThreshold(
            MetricType.DOCUMENTATION,
            target=30,
            warning_threshold=60,
            critical_threshold=90,
            comparison="lte",  # days since update
        ),
        MetricType.TEST_SUCCESS_RATE: MetricThreshold(
            MetricType.TEST_SUCCESS_RATE,
            target=100.0,
            warning_threshold=95.0,
            critical_threshold=90.0,
            comparison="gte",
        ),
        MetricType.BUILD_TIME: MetricThreshold(
            MetricType.BUILD_TIME,
            target=300,
            warning_threshold=600,
            critical_threshold=900,
            comparison="lte",  # seconds
        ),
    }

    def __init__(
        self,
        store: MetricStore | None = None,
        thresholds: dict[MetricType, MetricThreshold] | None = None,
    ):
        """Initialize the objective analyzer."""
        self.store = store or MetricStore()
        self.thresholds = thresholds or self.DEFAULT_THRESHOLDS.copy()
        self.trend_analyzer = TrendAnalyzer()
        self.anomaly_detector = AnomalyDetector()
        self.correlation_analyzer = CorrelationAnalyzer()

    def record_metric(
        self, metric_type: MetricType, value: float, context: dict[str, Any] | None = None
    ) -> MetricValue:
        """Record a new metric value."""
        metric = MetricValue(
            metric_type=metric_type,
            value=value,
            timestamp=datetime.now(timezone.utc),
            context=context or {},
        )
        self.store.add_metric(metric)
        return metric

    def check_threshold(
        self, metric_type: MetricType, value: float | None = None
    ) -> tuple[bool, MetricAlert | None]:
        """
        Check if a metric breaches its threshold.

        Args:
            metric_type: Type of metric to check
            value: Value to check (uses latest if None)

        Returns:
            Tuple of (is_ok, alert) where alert is None if ok
        """
        if value is None:
            latest = self.store.get_latest(metric_type)
            if latest is None:
                return True, None
            value = latest.value

        threshold = self.thresholds.get(metric_type)
        if threshold is None:
            return True, None

        is_ok, severity = threshold.check_value(value)
        if is_ok:
            return True, None

        alert = MetricAlert(
            metric_type=metric_type,
            severity=severity,  # type: ignore
            message=f"{metric_type.value} is at {value}, threshold is {threshold.target}",
            current_value=value,
            threshold_value=threshold.target,
            timestamp=datetime.now(timezone.utc),
        )
        return False, alert

    def analyze_trend(self, metric_type: MetricType, period_days: int = 7) -> TrendAnalysis | None:
        """Analyze the trend for a specific metric."""
        metrics = self.store.get_metrics(metric_type, days=period_days + 7)
        return self.trend_analyzer.analyze(metrics, period_days)

    def detect_anomalies(self, metric_type: MetricType) -> list[MetricValue]:
        """Detect anomalies in a metric's history."""
        metrics = self.store.get_metrics(metric_type, days=30)
        return self.anomaly_detector.detect(metrics)

    def analyze_correlation(self, metric_a: MetricType, metric_b: MetricType) -> float | None:
        """Analyze correlation between two metrics."""
        metrics_a = self.store.get_metrics(metric_a, days=30)
        metrics_b = self.store.get_metrics(metric_b, days=30)
        return self.correlation_analyzer.analyze_correlation(metrics_a, metrics_b)

    def generate_health_report(self) -> HealthReport:
        """Generate a comprehensive health report."""
        now = datetime.now(timezone.utc)

        # Collect current metrics
        current_metrics: dict[MetricType, float] = {}
        alerts: list[MetricAlert] = []

        for metric_type in MetricType:
            latest = self.store.get_latest(metric_type)
            if latest:
                current_metrics[metric_type] = latest.value
                is_ok, alert = self.check_threshold(metric_type, latest.value)
                if not is_ok and alert:
                    alerts.append(alert)

        # Analyze trends
        trends: list[TrendAnalysis] = []
        for metric_type in MetricType:
            trend = self.analyze_trend(metric_type)
            if trend:
                trends.append(trend)

        # Generate recommendations
        recommendations = self._generate_recommendations(current_metrics, alerts, trends)

        # Determine overall status
        if any(a.severity == AlertSeverity.CRITICAL for a in alerts):
            overall_status = "critical"
        elif any(a.severity == AlertSeverity.WARNING for a in alerts):
            overall_status = "warning"
        else:
            overall_status = "healthy"

        return HealthReport(
            timestamp=now,
            overall_status=overall_status,
            metrics=current_metrics,
            alerts=alerts,
            trends=trends,
            recommendations=recommendations,
        )

    def _generate_recommendations(
        self,
        metrics: dict[MetricType, float],
        alerts: list[MetricAlert],
        trends: list[TrendAnalysis],
    ) -> list[str]:
        """Generate recommendations based on analysis."""
        recommendations = []

        # Check for critical alerts
        for alert in alerts:
            if alert.severity == AlertSeverity.CRITICAL:
                recommendations.append(
                    f"CRITICAL: Address {alert.metric_type.value} immediately - "
                    f"current: {alert.current_value}, target: {alert.threshold_value}"
                )

        # Check for degrading trends
        for trend in trends:
            if trend.direction == TrendDirection.DEGRADING:
                recommendations.append(
                    f"TREND: {trend.metric_type.value} is degrading "
                    f"({trend.change_percent:.1f}% change over {trend.period_days} days)"
                )

        # Specific metric recommendations
        if MetricType.COVERAGE in metrics:
            coverage = metrics[MetricType.COVERAGE]
            if coverage < 70:
                recommendations.append(
                    f"Coverage is at {coverage:.1f}%. Consider a coverage sprint."
                )

        if MetricType.SECURITY in metrics:
            vulns = int(metrics[MetricType.SECURITY])
            if vulns > 0:
                recommendations.append(
                    f"There are {vulns} security vulnerabilities. Prioritize remediation."
                )

        # If everything is good
        if not recommendations:
            recommendations.append("All metrics are healthy. Consider stretch goals.")

        return recommendations

    def get_status_summary(self) -> dict[str, Any]:
        """Get a quick status summary."""
        report = self.generate_health_report()
        return {
            "status": report.overall_status,
            "alert_count": len(report.alerts),
            "critical_count": sum(1 for a in report.alerts if a.severity == AlertSeverity.CRITICAL),
            "metrics": {k.value: v for k, v in report.metrics.items()},
            "top_recommendation": report.recommendations[0] if report.recommendations else None,
        }


def create_analyzer(store_path: Path | None = None) -> ObjectiveAnalyzer:
    """Factory function to create an ObjectiveAnalyzer."""
    store = MetricStore(store_path) if store_path else MetricStore()
    return ObjectiveAnalyzer(store=store)


# Convenience functions
def record_coverage(value: float, context: dict[str, Any] | None = None) -> MetricValue:
    """Record a coverage metric."""
    analyzer = create_analyzer()
    return analyzer.record_metric(MetricType.COVERAGE, value, context)


def record_security_vulns(count: int, context: dict[str, Any] | None = None) -> MetricValue:
    """Record security vulnerability count."""
    analyzer = create_analyzer()
    return analyzer.record_metric(MetricType.SECURITY, float(count), context)


def record_ci_pass_rate(rate: float, context: dict[str, Any] | None = None) -> MetricValue:
    """Record CI/CD pass rate."""
    analyzer = create_analyzer()
    return analyzer.record_metric(MetricType.CI_CD, rate, context)


def get_health_report() -> HealthReport:
    """Get the current health report."""
    analyzer = create_analyzer()
    return analyzer.generate_health_report()
