"""
Tests for date sanitization policy enforcer.

Ensures that actual timestamps are preserved while planning terminology is removed.
"""

import pytest

from scripts.security.date_sanitizer import sanitize_planning_dates


class TestPreservedContexts:
    """Test that dates in technical/historical contexts are preserved."""

    def test_version_date_preserved(self):
        """Version release dates should be preserved."""
        text = "Version: 1.2.3 Released: 2026-01-05"
        sanitized, replacements = sanitize_planning_dates(text)
        assert "2026-01-05" in sanitized, "Condition must be true"
        assert len(replacements) == 0, "Replacements must not be empty"

    def test_session_date_preserved(self):
        """Session dates should be preserved."""
        text = "**Session Date:** 2026-01-06"
        sanitized, replacements = sanitize_planning_dates(text)
        assert "2026-01-06" in sanitized, "Condition must be true"
        assert len(replacements) == 0, "Replacements must not be empty"

    def test_created_date_preserved(self):
        """Created dates should be preserved."""
        text = "**Created:** 2026-01-05 (Session 9)"
        sanitized, replacements = sanitize_planning_dates(text)
        assert "2026-01-05" in sanitized, "Condition must be true"
        assert len(replacements) == 0, "Replacements must not be empty"

    def test_completion_date_preserved(self):
        """Completion dates should be preserved."""
        text = "**Completion Date:** 2026-01-06T05:30:00Z"
        sanitized, replacements = sanitize_planning_dates(text)
        assert "2026-01-06" in sanitized, "Condition must be true"
        assert len(replacements) == 0, "Replacements must not be empty"

    def test_timestamp_preserved(self):
        """ISO timestamps should be preserved."""
        text = "Timestamp: 2026-01-06T12:34:56Z"
        sanitized, replacements = sanitize_planning_dates(text)
        assert "2026-01-06T12:34:56Z" in sanitized, "Condition must be true"
        assert len(replacements) == 0, "Replacements must not be empty"

    def test_package_version_date_preserved(self):
        """Package version release dates should be preserved."""
        text = "- **Current Version:** aiohttp 3.13.3 (latest stable, released 2026-01-03)"
        sanitized, replacements = sanitize_planning_dates(text)
        assert "2026-01-03" in sanitized, "Condition must be true"
        assert len(replacements) == 0, "Replacements must not be empty"

    def test_report_generated_date_preserved(self):
        """Report generation dates should be preserved."""
        text = "**Report Generated**: 2026-01-04 05:39:00 UTC"
        sanitized, replacements = sanitize_planning_dates(text)
        assert "2026-01-04" in sanitized, "Condition must be true"
        assert len(replacements) == 0, "Replacements must not be empty"

    def test_last_updated_preserved(self):
        """Last updated dates should be preserved."""
        text = "*Last Updated: 2026-01-06 21:30 UTC*"
        sanitized, replacements = sanitize_planning_dates(text)
        assert "2026-01-06" in sanitized, "Condition must be true"
        assert len(replacements) == 0, "Replacements must not be empty"


class TestPlanningTerminologyReplacement:
    """Test that planning terminology is properly sanitized."""

    def test_quarter_reference_replaced(self):
        """Quarter references like 'Q1 2026' should be replaced."""
        text = "Planned for Q1 2026"
        sanitized, replacements = sanitize_planning_dates(text)
        assert "Q1 2026" not in sanitized, "Condition must be true"
        assert "Current Cycle" in sanitized, "Condition must be true"
        assert len(replacements) > 0, "Replacements must not be empty"

    def test_phase_with_quarter_replaced(self):
        """Phase references with quarters should be replaced."""
        text = "- **Removal**: v2.0.0 (Phase 2 (Q2 2026))"
        sanitized, replacements = sanitize_planning_dates(text)
        assert "Q2 2026" not in sanitized, "Condition must be true"
        assert "Current Cycle" in sanitized, "Condition must be true"
        assert len(replacements) > 0, "Replacements must not be empty"

    def test_month_name_in_planning_replaced(self):
        """Month names in planning contexts should be replaced."""
        text = "Project deadline: January 2026"
        sanitized, replacements = sanitize_planning_dates(text)
        assert "January 2026" not in sanitized, "Condition must be true"
        assert "Current Cycle" in sanitized, "Condition must be true"
        assert len(replacements) > 0, "Replacements must not be empty"

    def test_grace_period_through_quarter(self):
        """Planning horizons with quarters should be replaced."""
        text = "- **Grace Period**: 6 months (through Phase 6 Q4 2026)"
        sanitized, replacements = sanitize_planning_dates(text)
        assert "Q4 2026" not in sanitized, "Condition must be true"
        assert "Current Cycle" in sanitized, "Condition must be true"
        assert len(replacements) > 0, "Replacements must not be empty"

    def test_deadline_by_quarter(self):
        """Deadlines with quarters should be replaced."""
        text = "Must be completed by Q3 2026"
        sanitized, replacements = sanitize_planning_dates(text)
        assert "Q3 2026" not in sanitized, "Condition must be true"
        assert "Current Cycle" in sanitized, "Condition must be true"
        assert len(replacements) > 0, "Replacements must not be empty"


class TestMixedContent:
    """Test documents with both preserved and sanitized dates."""

    def test_mixed_dates_handled_correctly(self):
        """Document with both technical and planning dates."""
        text = """
# Project Status

**Last Updated:** 2026-01-05

## Version History
- v2.0.0 released 2026-01-03

## Roadmap
- Phase 1: Q1 2026
- Phase 2: Q2 2026
- Deprecation by Q4 2026

## Recent Changes
**Session Date:** 2026-01-04
Completed migration tasks.
"""
        sanitized, replacements = sanitize_planning_dates(text)

        # Technical dates should be preserved
        assert "2026-01-05" in sanitized, "Condition must be true"
        assert "2026-01-03" in sanitized, "Condition must be true"
        assert "2026-01-04" in sanitized, "Condition must be true"

        # Planning dates should be replaced
        assert "Q1 2026" not in sanitized, "Condition must be true"
        assert "Q2 2026" not in sanitized, "Condition must be true"
        assert "Q4 2026" not in sanitized, "Condition must be true"

        # Should have replacements
        assert len(replacements) > 0, "Replacements must not be empty"

    def test_changelog_entry(self):
        """CHANGELOG.md entry with both types of dates."""
        text = """
## [2.0.0] - 2026-01-03

### Deprecated
- `conf/` directory will be removed in favor of `configs/` (Phase 2 (Q2 2026))
"""
        sanitized, _replacements = sanitize_planning_dates(text)

        # Version date should be preserved
        assert "2026-01-03" in sanitized, "Condition must be true"

        # Planning quarter should be replaced
        assert "Q2 2026" not in sanitized, "Condition must be true"
        assert "Current Cycle" in sanitized, "Condition must be true"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_string(self):
        """Empty string should return empty string."""
        sanitized, replacements = sanitize_planning_dates("")
        assert sanitized == "", "sanitized is not valid"
        assert len(replacements) == 0, "Replacements must not be empty"

    def test_no_dates(self):
        """Text without dates should be unchanged."""
        text = "This is some regular text without any dates."
        sanitized, replacements = sanitize_planning_dates(text)
        assert sanitized == text, "sanitized is not valid"
        assert len(replacements) == 0, "Replacements must not be empty"

    def test_multiple_quarters_same_line(self):
        """Multiple quarter references on same line."""
        text = "Phases: Q1 2026, Q2 2026, Q3 2026"
        sanitized, replacements = sanitize_planning_dates(text)
        assert "Q1 2026" not in sanitized, "Condition must be true"
        assert "Q2 2026" not in sanitized, "Condition must be true"
        assert "Q3 2026" not in sanitized, "Condition must be true"
        assert len(replacements) >= 3, "Replacements must not be empty"

    def test_case_insensitivity(self):
        """Patterns should match regardless of case."""
        text = "deadline: q1 2026"
        sanitized, _replacements = sanitize_planning_dates(text)
        assert "q1 2026" not in sanitized, "Condition must be true"
        assert "current cycle" in sanitized.lower(), "Condition must be true"


class TestRealWorldExamples:
    """Test with real-world examples from the repository."""

    def test_ai_agent_utilities_registry(self):
        """Test the specific example from the problem statement."""
        text = "**Created:** 2026-01-05 (Session 9)"
        sanitized, replacements = sanitize_planning_dates(text)

        # This date should be preserved because it's in a "Created:" context
        assert "2026-01-05" in sanitized, "Condition must be true"
        assert "Current Cycle" not in sanitized, "Condition must be true"
        assert len(replacements) == 0, "Replacements must not be empty"

    def test_deprecation_notice(self):
        """Test deprecation notice with mixed dates."""
        text = """
- **Grace Period**: 6 months (through Phase 6 Q4 2026)
- **Removal**: v2.0.0 (Phase 2 (Q2 2026))
"""
        sanitized, replacements = sanitize_planning_dates(text)

        # Planning quarters should be replaced
        assert "Q4 2026" not in sanitized, "Condition must be true"
        assert "Q2 2026" not in sanitized, "Condition must be true"
        assert "Current Cycle" in sanitized, "Condition must be true"
        assert len(replacements) > 0, "Replacements must not be empty"

    def test_session_completion_summary(self):
        """Test session completion with timestamps."""
        text = """
# Session Completion Summary - 2026-01-06 - 100% Success
> **Date:** 2026-01-06T06:35:00Z

**Achievement Date:** 2026-01-06T06:35:00Z
**Session End:** 2026-01-06T05:30:00Z
"""
        sanitized, replacements = sanitize_planning_dates(text)

        # All these are session/technical dates and should be preserved
        assert "2026-01-06" in sanitized, "Condition must be true"
        assert sanitized.count("2026-01-06") >= 3, "Value must be greater than zero"
        assert len(replacements) == 0, "Replacements must not be empty"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
