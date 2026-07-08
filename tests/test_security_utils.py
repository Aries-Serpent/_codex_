"""
Unit tests for security utilities module.
Tests all redaction and sanitization functions.
"""

import pytest

from codex.security_utils import (
    redact_dict_with_secret_keys,
    redact_secret_name,
    redact_sensitive_value,
    safe_secret_reference,
    sanitize_log_message,
)


class TestRedactSensitiveValue:
    """Test redact_sensitive_value function.""" # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret

    def test_redact_simple_value(self):
        """Test basic redaction of sensitive value."""
        result = redact_sensitive_value("my-secret-key-12345")
        assert result == "[REDACTED]", "Result must not be empty"

    def test_redact_empty_value(self):
        """Test redaction of empty value."""
        result = redact_sensitive_value("")
        assert result == "[EMPTY]", "Result must not be empty"

    def test_redact_none_value(self):
        """Test redaction of None value."""
        result = redact_sensitive_value(None)
        assert result == "[EMPTY]", "Result must not be empty"

    def test_redact_with_preview_disabled(self):
        """Test that preview is disabled by default (production safety)."""
        result = redact_sensitive_value("my-secret-key-12345", show_preview=False)
        assert result == "[REDACTED]", "Result must not be empty"
        assert "my-s" not in result, "Result must not be empty"
        assert "2345" not in result, "Result must not be empty"

    def test_redact_with_preview_enabled_long_value(self):
        """Test preview mode for debugging (DEV ONLY)."""
        result = redact_sensitive_value("my-secret-key-12345", show_preview=True)
        assert "my-s" in result, "Result must not be empty"
        assert "[REDACTED]" in result, "Result must not be empty"
        assert "2345" in result, "Result must not be empty"

    def test_redact_with_preview_short_value(self):
        """Test preview mode with short value (< 8 chars)."""
        result = redact_sensitive_value("short", show_preview=True)
        assert result == "[REDACTED]", "Result must not be empty"


class TestRedactSecretName:
    """Test redact_secret_name function."""

    def test_redact_generic_secret_name(self):
        """Test redaction of generic secret name."""
        result = redact_secret_name("API_KEY")
        assert result == "[REDACTED_SECRET_NAME]", "Result must not be empty"

    def test_redact_sensitive_secret_name(self):
        """Test full redaction of sensitive secret names."""
        sensitive_names = [
            "PROD_DATABASE_PASSWORD",
            "AWS_SECRET_ACCESS_KEY",
            "PRIVATE_KEY",
            "JWT_SECRET",
        ]
        for name in sensitive_names:
            result = redact_secret_name(name)
            assert result == "[REDACTED_SECRET_NAME]", "Result must not be empty"

    def test_redact_empty_secret_name(self):
        """Test redaction of empty secret name."""
        result = redact_secret_name("")
        assert result == "[UNNAMED_SECRET]", "Result must not be empty"

    def test_redact_none_secret_name(self):
        """Test redaction of None secret name."""
        result = redact_secret_name(None)
        assert result == "[UNNAMED_SECRET]", "Result must not be empty"


class TestRedactDictWithSecretKeys:
    """Test redact_dict_with_secret_keys function."""

    def test_redact_dict_with_multiple_secrets(self):
        """Test redaction of dictionary with multiple secret keys."""
        data = {
            "GITHUB_TOKEN": "ghp_1234567890",
            "API_KEY": "sk-1234567890",
            "DATABASE_URL": "postgresql://user:pass@host/db",
        }
        result = redact_dict_with_secret_keys(data)

        assert len(result) == 3, "Result must not be empty"
        assert "secret_1" in result, "Result must not be empty"
        assert "secret_2" in result, "Result must not be empty"
        assert "secret_3" in result, "Result must not be empty"
        assert "GITHUB_TOKEN" not in result, "Result must not be empty"
        assert "API_KEY" not in result, "Result must not be empty"
        assert "DATABASE_URL" not in result, "Result must not be empty"

    def test_redact_empty_dict(self):
        """Test redaction of empty dictionary."""
        result = redact_dict_with_secret_keys({})
        assert result == {}, "Result must not be empty"

    def test_redact_none_dict(self):
        """Test redaction of None dictionary."""
        result = redact_dict_with_secret_keys(None)
        assert result == {}, "Result must not be empty"

    def test_redact_dict_preserves_count(self):
        """Test that redaction preserves the count of secrets."""
        data = {
            "SECRET_1": "value1",
            "SECRET_2": "value2",
            "SECRET_3": "value3",
            "SECRET_4": "value4",
            "SECRET_5": "value5",
        }
        result = redact_dict_with_secret_keys(data)
        assert len(result) == 5, "Result must not be empty"


class TestSanitizeLogMessage:
    """Test sanitize_log_message function."""

    def test_sanitize_github_token(self):
        """Test sanitization of GitHub token in log message."""
        message = "Using token: ghp_1234567890abcdefghijklmnopqrstuvwxyz"
        result = sanitize_log_message(message)
        assert "ghp_1234567890abcdefghijklmnopqrstuvwxyz" not in result, "Result must not be empty"
        assert "[REDACTED" in result, "Result must not be empty"

    def test_sanitize_api_key(self):
        """Test sanitization of API key in log message."""
        message = "API Key: sk-1234567890abcdefghijklmnopqrstuvwxyz"
        result = sanitize_log_message(message)
        assert "sk-1234567890abcdefghijklmnopqrstuvwxyz" not in result, "Result must not be empty"
        assert "[REDACTED]" in result, "Result must not be empty"

    def test_sanitize_jwt_token(self):
        """Test sanitization of JWT token in log message."""
        message = "JWT: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.abc123"
        result = sanitize_log_message(message)
        assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in result, "Result must not be empty"
        assert "[REDACTED]" in result, "Result must not be empty"

    def test_sanitize_base64_secret(self):
        """Test sanitization of base64-encoded secret."""
        message = "Secret: YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXoxMjM0NTY3ODkwYWJjZGVmZ2hpamtsbW5vcA=="
        result = sanitize_log_message(message)
        # Base64 string longer than 40 chars should be redacted
        assert "[REDACTED" in result, "Result must not be empty"

    def test_sanitize_clean_message(self):
        """Test that clean messages are not modified."""
        message = "Operation completed successfully"
        result = sanitize_log_message(message)
        assert result == message, "Result must not be empty"

    def test_sanitize_multiple_secrets(self):
        """Test sanitization of multiple secrets in one message."""
        message = "Token: ghp_abc123 and Key: sk-xyz789"
        result = sanitize_log_message(message)
        assert "ghp_abc123" not in result, "Result must not be empty"
        assert "sk-xyz789" not in result, "Result must not be empty"
        assert result.count("[REDACTED") >= 2, "Value must be greater than zero"


class TestSafeSecretReference:
    """Test safe_secret_reference function."""

    def test_safe_reference_generic_name(self):
        """Test safe reference for generic secret name."""
        result = safe_secret_reference("MY_API_KEY")
        assert "MY_API_KEY" in result, "Result must not be empty"
        assert result == "secret: MY_API_KEY", "Result must not be empty"

    def test_safe_reference_sensitive_name(self):
        """Test safe reference for sensitive secret name."""
        result = safe_secret_reference("PROD_DATABASE_PASSWORD")
        assert "PROD_DATABASE_PASSWORD" not in result, "Result must not be empty"
        assert "[REDACTED_SECRET_NAME]" in result, "Result must not be empty"

    def test_safe_reference_with_operation(self):
        """Test safe reference with operation parameter."""
        result = safe_secret_reference("verify", operation="check")
        assert "verify" in result or "[REDACTED" in result, "Result must not be empty"

    def test_safe_reference_empty_name(self):
        """Test safe reference with empty name."""
        result = safe_secret_reference("")
        assert "[EMPTY]" in result, "Result must not be empty"


class TestSecurityUtilsIntegration:
    """Integration tests for security utilities."""

    def test_end_to_end_secret_logging(self):
        """Test complete flow of secret logging with redaction."""
        # Simulate receiving secrets from API
        secrets_data = {
            "GITHUB_TOKEN": "ghp_1234567890",
            "CODEX_MASTER_KEY": "abc123def456",
            "GOOGLE_CLIENT_SECRET": "GOCSPX-secret123",
        }

        # Redact dictionary keys
        redacted_dict = redact_dict_with_secret_keys(secrets_data)

        # Create log message
        message = f"Configured {len(redacted_dict)} secrets"

        # Sanitize any leaked values
        safe_message = sanitize_log_message(message)

        # Verify no sensitive data in final message
        assert "ghp_1234567890" not in safe_message, "Condition must be true"
        assert "abc123def456" not in safe_message, "Condition must be true"
        assert "GOCSPX-secret123" not in safe_message, "Condition must be true"
        assert "GITHUB_TOKEN" not in str(redacted_dict), "Condition must be true"
        assert "3 secrets" in safe_message or "Configured 3" in safe_message, "Condition must be true"

    def test_codeql_alert_prevention(self):
        """Test that security utils prevent CodeQL clear-text logging alerts."""
        # Simulate the exact pattern that triggered CodeQL alerts
        secrets_result = {
            "secret1": "value1",
            "secret2": "value2",
            "secret3": "value3",
            "secret4": "value4",
        }

        # Apply redaction (as fixed in the codebase)
        redacted_result = redact_dict_with_secret_keys(secrets_result) if secrets_result else {}
        secret_count = len(redacted_result)

        # Create log message using only the count (not the dict)
        log_message = f"Secrets configuration complete: {secret_count} items processed"

        # Verify no secret names in log message
        assert "secret1" not in log_message, "Condition must be true"
        assert "secret2" not in log_message, "Condition must be true"
        assert "value1" not in log_message, "Value must be initialized"
        assert "value2" not in log_message, "Value must be initialized"

        # Verify redacted dict doesn't contain original keys
        for key in redacted_result:
            assert key.startswith("secret_"), "Condition must be true"

    def test_production_safety_defaults(self):
        """Test that production safety is the default behavior."""
        # show_preview should default to False
        result = redact_sensitive_value("my-secret-key-12345")
        assert "my-s" not in result, "Result must not be empty"
        assert "2345" not in result, "Result must not be empty"

        # Verify the default is safe for production
        assert result == "[REDACTED]", "Result must not be empty"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_unicode_in_secret_value(self):
        """Test redaction of unicode characters in secret."""
        result = redact_sensitive_value("🔑secret🔐key🗝️")
        assert result == "[REDACTED]", "Result must not be empty"

    def test_very_long_secret_value(self):
        """Test redaction of very long secret (> 1000 chars)."""
        long_secret = "a" * 10000
        result = redact_sensitive_value(long_secret)
        assert result == "[REDACTED]", "Result must not be empty"

    def test_special_characters_in_secret_name(self):
        """Test redaction of secret name with special characters."""
        result = redact_secret_name("MY-API_KEY.v2")
        assert "MY-API_KEY.v2" in result or "[REDACTED" in result, "Result must not be empty"

    def test_nested_dict_with_secrets(self):
        """Test that nested dicts are handled (current impl is flat)."""
        data = {"outer": {"inner": "secret_value"}}
        result = redact_dict_with_secret_keys(data)
        # Current implementation handles flat dicts
        # Nested values are preserved but keys are redacted
        assert len(result) == 1, "Result must not be empty"

    def test_sanitize_multiline_log(self):
        """Test sanitization of multiline log message."""
        message = """
        Starting operation
        Token: ghp_1234567890
        Processing...
        Key: sk-abcdefghij
        Complete
        """
        result = sanitize_log_message(message)
        assert "ghp_1234567890" not in result, "Result must not be empty"
        assert "sk-abcdefghij" not in result, "Result must not be empty"
        assert "[REDACTED]" in result, "Result must not be empty"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
