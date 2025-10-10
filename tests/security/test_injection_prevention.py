"""Security tests for injection attack prevention.

Validates input sanitization against common attack vectors per
AGENTS.md security policy.
"""
from __future__ import annotations

import pytest

from src.security import SecurityError, validate_input


class TestSQLInjectionPrevention:
    """Test SQL injection detection and blocking."""

    def test_sql_injection_drop_table_blocked(self) -> None:
        """Block DROP TABLE injection attempts."""
        malicious = "'; DROP TABLE users; --"
        with pytest.raises(SecurityError, match="SQL injection"):
            validate_input(malicious, input_type="sql")

    def test_sql_injection_or_bypass_blocked(self) -> None:
        """Block OR-based authentication bypass."""
        malicious = "admin' OR '1'='1"
        with pytest.raises(SecurityError, match="SQL injection"):
            validate_input(malicious, input_type="sql")

    def test_sql_safe_input_passes(self) -> None:
        """Allow legitimate SQL-safe input."""
        safe = "user_name_123"
        result = validate_input(safe, input_type="sql")
        assert result == safe

    def test_sql_comment_injection_blocked(self) -> None:
        """Block comment-based SQL injection."""
        malicious = "test -- ignore rest"
        with pytest.raises(SecurityError, match="SQL injection"):
            validate_input(malicious, input_type="sql")


class TestXSSPrevention:
    """Test cross-site scripting (XSS) prevention."""

    def test_xss_script_tag_blocked(self) -> None:
        """Block script tag injection."""
        malicious = "<script>alert('xss')</script>"
        with pytest.raises(SecurityError, match="XSS pattern"):
            validate_input(malicious, input_type="html")

    def test_xss_javascript_protocol_blocked(self) -> None:
        """Block javascript: protocol injection."""
        malicious = "<a href='javascript:alert(1)'>click</a>"
        with pytest.raises(SecurityError, match="XSS pattern"):
            validate_input(malicious, input_type="html")

    def test_xss_event_handler_blocked(self) -> None:
        """Block event handler injection."""
        malicious = "<img src=x onerror='alert(1)'>"
        with pytest.raises(SecurityError, match="XSS pattern"):
            validate_input(malicious, input_type="html")

    def test_safe_html_passes(self) -> None:
        """Allow safe HTML content."""
        safe = "Hello <b>world</b>"
        result = validate_input(safe, input_type="html")
        assert result == safe


class TestPathTraversalPrevention:
    """Test path traversal attack prevention."""

    def test_path_traversal_parent_blocked(self) -> None:
        """Block parent directory traversal."""
        malicious = "../../../etc/passwd"
        with pytest.raises(SecurityError, match="Path traversal"):
            validate_input(malicious, input_type="path")

    def test_path_traversal_absolute_blocked(self) -> None:
        """Block absolute path injection."""
        malicious = "/etc/shadow"
        with pytest.raises(SecurityError, match="Path traversal"):
            validate_input(malicious, input_type="path")

    def test_path_null_byte_blocked(self) -> None:
        """Block null byte injection."""
        malicious = "file.txt\0.jpg"
        with pytest.raises(SecurityError, match="Invalid characters"):
            validate_input(malicious, input_type="path")

    def test_safe_relative_path_passes(self) -> None:
        """Allow safe relative paths."""
        safe = "data/models/checkpoint.pt"
        result = validate_input(safe, input_type="path")
        assert result == safe


class TestInputSanitization:
    """Test general input sanitization."""

    def test_max_length_enforced(self) -> None:
        """Enforce maximum input length."""
        long_input = "a" * 10_001
        with pytest.raises(SecurityError, match="exceeds max length"):
            validate_input(long_input, max_length=10_000)

    def test_non_string_rejected(self) -> None:
        """Reject non-string input."""
        with pytest.raises(SecurityError, match="Expected string"):
            validate_input(123, input_type="text")  # type: ignore[arg-type]

    def test_control_characters_blocked(self) -> None:
        """Block dangerous control characters."""
        malicious = "test\0null"
        with pytest.raises(SecurityError, match="Invalid control characters"):
            validate_input(malicious, input_type="text")
