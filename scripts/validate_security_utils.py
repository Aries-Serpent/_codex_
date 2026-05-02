#!/usr/bin/env python3
"""
Validate Security Utils

Purpose:
    Validates security_utils

Usage:
    python scripts/validate_security_utils.py [options]

    Examples:
    $ python scripts/validate_security_utils.py --help

Arguments:
    [To be documented]

Environment Variables:
    [To be documented]

Dependencies:
    [To be documented]

Exit Codes:
    0: Success
    1: Error

Author: Codex Team
Last Updated: 2026-01-16
"""



import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from codex.security_utils import (
    redact_dict_with_secret_keys,
    redact_secret_name,
    redact_sensitive_value,
    safe_secret_reference,
    sanitize_log_message,
)


def test_redact_sensitive_value():
    """Test sensitive value redaction."""
    print("Testing redact_sensitive_value...")

    result = redact_sensitive_value("my-secret-key-12345")
    assert result == '[REDACTED]', f"Expected '[REDACTED]', got '{result}'"

    result = redact_sensitive_value("")
    assert result == '[EMPTY]', f"Expected '[EMPTY]', got '{result}'"

    result = redact_sensitive_value(None)
    assert result == '[EMPTY]', f"Expected '[EMPTY]', got '{result}'"

    print("✅ redact_sensitive_value tests passed")


def test_redact_secret_name():
    """Test secret name redaction."""
    print("Testing redact_secret_name...")

    result = redact_secret_name("API_KEY")
    assert result == '[REDACTED_SECRET_NAME]', f"Expected '[REDACTED_SECRET_NAME]', got '{result}'"

    result = redact_secret_name("PROD_DATABASE_PASSWORD")
    assert result == '[REDACTED_SECRET_NAME]', f"Expected '[REDACTED_SECRET_NAME]', got '{result}'"

    result = redact_secret_name("")
    assert result == '[UNNAMED_SECRET]', f"Expected '[UNNAMED_SECRET]', got '{result}'"

    print("✅ redact_secret_name tests passed")


def test_redact_dict_with_secret_keys():
    """Test dictionary key redaction."""
    print("Testing redact_dict_with_secret_keys...")

    data = {
        "GITHUB_TOKEN": "ghp_1234567890",
        "API_KEY": "sk-1234567890",
        "DATABASE_URL": "postgresql://user:pass@host/db"
    }
    result = redact_dict_with_secret_keys(data)

    assert len(result) == 3, f"Expected 3 keys, got {len(result)}"
    assert "secret_1" in result, "Expected 'secret_1' in result"
    assert "GITHUB_TOKEN" not in result, "Original key should be redacted"

    result = redact_dict_with_secret_keys({})
    assert result == {}, f"Expected empty dict, got {result}"

    result = redact_dict_with_secret_keys(None)
    assert result == {}, f"Expected empty dict, got {result}"

    print("✅ redact_dict_with_secret_keys tests passed")


def test_sanitize_log_message():
    """Test log message sanitization."""
    print("Testing sanitize_log_message...")

    message = "Using token: ghp_1234567890abcdefghijklmnopqrstuvwxyz"
    result = sanitize_log_message(message)
    assert "ghp_1234567890abcdefghijklmnopqrstuvwxyz" not in result, "Token should be redacted"
    assert "REDACTED" in result, "Should contain REDACTED marker"

    message = "Operation completed successfully"
    result = sanitize_log_message(message)
    assert result == message, "Clean message should not be modified"

    print("✅ sanitize_log_message tests passed")


def test_safe_secret_reference():
    """Test safe secret reference."""
    print("Testing safe_secret_reference...")

    result = safe_secret_reference("verify")
    assert result == "secret (verify)", f"Expected 'secret (verify)', got '{result}'"

    result = safe_secret_reference("set")
    assert result == "secret (set)", f"Expected 'secret (set)', got '{result}'"

    result = safe_secret_reference("")
    assert result == "secret", f"Expected 'secret', got '{result}'"

    result = safe_secret_reference()
    assert result == "secret", f"Expected 'secret', got '{result}'"

    print("✅ safe_secret_reference tests passed")


def test_codeql_alert_prevention():
    """Test that security utils prevent CodeQL alerts."""
    print("Testing CodeQL alert prevention...")

    # Simulate the exact pattern that triggered CodeQL alerts
    secrets_result = {
        "secret1": "value1",
        "secret2": "value2",
        "secret3": "value3",
        "secret4": "value4"
    }

    # Apply redaction (as fixed in the codebase)
    redacted_result = redact_dict_with_secret_keys(secrets_result) if secrets_result else {}
    secret_count = len(redacted_result)

    # Create log message using only the count (not the dict)
    log_message = f"Secrets configuration complete: {secret_count} items processed"

    # Verify no secret names in log message
    assert "secret1" not in log_message, "Secret name should not be in log"
    assert "value1" not in log_message, "Secret value should not be in log"

    # Verify redacted dict doesn't contain original keys
    for key in redacted_result:
        has_secret_prefix = key.startswith("secret_")
        assert has_secret_prefix, f"Key '{key}' should start with 'secret_'"

    assert len(redacted_result) == 4, f"Expected 4 secrets, got {len(redacted_result)}"

    print("✅ CodeQL alert prevention tests passed")


def test_production_safety():
    """Test production safety defaults."""
    print("Testing production safety defaults...")

    # show_preview should default to False (production safety)
    result = redact_sensitive_value("my-secret-key-12345")
    assert "my-s" not in result, "Preview should be disabled by default"
    assert "2345" not in result, "Preview should be disabled by default"
    assert result == '[REDACTED]', "Should return [REDACTED]"

    print("✅ Production safety tests passed")


def main():
    """Run all validation tests."""
    print("=" * 70)
    print("Security Utilities Validation")
    print("=" * 70)
    print()

    try:
        test_redact_sensitive_value()
        test_redact_secret_name()
        test_redact_dict_with_secret_keys()
        test_sanitize_log_message()
        test_safe_secret_reference()
        test_codeql_alert_prevention()
        test_production_safety()

        print()
        print("=" * 70)
        print("✅ ALL TESTS PASSED")
        print("=" * 70)
        return 0

    except AssertionError as e:
        print()
        print("=" * 70)
        print(f"❌ TEST FAILED: {e}")
        print("=" * 70)
        return 1

    except Exception as e:
        print()
        print("=" * 70)
        print(f"❌ UNEXPECTED ERROR: {e}")
        print("=" * 70)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
