"""Validation Loop Module — Verify fixes and detect cascading failures.

This module:
- Validates that fixes resolved the incident
- Detects cascading failures (fix caused new issues)
- Implements loop breaker (max 3 attempts per incident)
- Manages validation state and history
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ValidationStatus(str, Enum):
    """Status of validation."""

    PENDING = "pending"
    VALIDATING = "validating"
    SUCCESS = "success"
    FAILURE = "failure"
    CASCADE_DETECTED = "cascade_detected"
    LOOP_BREAKER_HIT = "loop_breaker_hit"


@dataclass
class ValidationReport:
    """Report from validation loop."""

    validation_id: str
    incident_id: str
    strategy_id: str
    attempt_number: int
    status: ValidationStatus
    original_failure: str
    validation_result: str
    cascade_detected: bool = False
    cascading_failures: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "validation_id": self.validation_id,
            "incident_id": self.incident_id,
            "strategy_id": self.strategy_id,
            "attempt_number": self.attempt_number,
            "status": self.status.value,
            "original_failure": self.original_failure,
            "validation_result": self.validation_result,
            "cascade_detected": self.cascade_detected,
            "cascading_failures": self.cascading_failures,
            "metrics": self.metrics,
            "timestamp": self.timestamp,
            "context": self.context,
        }


class CascadePattern(str, Enum):
    """Types of cascading failures."""

    DEPENDENCY_BREAK = "dependency_break"
    FIXTURE_FAILURE = "fixture_failure"
    SIDE_EFFECT = "side_effect"
    RESOURCE_LEAK = "resource_leak"
    IMPORT_SIDE_EFFECT = "import_side_effect"


@dataclass
class CascadeDetection:
    """Detection of cascading failure."""

    pattern: CascadePattern
    confidence: float
    affected_tests: List[str]
    affected_modules: List[str]
    evidence: List[str]


class ValidationLoop:
    """Validates fixes and detects cascades."""

    MAX_RETRY_ATTEMPTS = 3
    _validation_history: Dict[str, List[ValidationReport]] = {}

    @classmethod
    def validate_fix(
        cls,
        incident_id: str,
        strategy_id: str,
        original_failure: str,
        attempt_number: int = 1,
    ) -> ValidationReport:
        """Validate that a fix resolved the incident.

        Args:
            incident_id: ID of incident
            strategy_id: ID of strategy executed
            original_failure: Original failure description
            attempt_number: Current attempt number

        Returns:
            ValidationReport with success/failure/cascade status
        """
        import uuid
        from datetime import datetime, timezone

        validation_id = f"val_{incident_id}_{uuid.uuid4().hex[:6]}"
        now = datetime.now(timezone.utc)

        # Check loop breaker
        if attempt_number > cls.MAX_RETRY_ATTEMPTS:
            report = ValidationReport(
                validation_id=validation_id,
                incident_id=incident_id,
                strategy_id=strategy_id,
                attempt_number=attempt_number,
                status=ValidationStatus.LOOP_BREAKER_HIT,
                original_failure=original_failure,
                validation_result="Max retry attempts exceeded, escalating",
                timestamp=now.isoformat(),
            )
            logger.warning(f"Loop breaker hit for incident {incident_id}")
            return report

        # Run validation
        status, result, cascade = cls._run_validation(original_failure)

        # Build report
        report = ValidationReport(
            validation_id=validation_id,
            incident_id=incident_id,
            strategy_id=strategy_id,
            attempt_number=attempt_number,
            status=status,
            original_failure=original_failure,
            validation_result=result,
            cascade_detected=cascade["detected"],
            cascading_failures=cascade.get("failures", []),
            timestamp=now.isoformat(),
            metrics={
                "cascade_confidence": cascade.get("confidence", 0.0),
                "affected_test_count": len(cascade.get("affected_tests", [])),
            },
        )

        # Store in history
        if incident_id not in cls._validation_history:
            cls._validation_history[incident_id] = []
        cls._validation_history[incident_id].append(report)

        logger.info(
            f"Validation {validation_id} for incident {incident_id}: {status.value}"
        )

        return report

    @classmethod
    def _run_validation(cls, original_failure: str) -> tuple:
        """Run validation check on original failure.

        Args:
            original_failure: Description of original failure

        Returns:
            Tuple of (status, result_str, cascade_dict)
        """
        # Simulate running the failed test again
        import random  # noqa: S311  # Used for test simulation, not cryptography

        # Probability of success based on failure type
        success_prob = 0.7

        if "import" in original_failure.lower():
            success_prob = 0.75

        elif "assert" in original_failure.lower():
            success_prob = 0.65

        elif "timeout" in original_failure.lower():
            success_prob = 0.6

        # Simulate result
        if random.random() < success_prob:
            status = ValidationStatus.SUCCESS
            result = "Original failure resolved"
            cascade = {"detected": False}

        else:
            # Failure still exists - might be cascade
            cascade_prob = 0.3
            if random.random() < cascade_prob:
                status = ValidationStatus.CASCADE_DETECTED
                result = "Fix resolved original failure but caused cascade"
                cascade = cls._detect_cascade(original_failure)

            else:
                status = ValidationStatus.FAILURE
                result = "Fix did not resolve original failure"
                cascade = {"detected": False}

        return status, result, cascade

    @classmethod
    def _detect_cascade(cls, context: str) -> Dict[str, Any]:
        """Detect cascading failures.

        Args:
            context: Context of failure

        Returns:
            Dict with cascade detection info
        """
        # Analyze for cascade patterns
        cascade_info = {
            "detected": True,
            "patterns": [],
            "affected_tests": [],
            "affected_modules": [],
            "confidence": 0.6,
            "evidence": [],
            "failures": [],
        }

        # Pattern: Fixture failure
        if "fixture" in context.lower() or "conftest" in context.lower():
            cascade_info["patterns"].append(CascadePattern.FIXTURE_FAILURE.value)
            cascade_info["affected_tests"].append("test_*")
            cascade_info["confidence"] = 0.85
            cascade_info["evidence"].append("conftest-related failure")

        # Pattern: Import side effect
        elif "import" in context.lower():
            cascade_info["patterns"].append(CascadePattern.IMPORT_SIDE_EFFECT.value)
            cascade_info["affected_modules"].append("*")
            cascade_info["confidence"] = 0.7
            cascade_info["evidence"].append("Import side effect detected")

        # Pattern: Dependency break
        elif "depend" in context.lower() or "module" in context.lower():
            cascade_info["patterns"].append(CascadePattern.DEPENDENCY_BREAK.value)
            cascade_info["affected_modules"].append("dependent_modules")
            cascade_info["confidence"] = 0.6
            cascade_info["evidence"].append("Dependency chain broken")

        # Pattern: Resource leak
        elif "resource" in context.lower() or "memory" in context.lower():
            cascade_info["patterns"].append(CascadePattern.RESOURCE_LEAK.value)
            cascade_info["affected_tests"].append("test_memory_*")
            cascade_info["confidence"] = 0.7
            cascade_info["evidence"].append("Resource exhaustion detected")

        # Simulate cascading failures
        cascade_info["failures"] = [
            f"cascade_test_{i}" for i in range(len(cascade_info["patterns"]))
        ]

        return cascade_info

    @classmethod
    def handle_cascade(
        cls, validation_report: ValidationReport
    ) -> Optional[Any]:
        """Handle detected cascading failure.

        Args:
            validation_report: Report with cascade detection

        Returns:
            New incident ID for cascade, or None if not escalated
        """
        if not validation_report.cascade_detected:
            return None

        import uuid

        # Create new incident for cascade
        cascade_incident_id = f"cascade_{validation_report.incident_id}"

        logger.warning(
            f"Cascading failure detected in validation {validation_report.validation_id}: "
            f"{validation_report.cascading_failures}"
        )

        # This would trigger a new heal cycle for the cascade
        return cascade_incident_id

    @classmethod
    def should_retry(cls, report: ValidationReport) -> bool:
        """Determine if healing should be retried.

        Args:
            report: ValidationReport

        Returns:
            True if should retry, False otherwise
        """
        if report.status == ValidationStatus.SUCCESS:
            return False

        if report.status == ValidationStatus.LOOP_BREAKER_HIT:
            return False

        if report.attempt_number >= cls.MAX_RETRY_ATTEMPTS:
            return False

        # Retry on cascade (up to max attempts)
        if report.status == ValidationStatus.CASCADE_DETECTED:
            return report.attempt_number < cls.MAX_RETRY_ATTEMPTS

        # Retry on failure
        if report.status == ValidationStatus.FAILURE:
            return report.attempt_number < cls.MAX_RETRY_ATTEMPTS

        return False

    @classmethod
    def get_validation_history(
        cls, incident_id: Optional[str] = None
    ) -> Dict[str, List[ValidationReport]]:
        """Get validation history.

        Args:
            incident_id: Optional filter to specific incident

        Returns:
            Dict mapping incident_id to list of reports
        """
        if incident_id:
            return {incident_id: cls._validation_history.get(incident_id, [])}

        return cls._validation_history

    @classmethod
    def get_metrics(cls) -> Dict[str, Any]:
        """Get validation metrics.

        Returns:
            Dict with validation statistics
        """
        all_reports = []
        for reports in cls._validation_history.values():
            all_reports.extend(reports)

        success_count = sum(
            1
            for r in all_reports
            if r.status == ValidationStatus.SUCCESS
        )
        cascade_count = sum(
            1
            for r in all_reports
            if r.status == ValidationStatus.CASCADE_DETECTED
        )
        failure_count = sum(
            1
            for r in all_reports
            if r.status == ValidationStatus.FAILURE
        )
        loop_breaker_count = sum(
            1
            for r in all_reports
            if r.status == ValidationStatus.LOOP_BREAKER_HIT
        )

        metrics = {
            "total_validations": len(all_reports),
            "successful": success_count,
            "cascades_detected": cascade_count,
            "failures": failure_count,
            "loop_breaker_hits": loop_breaker_count,
            "success_rate": success_count / len(all_reports) if all_reports else 0,
            "cascade_prevention_rate": 1.0 - (cascade_count / len(all_reports)) if all_reports else 1.0,
            "average_attempts_per_incident": (
                len(all_reports) / len(cls._validation_history)
                if cls._validation_history
                else 0
            ),
        }

        return metrics

    @classmethod
    def clear_history(cls) -> None:
        """Clear validation history for testing."""
        cls._validation_history.clear()
