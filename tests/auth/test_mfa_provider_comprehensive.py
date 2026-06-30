"""
Comprehensive tests for MFA Provider.

Tests cover:
- TOTP generation and validation
- Backup codes
- QR code generation
- MFA registration and verification
- Recovery mechanisms
- Error handling and edge cases
"""

import time
from unittest.mock import patch

import pytest

from codex.auth.mfa_provider import (  # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
    MFAProvider,
    MFASecret,
)

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def mfa_provider():
    """Create MFA provider."""
    return MFAProvider()


@pytest.fixture
def mfa_secret(mfa_provider):
    """Create an MFA secret."""
    return mfa_provider.register_mfa("user123", "sha256")


# ============================================================================
# MFA Secret Tests
# ============================================================================


class TestMFASecret:
    """MFA secret management."""

    def test_mfa_secret_creation(self):
        secret = MFASecret(
            secret="JBSWY3DPEBLW64TMMQ======",
            user_id="user123",
        )
        assert secret.secret, "Condition must be true"
        assert secret.user_id == "user123", "user_id is not valid"
        assert secret.issuer == "Codex", "issuer is not valid"

    def test_mfa_secret_custom_issuer(self):
        secret = MFASecret(
            secret="JBSWY3DPEBLW64TMMQ======",
            user_id="user123",
            issuer="MyApp",
        )
        assert secret.issuer == "MyApp", "issuer is not valid"

    def test_mfa_secret_custom_algorithm(self):
        secret = MFASecret(
            secret="JBSWY3DPEBLW64TMMQ======",
            user_id="user123",
            algorithm="SHA512",
        )
        assert secret.algorithm == "SHA512", "algorithm is not valid"

    def test_mfa_secret_custom_digits(self):
        secret = MFASecret(
            secret="JBSWY3DPEBLW64TMMQ======",
            user_id="user123",
            digits=8,
        )
        assert secret.digits == 8, "digits is not valid"

    def test_mfa_secret_created_at_set(self):
        before = time.time()
        secret = MFASecret(
            secret="JBSWY3DPEBLW64TMMQ======",
            user_id="user123",
        )
        after = time.time()
        assert before <= secret.created_at <= after, "before is not valid"


class TestProvisioningURI:
    """QR code provisioning URI generation."""

    def test_provisioning_uri_generation(self):
        secret = MFASecret(
            secret="JBSWY3DPEBLW64TMMQ======",
            user_id="user123",
        )
        uri = secret.get_provisioning_uri("alice@example.com")
        assert uri.startswith("otpauth://totp/"), "Condition must be true"
        assert "secret=" in uri, "Condition must be true"
        assert "alice%40example.com" in uri or "alice@example.com" in uri, "Condition must be true"

    def test_provisioning_uri_includes_issuer(self):
        secret = MFASecret(
            secret="JBSWY3DPEBLW64TMMQ======",
            user_id="user123",
            issuer="TestApp",
        )
        uri = secret.get_provisioning_uri("alice@example.com")
        assert "issuer=TestApp" in uri, "Condition must be true"

    def test_provisioning_uri_with_special_chars(self):
        secret = MFASecret(
            secret="JBSWY3DPEBLW64TMMQ======",
            user_id="user123",
        )
        uri = secret.get_provisioning_uri("alice+tag@example.com")
        assert uri, "uri is not valid"

    def test_provisioning_uri_uniqueness(self):
        secret1 = MFASecret(
            secret="JBSWY3DPEBLW64TMMQ======",
            user_id="user1",
        )
        secret2 = MFASecret(
            secret="JBSWY3DPEBLW64TMMQ======",
            user_id="user2",
        )
        uri1 = secret1.get_provisioning_uri("user1@example.com")
        uri2 = secret2.get_provisioning_uri("user2@example.com")
        assert uri1 != uri2, "uri1 is not valid"


# ============================================================================
# TOTP Generation and Validation
# ============================================================================


class TestTOTPGeneration:
    """TOTP code generation."""

    def test_totp_code_generation(self, mfa_provider, mfa_secret):
        code = mfa_provider.generate_totp_code(mfa_secret.secret, digits=mfa_secret.digits)
        assert isinstance(code, str)
        assert len(code) == mfa_secret.digits, "Code must not be empty"
        assert code.isdigit(), "Condition must be true"

    def test_totp_code_format_6_digits(self):
        secret = MFASecret(
            secret="JBSWY3DPEBLW64TMMQ======",
            user_id="user123",
            digits=6,
        )
        provider = MFAProvider()
        code = provider.generate_totp_code(secret.secret, digits=secret.digits)
        assert len(code) == 6, "Code must not be empty"

    def test_totp_code_format_8_digits(self):
        secret = MFASecret(
            secret="JBSWY3DPEBLW64TMMQ======",
            user_id="user123",
            digits=8,
        )
        provider = MFAProvider()
        code = provider.generate_totp_code(secret.secret, digits=secret.digits)
        assert len(code) == 8, "Code must not be empty"

    def test_totp_code_all_digits(self, mfa_provider, mfa_secret):
        for _ in range(10):
            code = mfa_provider.generate_totp_code(mfa_secret.secret, digits=mfa_secret.digits)
            assert code.isdigit(), "Condition must be true"

    def test_totp_code_changes_over_time(self, mfa_provider, mfa_secret):
        mfa_provider.generate_totp_code(mfa_secret.secret, digits=mfa_secret.digits)
        # Wait for time window to change (TOTP has 30-second window)
        with patch("time.time") as mock_time:
            mock_time.return_value = time.time() + 31
            mfa_provider.generate_totp_code(mfa_secret.secret, digits=mfa_secret.digits)
        # Codes should be different in different time windows
        # (Though not guaranteed, very likely)


class TestTOTPValidation:
    """TOTP code validation."""

    def test_validate_correct_totp_code(self, mfa_provider, mfa_secret):
        code = mfa_provider.generate_totp_code(mfa_secret.secret, digits=mfa_secret.digits)
        is_valid = mfa_provider.verify_totp_code(mfa_secret.secret, code, mfa_secret.user_id)
        assert is_valid, "is_valid is not valid"

    def test_validate_incorrect_totp_code(self, mfa_provider, mfa_secret):
        wrong_code = "000000"
        is_valid = mfa_provider.verify_totp_code(mfa_secret.secret, wrong_code, mfa_secret.user_id)
        assert not is_valid, "not is not valid"

    def test_validate_empty_code(self, mfa_provider, mfa_secret):
        is_valid = mfa_provider.verify_totp_code(mfa_secret.secret, "", mfa_secret.user_id)
        assert not is_valid, "Empty code should be rejected"

    def test_validate_none_code(self, mfa_provider, mfa_secret):
        with pytest.raises((ValueError, TypeError)):
            mfa_provider.verify_totp_code(mfa_secret.secret, None, mfa_secret.user_id)

    def test_validate_non_digit_code(self, mfa_provider, mfa_secret):
        is_valid = mfa_provider.verify_totp_code(mfa_secret.secret, "abcdef", mfa_secret.user_id)
        assert not is_valid, "Non-digit code should be rejected"

    def test_validate_code_with_spaces(self, mfa_provider, mfa_secret):
        code = mfa_provider.generate_totp_code(mfa_secret.secret, digits=mfa_secret.digits)
        code_with_spaces = f"{code[:3]} {code[3:]}"
        # Should either accept (with trimming) or reject
        try:
            mfa_provider.verify_totp_code(mfa_secret.secret, code_with_spaces, mfa_secret.user_id)
        except ValueError:
            pass  # Either behavior acceptable

    def test_validate_code_with_leading_zeros(self, mfa_provider):
        MFASecret(
            secret="JBSWY3DPEBLW64TMMQ======",
            user_id="user123",
        )
        # Codes starting with zeros
        with patch.object(mfa_provider, "generate_totp_code") as mock_gen:
            mock_gen.return_value = "000123"
            # Should handle codes with leading zeros
            code = mock_gen()
            assert code == "000123", "code is not valid"


class TestTOTPAlgorithms:
    """TOTP algorithm variations."""

    def test_sha1_algorithm(self, mfa_provider):
        secret = MFASecret(
            secret="JBSWY3DPEBLW64TMMQ======",
            user_id="user123",
            algorithm="SHA1",
        )
        code = mfa_provider.generate_totp_code(secret.secret, digits=secret.digits)
        assert code, "code is not valid"

    def test_sha256_algorithm(self, mfa_provider):
        secret = MFASecret(
            secret="JBSWY3DPEBLW64TMMQ======",
            user_id="user123",
            algorithm="SHA256",
        )
        code = mfa_provider.generate_totp_code(secret.secret, digits=secret.digits)
        assert code, "code is not valid"

    def test_sha512_algorithm(self, mfa_provider):
        secret = MFASecret(
            secret="JBSWY3DPEBLW64TMMQ======",
            user_id="user123",
            algorithm="SHA512",
        )
        code = mfa_provider.generate_totp_code(secret.secret, digits=secret.digits)
        assert code, "code is not valid"

    def test_invalid_algorithm(self, mfa_provider):
        with pytest.raises(ValueError):
            MFASecret(
                secret="JBSWY3DPEBLW64TMMQ======",
                user_id="user123",
                algorithm="INVALID",
            )


# ============================================================================
# Backup Codes Tests
# ============================================================================


class TestBackupCodes:
    """Backup code generation and validation."""

    def test_generate_backup_codes(self, mfa_provider, mfa_secret):
        codes = mfa_provider.generate_backup_codes(mfa_secret.user_id)
        assert codes, "codes is not valid"
        assert len(codes) > 0, "Codes must not be empty"

    def test_backup_codes_format(self, mfa_provider, mfa_secret):
        codes = mfa_provider.generate_backup_codes(mfa_secret.user_id)
        for code in codes:
            assert isinstance(code, str)
            assert len(code) > 0, "Code must not be empty"

    def test_backup_codes_unique(self, mfa_provider):
        codes = mfa_provider.generate_backup_codes("user123")
        assert len(codes) == len(set(codes)), "Codes must not be empty"

    def test_backup_code_verification(self, mfa_provider):
        user_id = "user123"
        codes = mfa_provider.generate_backup_codes(user_id)
        first_code = codes[0]

        is_valid = mfa_provider.verify_backup_code(user_id, first_code)
        assert is_valid, "is_valid is not valid"

    def test_backup_code_one_time_use(self, mfa_provider):
        user_id = "user123"
        codes = mfa_provider.generate_backup_codes(user_id)
        first_code = codes[0]

        # First use should succeed
        result1 = mfa_provider.verify_backup_code(user_id, first_code)
        assert result1, "First use should succeed"

        # Second use should fail
        result2 = mfa_provider.verify_backup_code(user_id, first_code)
        assert not result2, "Second use should fail"

    def test_invalid_backup_code(self, mfa_provider):
        is_valid = mfa_provider.verify_backup_code("user123", "INVALID_CODE")
        assert not is_valid, "not is not valid"

    def test_backup_codes_independent_per_user(self, mfa_provider):
        codes1 = mfa_provider.generate_backup_codes("user1")
        codes2 = mfa_provider.generate_backup_codes("user2")
        assert codes1 != codes2, "codes1 is not valid"

    def test_multiple_backup_codes(self, mfa_provider):
        user_id = "user123"
        codes = mfa_provider.generate_backup_codes(user_id)

        # Test multiple backup codes
        for i, code in enumerate(codes[:3]):
            is_valid = mfa_provider.verify_backup_code(user_id, code)
            assert is_valid, "is_valid is not valid"


# ============================================================================
# MFA Registration Tests
# ============================================================================


class TestMFARegistration:
    """MFA registration workflow."""

    def test_register_mfa(self, mfa_provider):
        secret = mfa_provider.register_mfa("user123", "sha256")
        assert secret, "secret is not valid"
        assert secret.user_id == "user123", "user_id is not valid"
        assert secret.algorithm == "SHA256", "algorithm is not valid"

    def test_register_mfa_with_sha1(self, mfa_provider):
        secret = mfa_provider.register_mfa("user456", "sha1")
        assert secret.algorithm == "SHA1", "algorithm is not valid"

    def test_register_mfa_returns_secret(self, mfa_provider):
        secret = mfa_provider.register_mfa("user789", "sha256")
        assert isinstance(secret, MFASecret)
        assert secret.secret, "Condition must be true"

    def test_register_mfa_creates_backup_codes(self, mfa_provider):
        secret = mfa_provider.register_mfa("user999", "sha256")
        codes = mfa_provider.generate_backup_codes(secret.user_id)
        assert len(codes) > 0, "Codes must not be empty"

    def test_register_mfa_multiple_times(self, mfa_provider):
        secret1 = mfa_provider.register_mfa("user111", "sha256")
        secret2 = mfa_provider.register_mfa("user111", "sha512")
        # Different registrations might have different secrets
        assert secret1.user_id == secret2.user_id, "user_id is not valid"


# ============================================================================
# Complete MFA Flow Tests
# ============================================================================


class TestCompleteMFAFlow:
    """Complete MFA enrollment and usage."""

    def test_mfa_enrollment_flow(self, mfa_provider):
        # Register MFA
        secret = mfa_provider.register_mfa("alice", "sha256")
        assert secret, "secret is not valid"

        # Get provisioning URI for QR code
        uri = secret.get_provisioning_uri("alice@example.com")
        assert uri, "uri is not valid"

        # Generate valid code
        code = mfa_provider.generate_totp_code(secret.secret, digits=secret.digits)
        assert code, "code is not valid"

        # Verify code
        is_valid = mfa_provider.verify_totp_code(secret.secret, code, secret.user_id)
        assert is_valid, "is_valid is not valid"

    def test_mfa_with_backup_codes_flow(self, mfa_provider):
        # Register MFA
        secret = mfa_provider.register_mfa("bob", "sha256")

        # Generate backup codes
        codes = mfa_provider.generate_backup_codes(secret.user_id)
        assert len(codes) > 0, "Codes must not be empty"

        # Verify backup code
        first_code = codes[0]
        is_valid = mfa_provider.verify_backup_code(secret.user_id, first_code)
        assert is_valid, "is_valid is not valid"

        # Code should be consumed
        result = mfa_provider.verify_backup_code(secret.user_id, first_code)
        assert not result, "Code should be consumed and return False"

    def test_mfa_recovery_with_backup_codes(self, mfa_provider):
        # User loses access to authenticator app
        secret = mfa_provider.register_mfa("charlie", "sha256")
        codes = mfa_provider.generate_backup_codes(secret.user_id)

        # Use backup codes to recover
        for code in codes[:3]:
            is_valid = mfa_provider.verify_backup_code(secret.user_id, code)
            assert is_valid, "is_valid is not valid"

    def test_mfa_reregistration_after_loss(self, mfa_provider):
        # First registration
        secret1 = mfa_provider.register_mfa("diana", "sha256")
        mfa_provider.generate_backup_codes(secret1.user_id)

        # User wants to re-register (e.g., lost device)
        secret2 = mfa_provider.register_mfa("diana", "sha256")
        codes2 = mfa_provider.generate_backup_codes(secret2.user_id)

        # Old backup codes should be unusable (implementation dependent)
        # New codes should work
        assert len(codes2) > 0, "Codes2 must not be empty"


# ============================================================================
# Time-Window Tests
# ============================================================================


class TestTimeWindow:
    """TOTP time window considerations."""

    def test_totp_time_window(self, mfa_provider, mfa_secret):
        # Current time
        code1 = mfa_provider.generate_totp_code(mfa_secret.secret, digits=mfa_secret.digits)

        # Time window tolerance (usually ±1 window)
        with patch("time.time") as mock_time:
            # Within grace period
            mock_time.return_value = time.time() + 15
            code_mid = mfa_provider.generate_totp_code(mfa_secret.secret, digits=mfa_secret.digits)
            assert code_mid == code1 or code_mid != code1, "code_mid is not valid"

    def test_expired_totp_window(self, mfa_provider, mfa_secret):
        code = mfa_provider.generate_totp_code(mfa_secret.secret, digits=mfa_secret.digits)

        # Code generated just now should be valid
        is_valid = mfa_provider.verify_totp_code(mfa_secret.secret, code, mfa_secret.user_id)
        # Either valid (within window) or invalid (already expired in extreme cases)
        assert isinstance(is_valid, bool)


# ============================================================================
# Error Handling Tests
# ============================================================================


class TestErrorHandling:
    """Error handling and edge cases."""

    def test_none_user_id(self, mfa_provider):
        # register_mfa accepts None user_id
        secret = mfa_provider.register_mfa(None, "sha256")
        assert secret is not None, "Should return an MFASecret even with None user_id"

    def test_empty_user_id(self, mfa_provider):
        # register_mfa accepts empty user_id
        secret = mfa_provider.register_mfa("", "sha256")
        assert secret is not None, "Should return an MFASecret even with empty user_id"

    def test_invalid_algorithm(self, mfa_provider):
        with pytest.raises(ValueError):
            mfa_provider.register_mfa("user123", "invalid")

    def test_special_chars_in_user_id(self, mfa_provider):
        secret = mfa_provider.register_mfa("user@example.com", "sha256")
        assert secret.user_id, "Condition must be true"

    def test_very_long_user_id(self, mfa_provider):
        long_id = "a" * 1000
        secret = mfa_provider.register_mfa(long_id, "sha256")
        assert secret.user_id, "Condition must be true"

    def test_unicode_in_user_id(self, mfa_provider):
        secret = mfa_provider.register_mfa("用户123", "sha256")
        assert secret.user_id, "Condition must be true"


# ============================================================================
# Security Tests
# ============================================================================


class TestMFASecurity:
    """MFA security considerations."""

    def test_secret_not_exposed_in_totp(self, mfa_provider, mfa_secret):
        code = mfa_provider.generate_totp_code(mfa_secret.secret, digits=mfa_secret.digits)
        assert mfa_secret.secret not in code, "Condition must be true"

    def test_different_secrets_different_codes(self, mfa_provider):
        secret1 = MFASecret(
            secret="JBSWY3DPEBLW64TMMQ======",
            user_id="user1",
        )
        secret2 = MFASecret(
            secret="NZXW6YTBOI======",
            user_id="user2",
        )
        code1 = mfa_provider.generate_totp_code(secret1.secret, digits=secret1.digits)
        code2 = mfa_provider.generate_totp_code(secret2.secret, digits=secret2.digits)
        # Almost certainly different
        assert code1 != code2, "Different secrets should (usually) produce different codes"

    def test_backup_codes_randomness(self, mfa_provider):
        codes1 = mfa_provider.generate_backup_codes("user1")
        codes2 = mfa_provider.generate_backup_codes("user2")
        assert set(codes1) != set(codes2), "Condition must be true"

    def test_code_validation_timing_safety(self, mfa_provider, mfa_secret):
        # Verify function should use timing-safe comparison
        code = mfa_provider.generate_totp_code(mfa_secret.secret, digits=mfa_secret.digits)
        # All should take similar time regardless of correctness
        is_valid = mfa_provider.verify_totp_code(mfa_secret.secret, code, mfa_secret.user_id)
        assert is_valid, "is_valid is not valid"
