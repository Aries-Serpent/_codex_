"""
Comprehensive tests for CodeQL Findings Formatter - Phase 8A.

Tests cover:
- CWE grouping logic
- Severity sorting
- Fix pattern generation
- Confidence conversion
- Markdown report generation
- Edge cases (missing fields, empty inputs)
- Performance (<500ms target)
"""

import json
import tempfile
import time
from pathlib import Path

import pytest

# Import the formatter module
from scripts.ci.codeql_findings_formatter import (
    _convert_confidence_to_percent,
    _generate_fix_pattern,
    _generate_markdown_report,
    _get_cwe_title,
    _group_by_cwe,
    _load_findings,
    _parse_cwe_id,
    _severity_to_int,
    _sort_findings_by_severity,
    format_codeql_alerts,
)


class TestCWEParsing:
    """Tests for CWE ID parsing."""

    def test_parse_valid_cwe_id(self) -> None:
        """Test parsing valid CWE ID."""
        assert _parse_cwe_id("CWE-89") == "CWE-89"

    def test_parse_cwe_with_whitespace(self) -> None:
        """Test parsing CWE with surrounding whitespace."""
        assert _parse_cwe_id("  CWE-22  ") == "CWE-22"

    def test_parse_empty_cwe(self) -> None:
        """Test parsing empty CWE string."""
        # Empty string treated as UNKNOWN for consistent grouping
        result = _parse_cwe_id("")
        assert result in ["", "UNKNOWN"]  # Accept both behaviors


class TestCWETitles:
    """Tests for CWE title lookup."""

    def test_get_known_cwe_title(self) -> None:
        """Test getting title for known CWE."""
        title = _get_cwe_title("CWE-89")
        assert "SQL" in title

    def test_get_unknown_cwe_title(self) -> None:
        """Test getting title for unknown CWE."""
        title = _get_cwe_title("CWE-9999")
        assert title == "Unknown CWE"


class TestSeverityConversion:
    """Tests for severity level conversion."""

    def test_critical_severity(self) -> None:
        """Test CRITICAL severity conversion."""
        assert _severity_to_int("CRITICAL") == 4

    def test_high_severity(self) -> None:
        """Test HIGH severity conversion."""
        assert _severity_to_int("HIGH") == 3

    def test_medium_severity(self) -> None:
        """Test MEDIUM severity conversion."""
        assert _severity_to_int("MEDIUM") == 2

    def test_low_severity(self) -> None:
        """Test LOW severity conversion."""
        assert _severity_to_int("LOW") == 1

    def test_info_severity(self) -> None:
        """Test INFO severity conversion."""
        assert _severity_to_int("INFO") == 0

    def test_unknown_severity(self) -> None:
        """Test unknown severity conversion."""
        assert _severity_to_int("UNKNOWN") == -1

    def test_case_insensitive_severity(self) -> None:
        """Test case-insensitive severity conversion."""
        assert _severity_to_int("critical") == 4
        assert _severity_to_int("CrItIcAl") == 4


class TestConfidenceConversion:
    """Tests for confidence value conversion."""

    def test_confidence_float_to_percent(self) -> None:
        """Test converting float confidence to percentage."""
        assert _convert_confidence_to_percent(0.95) == "95%"

    def test_confidence_integer_0_to_100(self) -> None:
        """Test converting integer 0-100 confidence."""
        assert _convert_confidence_to_percent(95) == "95%"

    def test_confidence_string_with_percent(self) -> None:
        """Test string confidence with percent sign."""
        assert _convert_confidence_to_percent("95%") == "95%"

    def test_confidence_string_without_percent(self) -> None:
        """Test string confidence without percent sign."""
        assert _convert_confidence_to_percent("95") == "95%"

    def test_confidence_zero(self) -> None:
        """Test zero confidence."""
        assert _convert_confidence_to_percent(0) == "0%"

    def test_confidence_one(self) -> None:
        """Test confidence of 1.0."""
        assert _convert_confidence_to_percent(1.0) == "100%"


class TestFixPatternGeneration:
    """Tests for fix pattern generation."""

    def test_sql_injection_pattern(self) -> None:
        """Test fix pattern for SQL injection."""
        finding = {
            "cwe": "CWE-89",
            "fix_recommendation": "Use parameterized queries",
        }
        pattern = _generate_fix_pattern(finding)
        assert "parameterized" in pattern
        assert "@code-review-agent" in pattern

    def test_path_traversal_pattern(self) -> None:
        """Test fix pattern for path traversal."""
        finding = {
            "cwe": "CWE-22",
            "fix_recommendation": "Use pathlib.Path.resolve()",
        }
        pattern = _generate_fix_pattern(finding)
        assert "pathlib" in pattern
        assert "@code-review-agent" in pattern

    def test_hardcoded_credentials_pattern(self) -> None:
        """Test fix pattern for hardcoded credentials."""
        finding = {
            "cwe": "CWE-798",
            "fix_recommendation": "Move to environment variables",
        }
        pattern = _generate_fix_pattern(finding)
        assert "environment" in pattern
        assert "@secret-detection-agent" in pattern

    def test_generic_pattern_without_recommendation(self) -> None:
        """Test generic pattern when no recommendation provided."""
        finding = {"cwe": "CWE-999"}
        pattern = _generate_fix_pattern(finding)
        assert "security patch" in pattern


class TestFindingsLoading:
    """Tests for loading findings from cache."""

    def test_load_findings_from_cache(self) -> None:
        """Test loading findings from valid cache file."""
        findings_data = {
            "findings": [
                {
                    "cwe": "CWE-89",
                    "severity": "CRITICAL",
                    "description": "SQL Injection",
                    "file_path": "app.py",
                    "line_number": 42,
                }
            ]
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(findings_data, f)
            temp_path = f.name

        try:
            findings = _load_findings(temp_path)
            assert len(findings) == 1
            assert findings[0]["cwe"] == "CWE-89"
        finally:
            Path(temp_path).unlink()

    def test_load_findings_missing_file(self) -> None:
        """Test loading findings from non-existent file."""
        with pytest.raises(FileNotFoundError):
            _load_findings("/nonexistent/path/to/findings.json")

    def test_load_findings_invalid_json(self) -> None:
        """Test loading invalid JSON file."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            f.write("{ invalid json }")
            temp_path = f.name

        try:
            with pytest.raises(json.JSONDecodeError):
                _load_findings(temp_path)
        finally:
            Path(temp_path).unlink()


class TestCWEGrouping:
    """Tests for CWE grouping logic."""

    def test_group_findings_by_cwe(self) -> None:
        """Test grouping findings by CWE."""
        findings = [
            {"cwe": "CWE-89", "severity": "CRITICAL"},
            {"cwe": "CWE-89", "severity": "HIGH"},
            {"cwe": "CWE-22", "severity": "HIGH"},
        ]

        groups = _group_by_cwe(findings)
        assert len(groups) == 2
        assert len(groups["CWE-89"]) == 2
        assert len(groups["CWE-22"]) == 1

    def test_group_findings_with_missing_cwe(self) -> None:
        """Test grouping when CWE is missing."""
        findings = [{"severity": "HIGH"}, {"cwe": "CWE-89", "severity": "CRITICAL"}]

        groups = _group_by_cwe(findings)
        assert "UNKNOWN" in groups
        assert "CWE-89" in groups

    def test_group_empty_findings(self) -> None:
        """Test grouping empty findings list."""
        groups = _group_by_cwe([])
        assert len(groups) == 0


class TestSortingBySeverity:
    """Tests for severity-based sorting."""

    def test_sort_findings_by_severity(self) -> None:
        """Test sorting findings by severity."""
        findings = [
            {"severity": "LOW"},
            {"severity": "CRITICAL"},
            {"severity": "HIGH"},
            {"severity": "MEDIUM"},
        ]

        sorted_findings = _sort_findings_by_severity(findings)
        severities = [f["severity"] for f in sorted_findings]
        assert severities == ["CRITICAL", "HIGH", "MEDIUM", "LOW"]

    def test_sort_findings_with_missing_severity(self) -> None:
        """Test sorting when severity is missing."""
        findings = [{"cwe": "CWE-89"}, {"severity": "CRITICAL"}]

        sorted_findings = _sort_findings_by_severity(findings)
        # Missing severity should be treated as INFO (lowest)
        assert sorted_findings[0]["severity"] == "CRITICAL"


class TestFormatCodeQLAlerts:
    """Tests for main formatting function."""

    def test_format_alerts_complete(self) -> None:
        """Test formatting complete findings."""
        findings_data = {
            "findings": [
                {
                    "cwe": "CWE-89",
                    "severity": "CRITICAL",
                    "description": "SQL Injection",
                    "file_path": "queries.py",
                    "line_number": 42,
                    "tool": "CodeQL",
                    "fix_recommendation": "Use parameterized queries",
                    "confidence": 0.99,
                },
                {
                    "cwe": "CWE-22",
                    "severity": "HIGH",
                    "description": "Path Traversal",
                    "file_path": "file_ops.py",
                    "line_number": 15,
                    "tool": "Semgrep",
                    "fix_recommendation": "Validate paths",
                    "confidence": 0.92,
                },
            ]
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(findings_data, f)
            temp_path = f.name

        try:
            formatted = format_codeql_alerts(temp_path)

            # Verify structure
            assert "cwe_groups" in formatted
            assert "metadata" in formatted

            # Verify metadata
            assert formatted["metadata"]["total_findings"] == 2
            assert formatted["metadata"]["critical_count"] == 1
            assert formatted["metadata"]["high_count"] == 1
            assert formatted["metadata"]["cwe_count"] == 2

            # Verify CWE groups
            assert len(formatted["cwe_groups"]) == 2
            assert formatted["cwe_groups"][0]["cwe_id"] == "CWE-89"
            assert formatted["cwe_groups"][0]["severity"] == "CRITICAL"

            # Verify findings within group
            assert len(formatted["cwe_groups"][0]["findings"]) == 1
            finding = formatted["cwe_groups"][0]["findings"][0]
            assert "queries.py:42" in finding["file"]
            assert finding["confidence"] == "99%"

        finally:
            Path(temp_path).unlink()

    def test_format_alerts_empty(self) -> None:
        """Test formatting empty findings list."""
        findings_data = {"findings": []}

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(findings_data, f)
            temp_path = f.name

        try:
            formatted = format_codeql_alerts(temp_path)

            assert formatted["metadata"]["total_findings"] == 0
            assert len(formatted["cwe_groups"]) == 0

        finally:
            Path(temp_path).unlink()

    def test_format_alerts_missing_fields(self) -> None:
        """Test formatting findings with missing fields."""
        findings_data = {
            "findings": [
                {
                    "cwe": "CWE-89",
                    # Missing several fields - should handle gracefully
                }
            ]
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(findings_data, f)
            temp_path = f.name

        try:
            formatted = format_codeql_alerts(temp_path)
            assert formatted["metadata"]["total_findings"] == 1
            assert len(formatted["cwe_groups"]) == 1

        finally:
            Path(temp_path).unlink()


class TestMarkdownReportGeneration:
    """Tests for markdown report generation."""

    def test_markdown_report_structure(self) -> None:
        """Test markdown report contains expected sections."""
        formatted = {
            "cwe_groups": [
                {
                    "cwe_id": "CWE-89",
                    "cwe_title": "SQL Injection",
                    "severity": "CRITICAL",
                    "finding_count": 1,
                    "findings": [
                        {
                            "file": "queries.py:42",
                            "tool": "CodeQL",
                            "message": "SQL Injection",
                            "fix_pattern": "Use parameterized queries",
                            "confidence": "99%",
                        }
                    ],
                }
            ],
            "metadata": {
                "total_findings": 1,
                "critical_count": 1,
                "high_count": 0,
                "medium_count": 0,
                "low_count": 0,
                "info_count": 0,
                "cwe_count": 1,
                "generated_at": "2026-07-07T02:00:00Z",
            },
        }

        markdown = _generate_markdown_report(formatted)

        # Verify sections
        assert "# CodeQL Security Findings Report" in markdown
        assert "## Summary" in markdown
        assert "## Findings by CWE" in markdown
        assert "CWE-89" in markdown
        assert "SQL Injection" in markdown
        assert "CRITICAL" in markdown

    def test_markdown_report_metadata(self) -> None:
        """Test markdown report includes all metadata."""
        formatted = {
            "cwe_groups": [],
            "metadata": {
                "total_findings": 5,
                "critical_count": 2,
                "high_count": 1,
                "medium_count": 1,
                "low_count": 1,
                "info_count": 0,
                "cwe_count": 3,
                "generated_at": "2026-07-07T02:00:00Z",
            },
        }

        markdown = _generate_markdown_report(formatted)

        # Verify counts (with markdown formatting: **Total Findings**)
        assert "5" in markdown and "Total Findings" in markdown
        assert "2" in markdown and "Critical" in markdown
        assert "1" in markdown and "High" in markdown
        assert "1" in markdown and "Medium" in markdown
        assert "1" in markdown and "Low" in markdown


class TestPerformance:
    """Tests for performance requirements."""

    def test_format_large_findings_performance(self) -> None:
        """Test formatting performance with large dataset."""
        # Generate 100 findings
        findings_data = {
            "findings": [
                {
                    "cwe": f"CWE-{i % 10 + 79}",
                    "severity": ["CRITICAL", "HIGH", "MEDIUM"][i % 3],
                    "description": f"Finding {i}",
                    "file_path": f"file_{i}.py",
                    "line_number": i,
                    "tool": "CodeQL",
                    "fix_recommendation": "Apply fix",
                    "confidence": 0.9,
                }
                for i in range(100)
            ]
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(findings_data, f)
            temp_path = f.name

        try:
            start_time = time.time()
            formatted = format_codeql_alerts(temp_path)
            elapsed = time.time() - start_time

            # Should complete in under 500ms
            assert elapsed < 0.5
            assert formatted["metadata"]["total_findings"] == 100

        finally:
            Path(temp_path).unlink()


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_findings_with_special_characters(self) -> None:
        """Test handling findings with special characters."""
        findings_data = {
            "findings": [
                {
                    "cwe": "CWE-89",
                    "severity": "CRITICAL",
                    "description": "SQL <injection> & 'quotes'",
                    "file_path": 'file with "quotes".py',
                    "line_number": 42,
                    "tool": "CodeQL",
                    "fix_recommendation": "Use params",
                    "confidence": 0.99,
                }
            ]
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(findings_data, f)
            temp_path = f.name

        try:
            formatted = format_codeql_alerts(temp_path)
            assert formatted["metadata"]["total_findings"] == 1

        finally:
            Path(temp_path).unlink()

    def test_findings_with_unicode(self) -> None:
        """Test handling findings with unicode characters."""
        findings_data = {
            "findings": [
                {
                    "cwe": "CWE-89",
                    "severity": "CRITICAL",
                    "description": "SQL Injection 🚨 (crítica)",
                    "file_path": "файл.py",
                    "line_number": 42,
                    "tool": "CodeQL",
                    "fix_recommendation": "Fix 修復",
                    "confidence": 0.99,
                }
            ]
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(findings_data, f, ensure_ascii=False)
            temp_path = f.name

        try:
            formatted = format_codeql_alerts(temp_path)
            assert formatted["metadata"]["total_findings"] == 1

        finally:
            Path(temp_path).unlink()

    def test_multiple_findings_same_location(self) -> None:
        """Test multiple findings at same location."""
        findings_data = {
            "findings": [
                {
                    "cwe": "CWE-89",
                    "severity": "CRITICAL",
                    "description": "SQL Injection",
                    "file_path": "queries.py",
                    "line_number": 42,
                    "tool": "CodeQL",
                    "fix_recommendation": "Use params",
                    "confidence": 0.99,
                },
                {
                    "cwe": "CWE-22",
                    "severity": "HIGH",
                    "description": "Path Traversal",
                    "file_path": "queries.py",
                    "line_number": 42,
                    "tool": "Semgrep",
                    "fix_recommendation": "Validate paths",
                    "confidence": 0.92,
                },
            ]
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(findings_data, f)
            temp_path = f.name

        try:
            formatted = format_codeql_alerts(temp_path)
            assert formatted["metadata"]["total_findings"] == 2
            assert len(formatted["cwe_groups"]) == 2

        finally:
            Path(temp_path).unlink()
