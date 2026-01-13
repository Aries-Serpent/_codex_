"""
Tests for security utilities module.
Validates redaction and sanitization functions for sensitive data.
"""

import pytest
from codex.security_utils import (
    redact_sensitive_value,
    redact_secret_name,
    sanitize_log_message,
    safe_secret_reference
)


class TestRedactSensitiveValue:
    """Test redaction of sensitive values."""
    
    def test_redact_without_preview(self):
        """Test basic redaction without preview."""
        result = redact_sensitive_value("my-secret-key-12345")
        assert result == '[REDACTED]'
    
    def test_redact_with_preview(self):
        """Test redaction with preview showing first/last chars."""
        result = redact_sensitive_value("my-secret-key-12345", show_preview=True)
        assert result.startswith("my-s")
        assert result.endswith("2345")
        assert "[REDACTED]" in result
    
    def test_redact_empty_value(self):
        """Test redaction of empty value."""
        result = redact_sensitive_value("")
        assert result == '[EMPTY]'
    
    def test_redact_short_value_with_preview(self):
        """Test that short values are fully redacted even with preview."""
        result = redact_sensitive_value("short", show_preview=True)
        assert result == '[REDACTED]'


class TestRedactSecretName:
    """Test redaction of secret names."""
    
    def test_redact_codex_prefix(self):
        """Test that all secrets are consistently redacted."""
        result = redact_secret_name("CODEX_MASTER_KEY")
        assert result == "secret:[REDACTED]"
    
    def test_redact_github_prefix(self):
        """Test that all secrets are consistently redacted."""
        result = redact_secret_name("GITHUB_TOKEN")
        assert result == "secret:[REDACTED]"
    
    def test_redact_custom_secret(self):
        """Test that custom secrets are redacted consistently."""
        result = redact_secret_name("CUSTOM_API_KEY")
        assert result == "secret:[REDACTED]"
    
    def test_redact_empty_name(self):
        """Test redaction of empty secret name."""
        result = redact_secret_name("")
        assert result == '[UNNAMED_SECRET]'


class TestSanitizeLogMessage:
    """Test sanitization of log messages."""
    
    def test_sanitize_github_token(self):
        """Test that GitHub tokens are redacted."""
        message = "Using token: ghp_abc123def456ghi789jkl012mno345pqr678"
        result = sanitize_log_message(message)
        assert "ghp_" not in result
        assert "[REDACTED_GITHUB_TOKEN]" in result
    
    def test_sanitize_oauth_token(self):
        """Test that OAuth tokens are redacted."""
        message = "OAuth: gho_abc123def456ghi789jkl012mno345pqr678"
        result = sanitize_log_message(message)
        assert "gho_" not in result
        assert "[REDACTED_OAUTH_TOKEN]" in result
    
    def test_sanitize_long_base64(self):
        """Test that long base64-like strings are redacted."""
        message = "Key: YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXoxMjM0NTY3ODkw"
        result = sanitize_log_message(message)
        assert "[REDACTED_TOKEN]" in result
    
    def test_sanitize_normal_message(self):
        """Test that normal messages are not affected."""
        message = "Processing completed successfully"
        result = sanitize_log_message(message)
        assert result == message


class TestSafeSecretReference:
    """Test safe secret reference generation."""
    
    def test_reference_without_operation(self):
        """Test basic secret reference."""
        result = safe_secret_reference("MASTER_KEY")
        assert result == "secret"
    
    def test_reference_with_operation(self):
        """Test secret reference with operation."""
        result = safe_secret_reference("MASTER_KEY", "verify")
        assert result == "secret (verify)"
    
    def test_reference_set_operation(self):
        """Test secret reference for set operation."""
        result = safe_secret_reference("API_TOKEN", "set")
        assert result == "secret (set)"


def test_module_warning_comment():
    """Test that the module has proper security warnings."""
    import codex.security_utils as module
    
    # Check that module has security warnings in docstring
    assert module.__doc__ is not None
    assert "sensitive" in module.__doc__.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
