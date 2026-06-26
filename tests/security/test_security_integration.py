"""
Integration tests for security modules.
"""

import os
import tempfile

import pytest


class TestSecurityMasking:
    """Test sensitive data masking functions."""  # pragma: allowlist secret # pragma: allowlist secret

    def test_mask_token_standard(self):
        """Test standard token masking."""
        from codex.security import mask_token

        token = "sk_live_abc123xyz789"
        masked = mask_token(token)

        # Default shows last 4 characters
        assert "z789" in masked, "Condition must be true"
        assert "sk_live" not in masked, "Condition must be true"
        assert len(masked) == len(token), "Masked must not be empty"

    def test_mask_email(self):
        """Test email masking."""
        from codex.security import mask_email

        email = "user@example.com"
        masked = mask_email(email)

        assert "@" in masked, "Condition must be true"
        # Verify domain is preserved - this is intentional for email masking
        # Note: For URL validation, use sanitize_url() instead
        assert masked.endswith("@example.com"), f"Domain validation failed: {masked}"
        assert "user" not in masked, "Condition must be true"

    def test_mask_email_preserves_domain(self):
        """Test that email masking correctly preserves the full domain."""
        from codex.security import mask_email

        # These should all preserve the domain correctly
        assert mask_email("admin@example.com").endswith("@example.com"), "Condition must be true"
        assert mask_email("test@subdomain.example.com").endswith("@subdomain.example.com"), "Condition must be true"
        assert "@" in mask_email("user@test.org"), "Condition must be true"


class TestURLSanitization:
    """Test URL sanitization to prevent substring injection attacks."""

    def test_sanitize_url_allows_exact_domain(self):
        """Test that exact domain matches are allowed."""
        from codex.security import sanitize_url

        assert sanitize_url("http://example.com", ["example.com"]) is True
        assert sanitize_url("https://example.com/path", ["example.com"]) is True
        assert sanitize_url("http://example.com:8080/api", ["example.com"]) is True

    def test_sanitize_url_allows_subdomains(self):
        """Test that valid subdomains are allowed."""
        from codex.security import sanitize_url

        assert sanitize_url("http://api.example.com", ["example.com"]) is True
        assert sanitize_url("https://www.example.com", ["example.com"]) is True
        assert sanitize_url("http://subdomain.api.example.com", ["example.com"]) is True

    def test_sanitize_url_blocks_path_injection(self):
        """Test that domain in path is blocked (HIGH SEVERITY)."""
        from codex.security import sanitize_url

        # These should all be blocked - domain appears in path, not netloc
        assert sanitize_url("http://evil.com/example.com", ["example.com"]) is False
        assert sanitize_url("https://malicious.org/path/example.com", ["example.com"]) is False
        assert sanitize_url("http://attacker.net/redirect?to=example.com", ["example.com"]) is False

    def test_sanitize_url_blocks_domain_prefix_attack(self):
        """Test that domains with allowed domain as suffix are blocked."""
        from codex.security import sanitize_url

        # These should be blocked - not a subdomain, just has the string as suffix
        assert sanitize_url("http://evilexample.com", ["example.com"]) is False
        assert sanitize_url("https://fakeexample.com/api", ["example.com"]) is False
        assert sanitize_url("http://notexample.com", ["example.com"]) is False

    def test_sanitize_url_blocks_domain_suffix_attack(self):
        """Test that domains with allowed domain followed by other chars are blocked."""
        from codex.security import sanitize_url

        # These should be blocked - domain followed by malicious suffix
        assert sanitize_url("http://example.com.evil.com", ["example.com"]) is False
        assert sanitize_url("https://example.com.attacker.net", ["example.com"]) is False
        assert sanitize_url("http://example.com-phishing.org", ["example.com"]) is False

    def test_sanitize_url_handles_empty_input(self):
        """Test handling of empty or invalid URLs."""
        from codex.security import sanitize_url

        assert sanitize_url("", ["example.com"]) is False
        assert sanitize_url("not-a-url", ["example.com"]) is False
        assert sanitize_url("javascript:alert(1)", ["example.com"]) is False

    def test_sanitize_url_case_insensitive(self):
        """Test that domain matching is case-insensitive."""
        from codex.security import sanitize_url

        assert sanitize_url("http://EXAMPLE.COM", ["example.com"]) is True
        assert sanitize_url("http://Example.Com/path", ["example.com"]) is True
        assert sanitize_url("http://API.EXAMPLE.COM", ["example.com"]) is True

    def test_sanitize_url_multiple_allowed_domains(self):
        """Test validation with multiple allowed domains."""
        from codex.security import sanitize_url

        allowed = ["example.com", "trusted.org", "api.service.net"]

        assert sanitize_url("http://example.com", allowed) is True
        assert sanitize_url("https://trusted.org", allowed) is True
        assert sanitize_url("http://api.service.net", allowed) is True
        assert sanitize_url("http://evil.com", allowed) is False

    def test_sanitize_url_no_allowed_domains(self):
        """Test that without allowed domains, any valid URL passes."""
        from codex.security import sanitize_url

        # When allowed_domains is None, just check for valid URL structure
        assert sanitize_url("http://example.com", None) is True
        assert sanitize_url("https://any-domain.org", None) is True
        assert sanitize_url("", None) is False

    def test_mask_password_always_hidden(self):
        """Test password is always fully masked."""
        from codex.security import mask_password

        assert mask_password("mypassword123") == "***", "mask_passw is not valid"
        assert mask_password("") == "(empty)", "mask_passw is not valid"
        assert mask_password("a") == "***", "mask_passw is not valid"

    def test_mask_sensitive_bidirectional(self):
        """Test mask_sensitive shows both ends."""
        from codex.security import mask_sensitive

        value = "secret_key_12345"
        masked = mask_sensitive(value, show_chars=4)

        assert masked.startswith("secr"), "Condition must be true"
        assert masked.endswith("2345"), "Condition must be true"
        assert "***" in masked, "Condition must be true"


class TestLogSanitization:
    """Test log injection prevention."""

    def test_sanitize_removes_newlines(self):
        """Test newline removal prevents log injection."""
        from codex.security import sanitize_log

        malicious = "normal\nFAKE LOG: Admin access granted"
        sanitized = sanitize_log(malicious)

        assert "\n" not in sanitized, "Condition must be true"
        assert "normal" in sanitized, "Condition must be true"
        assert "FAKE LOG" in sanitized, "Condition must be true"

    def test_sanitize_removes_tabs(self):
        """Test tab character removal."""
        from codex.security import sanitize_log

        data = "column1\tcolumn2\tcolumn3"
        sanitized = sanitize_log(data)

        assert "\t" not in sanitized, "Condition must be true"

    def test_sanitize_handles_none(self):
        """Test handling of None values."""
        from codex.security import sanitize_log

        assert sanitize_log(None) == "None", "Condition must be true"

    def test_sanitize_truncates_long_input(self):
        """Test truncation of excessively long input."""
        from codex.security import sanitize_log

        long_data = "a" * 1000
        sanitized = sanitize_log(long_data, max_length=100)

        assert len(sanitized) <= 120, "Sanitized must not be empty"
        assert "truncated" in sanitized or len(sanitized) == 100, "Sanitized must not be empty"


class TestSecureHashing:
    """Test secure hashing functions."""

    def test_hash_secure_sha256(self):
        """Test SHA-256 hashing."""
        from codex.security import hash_secure

        token = "my_secret_token"
        hash1 = hash_secure(token)
        hash2 = hash_secure(token)

        # Deterministic
        assert hash1 == hash2, "hash1 is not valid"
        # SHA-256 produces 64 hex characters
        assert len(hash1) == 64, "Hash1 must not be empty"
        # Different input produces different hash
        assert hash_secure("different") != hash1, "Condition must be true"

    def test_hash_secure_sha512(self):
        """Test SHA-512 hashing."""
        from codex.security import hash_secure

        token = "my_secret_token"
        hash_val = hash_secure(token, algorithm="sha512")

        # SHA-512 produces 128 hex characters
        assert len(hash_val) == 128, "Hash_val must not be empty"

    def test_hash_secure_invalid_algorithm(self):
        """Test error on invalid algorithm."""
        from codex.security import hash_secure

        with pytest.raises(ValueError, match="Unsupported algorithm"):
            hash_secure("data", algorithm="md5")


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
        except ImportError:
            raise pytest.skip.Exception("cryptography package not installed")
        monkeypatch.setenv("ENCRYPTION_KEY", key)
        return key

    def test_store_and_load_secret(self, temp_dir, encryption_key):
        """Test basic encryption and decryption."""
        from codex.security.storage import SecureStorage

        storage = SecureStorage()
        secret = "my_api_key_12345"  # pragma: allowlist secret
        filepath = os.path.join(temp_dir, "secret.enc")

        # Store encrypted
        storage.store_secret(filepath, secret)
        assert os.path.exists(filepath), "Condition must be true"

        # Verify file is not plain text
        with open(filepath, "rb") as f:
            encrypted_content = f.read()
        assert secret.encode() not in encrypted_content, "Content must not be empty"

        # Load and verify
        loaded = storage.load_secret(filepath)
        assert loaded == secret, "loaded is not valid"

    def test_secure_file_permissions(self, temp_dir, encryption_key):
        """Test file permissions are set securely."""
        import stat

        from codex.security.storage import SecureStorage

        storage = SecureStorage()
        filepath = os.path.join(temp_dir, "secret.enc")

        storage.store_secret(filepath, "secret_data")

        # Check permissions (owner read/write only)
        file_stat = os.stat(filepath)
        mode = file_stat.st_mode

        # Should be 0o600 (owner read/write)
        assert mode & stat.S_IRUSR, "Condition must be true"
        assert mode & stat.S_IWUSR, "Condition must be true"
        assert not (mode & stat.S_IRGRP), "Condition must be true"
        assert not (mode & stat.S_IROTH), "Condition must be true"

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

        assert not storage.secret_exists(filepath), "Condition must be true"

        storage.store_secret(filepath, "data")

        assert storage.secret_exists(filepath), "st is not valid"


class TestIntegrationScenarios:
    """Test real-world usage scenarios."""

    def test_logging_pipeline(self):
        """Test complete logging pipeline with security."""
        import logging
        from io import StringIO

        from codex.security import mask_token, sanitize_log

        # Keep this test isolated even if prior tests globally disabled logging.
        previous_disable_level = logging.root.manager.disable
        logging.disable(logging.NOTSET)

        # Set up test logger
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        logger = logging.getLogger("test_security")
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

        try:
            # Simulate logging with security
            api_key = "sk_live_abc123xyz789"  # pragma: allowlist secret
            user_input = "normal\nmalicious_injection"

            logger.info(f"API Key: {mask_token(api_key)}")
            logger.info(f"User data: {sanitize_log(user_input)}")

            # Verify log output
            log_output = log_stream.getvalue()

            assert "sk_live" not in log_output, "Condition must be true"
            assert "z789" in log_output, "Condition must be true"
            # Check that the malicious newline was removed from user input
            user_data_line = log_output.split("User data:")[1].strip()
            assert "normalmalicious_injection" in user_data_line, "Data must not be empty"
        finally:
            logger.removeHandler(handler)
            handler.close()
            logging.disable(previous_disable_level)

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
        assert stored_hash == provided_hash, "stored_hash is not valid"

        # Verify different token doesn't match
        wrong_token = "wrong_token"
        wrong_hash = hash_secure(wrong_token)
        assert stored_hash != wrong_hash, "stored_hash is not valid"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
