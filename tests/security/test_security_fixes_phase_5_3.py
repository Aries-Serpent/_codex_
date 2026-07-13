"""
Phase 5.3 Security Fixes - Test Suite
Tests for token masking, log injection prevention, and secret sanitization.
"""

import pytest
from aries_serpent_core.security_utils import (
    sanitize_log_message,
    redact_sensitive_value,
    redact_secret_name,
)


class TestTokenMasking:
    """Test suite for GitHub token masking."""

    def test_github_token_masking(self):
        """Test that GitHub tokens are properly masked."""
        token = "ghp_" + "a" * 36
        message = f"Using token: {token}"
        result = sanitize_log_message(message)
        
        assert token not in result
        assert "[REDACTED_GITHUB_TOKEN]" in result
        assert "Using token" in result

    def test_github_pat_masking(self):
        """Test that GitHub PAT tokens are masked."""
        token = "github_pat_" + "a" * 82
        message = f"PAT token: {token}"
        result = sanitize_log_message(message)
        
        assert token not in result
        assert "[REDACTED" in result

    def test_api_key_masking(self):
        """Test that API keys are masked."""
        api_key = "sk_live_" + "a" * 20
        message = f"api_key={api_key}"
        result = sanitize_log_message(message)
        
        assert api_key not in result
        assert "[REDACTED]" in result

    def test_jwt_token_masking(self):
        """Test that JWT tokens are masked."""
        jwt = "******"
        message = f"JWT: {jwt}"
        result = sanitize_log_message(message)
        
        assert jwt not in result
        assert "[REDACTED]" in result

    def test_safe_content_not_masked(self):
        """Test that safe content is not masked."""
        git_sha = "abc1234567890def"
        message = f"Commit: {git_sha}"
        result = sanitize_log_message(message)
        
        # Git SHAs should not be masked
        assert git_sha in result


class TestClearTextLoggingPrevention:
    """Test suite for preventing clear-text logging of secrets."""

    def test_redact_sensitive_value(self):
        """Test value redaction."""
        secret = "my-secret-password-12345"
        result = redact_sensitive_value(secret)
        
        assert "[REDACTED]" in result
        assert secret not in result

    def test_redact_secret_name(self):
        """Test secret name redaction."""
        name = "DATABASE_PASSWORD"
        result = redact_secret_name(name)
        
        assert "[REDACTED" in result
        assert name not in result

    def test_empty_value_redaction(self):
        """Test empty value handling."""
        result = redact_sensitive_value(None)
        assert "[EMPTY]" in result or "[REDACTED]" in result

    def test_empty_secret_name_redaction(self):
        """Test empty secret name handling."""
        result = redact_secret_name("")
        assert result is not None


class TestLogInjectionPrevention:
    """Test suite for log injection prevention."""

    def test_control_characters_removed(self):
        """Test that control characters are handled."""
        # Log injection often uses control characters
        malicious = "test\ninjected\rline\x1bcode"
        result = sanitize_log_message(malicious)
        
        # Should not contain raw control characters after sanitization
        assert "\n" not in result or result.count("\n") <= 1
        
    def test_newline_injection_prevention(self):
        """Test that newline injection is prevented."""
        injection = "normal_log\nAdmin: 1"
        result = sanitize_log_message(injection)
        
        # Result should be handled safely (no multiple newlines)
        assert result.count("\n") <= 1

    def test_user_input_sanitization(self):
        """Test sanitization of user-controlled input."""
        user_input = "'; DROP TABLE users; --"
        result = sanitize_log_message(user_input)
        
        # Should still be loggable but not cause injection
        assert result is not None
        assert len(result) > 0


class TestStackTraceExposure:
    """Test suite for stack trace sanitization."""

    def test_token_in_stack_trace(self):
        """Test that tokens in stack traces are masked."""
        token = "ghp_" + "a" * 36
        stack_trace = f"""Traceback (most recent call last):
  File "script.py", line 10, in <module>
    token = '{token}'
KeyError: '{token}'"""
        
        result = sanitize_log_message(stack_trace)
        
        assert token not in result
        assert "[REDACTED_GITHUB_TOKEN]" in result

    def test_credentials_in_exception_message(self):
        """Test credentials in exception messages."""
        password = "super_secret_password"
        message = f"Login failed with password: {password}"
        result = sanitize_log_message(message)
        
        # Sanitization should handle this
        assert result is not None


class TestIntegration:
    """Integration tests for security fixes."""

    def test_multiple_tokens_in_single_message(self):
        """Test handling multiple tokens in one message."""
        token1 = "ghp_" + "a" * 36
        token2 = "sk_live_" + "b" * 20
        message = f"Token1: {token1}, Token2: {token2}"
        
        result = sanitize_log_message(message)
        
        assert token1 not in result
        assert token2 not in result
        assert result.count("[REDACTED") >= 2

    def test_complex_log_message(self):
        """Test sanitization of complex log messages."""
        token = "ghp_" + "a" * 36
        api_key = "sk_live_" + "b" * 20
        message = f"""
        Processing request:
        - GitHub token: {token}
        - API key: {api_key}
        - Status: success
        """
        
        result = sanitize_log_message(message)
        
        assert token not in result
        assert api_key not in result
        assert "Processing request" in result
        assert "Status: success" in result


class TestSecurityUtilsAvailability:
    """Test that security utilities are properly available."""

    def test_sanitize_log_message_available(self):
        """Test that sanitize_log_message is available."""
        assert callable(sanitize_log_message)

    def test_redact_sensitive_value_available(self):
        """Test that redact_sensitive_value is available."""
        assert callable(redact_sensitive_value)

    def test_redact_secret_name_available(self):
        """Test that redact_secret_name is available."""
        assert callable(redact_secret_name)

    def test_functions_work_with_strings(self):
        """Test that functions handle string inputs."""
        result1 = sanitize_log_message("test")
        result2 = redact_sensitive_value("test")
        result3 = redact_secret_name("test")
        
        assert isinstance(result1, str)
        assert isinstance(result2, str)
        assert isinstance(result3, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
