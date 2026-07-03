"""
Tests for workflow error pattern analyzer.

Tests cover:
- Error pattern detection for all categories
- Severity and category classification
- Recurring pattern detection
- Recommendation generation
- Report output formats
"""

import pytest

from scripts.ci.analyze_workflow_errors import (
    ERROR_PATTERNS,
    AnalysisResult,
    analyze_log_content,
    find_recurring_patterns,
)


class TestErrorPatternDetection:
    """Tests for individual error pattern detection."""

    def test_detect_import_error_module_not_found(self):
        """Test detection of ModuleNotFoundError."""
        log = "ModuleNotFoundError: No module named 'json'"
        result = analyze_log_content(log)

        assert result.total_errors > 0, "total_errors must be greater than zero"
        assert "import_error" in result.errors_by_type, "Result must not be empty"
        assert result.errors_by_type["import_error"][0].severity == "high", "Result must not be empty"

    def test_detect_import_error_name_error(self):
        """Test detection of NameError (undefined name)."""
        log = "NameError: name 'json' is not defined"
        result = analyze_log_content(log)

        assert "import_error" in result.errors_by_type, "Result must not be empty"
        assert "json" in result.errors_by_type["import_error"][0].match, "Result must not be empty"

    def test_detect_syntax_error(self):
        """Test detection of SyntaxError."""
        log = "SyntaxError: invalid syntax"
        result = analyze_log_content(log)

        assert "syntax_error" in result.errors_by_type, "Result must not be empty"
        assert result.errors_by_severity["high"] > 0, "Value must be greater than zero"

    def test_detect_yaml_syntax_error(self):
        """Test detection of YAML ScannerError."""
        log = "yaml.scanner.ScannerError: mapping values are not allowed here"
        result = analyze_log_content(log)

        assert "syntax_error" in result.errors_by_type, "Result must not be empty"

    def test_detect_test_failure(self):
        """Test detection of pytest FAILED."""
        log = "FAILED tests/test_example.py::test_function"
        result = analyze_log_content(log)

        assert "test_failure" in result.errors_by_type, "Result must not be empty"
        assert result.errors_by_category["testing"] > 0, "Value must be greater than zero"

    def test_detect_assertion_error(self):
        """Test detection of AssertionError."""
        log = "E   AssertionError: assert 1 == 2"
        result = analyze_log_content(log)

        assert "test_failure" in result.errors_by_type, "Result must not be empty"

    def test_detect_timeout_error(self):
        """Test detection of timeout."""
        log = "TimeoutError: Operation timed out after 30 seconds"
        result = analyze_log_content(log)

        assert "timeout_error" in result.errors_by_type, "Result must not be empty"
        assert result.errors_by_category["performance"] > 0, "Value must be greater than zero"

    def test_detect_permission_error(self):
        """Test detection of permission denied."""
        log = "PermissionError: [Errno 13] Permission denied: '/etc/passwd'"
        result = analyze_log_content(log)

        assert "permission_error" in result.errors_by_type, "Result must not be empty"
        assert result.errors_by_severity["high"] > 0, "Value must be greater than zero"

    def test_detect_github_permission_error(self):
        """Test detection of GitHub integration permission error."""
        log = "Resource not accessible by integration"
        result = analyze_log_content(log)

        assert "permission_error" in result.errors_by_type, "Result must not be empty"

    def test_detect_dependency_conflict(self):
        """Test detection of pip resolver conflict."""
        log = "pip resolver found incompatible requirements"
        result = analyze_log_content(log)

        assert "dependency_conflict" in result.errors_by_type, "Result must not be empty"
        assert result.errors_by_category["dependency"] > 0, "Value must be greater than zero"

    def test_detect_type_error(self):
        """Test detection of TypeError."""
        log = "TypeError: 'NoneType' object is not subscriptable"
        result = analyze_log_content(log)

        assert "type_error" in result.errors_by_type, "Result must not be empty"

    def test_detect_file_not_found(self):
        """Test detection of FileNotFoundError."""
        log = "FileNotFoundError: [Errno 2] No such file or directory: 'config.yaml'"
        result = analyze_log_content(log)

        assert "file_not_found" in result.errors_by_type, "Result must not be empty"

    def test_detect_network_error(self):
        """Test detection of ConnectionError."""
        log = "ConnectionError: HTTPConnectionPool(host='api.example.com', port=80)"
        result = analyze_log_content(log)

        assert "network_error" in result.errors_by_type, "Result must not be empty"
        assert result.errors_by_severity["low"] > 0, "Value must be greater than zero"

    def test_detect_memory_error(self):
        """Test detection of MemoryError."""
        log = "MemoryError"
        result = analyze_log_content(log)

        assert "memory_error" in result.errors_by_type, "Result must not be empty"
        assert result.errors_by_severity["high"] > 0, "Value must be greater than zero"


class TestMultipleErrorDetection:
    """Tests for detecting multiple errors in single log."""

    def test_detect_multiple_error_types(self):
        """Test detecting different error types in one log."""
        log = """
        ModuleNotFoundError: No module named 'pandas'
        SyntaxError: invalid syntax
        FAILED tests/test_foo.py::test_bar
        """
        result = analyze_log_content(log)

        assert result.total_errors >= 3, "total_errors must be greater than zero"
        assert "import_error" in result.errors_by_type, "Result must not be empty"
        assert "syntax_error" in result.errors_by_type, "Result must not be empty"
        assert "test_failure" in result.errors_by_type, "Result must not be empty"

    def test_detect_multiple_same_type(self):
        """Test detecting multiple errors of same type."""
        log = """
        ModuleNotFoundError: No module named 'json'
        ModuleNotFoundError: No module named 'yaml'
        ModuleNotFoundError: No module named 'toml'
        """
        result = analyze_log_content(log)

        assert len(result.errors_by_type["import_error"]) == 3, "Collection must not be empty"

    def test_error_line_numbers(self):
        """Test that line numbers are captured correctly."""
        log = "Line 1\nLine 2\nSyntaxError: invalid syntax\nLine 4"
        result = analyze_log_content(log)

        assert result.errors_by_type["syntax_error"][0].line_number == 3, "Result must not be empty"


class TestSeverityClassification:
    """Tests for severity classification."""

    def test_high_severity_errors(self):
        """Test that high severity errors are classified correctly."""
        high_severity_logs = [
            "ModuleNotFoundError: No module named 'critical'",
            "SyntaxError: unexpected EOF",
            "PermissionError: access denied",
            "MemoryError",
        ]

        for log in high_severity_logs:
            result = analyze_log_content(log)
            assert result.errors_by_severity["high"] > 0, f"Expected high severity for: {log}"

    def test_medium_severity_errors(self):
        """Test that medium severity errors are classified correctly."""
        medium_severity_logs = [
            "FAILED tests/test_example.py::test_func",
            "TypeError: unexpected argument",
            "FileNotFoundError: config.yaml not found",
        ]

        for log in medium_severity_logs:
            result = analyze_log_content(log)
            assert result.errors_by_severity["medium"] > 0, f"Expected medium severity for: {log}"

    def test_low_severity_errors(self):
        """Test that low severity errors are classified correctly."""
        log = "ConnectionError: failed to connect to api.example.com"
        result = analyze_log_content(log)

        assert result.errors_by_severity["low"] > 0, "Value must be greater than zero"


class TestCategoryClassification:
    """Tests for category classification."""

    def test_dependency_category(self):
        """Test dependency category."""
        log = "pip resolver found incompatible requirements"
        result = analyze_log_content(log)

        assert "dependency" in result.errors_by_category, "Result must not be empty"

    def test_code_quality_category(self):
        """Test code quality category."""
        log = "SyntaxError: invalid syntax"
        result = analyze_log_content(log)

        assert "code_quality" in result.errors_by_category, "Result must not be empty"

    def test_testing_category(self):
        """Test testing category."""
        log = "FAILED tests/test_api.py::test_endpoint"
        result = analyze_log_content(log)

        assert "testing" in result.errors_by_category, "Result must not be empty"

    def test_performance_category(self):
        """Test performance category."""
        log = "TimeoutError: operation timed out"
        result = analyze_log_content(log)

        assert "performance" in result.errors_by_category, "Result must not be empty"

    def test_security_category(self):
        """Test security category."""
        log = "403 Forbidden"
        result = analyze_log_content(log)

        assert "security" in result.errors_by_category, "Result must not be empty"


class TestRecurringPatterns:
    """Tests for recurring pattern detection."""

    def test_find_recurring_same_error(self):
        """Test finding recurring identical errors."""
        logs = [
            "ModuleNotFoundError: No module named 'json'",
            "ModuleNotFoundError: No module named 'json'",
            "ModuleNotFoundError: No module named 'json'",
        ]

        recurring = find_recurring_patterns(logs)

        assert len(recurring) > 0, "Recurring must not be empty"
        assert recurring[0]["occurrences"] >= 2, "Value must be greater than zero"

    def test_find_recurring_different_errors(self):
        """Test that different errors are not merged."""
        logs = [
            "ModuleNotFoundError: No module named 'json'",
            "ModuleNotFoundError: No module named 'yaml'",
            "ModuleNotFoundError: No module named 'toml'",
        ]

        recurring = find_recurring_patterns(logs)

        # Each error is unique, so no recurring patterns
        assert len(recurring) == 0, "Recurring must not be empty"

    def test_recurring_threshold(self):
        """Test that single occurrences are not reported."""
        logs = [
            "ModuleNotFoundError: No module named 'unique_module'",
        ]

        recurring = find_recurring_patterns(logs)

        assert len(recurring) == 0, "Recurring must not be empty"

    def test_recurring_sorted_by_count(self):
        """Test that recurring patterns are sorted by occurrence count."""
        logs = [
            "SyntaxError: a",
            "SyntaxError: a",
            "ModuleNotFoundError: No module named 'x'",
            "ModuleNotFoundError: No module named 'x'",
            "ModuleNotFoundError: No module named 'x'",
        ]

        recurring = find_recurring_patterns(logs)

        # Should be sorted with most frequent first
        if len(recurring) >= 2:
            assert recurring[0]["occurrences"] >= recurring[1]["occurrences"], "Value must be greater than zero"


class TestRecommendations:
    """Tests for recommendation generation."""

    def test_high_severity_recommendation(self):
        """Test that high severity triggers priority recommendation."""
        log = "ModuleNotFoundError: No module named 'critical'"
        result = analyze_log_content(log)

        high_priority_recs = [r for r in result.recommendations if "HIGH PRIORITY" in r]
        assert len(high_priority_recs) > 0, "High_priority_recs must not be empty"

    def test_dependency_recommendation(self):
        """Test dependency-specific recommendation."""
        log = "pip resolver found incompatible requirements"
        result = analyze_log_content(log)

        dep_recs = [r for r in result.recommendations if "Dependency" in r or "pip" in r]
        assert len(dep_recs) > 0, "Dep_recs must not be empty"

    def test_code_quality_recommendation(self):
        """Test code quality recommendation."""
        log = "SyntaxError: invalid syntax"
        result = analyze_log_content(log)

        quality_recs = [
            r for r in result.recommendations if "ruff" in r.lower() or "quality" in r.lower()
        ]
        assert len(quality_recs) > 0, "Quality_recs must not be empty"

    def test_most_common_recommendation(self):
        """Test recommendation for most common error type."""
        log = """
        ModuleNotFoundError: No module named 'a'
        ModuleNotFoundError: No module named 'b'
        ModuleNotFoundError: No module named 'c'
        SyntaxError: x
        """
        result = analyze_log_content(log)

        common_recs = [r for r in result.recommendations if "Most common" in r]
        assert len(common_recs) > 0, "Common_recs must not be empty"


class TestAnalysisResult:
    """Tests for AnalysisResult dataclass."""

    def test_to_dict(self):
        """Test conversion to dictionary."""
        result = AnalysisResult(
            total_errors=5,
            errors_by_severity={"high": 2, "medium": 2, "low": 1},
            errors_by_category={"dependency": 3, "testing": 2},
            recommendations=["Fix dependencies"],
        )

        d = result.to_dict()

        assert d["total_errors"] == 5, "Error should be raised or set"
        assert d["errors_by_severity"]["high"] == 2, "Error should be raised or set"
        assert "Fix dependencies" in d["recommendations"], "Condition must be true"

    def test_analyzed_at_timestamp(self):
        """Test that analyzed_at is set automatically."""
        result = AnalysisResult()

        assert result.analyzed_at is not None, "analyzed_at must be set on construction"
        # Should be ISO format containing 'T' separator
        assert "T" in result.analyzed_at, "analyzed_at must be ISO 8601 (contains 'T')"
        # Must also contain a date component: 4-digit year
        import re
        assert re.search(r"\d{4}-\d{2}-\d{2}", result.analyzed_at), (
            "analyzed_at must include a YYYY-MM-DD date component"
        )


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_log(self):
        """Test analyzing empty log."""
        result = analyze_log_content("")

        assert result.total_errors == 0, "Result must not be empty"
        assert len(result.errors_by_type) == 0, "Collection must not be empty"

    def test_no_errors_log(self):
        """Test log with no errors."""
        log = "Everything is fine\nTests passed\nBuild successful"
        result = analyze_log_content(log)

        assert result.total_errors == 0, "Result must not be empty"

    def test_unicode_in_log(self):
        """Test handling of unicode characters."""
        log = "SyntaxError: unexpected character '→' in expression"
        result = analyze_log_content(log)

        assert "syntax_error" in result.errors_by_type, "Result must not be empty"

    def test_very_long_line(self):
        """Test handling of very long lines."""
        log = "ModuleNotFoundError: No module named '" + "x" * 1000 + "'"
        result = analyze_log_content(log)

        assert "import_error" in result.errors_by_type, "Result must not be empty"
        # Context should be truncated
        assert len(result.errors_by_type["import_error"][0].context) <= 200, "Collection must not be empty"


class TestErrorPatternConfiguration:
    """Tests for error pattern configuration."""

    def test_all_patterns_have_required_fields(self):
        """Test that all patterns have required configuration."""
        required_fields = ["patterns", "severity", "category", "remediation"]

        for error_type, config in ERROR_PATTERNS.items():
            for field in required_fields:
                assert field in config, f"Missing {field} in {error_type}"

    def test_valid_severity_values(self):
        """Test that all severities are valid."""
        valid_severities = {"high", "medium", "low"}

        for error_type, config in ERROR_PATTERNS.items():
            assert config["severity"] in valid_severities, f"Invalid severity in {error_type}"

    def test_patterns_are_valid_regex(self):
        """Test that all patterns are valid regex."""
        import re

        for error_type, config in ERROR_PATTERNS.items():
            for pattern in config["patterns"]:
                try:
                    re.compile(pattern)
                except re.error as e:
                    pytest.fail(f"Invalid regex in {error_type}: {pattern} - {e}")
