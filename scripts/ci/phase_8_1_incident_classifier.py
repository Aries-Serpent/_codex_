#!/usr/bin/env python3
"""
Phase 8.1 Incident Classifier
Classifies detected failures into incident categories and severity levels.

Version: 1.0.0-final
Author: Phase 8.1 Monitoring System
"""

import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class Severity(Enum):
    """Incident severity levels."""

    P0 = "P0"  # Critical
    P1 = "P1"  # Urgent
    P2 = "P2"  # High
    P3 = "P3"  # Medium
    P4 = "P4"  # Low


class Category(Enum):
    """Incident categories."""

    INFRASTRUCTURE = "Infrastructure"
    CODE = "Code"
    CONFIGURATION = "Configuration"
    EXTERNAL = "External"
    OTHER = "Other"


@dataclass
class IncidentPattern:
    """Pattern for incident detection and classification."""

    name: str
    regex: str
    category: Category
    default_severity: Severity
    confidence_boost: float = 0.0


class IncidentClassifier:
    """Classifies incidents based on error patterns."""

    def __init__(self):
        """Initialize incident classifier with patterns."""
        self.patterns: List[IncidentPattern] = [
            # Infrastructure patterns
            IncidentPattern(
                name="GitHub API Rate Limit",
                regex=r"(API rate limit|API quota|rate limit exceeded)",
                category=Category.INFRASTRUCTURE,
                default_severity=Severity.P1,
                confidence_boost=0.10,
            ),
            IncidentPattern(
                name="npm Registry Timeout",
                regex=r"(npm ERR!.*network|npm.*timeout|registry\.npmjs|npm error)",
                category=Category.INFRASTRUCTURE,
                default_severity=Severity.P1,
                confidence_boost=0.10,
            ),
            IncidentPattern(
                name="Docker Registry Timeout",
                regex=r"(docker pull.*timeout|registry.*timeout|failed to download)",
                category=Category.INFRASTRUCTURE,
                default_severity=Severity.P1,
                confidence_boost=0.08,
            ),
            IncidentPattern(
                name="Network Connectivity",
                regex=r"(connection refused|connection timeout|network unreachable)",
                category=Category.INFRASTRUCTURE,
                default_severity=Severity.P1,
                confidence_boost=0.08,
            ),
            # Code patterns
            IncidentPattern(
                name="Test Failure",
                regex=r"(test.*failed|AssertionError|FAILED \(|test failure)",
                category=Category.CODE,
                default_severity=Severity.P2,
                confidence_boost=0.05,
            ),
            IncidentPattern(
                name="Type Error",
                regex=r"(TypeError|type.*error|type mismatch|mypy error)",
                category=Category.CODE,
                default_severity=Severity.P2,
                confidence_boost=0.07,
            ),
            IncidentPattern(
                name="Import Error",
                regex=r"(ImportError|ModuleNotFoundError|no module named)",
                category=Category.CODE,
                default_severity=Severity.P2,
                confidence_boost=0.08,
            ),
            IncidentPattern(
                name="Syntax Error",
                regex=r"(SyntaxError|syntax error|unexpected.*token)",
                category=Category.CODE,
                default_severity=Severity.P2,
                confidence_boost=0.09,
            ),
            IncidentPattern(
                name="Linting Error",
                regex=r"(lint.*error|ruff.*error|flake8|pylint error)",
                category=Category.CODE,
                default_severity=Severity.P3,
                confidence_boost=0.06,
            ),
            # Configuration patterns
            IncidentPattern(
                name="Workflow Syntax Error",
                regex=r"(workflow syntax|yaml error|invalid workflow|workflow file)",
                category=Category.CONFIGURATION,
                default_severity=Severity.P2,
                confidence_boost=0.09,
            ),
            IncidentPattern(
                name="Cache Error",
                regex=r"(cache.*error|cache.*failed|cache invalidation)",
                category=Category.CONFIGURATION,
                default_severity=Severity.P3,
                confidence_boost=0.07,
            ),
            IncidentPattern(
                name="Secret Error",
                regex=r"(secret.*error|missing.*secret|secret.*not.*found)",
                category=Category.CONFIGURATION,
                default_severity=Severity.P1,
                confidence_boost=0.10,
            ),
            IncidentPattern(
                name="Environment Error",
                regex=r"(environment.*error|env.*not.*set|environment variable)",
                category=Category.CONFIGURATION,
                default_severity=Severity.P2,
                confidence_boost=0.07,
            ),
            # External patterns
            IncidentPattern(
                name="Dependency Conflict",
                regex=r"(dependency conflict|version conflict|incompatible|dependency error)",
                category=Category.EXTERNAL,
                default_severity=Severity.P1,
                confidence_boost=0.08,
            ),
            IncidentPattern(
                name="Third-party Service",
                regex=r"(service unavailable|service error|external.*failed)",
                category=Category.EXTERNAL,
                default_severity=Severity.P1,
                confidence_boost=0.07,
            ),
            # Other patterns
            IncidentPattern(
                name="Timeout",
                regex=r"(timeout|timed out|took too long|exceeded.*timeout)",
                category=Category.OTHER,
                default_severity=Severity.P3,
                confidence_boost=0.05,
            ),
            IncidentPattern(
                name="Out of Memory",
                regex=r"(out of memory|OOM|memory.*exceeded|heap.*exhausted)",
                category=Category.OTHER,
                default_severity=Severity.P1,
                confidence_boost=0.10,
            ),
            IncidentPattern(
                name="Disk Space",
                regex=r"(disk.*full|no space left|disk space|storage.*full)",
                category=Category.OTHER,
                default_severity=Severity.P1,
                confidence_boost=0.09,
            ),
        ]

    def classify(
        self,
        error_message: str,
        failure_count: int = 1,
        workflow_name: Optional[str] = None,
    ) -> Tuple[Category, Severity, float, str]:
        """Classify an incident based on error message.

        Args:
            error_message: Error message text
            failure_count: Number of consecutive failures
            workflow_name: Name of affected workflow

        Returns:
            Tuple of (category, severity, confidence, pattern_name)
        """
        best_match = None
        best_confidence = 0.0

        # Search for matching patterns
        for pattern in self.patterns:
            if re.search(pattern.regex, error_message, re.IGNORECASE):
                # Base confidence from pattern
                base_confidence = 0.7 + pattern.confidence_boost

                # Boost confidence for consecutive failures
                if failure_count >= 3:
                    base_confidence += 0.2
                elif failure_count >= 2:
                    base_confidence += 0.1

                if base_confidence > best_confidence:
                    best_match = pattern
                    best_confidence = min(best_confidence, 0.99)

        if best_match:
            # Adjust severity based on context
            severity = self._adjust_severity(
                best_match.default_severity, failure_count, workflow_name
            )
            return (
                best_match.category,
                severity,
                min(best_confidence, 0.99),
                best_match.name,
            )

        # Default classification for unknown errors
        return (Category.OTHER, Severity.P3, 0.5, "Unknown Error")

    def _adjust_severity(
        self,
        base_severity: Severity,
        failure_count: int,
        workflow_name: Optional[str] = None,
    ) -> Severity:
        """Adjust severity based on context.

        Args:
            base_severity: Base severity from pattern
            failure_count: Number of consecutive failures
            workflow_name: Name of affected workflow

        Returns:
            Adjusted severity level
        """
        # Upgrade severity for production workflows
        production_workflows = ["deploy", "release", "production", "live"]
        if workflow_name and any(
            prod in workflow_name.lower() for prod in production_workflows
        ):
            if base_severity == Severity.P3:
                return Severity.P2
            elif base_severity == Severity.P2:
                return Severity.P1

        # Upgrade severity for multiple consecutive failures
        if failure_count >= 5:
            if base_severity == Severity.P4:
                return Severity.P3
            elif base_severity == Severity.P3:
                return Severity.P2
            elif base_severity == Severity.P2:
                return Severity.P1
        elif failure_count >= 3:
            if base_severity == Severity.P4:
                return Severity.P3
            elif base_severity == Severity.P3:
                return Severity.P2

        return base_severity

    def generate_incident_id(self) -> str:
        """Generate unique incident ID.

        Returns:
            Incident ID in format INCIDENT-YYYY-MM-DD-XXX
        """
        now = datetime.utcnow()
        date_str = now.strftime("%Y-%m-%d")

        # TODO: Read last incident number from log file
        incident_num = 1

        return f"INCIDENT-{date_str}-{incident_num:03d}"

    def classify_workflow_failure(
        self,
        workflow_name: str,
        error_log: str,
        failure_count: int = 1,
        run_id: Optional[str] = None,
    ) -> Dict[str, any]:
        """Classify a workflow failure into an incident.

        Args:
            workflow_name: Name of workflow
            error_log: Error log text
            failure_count: Number of consecutive failures
            run_id: GitHub Actions run ID

        Returns:
            Dictionary with incident classification
        """
        category, severity, confidence, pattern = self.classify(
            error_log, failure_count, workflow_name
        )

        incident_id = self.generate_incident_id()

        return {
            "incident_id": incident_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "workflow": workflow_name,
            "run_id": run_id,
            "category": category.value,
            "severity": severity.value,
            "pattern": pattern,
            "confidence": confidence,
            "consecutive_failures": failure_count,
            "requires_escalation": severity in (Severity.P0, Severity.P1),
            "action": {
                "escalation_channels": self._get_escalation_channels(severity),
                "assignment": self._get_assignment(category),
                "priority": severity.value,
            },
        }

    def _get_escalation_channels(self, severity: Severity) -> List[str]:
        """Get escalation channels for severity level.

        Args:
            severity: Severity level

        Returns:
            List of escalation channels
        """
        if severity == Severity.P0:
            return ["email", "slack", "github_issue", "sms"]
        elif severity == Severity.P1:
            return ["email", "slack", "github_issue"]
        elif severity == Severity.P2:
            return ["github_issue"]
        else:
            return ["log"]

    def _get_assignment(self, category: Category) -> str:
        """Get recommended agent assignment.

        Args:
            category: Incident category

        Returns:
            Agent name for assignment
        """
        mapping = {
            Category.INFRASTRUCTURE: "ci-failure-resolution-agent",
            Category.CODE: "ci-testing-agent",
            Category.CONFIGURATION: "config-validator",
            Category.EXTERNAL: "dependency-conflict-agent",
            Category.OTHER: "artifact-monitor-agent",
        }
        return mapping.get(category, "artifact-monitor-agent")


def main() -> int:
    """Main entry point for testing."""
    classifier = IncidentClassifier()

    # Test cases
    test_cases = [
        ("npm ERR! network timeout", "security-scan.yml", 3),
        ("ImportError: No module named pytest", "test-comprehensive.yml", 1),
        ("SyntaxError: unexpected token", "lint-quality.yml", 1),
        ("Docker pull timeout", "build-docker.yml", 2),
    ]

    print("Testing Incident Classifier\n" + "=" * 60)

    for error_msg, workflow, failures in test_cases:
        result = classifier.classify_workflow_failure(
            workflow, error_msg, failures
        )
        print(f"\nWorkflow: {workflow}")
        print(f"Error: {error_msg}")
        print(f"Consecutive Failures: {failures}")
        print(f"Category: {result['category']}")
        print(f"Severity: {result['severity']}")
        print(f"Pattern: {result['pattern']}")
        print(f"Confidence: {result['confidence']:.2%}")
        print(f"Requires Escalation: {result['requires_escalation']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
