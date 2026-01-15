"""
Tests for MFA Provider.

Comprehensive test suite for TOTP-based Multi-Factor Authentication.
"""

import time
from unittest.mock import patch

import pytest

from src.codex.auth.mfa_provider import (
    MFAProvider,
    MFASecret,
    BackupCode,
    MFAAttempt,
)


class TestMFASecret:
    """Tests for MFASecret data structure."""
    
    def test_secret_creation(self):
        """Test MFA secret creation."""
        secret = MFASecret(
            secret="JBSWY3DPEHPK3PXP",
            user_id="user123",
            issuer="Codex",
        )
        
        assert secret.secret == "JBSWY3DPEHPK3PXP"
        assert secret.user_id == "user123"
        assert secret.issuer == "Codex"
        assert secret.algorithm == "SHA1"
        assert secret.digits == 6
        assert secret.period == 30
    
    def test_provisioning_uri(self):
        """Test provisioning URI generation."""
        secret = MFASecret(
            secret="JBSWY3DPEHPK3PXP",
            user_id="user123",
            issuer="Codex",
        )
        
        uri = secret.get_provisioning_uri("test@example.com")
        
        assert uri.startswith("otpauth://totp/")
        assert "secret=JBSWY3DPEHPK3PXP" in uri
        assert "issuer=Codex" in uri
        assert "test%40example.com" in uri


class TestBackupCode:
    """Tests for BackupCode data structure."""
    
    def test_backup_code_creation(self):
        """Test backup code creation."""
        code = BackupCode(
            code="1234-5678",
            code_hash="hash123",
        )
        
        assert code.code == "1234-5678"
        assert code.code_hash == "hash123"
        assert code.used is False
        assert code.used_at is None


class TestMFAProvider:
    """Tests for MFAProvider."""
    
    def test_initialization(self):
        """Test MFA provider initialization."""
        provider = MFAProvider()
        
        assert provider is not None
        assert provider._secret_store == {}
        assert provider._backup_codes == {}
        assert provider._attempts == {}
        assert provider._locked_users == {}
    
    def test_generate_totp_secret(self):
        """Test TOTP secret generation."""
        provider = MFAProvider()
        secret = provider.generate_totp_secret("user123", "Codex")
        
        assert secret.user_id == "user123"
        assert secret.issuer == "Codex"
        assert len(secret.secret) > 0
        assert "user123" in provider._secret_store
    
    def test_generate_totp_unique_secrets(self):
        """Test that generated secrets are unique."""
        provider = MFAProvider()
        secret1 = provider.generate_totp_secret("user1")
        secret2 = provider.generate_totp_secret("user2")
        
        assert secret1.secret != secret2.secret
    
    def test_generate_totp(self):
        """Test TOTP generation."""
        provider = MFAProvider()
        secret = "JBSWY3DPEHPK3PXP"  # "Hello!" in base32
        
        # Generate TOTP
        totp = provider.generate_totp(secret)
        
        assert totp is not None
        assert len(totp) == 6
        assert totp.isdigit()
    
    def test_generate_totp_consistent(self):
        """Test TOTP generation is consistent for same time."""
        provider = MFAProvider()
        secret = "JBSWY3DPEHPK3PXP"
        timestamp = 1000000000.0
        
        totp1 = provider.generate_totp(secret, timestamp)
        totp2 = provider.generate_totp(secret, timestamp)
        
        assert totp1 == totp2
    
    def test_verify_totp_valid(self):
        """Test TOTP verification with valid code."""
        provider = MFAProvider()
        secret = "JBSWY3DPEHPK3PXP"
        user_id = "user123"
        
        # Generate code for current time
        code = provider.generate_totp(secret)
        
        # Verify immediately
        result = provider.verify_totp(secret, code, user_id)
        
        assert result is True
    
    def test_verify_totp_invalid(self):
        """Test TOTP verification with invalid code."""
        provider = MFAProvider()
        secret = "JBSWY3DPEHPK3PXP"
        user_id = "user123"
        
        # Verify with wrong code
        result = provider.verify_totp(secret, "000000", user_id)
        
        assert result is False
    
    def test_verify_totp_time_window(self):
        """Test TOTP verification with time window."""
        provider = MFAProvider()
        secret = "JBSWY3DPEHPK3PXP"
        user_id = "user123"
        
        # Generate code for 30 seconds ago
        past_time = time.time() - 30
        code = provider.generate_totp(secret, past_time)
        
        # Should still be valid with window=1
        result = provider.verify_totp(secret, code, user_id, window=1)
        
        assert result is True
    
    def test_rate_limiting(self):
        """Test rate limiting on failed attempts."""
        provider = MFAProvider()
        secret = "JBSWY3DPEHPK3PXP"
        user_id = "user123"
        
        # Make MAX_ATTEMPTS failed attempts
        for _ in range(provider.MAX_ATTEMPTS):
            provider.verify_totp(secret, "000000", user_id)
        
        # User should be locked out
        assert provider._is_locked_out(user_id) is True
        
        # Even valid code should fail now
        valid_code = provider.generate_totp(secret)
        result = provider.verify_totp(secret, valid_code, user_id)
        assert result is False
    
    def test_lockout_expiry(self):
        """Test that lockout expires after duration."""
        provider = MFAProvider()
        user_id = "user123"
        
        # Manually set lockout in the past
        provider._locked_users[user_id] = time.time() - 1
        
        # Should no longer be locked out
        assert provider._is_locked_out(user_id) is False
    
    def test_generate_backup_codes(self):
        """Test backup code generation."""
        provider = MFAProvider()
        user_id = "user123"
        
        codes = provider.generate_backup_codes(user_id, count=10)
        
        assert len(codes) == 10
        assert user_id in provider._backup_codes
        assert len(provider._backup_codes[user_id]) == 10
        
        # Codes should be in format XXXX-XXXX
        for code in codes:
            assert len(code) == 9  # 4 + 1 + 4
            assert '-' in code
    
    def test_backup_codes_unique(self):
        """Test that backup codes are unique."""
        provider = MFAProvider()
        user_id = "user123"
        
        codes = provider.generate_backup_codes(user_id, count=10)
        
        # All codes should be unique
        assert len(codes) == len(set(codes))
    
    def test_verify_backup_code_valid(self):
        """Test backup code verification with valid code."""
        provider = MFAProvider()
        user_id = "user123"
        
        codes = provider.generate_backup_codes(user_id, count=10)
        code_to_use = codes[0]
        
        result = provider.verify_backup_code(user_id, code_to_use)
        
        assert result is True
    
    def test_verify_backup_code_invalid(self):
        """Test backup code verification with invalid code."""
        provider = MFAProvider()
        user_id = "user123"
        
        provider.generate_backup_codes(user_id, count=10)
        
        result = provider.verify_backup_code(user_id, "INVALID-CODE")
        
        assert result is False
    
    def test_verify_backup_code_single_use(self):
        """Test that backup codes can only be used once."""
        provider = MFAProvider()
        user_id = "user123"
        
        codes = provider.generate_backup_codes(user_id, count=10)
        code_to_use = codes[0]
        
        # First use should succeed
        result1 = provider.verify_backup_code(user_id, code_to_use)
        assert result1 is True
        
        # Second use should fail
        result2 = provider.verify_backup_code(user_id, code_to_use)
        assert result2 is False
    
    def test_get_remaining_backup_codes(self):
        """Test getting count of remaining backup codes."""
        provider = MFAProvider()
        user_id = "user123"
        
        # Initially no codes
        assert provider.get_remaining_backup_codes(user_id) == 0
        
        # Generate codes
        codes = provider.generate_backup_codes(user_id, count=10)
        assert provider.get_remaining_backup_codes(user_id) == 10
        
        # Use one code
        provider.verify_backup_code(user_id, codes[0])
        assert provider.get_remaining_backup_codes(user_id) == 9
    
    def test_disable_mfa(self):
        """Test disabling MFA for a user."""
        provider = MFAProvider()
        user_id = "user123"
        
        # Enable MFA
        provider.generate_totp_secret(user_id)
        provider.generate_backup_codes(user_id)
        
        assert provider.is_mfa_enabled(user_id) is True
        
        # Disable MFA
        result = provider.disable_mfa(user_id)
        
        assert result is True
        assert provider.is_mfa_enabled(user_id) is False
        assert user_id not in provider._secret_store
        assert user_id not in provider._backup_codes
    
    def test_disable_mfa_not_enabled(self):
        """Test disabling MFA when not enabled."""
        provider = MFAProvider()
        user_id = "user123"
        
        result = provider.disable_mfa(user_id)
        
        assert result is False
    
    def test_is_mfa_enabled(self):
        """Test checking if MFA is enabled."""
        provider = MFAProvider()
        user_id = "user123"
        
        assert provider.is_mfa_enabled(user_id) is False
        
        provider.generate_totp_secret(user_id)
        
        assert provider.is_mfa_enabled(user_id) is True


class TestMFAProviderIntegration:
    """Integration tests for MFA workflow."""
    
    def test_full_mfa_setup_and_verification(self):
        """Test complete MFA setup and verification flow."""
        provider = MFAProvider()
        user_id = "user123"
        account_name = "test@example.com"
        
        # Step 1: Generate secret
        secret = provider.generate_totp_secret(user_id, "Codex")
        assert provider.is_mfa_enabled(user_id) is True
        
        # Step 2: Get provisioning URI (user would scan QR code)
        uri = secret.get_provisioning_uri(account_name)
        assert "otpauth://" in uri
        
        # Step 3: Generate backup codes
        backup_codes = provider.generate_backup_codes(user_id, count=10)
        assert len(backup_codes) == 10
        
        # Step 4: Verify TOTP
        totp_code = provider.generate_totp(secret.secret)
        assert provider.verify_totp(secret.secret, totp_code, user_id) is True
        
        # Step 5: Verify backup code
        assert provider.verify_backup_code(user_id, backup_codes[0]) is True
        assert provider.get_remaining_backup_codes(user_id) == 9
    
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
        assert provider._is_locked_out(user_id) is True
        
        # Even correct code should fail
        valid_code = provider.generate_totp(secret.secret)
        assert provider.verify_totp(secret.secret, valid_code, user_id) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
