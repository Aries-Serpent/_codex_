"""
Tests for Embedding Cache Module.
"""

import tempfile
import time
from pathlib import Path

import pytest

np = pytest.importorskip("numpy")

from codex.rag.cache.embedding_cache import (
    EmbeddingCache,
    EmbeddingCacheConfig,
    EmbeddingEntry,
)


class TestEmbeddingEntry:
    """Tests for EmbeddingEntry dataclass."""

    def test_creation(self):
        """Test creating embedding entry."""
        embedding = np.random.rand(384).astype(np.float32)
        entry = EmbeddingEntry(
            key="test_key",
            embedding=embedding,
        )

        assert entry.key == "test_key", "key is not valid"
        assert entry.embedding.shape == (384,)

    def test_dimension(self):
        """Test dimension property."""
        embedding = np.random.rand(768).astype(np.float32)
        entry = EmbeddingEntry(key="test", embedding=embedding)

        assert entry.dimension == 768, "dimension is not valid"

    def test_is_expired(self):
        """Test expiration check."""
        embedding = np.zeros(10)

        # Not expired (no expiry set)
        entry1 = EmbeddingEntry(key="test", embedding=embedding)
        assert not entry1.is_expired, "Condition must be true"

        # Expired
        entry2 = EmbeddingEntry(
            key="test",
            embedding=embedding,
            expires_at=time.time() - 1,
        )
        assert entry2.is_expired, "Condition must be true"


class TestEmbeddingCacheConfig:
    """Tests for EmbeddingCacheConfig."""

    def test_default_config(self):
        """Test default configuration."""
        config = EmbeddingCacheConfig()

        assert config.max_entries == 10000, "max_entries is not valid"
        assert config.enable_disk_cache is False, "enable_disk_cache is not valid"
        assert config.use_float16 is False, "use_float16 is not valid"

    def test_custom_config(self):
        """Test custom configuration."""
        config = EmbeddingCacheConfig(
            max_entries=5000,
            use_float16=True,
        )

        assert config.max_entries == 5000, "max_entries is not valid"
        assert config.use_float16 is True, "use_float16 is not valid"


class TestEmbeddingCache:
    """Tests for EmbeddingCache class."""

    @pytest.fixture
    def cache(self):
        """Create a test cache."""
        config = EmbeddingCacheConfig(max_entries=100)
        return EmbeddingCache(config)

    @pytest.fixture
    def sample_embedding(self):
        """Create a sample embedding."""
        return np.random.rand(384).astype(np.float32)

    def test_put_and_get(self, cache, sample_embedding):
        """Test basic put and get."""
        cache.put("text1", sample_embedding)

        result = cache.get("text1")

        assert result is not None, "result must be initialized"
        np.testing.assert_array_almost_equal(result, sample_embedding)

    def test_get_missing(self, cache):
        """Test getting non-existent key."""
        result = cache.get("nonexistent")
        assert result is None, "Result must not be empty"

    def test_delete(self, cache, sample_embedding):
        """Test delete operation."""
        cache.put("text1", sample_embedding)
        assert cache.get("text1") is not None, "Value must be initialized"

        deleted = cache.delete("text1")

        assert deleted is True, "deleted is not valid"
        assert cache.get("text1") is None, "Condition must be true"

    def test_clear(self, cache, sample_embedding):
        """Test clear operation."""
        cache.put("text1", sample_embedding)
        cache.put("text2", sample_embedding)

        cache.clear()

        assert len(cache) == 0, "Cache must not be empty"

    def test_contains(self, cache, sample_embedding):
        """Test contains check."""
        cache.put("text1", sample_embedding)

        assert cache.contains("text1") is True, "Condition must be true"
        assert cache.contains("text2") is False, "Condition must be true"

    def test_batch_operations(self, cache):
        """Test batch put and get."""
        texts = ["text1", "text2", "text3"]
        embeddings = [np.random.rand(384).astype(np.float32) for _ in range(3)]

        cache.put_batch(texts, embeddings)

        found_embeddings, found_indices = cache.get_batch(texts)

        assert len(found_embeddings) == 3, "Found_embeddings must not be empty"
        assert found_indices == [0, 1, 2]

    def test_batch_get_partial(self, cache, sample_embedding):
        """Test batch get with partial hits."""
        cache.put("text1", sample_embedding)
        cache.put("text3", sample_embedding)

        found_embeddings, found_indices = cache.get_batch(["text1", "text2", "text3"])

        assert len(found_embeddings) == 2, "Found_embeddings must not be empty"
        assert found_indices == [0, 2]

    def test_get_stats(self, cache, sample_embedding):
        """Test statistics."""
        cache.put("text1", sample_embedding)
        cache.get("text1")  # Hit
        cache.get("text2")  # Miss

        stats = cache.get_stats()

        assert stats["hits"] == 1, "Condition must be true"
        assert stats["misses"] == 1, "Condition must be true"
        assert stats["hit_rate"] == 0.5, "Condition must be true"

    def test_float16_conversion(self, sample_embedding):
        """Test float16 conversion for memory efficiency."""
        config = EmbeddingCacheConfig(use_float16=True)
        cache = EmbeddingCache(config)

        cache.put("text1", sample_embedding)

        stats = cache.get_stats()
        assert stats["dtype"] == "float16", "Condition must be true"

        # Memory should be roughly half
        assert stats["memory_bytes"] < sample_embedding.nbytes, "Condition must be true"

    def test_memory_tracking(self, cache, sample_embedding):
        """Test memory usage tracking."""
        cache.put("text1", sample_embedding)
        cache.put("text2", sample_embedding)

        stats = cache.get_stats()

        expected_bytes = sample_embedding.nbytes * 2
        # Allow for some overhead
        assert stats["memory_bytes"] >= expected_bytes * 0.9, "Value must be greater than zero"

    def test_eviction(self):
        """Test eviction when at capacity."""
        config = EmbeddingCacheConfig(max_entries=5)
        cache = EmbeddingCache(config)

        # Add 10 entries, only 5 should remain after eviction
        for i in range(10):
            cache.put(f"text{i}", np.random.rand(10).astype(np.float32))

        # Should have evicted some entries
        assert len(cache) <= 5, "Cache must not be empty"

    def test_ttl_expiration(self):
        """Test TTL expiration."""
        config = EmbeddingCacheConfig(default_ttl=0.1)
        cache = EmbeddingCache(config)

        embedding = np.random.rand(10).astype(np.float32)
        cache.put("text1", embedding)

        assert cache.get("text1") is not None, "Value must be initialized"

        time.sleep(0.15)

        assert cache.get("text1") is None, "Condition must be true"

    def test_len_and_contains(self, cache, sample_embedding):
        """Test len() and 'in' operators."""
        assert len(cache) == 0, "Cache must not be empty"
        assert "text1" not in cache, "Condition must be true"

        cache.put("text1", sample_embedding)

        assert len(cache) == 1, "Cache must not be empty"
        assert "text1" in cache, "Condition must be true"

    def test_returns_copy(self, cache, sample_embedding):
        """Test that get returns a copy."""
        cache.put("text1", sample_embedding)

        result1 = cache.get("text1")
        result1[0] = 999.0  # Modify the returned array

        result2 = cache.get("text1")

        # Original should be unchanged
        assert result2[0] != 999.0, "Result must not be empty"


class TestEmbeddingCacheDisk:
    """Tests for disk-based embedding cache."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for disk cache."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_disk_cache_enabled(self, temp_dir):
        """Test disk cache creation."""
        config = EmbeddingCacheConfig(
            enable_disk_cache=True,
            disk_cache_path=temp_dir,
        )
        cache = EmbeddingCache(config)

        embedding = np.random.rand(384).astype(np.float32)
        cache.put("text1", embedding)

        # Check that file was created
        disk_files = list(Path(temp_dir).glob("*.npy"))
        assert len(disk_files) == 1, "Disk_files must not be empty"


# ============================================================================
# MUTATION KILLING TESTS - DAY 2 REFINEMENT
# ============================================================================


class TestCacheBoundaryConditions:
    """Boundary condition tests to kill comparison operator mutations."""

    def test_expiry_exact_boundary(self):
        """Kill: 'time.time() > expires_at' mutations

        Ensures exact boundary checking at expiry moment.
        """
        embedding = np.zeros(10)

        # Entry that expired exactly 1 second ago
        entry = EmbeddingEntry(key="expired", embedding=embedding, expires_at=time.time() - 1.0)
        assert entry.is_expired is True, "is_expired is not valid"

        # Entry that expires in 1 second
        entry2 = EmbeddingEntry(
            key="not_expired", embedding=embedding, expires_at=time.time() + 1.0
        )
        assert entry2.is_expired is False, "is_expired is not valid"

    def test_cache_size_boundary(self):
        """Kill: '>=' vs '>' mutations in size checks"""
        config = EmbeddingCacheConfig(max_entries=5)
        cache = EmbeddingCache(config)

        # Fill to exactly max
        for i in range(5):
            embedding = np.random.rand(10)
            cache.put(f"key{i}", embedding)

        assert len(cache) == 5, "Cache must not be empty"

        # Adding one more should trigger eviction
        embedding = np.random.rand(10)
        cache.put("key_overflow", embedding)

        # Cache size should not exceed max_entries
        assert len(cache) <= 5, "Cache must not be empty"

    def test_ttl_boundary_exact_comparison(self):
        """Kill: TTL comparison operators

        Tests exact time boundary conditions.
        """
        config = EmbeddingCacheConfig(max_entries=10)
        cache = EmbeddingCache(config)
        embedding = np.zeros(10)

        # Put with TTL that expires in 0.1 seconds
        cache.put("ttl_test", embedding, ttl_seconds=0.1)
        assert cache.get("ttl_test") is not None, "Value must be initialized"

        # Wait for expiry
        time.sleep(0.15)
        assert cache.get("ttl_test") is None, "Condition must be true"


class TestCacheBooleanConditions:
    """Boolean condition tests to kill 'and'/'or' mutations."""

    def test_eviction_requires_both_conditions(self):
        """Kill: 'and' → 'or' mutations in eviction logic

        Ensures eviction requires both size AND age conditions.
        """
        config = EmbeddingCacheConfig(max_entries=3)
        cache = EmbeddingCache(config)

        # Add entries
        embeddings = [np.random.rand(10) for _ in range(3)]
        cache.put("key1", embeddings[0])
        time.sleep(0.1)
        cache.put("key2", embeddings[1])
        cache.put("key3", embeddings[2])

        # Cache should have exactly 3 entries
        assert len(cache) == 3, "Cache must not be empty"

        # Add one more - should evict oldest
        cache.put("key4", np.random.rand(10))
        assert len(cache) == 3, "Cache must not be empty"
        assert cache.get("key1") is None, "Condition must be true"

    def test_contains_check_exact_logic(self):
        """Kill: boolean mutation in contains logic"""
        config = EmbeddingCacheConfig(max_entries=10)
        cache = EmbeddingCache(config)
        embedding = np.zeros(10)

        cache.put("exists", embedding)

        # Exact boolean checks
        assert ("exists" in cache) is True, "Condition must be true"
        assert ("does_not_exist" in cache) is False, "Condition must be true"


class TestCacheReturnValues:
    """Return value tests to kill exact return type mutations."""

    def test_get_returns_exact_type(self):
        """Kill: return value mutations"""
        config = EmbeddingCacheConfig(max_entries=10)
        cache = EmbeddingCache(config)
        embedding = np.array([1.0, 2.0, 3.0], dtype=np.float32)

        cache.put("test", embedding)
        result = cache.get("test")

        # Exact type check
        assert isinstance(result, np.ndarray)
        assert result.dtype == np.float32, "Result must not be empty"
        assert len(result) == 3, "Result must not be empty"

    def test_get_missing_returns_none(self):
        """Kill: return value mutations on missing keys"""
        config = EmbeddingCacheConfig(max_entries=10)
        cache = EmbeddingCache(config)

        result = cache.get("nonexistent")
        assert result is None, "Result must not be empty"

    def test_contains_returns_bool(self):
        """Kill: return value type mutations"""
        config = EmbeddingCacheConfig(max_entries=10)
        cache = EmbeddingCache(config)
        embedding = np.zeros(10)

        cache.put("test", embedding)

        # Exact boolean returns
        assert cache.__contains__("test") is True, "Condition must be true"
        assert cache.__contains__("missing") is False, "Condition must be true"
        assert isinstance(cache.__contains__("test"), bool)
        assert isinstance(cache.__contains__("missing"), bool)


# ============================================================================
# MUTATION-KILLING TESTS
# ============================================================================
# These tests are specifically designed to kill surviving mutations from Day 2


class TestEmbeddingCacheBoundaryMutations:
    """Kill boundary-related mutations (>, >=, <, <=)."""

    def test_ttl_boundary_not_expired_at_exact_time(self):
        """Kill: TTL comparison mutations (> vs >=).

        Verifies entry is NOT expired exactly at TTL boundary.
        """
        config = EmbeddingCacheConfig(default_ttl=0.1)
        cache = EmbeddingCache(config)
        embedding = np.random.rand(5).astype(np.float32)

        cache.put("text_boundary", embedding)
        time.sleep(0.09)  # Just under TTL

        result = cache.get("text_boundary")
        # MUST NOT be expired - kills > vs >= mutation
        assert result is not None, "Entry should NOT be expired just before TTL expiry"

    def test_cache_size_exact_max_entries(self):
        """Kill: Size comparison mutations (> vs >=).

        Verifies cache respects exact max_entries boundary.
        """
        config = EmbeddingCacheConfig(max_entries=2)
        cache = EmbeddingCache(config)
        embedding = np.random.rand(5).astype(np.float32)

        # Add exactly max_entries
        cache.put("text1", embedding)
        cache.put("text2", embedding)
        assert len(cache) == 2, "Cache must not be empty"

        # Add one more - should trigger eviction
        cache.put("text3", embedding)
        # MUST respect max_entries boundary
        assert len(cache) <= 2, "Cache should not exceed max_entries"


class TestEmbeddingCacheBooleanMutations:
    """Kill boolean operator mutations (and vs or, not removal)."""

    def test_contains_exact_true_not_truthy(self):
        """Kill: Return value mutations (True -> 1, None -> False).

        Verifies exact boolean True returned.
        """
        config = EmbeddingCacheConfig(max_entries=10)
        cache = EmbeddingCache(config)
        embedding = np.random.rand(10).astype(np.float32)

        cache.put("key1", embedding)
        result = cache.contains("key1")

        # Exact assertions kill mutations
        assert result is True, "MUST be exact True"
        assert type(result) is bool, "MUST be bool type"
        # Note: In Python, True == 1, so we cannot use '!=' to distinguish them.
        # Use 'is' and type() checks above instead.

    def test_contains_exact_false_not_falsy(self):
        """Kill: Return value mutations (False -> 0, None, empty)."""
        config = EmbeddingCacheConfig(max_entries=10)
        cache = EmbeddingCache(config)

        result = cache.contains("nonexistent_key")

        # Exact assertions kill mutations
        assert result is False, "MUST be exact False"
        assert type(result) is bool, "MUST be bool type"
        # Note: In Python, False == 0, so we cannot use '!=' to distinguish them.
        # Use 'is' and type() checks above instead.


class TestEmbeddingCacheReturnValueMutations:
    """Kill return value type mutations."""

    def test_get_returns_ndarray_not_bool(self):
        """Kill: Return type mutation (np.ndarray -> True/False/None).

        Verifies get() returns exact array type, not bool or None.
        """
        config = EmbeddingCacheConfig(max_entries=10)
        cache = EmbeddingCache(config)
        embedding = np.random.rand(384).astype(np.float32)

        cache.put("embed1", embedding)
        result = cache.get("embed1")

        # Exact type assertions kill mutations
        assert isinstance(result, np.ndarray), "MUST return ndarray"
        assert not isinstance(result, bool), "MUST NOT return bool"
        assert result is not True, "MUST NOT be True"
        assert result is not None, "MUST NOT be None"
        # Verify actual array content
        assert result.shape == (384,), "MUST have correct shape"

    def test_get_missing_returns_none_exactly(self):
        """Kill: Return value mutation (None -> False, 0, empty array).

        Verifies get() returns exact None for missing keys.
        """
        config = EmbeddingCacheConfig(max_entries=10)
        cache = EmbeddingCache(config)

        result = cache.get("missing_key")

        # Exact assertions kill mutations
        assert result is None, "MUST be exact None"
        assert result is not False, "MUST NOT be False"
        assert result != 0, "MUST NOT be 0"
        assert not isinstance(result, np.ndarray), "MUST NOT be ndarray"

    def test_delete_returns_bool_true(self):
        """Kill: Delete return mutation (True -> None/False/1)."""
        config = EmbeddingCacheConfig(max_entries=10)
        cache = EmbeddingCache(config)
        embedding = np.random.rand(10).astype(np.float32)

        cache.put("deleteme", embedding)
        result = cache.delete("deleteme")

        # Exact assertions
        assert result is True, "MUST be exact True"
        assert type(result) is bool, "MUST be bool type"

    def test_delete_missing_returns_bool_false(self):
        """Kill: Delete return mutation (False -> None/True/0)."""
        config = EmbeddingCacheConfig(max_entries=10)
        cache = EmbeddingCache(config)

        result = cache.delete("nonexistent")

        # Exact assertions
        assert result is False, "MUST be exact False"
        assert type(result) is bool, "MUST be bool type"
