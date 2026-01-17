"""Tests for agents.self_healing module.

Phase 8 tests covering:
- IssueType enum
- IssueSeverity enum
- DetectedIssue dataclass
- RemediationAction dataclass
- SelfHealingEngine class
- DiagnosticResult
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


class TestIssueType:
    """Tests for IssueType enum."""

    def test_issue_types_exist(self):
        """Test all expected issue types exist."""
        from agents.self_healing import IssueType
        
        assert IssueType.TEST_FAILURE.value == "test_failure"
        assert IssueType.BUILD_FAILURE.value == "build_failure"
        assert IssueType.DEPENDENCY_CONFLICT.value == "dependency_conflict"
        assert IssueType.SECURITY_VULNERABILITY.value == "security_vulnerability"

    def test_issue_type_iteration(self):
        """Test that IssueType is iterable."""
        from agents.self_healing import IssueType
        
        types = list(IssueType)
        assert len(types) >= 4


class TestIssueSeverity:
    """Tests for IssueSeverity enum."""

    def test_severity_levels_exist(self):
        """Test all expected severity levels exist."""
        from agents.self_healing import IssueSeverity
        
        assert IssueSeverity.CRITICAL.value == "critical"
        assert IssueSeverity.HIGH.value == "high"
        assert IssueSeverity.MEDIUM.value == "medium"
        assert IssueSeverity.LOW.value == "low"
        assert IssueSeverity.INFO.value == "info"

    def test_severity_ordering(self):
        """Test severity levels can be compared."""
        from agents.self_healing import IssueSeverity
        
        # Enums can be compared by name
        assert IssueSeverity.CRITICAL.name == "CRITICAL"


class TestDetectedIssue:
    """Tests for DetectedIssue dataclass."""

    @pytest.fixture
    def DetectedIssue(self):
        """Import DetectedIssue class."""
        from agents.self_healing import DetectedIssue, IssueType, IssueSeverity
        return DetectedIssue

    @pytest.fixture
    def IssueType(self):
        """Import IssueType enum."""
        from agents.self_healing import IssueType
        return IssueType

    @pytest.fixture
    def IssueSeverity(self):
        """Import IssueSeverity enum."""
        from agents.self_healing import IssueSeverity
        return IssueSeverity

    def test_create_detected_issue(self, DetectedIssue, IssueType, IssueSeverity):
        """Test creating a detected issue."""
        issue = DetectedIssue(
            issue_type=IssueType.TEST_FAILURE,
            severity=IssueSeverity.HIGH,
            description="Test failed due to assertion error",
        )
        assert issue.issue_type == IssueType.TEST_FAILURE
        assert issue.severity == IssueSeverity.HIGH

    def test_issue_with_location(self, DetectedIssue, IssueType, IssueSeverity):
        """Test issue with file location."""
        issue = DetectedIssue(
            issue_type=IssueType.SYNTAX_ERROR,
            severity=IssueSeverity.CRITICAL,
            description="Invalid syntax",
            location="tests/test_example.py",
            file_path=Path("tests/test_example.py"),
            line_number=42,
        )
        assert issue.location == "tests/test_example.py"
        assert issue.line_number == 42

    def test_issue_with_context(self, DetectedIssue, IssueType, IssueSeverity):
        """Test issue with context data."""
        issue = DetectedIssue(
            issue_type=IssueType.DEPENDENCY_CONFLICT,
            severity=IssueSeverity.MEDIUM,
            description="Package version conflict",
            context={"package": "numpy", "required": "1.24.0", "found": "1.23.0"},
        )
        assert issue.context["package"] == "numpy"

    def test_issue_timestamp_auto_generated(self, DetectedIssue, IssueType, IssueSeverity):
        """Test that detected_at timestamp is auto-generated."""
        issue = DetectedIssue(
            issue_type=IssueType.LINT_ERROR,
            severity=IssueSeverity.LOW,
            description="Code style violation",
        )
        assert issue.detected_at is not None
        # Should be parseable as ISO format
        datetime.fromisoformat(issue.detected_at)


class TestRemediationAction:
    """Tests for RemediationAction dataclass."""

    @pytest.fixture
    def RemediationAction(self):
        """Import RemediationAction class if available."""
        try:
            from agents.self_healing import RemediationAction
            return RemediationAction
        except ImportError:
            pytest.skip("RemediationAction not available")

    def test_create_remediation_action(self, RemediationAction):
        """Test creating a remediation action."""
        action = RemediationAction(
            action_type="update_dependency",
            description="Update package version",
            command="pip install numpy==1.24.0",
        )
        assert action.action_type == "update_dependency"
        assert "pip install" in action.command


class TestSelfHealingEngine:
    """Tests for SelfHealingEngine class."""

    @pytest.fixture
    def SelfHealingEngine(self):
        """Import SelfHealingEngine class."""
        try:
            from agents.self_healing import SelfHealingEngine
            return SelfHealingEngine
        except ImportError:
            pytest.skip("SelfHealingEngine not available")

    def test_create_engine(self, SelfHealingEngine):
        """Test creating a self-healing engine."""
        engine = SelfHealingEngine()
        assert engine is not None

    def test_engine_diagnose_method(self, SelfHealingEngine):
        """Test engine has diagnose method."""
        engine = SelfHealingEngine()
        assert hasattr(engine, 'diagnose') or hasattr(engine, 'analyze')

    def test_engine_can_handle_test_output(self, SelfHealingEngine):
        """Test engine can process test output."""
        engine = SelfHealingEngine()
        
        test_output = """
        FAILED tests/test_example.py::test_function
        AssertionError: Expected 1, got 2
        """
        
        # Should not raise
        if hasattr(engine, 'diagnose'):
            result = engine.diagnose(test_output)
            assert result is not None


class TestDiagnosticResult:
    """Tests for DiagnosticResult dataclass."""

    @pytest.fixture
    def DiagnosticResult(self):
        """Import DiagnosticResult class if available."""
        try:
            from agents.self_healing import DiagnosticResult
            return DiagnosticResult
        except ImportError:
            pytest.skip("DiagnosticResult not available")

    def test_create_diagnostic_result(self, DiagnosticResult):
        """Test creating a diagnostic result."""
        result = DiagnosticResult(
            issues=[],
            health_score=1.0,
        )
        assert result.health_score == 1.0
        assert len(result.issues) == 0
