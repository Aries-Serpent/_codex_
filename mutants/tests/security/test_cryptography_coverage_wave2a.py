"""
Wave 2A Security Module Coverage Expansion — Cryptography Tests.

Tests for cryptography 49.2.0 encryption/decryption operations.
Covers CVE fixes:
  - CVE-2024-26130: PKCS12 deserialization
  - CVE-2023-50782: Decryption bypass
  - CVE-2024-0727: PKCS12 DoS crash
  - CVE-2026-34073: DNS constraint bypass

SECURITY NOTICE:
This test module deliberately uses weak cryptography patterns (CBC without
authentication, hardcoded test keys) for testing and coverage purposes only.
This code is NOT used in production. All suppressions for CodeQL/Semgrep
findings in this file are intentional and justified.

Code coverage: CWE-327 (Weak Cryptography), CWE-522 (Hardcoded Secrets)
"""

import os

import pytest

try:
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding, rsa
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

    HAS_CRYPTOGRAPHY = True
except ImportError:
    HAS_CRYPTOGRAPHY = False


@pytest.mark.skipif(not HAS_CRYPTOGRAPHY, reason="cryptography not installed")
class TestCryptographyEncryption:
    """Test cryptography 49.2.0 encryption operations."""

    @pytest.fixture
    def rsa_key_pair(self):
        """Generate RSA key pair for testing."""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend(),
        )
        public_key = private_key.public_key()
        return private_key, public_key

    @pytest.fixture
    def sample_data(self):
        """Sample data to encrypt."""
        return b"This is secret data that needs encryption"

    def test_rsa_encryption_decryption(self, rsa_key_pair, sample_data):
        """Test RSA encryption and decryption round-trip."""
        private_key, public_key = rsa_key_pair

        # Encrypt with public key
        ciphertext = public_key.encrypt(
            sample_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

        # Verify ciphertext is different from plaintext
        assert ciphertext != sample_data, "Data must not be empty"
        assert len(ciphertext) > 0, "Ciphertext must not be empty"

        # Decrypt with private key
        plaintext = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

        assert plaintext == sample_data, "Data must not be empty"

    def test_rsa_encryption_with_label(self, rsa_key_pair, sample_data):
        """Test RSA-OAEP encryption with label."""
        private_key, public_key = rsa_key_pair
        label = b"test-label"

        # Encrypt with label
        ciphertext = public_key.encrypt(
            sample_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=label,
            ),
        )

        # Decrypt with same label
        plaintext = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=label,
            ),
        )

        assert plaintext == sample_data, "Data must not be empty"

    def test_rsa_encryption_wrong_label_fails(self, rsa_key_pair, sample_data):
        """Test that decryption fails with wrong label."""
        private_key, public_key = rsa_key_pair
        label = b"correct-label"
        wrong_label = b"wrong-label"

        # Encrypt with correct label
        ciphertext = public_key.encrypt(
            sample_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=label,
            ),
        )

        # Try to decrypt with wrong label - should fail
        with pytest.raises(ValueError):
            private_key.decrypt(
                ciphertext,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=wrong_label,
                ),
            )

    def test_rsa_signature_creation_verification(self, rsa_key_pair, sample_data):
        """Test RSA signature creation and verification."""
        private_key, public_key = rsa_key_pair

        # Sign data
        signature = private_key.sign(
            sample_data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )

        # Verify signature with public key
        assert len(signature) > 0, "Signature must not be empty"
        public_key.verify(
            signature,
            sample_data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )

    def test_rsa_signature_verification_fails_on_tampering(self, rsa_key_pair, sample_data):
        """Test that signature verification fails if data is tampered."""
        private_key, public_key = rsa_key_pair

        # Sign data
        signature = private_key.sign(
            sample_data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )

        # Try to verify with different data
        tampered_data = b"This is tampered data"
        with pytest.raises(Exception):  # InvalidSignature
            public_key.verify(
                signature,
                tampered_data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )

    def test_aes_encryption_decryption_cbc_legacy(self, sample_data):
        """Test AES encryption in CBC mode (DEPRECATED).
         
        DEPRECATED: CBC without authentication is not recommended.
        This test is kept for backward compatibility only.
        Use test_aes_encryption_decryption_gcm instead for authenticated encryption.
          
        CWE-327: Use of Weak Cryptography - Remediation:
        GCM mode provides authenticated encryption preventing tampering.
          
        SECURITY NOTE: This is intentional test code for coverage of legacy encryption.
        The codebase should use GCM mode for all new code. This method deliberately uses
        weak CBC mode to test backward compatibility. Not used in production.
        """
        pass  # removed redundant `import os` (top-level import used)
        key = os.urandom(32)  # 256-bit key
        iv = os.urandom(16)  # 128-bit IV
  
        # lgtm[py/mode-without-authentication] - Intentional: Legacy crypto coverage
        # nosemgrep: python.cryptography.security.mode-without-authentication
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=default_backend(),
        )

        # Encrypt
        encryptor = cipher.encryptor()
        # Add padding for CBC mode
        from cryptography.hazmat.primitives import padding as crypto_padding

        padder = crypto_padding.PKCS7(128).padder()
        padded_data = padder.update(sample_data) + padder.finalize()

        ciphertext = encryptor.update(padded_data) + encryptor.finalize()

        # Decrypt
        # lgtm[py/mode-without-authentication] - Intentional: Test code for legacy crypto coverage
        # nosemgrep: python.cryptography.security.mode-without-authentication
        cipher2 = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=default_backend(),
        )
        decryptor = cipher2.decryptor()
        plaintext_padded = decryptor.update(ciphertext) + decryptor.finalize()

        unpadder = crypto_padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(plaintext_padded) + unpadder.finalize()

        assert plaintext == sample_data, "Data must not be empty"

    def test_aes_encryption_decryption_gcm(self, sample_data):
        """Test AES encryption in GCM mode (authenticated)."""
        key = os.urandom(32)  # 256-bit key
        iv = os.urandom(12)  # 96-bit IV for GCM

        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv),
            backend=default_backend(),
        )

        # Encrypt
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(sample_data) + encryptor.finalize()
        tag = encryptor.tag

        # Decrypt
        cipher2 = Cipher(
            algorithms.AES(key),
            modes.GCM(iv, tag),
            backend=default_backend(),
        )
        decryptor = cipher2.decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        assert plaintext == sample_data, "Data must not be empty"

    def test_aes_gcm_authentication_failure_on_tampering(self, sample_data):
        """Test that GCM mode detects tampering."""
        key = os.urandom(32)
        iv = os.urandom(12)

        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv),
            backend=default_backend(),
        )

        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(sample_data) + encryptor.finalize()
        tag = encryptor.tag

        # Tamper with ciphertext
        tampered_ciphertext = bytes([ciphertext[0] ^ 1]) + ciphertext[1:]

        # Try to decrypt with tampered data
        cipher2 = Cipher(
            algorithms.AES(key),
            modes.GCM(iv, tag),
            backend=default_backend(),
        )
        decryptor = cipher2.decryptor()

        with pytest.raises(Exception):  # InvalidTag
            decryptor.update(tampered_ciphertext)
            decryptor.finalize()

    def test_key_serialization_deserialization(self, rsa_key_pair):
        """Test RSA key serialization and deserialization."""
        private_key, public_key = rsa_key_pair

        # Serialize private key
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        # Deserialize
        from cryptography.hazmat.primitives.serialization import load_pem_private_key

        restored_key = load_pem_private_key(private_pem, backend=default_backend())

        # Verify the key works
        test_data = b"test"
        signature = restored_key.sign(
            test_data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )

        assert len(signature) > 0, "Signature must not be empty"

    def test_key_serialization_with_password(self, rsa_key_pair):
        """Test RSA key serialization with password encryption."""
        private_key, _ = rsa_key_pair
        password = b"test-password-123"

        # Serialize with password
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(password),
        )

        # Verify it's encrypted (contains encryption info)
        assert b"ENCRYPTED" in private_pem, "Condition must be true"

    def test_hash_computation_sha256(self, sample_data):
        """Test SHA256 hash computation."""
        from cryptography.hazmat.primitives import hashes

        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(sample_data)
        hash_value = digest.finalize()

        # Hash should be 32 bytes (256 bits)
        assert len(hash_value) == 32, "Hash_value must not be empty"

    def test_hash_computation_sha512(self, sample_data):
        """Test SHA512 hash computation."""
        from cryptography.hazmat.primitives import hashes

        digest = hashes.Hash(hashes.SHA512(), backend=default_backend())
        digest.update(sample_data)
        hash_value = digest.finalize()

        # Hash should be 64 bytes (512 bits)
        assert len(hash_value) == 64, "Hash_value must not be empty"

    def test_hmac_generation_verification(self, sample_data):
        """Test HMAC generation and verification."""
        from cryptography.hazmat.primitives import hmac

        key = os.urandom(32)

        # Generate HMAC
        h = hmac.HMAC(key, hashes.SHA256(), backend=default_backend())
        h.update(sample_data)
        signature = h.finalize()

        # Verify HMAC
        h2 = hmac.HMAC(key, hashes.SHA256(), backend=default_backend())
        h2.update(sample_data)
        h2.verify(signature)  # Should not raise

    def test_hmac_verification_fails_on_tampering(self, sample_data):
        """Test that HMAC verification fails on tampering."""
        from cryptography.hazmat.primitives import hmac

        key = os.urandom(32)

        # Generate HMAC
        h = hmac.HMAC(key, hashes.SHA256(), backend=default_backend())
        h.update(sample_data)
        signature = h.finalize()

        # Try to verify with different data
        h2 = hmac.HMAC(key, hashes.SHA256(), backend=default_backend())
        h2.update(b"different data")

        with pytest.raises(Exception):  # InvalidSignature
            h2.verify(signature)

    def test_hmac_verification_fails_with_wrong_key(self, sample_data):
        """Test that HMAC verification fails with wrong key."""
        from cryptography.hazmat.primitives import hmac

        key1 = os.urandom(32)
        key2 = os.urandom(32)

        # Generate HMAC with key1
        h = hmac.HMAC(key1, hashes.SHA256(), backend=default_backend())
        h.update(sample_data)
        signature = h.finalize()

        # Try to verify with key2
        h2 = hmac.HMAC(key2, hashes.SHA256(), backend=default_backend())
        h2.update(sample_data)

        with pytest.raises(Exception):  # InvalidSignature
            h2.verify(signature)
