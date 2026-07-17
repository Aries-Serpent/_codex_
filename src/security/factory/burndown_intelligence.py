"""
S7: Burndown Intelligence

Tracks metrics and provides adaptive feedback:
- findings_closed
- families_resolved
- wave_velocity

Success metric: Accurate ETA within ±1 week
"""

import statistics
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List


@dataclass
class BurndownMetrics:
    """Metrics at a point in time."""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    findings_closed: int = 0
    findings_remaining: int = 0
    families_resolved: int = 0
    families_remaining: int = 0
    wave_velocity: float = 0.0  # Findings/hour
    completion_percentage: float = 0.0


@dataclass
class BurndownReport:
    """Weekly burndown report."""
    week_number: int
    start_date: str
    end_date: str
    metrics_snapshots: List[BurndownMetrics] = field(default_factory=list)
    avg_velocity: float = 0.0
    eta_completion_days: float = 0.0
    trend: str = "stable"  # accelerating, stable, decelerating

    def get_summary(self) -> Dict[str, Any]:
        """Get report summary."""
        return {
            "week": self.week_number,
            "period": f"{self.start_date} to {self.end_date}",
            "avg_velocity": self.avg_velocity,
            "eta_days": self.eta_completion_days,
            "trend": self.trend,
            "snapshots": len(self.metrics_snapshots),
        }


class BurndownTracker:
    """Tracks burndown metrics and provides ETA."""

    def __init__(self):
        """Initialize tracker."""
        self.snapshots: List[BurndownMetrics] = []
        self.velocity_history: List[float] = []
        self.week_reports: List[BurndownReport] = []

    def record_snapshot(self, metrics: BurndownMetrics) -> None:
        """Record a snapshot of current metrics."""
        self.snapshots.append(metrics)
        self.velocity_history.append(metrics.wave_velocity)

    def compute_velocity(
        self,
        findings_closed_in_period: int,
        hours_elapsed: float,
    ) -> float:
        """Compute velocity in findings/hour."""
        if hours_elapsed <= 0:
            return 0.0
        return findings_closed_in_period / hours_elapsed

    def estimate_eta(self, remaining_findings: int) -> float:
        """Estimate completion date in days."""
        if not self.velocity_history or not any(self.velocity_history):
            return float("inf")

        # Use recent velocities (last 7 days)
        recent_velocities = self.velocity_history[-168:]  # 7 days * 24 hours
        if not recent_velocities:
            return float("inf")

        avg_velocity = statistics.mean([v for v in recent_velocities if v > 0])
        if avg_velocity <= 0:
            return float("inf")

        hours_needed = remaining_findings / avg_velocity
        return hours_needed / 24  # Convert to days

    def detect_trend(self) -> str:
        """Detect velocity trend."""
        if len(self.velocity_history) < 3:
            return "stable"

        # Compare recent velocities to older ones
        recent = self.velocity_history[-10:]  # Last 10 measurements
        older = self.velocity_history[-20:-10]  # Previous 10 measurements

        if not recent or not older:
            return "stable"

        recent_avg = statistics.mean([v for v in recent if v > 0]) or 0
        older_avg = statistics.mean([v for v in older if v > 0]) or 0

        if older_avg == 0:
            return "stable"

        change_ratio = recent_avg / older_avg
        if change_ratio > 1.2:
            return "accelerating"
        elif change_ratio < 0.8:
            return "decelerating"
        else:
            return "stable"

    def generate_weekly_report(
        self,
        week_number: int,
        metrics_for_week: List[BurndownMetrics],
    ) -> BurndownReport:
        """Generate weekly burndown report."""
        if not metrics_for_week:
            return BurndownReport(
                week_number=week_number,
                start_date="",
                end_date="",
            )

        # Calculate average velocity for the week
        velocities = [m.wave_velocity for m in metrics_for_week if m.wave_velocity > 0]
        avg_velocity = statistics.mean(velocities) if velocities else 0

        # Get first and last metrics
        first_metric = metrics_for_week[0]
        last_metric = metrics_for_week[-1]

        # Estimate ETA based on last metric
        eta_days = self.estimate_eta(last_metric.findings_remaining)

        # Detect trend
        trend = self.detect_trend()

        report = BurndownReport(
            week_number=week_number,
            start_date=first_metric.timestamp,
            end_date=last_metric.timestamp,
            metrics_snapshots=metrics_for_week,
            avg_velocity=avg_velocity,
            eta_completion_days=eta_days,
            trend=trend,
        )

        self.week_reports.append(report)
        return report

    def get_burndown_summary(self) -> Dict[str, Any]:
        """Get overall burndown summary."""
        if not self.snapshots:
            return {
                "total_snapshots": 0,
                "avg_velocity": 0.0,
                "estimated_eta_days": 0,
                "trend": "unknown",
            }

        latest = self.snapshots[-1]
        avg_velocity = (
            statistics.mean(self.velocity_history) if self.velocity_history else 0
        )
        eta_days = self.estimate_eta(latest.findings_remaining)

        return {
            "total_snapshots": len(self.snapshots),
            "findings_closed": latest.findings_closed,
            "findings_remaining": latest.findings_remaining,
            "families_resolved": latest.families_resolved,
            "avg_velocity": avg_velocity,
            "estimated_eta_days": eta_days,
            "trend": self.detect_trend(),
            "completion_percentage": latest.completion_percentage,
            "weekly_reports": len(self.week_reports),
        }


def compute_metrics(
    findings_closed: int,
    findings_remaining: int,
    families_resolved: int,
    families_remaining: int,
    wave_velocity: float = 0.0,
) -> BurndownMetrics:
    """Compute burndown metrics at a point in time."""
    total_findings = findings_closed + findings_remaining
    completion_percentage = (
        (findings_closed / total_findings * 100) if total_findings > 0 else 0
    )

    return BurndownMetrics(
        findings_closed=findings_closed,
        findings_remaining=findings_remaining,
        families_resolved=families_resolved,
        families_remaining=families_remaining,
        wave_velocity=wave_velocity,
        completion_percentage=completion_percentage,
    )
