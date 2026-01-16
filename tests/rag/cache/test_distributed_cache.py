"""
Tests for Distributed Cache Module.
"""

import pytest
import json

from codex.rag.cache.distributed_cache import (
    DistributedCache,
    DistributedCacheConfig,
    CacheBackend,
    MemoryCacheBackend,
)


class TestCacheBackend:
    """Tests for CacheBackend enum."""
    
    def test_backend_values(self):
        """Test backend enum values."""
        assert CacheBackend.MEMORY.value == "memory"
        assert CacheBackend.REDIS.value == "redis"
        assert CacheBackend.HYBRID.value == "hybrid"


class TestDistributedCacheConfig:
    """Tests for DistributedCacheConfig."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = DistributedCacheConfig()
        
        assert config.backend == CacheBackend.MEMORY
        assert config.memory_max_size == 1000
        assert config.redis_host == "localhost"
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = DistributedCacheConfig(
            backend=CacheBackend.HYBRID,
            memory_max_size=500,
            redis_port=6380,
        )
        
        assert config.backend == CacheBackend.HYBRID
        assert config.memory_max_size == 500
        assert config.redis_port == 6380


class TestMemoryCacheBackend:
    """Tests for MemoryCacheBackend."""
    
    @pytest.fixture
    def backend(self):
        config = DistributedCacheConfig(memory_max_size=100)
        return MemoryCacheBackend(config)
    
    def test_put_and_get(self, backend):
        """Test basic put and get."""
        backend.put("key1", {"data": "value"})
        
        result = backend.get("key1")
        assert result == {"data": "value"}
    
    def test_get_missing(self, backend):
        """Test getting missing key."""
        result = backend.get("nonexistent")
        assert result is None
    
    def test_delete(self, backend):
        """Test delete operation."""
        backend.put("key1", "value")
        deleted = backend.delete("key1")
        
        assert deleted is True
        assert backend.get("key1") is None
    
    def test_clear(self, backend):
        """Test clear operation."""
        backend.put("key1", "value1")
        backend.put("key2", "value2")
        
        backend.clear()
        
        assert backend.get("key1") is None
        assert backend.get("key2") is None
    
    def test_contains(self, backend):
        """Test contains check."""
        backend.put("key1", "value")
        
        assert backend.contains("key1") is True
        assert backend.contains("key2") is False
    
    def test_get_stats(self, backend):
        """Test getting stats."""
        backend.put("key1", "value")
        backend.get("key1")
        
        stats = backend.get_stats()
        
        assert "hits" in stats
        assert "misses" in stats


class TestDistributedCache:
    """Tests for DistributedCache class."""
    
    @pytest.fixture
    def memory_cache(self):
        """Create a memory-only distributed cache."""
        config = DistributedCacheConfig(backend=CacheBackend.MEMORY)
        return DistributedCache(config)
    
    def test_put_and_get(self, memory_cache):
        """Test basic put and get."""
        memory_cache.put("query1", {"results": [1, 2, 3]})
        
        result = memory_cache.get("query1")
        assert result == {"results": [1, 2, 3]}
    
    def test_get_missing(self, memory_cache):
        """Test getting missing key."""
        result = memory_cache.get("nonexistent")
        assert result is None
    
    def test_delete(self, memory_cache):
        """Test delete operation."""
        memory_cache.put("query1", "data")
        deleted = memory_cache.delete("query1")
        
        assert deleted is True
        assert memory_cache.get("query1") is None
    
    def test_clear(self, memory_cache):
        """Test clear operation."""
        memory_cache.put("query1", "data1")
        memory_cache.put("query2", "data2")
        
        memory_cache.clear()
        
        assert memory_cache.get("query1") is None
        assert memory_cache.get("query2") is None
    
    def test_contains(self, memory_cache):
        """Test contains check."""
        memory_cache.put("query1", "data")
        
        assert memory_cache.contains("query1") is True
        assert memory_cache.contains("query2") is False
    
    def test_contains_operator(self, memory_cache):
        """Test 'in' operator."""
        memory_cache.put("query1", "data")
        
        assert "query1" in memory_cache
        assert "query2" not in memory_cache
    
    def test_get_stats(self, memory_cache):
        """Test getting stats."""
        memory_cache.put("query1", "data")
        memory_cache.get("query1")
        
        stats = memory_cache.get_stats()
        
        assert "backend" in stats
        assert stats["backend"] == "memory"
        assert "memory" in stats
    
    def test_warm(self, memory_cache):
        """Test cache warming."""
        entries = {
            "query1": {"result": 1},
            "query2": {"result": 2},
            "query3": {"result": 3},
        }
        
        count = memory_cache.warm(entries)
        
        assert count == 3
        assert memory_cache.get("query1") == {"result": 1}
    
    def test_dict_key(self, memory_cache):
        """Test using dict as key."""
        query = {"filters": {"type": "doc"}, "text": "search"}
        memory_cache.put(query, "results")
        
        result = memory_cache.get(query)
        assert result == "results"
    
    def test_complex_values(self, memory_cache):
        """Test storing complex values."""
        value = {
            "results": [
                {"id": 1, "score": 0.9, "text": "Doc 1"},
                {"id": 2, "score": 0.8, "text": "Doc 2"},
            ],
            "metadata": {"total": 2, "query_time": 0.05},
        }
        
        memory_cache.put("query1", value)
        result = memory_cache.get("query1")
        
        assert result == value
    
    def test_ttl(self, memory_cache):
        """Test TTL support."""
        import time
        
        config = DistributedCacheConfig(
            backend=CacheBackend.MEMORY,
            memory_ttl=0.1,
        )
        cache = DistributedCache(config)
        
        cache.put("query1", "data", ttl=100)  # Long TTL
        assert cache.get("query1") is not None


class TestHybridCache:
    """Tests for hybrid cache mode (without Redis)."""
    
    @pytest.fixture
    def hybrid_cache(self):
        """Create a hybrid cache (will fallback to memory since Redis unavailable)."""
        config = DistributedCacheConfig(
            backend=CacheBackend.HYBRID,
            redis_host="nonexistent",  # Will fail to connect
        )
        return DistributedCache(config)
    
    def test_hybrid_fallback_to_memory(self, hybrid_cache):
        """Test that hybrid falls back to memory when Redis unavailable."""
        # Should still work using memory backend
        hybrid_cache.put("query1", "data")
        result = hybrid_cache.get("query1")
        
        assert result == "data"
    
    def test_hybrid_stats(self, hybrid_cache):
        """Test hybrid cache stats."""
        stats = hybrid_cache.get_stats()
        
        assert stats["backend"] == "hybrid"
        assert "memory" in stats
        assert "redis" in stats
