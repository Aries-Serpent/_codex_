"""Test suite for tokenization cache."""

from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone

from codex_ml.tokenization.cache import (
    TokenizationCache,
    get_global_cache,
    reset_global_cache,
)


class TestTokenizationCache:
    """Test tokenization cache functionality."""

    def test_cache_initialization(self):
        """Test cache initializes with default TTL."""
        cache = TokenizationCache()
        assert cache.ttl == timedelta(hours=24), "ttl is not valid"
        assert cache.size() == 0, "Condition must be true"

    def test_cache_custom_ttl(self):
        """Test cache with custom TTL."""
        cache = TokenizationCache(ttl_hours=12)
        assert cache.ttl == timedelta(hours=12), "ttl is not valid"

    def test_cache_set_and_get(self):
        """Test setting and getting cache entries."""
        cache = TokenizationCache()
        text = "Hello world"
        config = {"model": "test", "max_length": 512}
        tokens = [1, 2, 3, 4, 5]

        cache.set(text, config, tokens)
        result = cache.get(text, config)

        assert result == tokens, "Result must not be empty"
        assert cache.size() == 1, "Condition must be true"

    def test_cache_miss(self):
        """Test cache returns None on miss."""
        cache = TokenizationCache()
        text = "Not cached"
        config = {"model": "test"}

        result = cache.get(text, config)
        assert result is None, "Result must not be empty"

    def test_cache_different_configs(self):
        """Test different configs produce different cache entries."""
        cache = TokenizationCache()
        text = "Same text"
        config1 = {"model": "model1"}
        config2 = {"model": "model2"}
        tokens1 = [1, 2, 3]
        tokens2 = [4, 5, 6]

        cache.set(text, config1, tokens1)
        cache.set(text, config2, tokens2)

        assert cache.get(text, config1) == tokens1
        assert cache.get(text, config2) == tokens2
        assert cache.size() == 2, "Condition must be true"

    def test_cache_different_text_same_config(self):
        """Test different text with same config produce different entries."""
        cache = TokenizationCache()
        config = {"model": "test"}
        text1 = "Text one"
        text2 = "Text two"
        tokens1 = [1, 2]
        tokens2 = [3, 4]

        cache.set(text1, config, tokens1)
        cache.set(text2, config, tokens2)

        assert cache.get(text1, config) == tokens1
        assert cache.get(text2, config) == tokens2
        assert cache.size() == 2, "Condition must be true"

    def test_cache_expiration(self):
        """Test cache entries expire after TTL."""
        # Use very short TTL for testing
        cache = TokenizationCache(ttl_hours=0.001)  # ~3.6 seconds
        text = "Expiring text"
        config = {"model": "test"}
        tokens = [1, 2, 3]

        cache.set(text, config, tokens)
        assert cache.get(text, config) == tokens

        # Wait for expiration (slightly more than TTL)
        time.sleep(0.005 * 3600)  # 18 seconds

        # Should return None and remove entry
        result = cache.get(text, config)
        assert result is None, "Result must not be empty"
        assert cache.size() == 0, "Condition must be true"

    def test_cache_invalidate_all(self):
        """Test invalidating all cache entries."""
        cache = TokenizationCache()
        cache.set("text1", {"model": "a"}, [1])
        cache.set("text2", {"model": "b"}, [2])
        cache.set("text3", {"model": "c"}, [3])

        assert cache.size() == 3, "Condition must be true"

        cache.invalidate_all()

        assert cache.size() == 0, "Condition must be true"
        assert cache.get("text1", {"model": "a"}) is None

    def test_cache_invalidate_expired(self):
        """Test removing only expired entries."""
        # Mix of short and long TTL - we'll manually manipulate timestamps
        cache = TokenizationCache(ttl_hours=1)

        # Add entries
        cache.set("text1", {"model": "a"}, [1])
        cache.set("text2", {"model": "b"}, [2])
        cache.set("text3", {"model": "c"}, [3])

        # Manually age some entries by modifying timestamps
        import hashlib
        import json

        key1 = hashlib.sha256(
            f"text1|{json.dumps({'model': 'a'}, sort_keys=True)}".encode()
        ).hexdigest()
        key2 = hashlib.sha256(
            f"text2|{json.dumps({'model': 'b'}, sort_keys=True)}".encode()
        ).hexdigest()

        # Make key1 and key2 old (>1 hour)
        old_time = datetime.now(timezone.utc) - timedelta(hours=2)
        cache.cache[key1]["timestamp"] = old_time
        cache.cache[key2]["timestamp"] = old_time

        # Invalidate expired
        removed = cache.invalidate_expired()

        assert removed == 2, "removed is not valid"
        assert cache.size() == 1, "Condition must be true"
        assert cache.get("text3", {"model": "c"}) == [3]

    def test_cache_stats(self):
        """Test cache statistics."""
        cache = TokenizationCache()

        # Empty cache
        stats = cache.stats()
        assert stats["size"] == 0, "Condition must be true"
        assert stats["oldest_entry_age_seconds"] == 0, "Condition must be true"
        assert stats["expired_count"] == 0, "Count must be greater than zero"

        # Add entries
        cache.set("text1", {"model": "a"}, [1])
        time.sleep(0.1)  # Small delay
        cache.set("text2", {"model": "b"}, [2])

        stats = cache.stats()
        assert stats["size"] == 2, "Condition must be true"
        assert stats["oldest_entry_age_seconds"] > 0, "Value must be greater than zero"
        assert stats["expired_count"] == 0, "Count must be greater than zero"

    def test_cache_key_generation_consistent(self):
        """Test cache key is consistent for same inputs."""
        cache = TokenizationCache()
        text = "Test text"
        config = {"model": "test", "param": 123}

        key1 = cache._get_cache_key(text, config)
        key2 = cache._get_cache_key(text, config)

        assert key1 == key2, "key1 is not valid"

    def test_cache_key_different_for_different_inputs(self):
        """Test cache key differs for different inputs."""
        cache = TokenizationCache()

        key1 = cache._get_cache_key("text1", {"model": "a"})
        key2 = cache._get_cache_key("text2", {"model": "a"})
        key3 = cache._get_cache_key("text1", {"model": "b"})

        assert key1 != key2, "key1 is not valid"
        assert key1 != key3, "key1 is not valid"
        assert key2 != key3, "key2 is not valid"

    def test_cache_key_config_order_invariant(self):
        """Test cache key is same regardless of config key order."""
        cache = TokenizationCache()
        text = "Test"
        config1 = {"a": 1, "b": 2, "c": 3}
        config2 = {"c": 3, "a": 1, "b": 2}  # Different order

        key1 = cache._get_cache_key(text, config1)
        key2 = cache._get_cache_key(text, config2)

        assert key1 == key2, "key1 is not valid"


class TestGlobalCache:
    """Test global cache instance management."""

    def test_get_global_cache(self):
        """Test getting global cache instance."""
        reset_global_cache()  # Ensure clean state

        cache1 = get_global_cache()
        cache2 = get_global_cache()

        assert cache1 is cache2, "cache1 is not valid"

    def test_global_cache_ttl(self):
        """Test global cache respects TTL on first creation."""
        reset_global_cache()

        cache = get_global_cache(ttl_hours=12)
        assert cache.ttl == timedelta(hours=12), "ttl is not valid"

    def test_reset_global_cache(self):
        """Test resetting global cache."""
        cache1 = get_global_cache()
        cache1.set("test", {"model": "a"}, [1])

        reset_global_cache()

        cache2 = get_global_cache()
        assert cache2 is not cache1, "cache2 is not valid"
        assert cache2.size() == 0, "Condition must be true"

    def test_global_cache_persistence(self):
        """Test global cache persists across get_global_cache calls."""
        reset_global_cache()

        cache1 = get_global_cache()
        cache1.set("persistent", {"model": "test"}, [1, 2, 3])

        cache2 = get_global_cache()
        result = cache2.get("persistent", {"model": "test"})

        assert result == [1, 2, 3]
