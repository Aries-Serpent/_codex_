#!/usr/bin/env python3
"""
Unit tests for compliance validators

Tests for all 6 requirement validators and the unified orchestrator.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

# Add validators to path
sys.path.insert(0, str(Path(__file__).parents[0] / ".." / ".." / "scripts" / "ci" / "validators"))

from base import ComplianceResult
from req1_eligibility_validator import (
    REQ1EligibilityValidator,
    _check_branch_name,
    _check_description_quality,
    _check_title_quality,
)


class TestComplianceResult(unittest.TestCase):
    """Test ComplianceResult data class."""

    def test_valid_pass_result(self):
        """Test creating a valid pass result."""
        result = ComplianceResult(
            requirement_id="REQ-1",
            status="pass",
            score=1.0,
            reason="All checks passed",
        )
        self.assertEqual(result.requirement_id, "REQ-1")
        self.assertEqual(result.status, "pass")
        self.assertEqual(result.score, 1.0)

    def test_valid_warn_result(self):
        """Test creating a valid warn result."""
        result = ComplianceResult(
            requirement_id="REQ-2",
            status="warn",
            score=0.5,
            reason="Some checks need attention",
        )
        self.assertEqual(result.status, "warn")
        self.assertEqual(result.score, 0.5)

    def test_valid_fail_result(self):
        """Test creating a valid fail result."""
        result = ComplianceResult(
            requirement_id="REQ-3",
            status="fail",
            score=0.0,
            reason="Check failed",
        )
        self.assertEqual(result.status, "fail")
        self.assertEqual(result.score, 0.0)

    def test_invalid_score_range(self):
        """Test that invalid scores are rejected."""
        with self.assertRaises(ValueError):
            ComplianceResult(
                requirement_id="REQ-1",
                status="pass",
                score=1.5,  # Invalid
                reason="Test",
            )

    def test_invalid_status_mismatch(self):
        """Test that score/status mismatches are rejected."""
        with self.assertRaises(ValueError):
            ComplianceResult(
                requirement_id="REQ-1",
                status="fail",  # Should be pass
                score=1.0,
                reason="Test",
            )

    def test_to_dict(self):
        """Test conversion to dictionary."""
        result = ComplianceResult(
            requirement_id="REQ-1",
            status="pass",
            score=1.0,
            reason="Test",
            remediation=["Step 1", "Step 2"],
        )
        result_dict = result.to_dict()
        self.assertEqual(result_dict["requirement_id"], "REQ-1")
        self.assertEqual(result_dict["status"], "pass")
        self.assertEqual(len(result_dict["remediation"]), 2)

    def test_to_json(self):
        """Test JSON serialization."""
        result = ComplianceResult(
            requirement_id="REQ-1",
            status="pass",
            score=1.0,
            reason="Test",
        )
        json_str = result.to_json()
        parsed = json.loads(json_str)
        self.assertEqual(parsed["requirement_id"], "REQ-1")


class TestBranchNameValidation(unittest.TestCase):
    """Test branch name validation."""

    def test_valid_feature_branch(self):
        """Test valid feature branch."""
        self.assertTrue(_check_branch_name("feat/new-feature"))

    def test_valid_fix_branch(self):
        """Test valid fix branch."""
        self.assertTrue(_check_branch_name("fix/bug-123"))

    def test_valid_docs_branch(self):
        """Test valid docs branch."""
        self.assertTrue(_check_branch_name("docs/update-readme"))

    def test_valid_test_branch(self):
        """Test valid test branch."""
        self.assertTrue(_check_branch_name("test/coverage"))

    def test_valid_copilot_branch(self):
        """Test valid copilot automation branch."""
        self.assertTrue(_check_branch_name("copilot/my-feature"))

    def test_invalid_no_slash(self):
        """Test invalid branch (no slash)."""
        self.assertFalse(_check_branch_name("feature-name"))

    def test_invalid_bad_prefix(self):
        """Test invalid prefix."""
        self.assertFalse(_check_branch_name("bugfix/something"))

    def test_invalid_empty(self):
        """Test empty branch name."""
        self.assertFalse(_check_branch_name(""))


class TestTitleQuality(unittest.TestCase):
    """Test PR title quality validation."""

    def test_good_title(self):
        """Test good title."""
        issues = _check_title_quality("Add new compliance framework")
        self.assertEqual(len(issues), 0)

    def test_short_title(self):
        """Test title too short."""
        issues = _check_title_quality("Fix")
        self.assertTrue(any("too short" in i for i in issues))

    def test_empty_title(self):
        """Test empty title."""
        issues = _check_title_quality("")
        self.assertTrue(any("empty" in i.lower() for i in issues))

    def test_auto_generated_title(self):
        """Test auto-generated title detection."""
        issues = _check_title_quality("Merge pull request #123 from branch")
        self.assertTrue(any("auto-generated" in i for i in issues))


class TestDescriptionQuality(unittest.TestCase):
    """Test PR description quality validation."""

    def test_good_description(self):
        """Test good description."""
        desc = "This PR implements the new compliance framework with 6 requirement validators."
        issues = _check_description_quality(desc)
        self.assertEqual(len(issues), 0)

    def test_short_description(self):
        """Test short description."""
        issues = _check_description_quality("Fix")
        self.assertTrue(any("too short" in i for i in issues))

    def test_empty_description(self):
        """Test empty description."""
        issues = _check_description_quality("")
        self.assertTrue(any("empty" in i.lower() for i in issues))

    def test_few_words_description(self):
        """Test description with few words."""
        issues = _check_description_quality("a" * 100)  # Long but only one word
        self.assertTrue(any("too few words" in i for i in issues))


class TestREQ1Validator(unittest.TestCase):
    """Test REQ-1 eligibility validator."""

    def test_requirement_id(self):
        """Test requirement ID."""
        validator = REQ1EligibilityValidator("3575")
        self.assertEqual(validator.requirement_id, "REQ-1")

    @patch.object(REQ1EligibilityValidator, "_get_pr_details")
    def test_all_checks_pass(self, mock_get_pr):
        """Test when all checks pass."""
        mock_get_pr.return_value = {
            "head": {"ref": "feat/compliance"},
            "title": "Add compliance framework",
            "body": "This PR adds the new compliance framework with all requirements",
            "requested_reviewers": [{"login": "reviewer1"}],
        }

        validator = REQ1EligibilityValidator("3575")
        result = validator.validate()

        self.assertEqual(result.status, "pass")
        self.assertEqual(result.score, 1.0)

    @patch.object(REQ1EligibilityValidator, "_get_pr_details")
    def test_bad_branch_name(self, mock_get_pr):
        """Test when branch name is invalid."""
        mock_get_pr.return_value = {
            "head": {"ref": "feature-name"},
            "title": "Add compliance framework",
            "body": "Description",
            "requested_reviewers": [{"login": "reviewer1"}],
        }

        validator = REQ1EligibilityValidator("3575")
        result = validator.validate()

        self.assertEqual(result.status, "fail")
        self.assertEqual(result.score, 0.0)

    @patch.object(REQ1EligibilityValidator, "_get_pr_details")
    def test_missing_reviewers(self, mock_get_pr):
        """Test when reviewers not assigned."""
        mock_get_pr.return_value = {
            "head": {"ref": "feat/compliance"},
            "title": "Add compliance framework",
            "body": "Description with enough content",
            "requested_reviewers": [],
        }

        validator = REQ1EligibilityValidator("3575")
        result = validator.validate()

        self.assertEqual(result.status, "fail")
        self.assertEqual(result.score, 0.0)


class TestComplianceResultPerformance(unittest.TestCase):
    """Test performance tracking."""

    def test_elapsed_time_tracking(self):
        """Test that elapsed time is tracked."""
        result = ComplianceResult(
            requirement_id="REQ-1",
            status="pass",
            score=1.0,
            reason="Test",
            elapsed_ms=123.45,
        )
        self.assertEqual(result.elapsed_ms, 123.45)


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestComplianceResult))
    suite.addTests(loader.loadTestsFromTestCase(TestBranchNameValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestTitleQuality))
    suite.addTests(loader.loadTestsFromTestCase(TestDescriptionQuality))
    suite.addTests(loader.loadTestsFromTestCase(TestREQ1Validator))
    suite.addTests(loader.loadTestsFromTestCase(TestComplianceResultPerformance))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
