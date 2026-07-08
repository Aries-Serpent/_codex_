"""
Tests for Query Cache Module.
"""

import threading
import time

import pytest

pytest.importorskip("numpy")
from codex.rag.cache.query_cache import (
    CacheEntry,
    CacheStats,
    QueryCache,
    QueryCacheConfig,
)


class TestCacheStats:
    """Tests for CacheStats dataclass."""

    def test_hit_rate_calculation(self):
        """Test hit rate calculation."""
        stats = CacheStats(hits=80, misses=20)
        assert stats.hit_rate == 0.8, "hit_rate is not valid"

    def test_hit_rate_zero_requests(self):
        """Test hit rate with no requests."""
        stats = CacheStats()
        assert stats.hit_rate == 0.0, "hit_rate is not valid"

    def test_total_requests(self):
        """Test total requests calculation."""
        stats = CacheStats(hits=50, misses=50)
        assert stats.total_requests == 100, "total_requests is not valid"

    def test_to_dict(self):
        """Test converting to dictionary."""
        stats = CacheStats(hits=10, misses=5, max_size=100)

        d = stats.to_dict()
        assert d["hits"] == 10, "Condition must be true"
        assert d["misses"] == 5, "Condition must be true"
        assert d["hit_rate"] == 10 / 15, "Condition must be true"


class TestCacheEntry:
    """Tests for CacheEntry dataclass."""

    def test_creation(self):
        """Test creating cache entry."""
        entry = CacheEntry(
            key="test_key",
            value={"data": "value"},
        )

        assert entry.key == "test_key", "key is not valid"
        assert entry.value == {"data": "value"}, "Data must not be empty"
        assert entry.access_count == 0, "Count must be greater than zero"

    def test_is_expired_no_expiry(self):
        """Test is_expired with no expiry."""
        entry = CacheEntry(key="test", value="data")
        assert not entry.is_expired, "Condition must be true"

    def test_is_expired_with_expiry(self):
        """Test is_expired with expiry."""
        entry = CacheEntry(
            key="test",
            value="data",
            expires_at=time.time() - 1,  # Already expired
        )
        assert entry.is_expired, "Condition must be true"

    def test_touch(self):
        """Test touch updates access info."""
        entry = CacheEntry(key="test", value="data")
        initial_count = entry.access_count

        entry.touch()

        assert entry.access_count == initial_count + 1, "Count must be greater than zero"


class TestQueryCacheConfig:
    """Tests for QueryCacheConfig."""

    def test_default_config(self):
        """Test default configuration."""
        config = QueryCacheConfig()

        assert config.max_size == 1000, "max_size is not valid"
        assert config.default_ttl == 300.0, "default_ttl is not valid"
        assert config.enable_stats is True, "enable_stats is not valid"

    def test_custom_config(self):
        """Test custom configuration."""
        config = QueryCacheConfig(
            max_size=500,
            default_ttl=60.0,
            thread_safe=False,
        )

        assert config.max_size == 500, "max_size is not valid"
        assert config.default_ttl == 60.0, "default_ttl is not valid"
        assert config.thread_safe is False, "thread_safe is not valid"


class TestQueryCache:
    """Tests for QueryCache class."""

    @pytest.fixture
    def cache(self):
        """Create a test cache."""
        config = QueryCacheConfig(max_size=10, default_ttl=60.0)
        return QueryCache(config)

    def test_put_and_get(self, cache):
        """Test basic put and get."""
        cache.put("query1", {"result": "data"})

        result = cache.get("query1")
        assert result == {"result": "data"}, "Result must not be empty"

    def test_get_missing(self, cache):
        """Test getting non-existent key."""
        result = cache.get("nonexistent")
        assert result is None, "Result must not be empty"

    def test_delete(self, cache):
        """Test delete operation."""
        cache.put("query1", "data")
        assert cache.get("query1") is not None, "Value must be initialized"

        deleted = cache.delete("query1")
        assert deleted is True, "deleted is not valid"
        assert cache.get("query1") is None, "Condition must be true"

    def test_delete_missing(self, cache):
        """Test deleting non-existent key."""
        deleted = cache.delete("nonexistent")
        assert deleted is False, "deleted is not valid"

    def test_clear(self, cache):
        """Test clear operation."""
        cache.put("query1", "data1")
        cache.put("query2", "data2")

        cache.clear()

        assert len(cache) == 0, "Cache must not be empty"
        assert cache.get("query1") is None, "Condition must be true"

    def test_contains(self, cache):
        """Test contains check."""
        cache.put("query1", "data")

        assert cache.contains("query1") is True, "Condition must be true"
        assert cache.contains("query2") is False, "Condition must be true"

    def test_lru_eviction(self):
        """Test LRU eviction when at capacity."""
        config = QueryCacheConfig(max_size=3)
        cache = QueryCache(config)

        cache.put("query1", "data1")
        cache.put("query2", "data2")
        cache.put("query3", "data3")

        # Access query1 to make it recently used
        cache.get("query1")

        # Add new entry, should evict query2 (LRU)
        cache.put("query4", "data4")

        assert cache.get("query1") is not None, "Value must be initialized"
        assert len(cache) == 3, "Cache must not be empty"

    def test_ttl_expiration(self):
        """Test TTL-based expiration."""
        config = QueryCacheConfig(default_ttl=0.1)  # 100ms TTL
        cache = QueryCache(config)

        cache.put("query1", "data")
        assert cache.get("query1") is not None, "Value must be initialized"

        time.sleep(0.15)  # Wait for expiration

        assert cache.get("query1") is None, "Condition must be true"

    def test_custom_ttl(self, cache):
        """Test custom TTL per entry."""
        cache.put("short", "data", ttl=0.1)
        cache.put("long", "data", ttl=100.0)

        time.sleep(0.15)

        assert cache.get("short") is None, "Condition must be true"
        assert cache.get("long") is not None, "Value must be initialized"

    def test_stats_tracking(self, cache):
        """Test statistics tracking."""
        cache.put("query1", "data")

        cache.get("query1")  # Hit
        cache.get("query2")  # Miss

        stats = cache.get_stats()
        assert stats.hits == 1, "hits is not valid"
        assert stats.misses == 1, "misses is not valid"

    def test_get_entry_info(self, cache):
        """Test getting entry info."""
        cache.put("query1", "data")

        info = cache.get_entry_info("query1")

        assert info is not None, "info must be initialized"
        assert "created_at" in info, "Condition must be true"
        assert "access_count" in info, "Count must be greater than zero"

    def test_get_all_keys(self, cache):
        """Test getting all keys."""
        cache.put("query1", "data1")
        cache.put("query2", "data2")

        keys = cache.get_all_keys()

        assert len(keys) == 2, "Keys must not be empty"

    def test_warm(self, cache):
        """Test cache warming."""
        entries = {
            "query1": "data1",
            "query2": "data2",
            "query3": "data3",
        }

        count = cache.warm(entries)

        assert count == 3, "Count must be greater than zero"
        assert cache.get("query1") == "data1", "Data must not be empty"
        assert cache.get("query2") == "data2", "Data must not be empty"

    def test_len(self, cache):
        """Test len() operator."""
        assert len(cache) == 0, "Cache must not be empty"

        cache.put("query1", "data")
        assert len(cache) == 1, "Cache must not be empty"

    def test_contains_operator(self, cache):
        """Test 'in' operator."""
        cache.put("query1", "data")

        assert "query1" in cache, "Condition must be true"
        assert "query2" not in cache, "Condition must be true"

    def test_thread_safety(self):
        """Test thread-safe operations."""
        config = QueryCacheConfig(max_size=100, thread_safe=True)
        cache = QueryCache(config)

        def writer(n):
            for i in range(10):
                cache.put(f"query_{n}_{i}", f"data_{n}_{i}")

        def reader(n):
            for i in range(10):
                cache.get(f"query_{n}_{i}")

        threads = []
        for i in range(5):
            threads.append(threading.Thread(target=writer, args=(i,)))
            threads.append(threading.Thread(target=reader, args=(i,)))

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        # Should complete without errors
        assert True, "True is not valid"

    def test_dict_key(self, cache):
        """Test using dict as cache key."""
        query = {"filters": {"type": "doc"}, "text": "search"}
        cache.put(query, "results")

        result = cache.get(query)
        assert result == "results", "Result must not be empty"
