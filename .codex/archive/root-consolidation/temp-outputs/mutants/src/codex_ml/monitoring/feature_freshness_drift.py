"""Integration of feature freshness with drift detection."""

from __future__ import annotations

import logging
from typing import Any

from codex_ml.features.monitoring import FeatureHealthMonitor, FeatureHealthStatus

logger = logging.getLogger(__name__)

__all__ = ["FeatureFreshnessDriftDetector"]


class FeatureFreshnessDriftDetector:
    """Detect drift with feature freshness awareness."""

    def __init__(
        self,
        health_monitor: FeatureHealthMonitor,
        freshness_threshold_hours: int = 24,
    ):
        """Initialize freshness-aware drift detector.

        Args:
            health_monitor: Feature health monitor
            freshness_threshold_hours: Hours before feature is stale
        """
        self.health_monitor = health_monitor
        self.freshness_threshold_hours = freshness_threshold_hours

    def check_features_before_drift_detection(
        self,
        feature_names: list[str],
    ) -> dict[str, FeatureHealthStatus]:
        """Check feature freshness before drift detection.

        Args:
            feature_names: Features to check

        Returns:
            Dictionary of feature health status
        """
        health_status = self.health_monitor.check_all_features(feature_names)

        # Log warnings for stale features
        stale_features = [name for name, status in health_status.items() if not status.is_healthy]

        if stale_features:
            logger.warning(f"Stale features detected before drift check: {stale_features}")

        return health_status

    def get_drift_report_with_freshness(
        self,
        feature_names: list[str],
        drift_scores: dict[str, float],
    ) -> dict[str, dict[str, Any]]:
        """Generate drift report including freshness information.

        Args:
            feature_names: Feature names
            drift_scores: Drift scores per feature

        Returns:
            Combined drift and freshness report
        """
        health_status = self.check_features_before_drift_detection(feature_names)

        report = {}
        for name in feature_names:
            status = health_status.get(name)
            drift_score = drift_scores.get(name, 0.0)

            report[name] = {
                "drift_score": drift_score,
                "is_fresh": status.is_healthy if status else False,
                "freshness_level": status.freshness_level if status else "UNKNOWN",
                "freshness_minutes": status.freshness_minutes if status else float("inf"),
                "warnings": status.warnings if status else [],
            }

        return report

    def should_skip_drift_check(self, feature_name: str) -> bool:
        """Determine if drift check should be skipped due to staleness.

        Args:
            feature_name: Feature name

        Returns:
            True if drift check should be skipped
        """
        status = self.health_monitor.check_feature_health(feature_name)

        # Skip if feature is very stale (>48 hours)
        if status.freshness_minutes > (self.freshness_threshold_hours * 2 * 60):
            logger.warning(
                f"Skipping drift check for {feature_name}: "
                f"feature is very stale ({status.freshness_minutes / 60:.1f}h)"
            )
            return True

        return False
