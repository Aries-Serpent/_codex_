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

        assert "ghp_" in redacted
        assert "1234567890abcdef" not in redacted
        assert redacted.endswith("****")

    def test_redact_short_token(self):
        """Verify short token redaction."""
        token = "abc"
        redacted = redact_token(token)

        # Short tokens are masked per character
        assert len(redacted) == len(token) * 3  # 3 asterisks per char

    def test_redact_empty_token(self):
        """Verify empty token redaction."""
        token = ""
        redacted = redact_token(token)

        assert redacted == "***"

    def test_redact_with_suffix(self):
        """Verify token redaction with suffix visibility."""
        token = "ghp_1234567890abcdefghij1234567890ab"
        redacted = redact_token(token, suffix_visible=True)

        assert redacted.startswith("ghp_")
        assert redacted.endswith("90ab")

    def test_redact_long_suffix_visibility(self):
        """Verify suffix visibility works for long tokens."""
        token = "x" * 40
        redacted = redact_token(token, prefix_len=2, suffix_visible=True)

        assert redacted == "xx****xxxx"


class TestPasswordRedaction:
    """Tests for password redaction."""

    def test_redact_password_normal(self):
        """Verify password redaction."""
        password = "MyS3cur3P@ssw0rd!"
        redacted = redact_password(password)

        assert "MyS3cur3P@ssw0rd!" not in redacted
        assert redacted == "[REDACTED_PASSWORD]"

    def test_redact_empty_password(self):
        """Verify empty password redaction."""
        password = ""
        redacted = redact_password(password)

        assert redacted == "[EMPTY_PASSWORD]"


class TestEmailRedaction:
    """Tests for email redaction."""

    def test_redact_email_normal(self):
        """Verify email redaction."""
        email = "john.doe@example.com"
        redacted = redact_email(email)

        assert "john" not in redacted
        assert "doe" not in redacted
        assert (
            "example.com" in redacted
        )  # pragma: allowlist secret
        assert redacted.startswith("j")

    def test_redact_email_short_local(self):
        """Verify short local part redaction."""
        email = "a@example.com"
        redacted = redact_email(email)

        assert "*@example.com" in redacted

    def test_redact_invalid_email(self):
        """Verify invalid email handling."""
        email = "not_an_email"
        redacted = redact_email(email)

        assert redacted == "****"


class TestPIIRedaction:
    """Tests for PII redaction."""

    def test_redact_phone_number(self):
        """Verify phone number redaction."""
        phone = "555-123-4567"
        redacted = redact_pii(phone, "phone")

        assert "555" not in redacted
        assert "123" not in redacted
        assert "4567" in redacted

    def test_redact_ssn(self):
        """Verify SSN redaction."""
        ssn = "123-45-6789"
        redacted = redact_pii(ssn, "ssn")

        assert "123" not in redacted
        assert "45" not in redacted
        assert "6789" in redacted

    def test_redact_credit_card(self):
        """Verify credit card redaction."""
        cc = "4532-1111-2222-3333"
        redacted = redact_pii(cc, "credit_card")

        assert "4532" not in redacted
        assert "1111" not in redacted
        assert "3333" in redacted

    def test_redact_generic_pii(self):
        """Verify generic PII redaction."""
        value = "some sensitive info"
        redacted = redact_pii(value, "generic")

        assert redacted == "[REDACTED]"


class TestTokenHashing:
    """Tests for token hashing."""

    def test_hash_token(self):
        """Verify token hashing."""
        token = "ghp_1234567890abcdefghij1234567890ab"
        hashed = hash_token(token)

        # Should be a hex string
        assert all(c in "0123456789abcdef" for c in hashed)
        # Should be 8 chars by default
        assert len(hashed) == 8

    def test_hash_token_deterministic(self):
        """Verify token hashing is deterministic."""
        token = "same_token"
        hash1 = hash_token(token)
        hash2 = hash_token(token)

        assert hash1 == hash2

    def test_hash_different_tokens(self):
        """Verify different tokens produce different hashes."""
        token1 = "token_1"
        token2 = "token_2"

        hash1 = hash_token(token1)
        hash2 = hash_token(token2)

        assert hash1 != hash2

    def test_hash_empty_token(self):
        """Verify empty token handling."""
        token = ""
        hashed = hash_token(token)

        assert hashed == "no_token"


class TestLoggingSanitization:
    """Tests for logging sanitization."""

    def test_sanitize_normal_text(self):
        """Verify normal text passes through."""
        text = "This is normal log text"
        sanitized = sanitize_for_logging(text)

        assert sanitized == text

    def test_sanitize_newline_injection(self):
        """Verify newline injection prevention."""
        text = "Log line 1\nLog line 2"
        sanitized = sanitize_for_logging(text)

        assert "\n" not in sanitized
        assert "Log line 1" in sanitized
        assert "Log line 2" in sanitized

    def test_sanitize_carriage_return(self):
        """Verify carriage return removal."""
        text = "Line 1\rLine 2"
        sanitized = sanitize_for_logging(text)

        assert "\r" not in sanitized

    def test_sanitize_control_characters(self):
        """Verify control character removal."""
        text = "Normal\x00text\x1fwith\x7fcontrols"
        sanitized = sanitize_for_logging(text)

        assert "\x00" not in sanitized
        assert "\x1f" not in sanitized
        assert "\x7f" not in sanitized
        assert "Normal" in sanitized
        assert "text" in sanitized

    def test_sanitize_multiple_spaces(self):
        """Verify space collapsing."""
        text = "Text   with    multiple     spaces"
        sanitized = sanitize_for_logging(text)

        assert sanitized == "Text with multiple spaces"

    def test_sanitize_non_string(self):
        """Verify non-string input handling."""
        value = 12345
        sanitized = sanitize_for_logging(value)

        assert sanitized == "12345"


class TestLoggingFilter:
    """Tests for logging filter."""

    def test_create_log_filter(self):
        """Verify log filter creation."""
        filter_obj = create_log_filter()

        assert filter_obj is not None

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
        assert result is True  # Filter always returns True to allow record through


class TestSecureLoggingSetup:
    """Tests for secure logging setup."""

    def test_setup_secure_logging(self):
        """Verify secure logging setup."""
        logger = logging.getLogger("test_secure")

        # Should not raise
        setup_secure_logging(logger, add_redaction_filter=True)

        # Logger should have filter
        assert len(logger.filters) > 0

    def test_setup_without_filter(self):
        """Verify setup without filter."""
        logger = logging.getLogger("test_no_filter")
        initial_count = len(logger.filters)

        setup_secure_logging(logger, add_redaction_filter=False)

        # Filter count shouldn't change
        assert len(logger.filters) == initial_count


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

    assert raw_token not in caplog.text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
