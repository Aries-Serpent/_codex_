"""Tests for validate_handoff.py - Handoff Validation Utility."""

import json

# Import the module under test
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "handoff"))

from validate_handoff import (
    HandoffValidator,
    ValidationReport,
    ValidationResult,
)


class TestValidationResult:
    """Tests for ValidationResult class."""

    def test_init(self):
        """Test initialization."""
        result = ValidationResult("Test Check")
        assert result.name == "Test Check", "Result must not be empty"
        assert result.passed is False, "Result must not be empty"
        assert result.message == "", "Result must not be empty"
        assert result.severity == "info", "Result must not be empty"
        assert result.details == {}, "Result must not be empty"

    def test_pass_check(self):
        """Test marking check as passed."""
        result = ValidationResult("Test")
        result.pass_check("All good", {"key": "value"})

        assert result.passed is True, "Result must not be empty"
        assert result.message == "All good", "Result must not be empty"
        assert result.severity == "info", "Result must not be empty"
        assert result.details == {"key": "value"}, "Result must not be empty"

    def test_warn(self):
        """Test marking check as warning."""
        result = ValidationResult("Test")
        result.warn("Be careful", {"warning": "data"})

        assert result.passed is True, "Result must not be empty"
        assert result.message == "Be careful", "Result must not be empty"
        assert result.severity == "warning", "Result must not be empty"
        assert result.details == {"warning": "data"}, "Result must not be empty"

    def test_fail(self):
        """Test marking check as failed."""
        result = ValidationResult("Test")
        result.fail("Something wrong", {"error": "data"})

        assert result.passed is False, "Result must not be empty"
        assert result.message == "Something wrong", "Result must not be empty"
        assert result.severity == "error", "Result must not be empty"
        assert result.details == {"error": "data"}, "Result must not be empty"

    def test_to_dict(self):
        """Test conversion to dictionary."""
        result = ValidationResult("Test Check")
        result.pass_check("OK")

        data = result.to_dict()

        assert data["name"] == "Test Check", "Data must not be empty"
        assert data["passed"] is True, "Data must not be empty"
        assert data["message"] == "OK", "Data must not be empty"
        assert data["severity"] == "info", "Data must not be empty"


class TestValidationReport:
    """Tests for ValidationReport class."""

    def test_init(self):
        """Test initialization."""
        report = ValidationReport("Test Report")
        assert report.title == "Test Report", "title is not valid"
        assert report.results == [], "Result must not be empty"
        assert report.summary["total"] == 0, "rep is not valid"

    def test_add_result_passed(self):
        """Test adding passed result."""
        report = ValidationReport()
        result = ValidationResult("Check 1")
        result.pass_check("OK")

        report.add_result(result)

        assert len(report.results) == 1, "Collection must not be empty"
        assert report.summary["total"] == 1, "rep is not valid"
        assert report.summary["passed"] == 1, "rep is not valid"
        assert report.summary["failed"] == 0, "rep is not valid"

    def test_add_result_warning(self):
        """Test adding warning result."""
        report = ValidationReport()
        result = ValidationResult("Check 1")
        result.warn("Caution")

        report.add_result(result)

        assert report.summary["total"] == 1, "rep is not valid"
        assert report.summary["passed"] == 1, "rep is not valid"
        assert report.summary["warnings"] == 1, "rep is not valid"
        assert report.summary["failed"] == 0, "rep is not valid"

    def test_add_result_failed(self):
        """Test adding failed result."""
        report = ValidationReport()
        result = ValidationResult("Check 1")
        result.fail("Error")

        report.add_result(result)

        assert report.summary["total"] == 1, "rep is not valid"
        assert report.summary["passed"] == 0, "rep is not valid"
        assert report.summary["failed"] == 1, "rep is not valid"

    def test_is_valid_all_passed(self):
        """Test is_valid when all checks pass."""
        report = ValidationReport()
        for i in range(3):
            result = ValidationResult(f"Check {i}")
            result.pass_check("OK")
            report.add_result(result)

        assert report.is_valid is True, "is_valid is not valid"

    def test_is_valid_with_failures(self):
        """Test is_valid when some checks fail."""
        report = ValidationReport()

        result1 = ValidationResult("Check 1")
        result1.pass_check("OK")
        report.add_result(result1)

        result2 = ValidationResult("Check 2")
        result2.fail("Error")
        report.add_result(result2)

        assert report.is_valid is False, "is_valid is not valid"

    def test_is_valid_with_warnings(self):
        """Test is_valid with warnings only."""
        report = ValidationReport()
        result = ValidationResult("Check 1")
        result.warn("Warning")
        report.add_result(result)

        assert report.is_valid is True, "is_valid is not valid"

    def test_to_markdown(self):
        """Test markdown generation."""
        report = ValidationReport("Test Report")

        result1 = ValidationResult("Check 1")
        result1.pass_check("All good")
        report.add_result(result1)

        result2 = ValidationResult("Check 2")
        result2.warn("Be careful")
        report.add_result(result2)

        markdown = report.to_markdown()

        assert "Test Report" in markdown, "Condition must be true"
        assert "PASSED WITH WARNINGS" in markdown, "Condition must be true"
        assert "Check 1" in markdown, "Condition must be true"
        assert "Check 2" in markdown, "Condition must be true"
        assert "All good" in markdown, "Condition must be true"
        assert "Be careful" in markdown, "Condition must be true"

    def test_to_dict(self):
        """Test dictionary conversion."""
        report = ValidationReport("Test")
        result = ValidationResult("Check")
        result.pass_check("OK")
        report.add_result(result)

        data = report.to_dict()

        assert data["title"] == "Test", "Data must not be empty"
        assert data["is_valid"] is True, "Data must not be empty"
        assert len(data["results"]) == 1, "Collection must not be empty"
        assert "summary" in data, "Data must not be empty"


class TestHandoffValidator:
    """Tests for HandoffValidator class."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def validator(self):
        """Create validator instance."""
        return HandoffValidator()

    def test_init_loads_tracking(self, temp_dir):
        """Test that init loads tracking data."""
        tracking_file = temp_dir / "tracking.json"
        tracking_data = {"handoffs": [{"id": "HO-001"}], "metrics": {}}

        with open(tracking_file, "w") as f:
            json.dump(tracking_data, f)

        with patch("validate_handoff.TRACKING_FILE", tracking_file):
            validator = HandoffValidator()

        assert len(validator.tracking_data["handoffs"]) == 1, "Collection must not be empty"

    def test_get_handoff_found(self, validator):
        """Test getting existing handoff."""
        validator.tracking_data = {"handoffs": [{"id": "HO-001", "status": "pending"}]}

        result = validator.get_handoff("HO-001")

        assert result is not None, "result must be initialized"
        assert result["id"] == "HO-001", "Result must not be empty"

    def test_get_handoff_not_found(self, validator):
        """Test getting non-existent handoff."""
        validator.tracking_data = {"handoffs": []}

        result = validator.get_handoff("HO-999")

        assert result is None, "Result must not be empty"

    def test_validate_context_completeness_success(self, validator):
        """Test context completeness validation - success."""
        handoff = {
            "id": "HO-001",
            "from_agent": "copilot",
            "to_agent": "codex",
            "phase": "Plan 1",
            "status": "pending",
            "created": "2026-02-05T12:00:00Z",
        }

        result = validator.validate_context_completeness(handoff)

        assert result.passed is True, "Result must not be empty"

    def test_validate_context_completeness_missing_fields(self, validator):
        """Test context completeness validation - missing fields."""
        handoff = {"id": "HO-001", "status": "pending"}

        result = validator.validate_context_completeness(handoff)

        assert result.passed is False, "Result must not be empty"
        assert "Missing" in result.message, "Result must not be empty"

    def test_validate_context_summary_with_data(self, validator):
        """Test context summary validation with data."""
        handoff = {
            "context_summary": {"completed_tasks": 5, "deliverables": 3, "files_modified": 10}
        }

        result = validator.validate_context_summary(handoff)

        assert result.passed is True, "Result must not be empty"
        assert "18 work items" in result.message, "Result must not be empty"

    def test_validate_context_summary_empty(self, validator):
        """Test context summary validation - empty."""
        handoff = {
            "context_summary": {"completed_tasks": 0, "deliverables": 0, "files_modified": 0}
        }

        result = validator.validate_context_summary(handoff)

        assert result.severity == "warning", "Result must not be empty"

    def test_validate_context_summary_missing(self, validator):
        """Test context summary validation - missing."""
        handoff = {}

        result = validator.validate_context_summary(handoff)

        assert result.severity == "warning", "Result must not be empty"
        assert "No context summary" in result.message, "Result must not be empty"

    def test_validate_deliverables_exist_all_present(self, validator, temp_dir):
        """Test deliverables validation - all exist."""
        # Create test files
        file1 = temp_dir / "file1.py"
        file2 = temp_dir / "file2.py"
        file1.touch()
        file2.touch()

        with patch("validate_handoff.REPO_ROOT", temp_dir):
            result = validator.validate_deliverables_exist(["file1.py", "file2.py"])

        assert result.passed is True, "Result must not be empty"
        assert "All 2 deliverables exist" in result.message, "Result must not be empty"

    def test_validate_deliverables_exist_some_missing(self, validator, temp_dir):
        """Test deliverables validation - some missing."""
        file1 = temp_dir / "file1.py"
        file1.touch()

        with patch("validate_handoff.REPO_ROOT", temp_dir):
            result = validator.validate_deliverables_exist(["file1.py", "missing.py"])

        assert result.passed is False, "Result must not be empty"
        assert "missing" in result.message.lower(), "Result must not be empty"

    def test_validate_deliverables_exist_empty(self, validator):
        """Test deliverables validation - empty list."""
        result = validator.validate_deliverables_exist([])

        assert result.severity == "warning", "Result must not be empty"

    def test_validate_timeout_within_limit(self, validator):
        """Test timeout validation - within limit."""
        now = datetime.utcnow()
        created = (now - timedelta(minutes=30)).isoformat() + "Z"

        handoff = {"status": "pending", "created": created}

        result = validator.validate_timeout(handoff, timeout_minutes=60)

        assert result.passed is True, "Result must not be empty"

    def test_validate_timeout_exceeded(self, validator):
        """Test timeout validation - exceeded."""
        now = datetime.utcnow()
        created = (now - timedelta(minutes=90)).isoformat() + "Z"

        handoff = {"status": "pending", "created": created}

        result = validator.validate_timeout(handoff, timeout_minutes=60)

        assert result.passed is False, "Result must not be empty"
        assert "timed out" in result.message, "Result must not be empty"

    def test_validate_timeout_completed_status(self, validator):
        """Test timeout validation - completed status."""
        handoff = {"status": "complete", "created": "2026-01-01T00:00:00Z"}  # Very old

        result = validator.validate_timeout(handoff)

        assert result.passed is True, "Result must not be empty"
        assert "not in active state" in result.message, "Result must not be empty"

    def test_validate_chain_integrity_success(self, validator):
        """Test chain integrity - valid chain."""
        validator.tracking_data = {
            "handoffs": [
                {
                    "id": "HO-001",
                    "from_agent": "copilot",
                    "to_agent": "codex",
                    "status": "complete",
                    "created": "2026-02-05T10:00:00Z",
                },
                {
                    "id": "HO-002",
                    "from_agent": "codex",
                    "to_agent": "copilot",
                    "status": "complete",
                    "created": "2026-02-05T11:00:00Z",
                },
            ]
        }

        result = validator.validate_chain_integrity()

        assert result.passed is True, "Result must not be empty"

    def test_validate_chain_integrity_agent_mismatch(self, validator):
        """Test chain integrity - agent mismatch."""
        validator.tracking_data = {
            "handoffs": [
                {
                    "id": "HO-001",
                    "from_agent": "copilot",
                    "to_agent": "codex",
                    "status": "complete",
                    "created": "2026-02-05T10:00:00Z",
                },
                {
                    "id": "HO-002",
                    "from_agent": "copilot",
                    "to_agent": "codex",  # Should be from codex
                    "status": "complete",
                    "created": "2026-02-05T11:00:00Z",
                },
            ]
        }

        result = validator.validate_chain_integrity()

        assert result.passed is False, "Result must not be empty"
        assert "mismatch" in result.message.lower() or "issues" in result.message.lower(), "Result must not be empty"

    def test_validate_handoff_full(self, validator):
        """Test full handoff validation."""
        validator.tracking_data = {
            "handoffs": [
                {
                    "id": "HO-001",
                    "from_agent": "copilot",
                    "to_agent": "codex",
                    "phase": "Plan 1",
                    "status": "pending",
                    "created": datetime.utcnow().isoformat() + "Z",
                    "context_summary": {
                        "completed_tasks": 3,
                        "deliverables": 2,
                        "files_modified": 5,
                    },
                }
            ]
        }

        report = validator.validate_handoff("HO-001")

        assert report.is_valid is True, "is_valid is not valid"
        assert len(report.results) >= 2, "Collection must not be empty"

    def test_validate_handoff_not_found(self, validator):
        """Test validation of non-existent handoff."""
        validator.tracking_data = {"handoffs": []}

        report = validator.validate_handoff("HO-999")

        assert report.is_valid is False, "is_valid is not valid"
        assert "not found" in report.results[0].message, "Result must not be empty"

    def test_pre_handoff_check(self, validator, temp_dir):
        """Test pre-handoff check."""
        action_log = temp_dir / "action_log.ndjson"
        action_log.touch()

        with patch("validate_handoff.ACTION_LOG_PATH", action_log):
            report = validator.pre_handoff_check("Test Phase")

        assert len(report.results) >= 3, "Collection must not be empty"
        assert "Pre-Handoff Check" in report.title, "Condition must be true"

    def test_post_handoff_check_success(self, validator):
        """Test post-handoff check - success."""
        validator.tracking_data = {
            "handoffs": [
                {
                    "id": "HO-001",
                    "status": "pending",
                    "context_summary": {
                        "completed_tasks": 1,
                        "deliverables": 1,
                        "files_modified": 1,
                    },
                }
            ]
        }

        report = validator.post_handoff_check("HO-001")

        assert "Post-Handoff Check" in report.title, "Condition must be true"
        assert any("recorded" in r.message.lower() for r in report.results), "Result must not be empty"

    def test_post_handoff_check_not_found(self, validator):
        """Test post-handoff check - not found."""
        validator.tracking_data = {"handoffs": []}

        report = validator.post_handoff_check("HO-999")

        assert report.is_valid is False, "is_valid is not valid"

    def test_chain_validation(self, validator):
        """Test chain validation."""
        validator.tracking_data = {
            "handoffs": [
                {
                    "id": "HO-001",
                    "from_agent": "copilot",
                    "to_agent": "codex",
                    "status": "complete",
                    "created": datetime.utcnow().isoformat() + "Z",
                }
            ],
            "metrics": {"success_rate": 95},
        }

        report = validator.chain_validation()

        assert "Chain Validation" in report.title, "Condition must be true"
        assert len(report.results) >= 2, "Collection must not be empty"

    def test_mark_failed_for_retry_success(self, validator, temp_dir):
        """Test marking handoff for retry - success."""
        tracking_file = temp_dir / "tracking.json"
        validator.tracking_data = {
            "handoffs": [{"id": "HO-001", "status": "failed", "retry_count": 0}],
            "metrics": {"failed": 1, "pending": 0},
        }

        with patch("validate_handoff.TRACKING_FILE", tracking_file):
            success, message = validator.mark_failed_for_retry("HO-001")

        assert success is True, "success is not valid"
        assert "retry" in message.lower(), "Condition must be true"

    def test_mark_failed_for_retry_max_exceeded(self, validator):
        """Test marking handoff for retry - max exceeded."""
        validator.tracking_data = {
            "handoffs": [{"id": "HO-001", "status": "failed", "retry_count": 3}]
        }

        success, message = validator.mark_failed_for_retry("HO-001", max_retries=3)

        assert success is False, "success is not valid"
        assert "exceeded" in message.lower(), "Condition must be true"

    def test_mark_failed_for_retry_not_found(self, validator):
        """Test marking handoff for retry - not found."""
        validator.tracking_data = {"handoffs": []}

        success, message = validator.mark_failed_for_retry("HO-999")

        assert success is False, "success is not valid"
        assert "not found" in message.lower(), "Condition must be true"
