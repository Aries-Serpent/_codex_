"""Unit tests for sensitive data utilities (Phase 23 Week 3 gapfill)."""

from src.utils.sensitive_data import hash_sensitive_value, mask_sensitive_data


def test_mask_sensitive_data_email():
    """Test mask_sensitive_data masks email addresses."""
    text = "Contact me at user@example.com"
    result = mask_sensitive_data(text)
    assert "user@example.com" not in result, "Result must not be empty"
    # Accept either masking marker insertion ("***") or full token removal by
    # the redaction implementation; both indicate the sensitive token is not exposed.
    assert "***" in result or "@" not in result  # pragma: allowlist secret


def test_mask_sensitive_data_phone():
    """Test mask_sensitive_data masks phone numbers."""
    text = "Call 555-123-4567"
    result = mask_sensitive_data(text)
    assert "555-123-4567" not in result, "Result must not be empty"
    assert "5551234567" not in result, "Result must not be empty"
    assert "***" in result, "Result must not be empty"


def test_mask_sensitive_data_phone_unformatted():
    """Test mask_sensitive_data masks unformatted phone numbers."""
    text = "Call 5551234567"
    result = mask_sensitive_data(text)
    assert "5551234567" not in result, "Result must not be empty"
    assert "Call" in result, "Result must not be empty"
    assert "***" in result, "Result must not be empty"


def test_mask_sensitive_data_ssn():
    """Test mask_sensitive_data masks SSN patterns."""
    text = "SSN: 123-45-6789"
    result = mask_sensitive_data(text)
    assert "123-45-6789" not in result, "Result must not be empty"
    assert "SSN:" in result, "Result must not be empty"
    assert "***" in result, "Result must not be empty"


def test_mask_sensitive_data_credit_card():
    """Test mask_sensitive_data masks credit card numbers."""
    text = "Card: 4532-1234-5678-9010"
    result = mask_sensitive_data(text)
    assert "4532-1234-5678-9010" not in result, "Result must not be empty"
    assert "Card:" in result and "***" in result, "Result must not be empty"


def test_mask_sensitive_data_api_key():
    """Test mask_sensitive_data masks API keys."""
    api_key = "sk_test_1234567890abcdef"  # pragma: allowlist secret
    text = f"API_KEY={api_key}"
    result = mask_sensitive_data(text)
    assert api_key not in result, "Result must not be empty"
    assert "API_KEY=" in result, "Result must not be empty"
    assert result != text, "Result must not be empty"
    assert "***" in result, "Result must not be empty"


def test_mask_sensitive_data_password():
    """Test mask_sensitive_data masks password fields."""
    text = 'password="secret123"'  # pragma: allowlist secret
    result = mask_sensitive_data(text)
    assert "secret123" not in result, "Result must not be empty"
    assert "***" in result, "Result must not be empty"


def test_mask_sensitive_data_mixed():
    """Test mask_sensitive_data handles multiple sensitive types."""
    text = "Email: user@example.com, Phone: 555-1234, SSN: 123-45-6789"
    result = mask_sensitive_data(text)
    assert "user@example.com" not in result, "Result must not be empty"
    assert "555-1234" not in result, "Result must not be empty"
    assert "123-45-6789" not in result, "Result must not be empty"
    assert "***" in result, "Result must not be empty"


def test_mask_sensitive_data_preserves_structure():
    """Test mask_sensitive_data preserves text structure."""
    text = "Hello user@example.com, how are you?"
    result = mask_sensitive_data(text)
    assert "Hello" in result, "Result must not be empty"
    assert "how are you?" in result, "Result must not be empty"


def test_hash_sensitive_value_consistency():
    """Test hash_sensitive_value produces consistent hashes."""
    value = "sensitive_data"
    hash1 = hash_sensitive_value(value)
    hash2 = hash_sensitive_value(value)
    assert hash1 == hash2, "hash1 is not valid"


def test_hash_sensitive_value_uniqueness():
    """Test hash_sensitive_value yields distinct hashes for this representative sample.

    Note: Hash collisions are theoretically possible for any hash function.
    This test is a practical sanity check for these specific inputs, not a
    mathematical proof of collision-freedom.
    """
    values = [
        "alpha",
        "Alpha",  # case-variant edge case
        "ALPHA",  # additional case-variant edge case
        "beta",
        "gamma",
        "1234567890",
        "special_chars_!@#$%^&*()",
        "much longer value with more content",
        "another_completely_different_string",
        "café",  # Unicode accented Latin
        "CAFÉ",  # Unicode + case variant
        "こんにちは",  # non-Latin Unicode
        "emoji_😀",  # Unicode emoji
    ]
    hashes = [hash_sensitive_value(value) for value in values]
    # Expect no collisions within this small, fixed representative input set.
    assert len(set(hashes)) == len(values), "Values must not be empty"


def test_hash_sensitive_value_length():
    """Test hash_sensitive_value produces fixed-length output."""
    hash1 = hash_sensitive_value("short")
    hash2 = hash_sensitive_value("much longer value with more content")
    assert len(hash1) == len(hash2), "Hash1 must not be empty"


def test_hash_sensitive_value_empty():
    """Test hash_sensitive_value handles empty input."""
    result = hash_sensitive_value("")
    assert result != "", "Result must not be empty"
    assert len(result) > 0, "Result must not be empty"
