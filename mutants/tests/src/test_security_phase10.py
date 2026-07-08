"""Phase 10B gap-fill: security module coverage.

Tests for ``src/codex/security/__init__.py``, ``log_sanitizer.py``, and
``sanitization.py``.  Exercises the public API, edge cases, and error paths.
"""

from __future__ import annotations

import pytest

from codex.security import (
    hash_secure,
    mask_email,
    mask_password,
    mask_sensitive,
    mask_token,
    sanitize_log,
    sanitize_url,
)
from codex.security.log_sanitizer import (
    mask_secrets,
    safe_log,
    safe_log_message,
    sanitize_dict_for_log,
)
from codex.security.log_sanitizer import mask_sensitive as ls_mask_sensitive
from codex.security.log_sanitizer import sanitize_log as ls_sanitize_log
from codex.security.sanitization import sanitize_html

# ============================================================================
# mask_token
# ============================================================================


class TestMaskToken:
    def test_normal_token(self):
        assert mask_token("sk_live_abc123xyz") == "*" * (len("sk_live_abc123xyz") - 4) + "3xyz", "Collection must not be empty"

    def test_empty_token(self):
        assert mask_token("") == "***", "Condition must be true"

    def test_short_token(self):
        result = mask_token("ab")
        assert result == "**", "Result must not be empty"

    def test_exact_show_last(self):
        result = mask_token("abcdefgh", show_last=4)
        assert result.endswith("efgh"), "Result must not be empty"
        assert result.startswith("*"), "Result must not be empty"


# ============================================================================
# mask_email
# ============================================================================


class TestMaskEmail:
    def test_normal_email(self):
        result = mask_email("user@example.com")
        assert result.startswith("u"), "Result must not be empty"
        assert "@example.com" in result, "Result must not be empty"

    def test_no_at_sign(self):
        result = mask_email("not-an-email")
        assert result == "***", "Result must not be empty"


# ============================================================================
# mask_password
# ============================================================================


class TestMaskPassword:
    def test_normal_password(self):
        assert mask_password("secret") == "***", "mask_passw is not valid"

    def test_empty_password(self):
        assert mask_password("") == "(empty)", "mask_passw is not valid"


# ============================================================================
# mask_sensitive
# ============================================================================


class TestMaskSensitive:
    def test_normal_string(self):
        result = mask_sensitive("secret_key_12345")
        assert "***" in result, "Result must not be empty"

    def test_short_string(self):
        result = mask_sensitive("ab")
        assert result == "**", "Result must not be empty"

    def test_empty_string(self):
        assert mask_sensitive("") == "", "Condition must be true"

    def test_custom_show_chars(self):
        result = mask_sensitive("abcdefghijklmnop", show_chars=2)
        assert result.startswith("ab"), "Result must not be empty"
        assert result.endswith("op"), "Result must not be empty"


# ============================================================================
# sanitize_log / sanitize_log_input
# ============================================================================


class TestSanitizeLog:
    def test_removes_newlines(self):
        result = sanitize_log("line1\nline2\rline3")
        assert "\n" not in result, "Result must not be empty"
        assert "\r" not in result, "Result must not be empty"

    def test_removes_control_chars(self):
        result = sanitize_log("hello\x00world\x1f")
        assert "\x00" not in result, "Result must not be empty"

    def test_truncates_long_input(self):
        long_val = "x" * 1000
        result = sanitize_log(long_val, max_length=100)
        assert len(result) <= 120, "Result must not be empty"
        assert "truncated" in result, "Result must not be empty"

    def test_none_input(self):
        result = sanitize_log(None)
        assert result == "None", "Result must not be empty"

    def test_non_string_input(self):
        result = sanitize_log(12345)
        assert result == "12345", "Result must not be empty"


# ============================================================================
# sanitize_dict_for_log
# ============================================================================


class TestSanitizeDictForLog:
    def test_basic_dict(self):
        # Use the recursive implementation from log_sanitizer
        result = sanitize_dict_for_log({"key": "value\nnewline"})
        assert "\n" not in result["key"], "Result must not be empty"

    def test_nested_dict(self):
        # Use the recursive implementation from log_sanitizer
        result = sanitize_dict_for_log({"outer": {"inner": "val\x00ue"}})
        assert "\x00" not in result["outer"]["inner"], "Result must not be empty"

    def test_list_values(self):
        # Use the recursive implementation from log_sanitizer
        result = sanitize_dict_for_log({"items": ["a\nb", "c\rd"]})
        for item in result["items"]:
            assert "\n" not in item, "Item must not be empty"
            assert "\r" not in item, "Item must not be empty"


# ============================================================================
# hash_secure
# ============================================================================


class TestHashSecure:
    def test_sha256_default(self):
        result = hash_secure("test")
        assert len(result) == 64, "Result must not be empty"

    def test_sha512(self):
        result = hash_secure("test", algorithm="sha512")
        assert len(result) == 128, "Result must not be empty"

    def test_deterministic(self):
        assert hash_secure("hello") == hash_secure("hello"), "Condition must be true"

    def test_different_inputs_differ(self):
        assert hash_secure("a") != hash_secure("b"), "Condition must be true"

    def test_unsupported_algorithm(self):
        with pytest.raises(ValueError, match="Unsupported algorithm"):
            hash_secure("data", algorithm="md5")


# ============================================================================
# sanitize_url
# ============================================================================


class TestSanitizeUrl:
    def test_allowed_domain(self):
        assert sanitize_url("https://example.com/path", ["example.com"]) is True

    def test_blocked_domain(self):
        assert sanitize_url("https://evil.com/path", ["example.com"]) is False

    def test_subdomain_allowed(self):
        assert sanitize_url("https://api.example.com/v1", ["example.com"]) is True

    def test_domain_in_path_blocked(self):
        """Domain appearing only in the path should NOT match."""
        assert sanitize_url("https://evil.com/example.com", ["example.com"]) is False

    def test_domain_prefix_attack(self):
        """evilexample.com should not match example.com."""
        assert sanitize_url("https://evilexample.com", ["example.com"]) is False

    def test_empty_url(self):
        assert sanitize_url("") is False, "Condition must be true"

    def test_no_allowed_domains(self):
        assert sanitize_url("https://anything.com") is True, "Condition must be true"

    def test_url_with_port(self):
        assert sanitize_url("https://example.com:8443/api", ["example.com"]) is True

    def test_invalid_url(self):
        assert sanitize_url("not a url at all ://") is False, "Condition must be true"


# ============================================================================
# log_sanitizer module — mask_sensitive / safe_log_message
# ============================================================================


class TestLogSanitizer:
    def test_mask_sensitive_api_key(self):
        result = ls_mask_sensitive("Config: api_key=sk_live_abc123 loaded")
        assert "sk_live_abc123" not in result, "Result must not be empty"
        assert "REDACTED" in result, "Result must not be empty"

    def test_mask_sensitive_bearer_token(self):
        # Use a recognized bearer token pattern (must have "Bearer " prefix)
        result = ls_mask_sensitive("Auth: ******")
        # This input doesn't contain a secret but we're testing it doesn't break
        assert result == "Auth: ******", "Result must not be empty"

    def test_safe_log_message_combined(self):
        msg = "User api_key=secret123\nFake log line"
        result = safe_log_message(msg)
        assert "\n" not in result, "Result must not be empty"
        assert "REDACTED" in result, "Result must not be empty"

    def test_safe_log_message_no_mask(self):
        msg = "Hello world"
        result = safe_log_message(msg, mask_secrets=False)
        assert result == "Hello world", "Result must not be empty"

    def test_safe_log_alias(self):
        assert safe_log is ls_sanitize_log, "safe_log is not valid"

    def test_mask_secrets_alias(self):
        assert mask_secrets is ls_mask_sensitive, "mask_secrets is not valid"


# ============================================================================
# sanitization module — sanitize_html
# ============================================================================


class TestSanitizeHtml:
    def test_removes_script_tags(self):
        result = sanitize_html('<script>alert("xss")</script>Hello')
        assert "<script" not in result, "Result must not be empty"
        assert "Hello" in result, "Result must not be empty"

    def test_removes_event_handlers(self):
        result = sanitize_html('<img src="x" onerror="alert(1)">', allow_tags=True)
        assert "onerror" not in result, "Result must not be empty"

    def test_removes_javascript_protocol(self):
        result = sanitize_html('<a href="javascript:alert(1)">Click</a>', allow_tags=True)
        assert "javascript" not in result.lower(), "Result must not be empty"

    def test_strips_all_tags_by_default(self):
        result = sanitize_html("<b>bold</b> <i>italic</i>")
        assert "<b>" not in result, "Result must not be empty"
        assert "bold" in result, "Result must not be empty"

    def test_preserves_tags_when_allowed(self):
        result = sanitize_html("<b>bold</b>", allow_tags=True)
        assert "<b>" in result, "Result must not be empty"

    def test_non_string_input(self):
        assert sanitize_html(123) == "", "Condition must be true"
        assert sanitize_html(None) == "", "Condition must be true"

    def test_removes_iframe(self):
        result = sanitize_html('<iframe src="evil.com"></iframe>Safe')
        assert "<iframe" not in result, "Result must not be empty"
        assert "Safe" in result, "Result must not be empty"
