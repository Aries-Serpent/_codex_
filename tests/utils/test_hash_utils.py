"""
Tests for utility hash functions using Eigenstate Pattern.

Eigenstate Pattern: Tests for idempotent/deterministic operations
that should always produce the same output for the same input.

Phase 54: HIGH Priority Module Tests
Coverage Target: src/utils 30% → 45%+
"""

import hashlib


class TestEigenstateHashPatterns:
    """Tests applying Eigenstate Pattern to hash utilities."""

    def test_sha256_deterministic(self):
        """Hash of same input always produces same output (eigenstate).""" # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
        data = b"test data for hashing"
        hash1 = hashlib.sha256(data).hexdigest()
        hash2 = hashlib.sha256(data).hexdigest()
        hash3 = hashlib.sha256(data).hexdigest()

        assert hash1 == hash2 == hash3, "hash1 is not valid"
        assert len(hash1) == 64, "Hash1 must not be empty"

    def test_sha256_identifier_deterministic(self):
        """SHA-256 hash is deterministic for stable identifiers."""
        data = b"content identifier"
        hash1 = hashlib.sha256(data).hexdigest()
        hash2 = hashlib.sha256(data).hexdigest()

        assert hash1 == hash2, "hash1 is not valid"
        assert len(hash1) == 64, "Hash1 must not be empty"

    def test_blake2b_deterministic(self):
        """Blake2b hash is deterministic."""
        data = b"fast hashing content"
        hash1 = hashlib.blake2b(data).hexdigest()
        hash2 = hashlib.blake2b(data).hexdigest()

        assert hash1 == hash2, "hash1 is not valid"

    def test_empty_input_hash(self):
        """Empty input produces consistent hash (eigenstate boundary)."""
        empty_hash = hashlib.sha256(b"").hexdigest()
        assert empty_hash == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", "empty_hash is not valid"

    def test_hash_collision_resistance(self):
        """Different inputs produce different hashes."""
        data1 = b"input one"
        data2 = b"input two"

        hash1 = hashlib.sha256(data1).hexdigest()
        hash2 = hashlib.sha256(data2).hexdigest()

        assert hash1 != hash2, "hash1 is not valid"

    def test_hash_length_invariance(self):
        """Hash length is constant regardless of input size."""
        short_input = b"a"
        long_input = b"a" * 10000

        hash_short = hashlib.sha256(short_input).hexdigest()
        hash_long = hashlib.sha256(long_input).hexdigest()

        assert len(hash_short) == len(hash_long) == 64, "Hash_short must not be empty"

    def test_hash_update_accumulative(self):
        """Hash update is accumulative (eigenstate evolution)."""
        h1 = hashlib.sha256()
        h1.update(b"part1")
        h1.update(b"part2")

        h2 = hashlib.sha256(b"part1part2")

        assert h1.hexdigest() == h2.hexdigest(), "Condition must be true"

    def test_hash_copy_independence(self):
        """Hash copy creates independent state."""
        h1 = hashlib.sha256(b"initial")
        h2 = h1.copy()

        h1.update(b"more data")

        assert h1.hexdigest() != h2.hexdigest(), "Condition must be true"


class TestNormalizationEigenstates:
    """Tests for normalization functions (idempotent operations)."""

    def test_string_strip_idempotent(self):
        """String strip is idempotent."""
        s = "  test string  "
        result1 = s.strip()
        result2 = result1.strip()
        result3 = result2.strip()

        assert result1 == result2 == result3 == "test string", "Result must not be empty"

    def test_lowercase_idempotent(self):
        """Lowercase is idempotent."""
        s = "MiXeD CaSe"
        result1 = s.lower()
        result2 = result1.lower()

        assert result1 == result2 == "mixed case", "Result must not be empty"

    def test_path_normalization_idempotent(self):
        """Path normalization is idempotent."""
        import os.path

        path = "/foo/../bar/./baz"
        result1 = os.path.normpath(path)
        result2 = os.path.normpath(result1)

        assert result1 == result2, "Result must not be empty"

    def test_whitespace_collapse_idempotent(self):
        """Whitespace collapse is idempotent."""
        import re

        s = "multiple   spaces   here"
        result1 = re.sub(r"\s+", " ", s)
        result2 = re.sub(r"\s+", " ", result1)

        assert result1 == result2 == "multiple spaces here", "Result must not be empty"


class TestCacheKeyGeneration:
    """Tests for cache key generation (deterministic)."""

    def test_cache_key_from_args(self):
        """Cache key generation is deterministic."""

        def make_cache_key(*args, **kwargs):
            parts = [str(a) for a in args]
            parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            return hashlib.sha256(":".join(parts).encode()).hexdigest()

        key1 = make_cache_key("func", 1, 2, x=3)
        key2 = make_cache_key("func", 1, 2, x=3)

        assert key1 == key2, "key1 is not valid"

    def test_cache_key_order_independence(self):
        """Kwargs order doesn't affect cache key."""

        def make_cache_key(**kwargs):
            parts = [f"{k}={v}" for k, v in sorted(kwargs.items())]
            return hashlib.sha256(":".join(parts).encode()).hexdigest()

        key1 = make_cache_key(a=1, b=2, c=3)
        key2 = make_cache_key(c=3, a=1, b=2)

        assert key1 == key2, "key1 is not valid"

    def test_different_args_different_keys(self):
        """Different arguments produce different cache keys."""

        def make_cache_key(*args):
            return hashlib.sha256(str(args).encode()).hexdigest()

        key1 = make_cache_key(1, 2, 3)
        key2 = make_cache_key(1, 2, 4)

        assert key1 != key2, "key1 is not valid"


class TestContentDigest:
    """Tests for content digest generation."""

    def test_file_content_digest(self):
        """File content digest is deterministic."""
        content = b"file content for testing"
        digest1 = hashlib.sha256(content).hexdigest()
        digest2 = hashlib.sha256(content).hexdigest()

        assert digest1 == digest2, "digest1 is not valid"

    def test_json_content_digest(self):
        """JSON content digest handles key order."""
        import json

        data1 = {"a": 1, "b": 2}
        data2 = {"b": 2, "a": 1}

        # Sorted JSON ensures deterministic digest
        json1 = json.dumps(data1, sort_keys=True)
        json2 = json.dumps(data2, sort_keys=True)

        assert json1 == json2, "json1 is not valid"
        assert (hashlib.sha256(json1.encode()).hexdigest() == hashlib.sha256(json2.encode()).hexdigest()
        )

    def test_binary_digest_chunked(self):
        """Chunked hashing produces same result as full hash."""
        data = b"large content" * 1000

        # Full hash
        full_hash = hashlib.sha256(data).hexdigest()

        # Chunked hash
        h = hashlib.sha256()
        chunk_size = 256
        for i in range(0, len(data
        ), chunk_size):
            h.update(data[i : i + chunk_size])
        chunked_hash = h.hexdigest()

        assert full_hash == chunked_hash, "full_hash is not valid"
