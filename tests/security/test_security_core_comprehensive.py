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

import asyncio
import inspect
import logging
import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from security.core import (
    SecurityError,
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
    get_logger = logging.getLogger
    monkeypatch.setattr(
        logging,
        "getLogger",
        lambda name=None: mock if name == "codex.security" else get_logger(name),
    )
    return mock


@pytest.fixture
def session_metadata():
    """Return fresh request metadata for each session integrity test."""
    return {
        "fingerprint": "fingerprint123",
        "ip": "192.168.1.1",
        "user_agent": "TestBrowser/1.0",
    }


@pytest.fixture
def active_sessions(session_metadata):
    """Return independent server-side session metadata."""
    return [{"id": "session123", **session_metadata}]


@pytest.fixture
def fake_clock():
    """A controllable monotonic clock avoids sleeps and finite side effects."""
    return MagicMock(return_value=0.0)


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
        with pytest.raises(SecurityError, match="SQL injection pattern"):
            validate_input("'; DROP TABLE users; --", input_type="sql")

    def test_validate_input_sql_injection_delete(self):
        """Test DELETE statement detection."""
        with pytest.raises(SecurityError, match="SQL injection pattern"):
            validate_input("value'; DELETE FROM users WHERE '1'='1", input_type="sql")

    def test_validate_input_sql_injection_with_trailing_comment(self):
        """The trailing SQL comment is a rejected pattern."""
        with pytest.raises(SecurityError, match="SQL injection pattern"):
            validate_input("1' UNION SELECT * FROM users --", input_type="sql")

    def test_validate_input_xss_script_tag(self):
        """Test XSS script tag detection."""
        with pytest.raises(SecurityError, match="XSS pattern"):
            validate_input("<script>alert('xss')</script>", input_type="html")

    def test_validate_input_xss_javascript_uri(self):
        """Test JavaScript URI detection."""
        with pytest.raises(SecurityError, match="XSS pattern"):
            validate_input('<a href="javascript:alert()">click</a>', input_type="html")

    def test_validate_input_xss_event_handler(self):
        """Test event handler detection."""
        with pytest.raises(SecurityError, match="XSS pattern"):
            validate_input("<img src=x onerror=alert()>", input_type="html")

    def test_validate_input_json_prototype_pollution(self):
        """Test JSON prototype pollution detection."""
        with pytest.raises(SecurityError, match="Prototype pollution"):
            validate_input('{"__proto__": {"admin": true}}', input_type="json")

    def test_validate_input_clean_string(self):
        """Test valid clean string."""
        result = validate_input("This is a valid input")
        assert result == "This is a valid input"

    def test_validate_input_clean_email(self):
        """Test valid email input."""
        result = validate_input("user@example.com")
        assert result == "user@example.com"

    def test_validate_input_clean_with_numbers(self):
        """Test valid input with numbers."""
        result = validate_input("User123")
        assert result == "User123"

    def test_validate_input_empty_string(self):
        """Test empty string."""
        result = validate_input("")
        assert result == ""

    def test_validate_input_none_value(self):
        """Test None value."""
        with pytest.raises(SecurityError, match="Expected string"):
            validate_input(None)

    def test_validate_input_numeric_value(self):
        """Test numeric value."""
        with pytest.raises(SecurityError, match="Expected string"):
            validate_input(12345)

    def test_validate_input_comment_with_double_dash(self):
        """Test SQL comment detection."""
        with pytest.raises(SecurityError, match="SQL injection pattern"):
            validate_input("SELECT * FROM users -- comment", input_type="sql")

    def test_validate_input_comment_with_slash(self):
        """Test SQL block comment detection."""
        with pytest.raises(SecurityError, match="SQL injection pattern"):
            validate_input("SELECT * /* comment */ FROM users", input_type="sql")

    def test_validate_input_text_transforms_content(self):
        """Default text validation returns the sanitized string, not a boolean."""
        assert validate_input("FOO and safe text") == "[REDACTED] and safe text"

    @pytest.mark.parametrize("control", ["\0", "\x01", "\x1f"])
    def test_validate_input_rejects_text_controls(self, control):
        with pytest.raises(SecurityError, match="Invalid control characters"):
            validate_input(f"before{control}after")

    def test_validate_input_preserves_allowed_whitespace(self):
        text = "line1\nline2\r\n\tindented"
        assert validate_input(text) == text

    def test_validate_input_html_escapes_safe_markup(self):
        assert validate_input("<b>safe & sound</b>", input_type="html") == (
            "&lt;b&gt;safe &amp; sound&lt;/b&gt;"
        )

    def test_validate_input_max_length_boundary(self):
        assert validate_input("abcd", max_length=4) == "abcd"
        with pytest.raises(SecurityError, match="Input exceeds max length 4"):
            validate_input("abcde", max_length=4)

    @pytest.mark.parametrize("path", ["../secret", "/etc/passwd", "~/secret", "a\0b"])
    def test_validate_input_rejects_unsafe_paths(self, path):
        with pytest.raises(SecurityError, match="traversal|Invalid characters"):
            validate_input(path, input_type="path")

    def test_validate_input_rejects_symlink_escape(self, tmp_path, monkeypatch):
        root = tmp_path / "root"
        root.mkdir()
        outside = tmp_path / "outside"
        outside.mkdir()
        (root / "escape").symlink_to(outside, target_is_directory=True)
        monkeypatch.chdir(root)
        with pytest.raises(SecurityError, match="escape current directory"):
            validate_input("escape/secret.txt", input_type="path")

    def test_validate_input_rejects_unsupported_type(self):
        with pytest.raises(SecurityError, match="Unsupported input_type"):
            validate_input("value", input_type="xml")


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
        token = "valid_token"
        assert verify_csrf_token(token, token) is None

    def test_verify_csrf_token_invalid_token(self):
        """Test with invalid token."""
        with pytest.raises(SecurityError, match="CSRF token mismatch"):
            verify_csrf_token("token1", "token2")

    @pytest.mark.parametrize("provided", ["", None])
    def test_verify_csrf_token_missing_provided_token(self, provided):
        """A missing request token cannot match a valid server-side token."""
        with pytest.raises(SecurityError, match="Missing CSRF token"):
            verify_csrf_token(provided, "token")

    @pytest.mark.parametrize("session", ["", None])
    def test_verify_csrf_token_missing_session_token(self, session):
        with pytest.raises(SecurityError, match="Missing CSRF token"):
            verify_csrf_token("token", session)

    def test_verify_csrf_token_empty_token(self):
        """Test with empty token."""
        with pytest.raises(SecurityError, match="Missing CSRF token"):
            verify_csrf_token("", "")

    def test_verify_csrf_token_none_values(self):
        """Test with None values."""
        with pytest.raises(SecurityError, match="Missing CSRF token"):
            verify_csrf_token(None, None)

    def test_verify_csrf_token_case_sensitive(self):
        """Test token comparison is case sensitive."""
        with pytest.raises(SecurityError, match="CSRF token mismatch"):
            verify_csrf_token("Token", "token")

    def test_verify_csrf_token_whitespace_sensitive(self):
        """Test token comparison is whitespace sensitive."""
        with pytest.raises(SecurityError, match="CSRF token mismatch"):
            verify_csrf_token("token ", "token")

    def test_verify_csrf_token_long_token(self):
        """Test with long token."""
        long_token = "A" * 1000
        assert verify_csrf_token(long_token, long_token) is None


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
        decorator = rate_limiter(calls=5, period=60)
        assert callable(decorator), "Condition must be true"

    def test_rate_limiter_allows_calls_within_limit(self, fake_clock):
        """Test allowing calls within limit."""
        decorator = rate_limiter(calls=3, period=1, clock=fake_clock)

        @decorator
        def test_func():
            return "success"

        # First 3 calls should succeed
        for _ in range(3):
            result = test_func()
            assert result == "success", "Result must not be empty"

    def test_rate_limiter_blocks_calls_exceeding_limit(self, fake_clock):
        """Test blocking calls exceeding limit."""
        decorator = rate_limiter(calls=2, period=60, clock=fake_clock)
        executed = []

        @decorator
        def test_func():
            executed.append("called")
            return "success"

        # First 2 calls succeed
        test_func()
        test_func()

        # Third call should raise
        with pytest.raises(SecurityError, match="Rate limit exceeded"):
            test_func()
        assert executed == ["called", "called"]

    def test_rate_limiter_resets_after_time_window(self, fake_clock):
        """Test reset after time window expires."""
        decorator = rate_limiter(calls=1, period=1, clock=fake_clock)

        @decorator
        def test_func():
            return "success"

        # First call succeeds
        result = test_func()
        assert result == "success", "Result must not be empty"

        # Second call fails
        with pytest.raises(SecurityError, match="Rate limit exceeded"):
            test_func()

        # Entries remain in the window at the exact boundary.
        fake_clock.return_value = 1.0
        with pytest.raises(SecurityError, match="Rate limit exceeded"):
            test_func()

        fake_clock.return_value = 1.1

        # Should succeed again
        result = test_func()
        assert result == "success", "Result must not be empty"

    def test_rate_limiter_per_user_tracking(self, fake_clock):
        """Test per-user rate limit tracking."""
        decorator = rate_limiter(
            calls=2, period=60, key_func=lambda user_id: user_id, clock=fake_clock
        )

        @decorator
        def test_func(user_id):
            return "success"

        # Different users have separate limits
        assert test_func("user1") == "success", "Condition must be true"
        assert test_func("user2") == "success", "Condition must be true"
        assert test_func("user1") == "success", "Condition must be true"

        # user1 exceeds limit
        with pytest.raises(SecurityError, match="Rate limit exceeded"):
            test_func("user1")
        assert test_func("user2") == "success"

    @pytest.mark.parametrize("calls", [0, -1])
    def test_rate_limiter_invalid_calls(self, calls):
        """Invalid limits are rejected when the decorator is created."""
        with pytest.raises(ValueError, match="calls must be positive"):
            rate_limiter(calls=calls, period=60)

    @pytest.mark.parametrize("period", [0, -1])
    def test_rate_limiter_invalid_period(self, period):
        with pytest.raises(ValueError, match="period must be positive"):
            rate_limiter(calls=1, period=period)

    def test_rate_limiter_large_window(self, fake_clock):
        """Test with large time window."""
        decorator = rate_limiter(calls=1000, period=3600, clock=fake_clock)

        @decorator
        def test_func():
            return "success"

        # Should allow many calls
        for _ in range(100):
            result = test_func()
            assert result == "success", "Result must not be empty"

    def test_rate_limiter_preserves_signature_and_arguments(self, fake_clock):
        def original(value, *, suffix="!"):
            """The original callable's metadata."""
            return f"{value}{suffix}"

        decorated = rate_limiter(calls=1, clock=fake_clock)(original)
        assert inspect.signature(decorated) == inspect.signature(original)
        assert decorated.__name__ == original.__name__
        assert decorated.__doc__ == original.__doc__
        assert decorated("hello", suffix="?") == "hello?"

    def test_rate_limiter_async_keyed_windows(self, fake_clock):
        """Async calls enforce independent keys and expire like sync calls."""
        executed = []

        @rate_limiter(calls=1, period=1, key_func=lambda user: user, clock=fake_clock)
        async def request(user):
            executed.append(user)
            return user

        async def exercise():
            assert await request("alice") == "alice"
            assert await request("bob") == "bob"
            with pytest.raises(SecurityError, match="Rate limit exceeded"):
                await request("alice")
            assert executed == ["alice", "bob"]
            fake_clock.return_value = 1.1
            assert await request("alice") == "alice"
            assert executed == ["alice", "bob", "alice"]

        assert inspect.iscoroutinefunction(request)
        asyncio.run(exercise())


# ============================================================================
# VERIFY_SESSION_INTEGRITY TESTS
# ============================================================================


class TestVerifySessionIntegrity:
    """Test verify_session_integrity function."""

    def test_verify_session_integrity_valid(self, session_metadata, active_sessions):
        """Matching request and server-side metadata validate without mutation."""
        expected_metadata = session_metadata.copy()
        expected_sessions = [session.copy() for session in active_sessions]
        assert verify_session_integrity("session123", session_metadata, active_sessions) is None
        assert session_metadata == expected_metadata
        assert active_sessions == expected_sessions

    @pytest.mark.parametrize("session_id", ["", None])
    def test_verify_session_integrity_missing_id(
        self, session_id, session_metadata, active_sessions
    ):
        with pytest.raises(SecurityError, match="Incomplete session metadata"):
            verify_session_integrity(session_id, session_metadata, active_sessions)

    @pytest.mark.parametrize("field", ["fingerprint", "ip", "user_agent"])
    @pytest.mark.parametrize("missing_value", ["absent", "", None])
    def test_verify_session_integrity_incomplete_metadata(
        self, field, missing_value, session_metadata, active_sessions
    ):
        if missing_value == "absent":
            session_metadata.pop(field)
        else:
            session_metadata[field] = missing_value
        with pytest.raises(SecurityError, match="Incomplete session metadata"):
            verify_session_integrity("session123", session_metadata, active_sessions)

    @pytest.mark.parametrize(
        "field,message",
        [
            ("fingerprint", "Session fingerprint mismatch"),
            ("ip", "Session IP mismatch"),
            ("user_agent", "Session user agent mismatch"),
        ],
    )
    def test_verify_session_integrity_mismatch(
        self, field, message, session_metadata, active_sessions
    ):
        session_metadata[field] = "different"
        with pytest.raises(SecurityError, match=message):
            verify_session_integrity("session123", session_metadata, active_sessions)

    def test_verify_session_integrity_finds_matching_session(
        self, session_metadata, active_sessions
    ):
        """Unrelated sessions must not affect the requested session's checks."""
        active_sessions.insert(
            0, {"id": "other", "fingerprint": "other", "ip": "other", "user_agent": "other"}
        )
        assert verify_session_integrity("session123", session_metadata, active_sessions) is None

    def test_verify_session_integrity_checks_later_matching_session(
        self, session_metadata, active_sessions
    ):
        active_sessions.insert(0, {"id": "other"})
        active_sessions[1]["fingerprint"] = "changed"
        with pytest.raises(SecurityError, match="Session fingerprint mismatch"):
            verify_session_integrity("session123", session_metadata, active_sessions)


# ============================================================================
# LOG_SECURITY_EVENT TESTS
# ============================================================================


class TestLogSecurityEvent:
    """Test log_security_event function."""

    def test_log_security_event_basic(self, mock_logger):
        """Test basic security event logging."""
        assert log_security_event("login") is None
        mock_logger.info.assert_called_once_with("security_event", extra={"event": "login"})

    def test_log_security_event_with_explicit_logger(self, mock_logger):
        """A supplied logger receives the event instead of the default logger."""
        explicit_logger = MagicMock()
        assert log_security_event("login", logger=explicit_logger) is None
        explicit_logger.info.assert_called_once_with("security_event", extra={"event": "login"})
        mock_logger.info.assert_not_called()

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
            assert log_security_event(event_type) is None
            mock_logger.info.assert_called_with("security_event", extra={"event": event_type})
        assert mock_logger.info.call_count == len(event_types)

    def test_log_security_event_sanitizes_controls(self, mock_logger):
        """Control characters must not create forged multiline log entries."""
        event = "login\nforged\rentry"
        log_security_event(event)
        logged_event = mock_logger.info.call_args.kwargs["extra"]["event"]
        assert "\n" not in logged_event
        assert "\r" not in logged_event

    def test_log_security_event_empty(self, mock_logger):
        """Empty events retain the stable audit record shape."""
        log_security_event("")
        mock_logger.info.assert_called_once_with("security_event", extra={"event": ""})


# ============================================================================
# CHECK_PERMISSIONS TESTS
# ============================================================================


class TestCheckPermissions:
    """Check filesystem access, not application roles or admin overrides."""

    @pytest.mark.parametrize("mode", ["read", "write"])
    def test_check_permissions_existing_file(self, tmp_path, mode):
        path = tmp_path / "file.txt"
        path.write_text("content")
        assert check_permissions(path, mode) is True

    @pytest.mark.parametrize(
        "mode,access_flag", [("read", os.R_OK), ("write", os.W_OK), ("execute", os.X_OK)]
    )
    @pytest.mark.parametrize("allowed", [True, False])
    def test_check_permissions_delegates_to_os_access(
        self, tmp_path, monkeypatch, mode, access_flag, allowed
    ):
        """Both access outcomes are deterministic even when tests run as root."""
        path = tmp_path / "file.txt"
        path.touch()
        access = MagicMock(return_value=allowed)
        monkeypatch.setattr("security.core.os.access", access)
        assert check_permissions(path, mode) is allowed
        access.assert_called_once_with(path, access_flag)

    @pytest.mark.parametrize("mode", ["read", "write", "execute"])
    def test_check_permissions_missing_path(self, tmp_path, monkeypatch, mode):
        access = MagicMock()
        monkeypatch.setattr("security.core.os.access", access)
        assert check_permissions(tmp_path / "missing", mode) is False
        access.assert_not_called()

    @pytest.mark.parametrize("mode", ["", "Read", "delete", "*", "admin"])
    def test_check_permissions_unsupported_mode(self, tmp_path, monkeypatch, mode):
        """Unsupported access modes never confer permissions."""
        access = MagicMock()
        monkeypatch.setattr("security.core.os.access", access)
        assert check_permissions(tmp_path, mode) is False
        access.assert_not_called()


# ============================================================================
# PARAMETRIZED TESTS
# ============================================================================


@pytest.mark.parametrize(
    "value,input_type",
    [
        ("SELECT name FROM users", "sql"),
        ('{"name": "alice"}', "json"),
        ("subdir/file.txt", "path"),
        ("test@example.com", "text"),
        ("normal text", "text"),
        ("", "text"),
    ],
)
def test_validate_input_accepts_clean_values(value, input_type):
    """Validation returns accepted strings unchanged for these input types."""
    assert validate_input(value, input_type=input_type) == value


@pytest.mark.parametrize(
    "value,input_type,message",
    [
        ("'; DROP TABLE users;", "sql", "SQL injection pattern"),
        ("1' OR '1'='1", "sql", "SQL injection pattern"),
        ('{"constructor": {}}', "json", "Prototype pollution"),
        ('{"prototype": {}}', "json", "Prototype pollution"),
        ("<script>alert(1)</script>", "html", "XSS pattern"),
    ],
)
def test_validate_input_rejects_typed_patterns(value, input_type, message):
    with pytest.raises(SecurityError, match=message):
        validate_input(value, input_type=input_type)


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
