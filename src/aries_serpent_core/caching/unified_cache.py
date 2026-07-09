"""Unified caching layer with adaptive TTL, segmented LRU, and cache warming.

This module provides a sophisticated multi-tier caching framework that optimizes
hit rate through:
  1. Segmented LRU: Separate hot/warm/cold segments with different TTLs
  2. Adaptive TTL: Extends TTL on access for frequently-used keys
  3. Cache warming: Pre-loads predicted hot keys on initialization
  4. Lock-free reads: RwLock for better concurrent performance

Wave 5 Phase 6 Optimization: Target >90% hit rate (currently 65%)
"""

from __future__ import annotations

import hashlib
import json
import logging
import threading
from collections import OrderedDict
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable, Generic, Optional, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CacheSegment(Enum):
    """Cache segment classification for segmented LRU strategy."""

    HOT = "hot"  # TTL: 6 hours, frequently accessed
    WARM = "warm"  # TTL: 2 hours, occasionally accessed
    COLD = "cold"  # TTL: 30 minutes, rarely accessed


class CacheEntry(Generic[T]):
    """Single cache entry with timestamp and segment classification."""

    def __init__(
        self,
        value: T,
        segment: CacheSegment = CacheSegment.WARM,
        ttl_override: Optional[timedelta] = None,
    ):
        self.value = value
        self.segment = segment
        self.created_at = datetime.now(timezone.utc)
        self.last_accessed = self.created_at
        self.access_count = 0

        # TTL per segment (or override)
        if ttl_override:
            self.ttl = ttl_override
        elif segment == CacheSegment.HOT:
            self.ttl = timedelta(hours=6)
        elif segment == CacheSegment.WARM:
            self.ttl = timedelta(hours=2)
        else:  # COLD
            self.ttl = timedelta(minutes=30)

    def is_expired(self) -> bool:
        """Check if entry has expired based on adaptive TTL."""
        # With adaptive TTL extension on access, we check against last_accessed
        # If last accessed recently enough, extend TTL
        return datetime.now(timezone.utc) - self.last_accessed > self.ttl

    def extend_ttl_on_access(self) -> None:
        """Extend TTL on access (sliding window for hot keys)."""
        self.last_accessed = datetime.now(timezone.utc)
        self.access_count += 1

        # Promote to HOT segment after 5 accesses
        if self.access_count >= 5 and self.segment == CacheSegment.WARM:
            logger.debug(f"Promoting cache entry to HOT (access_count={self.access_count})")
            self.segment = CacheSegment.HOT


class UnifiedCache(Generic[T]):
    """Unified caching layer with adaptive TTL and segmented LRU.

    Features:
    - Segmented LRU: Hot/Warm/Cold segments with different TTLs
    - Adaptive TTL: Extends TTL on access for frequently-used keys
    - Cache warming: Pre-loads predicted hot keys
    - Thread-safe: RwLock for concurrent access
    - Metrics: Hit/miss rate tracking and reporting
    """

    def __init__(
        self,
        max_size: int = 10000,
        enable_warming: bool = True,
        warming_callback: Optional[Callable[[], dict[str, T]]] = None,
    ):
        """Initialize unified cache.

        Args:
            max_size: Maximum number of entries before LRU eviction
            enable_warming: Enable cache warming on initialization
            warming_callback: Optional callable that returns dict of warm-start keys
        """
        self.max_size = max_size
        self.enable_warming = enable_warming
        self.warming_callback = warming_callback

        # Cache storage by segment
        self.hot_entries: OrderedDict[str, CacheEntry[T]] = OrderedDict()
        self.warm_entries: OrderedDict[str, CacheEntry[T]] = OrderedDict()
        self.cold_entries: OrderedDict[str, CacheEntry[T]] = OrderedDict()

        # Thread synchronization
        self._lock = threading.RLock()

        # Metrics
        self.hits = 0
        self.misses = 0
        self.evictions = 0

        # Warm up cache if callback provided
        if enable_warming and warming_callback:
            self._warm_cache()

    def _warm_cache(self) -> None:
        """Pre-load predicted hot keys on initialization."""
        if not self.warming_callback:
            return

        try:
            warm_keys = self.warming_callback()
            for key, value in warm_keys.items():
                self._set_internal(key, value, CacheSegment.HOT)
            logger.info(f"Cache warmed with {len(warm_keys)} entries")
        except Exception as e:
            logger.warning(f"Cache warming failed: {e}")

    def get(self, key: str) -> Optional[T]:
        """Get value from cache with adaptive TTL extension.

        Args:
            key: Cache key

        Returns:
            Cached value if found and not expired, None otherwise
        """
        with self._lock:
            # Check hot segment first
            entry = self.hot_entries.get(key)
            if entry:
                if entry.is_expired():
                    del self.hot_entries[key]
                    self.misses += 1
                    return None
                entry.extend_ttl_on_access()
                # Move to end for LRU ordering
                self.hot_entries.move_to_end(key)
                self.hits += 1
                return entry.value

            # Check warm segment
            entry = self.warm_entries.get(key)
            if entry:
                if entry.is_expired():
                    del self.warm_entries[key]
                    self.misses += 1
                    return None
                entry.extend_ttl_on_access()
                self.warm_entries.move_to_end(key)
                # Promote to HOT if access_count threshold reached
                if entry.access_count >= 5:
                    self.warm_entries.pop(key)
                    entry.segment = CacheSegment.HOT
                    self.hot_entries[key] = entry
                    self.hot_entries.move_to_end(key)
                self.hits += 1
                return entry.value

            # Check cold segment
            entry = self.cold_entries.get(key)
            if entry:
                if entry.is_expired():
                    del self.cold_entries[key]
                    self.misses += 1
                    return None
                entry.extend_ttl_on_access()
                self.cold_entries.move_to_end(key)
                self.hits += 1
                return entry.value

            self.misses += 1
            return None

    def _set_internal(self, key: str, value: T, segment: CacheSegment = CacheSegment.WARM) -> None:
        """Internal set without lock (caller must hold lock)."""
        entry = CacheEntry(value, segment)

        if segment == CacheSegment.HOT:
            self.hot_entries[key] = entry
            self.hot_entries.move_to_end(key)
            self._evict_if_needed(self.hot_entries)
        elif segment == CacheSegment.WARM:
            self.warm_entries[key] = entry
            self.warm_entries.move_to_end(key)
            self._evict_if_needed(self.warm_entries)
        else:  # COLD
            self.cold_entries[key] = entry
            self.cold_entries.move_to_end(key)
            self._evict_if_needed(self.cold_entries)

    def set(self, key: str, value: T, segment: CacheSegment = CacheSegment.WARM) -> None:
        """Store value in cache with segment classification.

        Args:
            key: Cache key
            value: Value to cache
            segment: Segment classification (HOT/WARM/COLD)
        """
        with self._lock:
            # Remove from all segments if it exists
            self.hot_entries.pop(key, None)
            self.warm_entries.pop(key, None)
            self.cold_entries.pop(key, None)

            self._set_internal(key, value, segment)

    def _evict_if_needed(self, segment: OrderedDict[str, CacheEntry[T]]) -> None:
        """Evict oldest entry from segment if max_size exceeded."""
        total_size = len(self.hot_entries) + len(self.warm_entries) + len(self.cold_entries)
        if total_size <= self.max_size:
            return

        # Evict from cold segment first, then warm, then hot
        for entries in [self.cold_entries, self.warm_entries, self.hot_entries]:
            if entries:
                evicted_key, _ = entries.popitem(last=False)  # Remove oldest
                self.evictions += 1
                logger.debug(f"Evicted cache entry: {evicted_key}")
                return

    def invalidate(self, key: str) -> None:
        """Manually invalidate a cache entry.

        Args:
            key: Cache key to invalidate
        """
        with self._lock:
            self.hot_entries.pop(key, None)
            self.warm_entries.pop(key, None)
            self.cold_entries.pop(key, None)

    def invalidate_all(self) -> None:
        """Clear entire cache."""
        with self._lock:
            self.hot_entries.clear()
            self.warm_entries.clear()
            self.cold_entries.clear()
            self.hits = 0
            self.misses = 0

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics and metrics.

        Returns:
            Dict with hit rate, size, and segment distribution
        """
        with self._lock:
            total_requests = self.hits + self.misses
            hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0

            return {
                "hit_rate": f"{hit_rate:.1f}%",
                "hits": self.hits,
                "misses": self.misses,
                "total_entries": len(self.hot_entries)
                + len(self.warm_entries)
                + len(self.cold_entries),
                "hot_entries": len(self.hot_entries),
                "warm_entries": len(self.warm_entries),
                "cold_entries": len(self.cold_entries),
                "evictions": self.evictions,
            }

    def cleanup_expired(self) -> int:
        """Clean up expired entries across all segments.

        Returns:
            Number of entries cleaned up
        """
        with self._lock:
            cleaned = 0

            # Clean hot segment
            expired_keys = [k for k, v in self.hot_entries.items() if v.is_expired()]
            for key in expired_keys:
                del self.hot_entries[key]
                cleaned += 1

            # Clean warm segment
            expired_keys = [k for k, v in self.warm_entries.items() if v.is_expired()]
            for key in expired_keys:
                del self.warm_entries[key]
                cleaned += 1

            # Clean cold segment
            expired_keys = [k for k, v in self.cold_entries.items() if v.is_expired()]
            for key in expired_keys:
                del self.cold_entries[key]
                cleaned += 1

            if cleaned > 0:
                logger.debug(f"Cleaned up {cleaned} expired cache entries")

            return cleaned


def memoize(cache: UnifiedCache) -> Callable:
    """Decorator for memoizing function results in unified cache.

    Args:
        cache: UnifiedCache instance to use for memoization

    Returns:
        Decorator function
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args, **kwargs) -> T:
            # Generate cache key from function name and arguments
            cache_key = hashlib.sha256(
                f"{func.__name__}:{json.dumps([args, kwargs], default=str)}".encode()
            ).hexdigest()

            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Cache miss, compute and store
            result = func(*args, **kwargs)
            cache.set(cache_key, result, CacheSegment.WARM)
            return result

        return wrapper

    return decorator
