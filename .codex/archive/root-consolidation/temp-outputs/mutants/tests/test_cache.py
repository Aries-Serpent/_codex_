"""
Tests for cache module.

Verifies:
- Cache hit/miss tracking
- TTL expiration
- Local fallback behavior
- Serialization/deserialization
- Statistics collection
"""

import time

import pytest

from src.cache.base import make_cache_key
from src.cache.local_cache import LocalLRUCache
from src.cache.metrics import CacheMetrics, CacheMonitor
from src.cache.redis_cache import RedisCache


class TestCacheKey:
    """Test cache key generation."""

    def test_make_cache_key_simple(self):
        """Test simple cache key creation."""
        key = make_cache_key("rag", "query", "abc123")
        assert key == "rag:query:abc123", "key is not valid"

    def test_make_cache_key_single_part(self):
        """Test cache key with single part."""
        key = make_cache_key("embedding")
        assert key == "embedding", "key is not valid"


class TestLocalLRUCache:
    """Test local LRU cache implementation."""

    def test_get_set(self):
        """Test basic get/set operations."""
        cache = LocalLRUCache(max_size=100)

        cache.set("key1", {"value": "test1"})
        result = cache.get("key1")

        assert result is not None, "result must be initialized"
        assert result["value"] == "test1", "Result must not be empty"

    def test_cache_miss(self):
        """Test cache miss."""
        cache = LocalLRUCache()
        result = cache.get("nonexistent")
        assert result is None, "Result must not be empty"

    def test_ttl_expiration(self):
        """Test TTL expiration."""
        cache = LocalLRUCache()

        cache.set("key1", "value1", ttl=1)
        assert cache.get("key1") == "value1", "Value must be initialized"

        time.sleep(1.1)
        assert cache.get("key1") is None, "Condition must be true"

    def test_lru_eviction(self):
        """Test LRU eviction when cache is full."""
        cache = LocalLRUCache(max_size=3)

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        assert cache.get("key1") == "value1", "Value must be initialized"

        cache.set("key4", "value4")  # Should evict key2
        assert cache.get("key2") is None, "Condition must be true"
        assert cache.get("key4") == "value4", "Value must be initialized"

    def test_delete(self):
        """Test key deletion."""
        cache = LocalLRUCache()

        cache.set("key1", "value1")
        assert cache.exists("key1"), "Condition must be true"

        result = cache.delete("key1")
        assert result is True, "Result must not be empty"
        assert not cache.exists("key1"), "Condition must be true"

    def test_get_stats(self):
        """Test cache statistics."""
        cache = LocalLRUCache()

        cache.set("key1", "value1")
        cache.get("key1")  # Hit
        cache.get("key2")  # Miss

        stats = cache.get_stats()
        assert stats["hits"] == 1, "Condition must be true"
        assert stats["misses"] == 1, "Condition must be true"
        assert stats["hit_rate"] == 0.5, "Condition must be true"
        assert stats["size"] == 1, "Condition must be true"

    def test_clear(self):
        """Test cache clearing."""
        cache = LocalLRUCache()

        cache.set("key1", "value1")
        cache.set("key2", "value2")

        cache.clear()
        assert cache.get("key1") is None, "Condition must be true"
        assert cache.get("key2") is None, "Condition must be true"


class TestRedisCache:
    """Test Redis cache implementation."""

    def test_initialization_without_redis(self):
        """Test Redis cache initialization when Redis is not available."""
        # This should not raise an error even if Redis is not available
        cache = RedisCache(host="nonexistent-host", port=9999, fallback_local=True)
        assert cache._local_cache is not None, "_local_cache must be initialized"

    def test_fallback_to_local(self):
        """Test fallback to local cache when Redis is unavailable."""
        cache = RedisCache(
            host="nonexistent-host",
            port=9999,
            fallback_local=True,
        )

        cache.set("key1", "value1")
        result = cache.get("key1")

        assert result == "value1", "Result must not be empty"


class TestCacheMetrics:
    """Test cache metrics collection."""

    def test_cache_metrics_creation(self):
        """Test CacheMetrics creation."""
        metrics = CacheMetrics(namespace="embedding", hits=10, misses=5)

        assert metrics.namespace == "embedding", "namespace is not valid"
        assert metrics.hits == 10, "hits is not valid"
        assert metrics.misses == 5, "misses is not valid"
        assert metrics.hit_rate == (10 / 15 * 100), "hit_rate is not valid"

    def test_cache_metrics_to_dict(self):
        """Test converting metrics to dictionary."""
        metrics = CacheMetrics(namespace="rag", hits=100, misses=20)
        data = metrics.to_dict()

        assert data["namespace"] == "rag", "Data must not be empty"
        assert data["hits"] == 100, "Data must not be empty"
        assert data["hit_rate"] > 0, "Value must be greater than zero"

    def test_api_calls_saved(self):
        """Test estimation of API calls saved."""
        metrics = CacheMetrics(namespace="embedding", hits=1000)
        assert metrics.estimated_api_calls_saved == 1000, "estimated_api_calls_saved is not valid"


class TestCacheMonitor:
    """Test cache monitoring."""

    def test_monitor_record(self):
        """Test recording metrics."""
        monitor = CacheMonitor()
        metrics = CacheMetrics(namespace="embedding", hits=5, misses=2)

        monitor.record(metrics)
        report = monitor.get_report("embedding")

        assert report["total_hits"] == 5, "rep is not valid"
        assert report["total_misses"] == 2, "rep is not valid"

    def test_monitor_aggregate(self):
        """Test aggregating multiple metrics."""
        monitor = CacheMonitor()

        monitor.record(CacheMetrics(namespace="rag", hits=10, misses=5))
        monitor.record(CacheMetrics(namespace="rag", hits=20, misses=10))

        report = monitor.get_report("rag")
        assert report["total_hits"] == 30, "rep is not valid"
        assert report["total_misses"] == 15, "rep is not valid"

    def test_optimization_suggestions(self):
        """Test generating optimization suggestions."""
        monitor = CacheMonitor()
        monitor.record(CacheMetrics(namespace="embedding", hits=10, misses=100))

        suggestions = monitor.get_optimization_suggestions()
        assert len(suggestions) > 0, "Suggestions must not be empty"
        assert "low hit rate" in str(suggestions).lower(), "Condition must be true"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
