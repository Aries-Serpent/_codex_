"""Comprehensive tests for the PII Scrubber module.

PS-04: Privacy-First Memory - Test Suite
Tests all PII detection patterns including:
- Email addresses (RFC 5322 compliant)
- IP addresses (IPv4, IPv6)
- Phone numbers (international formats)
- SSN/Tax ID detection
- Credit card numbers (with Luhn validation)
- AWS access keys
- GPL license detection
"""

from codex.knowledge.pii import (
    RedactionMode,
    scrub,
    scrub_for_embedding,
)


class TestEmailScrubbing:
    """Test email PII detection and redaction."""

    def test_simple_email(self):
        text = "Contact john.doe@example.com for help"
        result, flags = scrub(text)
        assert flags["pii_email"] is True
        assert "@example.com" not in result
        assert flags["total_redactions"] >= 1

    def test_multiple_emails(self):
        text = "Send to a@b.com and c@d.org"
        result, flags = scrub(text, mode=RedactionMode.TOKEN_REPLACEMENT)
        assert flags["pii_email"] is True
        assert result.count("[EMAIL_REDACTED]") == 2

    def test_email_semantic_preservation(self):
        text = "Email: test@company.io"
        result, flags = scrub(text, mode=RedactionMode.SEMANTIC_PRESERVATION)
        assert "user@domain.com" in result
        assert flags["pii_email"] is True

    def test_email_with_subdomain(self):
        text = "admin@mail.server.example.com"
        result, flags = scrub(text)
        assert flags["pii_email"] is True

    def test_no_email_false_positive(self):
        text = "This is not an email: test@localhost"
        result, flags = scrub(text)
        # localhost doesn't match the pattern (needs 2+ char TLD)
        assert "test@localhost" in result


class TestPhoneScrubbing:
    """Test phone number PII detection."""

    def test_us_phone_format(self):
        text = "Call 555-123-4567"
        result, flags = scrub(text)
        assert flags["pii_phone"] is True
        assert "123-4567" not in result

    def test_international_format(self):
        text = "Phone: +1-800-555-1234"
        result, flags = scrub(text)
        assert flags["pii_phone"] is True
        assert "555-1234" not in result

    def test_parenthesis_format(self):
        text = "(555) 123-4567"
        result, flags = scrub(text)
        assert flags["pii_phone"] is True

    def test_phone_semantic_mode(self):
        text = "Call me at 555-123-4567"
        result, flags = scrub(text, mode=RedactionMode.SEMANTIC_PRESERVATION)
        assert "+1-555-000-0000" in result


class TestIPAddressScrubbing:
    """Test IP address detection."""

    def test_ipv4_address(self):
        text = "Server IP: 192.168.1.100"
        result, flags = scrub(text)
        assert flags["pii_ipv4"] is True
        assert "192.168.1.100" not in result
        assert "[IPV4_REDACTED]" in result

    def test_ipv4_semantic_mode(self):
        text = "IP: 10.0.0.50"
        result, flags = scrub(text, mode=RedactionMode.SEMANTIC_PRESERVATION)
        assert "10.0.0.1" in result

    def test_invalid_ipv4_no_match(self):
        text = "Not an IP: 999.999.999.999"
        result, flags = scrub(text)
        # 999 is > 255, so shouldn't match
        assert flags["pii_ipv4"] is False

    def test_ipv6_address(self):
        text = "IPv6: 2001:0db8:85a3:0000:0000:8a2e:0370:7334"
        result, flags = scrub(text)
        assert flags["pii_ipv6"] is True
        assert "[IPV6_REDACTED]" in result

    def test_disable_ip_detection(self):
        text = "Server: 192.168.1.1"
        result, flags = scrub(text, enable_ip=False)
        assert flags["pii_ipv4"] is False
        assert "192.168.1.1" in result


class TestSSNScrubbing:
    """Test Social Security Number detection."""

    def test_ssn_with_dashes(self):
        text = "SSN: 123-45-6789"
        result, flags = scrub(text)
        assert flags["pii_ssn"] is True
        assert "[SSN_REDACTED]" in result

    def test_ssn_with_dots(self):
        text = "SSN: 123.45.6789"
        result, flags = scrub(text)
        assert flags["pii_ssn"] is True

    def test_ssn_without_separators(self):
        text = "SSN: 123456789"
        result, flags = scrub(text)
        assert flags["pii_ssn"] is True

    def test_disable_ssn_detection(self):
        text = "SSN: 123-45-6789"
        result, flags = scrub(text, enable_ssn=False)
        assert flags["pii_ssn"] is False
        assert "123-45-6789" in result


class TestCreditCardScrubbing:
    """Test credit card number detection with Luhn validation."""

    def test_valid_visa_card(self):
        # Valid Visa test number
        text = "Card: 4111111111111111"
        result, flags = scrub(text)
        assert flags["pii_credit_card"] is True
        assert "[CREDIT_CARD_REDACTED]" in result

    def test_valid_mastercard(self):
        # Valid Mastercard test number
        text = "Pay with 5500000000000004"
        result, flags = scrub(text)
        assert flags["pii_credit_card"] is True

    def test_invalid_luhn_not_matched(self):
        # Invalid Luhn checksum - should not be redacted
        text = "Number: 4111111111111112"
        result, flags = scrub(text)
        # Invalid Luhn should not be flagged
        assert flags["pii_credit_card"] is False

    def test_disable_credit_card_detection(self):
        text = "Card: 4111111111111111"
        result, flags = scrub(text, enable_credit_card=False)
        assert flags["pii_credit_card"] is False


class TestAWSKeyScrubbing:
    """Test AWS access key detection."""

    def test_aws_access_key(self):
        text = "AWS key: AKIAIOSFODNN7EXAMPLE"
        result, flags = scrub(text)
        assert flags["pii_aws_key"] is True
        assert "[AWS_KEY_REDACTED]" in result

    def test_disable_aws_key_detection(self):
        text = "Key: AKIAIOSFODNN7EXAMPLE"
        result, flags = scrub(text, enable_aws_key=False)
        assert flags["pii_aws_key"] is False


class TestLicenseDetection:
    """Test GPL license detection."""

    def test_gpl_blocked_by_default(self):
        text = "This code is under GNU GENERAL PUBLIC LICENSE"
        result, flags = scrub(text)
        assert flags["license_gpl"] is True
        assert "[LICENSE_BLOCKED_GPL]" in result

    def test_gpl_allowed(self):
        text = "This code is under GPL v3"
        result, flags = scrub(text, allow_gpl=True)
        assert flags["license_gpl"] is True
        assert "GPL v3" in result


class TestRedactionModes:
    """Test different redaction modes."""

    def test_token_replacement_mode(self):
        text = "Email: test@example.com"
        result, flags = scrub(text, mode=RedactionMode.TOKEN_REPLACEMENT)
        assert "[EMAIL_REDACTED]" in result

    def test_semantic_preservation_mode(self):
        text = "Email: test@example.com"
        result, flags = scrub(text, mode=RedactionMode.SEMANTIC_PRESERVATION)
        assert "user@domain.com" in result


class TestMultiplePIITypes:
    """Test detection of multiple PII types in same text."""

    def test_email_and_phone(self):
        text = "Contact john@example.com or 555-123-4567"
        result, flags = scrub(text)
        assert flags["pii_email"] is True
        assert flags["pii_phone"] is True
        assert flags["total_redactions"] == 2

    def test_all_pii_types(self):
        text = """
        Email: test@example.com
        Phone: 555-123-4567
        IP: 192.168.1.1
        SSN: 123-45-6789
        Card: 4111111111111111
        AWS: AKIAIOSFODNN7EXAMPLE
        """
        result, flags = scrub(text)
        assert flags["pii_email"] is True
        assert flags["pii_phone"] is True
        assert flags["pii_ipv4"] is True
        assert flags["pii_ssn"] is True
        assert flags["pii_credit_card"] is True
        assert flags["pii_aws_key"] is True
        assert flags["total_redactions"] >= 6


class TestRedactionDetails:
    """Test redaction detail tracking."""

    def test_redaction_details_populated(self):
        text = "Email test@example.com and 555-123-4567"
        result, flags = scrub(text)
        assert len(flags["redaction_details"]) >= 2
        types = [d["type"] for d in flags["redaction_details"]]
        assert "email" in types
        assert "phone" in types


class TestScrubForEmbedding:
    """Test the convenience function for RAG pipeline."""

    def test_scrub_for_embedding_returns_string(self):
        text = "Contact admin@example.com"
        result = scrub_for_embedding(text)
        assert isinstance(result, str)
        assert "@example.com" not in result

    def test_scrub_for_embedding_all_pii_removed(self):
        text = "IP 192.168.1.1 and SSN 123-45-6789"
        result = scrub_for_embedding(text)
        assert "192.168.1.1" not in result
        assert "123-45-6789" not in result


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_string(self):
        result, flags = scrub("")
        assert result == ""
        assert flags["total_redactions"] == 0

    def test_no_pii(self):
        text = "This is clean text with no personal information."
        result, flags = scrub(text)
        assert result == text
        assert flags["total_redactions"] == 0

    def test_unicode_text(self):
        text = "Email: тест@example.com"
        result, flags = scrub(text)
        # Should still detect the email
        assert flags["pii_email"] is True

    def test_very_long_text(self):
        text = "test@example.com " * 1000
        result, flags = scrub(text)
        assert flags["pii_email"] is True
        assert flags["total_redactions"] == 1000
