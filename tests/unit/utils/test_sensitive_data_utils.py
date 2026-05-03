"""Unit tests for sensitive data utilities (Phase 23 Week 3 gapfill)."""


from src.utils.sensitive_data import hash_sensitive_value, mask_sensitive_data


def test_mask_sensitive_data_email():
    """Test mask_sensitive_data masks email addresses."""
    text = "Contact me at user@example.com"
    result = mask_sensitive_data(text)
    assert "user@example.com" not in result
    assert "***" in result or "@" not in result # pragma: allowlist secret # pragma: allowlist secret


def test_mask_sensitive_data_phone():
    """Test mask_sensitive_data masks phone numbers."""
    text = "Call 555-123-4567"
    result = mask_sensitive_data(text)
    assert "555-123-4567" not in result


def test_mask_sensitive_data_ssn():
    """Test mask_sensitive_data masks SSN patterns."""
    text = "SSN: 123-45-6789"
    result = mask_sensitive_data(text)
    assert "123-45-6789" not in result


def test_mask_sensitive_data_credit_card():
    """Test mask_sensitive_data masks credit card numbers."""
    text = "Card: 4532-1234-5678-9010"
    result = mask_sensitive_data(text)
    assert "4532-1234-5678-9010" not in result


def test_mask_sensitive_data_api_key():
    """Test mask_sensitive_data masks API keys."""
    text = "API_KEY=" + "sk_test_" + "1234567890abcdef"
    result = mask_sensitive_data(text)
    assert "sk_test_" + "1234567890abcdef" not in result


def test_mask_sensitive_data_password():
    """Test mask_sensitive_data masks password fields."""
    text = 'password="secret123"'
    result = mask_sensitive_data(text)
    assert "secret123" not in result


def test_mask_sensitive_data_mixed():
    """Test mask_sensitive_data handles multiple sensitive types."""
    text = "Email: user@example.com, Phone: 555-1234, SSN: 123-45-6789"
    result = mask_sensitive_data(text)
    assert "user@example.com" not in result
    assert "555-1234" not in result
    assert "123-45-6789" not in result


def test_mask_sensitive_data_preserves_structure():
    """Test mask_sensitive_data preserves text structure."""
    text = "Hello user@example.com, how are you?"
    result = mask_sensitive_data(text)
    assert "Hello" in result
    assert "how are you?" in result


def test_hash_sensitive_value_consistency():
    """Test hash_sensitive_value produces consistent hashes."""
    value = "sensitive_data"
    hash1 = hash_sensitive_value(value)
    hash2 = hash_sensitive_value(value)
    assert hash1 == hash2


def test_hash_sensitive_value_uniqueness():
    """Test hash_sensitive_value produces unique hashes."""
    hash1 = hash_sensitive_value("value1")
    hash2 = hash_sensitive_value("value2")
    assert hash1 != hash2


def test_hash_sensitive_value_length():
    """Test hash_sensitive_value produces fixed-length output."""
    hash1 = hash_sensitive_value("short")
    hash2 = hash_sensitive_value("much longer value with more content")
    assert len(hash1) == len(hash2)


def test_hash_sensitive_value_empty():
    """Test hash_sensitive_value handles empty input."""
    result = hash_sensitive_value("")
    assert result != ""
    assert len(result) > 0
