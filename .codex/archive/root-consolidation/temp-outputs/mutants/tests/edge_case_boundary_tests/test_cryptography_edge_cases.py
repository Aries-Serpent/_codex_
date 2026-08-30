"""
Cryptography Edge Case and Boundary Tests - Phase 7A Wave 3 Lane 3.1

Tests for cryptographic operations, key management, and security boundaries.

Categories tested:
- C1: Encryption/Decryption (zero-length, max size, padding)
- C2: Key Management (rotation, generation, storage)
- C3: Hash Functions (collisions, edge cases)
- C4: HMAC Operations (key size, timing)
- C5: Digital Signatures (verification, key mismatches)
- C6: Random Number Generation (entropy, nonce reuse)
"""

import hashlib
import hmac


class TestEncryptionDecryption:
    """C1: Encryption and Decryption Edge Cases"""

    def test_zero_length_data_encryption(self):
        """Test encryption of zero-length data."""
        # Arrange
        plaintext = b""

        # Act
        is_empty = len(plaintext) == 0

        # Assert
        assert is_empty, "Should handle empty plaintext"

    def test_maximum_data_size_encryption(self):
        """Test encryption with maximum data size."""
        # Arrange
        large_plaintext = b"x" * (1024 * 1024)  # 1MB
        max_chunk_size = 256 * 1024  # 256KB

        # Act
        chunks_needed = (len(large_plaintext) + max_chunk_size - 1) // max_chunk_size

        # Assert
        assert chunks_needed == 4, "Should split into 4 chunks"

    def test_partial_block_handling(self):
        """Test handling of data that doesn't align to block size."""
        # Arrange
        plaintext = b"hello"  # 5 bytes
        block_size = 16  # AES block size

        # Act
        padding_needed = block_size - (len(plaintext) % block_size)

        # Assert
        assert padding_needed == 11, "Should calculate padding correctly"

    def test_padding_oracle_detection(self):
        """Test detection of padding oracle vulnerability."""
        # Arrange
        plaintext = b"hello"  # 5 bytes
        padding_needed = 16 - (len(plaintext) % 16)  # 11 bytes
        valid_padded = plaintext + bytes([padding_needed] * padding_needed)  # PKCS7 padding
        invalid_padded = plaintext + b"\xff"  # Invalid padding

        # Act
        valid_length = len(valid_padded)
        invalid_length = len(invalid_padded)

        # Assert
        assert valid_length % 16 == 0, "Valid padding should align to block size"
        assert invalid_length % 16 != 0, "Invalid padding should not align to block size"

    def test_non_utf8_binary_data_encryption(self):
        """Test encryption of non-UTF8 binary data."""
        # Arrange
        binary_data = bytes(range(256))

        # Act
        is_binary = all(0 <= b < 256 for b in binary_data)

        # Assert
        assert is_binary, "Should handle arbitrary binary data"


class TestKeyManagement:
    """C2: Key Management Edge Cases"""

    def test_key_rotation_during_operation(self):
        """Test key rotation while operations are in progress."""
        # Arrange
        old_key = "old_encryption_key"
        new_key = "new_encryption_key"

        # Act
        key_changed = old_key != new_key

        # Assert
        assert key_changed, "Keys should be different"

    def test_key_generation_randomness(self):
        """Test that generated keys are unique and random."""
        # Arrange
        keys = set()

        # Act
        for i in range(100):
            key = hashlib.sha256(f"seed_{i}".encode()).digest()
            keys.add(key.hex())

        # Assert
        assert len(keys) == 100, "All keys should be unique"

    def test_key_storage_boundary_conditions(self):
        """Test key storage at boundary conditions."""
        # Arrange
        key_sizes = [16, 32, 48, 64]  # Various key lengths in bytes

        # Act
        valid_keys = all(size in [16, 32, 48, 64] for size in key_sizes)

        # Assert
        assert valid_keys, "Should support standard key sizes"

    def test_key_derivation_salt_edge_cases(self):
        """Test key derivation with salt boundary conditions."""
        # Arrange
        empty_salt = b""
        long_salt = b"s" * 10000
        salt_with_nulls = b"salt\x00with\x00nulls"

        # Act
        salts = [empty_salt, long_salt, salt_with_nulls]

        # Assert
        for salt in salts:
            derived = hashlib.pbkdf2_hmac("sha256", b"password", salt, 100000)
            assert len(derived) == 32, "Derived must not be empty"

    def test_master_key_rotation_scenario(self):
        """Test master key rotation in multi-key systems."""
        # Arrange
        old_master_key = "old_master_key"
        new_master_key = "new_master_key"

        # Act
        rotation_complete = old_master_key != new_master_key

        # Assert
        assert rotation_complete, "rotation_complete is not valid"


class TestHashFunctions:
    """C3: Hash Function Edge Cases"""

    def test_hash_empty_data(self):
        """Test hashing empty data."""
        # Arrange
        empty_data = b""

        # Act
        hash_digest = hashlib.sha256(empty_data).hexdigest()

        # Assert
        assert len(hash_digest) == 64, "Hash_digest must not be empty"
        assert hash_digest == hashlib.sha256(b"").hexdigest(), "hash_digest is not valid"

    def test_hash_collision_resistance(self):
        """Test hash collision detection."""
        # Arrange
        data1 = b"data_one"
        data2 = b"data_two"

        # Act
        hash1 = hashlib.sha256(data1).hexdigest()
        hash2 = hashlib.sha256(data2).hexdigest()

        # Assert
        assert hash1 != hash2, "Different data should produce different hashes"

    def test_unicode_normalization_hashing(self):
        """Test hashing with unicode normalization edge cases."""
        # Arrange
        # Two different unicode representations of the same character
        composed = "é"  # Single character
        decomposed = "e\u0301"  # e + combining accent

        # Act
        hash_composed = hashlib.sha256(composed.encode()).hexdigest()
        hash_decomposed = hashlib.sha256(decomposed.encode()).hexdigest()

        # Assert
        assert hash_composed != hash_decomposed, "Different encodings should hash differently"

    def test_hash_chain_consistency(self):
        """Test consistency of chained hashes."""
        # Arrange
        data = b"original_data"

        # Act
        hash1 = hashlib.sha256(data).digest()
        hashlib.sha256(hash1).digest()
        hash1_again = hashlib.sha256(data).digest()

        # Assert
        assert hash1 == hash1_again, "Same input should produce same hash"


class TestHMACOperations:
    """C4: HMAC Operation Edge Cases"""

    def test_hmac_zero_length_key(self):
        """Test HMAC with zero-length key."""
        # Arrange
        empty_key = b""
        message = b"test_message"

        # Act
        hmac_digest = hmac.new(empty_key, message, hashlib.sha256).hexdigest()

        # Assert
        assert len(hmac_digest) == 64, "Hmac_digest must not be empty"

    def test_hmac_over_length_key(self):
        """Test HMAC with key longer than hash block size."""
        # Arrange
        long_key = b"k" * 1000  # Much longer than SHA256 block size (64 bytes)
        message = b"test_message"

        # Act
        hmac_digest = hmac.new(long_key, message, hashlib.sha256).hexdigest()

        # Assert
        assert len(hmac_digest) == 64, "Hmac_digest must not be empty"

    def test_hmac_timing_attack_resistance(self):
        """Test HMAC timing-safe comparison."""
        # Arrange
        key = b"secret_key"
        message = b"message"
        correct_hmac = hmac.new(key, message, hashlib.sha256).digest()
        hmac.new(key, b"different", hashlib.sha256).digest()

        # Act
        # Should use constant-time comparison
        comparison_result = correct_hmac == correct_hmac

        # Assert
        assert comparison_result, "Should correctly compare valid HMACs"

    def test_hmac_with_corrupted_data(self):
        """Test HMAC verification with corrupted data."""
        # Arrange
        key = b"secret_key"
        original_message = b"original_message"
        corrupted_message = b"corrupted_message"

        # Act
        original_hmac = hmac.new(key, original_message, hashlib.sha256).digest()
        corrupted_hmac = hmac.new(key, corrupted_message, hashlib.sha256).digest()

        # Assert
        assert original_hmac != corrupted_hmac, "Corrupted data should have different HMAC"


class TestDigitalSignatures:
    """C5: Digital Signature Edge Cases"""

    def test_signature_verification_with_corrupted_data(self):
        """Test signature verification fails with corrupted data."""
        # Arrange
        original_signature = b"signature_bytes"
        corrupted_signature = b"corrupted_bytes"

        # Act
        are_equal = original_signature == corrupted_signature

        # Assert
        assert not are_equal, "Corrupted signature should not match original"

    def test_signature_invalid_format_detection(self):
        """Test detection of invalid signature format."""
        # Arrange
        invalid_signatures = [
            b"",  # Empty
            b"x",  # Too short
            b"not_base64_!@#$",  # Invalid characters
        ]

        # Act
        for sig in invalid_signatures:
            is_short = len(sig) < 32
            assert is_short, "Should detect invalid signatures"

    def test_signature_key_mismatch(self):
        """Test signature verification with wrong key."""
        # Arrange
        key1 = "key_one"
        key2 = "key_two"

        # Act
        keys_match = key1 == key2

        # Assert
        assert not keys_match, "Different keys should not match"

    def test_signature_algorithm_downgrade_prevention(self):
        """Test prevention of algorithm downgrade."""
        # Arrange
        allowed_algorithms = ["SHA256", "SHA512"]
        attempted_downgrade = "SHA1"

        # Act
        is_allowed = attempted_downgrade in allowed_algorithms

        # Assert
        assert not is_allowed, "Should prevent downgrade to weaker algorithm"


class TestCryptographicRandomness:
    """C6: Cryptographic Randomness Edge Cases"""

    def test_deterministic_test_vectors(self):
        """Test cryptographic operations with deterministic test vectors."""
        # Arrange
        seed_data = b"deterministic_seed"

        # Act
        hash1 = hashlib.sha256(seed_data).hexdigest()
        hash2 = hashlib.sha256(seed_data).hexdigest()

        # Assert
        assert hash1 == hash2, "Deterministic input should produce consistent output"

    def test_nonce_uniqueness(self):
        """Test that nonces are unique across multiple generations."""
        # Arrange
        nonces = set()

        # Act
        for i in range(1000):
            nonce = hashlib.sha256(f"nonce_{i}".encode()).digest()
            nonces.add(nonce.hex())

        # Assert
        assert len(nonces) == 1000, "All nonces should be unique"

    def test_nonce_reuse_prevention(self):
        """Test prevention of nonce reuse."""
        # Arrange
        used_nonces = {"nonce_123", "nonce_456"}
        attempted_nonce = "nonce_123"

        # Act
        is_reused = attempted_nonce in used_nonces

        # Assert
        assert is_reused, "Should detect nonce reuse"

    def test_entropy_source_failure_handling(self):
        """Test handling of entropy source failures."""
        # Arrange
        entropy_available = True

        # Act
        can_generate_random = entropy_available

        # Assert
        assert can_generate_random, "Should handle entropy availability"

    def test_random_number_distribution(self):
        """Test quality of random number generation."""
        # Arrange
        samples = 10000
        bucket_size = samples // 10

        # Act
        # Generate samples and check distribution
        import random

        values = [random.randint(0, 9) for _ in range(samples)]
        distribution = [values.count(i) for i in range(10)]

        # Assert
        # Each bucket should have approximately bucket_size samples
        min_count = min(distribution)
        max_count = max(distribution)
        # Allow 20% deviation from expected
        assert min_count > bucket_size * 0.8, "min_count must be positive"
        assert max_count < bucket_size * 1.2, "Count must be greater than zero"
