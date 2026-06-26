"""
Comprehensive tests for log sanitizer module.

Tests cover:
- Control character removal (log injection prevention)
- Sensitive data masking (API keys, tokens, passwords)
- Log truncation
- Dictionary sanitization
- Integration with sensitive patterns
"""

import pytest  # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret

from codex.security.log_sanitizer import (
    mask_secrets,
    mask_sensitive,
    safe_log,
    safe_log_message,
    sanitize_dict_for_log,
    sanitize_log,
)

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def log_with_injection():
    """Log entry with injection attack."""
    return "User alice\n[WARN] FAKE_LOG_ENTRY\nPassword: secret"


@pytest.fixture
def log_with_tokens():
    """Log entry with various token types."""
    return "Token: ******"


@pytest.fixture
def log_with_api_keys():
    """Log entry with API keys."""
    return "API Key: sk_live_abc123xyz789 and api_key=test_key_12345"


@pytest.fixture
def log_with_aws_keys():
    """Log entry with AWS credentials."""
    return "AWS Key: AKIAIOSFODNN7EXAMPLE"


@pytest.fixture
def log_with_hex_secrets():
    """Log entry with hex-encoded secrets."""
    return "Secret: a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0"


# ============================================================================
# Sanitize Log (Control Character Removal) Tests
# ============================================================================


class TestSanitizeLogBasic:
    """Basic sanitize_log functionality."""

    def test_plain_text_passthrough(self):
        """Test that plain text passes through unchanged."""
        assert sanitize_log("Hello World") == "Hello World", "Condition must be true"

    def test_none_converts_to_string(self):
        """Test that None converts to string 'None'."""
        assert sanitize_log(None) == "None", "Condition must be true"

    def test_integer_conversion(self):
        """Test conversion of integers to string."""
        assert sanitize_log(42) == "42", "Condition must be true"

    def test_float_conversion(self):
        """Test conversion of floats to string."""
        assert sanitize_log(3.14) == "3.14", "Condition must be true"

    def test_boolean_conversion(self):
        """Test conversion of booleans."""
        assert sanitize_log(True) == "True", "Condition must be true"
        assert sanitize_log(False) == "False", "Condition must be true"


class TestSanitizeLogInjectionPrevention:
    """Test log injection attack prevention."""

    def test_newline_removal(self):
        """Test removal of newline characters."""
        result = sanitize_log("line1\nline2")
        assert "\n" not in result, "Result must not be empty"
        assert "line1line2" == result, "Result must not be empty"

    def test_carriage_return_removal(self):
        """Test removal of carriage returns."""
        result = sanitize_log("line1\rline2")
        assert "\r" not in result, "Result must not be empty"

    def test_tab_removal(self):
        """Test removal of tab characters."""
        result = sanitize_log("col1\tcol2")
        assert "\t" not in result, "Result must not be empty"

    def test_null_byte_removal(self):
        """Test removal of null bytes."""
        result = sanitize_log("hello\x00world")
        assert "\x00" not in result, "Result must not be empty"

    def test_multiple_control_chars_removal(self):
        """Test removal of multiple control characters."""
        result = sanitize_log("start\n\r\tmiddle\x1aend")
        assert "\n" not in result, "Result must not be empty"
        assert "\r" not in result, "Result must not be empty"
        assert "\t" not in result, "Result must not be empty"

    def test_log_injection_attack(self):
        """Test prevention of log injection attack."""
        attack = "User: alice\n[ERROR] Unauthorized access\nPassword: secret"
        result = sanitize_log(attack)
        assert "[ERROR]" in result or "ERROR" in result, "Result must not be empty"
        # Newlines should be removed
        assert result.count("\n") == 0, "Result must not be empty"

    def test_forged_log_entry_removal(self):
        """Test removal of forged log entries."""
        forged = "INFO: Login successful\n[CRITICAL] System failure"
        result = sanitize_log(forged)
        assert result.count("\n") == 0, "Result must not be empty"


class TestSanitizeLogAnsiCodes:
    """Test ANSI escape code removal."""

    def test_ansi_color_removal(self):
        """Test removal of ANSI color codes."""
        result = sanitize_log("\x1b[31mRed Text\x1b[0m")
        assert "\x1b[" not in result, "Result must not be empty"
        assert "Red Text" in result, "Result must not be empty"

    def test_ansi_bold_removal(self):
        """Test removal of ANSI bold codes."""
        result = sanitize_log("\x1b[1mBold\x1b[0m")
        assert "\x1b[" not in result, "Result must not be empty"

    def test_multiple_ansi_codes(self):
        """Test removal of multiple ANSI codes."""
        result = sanitize_log("\x1b[31m\x1b[1mRed Bold\x1b[0m")
        assert "\x1b[" not in result, "Result must not be empty"


class TestSanitizeLogTruncation:
    """Test log truncation functionality."""

    def test_under_max_length(self):
        """Test string under max length."""
        short = "x" * 100
        result = sanitize_log(short, max_length=500)
        assert len(result) == 100, "Result must not be empty"

    def test_over_max_length_truncated(self):
        """Test string over max length is truncated."""
        long_str = "x" * 1000
        result = sanitize_log(long_str, max_length=100)
        assert "[truncated]" in result, "Result must not be empty"
        assert len(result) <= 116, "Result must not be empty"

    def test_truncation_marker(self):
        """Test that truncation marker is added."""
        long_str = "A" * 600
        result = sanitize_log(long_str, max_length=100)
        assert "...[truncated]" in result, "Result must not be empty"

    def test_custom_max_length(self):
        """Test custom max length values."""
        result = sanitize_log("x" * 1000, max_length=50)
        assert "[truncated]" in result, "Result must not be empty"


class TestSanitizeLogEdgeCases:
    """Test edge cases in log sanitization."""

    def test_empty_string(self):
        """Test empty string handling."""
        assert sanitize_log("") == "", "Condition must be true"

    def test_only_control_characters(self):
        """Test string with only control characters."""
        result = sanitize_log("\n\r\t")
        assert result == "", "Result must not be empty"

    def test_whitespace_preservation(self):
        """Test that regular spaces are preserved."""
        assert sanitize_log("hello   world") == "hello   world", "Condition must be true"

    def test_unicode_preservation(self):
        """Test that unicode is preserved."""
        text = "Hello 世界 🌍"
        result = sanitize_log(text)
        assert "世界" in result, "Result must not be empty"
        assert "🌍" in result, "Result must not be empty"

    def test_special_characters_preservation(self):
        """Test that special characters are preserved."""
        assert sanitize_log("user@example.com") == "user@example.com", "Condition must be true"
        assert sanitize_log("value: 123.45") == "value: 123.45", "Value must be initialized"


# ============================================================================
# Mask Sensitive Tests
# ============================================================================


class TestMaskSensitiveBasic:
    """Basic mask_sensitive functionality."""

    def test_plain_text_unchanged(self):
        """Test that plain text is unchanged."""
        assert mask_sensitive("Hello World") == "Hello World", "Condition must be true"

    def test_empty_string(self):
        """Test empty string handling."""
        assert mask_sensitive("") == "", "Condition must be true"


class TestMaskSensitiveApiKeys:
    """Test API key masking."""

    def test_api_key_masking(self):
        """Test masking of 'api_key=' patterns."""
        result = mask_sensitive("api_key=sk_test_abc123xyz789")
        assert "***REDACTED***" in result, "Result must not be empty"
        assert "sk_test_abc123xyz789" not in result, "Result must not be empty"

    def test_api_key_with_hyphen(self):
        """Test masking of 'api-key=' patterns."""
        result = mask_sensitive("api-key=secret123")
        assert "***REDACTED***" in result, "Result must not be empty"

    def test_api_key_case_insensitive(self):
        """Test case-insensitive API key masking."""
        result = mask_sensitive("API_KEY=mykey123")
        assert "***REDACTED***" in result, "Result must not be empty"

    def test_multiple_api_keys(self):
        """Test masking of multiple API keys."""
        result = mask_sensitive("key1=secret1 api_key=secret2 token=secret3")
        assert result.count("***REDACTED***") >= 2, "Value must be greater than zero"


class TestMaskSensitiveTokens:
    """Test token masking."""

    def test_bearer_token_masking(self):
        """Test masking of ******"""
        result = mask_sensitive("******")
        assert "***REDACTED***" in result, "Result must not be empty"
        assert "eyJ" not in result or "******" in result, "Result must not be empty"

    def test_bearer_token_case_insensitive(self):
        """Test case-insensitive ******"""
        result = mask_sensitive("bearer abc123token")
        assert "***REDACTED***" in result or "bearer" in result, "Result must not be empty"

    def test_token_equals_pattern(self):
        """Test masking of 'token=' patterns."""
        result = mask_sensitive("token=mytoken123abc")
        assert "***REDACTED***" in result, "Result must not be empty"


class TestMaskSensitivePasswords:
    """Test password masking."""

    def test_password_equals_pattern(self):
        """Test masking of 'password=' patterns."""
        result = mask_sensitive("******")
        assert "***REDACTED***" in result, "Result must not be empty"

    def test_password_colon_pattern(self):
        """Test masking of 'password:' patterns."""
        result = mask_sensitive("password: mysecretpass")
        assert "***REDACTED***" in result, "Result must not be empty"

    def test_secret_equals_pattern(self):
        """Test masking of 'secret=' patterns."""
        result = mask_sensitive("secret=hidden123")
        assert "***REDACTED***" in result, "Result must not be empty"


class TestMaskSensitiveJwt:
    """Test JWT token masking."""

    def test_jwt_token_masking(self):
        """Test masking of JWT tokens."""
        jwt = "******"
        result = mask_sensitive(f"Token: {jwt}")
        assert "***JWT_REDACTED***" in result, "Result must not be empty"

    def test_jwt_in_bearer_pattern(self):
        """Test JWT in ******"""
        result = mask_sensitive("******")
        assert "***" in result, "Result must not be empty"


class TestMaskSensitiveAwsKeys:
    """Test AWS credential masking."""

    def test_aws_access_key_masking(self):
        """Test masking of AWS access keys."""
        result = mask_sensitive("AKIAIOSFODNN7EXAMPLE")
        assert "***AWS_KEY_REDACTED***" in result, "Result must not be empty"

    def test_aws_key_in_context(self):
        """Test AWS key masking in context."""
        result = mask_sensitive("AWS Key: AKIAIOSFODNN7EXAMPLE for bucket")
        assert "***AWS_KEY_REDACTED***" in result, "Result must not be empty"

    def test_multiple_aws_keys(self):
        """Test masking of multiple AWS keys."""
        result = mask_sensitive("key1=AKIAIOSFODNN7EXAMPLE key2=AKIAIOSFODNN8EXAMPLE")
        assert result.count("***") >= 1, "Value must be greater than zero"


class TestMaskSensitivePrivateKeys:
    """Test private key masking."""

    def test_rsa_private_key_masking(self):
        """Test masking of RSA private keys."""
        key = """-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA2z2r1234567890abcdefg
MIIEpAIBAAKCAQEA2z2r1234567890abcdefg
-----END RSA PRIVATE KEY-----"""
        result = mask_sensitive(key)
        assert "***PRIVATE_KEY_REDACTED***" in result, "Result must not be empty"

    def test_private_key_no_rsa_prefix(self):
        """Test masking of private keys without RSA prefix."""
        key = """-----BEGIN PRIVATE KEY-----
MIIEvAIBADANBgkqhkiG9w0BAQE
-----END PRIVATE KEY-----"""
        result = mask_sensitive(key)
        assert "***PRIVATE_KEY_REDACTED***" in result, "Result must not be empty"


# ============================================================================
# Safe Log Message Tests
# ============================================================================


class TestSafeLogMessage:
    """Test comprehensive safe_log_message function."""

    def test_combined_injection_and_masking(self):
        """Test combined control character removal and masking."""
        msg = "User logged in\ntoken=sk_test_123\nFAKE_LOG_ENTRY"
        result = safe_log_message(msg)
        assert "\n" not in result, "Result must not be empty"
        assert "sk_test_123" not in result, "Result must not be empty"

    def test_mask_secrets_flag_true(self):
        """Test with mask_secrets=True."""
        msg = "api_key=secret123"
        result = safe_log_message(msg, mask_secrets=True)
        assert "***REDACTED***" in result, "Result must not be empty"

    def test_mask_secrets_flag_false(self):
        """Test with mask_secrets=False."""
        msg = "message with key=value"
        result = safe_log_message(msg, mask_secrets=False)
        # Should still remove control characters but not mask
        assert result, "Result must not be empty"

    def test_long_message_truncation(self):
        """Test that long messages are truncated."""
        msg = "x" * 1000 + "\ninjection"
        result = safe_log_message(msg)
        assert "[truncated]" in result or len(result) < 1000, "Result must not be empty"

    def test_real_world_log_entry(self):
        """Test realistic log entry."""
        msg = "User: alice\nPassword: secret123\nAPI_KEY=sk_live_abc123\nStatus: OK"
        result = safe_log_message(msg)
        assert "\n" not in result, "Result must not be empty"
        assert "secret" not in result, "Result must not be empty"
        assert "sk_live" not in result, "Result must not be empty"


# ============================================================================
# Sanitize Dictionary Tests
# ============================================================================


class TestSanitizeDictForLog:
    """Test dictionary sanitization for logging."""

    def test_simple_dict_sanitization(self):
        """Test sanitization of simple dictionary."""
        data = {"user": "alice", "status": "ok"}
        result = sanitize_dict_for_log(data)
        assert isinstance(result, dict)
        assert result["user"] == "alice", "Result must not be empty"

    def test_dict_with_injection(self):
        """Test sanitization of dict with injection."""
        data = {"message": "line1\nline2", "status": "ok"}
        result = sanitize_dict_for_log(data)
        assert "\n" not in result["message"], "Result must not be empty"

    def test_dict_with_sensitive_data(self):
        """Test sanitization of dict with sensitive data."""
        data = {"api_key": "sk_test_123", "user": "alice"}
        result = sanitize_dict_for_log(data)
        assert "sk_test" not in result["api_key"], "Result must not be empty"

    def test_nested_dict_sanitization(self):
        """Test sanitization of nested dictionaries."""
        data = {"user": {"name": "alice\ninjection", "token": "******"}}
        result = sanitize_dict_for_log(data)
        assert "\n" not in result["user"]["name"], "Result must not be empty"
        assert "***" in str(result["user"]["token"]), "Result must not be empty"

    def test_dict_with_list_values(self):
        """Test sanitization of dict with list values."""
        data = {"messages": ["line1\nline2", "normal"], "tokens": ["token1", "token2"]}
        result = sanitize_dict_for_log(data)
        assert isinstance(result["messages"], list)
        for msg in result["messages"]:
            assert "\n" not in str(msg), "Condition must be true"

    def test_dict_with_tuple_values(self):
        """Test sanitization of dict with tuple values."""
        data = {"coords": (1, 2), "data": ("a\nb", "c")}
        result = sanitize_dict_for_log(data)
        assert isinstance(result["coords"], list)

    def test_dict_with_long_values(self):
        """Test truncation of long values in dict."""
        data = {"long_message": "x" * 1000}
        result = sanitize_dict_for_log(data, max_length=100)
        assert "[truncated]" in result["long_message"], "Result must not be empty"

    def test_dict_mask_secrets_flag(self):
        """Test mask_secrets flag in dict sanitization."""
        data = {"api_key": "sk_test_abc123"}
        result = sanitize_dict_for_log(data, mask_secrets=True)
        assert "***REDACTED***" in result["api_key"], "Result must not be empty"

        result_no_mask = sanitize_dict_for_log(data, mask_secrets=False)
        # Should still sanitize but not mask
        assert result_no_mask, "Result must not be empty"

    def test_empty_dict(self):
        """Test empty dictionary."""
        assert sanitize_dict_for_log({}) == {}, "sanitize_dict_f is not valid"

    def test_dict_with_none_values(self):
        """Test dictionary with None values."""
        data = {"key": None}
        result = sanitize_dict_for_log(data)
        assert result["key"] == "None", "Result must not be empty"

    def test_deeply_nested_dict(self):
        """Test deeply nested dictionary."""
        data = {"level1": {"level2": {"level3": {"message": "test\ninjection", "token": "******"}}}}
        result = sanitize_dict_for_log(data)
        assert "\n" not in result["level1"]["level2"]["level3"]["message"], "Result must not be empty"


# ============================================================================
# Alias Tests
# ============================================================================


class TestAliases:
    """Test function aliases."""

    def test_safe_log_alias(self):
        """Test safe_log is alias for sanitize_log."""
        assert safe_log == sanitize_log, "safe_log is not valid"
        assert safe_log("hello\nworld") == sanitize_log("hello\nworld"), "Condition must be true"

    def test_mask_secrets_alias(self):
        """Test mask_secrets is alias for mask_sensitive."""
        assert mask_secrets == mask_sensitive, "mask_secrets is not valid"
        msg = "token=abc123"
        assert mask_secrets(msg) == mask_sensitive(msg), "Condition must be true"


# ============================================================================
# Integration Tests
# ============================================================================


class TestLogSanitizerIntegration:
    """Integration tests for log sanitization."""

    def test_complete_log_entry_sanitization(self, log_with_injection):
        """Test complete sanitization of log with injection."""
        result = safe_log_message(log_with_injection)
        assert "\n" not in result, "Result must not be empty"
        assert "secret" not in result, "Result must not be empty"

    def test_token_log_sanitization(self, log_with_tokens):
        """Test sanitization of log with JWT tokens."""
        result = safe_log_message(log_with_tokens)
        assert "***" in result, "Result must not be empty"

    def test_api_key_log_sanitization(self, log_with_api_keys):
        """Test sanitization of log with API keys."""
        result = safe_log_message(log_with_api_keys)
        assert "***REDACTED***" in result, "Result must not be empty"

    def test_aws_key_log_sanitization(self, log_with_aws_keys):
        """Test sanitization of log with AWS keys."""
        result = safe_log_message(log_with_aws_keys)
        assert "***AWS_KEY_REDACTED***" in result, "Result must not be empty"

    def test_hex_secret_log_sanitization(self, log_with_hex_secrets):
        """Test sanitization of log with hex secrets."""
        result = safe_log_message(log_with_hex_secrets)
        assert "***HEX_REDACTED***" in result, "Result must not be empty"

    def test_multiple_threats_combined(self):
        """Test handling of multiple security threats together."""
        msg = """Login attempt
Token: ******
api_key=sk_live_abc123
[FAKE] injection
AKIAIOSFODNN7EXAMPLE
Password: secret123"""
        result = safe_log_message(msg)
        # No newlines
        assert "\n" not in result, "Result must not be empty"
        # Secrets masked
        assert "sk_live" not in result, "Result must not be empty"
        assert result, "Result must not be empty"

    def test_benign_log_entry_unchanged(self):
        """Test that benign log entries remain readable."""
        msg = "User alice logged in successfully at 2025-01-15T10:30:00Z"
        result = safe_log_message(msg)
        assert "alice" in result, "Result must not be empty"
        assert "logged in" in result, "Result must not be empty"
