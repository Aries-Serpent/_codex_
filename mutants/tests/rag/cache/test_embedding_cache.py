"""
Tests for Embedding Cache Module.
"""

import pytest
import numpy as np
import tempfile
import time
from pathlib import Path

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
        
        assert entry.key == "test_key"
        assert entry.embedding.shape == (384,)
    
    def test_dimension(self):
        """Test dimension property."""
        embedding = np.random.rand(768).astype(np.float32)
        entry = EmbeddingEntry(key="test", embedding=embedding)
        
        assert entry.dimension == 768
    
    def test_is_expired(self):
        """Test expiration check."""
        embedding = np.zeros(10)
        
        # Not expired (no expiry set)
        entry1 = EmbeddingEntry(key="test", embedding=embedding)
        assert not entry1.is_expired
        
        # Expired
        entry2 = EmbeddingEntry(
            key="test",
            embedding=embedding,
            expires_at=time.time() - 1,
        )
        assert entry2.is_expired


class TestEmbeddingCacheConfig:
    """Tests for EmbeddingCacheConfig."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = EmbeddingCacheConfig()
        
        assert config.max_entries == 10000
        assert config.enable_disk_cache is False
        assert config.use_float16 is False
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = EmbeddingCacheConfig(
            max_entries=5000,
            use_float16=True,
        )
        
        assert config.max_entries == 5000
        assert config.use_float16 is True


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
        
        assert result is not None
        np.testing.assert_array_almost_equal(result, sample_embedding)
    
    def test_get_missing(self, cache):
        """Test getting non-existent key."""
        result = cache.get("nonexistent")
        assert result is None
    
    def test_delete(self, cache, sample_embedding):
        """Test delete operation."""
        cache.put("text1", sample_embedding)
        assert cache.get("text1") is not None
        
        deleted = cache.delete("text1")
        
        assert deleted is True
        assert cache.get("text1") is None
    
    def test_clear(self, cache, sample_embedding):
        """Test clear operation."""
        cache.put("text1", sample_embedding)
        cache.put("text2", sample_embedding)
        
        cache.clear()
        
        assert len(cache) == 0
    
    def test_contains(self, cache, sample_embedding):
        """Test contains check."""
        cache.put("text1", sample_embedding)
        
        assert cache.contains("text1") is True
        assert cache.contains("text2") is False
    
    def test_batch_operations(self, cache):
        """Test batch put and get."""
        texts = ["text1", "text2", "text3"]
        embeddings = [np.random.rand(384).astype(np.float32) for _ in range(3)]
        
        cache.put_batch(texts, embeddings)
        
        found_embeddings, found_indices = cache.get_batch(texts)
        
        assert len(found_embeddings) == 3
        assert found_indices == [0, 1, 2]
    
    def test_batch_get_partial(self, cache, sample_embedding):
        """Test batch get with partial hits."""
        cache.put("text1", sample_embedding)
        cache.put("text3", sample_embedding)
        
        found_embeddings, found_indices = cache.get_batch(["text1", "text2", "text3"])
        
        assert len(found_embeddings) == 2
        assert found_indices == [0, 2]
    
    def test_get_stats(self, cache, sample_embedding):
        """Test statistics."""
        cache.put("text1", sample_embedding)
        cache.get("text1")  # Hit
        cache.get("text2")  # Miss
        
        stats = cache.get_stats()
        
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 0.5
    
    def test_float16_conversion(self, sample_embedding):
        """Test float16 conversion for memory efficiency."""
        config = EmbeddingCacheConfig(use_float16=True)
        cache = EmbeddingCache(config)
        
        cache.put("text1", sample_embedding)
        
        stats = cache.get_stats()
        assert stats["dtype"] == "float16"
        
        # Memory should be roughly half
        assert stats["memory_bytes"] < sample_embedding.nbytes
    
    def test_memory_tracking(self, cache, sample_embedding):
        """Test memory usage tracking."""
        cache.put("text1", sample_embedding)
        cache.put("text2", sample_embedding)
        
        stats = cache.get_stats()
        
        expected_bytes = sample_embedding.nbytes * 2
        # Allow for some overhead
        assert stats["memory_bytes"] >= expected_bytes * 0.9
    
    def test_eviction(self):
        """Test eviction when at capacity."""
        config = EmbeddingCacheConfig(max_entries=5)
        cache = EmbeddingCache(config)
        
        # Add 10 entries, only 5 should remain after eviction
        for i in range(10):
            cache.put(f"text{i}", np.random.rand(10).astype(np.float32))
        
        # Should have evicted some entries
        assert len(cache) <= 5
    
    def test_ttl_expiration(self):
        """Test TTL expiration."""
        config = EmbeddingCacheConfig(default_ttl=0.1)
        cache = EmbeddingCache(config)
        
        embedding = np.random.rand(10).astype(np.float32)
        cache.put("text1", embedding)
        
        assert cache.get("text1") is not None
        
        time.sleep(0.15)
        
        assert cache.get("text1") is None
    
    def test_len_and_contains(self, cache, sample_embedding):
        """Test len() and 'in' operators."""
        assert len(cache) == 0
        assert "text1" not in cache
        
        cache.put("text1", sample_embedding)
        
        assert len(cache) == 1
        assert "text1" in cache
    
    def test_returns_copy(self, cache, sample_embedding):
        """Test that get returns a copy."""
        cache.put("text1", sample_embedding)
        
        result1 = cache.get("text1")
        result1[0] = 999.0  # Modify the returned array
        
        result2 = cache.get("text1")
        
        # Original should be unchanged
        assert result2[0] != 999.0


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
        assert len(disk_files) == 1
