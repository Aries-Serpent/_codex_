"""Feature store monitoring and health checks.

Provides:
- Feature freshness tracking
- Health status monitoring
- SLA enforcement and alerting
- Health report generation
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

logger = logging.getLogger(__name__)

__all__ = ["FeatureHealthMonitor", "FeatureHealthStatus", "HealthAlert"]

# TYPE_CHECKING import for FeatureStore type hint
try:
    from codex_ml.features.store import FeatureStore
except ImportError:
    FeatureStore = None


@dataclass
class HealthAlert:
    """Alert for unhealthy feature.

    Attributes:
        feature_name: Feature name
        severity: Alert severity (CRITICAL, WARNING, INFO)
        message: Alert message
        timestamp: Alert timestamp
        metric_value: Relevant metric value
    """

    feature_name: str
    severity: str
    message: str
    timestamp: str
    metric_value: Optional[float] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "feature_name": self.feature_name,
            "severity": self.severity,
            "message": self.message,
            "timestamp": self.timestamp,
            "metric_value": self.metric_value,
        }


@dataclass
class FeatureHealthStatus:
    """Health status for a feature.

    Attributes:
        feature_name: Feature name
        is_healthy: Whether feature is healthy
        last_updated: Last update timestamp
        freshness_minutes: Minutes since last update
        error_count: Number of errors in monitoring window
        warnings: list of warning messages
        freshness_level: Freshness classification
    """

    feature_name: str
    is_healthy: bool
    last_updated: str
    freshness_minutes: float
    error_count: int = 0
    warnings: list[str] = field(default_factory=list)
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

    def __init__(
        self,
        feature_store: Optional[FeatureStore] = None,
        freshness_threshold_minutes: int = 60,
    ):
        """Initialize feature health monitor.

        Args:
            feature_store: Optional FeatureStore instance for integration
            freshness_threshold_minutes: Max minutes before feature is stale
        """
        self.feature_store = feature_store
        self.freshness_threshold = timedelta(minutes=freshness_threshold_minutes)
        self.feature_updates: dict[str, datetime] = {}
        self.error_counts: dict[str, int] = {}

    def record_feature_update(self, feature_name: str):
        """Record feature update timestamp.

        Args:
            feature_name: Feature name
        """
        self.feature_updates[feature_name] = datetime.now(timezone.utc)
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
        if freshness_minutes < self.FRESHNESS_THRESHOLDS["ACCEPTABLE"]:
            return "ACCEPTABLE"
        if freshness_minutes < self.FRESHNESS_THRESHOLDS["STALE"]:
            return "STALE"
        return "VERY_STALE"

    def check_feature_health(self, feature_name: str) -> FeatureHealthStatus:
        """Check health of a feature.

        Args:
            feature_name: Feature name

        Returns:
            Feature health status
        """
        now = datetime.now(timezone.utc)
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
                f"Feature is stale (>{self.freshness_threshold.total_seconds() / 60:.0f} min)"
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

    def check_all_features(self, feature_names: list[str]) -> dict[str, FeatureHealthStatus]:
        """Check health of all features.

        Args:
            feature_names: list of feature names to check

        Returns:
            Dictionary mapping feature names to health status
        """
        return {name: self.check_feature_health(name) for name in feature_names}

    def get_freshness_report(self) -> dict[str, int]:
        """Get freshness distribution report.

        Returns:
            Dictionary with count per freshness level
        """
        report = {level: 0 for level in ["FRESH", "ACCEPTABLE", "STALE", "VERY_STALE", "UNKNOWN"]}

        for feature_name in self.feature_updates:
            status = self.check_feature_health(feature_name)
            report[status.freshness_level] += 1

        return report

    def alert_stale_features(self, threshold_hours: int = 24) -> list[str]:
        """Get list of stale features.

        Args:
            threshold_hours: Hours threshold for staleness

        Returns:
            list of stale feature names
        """
        threshold_minutes = threshold_hours * 60
        stale_features = []

        for feature_name in self.feature_updates:
            status = self.check_feature_health(feature_name)
            if status.freshness_minutes > threshold_minutes:
                stale_features.append(feature_name)

        return stale_features

    def reset_error_counts(self) -> None:
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

        now = datetime.now(timezone.utc)
        age = now - last_updated
        age_hours = age.total_seconds() / 3600
        return threshold_hours - age_hours

    def get_freshness_distribution(self) -> dict[str, float]:
        """Get distribution of feature freshness as percentages.

        Returns:
            Dictionary with percentage per freshness level
        """
        report = self.get_freshness_report()
        total = sum(report.values())

        if total == 0:
            return {level: 0.0 for level in report}

        return {level: (count / total) * 100 for level, count in report.items()}

    def check_all(self, feature_names: list[str]) -> dict[str, FeatureHealthStatus]:
        """Check health of all features (alias for check_all_features).

        Args:
            feature_names: list of feature names to check

        Returns:
            Dictionary mapping feature names to health status
        """
        return self.check_all_features(feature_names)

    def generate_alerts(
        self,
        health_statuses: dict[str, FeatureHealthStatus],
        sla_minutes: int = 120,
    ) -> list[HealthAlert]:
        """Generate alerts for unhealthy features.

        Args:
            health_statuses: Dictionary of feature health statuses
            sla_minutes: SLA threshold in minutes

        Returns:
            list of health alerts
        """
        alerts = []
        now = datetime.now(timezone.utc)

        for feature_name, status in health_statuses.items():
            # Critical: Feature never updated or very stale
            if status.last_updated == "never":
                alerts.append(
                    HealthAlert(
                        feature_name=feature_name,
                        severity="CRITICAL",
                        message="Feature has never been updated",
                        timestamp=now.isoformat(),
                    )
                )
            elif status.freshness_level == "VERY_STALE":
                alerts.append(
                    HealthAlert(
                        feature_name=feature_name,
                        severity="CRITICAL",
                        message=f"Feature is very stale ({status.freshness_minutes:.0f} min)",
                        timestamp=now.isoformat(),
                        metric_value=status.freshness_minutes,
                    )
                )
            # Warning: Feature approaching SLA violation
            elif status.freshness_minutes > sla_minutes * 0.8:
                alerts.append(
                    HealthAlert(
                        feature_name=feature_name,
                        severity="WARNING",
                        message=f"Feature approaching SLA violation ({status.freshness_minutes:.0f}/{sla_minutes} min)",  # noqa: E501
                        timestamp=now.isoformat(),
                        metric_value=status.freshness_minutes,
                    )
                )
            # Warning: High error rate
            if status.error_count > 5:
                alerts.append(
                    HealthAlert(
                        feature_name=feature_name,
                        severity="WARNING",
                        message=f"High error count ({status.error_count} errors)",
                        timestamp=now.isoformat(),
                        metric_value=float(status.error_count),
                    )
                )

        return alerts

    def generate_health_report(
        self,
        health_statuses: dict[str, FeatureHealthStatus],
        format: str = "markdown",
        include_recommendations: bool = True,
    ) -> str:
        """Generate health report in specified format.

        Args:
            health_statuses: Dictionary of feature health statuses
            format: Report format (json, markdown)
            include_recommendations: Include recommendations section

        Returns:
            Formatted health report string
        """
        if format == "json":
            return self._generate_json_report(health_statuses, include_recommendations)
        if format == "markdown":
            return self._generate_markdown_report(health_statuses, include_recommendations)
        raise ValueError(f"Unsupported format: {format}")

    def _generate_json_report(
        self,
        health_statuses: dict[str, FeatureHealthStatus],
        include_recommendations: bool,
    ) -> str:
        """Generate JSON health report."""
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "total_features": len(health_statuses),
                "healthy_features": sum(1 for s in health_statuses.values() if s.is_healthy),
                "unhealthy_features": sum(1 for s in health_statuses.values() if not s.is_healthy),
            },
            "freshness_distribution": self.get_freshness_distribution(),
            "features": {
                name: {
                    "is_healthy": status.is_healthy,
                    "last_updated": status.last_updated,
                    "freshness_minutes": status.freshness_minutes,
                    "freshness_level": status.freshness_level,
                    "error_count": status.error_count,
                    "warnings": status.warnings,
                }
                for name, status in health_statuses.items()
            },
            "alerts": [alert.to_dict() for alert in self.generate_alerts(health_statuses)],
        }

        if include_recommendations:
            report["recommendations"] = self._generate_recommendations(health_statuses)

        return json.dumps(report, indent=2)

    def _generate_markdown_report(
        self,
        health_statuses: dict[str, FeatureHealthStatus],
        include_recommendations: bool = True,
    ) -> str:
        """Generate Markdown health report."""
        lines = []
        lines.append("# Feature Health Report")
        lines.append(f"\n**Generated:** {datetime.now(timezone.utc).isoformat()}\n")

        # Summary
        healthy_count = sum(1 for s in health_statuses.values() if s.is_healthy)
        total_count = len(health_statuses)
        lines.append("## Summary\n")
        lines.append(f"- Total Features: {total_count}")
        lines.append(f"- Healthy: {healthy_count} ({healthy_count / total_count * 100:.1f}%)")
        lines.append(
            f"- Unhealthy: {total_count - healthy_count} ({(total_count - healthy_count) / total_count * 100:.1f}%)"  # noqa: E501
        )

        # Freshness Distribution
        freshness_dist = self.get_freshness_distribution()
        lines.append("\n## Freshness Distribution\n")
        for level, pct in freshness_dist.items():
            lines.append(f"- {level}: {pct:.1f}%")

        # Feature Details
        lines.append("\n## Feature Details\n")
        lines.append("| Feature | Status | Freshness | Last Updated | Errors |")
        lines.append("|---------|--------|-----------|--------------|--------|")

        for name, status in sorted(health_statuses.items()):
            status_icon = "✓" if status.is_healthy else "✗"
            lines.append(
                f"| {name} | {status_icon} | {status.freshness_level} | "
                f"{status.last_updated} | {status.error_count} |"
            )

        # Alerts
        alerts = self.generate_alerts(health_statuses)
        if alerts:
            lines.append("\n## Alerts\n")
            for alert in alerts:
                lines.append(f"- **[{alert.severity}]** {alert.feature_name}: {alert.message}")

        # Recommendations
        if include_recommendations:
            recommendations = self._generate_recommendations(health_statuses)
            if recommendations:
                lines.append("\n## Recommendations\n")
                for rec in recommendations:
                    lines.append(f"- {rec}")

        return "\n".join(lines)

    def _generate_recommendations(
        self,
        health_statuses: dict[str, FeatureHealthStatus],
    ) -> list[str]:
        """Generate recommendations based on health statuses."""
        recommendations = []

        # Check for stale features
        stale_features = [
            name
            for name, status in health_statuses.items()
            if status.freshness_level in ["STALE", "VERY_STALE"]
        ]
        if stale_features:
            recommendations.append(
                f"Update {len(stale_features)} stale feature(s): {', '.join(stale_features[:5])}"
                + (" ..." if len(stale_features) > 5 else "")
            )

        # Check for features with high error rates
        error_features = [
            name for name, status in health_statuses.items() if status.error_count > 5
        ]
        if error_features:
            recommendations.append(
                f"Investigate {len(error_features)} feature(s) with high error rates: {', '.join(error_features[:5])}"  # noqa: E501
                + (" ..." if len(error_features) > 5 else "")
            )

        # Check for features never updated
        never_updated = [
            name for name, status in health_statuses.items() if status.last_updated == "never"
        ]
        if never_updated:
            recommendations.append(
                f"Initialize {len(never_updated)} feature(s) that have never been updated"
            )

        return recommendations

    def check_health(self) -> dict[str, Any]:
        """Check health of all features in feature store.

        Returns:
            Dictionary with overall_status and detailed health information
        """
        if self.feature_store is None:
            # Use manually tracked features if no feature store
            feature_names = list(self.feature_updates.keys())
        else:
            # Get feature names from feature store
            try:
                feature_names = list(self.feature_store.feature_groups.keys())
                # Update feature_updates from feature store versions
                for name in feature_names:
                    versions = self.feature_store.feature_versions.get(name, [])
                    if versions:
                        latest = versions[-1]
                        if hasattr(latest, "created_at"):
                            try:
                                self.feature_updates[name] = datetime.fromisoformat(
                                    latest.created_at
                                )
                            except (ValueError, AttributeError) as e:
                                logger.debug(
                                    "Failed to parse feature timestamp for '%s': %s",
                                    name,
                                    e,
                                )
            except (ValueError, TypeError) as e:
                type(e).__name__
                logger.debug("Exception: <ERROR_TYPE>")
                logger.warning("Could not load features from store: <ERROR_TYPE>")
                feature_names = list(self.feature_updates.keys())

        # Check health of all features
        health_statuses = self.check_all_features(feature_names)

        # Calculate overall status
        healthy_count = sum(1 for s in health_statuses.values() if s.is_healthy)
        total_count = len(health_statuses)

        if total_count == 0:
            overall_status = "unknown"
        elif healthy_count == total_count:
            overall_status = "healthy"
        elif healthy_count >= total_count * 0.8:
            overall_status = "warning"
        else:
            overall_status = "critical"

        # Generate alerts
        alerts = self.generate_alerts(health_statuses, sla_minutes=120)

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_status": overall_status,
            "total_features": total_count,
            "healthy_features": healthy_count,
            "unhealthy_features": total_count - healthy_count,
            "health_statuses": {name: vars(status) for name, status in health_statuses.items()},
            "alerts": [alert.to_dict() for alert in alerts],
            "freshness_distribution": self.get_freshness_report() if feature_names else {},
        }

    def save_health_report(
        self, output_path: Optional[str] = None, format: str = "json"
    ) -> dict[str, Any]:
        """Save health report to file.

        Args:
            output_path: Optional output file path (default: auto-generated)
            format: Report format ('json' or 'markdown')

        Returns:
            Health report dictionary
        """
        report = self.check_health()

        # Generate default path if not provided
        if output_path is None:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            ext = "json" if format == "json" else "md"
            output_path = f"health_report_{timestamp}.{ext}"

        # Write report
        from pathlib import Path

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        if format == "json":
            with open(output_file, "w") as f:
                json.dump(report, f, indent=2)
            logger.info(f"Saved health report to {output_path}")
        elif format == "markdown":
            # Get health statuses for markdown generation
            feature_names = list(report["health_statuses"].keys())
            health_statuses = self.check_all_features(feature_names)
            markdown_content = self._generate_markdown_report(health_statuses)
            with open(output_file, "w") as f:
                f.write(markdown_content)
            logger.info(f"Saved markdown health report to {output_path}")
        else:
            raise ValueError(f"Unsupported format: {format}. Use 'json' or 'markdown'")

        return report

    def get_stale_features(self, threshold_hours: int = 24) -> list[str]:
        """Get list of stale features.

        Args:
            threshold_hours: Hours threshold for staleness (default: 24)

        Returns:
            list of stale feature names
        """
        return self.alert_stale_features(threshold_hours=threshold_hours)
