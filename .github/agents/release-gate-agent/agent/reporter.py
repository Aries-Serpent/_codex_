"""
Release Reporter - AFTERMATH Phase

#AFTERMATH_PATTERN_IDENTIFIED: release_outcome_tracking
#AFTERMATH_METRIC: releases_tracked
#AFTERMATH_LESSON_LEARNED: release_patterns_identified

Tracks release outcomes and learns from patterns.
"""

import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

_core_path = str(Path(__file__).parent.parent.parent / "core")
if _core_path not in sys.path:
    sys.path.insert(0, _core_path)
from cognitive_brain import CognitiveBrain  # noqa: E402


@dataclass
class ReleaseReport:
    """Comprehensive release report."""
    release_id: str
    outcome: str  # "success" | "failed" | "blocked"
    risk_score: float
    validation_pass_rate: float
    blockers_count: int
    warnings_count: int
    duration_seconds: float
    health_status: str
    lessons_learned: Dict[str, Any]
    timestamp: datetime
    metadata: Dict[str, Any]


class ReleaseReporter:
    """
    Release Reporter - AFTERMATH Phase

    #AFTERMATH_PATTERN_IDENTIFIED: outcome_analysis
    #AFTERMATH_LESSON_LEARNED: continuous_improvement

    Analyzes release outcomes and records patterns in cognitive brain.
    """

    def __init__(self):
        self.brain = CognitiveBrain(Path(".codex/brain.db"))

    def generate_aftermath_report(
        self,
        validation_results: Dict[str, Any],
        decision_result: Dict[str, Any],
        execution_result: Dict[str, Any],
        release_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        AFTERMATH: Generate comprehensive release report and record patterns.

        #AFTERMATH_LESSON_LEARNED: pattern_recording

        Args:
            validation_results: Results from PERCEIVE phase
            decision_result: Results from DECIDE phase
            execution_result: Results from ACT phase
            release_info: Original release metadata

        Returns:
            Comprehensive aftermath report
        """
        # Determine outcome
        outcome = self._determine_outcome(execution_result)

        # Extract lessons learned
        lessons_learned = self._extract_lessons(
            validation_results, decision_result, execution_result
        )

        # Record pattern in cognitive brain
        self._record_pattern(
            validation_results, decision_result, execution_result, outcome
        )

        # Generate report
        report = ReleaseReport(
            release_id=release_info.get("version", "unknown"),
            outcome=outcome,
            risk_score=decision_result.get("risk_score", 0.0),
            validation_pass_rate=validation_results.get("pass_rate", 0.0),
            blockers_count=len(decision_result.get("blockers", [])),
            warnings_count=len(decision_result.get("warnings", [])),
            duration_seconds=execution_result.get("duration_seconds", 0.0),
            health_status=execution_result.get("health_status", "unknown"),
            lessons_learned=lessons_learned,
            timestamp=datetime.now(),
            metadata={
                "release_url": execution_result.get("release_url", ""),
                "git_tag": execution_result.get("git_tag", ""),
                "decision": decision_result.get("decision", "unknown")
            }
        )

        return {
            "release_id": report.release_id,
            "outcome": report.outcome,
            "risk_score": report.risk_score,
            "validation_pass_rate": report.validation_pass_rate,
            "blockers_count": report.blockers_count,
            "warnings_count": report.warnings_count,
            "duration_seconds": report.duration_seconds,
            "health_status": report.health_status,
            "lessons_learned": report.lessons_learned,
            "timestamp": report.timestamp.isoformat(),
            "metadata": report.metadata
        }

    def _determine_outcome(self, execution_result: Dict[str, Any]) -> str:
        """Determine overall release outcome."""
        status = execution_result.get("status", "unknown")
        health = execution_result.get("health_status", "unknown")

        if status == "success" and health == "healthy":
            return "success"
        if status == "blocked":
            return "blocked"
        return "failed"

    def _extract_lessons(
        self,
        validation_results: Dict[str, Any],
        decision_result: Dict[str, Any],
        execution_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract lessons learned from release process."""
        lessons = {}

        # Lesson 1: Validation effectiveness
        validations = validation_results.get("validations", [])
        failed_checks = [v for v in validations if not v["passed"]]
        if failed_checks:
            lessons["validation_gaps"] = [
                f"{v['check_name']}: {v.get('error_message', 'Failed')}"
                for v in failed_checks
            ]

        # Lesson 2: Decision accuracy
        if decision_result.get("decision") == "block" and execution_result.get("status") == "blocked":
            lessons["decision_accuracy"] = "Correctly blocked release with issues"
        elif decision_result.get("decision") == "approve" and execution_result.get("health_status") == "healthy":
            lessons["decision_accuracy"] = "Correctly approved healthy release"

        # Lesson 3: Risk assessment calibration
        risk_score = decision_result.get("risk_score", 0.0)
        outcome = self._determine_outcome(execution_result)
        if risk_score > 0.5 and outcome == "success":
            lessons["risk_calibration"] = "High risk score but successful release - may be over-cautious"
        elif risk_score < 0.3 and outcome == "failed":
            lessons["risk_calibration"] = "Low risk score but failed release - may be under-estimating risk"

        # Lesson 4: Performance metrics
        duration = execution_result.get("duration_seconds", 0.0)
        if duration > 300:  # 5 minutes
            lessons["performance"] = f"Release process took {duration:.1f}s - consider optimization"

        return lessons

    def _record_pattern(
        self,
        validation_results: Dict[str, Any],
        decision_result: Dict[str, Any],
        execution_result: Dict[str, Any],
        outcome: str
    ) -> None:
        """Record release pattern in cognitive brain."""
        try:
            # Record pattern for future learning
            self.brain.record_pattern(
                pattern_type="release_outcome",
                success=(outcome == "success"),
                metadata={
                    "risk_score": decision_result.get("risk_score", 0.0),
                    "validation_pass_rate": validation_results.get("pass_rate", 0.0),
                    "decision": decision_result.get("decision", "unknown"),
                    "health_status": execution_result.get("health_status", "unknown"),
                    "duration_seconds": execution_result.get("duration_seconds", 0.0),
                    "blockers_count": len(decision_result.get("blockers", [])),
                    "warnings_count": len(decision_result.get("warnings", []))
                }
            )
        except Exception:
            # Best-effort: if brain recording fails, continue without error
            # This ensures release process isn't blocked by telemetry issues
            pass
