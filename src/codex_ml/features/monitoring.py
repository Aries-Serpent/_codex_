"""Feature store monitoring and health checks."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List

logger = logging.getLogger(__name__)

__all__ = ["FeatureHealthMonitor", "FeatureHealthStatus"]


@dataclass
class FeatureHealthStatus:
    """Health status for a feature.

    Attributes:
        feature_name: Feature name
        is_healthy: Whether feature is healthy
        last_updated: Last update timestamp
        freshness_minutes: Minutes since last update
        error_count: Number of errors in monitoring window
        warnings: List of warning messages
        freshness_level: Freshness classification
    """

    feature_name: str
    is_healthy: bool
    last_updated: str
    freshness_minutes: float
    error_count: int = 0
    warnings: List[str] = field(default_factory=list)
    freshness_level: str = "UNKNOWN"


class FeatureHealthMonitor:
    """Monitor feature health and freshness."""

    # Freshness thresholds in minutes
    FRESHNESS_THRESHOLDS = {
        "FRESH": 60,  # < 1 hour
        "ACCEPTABLE": 360,  # 1-6 hours
        "STALE": 1440,  # 6-24 hours
        "VERY_STALE": float("inf"),  # > 24 hours
    }

    def __init__(self, freshness_threshold_minutes: int = 60):
        """Initialize feature health monitor.

        Args:
            freshness_threshold_minutes: Max minutes before feature is stale
        """
        self.freshness_threshold = timedelta(minutes=freshness_threshold_minutes)
        self.feature_updates: Dict[str, datetime] = {}
        self.error_counts: Dict[str, int] = {}

    def record_feature_update(self, feature_name: str):
        """Record feature update timestamp.

        Args:
            feature_name: Feature name
        """
        self.feature_updates[feature_name] = datetime.now()
        logger.debug(f"Recorded update for feature: {feature_name}")

    def record_feature_error(self, feature_name: str):
        """Record feature error.

        Args:
            feature_name: Feature name
        """
        self.error_counts[feature_name] = self.error_counts.get(feature_name, 0) + 1
        logger.warning(f"Recorded error for feature: {feature_name}")

    def get_freshness_level(self, freshness_minutes: float) -> str:
        """Get freshness level classification.

        Args:
            freshness_minutes: Minutes since last update

        Returns:
            Freshness level string
        """
        if freshness_minutes < self.FRESHNESS_THRESHOLDS["FRESH"]:
            return "FRESH"
        elif freshness_minutes < self.FRESHNESS_THRESHOLDS["ACCEPTABLE"]:
            return "ACCEPTABLE"
        elif freshness_minutes < self.FRESHNESS_THRESHOLDS["STALE"]:
            return "STALE"
        else:
            return "VERY_STALE"

    def check_feature_health(self, feature_name: str) -> FeatureHealthStatus:
        """Check health of a feature.

        Args:
            feature_name: Feature name

        Returns:
            Feature health status
        """
        now = datetime.now()
        last_updated = self.feature_updates.get(feature_name)

        if not last_updated:
            return FeatureHealthStatus(
                feature_name=feature_name,
                is_healthy=False,
                last_updated="never",
                freshness_minutes=float("inf"),
                error_count=0,
                warnings=["Feature has never been updated"],
                freshness_level="UNKNOWN",
            )

        age = now - last_updated
        freshness_minutes = age.total_seconds() / 60
        error_count = self.error_counts.get(feature_name, 0)
        freshness_level = self.get_freshness_level(freshness_minutes)

        warnings = []
        is_healthy = True

        if age > self.freshness_threshold:
            warnings.append(
                f"Feature is stale (>{self.freshness_threshold.total_seconds()/60:.0f} min)"
            )
            is_healthy = False

        if error_count > 0:
            warnings.append(f"{error_count} errors in monitoring window")
            if error_count > 5:
                is_healthy = False

        return FeatureHealthStatus(
            feature_name=feature_name,
            is_healthy=is_healthy,
            last_updated=last_updated.isoformat(),
            freshness_minutes=freshness_minutes,
            error_count=error_count,
            warnings=warnings,
            freshness_level=freshness_level,
        )

    def check_all_features(self, feature_names: List[str]) -> Dict[str, FeatureHealthStatus]:
        """Check health of all features.

        Args:
            feature_names: List of feature names to check

        Returns:
            Dictionary mapping feature names to health status
        """
        return {name: self.check_feature_health(name) for name in feature_names}

    def get_freshness_report(self) -> Dict[str, int]:
        """Get freshness distribution report.

        Returns:
            Dictionary with count per freshness level
        """
        report = {level: 0 for level in ["FRESH", "ACCEPTABLE", "STALE", "VERY_STALE", "UNKNOWN"]}

        for feature_name in self.feature_updates:
            status = self.check_feature_health(feature_name)
            report[status.freshness_level] += 1

        return report

    def alert_stale_features(self, threshold_hours: int = 24) -> List[str]:
        """Get list of stale features.

        Args:
            threshold_hours: Hours threshold for staleness

        Returns:
            List of stale feature names
        """
        threshold_minutes = threshold_hours * 60
        stale_features = []

        for feature_name in self.feature_updates:
            status = self.check_feature_health(feature_name)
            if status.freshness_minutes > threshold_minutes:
                stale_features.append(feature_name)

        return stale_features

    def reset_error_counts(self):
        """Reset error counts for all features."""
        self.error_counts.clear()
        logger.info("Reset error counts for all features")

    def get_time_until_stale(self, feature_name: str, threshold_hours: int = 24) -> float:
        """Get time until feature becomes stale.

        Args:
            feature_name: Feature name
            threshold_hours: Staleness threshold in hours

        Returns:
            Hours until stale (negative if already stale)
        """
        last_updated = self.feature_updates.get(feature_name)
        if not last_updated:
            return float("-inf")  # Already very stale

        now = datetime.now()
        age = now - last_updated
        age_hours = age.total_seconds() / 3600
        return threshold_hours - age_hours

    def get_freshness_distribution(self) -> Dict[str, float]:
        """Get distribution of feature freshness as percentages.

        Returns:
            Dictionary with percentage per freshness level
        """
        report = self.get_freshness_report()
        total = sum(report.values())

        if total == 0:
            return {level: 0.0 for level in report.keys()}

        return {level: (count / total) * 100 for level, count in report.items()}
