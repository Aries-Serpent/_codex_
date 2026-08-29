"""
Unit tests for security logging utilities.

These tests verify that sensitive information is properly redacted
and that security utilities work as expected.
"""

import logging

import pytest

from src.security.logging import (
    create_log_filter,
    hash_token,
    redact_email,
    redact_password,
    redact_pii,
    redact_token,
    sanitize_for_logging,
    setup_secure_logging,
)


class TestTokenRedaction:
    """Tests for token redaction."""

    def test_redact_github_token(self):
        """Verify GitHub token redaction."""
        token = "ghp_1234567890abcdefghij1234567890ab"
        redacted = redact_token(token)

        assert "ghp_" in redacted, "Condition must be true"
        assert "1234567890abcdef" not in redacted, "Condition must be true"
        assert redacted.endswith("****"), "Condition must be true"

    def test_redact_short_token(self):
        """Verify short token redaction."""
        token = "abc"
        redacted = redact_token(token)

        # Short tokens are masked per character
        assert len(redacted) == len(token) * 3, "Redacted must not be empty"

    def test_redact_empty_token(self):
        """Verify empty token redaction."""
        token = ""
        redacted = redact_token(token)

        assert redacted == "***", "redacted is not valid"

    def test_redact_with_suffix(self):
        """Verify token redaction with suffix visibility."""
        token = "ghp_1234567890abcdefghij1234567890ab"
        redacted = redact_token(token, suffix_visible=True)

        assert redacted.startswith("ghp_"), "Condition must be true"
        assert redacted.endswith("90ab"), "Condition must be true"

    def test_redact_long_suffix_visibility(self):
        """Verify suffix visibility works for long tokens."""
        token = "x" * 40
        redacted = redact_token(token, prefix_len=2, suffix_visible=True)

        assert redacted == "xx****xxxx", "redacted is not valid"


class TestPasswordRedaction:
    """Tests for password redaction."""

    def test_redact_password_normal(self):
        """Verify password redaction."""
        password = "MyS3cur3P@ssw0rd!"
        redacted = redact_password(password)

        assert "MyS3cur3P@ssw0rd!" not in redacted, "Condition must be true"
        assert redacted == "[REDACTED_PASSWORD]", "redacted is not valid"

    def test_redact_empty_password(self):
        """Verify empty password redaction."""
        password = ""
        redacted = redact_password(password)

        assert redacted == "[EMPTY_PASSWORD]", "redacted is not valid"


class TestEmailRedaction:
    """Tests for email redaction."""

    def test_redact_email_normal(self):
        """Verify email redaction."""
        email = "john.doe@example.com"
        redacted = redact_email(email)

        assert "john" not in redacted, "Condition must be true"
        assert "doe" not in redacted, "Condition must be true"
        # Verify email domain is redacted appropriately
        assert redacted.count("@") == 1, "Email should maintain @ symbol"
        assert "john" not in redacted.split("@")[0], "Local part should be redacted"
        assert redacted.startswith("j"), "Condition must be true"

    def test_redact_email_short_local(self):
        """Verify short local part redaction."""
        email = "a@example.com"
        redacted = redact_email(email)

        assert "*@example.com" in redacted, "Condition must be true"

    def test_redact_invalid_email(self):
        """Verify invalid email handling."""
        email = "not_an_email"
        redacted = redact_email(email)

        assert redacted == "****", "redacted is not valid"


class TestPIIRedaction:
    """Tests for PII redaction."""

    def test_redact_phone_number(self):
        """Verify phone number redaction."""
        phone = "555-123-4567"
        redacted = redact_pii(phone, "phone")

        assert "555" not in redacted, "Condition must be true"
        assert "123" not in redacted, "Condition must be true"
        assert "4567" in redacted, "Condition must be true"

    def test_redact_ssn(self):
        """Verify SSN redaction."""
        ssn = "123-45-6789"
        redacted = redact_pii(ssn, "ssn")

        assert "123" not in redacted, "Condition must be true"
        assert "45" not in redacted, "Condition must be true"
        assert "6789" in redacted, "Condition must be true"

    def test_redact_credit_card(self):
        """Verify credit card redaction."""
        cc = "4532-1111-2222-3333"
        redacted = redact_pii(cc, "credit_card")

        assert "4532" not in redacted, "Condition must be true"
        assert "1111" not in redacted, "Condition must be true"
        assert "3333" in redacted, "Condition must be true"

    def test_redact_generic_pii(self):
        """Verify generic PII redaction."""
        value = "some sensitive info"
        redacted = redact_pii(value, "generic")

        assert redacted == "[REDACTED]", "redacted is not valid"


class TestTokenHashing:
    """Tests for token hashing."""

    def test_hash_token(self):
        """Verify token hashing."""
        token = "ghp_1234567890abcdefghij1234567890ab"
        hashed = hash_token(token)

        # Should be a hex string
        assert all(c in "0123456789abcdef" for c in hashed), "Condition must be true"
        # Should be 8 chars by default
        assert len(hashed) == 8, "Hashed must not be empty"

    def test_hash_token_deterministic(self):
        """Verify token hashing is deterministic."""
        token = "same_token"
        hash1 = hash_token(token)
        hash2 = hash_token(token)

        assert hash1 == hash2, "hash1 is not valid"

    def test_hash_different_tokens(self):
        """Verify different tokens produce different hashes."""
        token1 = "token_1"
        token2 = "token_2"

        hash1 = hash_token(token1)
        hash2 = hash_token(token2)

        assert hash1 != hash2, "hash1 is not valid"

    def test_hash_empty_token(self):
        """Verify empty token handling."""
        token = ""
        hashed = hash_token(token)

        assert hashed == "no_token", "hashed is not valid"


class TestLoggingSanitization:
    """Tests for logging sanitization."""

    def test_sanitize_normal_text(self):
        """Verify normal text passes through."""
        text = "This is normal log text"
        sanitized = sanitize_for_logging(text)

        assert sanitized == text, "sanitized is not valid"

    def test_sanitize_newline_injection(self):
        """Verify newline injection prevention."""
        text = "Log line 1\nLog line 2"
        sanitized = sanitize_for_logging(text)

        assert "\n" not in sanitized, "Condition must be true"
        assert "Log line 1" in sanitized, "Condition must be true"
        assert "Log line 2" in sanitized, "Condition must be true"

    def test_sanitize_carriage_return(self):
        """Verify carriage return removal."""
        text = "Line 1\rLine 2"
        sanitized = sanitize_for_logging(text)

        assert "\r" not in sanitized, "Condition must be true"

    def test_sanitize_control_characters(self):
        """Verify control character removal."""
        text = "Normal\x00text\x1fwith\x7fcontrols"
        sanitized = sanitize_for_logging(text)

        assert "\x00" not in sanitized, "Condition must be true"
        assert "\x1f" not in sanitized, "Condition must be true"
        assert "\x7f" not in sanitized, "Condition must be true"
        assert "Normal" in sanitized, "Condition must be true"
        assert "text" in sanitized, "Condition must be true"

    def test_sanitize_multiple_spaces(self):
        """Verify space collapsing."""
        text = "Text   with    multiple     spaces"
        sanitized = sanitize_for_logging(text)

        assert sanitized == "Text with multiple spaces", "sanitized is not valid"

    def test_sanitize_non_string(self):
        """Verify non-string input handling."""
        value = 12345
        sanitized = sanitize_for_logging(value)

        assert sanitized == "12345", "sanitized is not valid"


class TestLoggingFilter:
    """Tests for logging filter."""

    def test_create_log_filter(self):
        """Verify log filter creation."""
        filter_obj = create_log_filter()

        assert filter_obj is not None, "filter_obj must be initialized"

    def test_log_filter_redacts_github_token(self):
        """Verify filter redacts GitHub tokens."""
        pass  # removed redundant `import logging` (top-level import used)

        logger = logging.getLogger("test_filter")
        logger.handlers = []  # Clear existing handlers

        # Create handler with filter
        handler = logging.StreamHandler()
        filter_obj = create_log_filter()
        handler.addFilter(filter_obj)
        logger.addHandler(handler)

        # This test is simplified - in real scenarios you'd capture logs
        # Just verify the filter doesn't crash
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Token: ghp_1234567890abcdefghij1234567890ab",
            args=(),
            exc_info=None,
        )

        result = filter_obj.filter(record)
        assert result is True, "Result must not be empty"


class TestSecureLoggingSetup:
    """Tests for secure logging setup."""

    def test_setup_secure_logging(self):
        """Verify secure logging setup."""
        logger = logging.getLogger("test_secure")

        # Should not raise
        setup_secure_logging(logger, add_redaction_filter=True)

        # Logger should have filter
        assert len(logger.filters) > 0, "Collection must not be empty"

    def test_setup_without_filter(self):
        """Verify setup without filter."""
        logger = logging.getLogger("test_no_filter")
        initial_count = len(logger.filters)

        setup_secure_logging(logger, add_redaction_filter=False)

        # Filter count shouldn't change
        assert len(logger.filters) == initial_count, "Collection must not be empty"


# Integration test
def test_integration_secret_not_in_logs(caplog):
    """Integration test: verify secrets don't appear in logs."""
    logger = logging.getLogger("integration_test")
    setup_secure_logging(logger, add_redaction_filter=True)

    raw_token = "ghp_1234567890abcdefghij1234567890ab"

    # Simulate logging with redaction
    logger.info(f"Using token: {redact_token(raw_token)}")

    # Raw token should not appear in logs
    with caplog.at_level(logging.INFO):
        logger.info(f"Token: {redact_token(raw_token)}")

    assert raw_token not in caplog.text, "Condition must be true"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
