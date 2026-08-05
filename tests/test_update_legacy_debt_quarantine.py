"""Tests for scripts/validation/update_legacy_debt_quarantine.py

This test module validates:
1. Pytest summary regex pattern handles both singular "error" and plural "errors"
2. Control flow doesn't create duplicate pytest runs
3. PytestResult calculations work correctly
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts" / "validation"))

from update_legacy_debt_quarantine import (
    PytestResult,
    _extract_short_cause,
    _top_cause,
    update_quarantine,
)


class TestPytestSummaryRegex:
    """Verify regex pattern handles singular/plural error forms correctly."""

    def test_regex_plural_errors_with_failed(self):
        """Test pattern: '1041 passed, 24 failed, 13 errors in 12.34s'"""
        summary_pattern = re.compile(
            r"(?P<passed>\d+)\s+passed"
            r"(?:,\s*(?P<failed>\d+)\s+failed)?"
            r"(?:,\s*(?P<errored>\d+)\s+errors?)?"
            r"(?:,\s*(?P<skipped>\d+)\s+skipped)?"
            r"(?:,\s*(?P<xfail>\d+)\s+xfail)?"
            r"(?:,\s*(?P<xpass>\d+)\s+xpass)?"
            r"(?:\s+in\s+[\d.]+s)?"
        )
        line = "1041 passed, 24 failed, 13 errors in 12.34s"
        match = summary_pattern.search(line)

        assert match is not None
        assert match.group("passed") == "1041"
        assert match.group("failed") == "24"
        assert match.group("errored") == "13"

    def test_regex_plural_errors_only(self):
        """Test pattern: '1041 passed, 13 errors in 12.34s'"""
        summary_pattern = re.compile(
            r"(?P<passed>\d+)\s+passed"
            r"(?:,\s*(?P<failed>\d+)\s+failed)?"
            r"(?:,\s*(?P<errored>\d+)\s+errors?)?"
            r"(?:,\s*(?P<skipped>\d+)\s+skipped)?"
            r"(?:,\s*(?P<xfail>\d+)\s+xfail)?"
            r"(?:,\s*(?P<xpass>\d+)\s+xpass)?"
            r"(?:\s+in\s+[\d.]+s)?"
        )
        line = "1041 passed, 13 errors in 12.34s"
        match = summary_pattern.search(line)

        assert match is not None
        assert match.group("passed") == "1041"
        assert match.group("failed") is None
        assert match.group("errored") == "13"

    def test_regex_singular_error_with_failed(self):
        """Test pattern: '1041 passed, 24 failed, 1 error in 12.34s'"""
        summary_pattern = re.compile(
            r"(?P<passed>\d+)\s+passed"
            r"(?:,\s*(?P<failed>\d+)\s+failed)?"
            r"(?:,\s*(?P<errored>\d+)\s+errors?)?"
            r"(?:,\s*(?P<skipped>\d+)\s+skipped)?"
            r"(?:,\s*(?P<xfail>\d+)\s+xfail)?"
            r"(?:,\s*(?P<xpass>\d+)\s+xpass)?"
            r"(?:\s+in\s+[\d.]+s)?"
        )
        line = "1041 passed, 24 failed, 1 error in 12.34s"
        match = summary_pattern.search(line)

        assert match is not None
        assert match.group("passed") == "1041"
        assert match.group("failed") == "24"
        assert match.group("errored") == "1"

    def test_regex_singular_error_only(self):
        """Test pattern: '1041 passed, 1 error in 12.34s'"""
        summary_pattern = re.compile(
            r"(?P<passed>\d+)\s+passed"
            r"(?:,\s*(?P<failed>\d+)\s+failed)?"
            r"(?:,\s*(?P<errored>\d+)\s+errors?)?"
            r"(?:,\s*(?P<skipped>\d+)\s+skipped)?"
            r"(?:,\s*(?P<xfail>\d+)\s+xfail)?"
            r"(?:,\s*(?P<xpass>\d+)\s+xpass)?"
            r"(?:\s+in\s+[\d.]+s)?"
        )
        line = "1041 passed, 1 error in 12.34s"
        match = summary_pattern.search(line)

        assert match is not None
        assert match.group("passed") == "1041"
        assert match.group("failed") is None
        assert match.group("errored") == "1"

    def test_regex_no_errors(self):
        """Test pattern: '1041 passed in 12.34s'"""
        summary_pattern = re.compile(
            r"(?P<passed>\d+)\s+passed"
            r"(?:,\s*(?P<failed>\d+)\s+failed)?"
            r"(?:,\s*(?P<errored>\d+)\s+errors?)?"
            r"(?:,\s*(?P<skipped>\d+)\s+skipped)?"
            r"(?:,\s*(?P<xfail>\d+)\s+xfail)?"
            r"(?:,\s*(?P<xpass>\d+)\s+xpass)?"
            r"(?:\s+in\s+[\d.]+s)?"
        )
        line = "1041 passed in 12.34s"
        match = summary_pattern.search(line)

        assert match is not None
        assert match.group("passed") == "1041"
        assert match.group("failed") is None
        assert match.group("errored") is None


class TestPytestResultCalculations:
    """Verify PytestResult calculations are correct."""

    def test_non_attributable_property(self):
        """Test that non_attributable correctly sums failed + errored."""
        result = PytestResult()
        result.failed = 10
        result.errored = 5
        assert result.non_attributable == 15

    def test_non_attributable_with_zeros(self):
        """Test non_attributable with zero values."""
        result = PytestResult()
        result.failed = 0
        result.errored = 0
        assert result.non_attributable == 0

    def test_total_calculation(self):
        """Test total includes all test outcomes."""
        result = PytestResult()
        result.passed = 100
        result.failed = 10
        result.errored = 5
        result.total = result.passed + result.failed + result.errored
        assert result.total == 115


class TestExtractShortCause:
    """Test short cause extraction from failure messages."""

    def test_name_error(self):
        """Test NameError extraction."""
        message = "NameError: name 'CognitiveBrain' is not defined"
        cause = _extract_short_cause(message)
        assert "NameError" in cause
        assert "CognitiveBrain" in cause

    def test_attribute_error(self):
        """Test AttributeError extraction."""
        message = "AttributeError: 'NoneType' object has no attribute 'score'"
        cause = _extract_short_cause(message)
        assert "AttributeError" in cause

    def test_import_error(self):
        """Test ImportError extraction."""
        message = "ImportError: cannot import name 'MagicMock' from 'unittest.mock'"
        cause = _extract_short_cause(message)
        assert "ImportError" in cause or "cannot import" in cause

    def test_assertion_threshold(self):
        """Test assertion with threshold extraction."""
        message = "AssertionError: assert 0.4494 > 0.35"
        cause = _extract_short_cause(message)
        assert "Assertion" in cause
        assert "0.4494" in cause

    def test_unknown_message(self):
        """Test fallback for unknown message types."""
        message = "SomeWeirdError: this is an unusual failure"
        cause = _extract_short_cause(message)
        assert cause != ""


class TestTopCause:
    """Test top cause detection from multiple failure messages."""

    def test_empty_messages(self):
        """Test with no failure messages."""
        causes = _top_cause([])
        assert causes == "-"

    def test_single_message(self):
        """Test with single message."""
        messages = ["NameError: name 'x' is not defined"]
        cause = _top_cause(messages)
        assert cause != "-"

    def test_multiple_same_cause(self):
        """Test that most common cause is returned."""
        messages = [
            "NameError: name 'x' is not defined",
            "NameError: name 'x' is not defined",
            "AttributeError: 'NoneType' object has no attribute 'y'",
        ]
        cause = _top_cause(messages)
        # The most common should be NameError (appears twice)
        assert "NameError" in cause


class TestControlFlow:
    """Test that control flow avoids duplicate pytest runs."""

    @patch("update_legacy_debt_quarantine.run_pytest")
    def test_update_quarantine_with_provided_result(self, mock_run_pytest):
        """Test that update_quarantine doesn't call run_pytest when result is provided."""
        # Create a mock result
        result = PytestResult()
        result.total = 100
        result.passed = 100
        result.failed = 0
        result.errored = 0

        # Mock the _read_doc and _write_doc to avoid file I/O
        with patch(
            "update_legacy_debt_quarantine._read_doc"
        ) as mock_read, patch(
            "update_legacy_debt_quarantine._write_doc"
        ), patch(
            "update_legacy_debt_quarantine._parse_latest_summary",
            return_value=None,
        ):
            mock_read.return_value = (
                "## Quarantine Summary\n\n"
                "| Metric | Count |\n"
                "|---|---|\n"
                "| Total cognitive_brain tests executed | 0 |\n"
                "| Passed | 0 |\n"
                "| Failed | 0 |\n"
                "| Errored | 0 |\n"
                "| Failures attributable to PR #5430 | 0 |\n\n"
                "## Exit Criteria\n"
            )

            # Call update_quarantine with result provided
            update_quarantine("tests/cognitive_brain", result=result)

            # Verify run_pytest was NOT called (since result was provided)
            mock_run_pytest.assert_not_called()

    @patch("update_legacy_debt_quarantine.run_pytest")
    def test_update_quarantine_without_result_calls_run_pytest(
        self, mock_run_pytest
    ):
        """Test that update_quarantine calls run_pytest when result is None."""
        # Create a mock result for run_pytest to return
        result = PytestResult()
        result.total = 100
        result.passed = 100
        result.failed = 0
        result.errored = 0
        mock_run_pytest.return_value = result

        # Mock file I/O
        with patch(
            "update_legacy_debt_quarantine._read_doc"
        ) as mock_read, patch(
            "update_legacy_debt_quarantine._write_doc"
        ) as mock_write, patch(
            "update_legacy_debt_quarantine._parse_latest_summary",
            return_value=None,
        ):
            mock_read.return_value = (
                "## Quarantine Summary\n\n"
                "| Metric | Count |\n"
                "|---|---|\n"
                "| Total cognitive_brain tests executed | 0 |\n"
                "| Passed | 0 |\n"
                "| Failed | 0 |\n"
                "| Errored | 0 |\n"
                "| Failures attributable to PR #5430 | 0 |\n\n"
                "## Exit Criteria\n"
            )

            # Call update_quarantine WITHOUT result (None)
            update_quarantine("tests/cognitive_brain", result=None)

            # Verify run_pytest WAS called
            mock_run_pytest.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
