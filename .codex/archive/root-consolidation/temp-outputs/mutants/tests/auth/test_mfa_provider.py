"""
Tests for MFA Provider.

Comprehensive test suite for TOTP-based Multi-Factor Authentication.
"""

import time

import pytest

from codex.auth.mfa_provider import (
    BackupCode,
    MFAProvider,
    MFASecret,
)


class TestMFASecret: # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
    """Tests for MFASecret data structure."""

    def test_secret_creation(self):
        """Test MFA secret creation."""
        secret = MFASecret(
            secret="JBSWY3DPEHPK3PXP",  # pragma: allowlist secret
            user_id="user123",
            issuer="Codex",
        )

        assert secret.secret == "JBSWY3DPEHPK3PXP"  # pragma: allowlist secret
        assert secret.user_id == "user123", "user_id is not valid"
        assert secret.issuer == "Codex", "issuer is not valid"
        assert secret.algorithm == "SHA256", "algorithm is not valid"
        assert secret.digits == 6, "digits is not valid"
        assert secret.period == 30, "period is not valid"

    def test_secret_creation_sha1_compatibility(self):
        """Test existing SHA1 secrets still normalize and work."""
        provider = MFAProvider()
        secret = MFASecret(
            secret="JBSWY3DPEHPK3PXP",  # pragma: allowlist secret
            user_id="user123",
            issuer="Codex",
            algorithm="SHA1",
        )
        provider._secret_store[secret.user_id] = secret

        code = provider.generate_totp(secret.secret, algorithm=secret.algorithm)

        assert secret.algorithm == "SHA1", "algorithm is not valid"
        assert (provider.verify_totp(secret.secret, code, secret.user_id, algorithm=secret.algorithm)
            is True
        )

    def test_provisioning_uri(self):
        """Test provisioning URI generation."""
        secret = MFASecret(
            secret="JBSWY3DPEHPK3PXP",  # pragma: allowlist secret
            user_id="user123",
            issuer="Codex",
        )

        uri = secret.get_provisioning_uri("test@example.com")

        assert uri.startswith("otpauth://totp/"), "Condition must be true"
        assert "secret=JBSWY3DPEHPK3PXP" in uri, "Condition must be true"
        assert "issuer=Codex" in uri, "Condition must be true"
        assert "algorithm=SHA256" in uri, "Condition must be true"
        assert "test%40example.com" in uri, "Condition must be true"

    def test_provisioning_uri_sha1_compatibility(self):
        """Test SHA1 secrets still emit the correct provisioning metadata."""
        secret = MFASecret(
            secret="JBSWY3DPEHPK3PXP",  # pragma: allowlist secret
            user_id="user123",
            issuer="Codex",
            algorithm="SHA1",
        )

        uri = secret.get_provisioning_uri("test@example.com")

        assert "algorithm=SHA1" in uri, "Condition must be true"


class TestBackupCode:
    """Tests for BackupCode data structure."""

    def test_backup_code_creation(self):
        """Test backup code creation."""
        code = BackupCode(
            code="1234-5678",
            code_hash="hash123",
        )

        assert code.code == "1234-5678", "code is not valid"
        assert code.code_hash == "hash123", "code_hash is not valid"
        assert code.used is False, "used is not valid"
        assert code.used_at is None, "used_at is not valid"


class TestMFAProvider:
    """Tests for MFAProvider."""

    def test_initialization(self):
        """Test MFA provider initialization."""
        provider = MFAProvider()

        assert provider is not None, "provider must be initialized"
        assert provider._secret_store == {}, "_secret_store is not valid"
        assert provider._backup_codes == {}, "_backup_codes is not valid"
        assert provider._attempts == {}, "_attempts is not valid"
        assert provider._locked_users == {}, "_locked_users is not valid"

    def test_generate_totp_secret(self):
        """Test TOTP secret generation."""
        provider = MFAProvider()
        secret = provider.generate_totp_secret("user123", "Codex")

        assert secret.user_id == "user123", "user_id is not valid"
        assert secret.issuer == "Codex", "issuer is not valid"
        assert len(secret.secret) > 0, "Collection must not be empty"
        assert "user123" in provider._secret_store, "Condition must be true"

    def test_generate_totp_unique_secrets(self):
        """Test that generated secrets are unique."""
        provider = MFAProvider()
        secret1 = provider.generate_totp_secret("user1")
        secret2 = provider.generate_totp_secret("user2")

        assert secret1.secret != secret2.secret, "secret is not valid"

    def test_generate_totp_secret_normalizes_algorithm(self):
        """Test algorithm normalization for newly generated secrets."""
        provider = MFAProvider()

        secret = provider.generate_totp_secret("user123", algorithm="sha512")

        assert secret.algorithm == "SHA512", "algorithm is not valid"

    def test_generate_totp_secret_normalizes_mixed_case_algorithm(self):
        """Test mixed-case algorithm normalization."""
        provider = MFAProvider()

        secret = provider.generate_totp_secret("user123", algorithm="sHa512")

        assert secret.algorithm == "SHA512", "algorithm is not valid"

    def test_generate_totp(self):
        """Test TOTP generation."""
        provider = MFAProvider()
        secret = "JBSWY3DPEHPK3PXP"  # "Hello!" in base32  # pragma: allowlist secret

        # Generate TOTP
        totp = provider.generate_totp(secret)

        assert totp is not None, "totp must be initialized"
        assert len(totp) == 6, "Totp must not be empty"
        assert totp.isdigit(), "Condition must be true"

    def test_generate_totp_consistent(self):
        """Test TOTP generation is consistent for same time."""
        provider = MFAProvider()
        secret = "JBSWY3DPEHPK3PXP"  # pragma: allowlist secret
        timestamp = 1000000000.0

        totp1 = provider.generate_totp(secret, timestamp)
        totp2 = provider.generate_totp(secret, timestamp)

        assert totp1 == totp2, "totp1 is not valid"

    def test_generate_totp_sha1_compatibility(self):
        """Test explicit SHA1 compatibility for RFC 6238 clients."""
        provider = MFAProvider()
        secret = "JBSWY3DPEHPK3PXP"  # pragma: allowlist secret
        timestamp = 1000000000.0

        totp1 = provider.generate_totp(secret, timestamp, algorithm="SHA1")
        totp2 = provider.generate_totp(secret, timestamp, algorithm="sha1")

        assert totp1 == totp2, "totp1 is not valid"

    def test_verify_totp_valid(self):
        """Test TOTP verification with valid code."""
        provider = MFAProvider()
        secret = "JBSWY3DPEHPK3PXP"  # pragma: allowlist secret
        user_id = "user123"

        # Generate code for current time
        code = provider.generate_totp(secret)

        # Verify immediately
        result = provider.verify_totp(secret, code, user_id)

        assert result is True, "Result must not be empty"

    def test_verify_totp_invalid(self):
        """Test TOTP verification with invalid code."""
        provider = MFAProvider()
        secret = "JBSWY3DPEHPK3PXP"  # pragma: allowlist secret
        user_id = "user123"

        # Verify with wrong code
        result = provider.verify_totp(secret, "000000", user_id)

        assert result is False, "Result must not be empty"

    def test_verify_totp_time_window(self):
        """Test TOTP verification with time window."""
        provider = MFAProvider()
        secret = "JBSWY3DPEHPK3PXP"  # pragma: allowlist secret
        user_id = "user123"

        # Generate code for 30 seconds ago
        past_time = time.time() - 30
        code = provider.generate_totp(secret, past_time)

        # Should still be valid with window=1
        result = provider.verify_totp(secret, code, user_id, window=1)

        assert result is True, "Result must not be empty"

    def test_verify_totp_sha1_compatibility(self):
        """Test SHA1 verification remains available for existing secrets."""
        provider = MFAProvider()
        secret = "JBSWY3DPEHPK3PXP"  # pragma: allowlist secret
        user_id = "user123"
        code = provider.generate_totp(secret, algorithm="SHA1")

        assert provider.verify_totp(secret, code, user_id, algorithm="SHA1") is True

    def test_generate_totp_invalid_algorithm(self):
        """Test invalid TOTP algorithms are rejected."""
        provider = MFAProvider()

        with pytest.raises(ValueError, match="Unsupported TOTP algorithm"):
            provider.generate_totp("JBSWY3DPEHPK3PXP", algorithm="MD5")

    def test_secret_creation_invalid_algorithm(self):
        """Test invalid secret algorithms are rejected during construction."""
        with pytest.raises(ValueError, match="Unsupported TOTP algorithm"):
            MFASecret(
                secret="JBSWY3DPEHPK3PXP", user_id="user123", algorithm="MD5"
            )  # pragma: allowlist secret

    def test_verify_totp_invalid_algorithm(self):
        """Test invalid verify_totp algorithms are rejected."""
        provider = MFAProvider()

        with pytest.raises(ValueError, match="Unsupported TOTP algorithm"):
            provider.verify_totp("JBSWY3DPEHPK3PXP", "000000", "user123", algorithm="MD5")

    def test_rate_limiting(self):
        """Test rate limiting on failed attempts."""
        provider = MFAProvider()
        secret = "JBSWY3DPEHPK3PXP"  # pragma: allowlist secret
        user_id = "user123"

        # Make MAX_ATTEMPTS failed attempts
        for _ in range(provider.MAX_ATTEMPTS):
            provider.verify_totp(secret, "000000", user_id)

        # User should be locked out
        assert provider._is_locked_out(user_id) is True, "Condition must be true"

        # Even valid code should fail now
        valid_code = provider.generate_totp(secret)
        result = provider.verify_totp(secret, valid_code, user_id)
        assert result is False, "Result must not be empty"

    def test_lockout_expiry(self):
        """Test that lockout expires after duration."""
        provider = MFAProvider()
        user_id = "user123"

        # Manually set lockout in the past
        provider._locked_users[user_id] = time.time() - 1

        # Should no longer be locked out
        assert provider._is_locked_out(user_id) is False, "Condition must be true"

    def test_generate_backup_codes(self):
        """Test backup code generation."""
        provider = MFAProvider()
        user_id = "user123"

        codes = provider.generate_backup_codes(user_id, count=10)

        assert len(codes) == 10, "Codes must not be empty"
        assert user_id in provider._backup_codes, "Condition must be true"
        assert len(provider._backup_codes[user_id]) == 10, "Collection must not be empty"

        # Codes should be in format XXXX-XXXX
        for code in codes:
            assert len(code) == 9, "Code must not be empty"
            assert "-" in code, "Condition must be true"

    def test_backup_codes_unique(self):
        """Test that backup codes are unique."""
        provider = MFAProvider()
        user_id = "user123"

        codes = provider.generate_backup_codes(user_id, count=10)

        # All codes should be unique
        assert len(codes) == len(set(codes)), "Codes must not be empty"

    def test_verify_backup_code_valid(self):
        """Test backup code verification with valid code."""
        provider = MFAProvider()
        user_id = "user123"

        codes = provider.generate_backup_codes(user_id, count=10)
        code_to_use = codes[0]

        result = provider.verify_backup_code(user_id, code_to_use)

        assert result is True, "Result must not be empty"

    def test_verify_backup_code_invalid(self):
        """Test backup code verification with invalid code."""
        provider = MFAProvider()
        user_id = "user123"

        provider.generate_backup_codes(user_id, count=10)

        result = provider.verify_backup_code(user_id, "INVALID-CODE")

        assert result is False, "Result must not be empty"

    def test_verify_backup_code_single_use(self):
        """Test that backup codes can only be used once."""
        provider = MFAProvider()
        user_id = "user123"

        codes = provider.generate_backup_codes(user_id, count=10)
        code_to_use = codes[0]

        # First use should succeed
        result1 = provider.verify_backup_code(user_id, code_to_use)
        assert result1 is True, "Result must not be empty"

        # Second use should fail
        result2 = provider.verify_backup_code(user_id, code_to_use)
        assert result2 is False, "Result must not be empty"

    def test_get_remaining_backup_codes(self):
        """Test getting count of remaining backup codes."""
        provider = MFAProvider()
        user_id = "user123"

        # Initially no codes
        assert provider.get_remaining_backup_codes(user_id) == 0, "Condition must be true"

        # Generate codes
        codes = provider.generate_backup_codes(user_id, count=10)
        assert provider.get_remaining_backup_codes(user_id) == 10, "Condition must be true"

        # Use one code
        provider.verify_backup_code(user_id, codes[0])
        assert provider.get_remaining_backup_codes(user_id) == 9, "Condition must be true"

    def test_disable_mfa(self):
        """Test disabling MFA for a user."""
        provider = MFAProvider()
        user_id = "user123"

        # Enable MFA
        provider.generate_totp_secret(user_id)
        provider.generate_backup_codes(user_id)

        assert provider.is_mfa_enabled(user_id) is True, "Condition must be true"

        # Disable MFA
        result = provider.disable_mfa(user_id)

        assert result is True, "Result must not be empty"
        assert provider.is_mfa_enabled(user_id) is False, "Condition must be true"
        assert user_id not in provider._secret_store, "Condition must be true"
        assert user_id not in provider._backup_codes, "Condition must be true"

    def test_disable_mfa_not_enabled(self):
        """Test disabling MFA when not enabled."""
        provider = MFAProvider()
        user_id = "user123"

        result = provider.disable_mfa(user_id)

        assert result is False, "Result must not be empty"

    def test_is_mfa_enabled(self):
        """Test checking if MFA is enabled."""
        provider = MFAProvider()
        user_id = "user123"

        assert provider.is_mfa_enabled(user_id) is False, "Condition must be true"

        provider.generate_totp_secret(user_id)

        assert provider.is_mfa_enabled(user_id) is True, "Condition must be true"


class TestMFAProviderIntegration:
    """Integration tests for MFA workflow."""

    def test_full_mfa_setup_and_verification(self):
        """Test complete MFA setup and verification flow."""
        provider = MFAProvider()
        user_id = "user123"
        account_name = "test@example.com"

        # Step 1: Generate secret
        secret = provider.generate_totp_secret(user_id, "Codex")
        assert provider.is_mfa_enabled(user_id) is True, "Condition must be true"

        # Step 2: Get provisioning URI (user would scan QR code)
        uri = secret.get_provisioning_uri(account_name)
        assert "otpauth://" in uri, "Condition must be true"

        # Step 3: Generate backup codes
        backup_codes = provider.generate_backup_codes(user_id, count=10)
        assert len(backup_codes) == 10, "Backup_codes must not be empty"

        # Step 4: Verify TOTP
        totp_code = provider.generate_totp(secret.secret)
        assert provider.verify_totp(secret.secret, totp_code, user_id) is True

        # Step 5: Verify backup code
        assert provider.verify_backup_code(user_id, backup_codes[0]) is True
        assert provider.get_remaining_backup_codes(user_id) == 9, "Condition must be true"

    def test_mfa_recovery_flow(self):
        """Test MFA recovery using backup codes."""
        provider = MFAProvider()
        user_id = "user123"

        # Setup MFA
        secret = provider.generate_totp_secret(user_id)
        backup_codes = provider.generate_backup_codes(user_id, count=10)

        # Simulate lost device - use backup code
        first_backup = backup_codes[0]
        assert provider.verify_backup_code(user_id, first_backup) is True

        # User can still use TOTP after using backup code
        totp_code = provider.generate_totp(secret.secret)
        assert provider.verify_totp(secret.secret, totp_code, user_id) is True

    def test_mfa_attack_prevention(self):
        """Test MFA security against brute force attacks."""
        provider = MFAProvider()
        user_id = "user123"

        secret = provider.generate_totp_secret(user_id)

        # Simulate brute force attack
        for _ in range(provider.MAX_ATTEMPTS):
            provider.verify_totp(secret.secret, "000000", user_id)

        # Account should be locked
        assert provider._is_locked_out(user_id) is True, "Condition must be true"

        # Even correct code should fail
        valid_code = provider.generate_totp(secret.secret)
        assert provider.verify_totp(secret.secret, valid_code, user_id) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
