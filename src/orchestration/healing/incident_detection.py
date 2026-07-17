"""Incident Detection Module — Classify failures and detect patterns.

This module:
- Parses CI/CD logs and test output
- Classifies failure types (test, CI, security, deployment)
- Detects patterns (flaky tests, cascading failures)
- Generates root-cause hypotheses
- Returns incident metadata for strategy generation
"""

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class FailureType(str, Enum):
    """Classification of failure type."""

    TEST_FAILURE = "test_failure"
    CI_FAILURE = "ci_failure"
    SECURITY_FINDING = "security_finding"
    DEPLOYMENT_FAILURE = "deployment_failure"
    IMPORT_ERROR = "import_error"
    ASSERTION_ERROR = "assertion_error"
    TIMEOUT = "timeout"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    FLAKY_TEST = "flaky_test"
    CASCADING_FAILURE = "cascading_failure"


class Severity(str, Enum):
    """Incident severity levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class RootCauseHypothesis:
    """Hypothesis about root cause of failure."""

    description: str
    confidence: float  # 0.0-1.0
    evidence: List[str]
    related_patterns: List[str] = field(default_factory=list)
    suggested_action: Optional[str] = None


@dataclass
class IncidentReport:
    """Complete incident detection report."""

    incident_id: str
    timestamp: str
    failure_type: FailureType
    severity: Severity
    affected_modules: List[str]
    affected_tests: List[str]
    root_cause_hypotheses: List[RootCauseHypothesis]
    is_flaky: bool = False
    is_cascading: bool = False
    retry_count: int = 0
    failure_log_snippet: str = ""
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "incident_id": self.incident_id,
            "timestamp": self.timestamp,
            "failure_type": self.failure_type.value,
            "severity": self.severity.value,
            "affected_modules": self.affected_modules,
            "affected_tests": self.affected_tests,
            "root_cause_hypotheses": [
                {
                    "description": h.description,
                    "confidence": h.confidence,
                    "evidence": h.evidence,
                    "related_patterns": h.related_patterns,
                    "suggested_action": h.suggested_action,
                }
                for h in self.root_cause_hypotheses
            ],
            "is_flaky": self.is_flaky,
            "is_cascading": self.is_cascading,
            "retry_count": self.retry_count,
            "failure_log_snippet": self.failure_log_snippet,
            "context": self.context,
        }


class IncidentDetector:
    """Detects and classifies incidents from failure logs."""

    # Patterns for failure detection
    PATTERNS = {
        "import_error": [
            r"ImportError:",
            r"ModuleNotFoundError:",
            r"cannot import name",
            r"No module named",
        ],
        "assertion_error": [
            r"AssertionError:",
            r"assert .+ == .+",
            r"assert .+ is .+",
        ],
        "timeout": [
            r"TimeoutError:",
            r"timeout",
            r"TIMEOUT",
            r"exceeded.*timeout",
        ],
        "flaky": [
            r"@pytest.mark.flaky",
            r"reruns=",
            r"flaky test",
        ],
        "cascading": [
            r"conftest.py",
            r"fixture.*error",
            r"setup.*failed",
        ],
        "resource": [
            r"MemoryError:",
            r"out of memory",
            r"ResourceWarning",
        ],
    }

    @classmethod
    def detect_from_logs(
        cls,
        failure_log: str,
        test_name: Optional[str] = None,
        incident_id: Optional[str] = None,
    ) -> IncidentReport:
        """Detect incident from failure logs.

        Args:
            failure_log: Full test/CI failure output
            test_name: Name of failing test (optional)
            incident_id: Pre-generated incident ID (optional)

        Returns:
            IncidentReport with classification and hypotheses
        """
        import uuid
        from datetime import datetime, timezone

        if not incident_id:
            incident_id = str(uuid.uuid4())[:8]

        timestamp = datetime.now(timezone.utc).isoformat()

        # Classify failure type
        failure_type = cls._classify_failure_type(failure_log)

        # Extract affected modules/tests
        affected_modules = cls._extract_affected_modules(failure_log)
        affected_tests = cls._extract_affected_tests(failure_log, test_name)

        # Generate root cause hypotheses
        hypotheses = cls._generate_hypotheses(failure_log, failure_type)

        # Detect patterns
        is_flaky = cls._detect_flaky(failure_log)
        is_cascading = cls._detect_cascading(failure_log, affected_modules)

        # Determine severity
        severity = cls._determine_severity(failure_type, is_cascading)

        # Build report
        report = IncidentReport(
            incident_id=incident_id,
            timestamp=timestamp,
            failure_type=failure_type,
            severity=severity,
            affected_modules=affected_modules,
            affected_tests=affected_tests,
            root_cause_hypotheses=hypotheses,
            is_flaky=is_flaky,
            is_cascading=is_cascading,
            failure_log_snippet=failure_log[:500],
            context={
                "log_length": len(failure_log),
                "test_name": test_name,
            },
        )

        logger.info(
            f"Detected {failure_type.value} incident {incident_id}: "
            f"{severity.value} severity, {len(hypotheses)} hypotheses"
        )

        return report

    @classmethod
    def _classify_failure_type(cls, log: str) -> FailureType:
        """Classify failure type from log content."""
        log_lower = log.lower()

        # Check for specific patterns
        if any(p in log for p in cls.PATTERNS["import_error"]):
            return FailureType.IMPORT_ERROR

        if any(p in log for p in cls.PATTERNS["assertion_error"]):
            return FailureType.ASSERTION_ERROR

        if any(p in log for p in cls.PATTERNS["timeout"]):
            return FailureType.TIMEOUT

        if any(p in log for p in cls.PATTERNS["resource"]):
            return FailureType.RESOURCE_EXHAUSTION

        if "FAILED" in log and "test" in log_lower:
            return FailureType.TEST_FAILURE

        if "error" in log_lower and ("ci" in log_lower or "workflow" in log_lower):
            return FailureType.CI_FAILURE

        if "security" in log_lower or "vulnerability" in log_lower:
            return FailureType.SECURITY_FINDING

        if "deploy" in log_lower or "deployment" in log_lower:
            return FailureType.DEPLOYMENT_FAILURE

        # Default
        return FailureType.TEST_FAILURE

    @classmethod
    def _extract_affected_modules(cls, log: str) -> List[str]:
        """Extract module names from log."""
        modules = set()

        # Look for Python import paths
        for match in re.finditer(r"(src/[\w/]+\.py|tests/[\w/]+\.py)", log):
            path = match.group(1)
            # Extract module from path
            parts = path.split("/")
            if len(parts) >= 2:
                modules.add(parts[1])

        # Look for module names in common patterns
        for match in re.finditer(r"in ([\w_]+(?:\.[\w_]+)*)", log):
            modules.add(match.group(1))

        return sorted(list(modules))

    @classmethod
    def _extract_affected_tests(
        cls, log: str, test_name: Optional[str] = None
    ) -> List[str]:
        """Extract test names from log."""
        tests = set()

        if test_name:
            tests.add(test_name)

        # Look for pytest test names
        for match in re.finditer(r"(test_[\w_]+(?:::\w+)?)", log):
            tests.add(match.group(1))

        # Look for FAILED patterns
        for match in re.finditer(r"FAILED ([\w_/]+::[\w_:]+)", log):
            tests.add(match.group(1))

        return sorted(list(tests))

    @classmethod
    def _generate_hypotheses(
        cls, log: str, failure_type: FailureType
    ) -> List[RootCauseHypothesis]:
        """Generate root cause hypotheses."""
        hypotheses = []

        if failure_type == FailureType.IMPORT_ERROR:
            hypotheses.append(
                RootCauseHypothesis(
                    description="Missing or incorrect import path",
                    confidence=0.9,
                    evidence=["ImportError pattern detected"],
                    suggested_action="Add missing import or fix import path",
                )
            )
            hypotheses.append(
                RootCauseHypothesis(
                    description="P19 shadow import (stale .egg-link in site-packages)",
                    confidence=0.6,
                    evidence=["Import resolution may be shadowed"],
                    suggested_action="Run: pip install --force-reinstall --no-deps -e .",
                )
            )

        elif failure_type == FailureType.ASSERTION_ERROR:
            hypotheses.append(
                RootCauseHypothesis(
                    description="Test assertion failure (logic or API mismatch)",
                    confidence=0.85,
                    evidence=["AssertionError detected"],
                    suggested_action="Verify test expectations match implementation",
                )
            )

        elif failure_type == FailureType.TIMEOUT:
            hypotheses.append(
                RootCauseHypothesis(
                    description="Test execution timeout (resource, async, or deadlock)",
                    confidence=0.8,
                    evidence=["Timeout pattern detected"],
                    suggested_action="Add pytest.mark.timeout or check for resource leaks",
                )
            )

        elif failure_type == FailureType.RESOURCE_EXHAUSTION:
            hypotheses.append(
                RootCauseHypothesis(
                    description="Memory or resource exhaustion",
                    confidence=0.9,
                    evidence=["ResourceWarning or MemoryError detected"],
                    suggested_action="Check for resource leaks or mock expensive operations",
                )
            )

        elif failure_type == FailureType.CASCADING_FAILURE:
            hypotheses.append(
                RootCauseHypothesis(
                    description="Fixture or setup failure affecting multiple tests",
                    confidence=0.85,
                    evidence=["conftest.py or setup error detected"],
                    suggested_action="Fix conftest or test setup",
                )
            )

        else:
            # Generic hypothesis
            hypotheses.append(
                RootCauseHypothesis(
                    description="Test or CI failure of unknown origin",
                    confidence=0.5,
                    evidence=["Failure detected, specific pattern not matched"],
                    suggested_action="Investigate logs manually",
                )
            )

        return hypotheses

    @classmethod
    def _detect_flaky(cls, log: str) -> bool:
        """Detect if test is marked as flaky."""
        for pattern in cls.PATTERNS["flaky"]:
            if re.search(pattern, log, re.IGNORECASE):
                return True
        return False

    @classmethod
    def _detect_cascading(cls, log: str, affected_modules: List[str]) -> bool:
        """Detect if failure is cascading (affects multiple modules)."""
        for pattern in cls.PATTERNS["cascading"]:
            if re.search(pattern, log, re.IGNORECASE):
                return True

        # Heuristic: cascading if >1 module affected
        if len(affected_modules) > 1:
            return True

        return False

    @classmethod
    def _determine_severity(
        cls, failure_type: FailureType, is_cascading: bool
    ) -> Severity:
        """Determine incident severity."""
        # Cascading failures are always high severity
        if is_cascading:
            return Severity.HIGH

        # Map failure types to base severity
        severity_map = {
            FailureType.SECURITY_FINDING: Severity.CRITICAL,
            FailureType.DEPLOYMENT_FAILURE: Severity.HIGH,
            FailureType.IMPORT_ERROR: Severity.HIGH,
            FailureType.TIMEOUT: Severity.MEDIUM,
            FailureType.RESOURCE_EXHAUSTION: Severity.HIGH,
            FailureType.ASSERTION_ERROR: Severity.MEDIUM,
            FailureType.TEST_FAILURE: Severity.MEDIUM,
            FailureType.CI_FAILURE: Severity.HIGH,
            FailureType.FLAKY_TEST: Severity.LOW,
            FailureType.CASCADING_FAILURE: Severity.HIGH,
        }

        return severity_map.get(failure_type, Severity.MEDIUM)
