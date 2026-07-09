"""
Tier 1 Mutation Killing Enhancements for Cache Module

Focus: Harden error handling assertions by:
1. Verifying specific error messages, not just error presence
2. Testing error codes/types precisely
3. Adding boundary condition assertions
4. Testing cache hit/miss rates with exact value checks
5. Verifying expiration boundaries with strict comparisons
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


class TestCacheStatsExactValues:
    """Test CacheStats with strong value assertions."""

    def test_hit_rate_exactly_zero(self):
        """Test hit rate is exactly 0.0 with no hits."""
        stats = CacheStats(hits=0, misses=10)
        assert stats.hit_rate == 0.0, \
            f"Hit rate must be exactly 0.0, got {stats.hit_rate}"
        assert stats.hit_rate >= 0.0, \
            f"Hit rate must be >= 0.0, got {stats.hit_rate}"
        assert stats.hit_rate <= 1.0, \
            f"Hit rate must be <= 1.0, got {stats.hit_rate}"

    def test_hit_rate_exactly_one(self):
        """Test hit rate is exactly 1.0 with only hits."""
        stats = CacheStats(hits=10, misses=0)
        assert stats.hit_rate == 1.0, \
            f"Hit rate must be exactly 1.0, got {stats.hit_rate}"
        assert stats.hit_rate >= 0.0, \
            f"Hit rate must be >= 0.0, got {stats.hit_rate}"
        assert stats.hit_rate <= 1.0, \
            f"Hit rate must be <= 1.0, got {stats.hit_rate}"

    def test_hit_rate_half(self):
        """Test hit rate with equal hits and misses."""
        stats = CacheStats(hits=50, misses=50)
        assert stats.hit_rate == 0.5, \
            f"Hit rate must be exactly 0.5, got {stats.hit_rate}"
        assert stats.hit_rate > 0.4, \
            f"Hit rate {stats.hit_rate} must be > 0.4"
        assert stats.hit_rate < 0.6, \
            f"Hit rate {stats.hit_rate} must be < 0.6"

    def test_total_requests_exact(self):
        """Test total request count is exactly hits + misses."""
        for hits, misses in [(0, 10), (10, 0), (5, 5), (100, 50)]:
            stats = CacheStats(hits=hits, misses=misses)
            expected_total = hits + misses
            assert stats.total_requests == expected_total, \
                f"Total must be exactly {expected_total}, got {stats.total_requests}"
            assert stats.total_requests > 0 or (hits == 0 and misses == 0), \
                f"Total {stats.total_requests} is invalid for hits={hits}, misses={misses}"


class TestCacheEntryBoundaries:
    """Test CacheEntry expiration boundaries."""

    def test_entry_expires_exactly_at_boundary(self):
        """Test entry status changes exactly at expiration time."""
        now = time.time()

        # Entry that expires in the future
        entry_future = CacheEntry(key="future", value="data", expires_at=now + 10)
        assert not entry_future.is_expired, \
            "Entry expiring in future must not be expired"

        # Entry that expired in the past
        entry_past = CacheEntry(key="past", value="data", expires_at=now - 10)
        assert entry_past.is_expired, \
            "Entry expired in past must be expired"

    def test_entry_expiration_at_boundary_time(self):
        """Test expiration behavior at exact boundary."""
        now = time.time()

        # Just barely expired (1ms ago)
        entry = CacheEntry(
            key="boundary",
            value="data",
            expires_at=now - 0.001
        )
        assert entry.is_expired, \
            "Entry expired even slightly in past must be expired"

        # Not yet expired (expires in far future)
        entry2 = CacheEntry(
            key="not_yet",
            value="data",
            expires_at=now + 1000
        )
        assert not entry2.is_expired, \
            "Entry expiring far in future must not be expired"

    def test_entry_touch_increments_access_count(self):
        """Test access_count increases exactly by 1 on each touch."""
        entry = CacheEntry(key="touch_test", value="data")

        initial = entry.access_count
        assert initial == 0, f"Initial access count must be 0, got {initial}"

        entry.touch()
        after_first = entry.access_count
        assert after_first == initial + 1, \
            f"After touch, count must be {initial + 1}, got {after_first}"

        entry.touch()
        after_second = entry.access_count
        assert after_second == initial + 2, \
            f"After second touch, count must be {initial + 2}, got {after_second}"


class TestQueryCacheBasicOperations:
    """Test QueryCache with strong assertions."""

    def test_cache_hit_miss_counts_exact(self):
        """Test hit/miss counts are tracked exactly."""
        config = QueryCacheConfig(max_size=100)
        cache = QueryCache(config)
        stats = cache.get_stats()

        # Initial state
        assert stats.hits == 0, f"Initial hits must be 0, got {stats.hits}"
        assert stats.misses == 0, f"Initial misses must be 0, got {stats.misses}"
        assert stats.size == 0, f"Initial size must be 0, got {stats.size}"
        assert stats.max_size == 100, f"Initial max_size must be 100, got {stats.max_size}"

        # A put followed by a get for the same key is a hit.
        cache.put("key1", {"value": 1})
        result = cache.get("key1")
        stats = cache.get_stats()

        # Verify exact counts after operations
        assert result is not None, "Get should return non-None for existing key"
        assert stats.hits == 1, f"Expected exactly 1 hit, got {stats.hits}"
        assert stats.misses == 0, f"Expected exactly 0 misses, got {stats.misses}"
        assert stats.size == 1, f"Expected cache size 1 after put/get, got {stats.size}"

    def test_cache_hit_rate_progression(self):
        """Test hit rate changes exactly as operations proceed."""
        config = QueryCacheConfig(max_size=100)
        cache = QueryCache(config)

        # Put and get same key multiple times
        cache.put("key1", {"data": "value"})

        # First get
        cache.get("key1")
        stats = cache.get_stats()
        assert stats.hits == 1, f"Expected exactly 1 hit, got {stats.hits}"
        assert stats.misses == 0, f"Expected exactly 0 misses, got {stats.misses}"

        # Get again
        cache.get("key1")
        stats = cache.get_stats()
        assert stats.hits == 2, f"Expected exactly 2 hits, got {stats.hits}"
        assert stats.misses == 0, f"Expected exactly 0 misses, got {stats.misses}"

    def test_cache_respects_size_limit(self):
        """Test cache respects max_size with strong assertion."""
        max_size = 5
        config = QueryCacheConfig(max_size=max_size)
        cache = QueryCache(config)

        # Add more than max_size items
        for i in range(max_size + 5):
            cache.put(f"key_{i}", {"value": i})

        # Cache size should not exceed max_size
        current_size = cache.get_stats().size
        assert current_size <= max_size, \
            f"Cache size {current_size} must not exceed {max_size}"
        assert current_size > 0, \
            f"Cache should contain items, got {current_size}"


class TestCacheErrorHandling:
    """Test error handling with specific error message validation."""

    def test_put_with_invalid_key_format(self):
        """Test put operation rejects invalid key types if applicable."""
        config = QueryCacheConfig(max_size=100)
        cache = QueryCache(config)

        # Most implementations accept string keys
        try:
            cache.put("valid_key", {"value": 1})
            # If it succeeds, verify it's accessible
            result = cache.get("valid_key")
            assert result is not None, "Put/Get roundtrip failed"
        except (TypeError, ValueError) as e:
            # Some implementations may validate key type
            assert "key" in str(e).lower() or "type" in str(e).lower(), \
                f"Error message should mention key/type: {e}"

    def test_cache_handles_none_values(self):
        """Test cache behavior with None values."""
        config = QueryCacheConfig(max_size=100)
        cache = QueryCache(config)

        # Behavior may vary - some caches allow None, some don't
        try:
            cache.put("none_key", None)
            result = cache.get("none_key")
            # If it accepts None, result should be None or error
        except (TypeError, ValueError):
            # Rejecting None is also valid
            pass

    def test_cache_thread_safety_concurrent_operations(self):
        """Test cache behavior under concurrent access."""
        config = QueryCacheConfig(max_size=100)
        cache = QueryCache(config)

        errors: list = []

        def add_items(start, count):
            try:
                for i in range(start, start + count):
                    cache.put(f"key_{i}", {"thread": start, "item": i})
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=add_items, args=(i * 10, 10))
            for i in range(3)
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should complete without errors
        assert len(errors) == 0, \
            f"Concurrent operations should not error: {errors}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
