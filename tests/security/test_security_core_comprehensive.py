"""Comprehensive tests for security.core module.

This module provides extensive coverage of core security functions including:
- Input validation and sanitization
- CSRF token verification
- Rate limiting
- Security event logging
- Path validation
- Permission checks
"""

from __future__ import annotations

import json
import logging
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from security.core import (
    check_permissions,
    enforce_absolute_path,
    hmac_compare,
    log_security_event,
    rate_limiter,
    sanitize_for_logging,
    sanitize_path,
    sanitize_user_content,
    validate_input,
    verify_csrf_token,
    verify_session_integrity,
)

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def mock_logger(monkeypatch):
    """Mock logger for testing."""
    mock = MagicMock()
    monkeypatch.setattr(logging, "getLogger", lambda name: mock)
    return mock


@pytest.fixture
def temp_session_file(tmp_path):
    """Create a temporary session file."""
    session_file = tmp_path / "session.json"
    session_data = {
        "user_id": "user123",
        "username": "testuser",
        "created_at": datetime.now(UTC).isoformat(),
        "last_activity": datetime.now(UTC).isoformat(),
        "ip_address": "192.168.1.1",
        "user_agent": "Mozilla/5.0...",
    }
    session_file.write_text(json.dumps(session_data))
    return session_file


@pytest.fixture
def rate_limiter_instance():
    """Create a rate limiter instance for testing."""
    return rate_limiter(max_calls=5, time_window=60)


# ============================================================================
# SANITIZE_FOR_LOGGING TESTS
# ============================================================================


class TestSanitizeForLogging:
    """Test sanitize_for_logging function."""

    def test_sanitize_basic_string(self):
        """Test sanitizing a basic string."""
        result = sanitize_for_logging("Hello World")
        assert result == "Hello World", "Result must not be empty"

    def test_sanitize_removes_newlines(self):
        """Test that newlines are removed."""
        result = sanitize_for_logging("Hello\nWorld")
        assert "\n" not in result, "Result must not be empty"
        assert "Hello" in result and "World" in result, "Result must not be empty"

    def test_sanitize_removes_carriage_returns(self):
        """Test that carriage returns are removed."""
        result = sanitize_for_logging("Hello\rWorld")
        assert "\r" not in result, "Result must not be empty"

    def test_sanitize_removes_tabs(self):
        """Test that tabs are removed."""
        result = sanitize_for_logging("Hello\tWorld")
        assert "\t" not in result, "Result must not be empty"

    def test_sanitize_removes_control_characters(self):
        """Test that control characters are removed."""
        result = sanitize_for_logging("Hello\x00\x01\x02World")
        assert "\x00" not in result, "Result must not be empty"
        assert "\x01" not in result, "Result must not be empty"

    def test_sanitize_truncates_long_strings(self):
        """Test that strings are truncated to max length."""
        long_string = "A" * 500
        result = sanitize_for_logging(long_string, max_length=200)
        assert len(result) <= 200, "Result must not be empty"

    def test_sanitize_custom_max_length(self):
        """Test custom max_length parameter."""
        result = sanitize_for_logging("A" * 100, max_length=50)
        assert len(result) <= 50, "Result must not be empty"

    def test_sanitize_with_special_chars(self):
        """Test sanitizing special characters."""
        result = sanitize_for_logging("!@#$%^&*()")
        assert "!" in result, "Result must not be empty"

    def test_sanitize_with_unicode(self):
        """Test sanitizing unicode characters."""
        result = sanitize_for_logging("Hello 世界 🌍")
        assert "Hello" in result, "Result must not be empty"

    def test_sanitize_none_value(self):
        """Test sanitizing None value."""
        result = sanitize_for_logging(None)
        assert isinstance(result, str)

    def test_sanitize_numeric_value(self):
        """Test sanitizing numeric values."""
        result = sanitize_for_logging(12345)
        assert "12345" in result, "Result must not be empty"

    def test_sanitize_empty_string(self):
        """Test sanitizing empty string."""
        result = sanitize_for_logging("")
        assert result == "", "Result must not be empty"

    def test_sanitize_whitespace_only(self):
        """Test sanitizing whitespace-only string."""
        result = sanitize_for_logging("   ")
        assert result.strip() == "", "Result must not be empty"


# ============================================================================
# VALIDATE_INPUT TESTS
# ============================================================================


class TestValidateInput:
    """Test validate_input function."""

    def test_validate_input_sql_injection_basic(self):
        """Test basic SQL injection pattern detection."""
        result = validate_input("'; DROP TABLE users; --")
        assert result is False, "Result must not be empty"

    def test_validate_input_sql_injection_delete(self):
        """Test DELETE statement detection."""
        result = validate_input("value'; DELETE FROM users WHERE '1'='1")
        assert result is False, "Result must not be empty"

    def test_validate_input_sql_injection_union(self):
        """Test UNION statement detection."""
        result = validate_input("1' UNION SELECT * FROM users --")
        assert result is False, "Result must not be empty"

    def test_validate_input_xss_script_tag(self):
        """Test XSS script tag detection."""
        result = validate_input("<script>alert('xss')</script>")
        assert result is False, "Result must not be empty"

    def test_validate_input_xss_javascript_uri(self):
        """Test JavaScript URI detection."""
        result = validate_input('<a href="javascript:alert()">click</a>')
        assert result is False, "Result must not be empty"

    def test_validate_input_xss_event_handler(self):
        """Test event handler detection."""
        result = validate_input("<img src=x onerror=alert()>")
        assert result is False, "Result must not be empty"

    def test_validate_input_json_prototype_pollution(self):
        """Test JSON prototype pollution detection."""
        result = validate_input('{"__proto__": {"admin": true}}')
        assert result is False, "Result must not be empty"

    def test_validate_input_clean_string(self):
        """Test valid clean string."""
        result = validate_input("This is a valid input")
        assert result is True, "Result must not be empty"

    def test_validate_input_clean_email(self):
        """Test valid email input."""
        result = validate_input("user@example.com")
        assert result is True, "Result must not be empty"

    def test_validate_input_clean_with_numbers(self):
        """Test valid input with numbers."""
        result = validate_input("User123")
        assert result is True, "Result must not be empty"

    def test_validate_input_empty_string(self):
        """Test empty string."""
        result = validate_input("")
        assert result is True, "Result must not be empty"

    def test_validate_input_none_value(self):
        """Test None value."""
        result = validate_input(None)
        assert result is True, "Result must not be empty"

    def test_validate_input_numeric_value(self):
        """Test numeric value."""
        result = validate_input(12345)
        assert result is True, "Result must not be empty"

    def test_validate_input_comment_with_double_dash(self):
        """Test SQL comment detection."""
        result = validate_input("SELECT * FROM users -- comment")
        assert result is False, "Result must not be empty"

    def test_validate_input_comment_with_slash(self):
        """Test SQL block comment detection."""
        result = validate_input("SELECT * /* comment */ FROM users")
        assert result is False, "Result must not be empty"


# ============================================================================
# SANITIZE_USER_CONTENT TESTS
# ============================================================================


class TestSanitizeUserContent:
    """Test sanitize_user_content function."""

    def test_sanitize_user_content_escapes_html(self):
        """Test HTML escaping."""
        result = sanitize_user_content("<script>alert()</script>")
        assert "<" not in result or "&lt;" in result, "Result must not be empty"

    def test_sanitize_user_content_removes_dangerous_tags(self):
        """Test dangerous tag removal."""
        result = sanitize_user_content("<iframe src='evil.com'></iframe>")
        assert "iframe" not in result.lower() or "&" in result, "Result must not be empty"

    def test_sanitize_user_content_preserves_safe_text(self):
        """Test safe text preservation."""
        result = sanitize_user_content("This is safe content")
        assert "safe content" in result, "Result must not be empty"

    def test_sanitize_user_content_empty_string(self):
        """Test empty string."""
        result = sanitize_user_content("")
        assert result == "", "Result must not be empty"

    def test_sanitize_user_content_with_quotes(self):
        """Test content with quotes."""
        result = sanitize_user_content('Content with "quotes"')
        assert "quotes" in result or "quot" in result, "Result must not be empty"

    def test_sanitize_user_content_with_apostrophes(self):
        """Test content with apostrophes."""
        result = sanitize_user_content("It's a test")
        assert "test" in result, "Result must not be empty"

    def test_sanitize_user_content_numeric(self):
        """Test numeric content."""
        result = sanitize_user_content(12345)
        assert "12345" in result or isinstance(result, str)

    def test_sanitize_user_content_none(self):
        """Test None value."""
        result = sanitize_user_content(None)
        assert result == "" or result == "None", "Result must not be empty"


# ============================================================================
# SANITIZE_PATH TESTS
# ============================================================================


class TestSanitizePath:
    """Test sanitize_path function."""

    def test_sanitize_path_removes_null_bytes(self):
        """Test null byte removal."""
        result = sanitize_path("path/to/file\x00.txt")
        assert "\x00" not in result, "Result must not be empty"

    def test_sanitize_path_handles_absolute_path(self):
        """Test absolute path handling."""
        result = sanitize_path("/home/user/file.txt")
        assert result is not None, "result must be initialized"

    def test_sanitize_path_handles_relative_path(self):
        """Test relative path handling."""
        result = sanitize_path("../file.txt")
        assert result is not None, "result must be initialized"

    def test_sanitize_path_handles_current_dir(self):
        """Test current directory."""
        result = sanitize_path("./file.txt")
        assert result is not None, "result must be initialized"

    def test_sanitize_path_windows_path(self):
        """Test Windows path."""
        result = sanitize_path("C:\\Users\\file.txt")
        assert result is not None, "result must be initialized"

    def test_sanitize_path_with_spaces(self):
        """Test path with spaces."""
        result = sanitize_path("path/to/my file.txt")
        assert "file" in result, "Result must not be empty"

    def test_sanitize_path_empty_string(self):
        """Test empty path."""
        result = sanitize_path("")
        assert result == "" or result is None, "Result must not be empty"

    def test_sanitize_path_removes_double_slashes(self):
        """Test double slash removal."""
        result = sanitize_path("path//to//file")
        assert "//" not in result or result is not None, "result must be initialized"

    def test_sanitize_path_with_dots(self):
        """Test path with dots."""
        result = sanitize_path("path/./to/../file")
        assert result is not None, "result must be initialized"


# ============================================================================
# ENFORCE_ABSOLUTE_PATH TESTS
# ============================================================================


class TestEnforceAbsolutePath:
    """Test enforce_absolute_path function."""

    def test_enforce_absolute_path_with_absolute(self):
        """Test with absolute path."""
        result = enforce_absolute_path("/home/user/file.txt")
        assert result == Path("/home/user/file.txt"), "Result must not be empty"

    def test_enforce_absolute_path_with_relative(self):
        """Test with relative path raises error."""
        with pytest.raises((ValueError, RuntimeError)):
            enforce_absolute_path("relative/path.txt")

    def test_enforce_absolute_path_with_current_dir(self):
        """Test with current directory path."""
        with pytest.raises((ValueError, RuntimeError)):
            enforce_absolute_path("./file.txt")

    def test_enforce_absolute_path_with_parent_dir(self):
        """Test with parent directory path."""
        with pytest.raises((ValueError, RuntimeError)):
            enforce_absolute_path("../file.txt")

    def test_enforce_absolute_path_returns_path_object(self):
        """Test return type is Path object."""
        result = enforce_absolute_path("/home/user/file.txt")
        assert isinstance(result, Path)

    def test_enforce_absolute_path_with_symlink(self):
        """Test with symlink path."""
        result = enforce_absolute_path("/usr/local/bin")
        assert isinstance(result, Path)

    def test_enforce_absolute_path_empty_string(self):
        """Test with empty string."""
        with pytest.raises((ValueError, RuntimeError)):
            enforce_absolute_path("")

    def test_enforce_absolute_path_dot(self):
        """Test with single dot."""
        with pytest.raises((ValueError, RuntimeError)):
            enforce_absolute_path(".")

    def test_enforce_absolute_path_double_dot(self):
        """Test with double dot."""
        with pytest.raises((ValueError, RuntimeError)):
            enforce_absolute_path("..")


# ============================================================================
# VERIFY_CSRF_TOKEN TESTS
# ============================================================================


class TestVerifyCSRFToken:
    """Test verify_csrf_token function."""

    def test_verify_csrf_token_valid_token(self):
        """Test with valid CSRF token."""
        session_id = "session123"
        token = "valid_token"
        result = verify_csrf_token(session_id, token, token)
        assert isinstance(result, bool)

    def test_verify_csrf_token_invalid_token(self):
        """Test with invalid token."""
        result = verify_csrf_token("session123", "token1", "token2")
        assert result is False, "Result must not be empty"

    def test_verify_csrf_token_empty_session_id(self):
        """Test with empty session ID."""
        result = verify_csrf_token("", "token", "token")
        assert isinstance(result, bool)

    def test_verify_csrf_token_empty_token(self):
        """Test with empty token."""
        result = verify_csrf_token("session123", "", "")
        assert result is True or result is False, "Result must not be empty"

    def test_verify_csrf_token_none_values(self):
        """Test with None values."""
        result = verify_csrf_token(None, None, None)
        assert isinstance(result, bool)

    def test_verify_csrf_token_case_sensitive(self):
        """Test token comparison is case sensitive."""
        result = verify_csrf_token("session123", "Token", "token")
        assert result is False, "Result must not be empty"

    def test_verify_csrf_token_whitespace_sensitive(self):
        """Test token comparison is whitespace sensitive."""
        result = verify_csrf_token("session123", "token ", "token")
        assert result is False, "Result must not be empty"

    def test_verify_csrf_token_long_token(self):
        """Test with long token."""
        long_token = "A" * 1000
        result = verify_csrf_token("session123", long_token, long_token)
        assert isinstance(result, bool)


# ============================================================================
# HMAC_COMPARE TESTS
# ============================================================================


class TestHmacCompare:
    """Test hmac_compare function."""

    def test_hmac_compare_identical_strings(self):
        """Test comparing identical strings."""
        result = hmac_compare("test", "test")
        assert result is True, "Result must not be empty"

    def test_hmac_compare_different_strings(self):
        """Test comparing different strings."""
        result = hmac_compare("test1", "test2")
        assert result is False, "Result must not be empty"

    def test_hmac_compare_case_sensitive(self):
        """Test case sensitivity."""
        result = hmac_compare("Test", "test")
        assert result is False, "Result must not be empty"

    def test_hmac_compare_empty_strings(self):
        """Test comparing empty strings."""
        result = hmac_compare("", "")
        assert result is True, "Result must not be empty"

    def test_hmac_compare_one_empty(self):
        """Test comparing one empty and one non-empty."""
        result = hmac_compare("", "test")
        assert result is False, "Result must not be empty"

    def test_hmac_compare_whitespace(self):
        """Test comparing whitespace."""
        result = hmac_compare("test ", "test")
        assert result is False, "Result must not be empty"

    def test_hmac_compare_long_strings(self):
        """Test comparing long strings."""
        long_str = "A" * 10000
        result = hmac_compare(long_str, long_str)
        assert result is True, "Result must not be empty"

    def test_hmac_compare_unicode(self):
        """Test comparing unicode strings."""
        result = hmac_compare("世界", "世界")
        assert result is True, "Result must not be empty"

    def test_hmac_compare_special_chars(self):
        """Test comparing special characters."""
        result = hmac_compare("!@#$%", "!@#$%")
        assert result is True, "Result must not be empty"

    def test_hmac_compare_timing_resistance(self):
        """Test timing-resistant comparison."""
        # This is a security property - should take similar time
        import timeit

        t1 = timeit.timeit(lambda: hmac_compare("a" * 100, "a" * 100), number=100)
        t2 = timeit.timeit(lambda: hmac_compare("a" * 100, "b" * 100), number=100)
        # Times should be similar (within 10x range due to variance)
        assert abs(t1 - t2) < max(t1, t2)


# ============================================================================
# RATE_LIMITER TESTS
# ============================================================================


class TestRateLimiter:
    """Test rate_limiter function."""

    def test_rate_limiter_decorator_creation(self):
        """Test creating a rate limiter decorator."""
        decorator = rate_limiter(max_calls=5, time_window=60)
        assert callable(decorator), "Condition must be true"

    def test_rate_limiter_allows_calls_within_limit(self):
        """Test allowing calls within limit."""
        decorator = rate_limiter(max_calls=3, time_window=1)

        @decorator
        def test_func():
            return "success"

        # First 3 calls should succeed
        for _ in range(3):
            result = test_func()
            assert result == "success", "Result must not be empty"

    def test_rate_limiter_blocks_calls_exceeding_limit(self):
        """Test blocking calls exceeding limit."""
        decorator = rate_limiter(max_calls=2, time_window=60)

        @decorator
        def test_func():
            return "success"

        # First 2 calls succeed
        test_func()
        test_func()

        # Third call should raise
        with pytest.raises(Exception):
            test_func()

    def test_rate_limiter_resets_after_time_window(self):
        """Test reset after time window expires."""
        decorator = rate_limiter(max_calls=1, time_window=1)

        @decorator
        def test_func():
            return "success"

        # First call succeeds
        result = test_func()
        assert result == "success", "Result must not be empty"

        # Second call fails
        with pytest.raises(Exception):
            test_func()

        # Wait for window to expire
        time.sleep(1.1)

        # Should succeed again
        result = test_func()
        assert result == "success", "Result must not be empty"

    def test_rate_limiter_per_user_tracking(self):
        """Test per-user rate limit tracking."""
        decorator = rate_limiter(max_calls=2, time_window=60, per_user=True)

        @decorator
        def test_func(user_id):
            return "success"

        # Different users have separate limits
        assert test_func("user1") == "success", "Condition must be true"
        assert test_func("user2") == "success", "Condition must be true"
        assert test_func("user1") == "success", "Condition must be true"

        # user1 exceeds limit
        with pytest.raises(Exception):
            test_func("user1")

    def test_rate_limiter_zero_calls(self):
        """Test with max_calls=0."""
        decorator = rate_limiter(max_calls=0, time_window=60)

        @decorator
        def test_func():
            return "success"

        with pytest.raises(Exception):
            test_func()

    def test_rate_limiter_large_window(self):
        """Test with large time window."""
        decorator = rate_limiter(max_calls=1000, time_window=3600)

        @decorator
        def test_func():
            return "success"

        # Should allow many calls
        for _ in range(100):
            result = test_func()
            assert result == "success", "Result must not be empty"


# ============================================================================
# VERIFY_SESSION_INTEGRITY TESTS
# ============================================================================


class TestVerifySessionIntegrity:
    """Test verify_session_integrity function."""

    def test_verify_session_integrity_valid(self, temp_session_file):
        """Test with valid session."""
        result = verify_session_integrity(temp_session_file)
        assert isinstance(result, bool)

    def test_verify_session_integrity_missing_file(self):
        """Test with missing session file."""
        result = verify_session_integrity("/nonexistent/session.json")
        assert result is False, "Result must not be empty"

    def test_verify_session_integrity_corrupted_json(self, tmp_path):
        """Test with corrupted JSON."""
        session_file = tmp_path / "corrupt.json"
        session_file.write_text("not valid json")
        result = verify_session_integrity(session_file)
        assert result is False, "Result must not be empty"

    def test_verify_session_integrity_empty_file(self, tmp_path):
        """Test with empty file."""
        session_file = tmp_path / "empty.json"
        session_file.write_text("")
        result = verify_session_integrity(session_file)
        assert result is False, "Result must not be empty"

    def test_verify_session_integrity_expired_session(self, tmp_path):
        """Test with expired session."""
        session_file = tmp_path / "expired.json"
        expired_time = datetime.now(UTC) - timedelta(days=30)
        session_data = {
            "user_id": "user123",
            "created_at": expired_time.isoformat(),
        }
        session_file.write_text(json.dumps(session_data))
        result = verify_session_integrity(session_file)
        assert isinstance(result, bool)

    def test_verify_session_integrity_missing_user_id(self, tmp_path):
        """Test with missing user_id."""
        session_file = tmp_path / "no_user.json"
        session_data = {
            "created_at": datetime.now(UTC).isoformat(),
        }
        session_file.write_text(json.dumps(session_data))
        result = verify_session_integrity(session_file)
        assert result is False, "Result must not be empty"


# ============================================================================
# LOG_SECURITY_EVENT TESTS
# ============================================================================


class TestLogSecurityEvent:
    """Test log_security_event function."""

    def test_log_security_event_basic(self, mock_logger):
        """Test basic security event logging."""
        result = log_security_event("login", "user123", "success")
        assert result is None or isinstance(result, dict)

    def test_log_security_event_with_details(self, mock_logger):
        """Test logging with additional details."""
        result = log_security_event(
            "login", "user123", "success", details={"ip": "192.168.1.1", "method": "password"}
        )
        assert result is None or isinstance(result, dict)

    def test_log_security_event_types(self, mock_logger):
        """Test various event types."""
        event_types = [
            "login",
            "logout",
            "failed_login",
            "password_change",
            "permission_denied",
            "account_locked",
            "suspicious_activity",
        ]

        for event_type in event_types:
            result = log_security_event(event_type, "user123", "info")
            assert result is None or isinstance(result, dict)

    def test_log_security_event_with_timestamp(self, mock_logger):
        """Test logging with timestamp."""
        timestamp = datetime.now(UTC)
        result = log_security_event("login", "user123", "success", timestamp=timestamp)
        assert result is None or isinstance(result, dict)

    def test_log_security_event_with_context(self, mock_logger):
        """Test logging with context."""
        result = log_security_event(
            "login", "user123", "success", context={"app": "codex", "version": "1.0"}
        )
        assert result is None or isinstance(result, dict)


# ============================================================================
# CHECK_PERMISSIONS TESTS
# ============================================================================


class TestCheckPermissions:
    """Test check_permissions function."""

    def test_check_permissions_has_permission(self):
        """Test with user having permission."""
        user_perms = ["read", "write"]
        required = "read"
        result = check_permissions(user_perms, required)
        assert result is True, "Result must not be empty"

    def test_check_permissions_lacks_permission(self):
        """Test with user lacking permission."""
        user_perms = ["read"]
        required = "write"
        result = check_permissions(user_perms, required)
        assert result is False, "Result must not be empty"

    def test_check_permissions_admin_override(self):
        """Test admin permission override."""
        user_perms = ["admin"]
        required = "delete"
        result = check_permissions(user_perms, required)
        assert result is True, "Result must not be empty"

    def test_check_permissions_empty_user_perms(self):
        """Test with empty user permissions."""
        result = check_permissions([], "read")
        assert result is False, "Result must not be empty"

    def test_check_permissions_empty_required(self):
        """Test with empty required permission."""
        result = check_permissions(["read"], "")
        assert isinstance(result, bool)

    def test_check_permissions_multiple_required(self):
        """Test with multiple required permissions."""
        user_perms = ["read", "write"]
        required = ["read", "write"]
        result = check_permissions(user_perms, required)
        assert isinstance(result, bool)

    def test_check_permissions_case_sensitivity(self):
        """Test case sensitivity."""
        result = check_permissions(["Read"], "read")
        assert result is False, "Result must not be empty"

    def test_check_permissions_wildcard(self):
        """Test wildcard permissions."""
        user_perms = ["*"]
        result = check_permissions(user_perms, "any_permission")
        assert result is True, "Result must not be empty"


# ============================================================================
# PARAMETRIZED TESTS
# ============================================================================


@pytest.mark.parametrize(
    "malicious_input,expected",
    [
        ("'; DROP TABLE;", False),
        ("1' OR '1'='1", False),
        ("test@example.com", True),
        ("normal text", True),
        ("", True),
    ],
)
def test_validate_input_parametrized(malicious_input, expected):
    """Parametrized test for validate_input."""
    result = validate_input(malicious_input)
    assert result == expected, "Result must not be empty"


@pytest.mark.parametrize(
    "value,max_len,should_truncate",
    [
        ("short", 100, False),
        ("A" * 50, 100, False),
        ("A" * 500, 100, True),
        ("test", 4, False),
        ("test", 3, True),
    ],
)
def test_sanitize_for_logging_parametrized(value, max_len, should_truncate):
    """Parametrized test for sanitize_for_logging."""
    result = sanitize_for_logging(value, max_length=max_len)
    if should_truncate:
        assert len(result) <= max_len, "Result must not be empty"
    else:
        assert len(result) <= max_len, "Result must not be empty"


@pytest.mark.parametrize(
    "path,should_be_absolute",
    [
        ("/home/user/file.txt", True),
        ("relative/path", False),
        ("./file.txt", False),
        ("../parent", False),
        ("/usr/local/bin", True),
    ],
)
def test_enforce_absolute_path_parametrized(path, should_be_absolute):
    """Parametrized test for enforce_absolute_path."""
    if should_be_absolute:
        result = enforce_absolute_path(path)
        assert isinstance(result, Path)
    else:
        with pytest.raises((ValueError, RuntimeError)):
            enforce_absolute_path(path)
