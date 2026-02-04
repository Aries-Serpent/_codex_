"""Tests for response caching"""

import time

from src.codex_ml.serving.caching import (
    CacheEntry,
    CacheMetrics,
    ResponseCache,
)


class TestCacheMetrics:
    """Test cache metrics tracking"""

    def test_initialization(self):
        """Test metrics initialization"""
        metrics = CacheMetrics(max_size=100)
        assert metrics.hits == 0
        assert metrics.misses == 0
        assert metrics.evictions == 0
        assert metrics.total_size == 0
        assert metrics.max_size == 100

    def test_record_operations(self):
        """Test recording cache operations"""
        metrics = CacheMetrics()
        metrics.record_hit()
        metrics.record_hit()
        metrics.record_miss()
        metrics.record_eviction()

        assert metrics.hits == 2
        assert metrics.misses == 1
        assert metrics.evictions == 1

    def test_hit_rate_calculation(self):
        """Test hit rate calculation"""
        metrics = CacheMetrics()

        # No operations yet
        assert metrics.get_hit_rate() == 0.0

        # 3 hits, 1 miss = 75% hit rate
        metrics.record_hit()
        metrics.record_hit()
        metrics.record_hit()
        metrics.record_miss()

        assert metrics.get_hit_rate() == 0.75

    def test_to_dict(self):
        """Test metrics dictionary conversion"""
        metrics = CacheMetrics(max_size=100)
        metrics.record_hit()
        metrics.record_miss()
        metrics.total_size = 10

        metrics_dict = metrics.to_dict()
        assert metrics_dict["hits"] == 1
        assert metrics_dict["misses"] == 1
        assert metrics_dict["hit_rate"] == 0.5
        assert metrics_dict["total_size"] == 10
        assert metrics_dict["max_size"] == 100
        assert metrics_dict["memory_utilization"] == 0.1  # 10/100


class TestCacheEntry:
    """Test cache entry with TTL"""

    def test_initialization(self):
        """Test cache entry initialization"""
        entry = CacheEntry(value="test_value", timestamp=time.time(), ttl=60.0)
        assert entry.value == "test_value"
        assert entry.ttl == 60.0
        assert entry.access_count == 0

    def test_not_expired(self):
        """Test entry is not expired"""
        entry = CacheEntry(value="test", timestamp=time.time(), ttl=60.0)
        assert not entry.is_expired()

    def test_expired(self):
        """Test entry is expired"""
        # Entry created 61 seconds ago with 60s TTL
        old_timestamp = time.time() - 61
        entry = CacheEntry(value="test", timestamp=old_timestamp, ttl=60.0)
        assert entry.is_expired()

    def test_no_expiration(self):
        """Test entry with no expiration (TTL=0)"""
        old_timestamp = time.time() - 1000
        entry = CacheEntry(value="test", timestamp=old_timestamp, ttl=0)
        assert not entry.is_expired()

    def test_access_tracking(self):
        """Test access count tracking"""
        entry = CacheEntry(value="test", timestamp=time.time(), ttl=60.0)

        assert entry.access_count == 0
        entry.access()
        assert entry.access_count == 1
        entry.access()
        assert entry.access_count == 2


class TestResponseCache:
    """Test response cache"""

    def test_initialization(self):
        """Test cache initialization"""
        cache = ResponseCache(max_size=100, default_ttl=300.0)
        assert cache.max_size == 100
        assert cache.default_ttl == 300.0
        assert len(cache) == 0

    def test_put_and_get(self):
        """Test basic put and get operations"""
        cache = ResponseCache(max_size=10, default_ttl=60.0)

        # Put value
        cache.put("key1", "value1")

        # Get value
        result = cache.get("key1")
        assert result == "value1"

        # Check metrics
        metrics = cache.get_metrics()
        assert metrics["hits"] == 1
        assert metrics["misses"] == 0

    def test_cache_miss(self):
        """Test cache miss"""
        cache = ResponseCache()

        # Get non-existent key
        result = cache.get("nonexistent")
        assert result is None

        # Check metrics
        metrics = cache.get_metrics()
        assert metrics["hits"] == 0
        assert metrics["misses"] == 1

    def test_ttl_expiration(self):
        """Test TTL-based expiration"""
        cache = ResponseCache(default_ttl=0.1)  # 100ms TTL

        # Put value with short TTL
        cache.put("key1", "value1", ttl=0.1)

        # Should be in cache immediately
        assert cache.get("key1") == "value1"

        # Wait for expiration
        time.sleep(0.15)

        # Should be expired now
        assert cache.get("key1") is None

    def test_lru_eviction(self):
        """Test LRU eviction when max_size is reached"""
        cache = ResponseCache(max_size=3, default_ttl=0)  # No TTL

        # Fill cache
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")

        assert len(cache) == 3

        # Add 4th item, should evict key1 (least recently used)
        cache.put("key4", "value4")

        assert len(cache) == 3
        assert cache.get("key1") is None  # Evicted
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
        assert cache.get("key4") == "value4"

        # Check eviction metric
        metrics = cache.get_metrics()
        assert metrics["evictions"] == 1

    def test_lru_ordering(self):
        """Test LRU ordering is maintained"""
        cache = ResponseCache(max_size=3, default_ttl=0)

        # Fill cache
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")

        # Access key1 (moves to end)
        cache.get("key1")

        # Add key4, should evict key2 (now least recently used)
        cache.put("key4", "value4")

        assert cache.get("key1") == "value1"  # Still in cache
        assert cache.get("key2") is None  # Evicted
        assert cache.get("key3") == "value3"
        assert cache.get("key4") == "value4"

    def test_update_existing_key(self):
        """Test updating an existing cache entry"""
        cache = ResponseCache()

        cache.put("key1", "value1")
        assert cache.get("key1") == "value1"

        # Update with new value
        cache.put("key1", "value2")
        assert cache.get("key1") == "value2"

        # Should still be 1 entry
        assert len(cache) == 1

    def test_clear(self):
        """Test clearing cache"""
        cache = ResponseCache()

        cache.put("key1", "value1")
        cache.put("key2", "value2")
        assert len(cache) == 2

        cache.clear()
        assert len(cache) == 0
        assert cache.get("key1") is None

    def test_remove_expired(self):
        """Test removing expired entries"""
        cache = ResponseCache(default_ttl=0.1)

        # Add entries with short TTL
        cache.put("key1", "value1", ttl=0.1)
        cache.put("key2", "value2", ttl=0.1)
        cache.put("key3", "value3", ttl=10.0)  # Long TTL

        assert len(cache) == 3

        # Wait for expiration
        time.sleep(0.15)

        # Remove expired
        removed = cache.remove_expired()

        assert removed == 2  # key1 and key2 expired
        assert len(cache) == 1
        assert cache.get("key3") == "value3"  # Still valid

    def test_content_based_keys(self):
        """Test content-based key generation"""
        cache = ResponseCache()

        # Same content should generate same key
        cache.put({"a": 1, "b": 2}, "value1")

        # Same content, different order, should hit cache
        result = cache.get({"b": 2, "a": 1})
        assert result == "value1"

        # Different content should miss
        result = cache.get({"a": 1, "b": 3})
        assert result is None

    def test_complex_data_types(self):
        """Test caching with complex data types"""
        cache = ResponseCache()

        # Cache with list input
        cache.put(["item1", "item2", "item3"], {"result": "processed"})
        result = cache.get(["item1", "item2", "item3"])
        assert result == {"result": "processed"}

        # Cache with nested dict
        cache.put({"nested": {"key": "value"}}, "nested_result")
        result = cache.get({"nested": {"key": "value"}})
        assert result == "nested_result"

    def test_contains(self):
        """Test __contains__ operator"""
        cache = ResponseCache()

        cache.put("key1", "value1")

        assert "key1" in cache
        assert "key2" not in cache
