"""Comprehensive drift detection system for data, config, and model monitoring.

This module provides a unified drift detection system that monitors:
- Data drift (distribution changes)
- Config drift (configuration changes)
- Model drift (performance degradation)
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

__all__ = [
    "ComprehensiveDriftMonitor",
    "DriftAlert",
    "DriftDetector",
    "DriftType",
]


@dataclass
class DriftAlert:
    """Alert for detected drift.

    Attributes:
        drift_type: Type of drift detected
        severity: Severity level (low, medium, high, critical)
        message: Human-readable description
        details: Additional details dict
        timestamp: When drift was detected
    """

    drift_type: str
    severity: str
    message: str
    details: dict[str, Any]
    timestamp: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert alert to dict."""
        return {
            "drift_type": self.drift_type,
            "severity": self.severity,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp,
        }


class DriftType:
    """Drift type constants."""

    DATA = "data_drift"
    CONFIG = "config_drift"
    MODEL = "model_drift"
    CHECKPOINT = "checkpoint_drift"
    ENVIRONMENT = "environment_drift"


class DriftDetector:
    """Base class for drift detection."""

    def __init__(self, threshold: float = 0.1):
        """Initialize drift detector.

        Args:
            threshold: Threshold for drift detection (0.0 to 1.0)
        """
        self.threshold = threshold
        self.alerts: list[DriftAlert] = []

    def detect(self, current: Any, baseline: Any) -> bool:
        """Detect drift between current and baseline.

        Args:
            current: Current value/state
            baseline: Baseline value/state

        Returns:
            True if drift detected

        Note:
            Subclasses must implement this method.
        """
        raise TypeError(
            f"{self.__class__.__name__}.detect() must be implemented by subclass. "
            f"Use DataDriftDetector, ConfigDriftDetector, or ModelDriftDetector."
        )

    def add_alert(self, alert: DriftAlert):
        """Add drift alert."""
        self.alerts.append(alert)
        logger.warning(f"Drift detected: {alert.message}")

    def get_alerts(self) -> list[DriftAlert]:
        """Get all alerts."""
        return self.alerts

    def clear_alerts(self) -> None:
        """Clear all alerts."""
        self.alerts = []


class DataDriftDetector(DriftDetector):
    """Detect data distribution drift."""

    def detect(self, current_stats: dict[str, float], baseline_stats: dict[str, float]) -> bool:
        """Detect data drift using statistical comparison.

        Args:
            current_stats: Current data statistics (mean, std, etc.)
            baseline_stats: Baseline statistics

        Returns:
            True if drift detected
        """
        drift_detected = False

        # Compare means
        if "mean" in current_stats and "mean" in baseline_stats:
            mean_diff = abs(current_stats["mean"] - baseline_stats["mean"])
            if mean_diff > self.threshold:
                self.add_alert(
                    DriftAlert(
                        drift_type=DriftType.DATA,
                        severity="high",
                        message=f"Mean shifted by {mean_diff:.4f}",
                        details={
                            "current_mean": current_stats["mean"],
                            "baseline_mean": baseline_stats["mean"],
                        },
                    )
                )
                drift_detected = True

        # Compare standard deviations
        if "std" in current_stats and "std" in baseline_stats:
            std_diff = abs(current_stats["std"] - baseline_stats["std"])
            if std_diff > self.threshold:
                self.add_alert(
                    DriftAlert(
                        drift_type=DriftType.DATA,
                        severity="medium",
                        message=f"Std deviation changed by {std_diff:.4f}",
                        details={
                            "current_std": current_stats["std"],
                            "baseline_std": baseline_stats["std"],
                        },
                    )
                )
                drift_detected = True

        return drift_detected


class ConfigDriftDetector(DriftDetector):
    """Detect configuration drift."""

    def detect(self, current_config: dict[str, Any], baseline_config: dict[str, Any]) -> bool:
        """Detect config drift by comparing configurations.

        Args:
            current_config: Current configuration
            baseline_config: Baseline configuration

        Returns:
            True if drift detected
        """
        from codex_ml.utils.config_drift import ConfigDrift

        drift = ConfigDrift(current_config)
        baseline = ConfigDrift(baseline_config)
        diff = drift.compare(baseline)

        drift_detected = False

        if diff["added"]:
            self.add_alert(
                DriftAlert(
                    drift_type=DriftType.CONFIG,
                    severity="medium",
                    message=f"Config keys added: {diff['added']}",
                    details={"added": diff["added"]},
                )
            )
            drift_detected = True

        if diff["removed"]:
            self.add_alert(
                DriftAlert(
                    drift_type=DriftType.CONFIG,
                    severity="high",
                    message=f"Config keys removed: {diff['removed']}",
                    details={"removed": diff["removed"]},
                )
            )
            drift_detected = True

        if diff["modified"]:
            self.add_alert(
                DriftAlert(
                    drift_type=DriftType.CONFIG,
                    severity="high",
                    message=f"Config values modified: {diff['modified']}",
                    details={"modified": diff["modified"]},
                )
            )
            drift_detected = True

        return drift_detected


class ModelDriftDetector(DriftDetector):
    """Detect model performance drift."""

    def detect(self, current_metrics: dict[str, float], baseline_metrics: dict[str, float]) -> bool:
        """Detect model drift by comparing performance metrics.

        Args:
            current_metrics: Current model metrics
            baseline_metrics: Baseline metrics

        Returns:
            True if drift detected
        """
        drift_detected = False

        for metric_name in baseline_metrics:
            if metric_name not in current_metrics:
                continue

            current_val = current_metrics[metric_name]
            baseline_val = baseline_metrics[metric_name]

            # Calculate relative change
            if baseline_val != 0:
                rel_change = abs(current_val - baseline_val) / abs(baseline_val)
            else:
                rel_change = abs(current_val - baseline_val)

            if rel_change > self.threshold:
                # Determine severity based on change magnitude
                if rel_change > 0.5:
                    severity = "critical"
                elif rel_change > 0.3:
                    severity = "high"
                elif rel_change > 0.15:
                    severity = "medium"
                else:
                    severity = "low"

                self.add_alert(
                    DriftAlert(
                        drift_type=DriftType.MODEL,
                        severity=severity,
                        message=f"{metric_name} changed by {rel_change * 100:.1f}%",
                        details={
                            "metric": metric_name,
                            "current": current_val,
                            "baseline": baseline_val,
                            "relative_change": rel_change,
                        },
                    )
                )
                drift_detected = True

        return drift_detected


class ComprehensiveDriftMonitor:
    """Comprehensive drift monitoring system.

    Monitors data, config, and model drift with unified alerting.
    """

    def __init__(
        self,
        data_threshold: float = 0.1,
        config_threshold: float = 0.0,
        model_threshold: float = 0.1,
    ):
        """Initialize comprehensive drift monitor.

        Args:
            data_threshold: Threshold for data drift
            config_threshold: Threshold for config drift (0.0 = any change)
            model_threshold: Threshold for model drift
        """
        self.data_detector = DataDriftDetector(threshold=data_threshold)
        self.config_detector = ConfigDriftDetector(threshold=config_threshold)
        self.model_detector = ModelDriftDetector(threshold=model_threshold)

        self.monitoring_enabled = True

    def monitor_all(
        self,
        current_data_stats: Optional[dict[str, float]] = None,
        baseline_data_stats: Optional[dict[str, float]] = None,
        current_config: Optional[dict[str, Any]] = None,
        baseline_config: Optional[dict[str, Any]] = None,
        current_metrics: Optional[dict[str, float]] = None,
        baseline_metrics: Optional[dict[str, float]] = None,
    ) -> dict[str, bool]:
        """Monitor all types of drift.

        Args:
            current_data_stats: Current data statistics
            baseline_data_stats: Baseline data statistics
            current_config: Current configuration
            baseline_config: Baseline configuration
            current_metrics: Current model metrics
            baseline_metrics: Baseline model metrics

        Returns:
            dict mapping drift type to detected status
        """
        if not self.monitoring_enabled:
            return {}

        results = {}

        # Check data drift
        if current_data_stats and baseline_data_stats:
            results["data"] = self.data_detector.detect(current_data_stats, baseline_data_stats)

        # Check config drift
        if current_config and baseline_config:
            results["config"] = self.config_detector.detect(current_config, baseline_config)

        # Check model drift
        if current_metrics and baseline_metrics:
            results["model"] = self.model_detector.detect(current_metrics, baseline_metrics)

        return results

    def get_all_alerts(self) -> list[DriftAlert]:
        """Get all alerts from all detectors."""
        alerts = []
        alerts.extend(self.data_detector.get_alerts())
        alerts.extend(self.config_detector.get_alerts())
        alerts.extend(self.model_detector.get_alerts())
        return alerts

    def clear_all_alerts(self) -> None:
        """Clear alerts from all detectors."""
        self.data_detector.clear_alerts()
        self.config_detector.clear_alerts()
        self.model_detector.clear_alerts()

    def save_alerts(self, path: Path | str):
        """Save alerts to JSON file.

        Args:
            path: Path where alerts will be saved
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        alerts_data = [alert.to_dict() for alert in self.get_all_alerts()]

        with open(path, "w", encoding="utf-8") as f:
            json.dump(alerts_data, f, indent=2)

        logger.info(f"Saved {len(alerts_data)} drift alerts to {path}")

    def has_critical_drift(self) -> bool:
        """Check if any critical drift detected.

        Returns:
            True if critical drift detected
        """
        alerts = self.get_all_alerts()
        return any(alert.severity == "critical" for alert in alerts)

    def get_drift_summary(self) -> dict[str, Any]:
        """Get summary of detected drift.

        Returns:
            Summary dict with counts by type and severity
        """
        alerts = self.get_all_alerts()

        summary: dict[str, Any] = {
            "total_alerts": len(alerts),
            "by_type": {},
            "by_severity": {},
            "critical_count": 0,
        }

        for alert in alerts:
            # Count by type
            if alert.drift_type not in summary["by_type"]:
                summary["by_type"][alert.drift_type] = 0
            summary["by_type"][alert.drift_type] += 1

            # Count by severity
            if alert.severity not in summary["by_severity"]:
                summary["by_severity"][alert.severity] = 0
            summary["by_severity"][alert.severity] += 1

            # Count critical
            if alert.severity == "critical":
                summary["critical_count"] += 1

        return summary
