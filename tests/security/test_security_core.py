"""Comprehensive coverage for security.core."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

import pytest

from security import core

# ---------------------------------------------------------------------------
# sanitize_for_logging
# ---------------------------------------------------------------------------


def test_sanitize_for_logging_basic() -> None:
    result = core.sanitize_for_logging("hello world")
    assert result == "hello world", "Result must not be empty"


def test_sanitize_for_logging_removes_newlines() -> None:
    result = core.sanitize_for_logging("line1\nline2\r\nline3")
    assert "\n" not in result, "Result must not be empty"
    assert "\r" not in result, "Result must not be empty"


def test_sanitize_for_logging_removes_control_chars() -> None:
    result = core.sanitize_for_logging("hello\x00world\x1f!")
    assert "\x00" not in result, "Result must not be empty"
    assert "\x1f" not in result, "Result must not be empty"


def test_sanitize_for_logging_truncates_long_input() -> None:
    long_str = "a" * 300
    result = core.sanitize_for_logging(long_str, max_length=200)
    assert result.endswith("...[truncated]"), "Result must not be empty"
    assert len(result) == 200 + len("...[truncated]"), "Result must not be empty"


def test_sanitize_for_logging_accepts_bytes() -> None:
    result = core.sanitize_for_logging(b"hello bytes")
    assert "hello bytes" in result, "Result must not be empty"


def test_sanitize_for_logging_accepts_non_string() -> None:
    result = core.sanitize_for_logging(12345)
    assert "12345" in result, "Result must not be empty"


def test_sanitize_for_logging_removes_tabs() -> None:
    result = core.sanitize_for_logging("col1\tcol2")
    assert "\t" not in result, "Result must not be empty"


# ---------------------------------------------------------------------------
# _ensure_str (tested indirectly)
# ---------------------------------------------------------------------------


def test_ensure_str_via_sanitize_bytes() -> None:
    # bytes -> decoded str
    result = core.sanitize_for_logging(b"\xff\xfe hello")
    assert isinstance(result, str)


def test_ensure_str_via_sanitize_int() -> None:
    result = core.sanitize_for_logging(42)
    assert result == "42", "Result must not be empty"


# ---------------------------------------------------------------------------
# sanitize_user_content
# ---------------------------------------------------------------------------


def test_sanitize_user_content_html() -> None:
    result = core.sanitize_user_content("<script>alert('x')</script>")
    assert "<" not in result, "Result must not be empty"


def test_sanitize_user_content_markdown() -> None:
    result = core.sanitize_user_content("<b>bold</b>", content_type="markdown")
    assert "&lt;" in result or "<" not in result, "Result must not be empty"


def test_sanitize_user_content_removes_javascript_protocol() -> None:
    result = core.sanitize_user_content("javascript:alert(1)")
    assert "javascript:" not in result, "Result must not be empty"


def test_sanitize_user_content_removes_onerror() -> None:
    result = core.sanitize_user_content('<img onerror="alert(1)">')
    # onerror= pattern should be stripped
    assert "onerror" not in result, "Result must not be empty"


def test_sanitize_user_content_plain_text_unchanged() -> None:
    result = core.sanitize_user_content("hello world")
    assert "hello" in result, "Result must not be empty"


# ---------------------------------------------------------------------------
# validate_input
# ---------------------------------------------------------------------------


def test_validate_input_sql_rejects() -> None:
    with pytest.raises(core.SecurityError):
        core.validate_input("1; DROP TABLE users;", input_type="sql")


def test_validate_input_sql_accepts_clean() -> None:
    result = core.validate_input("SELECT * FROM users", input_type="sql")
    assert "SELECT" in result, "Result must not be empty"


def test_validate_input_sql_rejects_or_pattern() -> None:
    with pytest.raises(core.SecurityError):
        core.validate_input("' OR '1'='1", input_type="sql")


def test_validate_input_sql_rejects_comment() -> None:
    with pytest.raises(core.SecurityError):
        core.validate_input("admin'--", input_type="sql")


def test_validate_input_sql_rejects_block_comment() -> None:
    with pytest.raises(core.SecurityError):
        core.validate_input("/* comment */", input_type="sql")


def test_validate_input_html_rejects_script_tag() -> None:
    with pytest.raises(core.SecurityError):
        core.validate_input("<script>alert(1)</script>", input_type="html")


def test_validate_input_html_rejects_javascript_url() -> None:
    with pytest.raises(core.SecurityError):
        core.validate_input("javascript:void(0)", input_type="html")


def test_validate_input_html_accepts_clean() -> None:
    result = core.validate_input("Hello world", input_type="html")
    assert "Hello" in result, "Result must not be empty"


def test_validate_path_traversal_blocked() -> None:
    with pytest.raises(core.SecurityError):
        core.validate_input("../../etc/passwd", input_type="path")


def test_validate_input_path_null_byte() -> None:
    with pytest.raises(core.SecurityError):
        core.validate_input("file\x00.txt", input_type="path")


def test_validate_input_path_tilde_blocked() -> None:
    with pytest.raises(core.SecurityError):
        core.validate_input("~/secret", input_type="path")


def test_validate_input_path_absolute_blocked() -> None:
    with pytest.raises(core.SecurityError):
        core.validate_input("/etc/passwd", input_type="path")


def test_validate_input_path_accepts_relative() -> None:
    result = core.validate_input("subdir/file.txt", input_type="path")
    assert result == "subdir/file.txt", "Result must not be empty"


def test_validate_input_path_newline_blocked() -> None:
    with pytest.raises(core.SecurityError):
        core.validate_input("file\nname.txt", input_type="path")


def test_validate_input_text_accepts_normal() -> None:
    result = core.validate_input("hello world", input_type="text")
    assert "hello" in result, "Result must not be empty"


def test_validate_input_text_rejects_null_byte() -> None:
    with pytest.raises(core.SecurityError):
        core.validate_input("hello\x00world", input_type="text")


def test_validate_input_text_rejects_control_char() -> None:
    with pytest.raises(core.SecurityError):
        core.validate_input("hello\x01world", input_type="text")


def test_validate_input_text_allows_tab_newline_cr() -> None:
    # \t \n \r are allowed in text mode
    result = core.validate_input("line1\nline2\ttabbed", input_type="text")
    assert isinstance(result, str)


def test_validate_input_json_blocks_prototype() -> None:
    with pytest.raises(core.SecurityError):
        core.validate_input("__proto__", input_type="json")


def test_validate_input_json_blocks_constructor() -> None:
    with pytest.raises(core.SecurityError):
        core.validate_input('{"constructor": {}}', input_type="json")


def test_validate_input_json_accepts_clean() -> None:
    result = core.validate_input('{"key": "value"}', input_type="json")
    assert '"key"' in result, "Result must not be empty"


def test_validate_input_exceeds_max_length() -> None:
    long_str = "a" * 10_001
    with pytest.raises(core.SecurityError, match="max length"):
        core.validate_input(long_str)


def test_validate_input_non_string_raises() -> None:
    with pytest.raises(core.SecurityError, match="Expected string"):
        core.validate_input(123)  # type: ignore[arg-type]


def test_validate_input_unsupported_type_raises() -> None:
    with pytest.raises(core.SecurityError, match="Unsupported"):
        core.validate_input("value", input_type="xml")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# enforce_absolute_path
# ---------------------------------------------------------------------------


def test_enforce_absolute_path_valid(tmp_path: Path) -> None:
    result = core.enforce_absolute_path(str(tmp_path))
    assert result == tmp_path, "Result must not be empty"


def test_enforce_absolute_path_traversal_raises() -> None:
    with pytest.raises(core.SecurityError, match="traversal"):
        core.enforce_absolute_path("/safe/../etc/passwd")


def test_enforce_absolute_path_relative_raises() -> None:
    with pytest.raises(core.SecurityError, match="absolute"):
        core.enforce_absolute_path("relative/path")


# ---------------------------------------------------------------------------
# sanitize_path
# ---------------------------------------------------------------------------


def test_sanitize_path_valid(tmp_path: Path) -> None:
    subdir = tmp_path / "sub"
    subdir.mkdir()
    result = core.sanitize_path(subdir, tmp_path)
    assert result == subdir.resolve(), "Result must not be empty"


def test_sanitize_path_escape_raises(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside"
    with pytest.raises(ValueError, match="outside base directory"):
        core.sanitize_path(outside, tmp_path)


# ---------------------------------------------------------------------------
# check_permissions
# ---------------------------------------------------------------------------


def test_check_permissions_nonexistent_path(tmp_path: Path) -> None:
    result = core.check_permissions(tmp_path / "nonexistent.txt", "read")
    assert result is False, "Result must not be empty"


def test_check_permissions_read_existing(tmp_path: Path) -> None:
    f = tmp_path / "test.txt"
    f.write_text("hello")
    assert core.check_permissions(f, "read") is True


def test_check_permissions_write_existing(tmp_path: Path) -> None:
    f = tmp_path / "test.txt"
    f.write_text("hello")
    assert core.check_permissions(f, "write") is True


def test_check_permissions_execute_dir(tmp_path: Path) -> None:
    result = core.check_permissions(tmp_path, "execute")
    assert isinstance(result, bool)


def test_check_permissions_unknown_mode(tmp_path: Path) -> None:
    f = tmp_path / "test.txt"
    f.write_text("hello")
    result = core.check_permissions(f, "unknown")
    assert result is False, "Result must not be empty"


# ---------------------------------------------------------------------------
# rate_limiter
# ---------------------------------------------------------------------------


def test_rate_limiter_allows_then_blocks() -> None:
    calls = []

    @core.rate_limiter(calls=2, period=10, key_func=lambda *_: "k")
    def fn(x: int) -> int:
        calls.append(x)
        return x

    assert fn(1) == 1, "Condition must be true"
    assert fn(2) == 2, "Condition must be true"
    with pytest.raises(core.SecurityError):
        fn(3)


def test_rate_limiter_invalid_calls() -> None:
    with pytest.raises(ValueError, match="calls must be positive"):
        core.rate_limiter(calls=0, period=10)


def test_rate_limiter_invalid_period() -> None:
    with pytest.raises(ValueError, match="period must be positive"):
        core.rate_limiter(calls=10, period=0)


def test_rate_limiter_global_key() -> None:
    @core.rate_limiter(calls=3, period=60)
    def fn() -> str:
        return "ok"

    assert fn() == "ok", "Condition must be true"
    assert fn() == "ok", "Condition must be true"
    assert fn() == "ok", "Condition must be true"
    with pytest.raises(core.SecurityError):
        fn()


def test_rate_limiter_key_func() -> None:
    @core.rate_limiter(calls=1, period=60, key_func=lambda user: user)
    def fn(user: str) -> str:
        return user

    assert fn("alice") == "alice", "Condition must be true"
    assert fn("bob") == "bob", "Condition must be true"
    with pytest.raises(core.SecurityError):
        fn("alice")  # alice is now blocked


def test_rate_limiter_window_expires() -> None:
    clock_time = [0.0]

    def fake_clock() -> float:
        return clock_time[0]

    @core.rate_limiter(calls=1, period=5.0, clock=fake_clock)
    def fn() -> str:
        return "ok"

    assert fn() == "ok", "Condition must be true"
    with pytest.raises(core.SecurityError):
        fn()

    # Advance time past window
    clock_time[0] = 6.0
    assert fn() == "ok", "Condition must be true"


def test_rate_limiter_async() -> None:
    async def run() -> None:
        @core.rate_limiter(calls=2, period=10)
        async def async_fn() -> str:
            return "ok"

        assert await async_fn() == "ok", "Condition must be true"
        assert await async_fn() == "ok", "Condition must be true"
        with pytest.raises(core.SecurityError):
            await async_fn()

    asyncio.run(run())


def test_rate_limiter_async_with_key_func() -> None:
    async def run() -> None:
        @core.rate_limiter(calls=1, period=60, key_func=lambda user: user)
        async def async_fn(user: str) -> str:
            return user

        assert await async_fn("alice") == "alice", "Condition must be true"
        assert await async_fn("bob") == "bob", "Condition must be true"
        with pytest.raises(core.SecurityError):
            await async_fn("alice")

    asyncio.run(run())


# ---------------------------------------------------------------------------
# verify_csrf_token
# ---------------------------------------------------------------------------


def test_verify_csrf_token_match() -> None:
    # Should not raise
    core.verify_csrf_token("token123", "token123")


def test_verify_csrf_token_mismatch() -> None:
    with pytest.raises(core.SecurityError, match="mismatch"):
        core.verify_csrf_token("token_a", "token_b")


def test_verify_csrf_token_none_provided() -> None:
    with pytest.raises(core.SecurityError, match="Missing"):
        core.verify_csrf_token(None, "session_token")


def test_verify_csrf_token_none_session() -> None:
    with pytest.raises(core.SecurityError, match="Missing"):
        core.verify_csrf_token("provided_token", None)


def test_verify_csrf_token_empty_string() -> None:
    with pytest.raises(core.SecurityError, match="Missing"):
        core.verify_csrf_token("", "session")


# ---------------------------------------------------------------------------
# verify_session_integrity
# ---------------------------------------------------------------------------


def test_verify_session_integrity_valid() -> None:
    sessions = [
        {
            "id": "sess123",
            "fingerprint": "fp-abc",
            "ip": "127.0.0.1",
            "user_agent": "TestBrowser/1.0",
        }
    ]
    metadata = {
        "fingerprint": "fp-abc",
        "ip": "127.0.0.1",
        "user_agent": "TestBrowser/1.0",
    }
    # Should not raise
    core.verify_session_integrity("sess123", metadata, sessions)


def test_verify_session_integrity_incomplete_metadata() -> None:
    with pytest.raises(core.SecurityError, match="Incomplete"):
        core.verify_session_integrity(
            "sess123",
            {"fingerprint": "fp-abc", "ip": "127.0.0.1"},  # missing user_agent
            [],
        )


def test_verify_session_integrity_fingerprint_mismatch() -> None:
    sessions = [
        {
            "id": "sess123",
            "fingerprint": "fp-original",
            "ip": "127.0.0.1",
            "user_agent": "TestBrowser/1.0",
        }
    ]
    metadata = {
        "fingerprint": "fp-different",
        "ip": "127.0.0.1",
        "user_agent": "TestBrowser/1.0",
    }
    with pytest.raises(core.SecurityError, match="fingerprint"):
        core.verify_session_integrity("sess123", metadata, sessions)


def test_verify_session_integrity_ip_mismatch() -> None:
    sessions = [
        {
            "id": "sess123",
            "fingerprint": "fp-abc",
            "ip": "192.168.1.1",
            "user_agent": "TestBrowser/1.0",
        }
    ]
    metadata = {
        "fingerprint": "fp-abc",
        "ip": "127.0.0.1",
        "user_agent": "TestBrowser/1.0",
    }
    with pytest.raises(core.SecurityError, match="Session IP mismatch"):
        core.verify_session_integrity("sess123", metadata, sessions)


def test_verify_session_integrity_user_agent_mismatch() -> None:
    sessions = [
        {
            "id": "sess123",
            "fingerprint": "fp-abc",
            "ip": "127.0.0.1",
            "user_agent": "OriginalBrowser/1.0",
        }
    ]
    metadata = {
        "fingerprint": "fp-abc",
        "ip": "127.0.0.1",
        "user_agent": "DifferentBrowser/2.0",
    }
    with pytest.raises(core.SecurityError, match="user agent"):
        core.verify_session_integrity("sess123", metadata, sessions)


def test_verify_session_integrity_no_matching_session() -> None:
    # No matching session — no exception (loop just doesn't find it)
    metadata = {
        "fingerprint": "fp-abc",
        "ip": "127.0.0.1",
        "user_agent": "TestBrowser/1.0",
    }
    core.verify_session_integrity("unknown-sess", metadata, [])


# ---------------------------------------------------------------------------
# log_security_event
# ---------------------------------------------------------------------------


def test_log_security_event_with_custom_logger() -> None:
    mock_logger = logging.getLogger("test_security_event")
    # Should not raise
    core.log_security_event("user_login", logger=mock_logger)


def test_log_security_event_default_logger() -> None:
    # Should not raise
    core.log_security_event("user_logout")


# ---------------------------------------------------------------------------
# hmac_compare
# ---------------------------------------------------------------------------


def test_hmac_compare_equal() -> None:
    assert core.hmac_compare("secret123", "secret123") is True


def test_hmac_compare_different() -> None:
    assert core.hmac_compare("secret123", "secret456") is False


def test_hmac_compare_different_lengths() -> None:
    assert core.hmac_compare("short", "muchlongerstring") is False


def test_hmac_compare_empty_strings() -> None:
    assert core.hmac_compare("", "") is True


def test_hmac_compare_unicode() -> None:
    token = "αβγδ1234"
    assert core.hmac_compare(token, token) is True
    assert core.hmac_compare(token, "αβγδ5678") is False
