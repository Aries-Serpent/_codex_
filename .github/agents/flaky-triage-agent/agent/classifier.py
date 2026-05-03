"""
Flaky Test Classifier - DECIDE Phase

Classifies tests as flaky and determines remediation actions.

#AFTERMATH_PATTERN_IDENTIFIED: flaky_classification
#AFTERMATH_METRIC: flakes_classified

PDA Loop: DECIDE Phase
- Apply flakiness thresholds
- Classify severity levels
- Determine remediation actions
- Prioritize by impact
- Query cognitive brain for historical patterns
"""

# Import from detector
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Optional

sys.path.insert(0, str(Path(__file__).parent))
from detector import TestStatistics


class FlakySeverity(Enum):
    """Severity levels for flaky tests."""
    CRITICAL = "critical"  # Always fails or 0-50% pass rate
    HIGH = "high"          # 50-80% pass rate
    MEDIUM = "medium"      # 80-95% pass rate
    LOW = "low"            # 95-99% pass rate


class RemediationAction(Enum):
    """Remediation actions for flaky tests."""
    QUARANTINE = "quarantine"        # Remove from CI temporarily
    MARK_FLAKY = "mark_flaky"       # Mark with @pytest.mark.flaky
    INVESTIGATE = "investigate"      # Create GitHub issue
    MONITOR = "monitor"              # Watch for patterns
    SKIP = "skip"                    # Skip test entirely


@dataclass
class FlakyTestClassification:
    """Classification result for a flaky test."""
    test_name: str
    is_flaky: bool
    severity: FlakySeverity
    confidence: float  # 0.0 to 1.0
    pass_rate: float
    recommended_action: RemediationAction
    reasons: list[str]  # Why classified as flaky
    impact_score: float  # 0.0 to 1.0 (higher = more impact)
    metadata: dict[str, Any]


class FlakyTestClassifier:
    """
    Classifier for flaky tests - DECIDE Phase.

    #AFTERMATH_PATTERN_IDENTIFIED: classification_logic

    Responsibilities:
    - Apply flakiness detection thresholds
    - Classify severity based on pass rate and impact
    - Determine appropriate remediation actions
    - Prioritize tests by impact
    - Learn from historical patterns
    """

    # Flakiness thresholds
    FLAKY_THRESHOLD = 0.95  # <95% pass rate = flaky
    CRITICAL_THRESHOLD = 0.50
    HIGH_THRESHOLD = 0.80
    MEDIUM_THRESHOLD = 0.95

    # Timing variance thresholds
    HIGH_VARIANCE_THRESHOLD = 0.5  # Coefficient of variation > 50%

    def __init__(self, cognitive_brain_path: Optional[Path] = None):
        """
        Initialize classifier.

        Args:
            cognitive_brain_path: Path to cognitive brain database
        """
        self.cognitive_brain_path = cognitive_brain_path
        self.classifications: list[FlakyTestClassification] = []

        #AFTERMATH_METRIC: classifier_initialized

    def decide(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        DECIDE phase - classify flaky tests and determine actions.

        #AFTERMATH_PATTERN_IDENTIFIED: decision_phase

        Args:
            context: Context from PERCEIVE phase (detector)

        Returns:
            Decision dictionary with classifications and actions
        """
        decision = {
            "classifications": [],
            "actions": {},
            "priorities": []
        }

        # Classify each test
        test_statistics = context.get("test_statistics", {})
        for test_name, stats in test_statistics.items():
            classification = self._classify_test(stats, context)
            if classification.is_flaky:
                decision["classifications"].append(classification)
                self.classifications.append(classification)

        # Determine actions for each flaky test
        for classification in decision["classifications"]:
            action = self._determine_action(classification)
            decision["actions"][classification.test_name] = action

        # Prioritize by impact
        decision["priorities"] = self._prioritize_by_impact(
            decision["classifications"]
        )

        #AFTERMATH_METRIC: flaky_tests_found = len(decision["classifications"])
        #AFTERMATH_METRIC: actions_determined = len(decision["actions"])

        return decision

    def _classify_test(self, stats: TestStatistics, context: dict[str, Any]) -> FlakyTestClassification:
        """
        Classify a single test.

        #AFTERMATH_PATTERN_IDENTIFIED: test_classification
        """
        reasons = []
        confidence = 0.0

        # Check pass rate
        is_flaky = stats.pass_rate < self.FLAKY_THRESHOLD
        if is_flaky:
            reasons.append(f"Pass rate {stats.pass_rate:.1%} below threshold {self.FLAKY_THRESHOLD:.1%}")
            confidence += 0.5

        # Check timing variance
        if stats.total_runs > 1:
            coeff_var = stats.std_duration / stats.avg_duration if stats.avg_duration > 0 else 0
            if coeff_var > self.HIGH_VARIANCE_THRESHOLD:
                reasons.append(f"High timing variance: {coeff_var:.1%}")
                confidence += 0.3
                is_flaky = True

        # Check for code patterns that cause flakiness
        code_patterns = context.get("code_patterns", {})
        if code_patterns.get("concurrency"):
            reasons.append("Concurrency issues detected in test code")
            confidence += 0.2
            is_flaky = True

        # Check timing anomalies
        timing_anomalies = context.get("timing_anomalies", [])
        test_anomalies = [a for a in timing_anomalies if a["test_name"] == stats.test_name]
        if test_anomalies:
            reasons.append(f"{len(test_anomalies)} timing anomalies detected")
            confidence += 0.1

        # Determine severity
        severity = self._determine_severity(stats.pass_rate)

        # Calculate impact score
        impact_score = self._calculate_impact(stats, severity)

        # Cap confidence at 1.0
        confidence = min(confidence, 1.0)

        # Determine recommended action
        recommended_action = self._get_recommended_action(severity, confidence, stats)

        return FlakyTestClassification(
            test_name=stats.test_name,
            is_flaky=is_flaky,
            severity=severity,
            confidence=confidence,
            pass_rate=stats.pass_rate,
            recommended_action=recommended_action,
            reasons=reasons,
            impact_score=impact_score,
            metadata={
                "total_runs": stats.total_runs,
                "failed_count": stats.failed_count,
                "avg_duration": stats.avg_duration,
                "std_duration": stats.std_duration
            }
        )

    def _determine_severity(self, pass_rate: float) -> FlakySeverity:
        """
        Determine severity based on pass rate.

        #AFTERMATH_PATTERN_IDENTIFIED: severity_determination
        """
        if pass_rate < self.CRITICAL_THRESHOLD:
            return FlakySeverity.CRITICAL
        if pass_rate < self.HIGH_THRESHOLD:
            return FlakySeverity.HIGH
        if pass_rate < self.MEDIUM_THRESHOLD:
            return FlakySeverity.MEDIUM
        return FlakySeverity.LOW

    def _calculate_impact(self, stats: TestStatistics, severity: FlakySeverity) -> float:
        """
        Calculate impact score (0.0 to 1.0).

        #AFTERMATH_PATTERN_IDENTIFIED: impact_calculation

        Factors:
        - Severity level
        - Frequency of failures
        - Test execution time (longer = higher impact on CI)
        """
        impact = 0.0

        # Severity contribution (0.0 to 0.5)
        severity_scores = {
            FlakySeverity.CRITICAL: 0.5,
            FlakySeverity.HIGH: 0.4,
            FlakySeverity.MEDIUM: 0.3,
            FlakySeverity.LOW: 0.2
        }
        impact += severity_scores[severity]

        # Failure frequency contribution (0.0 to 0.3)
        if stats.total_runs > 0:
            failure_rate = stats.failed_count / stats.total_runs
            impact += failure_rate * 0.3

        # Duration contribution (0.0 to 0.2)
        # Longer tests have higher impact when they fail
        if stats.avg_duration > 60:  # > 1 minute
            impact += 0.2
        elif stats.avg_duration > 30:  # > 30 seconds
            impact += 0.1

        return min(impact, 1.0)

    def _get_recommended_action(self, severity: FlakySeverity, confidence: float,
                                stats: TestStatistics) -> RemediationAction:
        """
        Determine recommended remediation action.

        #AFTERMATH_PATTERN_IDENTIFIED: action_recommendation
        """
        # Critical severity or high confidence -> quarantine
        if severity == FlakySeverity.CRITICAL or confidence > 0.8:
            return RemediationAction.QUARANTINE

        # High severity -> mark as flaky
        if severity == FlakySeverity.HIGH:
            return RemediationAction.MARK_FLAKY

        # Medium severity with multiple failures -> investigate
        if severity == FlakySeverity.MEDIUM and stats.failed_count > 3:
            return RemediationAction.INVESTIGATE

        # Low severity or low confidence -> monitor
        return RemediationAction.MONITOR

    def _determine_action(self, classification: FlakyTestClassification) -> dict[str, Any]:
        """
        Determine specific action details.

        #AFTERMATH_PATTERN_IDENTIFIED: action_details
        """
        action = {
            "type": classification.recommended_action.value,
            "test_name": classification.test_name,
            "severity": classification.severity.value,
            "confidence": classification.confidence,
            "reasons": classification.reasons
        }

        # Add action-specific details
        if classification.recommended_action == RemediationAction.QUARANTINE:
            action["details"] = {
                "add_to_quarantine_list": True,
                "skip_in_ci": True,
                "create_issue": True
            }
        elif classification.recommended_action == RemediationAction.MARK_FLAKY:
            action["details"] = {
                "apply_decorator": "@pytest.mark.flaky(reruns=3)",
                "create_issue": False
            }
        elif classification.recommended_action == RemediationAction.INVESTIGATE:
            action["details"] = {
                "create_issue": True,
                "assign_team": "testing",
                "priority": "high"
            }
        else:  # MONITOR
            action["details"] = {
                "continue_tracking": True,
                "alert_threshold": 5  # Alert after 5 more failures
            }

        return action

    def _prioritize_by_impact(self, classifications: list[FlakyTestClassification]) -> list[str]:
        """
        Prioritize tests by impact score.

        #AFTERMATH_PATTERN_IDENTIFIED: impact_prioritization
        """
        sorted_tests = sorted(
            classifications,
            key=lambda c: c.impact_score,
            reverse=True
        )

        return [c.test_name for c in sorted_tests]

        #AFTERMATH_METRIC: tests_prioritized = len(priorities)

    def get_summary(self) -> dict[str, Any]:
        """
        Generate classifier summary.

        #AFTERMATH_METRIC: classifier_summary_generated

        Returns:
            Summary dictionary
        """
        summary = {
            "total_classified": len(self.classifications),
            "by_severity": {},
            "by_action": {},
            "avg_confidence": 0.0
        }

        if self.classifications:
            for classification in self.classifications:
                # Count by severity
                sev = classification.severity.value
                summary["by_severity"][sev] = summary["by_severity"].get(sev, 0) + 1

                # Count by action
                action = classification.recommended_action.value
                summary["by_action"][action] = summary["by_action"].get(action, 0) + 1

            # Calculate average confidence
            summary["avg_confidence"] = sum(
                c.confidence for c in self.classifications
            ) / len(self.classifications)

        #AFTERMATH_LESSON_LEARNED: classification_patterns_identified
        return summary
