"""Drift Detection — Monitor for deviations from baseline behavior.

This module implements:
- Baseline capture: Phase 1-7 expected behavior
- Drift monitoring: Detect deviations >1% (false positive threshold)
- Escalation: Generate GitHub issue if drift detected
- Drift reporting
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class BaselineMetrics:
    """Baseline metrics for comparison."""

    metric_name: str
    expected_value: float
    tolerance_pct: float = 1.0  # Allow 1% deviation


@dataclass
class DriftObservation:
    """A single drift observation."""

    metric_name: str
    observed_value: float
    expected_value: float
    drift_magnitude_pct: float
    timestamp: datetime
    severity: str  # "info", "warning", "alert"


@dataclass
class DriftReport:
    """Report of drift detection."""

    timestamp: datetime
    drift_detected: bool
    total_metrics_checked: int
    metrics_with_drift: List[DriftObservation]
    drift_magnitude_pct: float  # Overall drift magnitude
    action_taken: str  # "none", "logged", "issue_generated"
    issue_link: Optional[str] = None
    false_positive_rate_pct: float = 0.0


class DriftDetector:
    """Detects deviations from baseline behavior."""

    # False positive threshold: >1% deviation considered real drift
    DRIFT_THRESHOLD_PCT = 1.0

    def __init__(self):
        """Initialize drift detector with baseline metrics."""
        self.baseline_metrics = self._initialize_baseline()
        self.observations: List[DriftObservation] = []
        self.reports: List[DriftReport] = []
        self.created_at = datetime.now(timezone.utc)

    def _initialize_baseline(self) -> Dict[str, BaselineMetrics]:
        """Initialize baseline metrics from Phase 1-7."""
        return {
            "lane_a_success_rate": BaselineMetrics("lane_a_success_rate", 98.5, tolerance_pct=1.0),
            "lane_b_success_rate": BaselineMetrics("lane_b_success_rate", 98.5, tolerance_pct=1.0),
            "lane_c_success_rate": BaselineMetrics("lane_c_success_rate", 99.0, tolerance_pct=1.0),
            "lane_d_success_rate": BaselineMetrics("lane_d_success_rate", 99.2, tolerance_pct=0.8),
            "lane_e_success_rate": BaselineMetrics("lane_e_success_rate", 99.0, tolerance_pct=1.0),
            "orchestration_overhead_pct": BaselineMetrics("orchestration_overhead_pct", 2.5, tolerance_pct=1.5),
            "decision_latency_ms": BaselineMetrics("decision_latency_ms", 150.0, tolerance_pct=0.5),
            "replay_determinism_pct": BaselineMetrics("replay_determinism_pct", 100.0, tolerance_pct=0.1),
            "error_budget_burn_rate": BaselineMetrics("error_budget_burn_rate", 0.5, tolerance_pct=2.0),
        }

    def detect_drift(self, observed_metrics: Dict[str, float]) -> DriftReport:
        """
        Detect drift in observed metrics.

        Args:
            observed_metrics: Dict of metric_name -> observed_value

        Returns:
            DriftReport indicating if drift detected and actions taken
        """
        logger.info("Running drift detection")

        drifts = []
        for metric_name, baseline in self.baseline_metrics.items():
            if metric_name not in observed_metrics:
                logger.warning(f"Metric {metric_name} not in observed metrics")
                continue

            observed_value = observed_metrics[metric_name]
            drift_magnitude_pct = abs((observed_value - baseline.expected_value) / baseline.expected_value * 100)

            if drift_magnitude_pct > baseline.tolerance_pct:
                severity = "alert" if drift_magnitude_pct > baseline.tolerance_pct * 2 else "warning"

                observation = DriftObservation(
                    metric_name=metric_name,
                    observed_value=observed_value,
                    expected_value=baseline.expected_value,
                    drift_magnitude_pct=drift_magnitude_pct,
                    timestamp=datetime.now(timezone.utc),
                    severity=severity,
                )
                drifts.append(observation)
                self.observations.append(observation)

                logger.warning(
                    f"Drift detected in {metric_name}: "
                    f"expected {baseline.expected_value}, got {observed_value} "
                    f"(drift: {drift_magnitude_pct:.2f}%, threshold: {baseline.tolerance_pct:.2f}%)"
                )

        drift_detected = len(drifts) > 0
        avg_drift = (sum(d.drift_magnitude_pct for d in drifts) / len(drifts)) if drifts else 0.0

        # Determine action
        action_taken = "none"
        issue_link = None
        if drift_detected and avg_drift > self.DRIFT_THRESHOLD_PCT:
            action_taken = "issue_generated"
            # Issue generation will be handled by IssueGenerator
            issue_link = None  # Will be set after issue creation

        report = DriftReport(
            timestamp=datetime.now(timezone.utc),
            drift_detected=drift_detected,
            total_metrics_checked=len(self.baseline_metrics),
            metrics_with_drift=drifts,
            drift_magnitude_pct=avg_drift,
            action_taken=action_taken,
            issue_link=issue_link,
            false_positive_rate_pct=0.0 if drift_detected else 0.5,  # ~0.5% false positive assumed
        )

        self.reports.append(report)
        logger.info(
            f"Drift detection complete: drift_detected={drift_detected}, "
            f"metrics_checked={report.total_metrics_checked}, "
            f"avg_drift={avg_drift:.2f}%"
        )

        return report

    def get_drift_reports(self) -> List[DriftReport]:
        """Get all drift reports."""
        return self.reports

    def get_drift_summary(self) -> Dict:
        """Get summary of all drift observations."""
        if not self.reports:
            return {"total_reports": 0, "drifts_detected": 0}

        total_drifts = sum(len(r.metrics_with_drift) for r in self.reports)
        avg_drift_magnitude = (sum(r.drift_magnitude_pct for r in self.reports) / len(self.reports)) if self.reports else 0

        return {
            "total_reports": len(self.reports),
            "total_drifts_detected": total_drifts,
            "avg_drift_magnitude_pct": avg_drift_magnitude,
            "false_positive_rate_pct": sum(r.false_positive_rate_pct for r in self.reports) / len(self.reports)
            if self.reports
            else 0,
            "issues_generated": sum(1 for r in self.reports if r.action_taken == "issue_generated"),
        }

    def update_baseline(self, metric_name: str, new_expected_value: float, new_tolerance_pct: float) -> bool:
        """Update baseline for a specific metric."""
        if metric_name not in self.baseline_metrics:
            logger.warning(f"Metric {metric_name} not found in baseline")
            return False

        old_value = self.baseline_metrics[metric_name].expected_value
        self.baseline_metrics[metric_name].expected_value = new_expected_value
        self.baseline_metrics[metric_name].tolerance_pct = new_tolerance_pct

        logger.info(
            f"Updated baseline for {metric_name}: {old_value:.2f} → {new_expected_value:.2f}, "
            f"tolerance: {new_tolerance_pct:.2f}%"
        )
        return True
