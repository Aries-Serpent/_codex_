"""
Integration tests for security modules.
"""

import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock


class TestSecurityMasking:
    """Test sensitive data masking functions."""
    
    def test_mask_token_standard(self):
        """Test standard token masking."""
        from codex.security import mask_token
        
        token = "sk_live_abc123xyz789"
        masked = mask_token(token)
        
        assert "xyz789" in masked
        assert "sk_live" not in masked
        assert len(masked) == len(token)
    
    def test_mask_email(self):
        """Test email masking."""
        from codex.security import mask_email
        
        email = "user@example.com"
        masked = mask_email(email)
        
        assert "@" in masked
        assert "example.com" in masked
        assert "user" not in masked
    
    def test_mask_password_always_hidden(self):
        """Test password is always fully masked."""
        from codex.security import mask_password
        
        assert mask_password("mypassword123") == "***"
        assert mask_password("") == "(empty)"
        assert mask_password("a") == "***"
    
    def test_mask_sensitive_bidirectional(self):
        """Test mask_sensitive shows both ends."""
        from codex.security import mask_sensitive
        
        value = "secret_key_12345"
        masked = mask_sensitive(value, show_chars=4)
        
        assert masked.startswith("secr")
        assert masked.endswith("2345")
        assert "***" in masked


class TestLogSanitization:
    """Test log injection prevention."""
    
    def test_sanitize_removes_newlines(self):
        """Test newline removal prevents log injection."""
        from codex.security import sanitize_log
        
        malicious = "normal\nFAKE LOG: Admin access granted"
        sanitized = sanitize_log(malicious)
        
        assert "\n" not in sanitized
        assert "normal" in sanitized
        assert "FAKE LOG" in sanitized  # Content preserved
    
    def test_sanitize_removes_tabs(self):
        """Test tab character removal."""
        from codex.security import sanitize_log
        
        data = "column1\tcolumn2\tcolumn3"
        sanitized = sanitize_log(data)
        
        assert "\t" not in sanitized
    
    def test_sanitize_handles_none(self):
        """Test handling of None values."""
        from codex.security import sanitize_log
        
        assert sanitize_log(None) == "None"
    
    def test_sanitize_truncates_long_input(self):
        """Test truncation of excessively long input."""
        from codex.security import sanitize_log
        
        long_data = "a" * 1000
        sanitized = sanitize_log(long_data, max_length=100)
        
        assert len(sanitized) <= 120  # 100 + "[truncated]"
        assert "truncated" in sanitized or len(sanitized) == 100


class TestSecureHashing:
    """Test secure hashing functions."""
    
    def test_hash_secure_sha256(self):
        """Test SHA-256 hashing."""
        from codex.security import hash_secure
        
        token = "my_secret_token"
        hash1 = hash_secure(token)
        hash2 = hash_secure(token)
        
        # Deterministic
        assert hash1 == hash2
        # SHA-256 produces 64 hex characters
        assert len(hash1) == 64
        # Different input produces different hash
        assert hash_secure("different") != hash1
    
    def test_hash_secure_sha512(self):
        """Test SHA-512 hashing."""
        from codex.security import hash_secure
        
        token = "my_secret_token"
        hash_val = hash_secure(token, algorithm='sha512')
        
        # SHA-512 produces 128 hex characters
        assert len(hash_val) == 128
    
    def test_hash_secure_invalid_algorithm(self):
        """Test error on invalid algorithm."""
        from codex.security import hash_secure
        
        with pytest.raises(ValueError, match="Unsupported algorithm"):
            hash_secure("data", algorithm='md5')


class TestEncryptedStorage:
    """Test encrypted storage functionality."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def encryption_key(self, monkeypatch):
        """Set up encryption key for tests."""
        try:
            from codex.security.storage import generate_key
            key = generate_key()
            monkeypatch.setenv("ENCRYPTION_KEY", key)
            return key
        except ImportError:
            pytest.skip("cryptography package not installed")
    
    def test_store_and_load_secret(self, temp_dir, encryption_key):
        """Test basic encryption and decryption."""
        from codex.security.storage import SecureStorage
        
        storage = SecureStorage()
        secret = "my_api_key_12345"
        filepath = os.path.join(temp_dir, "secret.enc")
        
        # Store encrypted
        storage.store_secret(filepath, secret)
        assert os.path.exists(filepath)
        
        # Verify file is not plain text
        with open(filepath, 'rb') as f:
            encrypted_content = f.read()
        assert secret.encode() not in encrypted_content
        
        # Load and verify
        loaded = storage.load_secret(filepath)
        assert loaded == secret
    
    def test_secure_file_permissions(self, temp_dir, encryption_key):
        """Test file permissions are set securely."""
        from codex.security.storage import SecureStorage
        import stat
        
        storage = SecureStorage()
        filepath = os.path.join(temp_dir, "secret.enc")
        
        storage.store_secret(filepath, "secret_data")
        
        # Check permissions (owner read/write only)
        file_stat = os.stat(filepath)
        mode = file_stat.st_mode
        
        # Should be 0o600 (owner read/write)
        assert mode & stat.S_IRUSR  # Owner can read
        assert mode & stat.S_IWUSR  # Owner can write
        assert not (mode & stat.S_IRGRP)  # Group cannot read
        assert not (mode & stat.S_IROTH)  # Others cannot read
    
    def test_load_nonexistent_file(self, encryption_key):
        """Test error handling for missing files."""
        from codex.security.storage import SecureStorage
        
        storage = SecureStorage()
        
        with pytest.raises(FileNotFoundError):
            storage.load_secret("nonexistent.enc")
    
    def test_secret_exists_check(self, temp_dir, encryption_key):
        """Test checking if secret file exists."""
        from codex.security.storage import SecureStorage
        
        storage = SecureStorage()
        filepath = os.path.join(temp_dir, "secret.enc")
        
        assert not storage.secret_exists(filepath)
        
        storage.store_secret(filepath, "data")
        
        assert storage.secret_exists(filepath)


class TestIntegrationScenarios:
    """Test real-world usage scenarios."""
    
    def test_logging_pipeline(self):
        """Test complete logging pipeline with security."""
        from codex.security import mask_token, sanitize_log
        import logging
        from io import StringIO
        
        # Set up test logger
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        logger = logging.getLogger('test_security')
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        # Simulate logging with security
        api_key = "sk_live_abc123xyz789"
        user_input = "normal\nmalicious_injection"
        
        logger.info(f"API Key: {mask_token(api_key)}")
        logger.info(f"User data: {sanitize_log(user_input)}")
        
        # Verify log output
        log_output = log_stream.getvalue()
        
        assert "sk_live" not in log_output  # Key is masked
        assert "xyz789" in log_output  # Last 6 chars visible
        assert "\n" not in log_output.split("User data:")[1]  # Injection prevented
    
    def test_token_comparison_workflow(self):
        """Test secure token comparison workflow."""
        from codex.security import hash_secure
        
        # Simulate storing hashed token
        original_token = "user_api_token_12345"
        stored_hash = hash_secure(original_token)
        
        # Simulate token verification
        provided_token = "user_api_token_12345"
        provided_hash = hash_secure(provided_token)
        
        # Verify tokens match
        assert stored_hash == provided_hash
        
        # Verify different token doesn't match
        wrong_token = "wrong_token"
        wrong_hash = hash_secure(wrong_token)
        assert stored_hash != wrong_hash


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
