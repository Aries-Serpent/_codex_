"""
L1 Request Cache: In-process request-scoped cache for sub-300ms latency optimization.

Part of Phase 13.4 4-layer cache hierarchy. Optimized for:
- <300ms p99 latency on cached requests
- Request-scoped isolation (thread-local storage)
- Zero garbage collection impact
- O(1) get/set operations

Thread Safety: Thread-local storage (no locks needed)
Eviction: LRU when capacity exceeded
TTL: 300 seconds (request-scoped, resets per request)
"""

from __future__ import annotations

import hashlib
import logging
import threading
import time
from collections import OrderedDict
from typing import Any, Callable, Generic, Optional, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")

# L1 constraints for sub-300ms performance
L1_MAX_SIZE = 5000  # Per-request cache size
L1_TTL = 300  # 5 minutes


class L1RequestCacheEntry(Generic[T]):
    """Single L1 cache entry with minimal overhead."""

    __slots__ = ("value", "created_at", "ttl_at", "hits")

    def __init__(self, value: T, ttl: int = L1_TTL):
        self.value = value
        self.created_at = time.time()
        self.ttl_at = self.created_at + ttl
        self.hits = 0

    def is_expired(self) -> bool:
        """Check if entry has expired."""
        return time.time() > self.ttl_at

    def record_hit(self) -> None:
        """Record a cache hit."""
        self.hits += 1


class L1RequestCache(Generic[T]):
    """
    Thread-local request cache for in-process caching.

    Designed for maximum performance:
    - Uses OrderedDict for O(1) LRU operations
    - Thread-local storage (no locks needed)
    - Minimal memory overhead per entry
    - Lazy expiration (on access)

    Usage:
        cache = L1RequestCache()
        cache.set("query:123", result)
        value = cache.get("query:123")
        stats = cache.get_stats()
    """

    def __init__(self, max_size: int = L1_MAX_SIZE, default_ttl: int = L1_TTL):
        """Initialize L1 request cache.

        Args:
            max_size: Maximum entries per request
            default_ttl: Default TTL in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._local = threading.local()

    def _get_cache(self) -> dict[str, L1RequestCacheEntry[Any]]:
        """Get thread-local cache instance."""
        if not hasattr(self._local, "cache"):
            self._local.cache = OrderedDict()
            self._local.hits = 0
            self._local.misses = 0
        return self._local.cache

    def _get_stats_local(self) -> tuple[int, int]:
        """Get thread-local hit/miss counts."""
        if not hasattr(self._local, "hits"):
            self._local.hits = 0
            self._local.misses = 0
        return self._local.hits, self._local.misses

    def get(self, key: str) -> Optional[T]:
        """Get value from L1 cache.

        Args:
            key: Cache key

        Returns:
            Cached value if found and not expired, None otherwise
        """
        cache = self._get_cache()

        if key not in cache:
            hits, misses = self._get_stats_local()
            self._local.misses = misses + 1
            return None

        entry = cache[key]

        # Check expiration
        if entry.is_expired():
            del cache[key]
            hits, misses = self._get_stats_local()
            self._local.misses = misses + 1
            return None

        # Move to end (most recently used) and record hit
        cache.move_to_end(key)
        entry.record_hit()
        hits, misses = self._get_stats_local()
        self._local.hits = hits + 1
        return entry.value

    def set(self, key: str, value: T, ttl: Optional[int] = None) -> None:
        """Set value in L1 cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Optional TTL in seconds (uses default if not provided)
        """
        cache = self._get_cache()
        ttl = ttl or self.default_ttl

        # Remove if exists to update position
        if key in cache:
            del cache[key]

        # Add to cache
        cache[key] = L1RequestCacheEntry(value, ttl)

        # Evict oldest if over capacity
        if len(cache) > self.max_size:
            oldest_key = next(iter(cache))
            del cache[oldest_key]
            logger.debug(f"L1 cache evicted: {oldest_key}")

    def delete(self, key: str) -> bool:
        """Delete key from L1 cache.

        Args:
            key: Cache key

        Returns:
            True if key existed and was deleted, False otherwise
        """
        cache = self._get_cache()
        if key in cache:
            del cache[key]
            return True
        return False

    def exists(self, key: str) -> bool:
        """Check if key exists in L1 cache (without changing LRU order).

        Args:
            key: Cache key

        Returns:
            True if key exists and not expired, False otherwise
        """
        cache = self._get_cache()
        if key not in cache:
            return False

        entry = cache[key]
        if entry.is_expired():
            del cache[key]
            return False

        return True

    def clear(self) -> None:
        """Clear thread-local cache."""
        if hasattr(self._local, "cache"):
            self._local.cache.clear()
            self._local.hits = 0
            self._local.misses = 0

    def get_stats(self) -> dict[str, Any]:
        """Get L1 cache statistics for this thread.

        Returns:
            Dict with hit rate, size, and utilization metrics
        """
        cache = self._get_cache()
        hits, misses = self._get_stats_local()
        total = hits + misses

        return {
            "hits": hits,
            "misses": misses,
            "hit_rate": (hits / total * 100) if total > 0 else 0.0,
            "size": len(cache),
            "max_size": self.max_size,
            "utilization": len(cache) / self.max_size,
        }

    def cleanup_expired(self) -> int:
        """Remove expired entries from L1 cache.

        Returns:
            Number of entries cleaned up
        """
        cache = self._get_cache()
        expired_keys = [k for k, v in cache.items() if v.is_expired()]
        for key in expired_keys:
            del cache[key]
        return len(expired_keys)

    def get_keys(self) -> list[str]:
        """Get all keys in L1 cache for this thread."""
        return list(self._get_cache().keys())


class L1CacheDecorator:
    """Decorator for caching function results in L1 cache.

    Usage:
        cache = L1RequestCache()
        decorator = L1CacheDecorator(cache)

        @decorator.cache_result(ttl=300)
        def expensive_operation(query_id: str) -> dict:
            return {"result": "expensive computation"}

        result1 = expensive_operation("123")  # Executes function
        result2 = expensive_operation("123")  # Returns cached result
    """

    def __init__(self, cache: L1RequestCache):
        """Initialize decorator with cache instance."""
        self.cache = cache

    def cache_result(self, ttl: Optional[int] = None) -> Callable:
        """Decorator to cache function results.

        Args:
            ttl: Optional TTL in seconds

        Returns:
            Decorated function
        """

        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            def wrapper(*args, **kwargs) -> T:
                # Generate cache key from function name and arguments
                # Use sorted kwargs to ensure consistent key generation regardless of order
                sorted_kwargs = sorted(kwargs.items())
                cache_key = f"{func.__module__}.{func.__name__}:{hashlib.sha256(f'{args}:{sorted_kwargs}'.encode()).hexdigest()}"

                # Try to get from cache
                cached_value = self.cache.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"L1 cache hit: {func.__name__}")
                    return cached_value

                # Cache miss, compute and store
                logger.debug(f"L1 cache miss: {func.__name__}")
                result = func(*args, **kwargs)
                self.cache.set(cache_key, result, ttl)
                return result

            return wrapper

        return decorator


# Global L1 cache instance
_l1_cache_instance: Optional[L1RequestCache] = None


def get_l1_cache() -> L1RequestCache:
    """Get the global L1 cache instance (singleton per thread)."""
    global _l1_cache_instance
    if _l1_cache_instance is None:
        _l1_cache_instance = L1RequestCache()
    return _l1_cache_instance


def reset_l1_cache() -> None:
    """Reset the global L1 cache (for testing or request cleanup)."""
    cache = get_l1_cache()
    cache.clear()
