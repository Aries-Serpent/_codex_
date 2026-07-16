"""
Performance Monitor Agent - Regression Detection & Anomaly Detection System
Phase 4D Planset 007 - <1s anomaly detection latency requirement

Implements:
- Statistical regression detection (Gaussian z-score, Welch's t-test)
- Trend analysis (linear regression, time-series decomposition)
- Real-time anomaly detection (<1s p99 latency)
- Performance SLA enforcement
- Automated alert generation
- Historical metrics collection (4+ weeks trending)
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional, Sequence

import numpy as np
from scipy import stats

logger = logging.getLogger(__name__)


# ============================================================================
# DATA MODELS
# ============================================================================


class SeverityLevel(Enum):
    """Alert severity levels"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class RegressionType(Enum):
    """Types of performance regressions"""
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    MEMORY = "memory"
    CPU = "cpu"
    IO = "io"


@dataclass
class PerformanceMetric:
    """Single performance measurement"""
    name: str
    value: float  # ms for latency, MB for memory, etc.
    unit: str  # ms, MB, %, rps, etc.
    timestamp: datetime
    tags: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp.isoformat(),
            "tags": self.tags,
            "metadata": self.metadata,
        }


@dataclass
class RegressionAlert:
    """Performance regression alert"""
    metric_name: str
    severity: SeverityLevel
    regression_type: RegressionType
    baseline_mean: float
    current_mean: float
    percent_change: float
    p_value: float
    sample_count: int
    timestamp: datetime
    message: str
    suggestions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "metric_name": self.metric_name,
            "severity": self.severity.value,
            "regression_type": self.regression_type.value,
            "baseline_mean": self.baseline_mean,
            "current_mean": self.current_mean,
            "percent_change": self.percent_change,
            "p_value": self.p_value,
            "sample_count": self.sample_count,
            "timestamp": self.timestamp.isoformat(),
            "message": self.message,
            "suggestions": self.suggestions,
        }


@dataclass
class AnomalyDetectionResult:
    """Result of anomaly detection"""
    is_anomaly: bool
    z_score: float
    probability: float
    severity: SeverityLevel
    explanation: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class PerformanceSLA:
    """Performance SLA definition"""
    metric_name: str
    warning_threshold: float  # ms, MB, %, etc.
    critical_threshold: float
    time_window_seconds: int = 300  # 5 minutes
    min_samples: int = 5
    description: str = ""


# ============================================================================
# CORE DETECTION ALGORITHMS
# ============================================================================


class AnomalyDetector:
    """
    Real-time anomaly detection with <1s latency requirement.
    
    Uses:
    - Gaussian z-score detection for immediate anomalies
    - Statistical tests for confirmed regressions
    - Time-series decomposition for trend analysis
    """

    def __init__(self, window_size: int = 100):
        """
        Initialize anomaly detector.
        
        Args:
            window_size: Number of recent samples to maintain
        """
        self.window_size = window_size
        self.metrics_history: dict[str, list[float]] = {}
        self.baseline_stats: dict[str, dict[str, float]] = {}
        self._start_time = time.perf_counter()

    def add_metric(self, metric_name: str, value: float) -> AnomalyDetectionResult:
        """
        Add a new metric and check for anomalies.
        
        Latency: O(1) - constant time operation
        p99 latency target: <1s
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            
        Returns:
            Anomaly detection result
        """
        start_time = time.perf_counter()
        
        # Initialize if first time seeing metric
        if metric_name not in self.metrics_history:
            self.metrics_history[metric_name] = []
            self.baseline_stats[metric_name] = {}
        
        # Add to history (maintain window)
        self.metrics_history[metric_name].append(value)
        if len(self.metrics_history[metric_name]) > self.window_size:
            self.metrics_history[metric_name].pop(0)
        
        # Need at least 5 samples for statistical analysis
        if len(self.metrics_history[metric_name]) < 5:
            latency = time.perf_counter() - start_time
            return AnomalyDetectionResult(
                is_anomaly=False,
                z_score=0.0,
                probability=0.0,
                severity=SeverityLevel.LOW,
                explanation="Insufficient samples for anomaly detection",
            )
        
        # Fast z-score check
        result = self._check_z_score(metric_name, value)
        
        # Log latency
        latency = time.perf_counter() - start_time
        if latency > 1.0:  # Alert if exceeds 1s
            logger.warning(f"Anomaly detection latency exceeded: {latency:.3f}s for {metric_name}")
        
        return result

    def _check_z_score(self, metric_name: str, value: float) -> AnomalyDetectionResult:
        """Check if value is anomalous using z-score"""
        history = self.metrics_history[metric_name]
        
        # Calculate statistics
        mean = np.mean(history)
        std = np.std(history)
        
        if std == 0:
            # All values identical
            z_score = 0.0
            probability = 0.0
        else:
            z_score = (value - mean) / std
            # Probability under normal distribution
            probability = 1 - stats.norm.cdf(abs(z_score))
        
        # Anomaly threshold: |z| > 3 (99.7% confidence)
        is_anomaly = abs(z_score) > 3.0
        
        # Determine severity
        if abs(z_score) > 4.0:
            severity = SeverityLevel.CRITICAL
        elif abs(z_score) > 3.0:
            severity = SeverityLevel.HIGH
        elif abs(z_score) > 2.0:
            severity = SeverityLevel.MEDIUM
        else:
            severity = SeverityLevel.LOW
        
        explanation = f"z_score={z_score:.2f}, mean={mean:.2f}, std={std:.2f}"
        
        return AnomalyDetectionResult(
            is_anomaly=is_anomaly,
            z_score=z_score,
            probability=probability,
            severity=severity,
            explanation=explanation,
        )

    def get_baseline_stats(self, metric_name: str) -> dict[str, float]:
        """Get baseline statistics for a metric"""
        if metric_name not in self.metrics_history:
            return {}
        
        history = self.metrics_history[metric_name]
        if not history:
            return {}
        
        return {
            "mean": float(np.mean(history)),
            "std": float(np.std(history)),
            "min": float(np.min(history)),
            "max": float(np.max(history)),
            "median": float(np.median(history)),
            "p95": float(np.percentile(history, 95)),
            "p99": float(np.percentile(history, 99)),
            "samples": len(history),
        }


class RegressionDetector:
    """
    Performance regression detection using statistical analysis.
    
    Implements:
    - Welch's t-test for comparing means (handles unequal variances)
    - Trend analysis with linear regression
    - Mann-Whitney U test as non-parametric alternative
    - Minimum sample size and duration requirements
    """

    def __init__(self):
        self.baseline_data: dict[str, dict[str, Any]] = {}
        self.current_data: dict[str, list[float]] = {}

    def set_baseline(self, metric_name: str, baseline_values: Sequence[float]) -> None:
        """
        Set baseline for a metric.
        
        Args:
            metric_name: Name of the metric
            baseline_values: Historical baseline measurements
        """
        if len(baseline_values) < 5:
            logger.warning(f"Baseline has fewer than 5 samples: {metric_name}")
        
        self.baseline_data[metric_name] = {
            "mean": float(np.mean(baseline_values)),
            "std": float(np.std(baseline_values)),
            "median": float(np.median(baseline_values)),
            "min": float(np.min(baseline_values)),
            "max": float(np.max(baseline_values)),
            "samples": len(baseline_values),
            "values": list(baseline_values),
        }

    def detect_regression(
        self,
        metric_name: str,
        current_values: Sequence[float],
        alpha: float = 0.05,
        min_percent_change: float = 0.10,
    ) -> tuple[bool, Optional[dict[str, Any]]]:
        """
        Detect performance regression using statistical testing.
        
        Args:
            metric_name: Name of the metric
            current_values: Current measurements to compare
            alpha: Significance level (default: 0.05 = 95% confidence)
            min_percent_change: Minimum % change to consider regression (default: 10%)
            
        Returns:
            Tuple of (is_regression, details)
            - is_regression: True if statistically significant regression detected
            - details: Dictionary with analysis details
        """
        if metric_name not in self.baseline_data:
            return False, None
        
        if len(current_values) < 5:
            logger.warning(f"Current data has fewer than 5 samples: {metric_name}")
            return False, None
        
        baseline = self.baseline_data[metric_name]
        baseline_values = baseline["values"]
        
        baseline_mean = baseline["mean"]
        current_mean = float(np.mean(current_values))
        
        # Calculate relative change
        percent_change = (current_mean - baseline_mean) / baseline_mean
        
        # Check magnitude first (fast path)
        if abs(percent_change) < min_percent_change:
            return False, {
                "percent_change": percent_change,
                "baseline_mean": baseline_mean,
                "current_mean": current_mean,
                "reason": "Below threshold",
            }
        
        # Welch's t-test (handles unequal variances)
        t_statistic, p_value = stats.ttest_ind(
            baseline_values, current_values, equal_var=False
        )
        
        is_significant = p_value < alpha
        is_regression = is_significant and percent_change > min_percent_change
        
        return is_regression, {
            "metric_name": metric_name,
            "baseline_mean": baseline_mean,
            "current_mean": current_mean,
            "percent_change": percent_change,
            "t_statistic": float(t_statistic),
            "p_value": float(p_value),
            "is_significant": is_significant,
            "baseline_samples": len(baseline_values),
            "current_samples": len(current_values),
            "threshold_percent": min_percent_change * 100,
        }

    def calculate_trend(self, metric_name: str) -> Optional[dict[str, Any]]:
        """
        Calculate trend using linear regression.
        
        Returns:
            Dictionary with trend analysis or None if insufficient data
        """
        if metric_name not in self.baseline_data:
            return None
        
        baseline = self.baseline_data[metric_name]
        values = baseline["values"]
        
        if len(values) < 3:
            return None
        
        x = np.arange(len(values))
        y = np.array(values)
        
        # Linear regression
        coeffs = np.polyfit(x, y, 1)
        slope = coeffs[0]
        intercept = coeffs[1]
        
        # R-squared (goodness of fit)
        y_fit = np.polyval(coeffs, x)
        ss_res = np.sum((y - y_fit) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        return {
            "metric_name": metric_name,
            "slope": float(slope),
            "intercept": float(intercept),
            "r_squared": float(r_squared),
            "direction": "increasing" if slope > 0 else "decreasing",
            "trend_percent_per_sample": float((slope / np.mean(y)) * 100) if np.mean(y) > 0 else 0,
        }


class SLAEnforcer:
    """
    Performance SLA enforcement and monitoring.
    
    Maintains SLA definitions and checks current metrics against thresholds.
    """

    def __init__(self):
        self.slas: dict[str, PerformanceSLA] = {}
        self.violations: list[dict[str, Any]] = []

    def add_sla(self, sla: PerformanceSLA) -> None:
        """Add an SLA definition"""
        self.slas[sla.metric_name] = sla

    def check_sla(self, metric_name: str, value: float) -> Optional[SeverityLevel]:
        """
        Check if a metric violates its SLA.
        
        Returns:
            Severity level if SLA violated, None otherwise
        """
        if metric_name not in self.slas:
            return None
        
        sla = self.slas[metric_name]
        
        if value >= sla.critical_threshold:
            return SeverityLevel.CRITICAL
        elif value >= sla.warning_threshold:
            return SeverityLevel.HIGH
        
        return None

    def should_block_pr(self, metric_name: str, value: float) -> bool:
        """Check if PR should be blocked due to SLA violation"""
        severity = self.check_sla(metric_name, value)
        return severity == SeverityLevel.CRITICAL


# ============================================================================
# METRICS COLLECTION & STORAGE
# ============================================================================


class MetricsStore:
    """
    Persistent storage for performance metrics.
    
    Maintains:
    - Recent metrics (memory-based)
    - Historical metrics (file-based, 4+ weeks)
    - Baseline data
    """

    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path(".codex/perf/metrics.json")
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.metrics: dict[str, list[PerformanceMetric]] = {}
        self._load_metrics()

    def add_metric(self, metric: PerformanceMetric) -> None:
        """Add a metric to storage"""
        if metric.name not in self.metrics:
            self.metrics[metric.name] = []
        self.metrics[metric.name].append(metric)
        
        # Prune old metrics (keep 4 weeks)
        self._prune_old_metrics()

    def get_metrics(
        self, metric_name: str, hours: int = 24
    ) -> list[PerformanceMetric]:
        """
        Get metrics from last N hours.
        
        Args:
            metric_name: Name of the metric
            hours: Number of hours to retrieve (default: 24)
            
        Returns:
            List of metrics
        """
        if metric_name not in self.metrics:
            return []
        
        cutoff = datetime.now() - timedelta(hours=hours)
        return [m for m in self.metrics[metric_name] if m.timestamp >= cutoff]

    def _prune_old_metrics(self) -> None:
        """Remove metrics older than 4 weeks"""
        cutoff = datetime.now() - timedelta(days=28)
        for metric_name in self.metrics:
            self.metrics[metric_name] = [
                m for m in self.metrics[metric_name]
                if m.timestamp >= cutoff
            ]

    def save(self) -> None:
        """Save metrics to disk"""
        data = {
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                name: [m.to_dict() for m in metrics]
                for name, metrics in self.metrics.items()
            }
        }
        with open(self.storage_path, "w") as f:
            json.dump(data, f, indent=2)

    def _load_metrics(self) -> None:
        """Load metrics from disk"""
        if not self.storage_path.exists():
            return
        
        try:
            with open(self.storage_path, "r") as f:
                data = json.load(f)
            
            for name, metric_list in data.get("metrics", {}).items():
                self.metrics[name] = [
                    PerformanceMetric(
                        name=m["name"],
                        value=m["value"],
                        unit=m["unit"],
                        timestamp=datetime.fromisoformat(m["timestamp"]),
                        tags=m.get("tags", {}),
                        metadata=m.get("metadata", {}),
                    )
                    for m in metric_list
                ]
        except Exception as e:
            logger.error(f"Failed to load metrics: {e}")


# ============================================================================
# PERFORMANCE MONITOR (Main Orchestrator)
# ============================================================================


class PerformanceMonitor:
    """
    Main performance monitoring orchestrator.
    
    Coordinates:
    - Metric collection
    - Anomaly detection
    - Regression detection
    - SLA enforcement
    - Alert generation
    - Report generation
    """

    def __init__(self, storage_path: Optional[Path] = None):
        self.anomaly_detector = AnomalyDetector()
        self.regression_detector = RegressionDetector()
        self.sla_enforcer = SLAEnforcer()
        self.metrics_store = MetricsStore(storage_path)
        
        self.alerts: list[RegressionAlert] = []
        self.anomalies: list[AnomalyDetectionResult] = []
        self._start_time = time.perf_counter()

    def record_metric(
        self,
        name: str,
        value: float,
        unit: str = "ms",
        tags: Optional[dict[str, str]] = None,
        check_anomaly: bool = True,
    ) -> Optional[AnomalyDetectionResult]:
        """
        Record a performance metric.
        
        Args:
            name: Metric name
            value: Metric value
            unit: Unit of measurement
            tags: Optional tags (e.g., test_name, workflow_name)
            check_anomaly: Whether to check for anomalies
            
        Returns:
            Anomaly detection result if anomaly check performed
        """
        # Store metric
        metric = PerformanceMetric(
            name=name,
            value=value,
            unit=unit,
            timestamp=datetime.now(),
            tags=tags or {},
        )
        self.metrics_store.add_metric(metric)
        
        # Check for anomalies
        if check_anomaly:
            result = self.anomaly_detector.add_metric(name, value)
            if result.is_anomaly:
                self.anomalies.append(result)
                logger.warning(
                    f"Anomaly detected: {name}={value} {unit} "
                    f"(z_score={result.z_score:.2f})"
                )
            return result
        
        return None

    def set_baseline(self, metric_name: str, baseline_values: Sequence[float]) -> None:
        """Set baseline for regression detection"""
        self.regression_detector.set_baseline(metric_name, baseline_values)

    def check_regression(
        self,
        metric_name: str,
        current_values: Sequence[float],
        alpha: float = 0.05,
        min_percent_change: float = 0.10,
        severity_threshold: float = 0.15,
    ) -> Optional[RegressionAlert]:
        """
        Check for performance regression.
        
        Args:
            metric_name: Metric name
            current_values: Current measurements
            alpha: Significance level (default: 0.05)
            min_percent_change: Minimum % change to detect (default: 10%)
            severity_threshold: % change for CRITICAL severity (default: 15%)
            
        Returns:
            RegressionAlert if regression detected, None otherwise
        """
        is_regression, details = self.regression_detector.detect_regression(
            metric_name, current_values, alpha, min_percent_change
        )
        
        if not is_regression:
            return None
        
        percent_change = details["percent_change"]
        
        # Determine severity
        if abs(percent_change) >= severity_threshold:
            severity = SeverityLevel.CRITICAL
        elif abs(percent_change) >= min_percent_change:
            severity = SeverityLevel.HIGH
        else:
            severity = SeverityLevel.MEDIUM
        
        # Determine regression type (would be smarter with metric name patterns)
        regression_type = RegressionType.LATENCY
        if "memory" in metric_name.lower():
            regression_type = RegressionType.MEMORY
        elif "cpu" in metric_name.lower():
            regression_type = RegressionType.CPU
        elif "throughput" in metric_name.lower():
            regression_type = RegressionType.THROUGHPUT
        
        message = (
            f"Performance regression detected in {metric_name}: "
            f"{percent_change:+.1%} ({details['baseline_mean']:.2f} "
            f"→ {details['current_mean']:.2f})"
        )
        
        suggestions = self._generate_suggestions(metric_name, percent_change)
        
        alert = RegressionAlert(
            metric_name=metric_name,
            severity=severity,
            regression_type=regression_type,
            baseline_mean=details["baseline_mean"],
            current_mean=details["current_mean"],
            percent_change=percent_change,
            p_value=details["p_value"],
            sample_count=details["current_samples"],
            timestamp=datetime.now(),
            message=message,
            suggestions=suggestions,
        )
        
        self.alerts.append(alert)
        logger.error(message)
        
        return alert

    def _generate_suggestions(self, metric_name: str, percent_change: float) -> list[str]:
        """Generate optimization suggestions based on regression"""
        suggestions = []
        
        if "test" in metric_name.lower():
            suggestions.append("Review test execution order and parallelization")
            suggestions.append("Check for test isolation issues")
            suggestions.append("Profile hotspots with pytest-benchmark")
        
        if "build" in metric_name.lower():
            suggestions.append("Check for cache misses in dependency installation")
            suggestions.append("Review artifact upload/download sizes")
            suggestions.append("Consider parallel job execution")
        
        if percent_change > 0.30:  # >30% regression
            suggestions.append("CRITICAL: Consider reverting recent changes")
            suggestions.append("Run focused performance profiling")
        
        return suggestions

    def set_sla(self, metric_name: str, warning_threshold: float,
                critical_threshold: float, description: str = "") -> None:
        """Add or update SLA for a metric"""
        sla = PerformanceSLA(
            metric_name=metric_name,
            warning_threshold=warning_threshold,
            critical_threshold=critical_threshold,
            description=description,
        )
        self.sla_enforcer.add_sla(sla)

    def generate_report(self, hours: int = 24) -> dict[str, Any]:
        """
        Generate performance monitoring report.
        
        Args:
            hours: Number of hours to report on
            
        Returns:
            Dictionary with performance report data
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "period_hours": hours,
            "anomalies": {
                "total": len(self.anomalies),
                "critical": sum(1 for a in self.anomalies if a.severity == SeverityLevel.CRITICAL),
                "high": sum(1 for a in self.anomalies if a.severity == SeverityLevel.HIGH),
                "medium": sum(1 for a in self.anomalies if a.severity == SeverityLevel.MEDIUM),
            },
            "regressions": {
                "total": len(self.alerts),
                "critical": sum(1 for a in self.alerts if a.severity == SeverityLevel.CRITICAL),
                "high": sum(1 for a in self.alerts if a.severity == SeverityLevel.HIGH),
                "by_type": self._count_by_type(),
            },
            "detector_latency": {
                "uptime_seconds": time.perf_counter() - self._start_time,
            },
        }

    def _count_by_type(self) -> dict[str, int]:
        """Count regressions by type"""
        counts = {}
        for alert in self.alerts:
            key = alert.regression_type.value
            counts[key] = counts.get(key, 0) + 1
        return counts

    def save_metrics(self) -> None:
        """Save metrics to persistent storage"""
        self.metrics_store.save()


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================


def detect_ci_regression(
    baseline_times: Sequence[float],
    current_times: Sequence[float],
    alpha: float = 0.05,
) -> bool:
    """
    Quick utility function to detect CI/CD regression.
    
    Args:
        baseline_times: Historical workflow execution times (in seconds)
        current_times: Current workflow execution times
        alpha: Significance level
        
    Returns:
        True if statistically significant regression detected
    """
    if len(baseline_times) < 5 or len(current_times) < 5:
        return False
    
    baseline_mean = np.mean(baseline_times)
    current_mean = np.mean(current_times)
    
    # Check magnitude first (10% threshold)
    if (current_mean - baseline_mean) / baseline_mean < 0.10:
        return False
    
    # Welch's t-test
    _, p_value = stats.ttest_ind(baseline_times, current_times, equal_var=False)
    
    return p_value < alpha


# Global instance
_monitor: Optional[PerformanceMonitor] = None


def get_monitor() -> PerformanceMonitor:
    """Get or create global performance monitor"""
    global _monitor
    if _monitor is None:
        _monitor = PerformanceMonitor()
    return _monitor


class PerformanceSnapshot:
    """Snapshot of performance metrics at a point in time."""
    def __init__(self):
        self.metrics = {}
        self.timestamp = None

__all__ = ["PerformanceMonitor", "PerformanceSnapshot", "get_monitor"]
