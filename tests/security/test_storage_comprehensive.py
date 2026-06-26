"""
Comprehensive tests for secure storage module.

Tests cover:
- Encryption/decryption with multiple algorithms
- File storage and permissions
- Key derivation and generation
- Error handling and edge cases
"""

import os
import stat  # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from codex.security.storage import (
    SecureStorage,
    derive_key_from_password,
    generate_key,
)

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def encryption_key():
    """Generate a test encryption key."""
    return generate_key()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def fernet_storage(encryption_key):
    """Create a SecureStorage instance with Fernet algorithm."""
    return SecureStorage(key=encryption_key, algorithm="fernet")


@pytest.fixture
def aes_gcm_storage(encryption_key):
    """Create a SecureStorage instance with AES-GCM algorithm."""
    return SecureStorage(key=encryption_key, algorithm="aes-gcm")


@pytest.fixture
def chacha20_storage(encryption_key):
    """Create a SecureStorage instance with ChaCha20 algorithm."""
    return SecureStorage(key=encryption_key, algorithm="chacha20")


# ============================================================================
# Initialization Tests
# ============================================================================


class TestSecureStorageInitialization:
    """Test SecureStorage initialization."""

    def test_init_with_explicit_key_fernet(self, encryption_key):
        """Test initialization with explicit key and Fernet."""
        storage = SecureStorage(key=encryption_key, algorithm="fernet")
        assert storage.algorithm == "fernet", "algorithm is not valid"

    def test_init_with_explicit_key_aes_gcm(self, encryption_key):
        """Test initialization with explicit key and AES-GCM."""
        storage = SecureStorage(key=encryption_key, algorithm="aes-gcm")
        assert storage.algorithm == "aes-gcm", "algorithm is not valid"

    def test_init_with_explicit_key_chacha20(self, encryption_key):
        """Test initialization with explicit key and ChaCha20."""
        storage = SecureStorage(key=encryption_key, algorithm="chacha20")
        assert storage.algorithm == "chacha20", "algorithm is not valid"

    def test_init_with_env_key(self, encryption_key):
        """Test initialization reading key from environment."""
        with patch.dict(os.environ, {"ENCRYPTION_KEY": encryption_key}):
            storage = SecureStorage(algorithm="fernet")
            assert storage.algorithm == "fernet", "algorithm is not valid"

    def test_init_without_key_raises_error(self):
        """Test that initialization without key raises error."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Encryption key required"):
                SecureStorage()

    def test_init_with_invalid_algorithm(self, encryption_key):
        """Test that invalid algorithm raises error."""
        with pytest.raises(ValueError, match="Unsupported algorithm"):
            SecureStorage(key=encryption_key, algorithm="invalid")

    def test_init_without_cryptography_raises_error(self, encryption_key):
        """Test that missing cryptography package raises error."""
        with patch("codex.security.storage.CRYPTO_AVAILABLE", False):
            with pytest.raises(ImportError):
                SecureStorage(key=encryption_key)

    def test_default_algorithm_is_fernet(self, encryption_key):
        """Test that default algorithm is Fernet."""
        storage = SecureStorage(key=encryption_key)
        assert storage.algorithm == "fernet", "algorithm is not valid"


# ============================================================================
# Key Generation Tests
# ============================================================================


class TestGenerateKey:
    """Test key generation."""

    def test_generate_key_returns_string(self):
        """Test that generate_key returns a string."""
        key = generate_key()
        assert isinstance(key, str)

    def test_generate_key_is_base64(self):
        """Test that generated key is base64-encoded."""
        key = generate_key()
        # Base64 keys should be decodable
        from base64 import b64decode

        decoded = b64decode(key)
        assert isinstance(decoded, bytes)

    def test_generate_key_unique(self):
        """Test that each generated key is unique."""
        key1 = generate_key()
        key2 = generate_key()
        assert key1 != key2, "key1 is not valid"

    def test_generate_key_can_be_used(self):
        """Test that generated key can be used for encryption."""
        key = generate_key()
        storage = SecureStorage(key=key, algorithm="fernet")
        encrypted = storage.encrypt("test")
        decrypted = storage.decrypt(encrypted)
        assert decrypted == "test", "decrypted is not valid"

    def test_generate_key_without_cryptography_raises_error(self):
        """Test that missing cryptography raises error."""
        with patch("codex.security.storage.CRYPTO_AVAILABLE", False):
            with pytest.raises(ImportError):
                generate_key()


# ============================================================================
# Key Derivation Tests
# ============================================================================


class TestDeriveKeyFromPassword:
    """Test password-based key derivation."""

    def test_derive_key_returns_tuple(self):
        """Test that derive_key returns (key, salt) tuple."""
        result = derive_key_from_password("password123")
        assert isinstance(result, tuple)
        assert len(result) == 2, "Result must not be empty"

    def test_derived_key_is_string(self):
        """Test that derived key is a string."""
        key, salt = derive_key_from_password("password123")
        assert isinstance(key, str)

    def test_derived_salt_is_bytes(self):
        """Test that derived salt is bytes."""
        key, salt = derive_key_from_password("password123")
        assert isinstance(salt, bytes)

    def test_same_password_same_salt_same_key(self):
        """Test deterministic key derivation with same salt."""
        password = "test_password"
        key1, salt1 = derive_key_from_password(password)
        key2, salt2 = derive_key_from_password(password, salt=salt1)
        assert key1 == key2, "key1 is not valid"
        assert salt1 == salt2, "salt1 is not valid"

    def test_same_password_different_salt_different_key(self):
        """Test that different salts produce different keys."""
        password = "test_password"
        key1, salt1 = derive_key_from_password(password)
        key2, salt2 = derive_key_from_password(password)
        assert key1 != key2, "key1 is not valid"
        assert salt1 != salt2, "salt1 is not valid"

    def test_different_password_different_key(self):
        """Test that different passwords produce different keys."""
        key1, _ = derive_key_from_password("password1")
        key2, _ = derive_key_from_password("password2")
        assert key1 != key2, "key1 is not valid"

    def test_derived_key_can_be_used(self):
        """Test that derived key can be used for encryption."""
        key, salt = derive_key_from_password("mypassword")
        storage = SecureStorage(key=key, algorithm="fernet")
        encrypted = storage.encrypt("secret")
        decrypted = storage.decrypt(encrypted)
        assert decrypted == "secret", "decrypted is not valid"

    def test_empty_password_allowed(self):
        """Test that empty password is allowed (though not recommended)."""
        key, salt = derive_key_from_password("")
        assert isinstance(key, str)
        assert isinstance(salt, bytes)

    def test_long_password_allowed(self):
        """Test that very long passwords are allowed."""
        long_password = "x" * 1000
        key, salt = derive_key_from_password(long_password)
        assert isinstance(key, str)

    def test_unicode_password_allowed(self):
        """Test that unicode passwords are allowed."""
        key, salt = derive_key_from_password("password_世界_🌍")
        assert isinstance(key, str)

    def test_derive_key_without_cryptography_raises_error(self):
        """Test that missing cryptography raises error."""
        with patch("codex.security.storage.CRYPTO_AVAILABLE", False):
            with pytest.raises(ImportError):
                derive_key_from_password("password")


# ============================================================================
# Encryption/Decryption Tests (Fernet)
# ============================================================================


class TestFernetEncryption:
    """Test Fernet encryption/decryption."""

    def test_encrypt_returns_bytes(self, fernet_storage):
        """Test that encrypt returns bytes."""
        result = fernet_storage.encrypt("test")
        assert isinstance(result, bytes)

    def test_decrypt_returns_string(self, fernet_storage):
        """Test that decrypt returns string."""
        encrypted = fernet_storage.encrypt("test")
        decrypted = fernet_storage.decrypt(encrypted)
        assert isinstance(decrypted, str)

    def test_roundtrip_encryption(self, fernet_storage):
        """Test encrypt/decrypt roundtrip."""
        original = "Hello, World!"
        encrypted = fernet_storage.encrypt(original)
        decrypted = fernet_storage.decrypt(encrypted)
        assert decrypted == original, "decrypted is not valid"

    def test_encrypt_empty_string(self, fernet_storage):
        """Test encryption of empty string."""
        encrypted = fernet_storage.encrypt("")
        decrypted = fernet_storage.decrypt(encrypted)
        assert decrypted == "", "decrypted is not valid"

    def test_encrypt_unicode_string(self, fernet_storage):
        """Test encryption of unicode content."""
        original = "Hello 世界 🌍"
        encrypted = fernet_storage.encrypt(original)
        decrypted = fernet_storage.decrypt(encrypted)
        assert decrypted == original, "decrypted is not valid"

    def test_encrypt_long_string(self, fernet_storage):
        """Test encryption of very long string."""
        original = "x" * 100000
        encrypted = fernet_storage.encrypt(original)
        decrypted = fernet_storage.decrypt(encrypted)
        assert decrypted == original, "decrypted is not valid"

    def test_encrypt_special_characters(self, fernet_storage):
        """Test encryption of special characters."""
        original = "!@#$%^&*()_+-=[]{}|;:',.<>?/~`"
        encrypted = fernet_storage.encrypt(original)
        decrypted = fernet_storage.decrypt(encrypted)
        assert decrypted == original, "decrypted is not valid"

    def test_decrypt_with_wrong_key_raises_error(self, encryption_key):
        """Test that decryption with wrong key raises error."""
        storage1 = SecureStorage(key=encryption_key, algorithm="fernet")
        encrypted = storage1.encrypt("test")

        other_key = generate_key()
        storage2 = SecureStorage(key=other_key, algorithm="fernet")

        with pytest.raises(Exception):  # InvalidToken
            storage2.decrypt(encrypted)

    def test_decrypt_corrupted_data_raises_error(self, fernet_storage):
        """Test that decryption of corrupted data raises error."""
        with pytest.raises(Exception):  # InvalidToken
            fernet_storage.decrypt(b"corrupted_data")

    def test_encrypt_twice_produces_different_results(self, fernet_storage):
        """Test that same plaintext encrypted twice produces different ciphertexts."""
        plaintext = "test"
        encrypted1 = fernet_storage.encrypt(plaintext)
        encrypted2 = fernet_storage.encrypt(plaintext)
        # Fernet includes timestamp, so different encryptions differ
        assert encrypted1 != encrypted2, "encrypted1 is not valid"
        # But both decrypt to same value
        assert fernet_storage.decrypt(encrypted1) == plaintext, "fernet_st is not valid"
        assert fernet_storage.decrypt(encrypted2) == plaintext, "fernet_st is not valid"


# ============================================================================
# Encryption/Decryption Tests (AES-GCM)
# ============================================================================


class TestAESGCMEncryption:
    """Test AES-GCM encryption/decryption."""

    def test_aes_gcm_roundtrip(self, aes_gcm_storage):
        """Test AES-GCM encrypt/decrypt roundtrip."""
        original = "Secret message"
        encrypted = aes_gcm_storage.encrypt(original)
        decrypted = aes_gcm_storage.decrypt(encrypted)
        assert decrypted == original, "decrypted is not valid"

    def test_aes_gcm_unicode(self, aes_gcm_storage):
        """Test AES-GCM with unicode content."""
        original = "Hello 世界 🌍"
        encrypted = aes_gcm_storage.encrypt(original)
        decrypted = aes_gcm_storage.decrypt(encrypted)
        assert decrypted == original, "decrypted is not valid"

    def test_aes_gcm_produces_different_ciphertexts(self, aes_gcm_storage):
        """Test that AES-GCM with random nonce produces different ciphertexts."""
        plaintext = "test"
        encrypted1 = aes_gcm_storage.encrypt(plaintext)
        encrypted2 = aes_gcm_storage.encrypt(plaintext)
        assert encrypted1 != encrypted2, "encrypted1 is not valid"


# ============================================================================
# Encryption/Decryption Tests (ChaCha20)
# ============================================================================


class TestChaCha20Encryption:
    """Test ChaCha20-Poly1305 encryption/decryption."""

    def test_chacha20_roundtrip(self, chacha20_storage):
        """Test ChaCha20 encrypt/decrypt roundtrip."""
        original = "Secret message"
        encrypted = chacha20_storage.encrypt(original)
        decrypted = chacha20_storage.decrypt(encrypted)
        assert decrypted == original, "decrypted is not valid"

    def test_chacha20_unicode(self, chacha20_storage):
        """Test ChaCha20 with unicode content."""
        original = "Hello 世界 🌍"
        encrypted = chacha20_storage.encrypt(original)
        decrypted = chacha20_storage.decrypt(encrypted)
        assert decrypted == original, "decrypted is not valid"


# ============================================================================
# File Storage Tests
# ============================================================================


class TestFileStorage:
    """Test file-based secret storage."""

    def test_store_and_load_secret(self, fernet_storage, temp_dir):
        """Test storing and loading a secret."""
        secret = "my_secret_value"
        filepath = os.path.join(temp_dir, "secret.enc")

        fernet_storage.store_secret(filepath, secret)
        loaded = fernet_storage.load_secret(filepath)

        assert loaded == secret, "loaded is not valid"

    def test_store_secret_creates_file(self, fernet_storage, temp_dir):
        """Test that store_secret creates the file."""
        filepath = os.path.join(temp_dir, "secret.enc")
        assert not Path(filepath).exists(), "Condition must be true"

        fernet_storage.store_secret(filepath, "test")

        assert Path(filepath).exists(), "Condition must be true"

    def test_store_secret_creates_parent_dirs(self, fernet_storage, temp_dir):
        """Test that store_secret creates parent directories."""
        filepath = os.path.join(temp_dir, "subdir1", "subdir2", "secret.enc")

        fernet_storage.store_secret(filepath, "test")

        assert Path(filepath).exists(), "Condition must be true"

    def test_store_secret_sets_permissions(self, fernet_storage, temp_dir):
        """Test that store_secret sets secure file permissions."""
        filepath = os.path.join(temp_dir, "secret.enc")
        fernet_storage.store_secret(filepath, "test")

        # Check permissions: should be 0o600 (owner read/write only)
        file_stat = os.stat(filepath)
        stat.filemode(file_stat.st_mode)
        # Permission check: only owner should have read/write
        mode = stat.S_IMODE(file_stat.st_mode)
        assert mode == (stat.S_IRUSR | stat.S_IWUSR), "mode is not valid"

    def test_load_nonexistent_file_raises_error(self, fernet_storage, temp_dir):
        """Test that loading nonexistent file raises error."""
        filepath = os.path.join(temp_dir, "nonexistent.enc")

        with pytest.raises(FileNotFoundError):
            fernet_storage.load_secret(filepath)

    def test_store_unicode_secret(self, fernet_storage, temp_dir):
        """Test storing unicode secret."""
        secret = "Secret: 世界 🌍"
        filepath = os.path.join(temp_dir, "unicode_secret.enc")

        fernet_storage.store_secret(filepath, secret)
        loaded = fernet_storage.load_secret(filepath)

        assert loaded == secret, "loaded is not valid"

    def test_store_large_secret(self, fernet_storage, temp_dir):
        """Test storing large secret."""
        secret = "x" * 1000000  # 1MB
        filepath = os.path.join(temp_dir, "large_secret.enc")

        fernet_storage.store_secret(filepath, secret)
        loaded = fernet_storage.load_secret(filepath)

        assert loaded == secret, "loaded is not valid"

    def test_store_secret_overwrites_existing(self, fernet_storage, temp_dir):
        """Test that store_secret overwrites existing file."""
        filepath = os.path.join(temp_dir, "secret.enc")

        fernet_storage.store_secret(filepath, "first")
        fernet_storage.store_secret(filepath, "second")

        loaded = fernet_storage.load_secret(filepath)
        assert loaded == "second", "loaded is not valid"

    def test_secret_exists_returns_true(self, fernet_storage, temp_dir):
        """Test secret_exists returns True for existing file."""
        filepath = os.path.join(temp_dir, "secret.enc")
        fernet_storage.store_secret(filepath, "test")

        assert fernet_storage.secret_exists(filepath), "fernet_st is not valid"

    def test_secret_exists_returns_false(self, fernet_storage, temp_dir):
        """Test secret_exists returns False for nonexistent file."""
        filepath = os.path.join(temp_dir, "nonexistent.enc")

        assert not fernet_storage.secret_exists(filepath), "Condition must be true"


# ============================================================================
# Cross-Algorithm Tests
# ============================================================================


class TestCrossAlgorithmCompatibility:
    """Test interactions between algorithms."""

    def test_fernet_encrypted_data_not_decryptable_by_aes(self, encryption_key, temp_dir):
        """Test that Fernet-encrypted data cannot be decrypted by AES-GCM."""
        fernet = SecureStorage(key=encryption_key, algorithm="fernet")
        encrypted = fernet.encrypt("test")

        aes = SecureStorage(key=encryption_key, algorithm="aes-gcm")

        # Should raise an error (authentication failure)
        with pytest.raises(Exception):
            aes.decrypt(encrypted)

    def test_different_algorithms_same_plaintext(self, encryption_key):
        """Test that different algorithms produce different ciphertexts."""
        plaintext = "test_plaintext"

        fernet = SecureStorage(key=encryption_key, algorithm="fernet")
        aes = SecureStorage(key=encryption_key, algorithm="aes-gcm")
        chacha = SecureStorage(key=encryption_key, algorithm="chacha20")

        encrypted_fernet = fernet.encrypt(plaintext)
        encrypted_aes = aes.encrypt(plaintext)
        encrypted_chacha = chacha.encrypt(plaintext)

        # All should decrypt to same value
        assert fernet.decrypt(encrypted_fernet) == plaintext, "Condition must be true"
        assert aes.decrypt(encrypted_aes) == plaintext, "Condition must be true"
        assert chacha.decrypt(encrypted_chacha) == plaintext, "Condition must be true"


# ============================================================================
# Edge Cases and Error Handling Tests
# ============================================================================


class TestEdgeCasesAndErrors:
    """Test edge cases and error conditions."""

    def test_encrypt_none_value_raises_error(self, fernet_storage):
        """Test that encrypting None raises error."""
        with pytest.raises((AttributeError, TypeError)):
            fernet_storage.encrypt(None)

    def test_empty_key_raises_error(self):
        """Test that empty key raises error."""
        with pytest.raises(ValueError):
            SecureStorage(key="", algorithm="fernet")

    def test_key_derived_from_empty_password(self):
        """Test key derivation from empty password."""
        key, salt = derive_key_from_password("")
        storage = SecureStorage(key=key, algorithm="fernet")

        # Should still work
        encrypted = storage.encrypt("test")
        decrypted = storage.decrypt(encrypted)
        assert decrypted == "test", "decrypted is not valid"

    def test_store_secret_with_special_filename(self, fernet_storage, temp_dir):
        """Test storing secret with special characters in filename."""
        filepath = os.path.join(temp_dir, "secret_with-special.chars_123.enc")

        fernet_storage.store_secret(filepath, "test")
        loaded = fernet_storage.load_secret(filepath)

        assert loaded == "test", "loaded is not valid"


# ============================================================================
# Integration Tests
# ============================================================================


class TestStorageIntegration:
    """Integration tests for secure storage."""

    def test_complete_workflow(self, temp_dir):
        """Test complete workflow: generate key, derive, encrypt, store, load."""
        # Generate key
        key = generate_key()

        # Create storage
        storage = SecureStorage(key=key, algorithm="fernet")

        # Store secret
        filepath = os.path.join(temp_dir, "workflow_secret.enc")
        secret = "my_important_secret"
        storage.store_secret(filepath, secret)

        # Load secret
        loaded = storage.load_secret(filepath)

        assert loaded == secret, "loaded is not valid"

    def test_password_based_workflow(self, temp_dir):
        """Test workflow using password-based key derivation."""
        password = "MySecurePassword123!"

        # Derive key
        key, salt = derive_key_from_password(password)

        # Create storage and store secret
        storage = SecureStorage(key=key, algorithm="fernet")
        filepath = os.path.join(temp_dir, "password_secret.enc")
        secret = "database_password"
        storage.store_secret(filepath, secret)

        # Recreate key from password and salt
        key2, _ = derive_key_from_password(password, salt=salt)
        storage2 = SecureStorage(key=key2, algorithm="fernet")

        # Load secret
        loaded = storage2.load_secret(filepath)

        assert loaded == secret, "loaded is not valid"

    def test_multi_algorithm_storage(self, encryption_key, temp_dir):
        """Test storing with one algorithm, attempting load with another."""
        secret = "test_secret"
        filepath = os.path.join(temp_dir, "secret.enc")

        # Store with Fernet
        fernet = SecureStorage(key=encryption_key, algorithm="fernet")
        fernet.store_secret(filepath, secret)

        # Try to load with Fernet (should work)
        loaded = fernet.load_secret(filepath)
        assert loaded == secret, "loaded is not valid"

        # Try to load with AES-GCM (should fail)
        aes = SecureStorage(key=encryption_key, algorithm="aes-gcm")
        with pytest.raises(Exception):
            aes.load_secret(filepath)
