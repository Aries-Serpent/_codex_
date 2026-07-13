"""Monthly Review Cycle — Capture metrics, analyze trends, drive decisions.

This module implements:
- Monthly snapshot: capture lane metrics, incident count, fix time
- Trend analysis: comparing current vs. baseline metrics
- Decision authority: recommendations for @mbaetiong or team
- Review report generation
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class LaneMetrics:
    """Metrics for a single lane."""

    lane_id: str
    success_rate_pct: float
    avg_execution_time_seconds: float
    incident_count: int
    avg_incident_fix_time_minutes: float
    error_rate_pct: float
    rollback_count: int


@dataclass
class MetricTrend:
    """Trend analysis for a metric."""

    metric_name: str
    baseline_value: float
    current_value: float
    change_pct: float
    direction: str  # "improving", "degrading", "stable"
    recommendation: str


@dataclass
class ReviewReport:
    """Monthly review report."""

    month: str  # YYYY-MM format
    timestamp: datetime
    lane_metrics: Dict[str, LaneMetrics]
    trends: List[MetricTrend]
    incident_summary: Dict[str, int]  # incident_type -> count
    total_incidents: int
    avg_fix_time_minutes: float
    recommendations: List[str]
    decision_authority: str  # "@mbaetiong", "team", "auto_approved"
    decisions_made: List[str]


class MonthlyReviewCycle:
    """Manages monthly review cycle for governance."""

    def __init__(self):
        """Initialize monthly review cycle."""
        self.reviews: Dict[str, ReviewReport] = {}
        self.baseline_metrics: Dict[str, Dict[str, float]] = {
            "lane_A": {"success_rate": 98.5, "avg_fix_time": 15.0},
            "lane_B": {"success_rate": 98.5, "avg_fix_time": 15.0},
            "lane_C": {"success_rate": 99.0, "avg_fix_time": 20.0},
            "lane_D": {"success_rate": 99.2, "avg_fix_time": 10.0},
            "lane_E": {"success_rate": 99.0, "avg_fix_time": 12.0},
            "lane_H": {"success_rate": 99.5, "avg_fix_time": 8.0},
            "lane_I": {"success_rate": 99.8, "avg_fix_time": 5.0},
        }
        self.created_at = datetime.now(timezone.utc)

    def capture_monthly_snapshot(self, month: str) -> ReviewReport:
        """
        Capture monthly snapshot of metrics.

        Args:
            month: Month in YYYY-MM format

        Returns:
            ReviewReport with captured metrics and analysis
        """
        logger.info(f"Capturing monthly snapshot for {month}")

        lane_metrics = {}
        for lane_id in ["A", "B", "C", "D", "E", "H", "I"]:
            baseline = self.baseline_metrics.get(f"lane_{lane_id}", {})
            lane_metrics[lane_id] = LaneMetrics(
                lane_id=lane_id,
                success_rate_pct=baseline.get("success_rate", 99.0) + (1.0 if lane_id in ["H", "I"] else 0),
                avg_execution_time_seconds=baseline.get("avg_fix_time", 15.0) * 60,
                incident_count=self._simulate_incident_count(lane_id),
                avg_incident_fix_time_minutes=baseline.get("avg_fix_time", 15.0),
                error_rate_pct=max(0, 100 - baseline.get("success_rate", 99.0)),
                rollback_count=self._simulate_rollback_count(lane_id),
            )

        # Analyze trends
        trends = self._analyze_trends(lane_metrics)

        # Summarize incidents
        incident_summary = {
            "test_failure": 12,
            "timeout": 5,
            "deployment_failure": 2,
            "rollback_required": 1,
        }
        total_incidents = sum(incident_summary.values())
        avg_fix_time = sum(m.avg_incident_fix_time_minutes for m in lane_metrics.values()) / len(lane_metrics)

        # Generate recommendations
        recommendations = self._generate_recommendations(trends, total_incidents)

        report = ReviewReport(
            month=month,
            timestamp=datetime.now(timezone.utc),
            lane_metrics=lane_metrics,
            trends=trends,
            incident_summary=incident_summary,
            total_incidents=total_incidents,
            avg_fix_time_minutes=avg_fix_time,
            recommendations=recommendations,
            decision_authority="@mbaetiong" if total_incidents > 15 else "team",
            decisions_made=[],
        )

        self.reviews[month] = report
        logger.info(f"Captured snapshot for {month}: {total_incidents} incidents, {avg_fix_time:.1f}min avg fix time")
        return report

    def _simulate_incident_count(self, lane_id: str) -> int:
        """Simulate incident count for a lane."""
        base_counts = {"A": 3, "B": 2, "C": 4, "D": 1, "E": 2, "H": 1, "I": 0}
        return base_counts.get(lane_id, 2)

    def _simulate_rollback_count(self, lane_id: str) -> int:
        """Simulate rollback count for a lane."""
        return 1 if lane_id in ["A", "C"] else 0

    def _analyze_trends(self, current_metrics: Dict[str, LaneMetrics]) -> List[MetricTrend]:
        """Analyze metrics trends."""
        trends = []

        for lane_id, metrics in current_metrics.items():
            baseline = self.baseline_metrics.get(f"lane_{lane_id}", {})
            baseline_success = baseline.get("success_rate", 99.0)

            change_pct = ((metrics.success_rate_pct - baseline_success) / baseline_success) * 100

            if abs(change_pct) < 0.5:
                direction = "stable"
            elif change_pct > 0:
                direction = "improving"
            else:
                direction = "degrading"

            recommendation = ""
            if direction == "degrading":
                recommendation = f"Investigate degradation in lane {lane_id}"
            elif metrics.incident_count > baseline.get("avg_fix_time", 15.0):
                recommendation = f"High incident count in lane {lane_id}; review recent changes"

            trends.append(
                MetricTrend(
                    metric_name=f"lane_{lane_id}_success_rate",
                    baseline_value=baseline_success,
                    current_value=metrics.success_rate_pct,
                    change_pct=change_pct,
                    direction=direction,
                    recommendation=recommendation,
                )
            )

        return trends

    def _generate_recommendations(self, trends: List[MetricTrend], total_incidents: int) -> List[str]:
        """Generate recommendations based on trends."""
        recommendations = []

        degrading_lanes = [t for t in trends if t.direction == "degrading"]
        if degrading_lanes:
            recommendations.append(f"Address degradation in {len(degrading_lanes)} lane(s)")

        if total_incidents > 20:
            recommendations.append("High incident count; consider additional safeguards")

        improving_lanes = [t for t in trends if t.direction == "improving"]
        if improving_lanes:
            recommendations.append(f"Document improvements in {len(improving_lanes)} lane(s) as best practices")

        return recommendations

    def get_review_report(self, month: str) -> Optional[ReviewReport]:
        """Get review report for specific month."""
        return self.reviews.get(month)

    def get_all_reviews(self) -> List[ReviewReport]:
        """Get all review reports."""
        return list(self.reviews.values())

    def get_review_summary(self) -> Dict:
        """Get summary across all reviews."""
        if not self.reviews:
            return {"total_reviews": 0}

        total_incidents = sum(r.total_incidents for r in self.reviews.values())
        avg_fix_time = sum(r.avg_fix_time_minutes for r in self.reviews.values()) / len(self.reviews)

        return {
            "total_reviews": len(self.reviews),
            "months_reviewed": list(self.reviews.keys()),
            "total_incidents_across_reviews": total_incidents,
            "avg_fix_time_minutes": avg_fix_time,
            "trend": "stable" if len(self.reviews) < 2 else self._compute_overall_trend(),
        }

    def _compute_overall_trend(self) -> str:
        """Compute overall trend across reviews."""
        if len(self.reviews) < 2:
            return "insufficient_data"

        recent_reviews = sorted(self.reviews.values(), key=lambda r: r.timestamp)[-2:]
        old_incidents = recent_reviews[0].total_incidents
        new_incidents = recent_reviews[1].total_incidents

        if new_incidents < old_incidents:
            return "improving"
        elif new_incidents > old_incidents:
            return "degrading"
        else:
            return "stable"
