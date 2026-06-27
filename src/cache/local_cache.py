"""
Local in-memory LRU cache implementation.

Uses Python's built-in functools.lru_cache inspired approach with manual
dictionary tracking for cache key visibility and statistics.

Optimizations:
- O(1) get/set/delete operations
- Automatic LRU eviction when max_size reached
- TTL support with lazy eviction
- Cache statistics tracking
"""

from __future__ import annotations

import logging
import time
from collections import OrderedDict
from typing import Any, Optional

from .base import CacheBackend

logger = logging.getLogger(__name__)

# Safeguards
DEFAULT_MAX_SIZE = 10000
DEFAULT_TTL = 3600  # 1 hour


class LocalLRUCache(CacheBackend):
    """In-memory LRU cache for local use."""

    def __init__(self, max_size: int = DEFAULT_MAX_SIZE) -> None:
        """Initialize LRU cache."""
        self.max_size = max_size
        self._cache: OrderedDict[str, dict[str, Any]] = OrderedDict()
        self._hits = 0
        self._misses = 0
        logger.info(f"LocalLRUCache initialized with max_size={max_size}")

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache, moving to end (most recently used)."""
        if key not in self._cache:
            self._misses += 1
            return None

        # Check TTL
        entry = self._cache[key]
        if entry.get("ttl_at") and time.time() > entry["ttl_at"]:
            del self._cache[key]
            self._misses += 1
            return None

        # Move to end (most recently used)
        self._cache.move_to_end(key)
        self._hits += 1
        return entry["value"]

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with optional TTL."""
        # If key exists, remove it first to update position
        if key in self._cache:
            del self._cache[key]

        # Add to cache
        ttl_at = None
        if ttl:
            ttl_at = time.time() + ttl

        self._cache[key] = {
            "value": value,
            "ttl_at": ttl_at,
            "created_at": time.time(),
        }

        # Evict oldest item if over capacity
        if len(self._cache) > self.max_size:
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
            logger.debug(f"LRU eviction: removed {oldest_key}")

    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def exists(self, key: str) -> bool:
        """Check if key exists in cache (without changing LRU order)."""
        if key not in self._cache:
            return False

        # Check TTL
        entry = self._cache[key]
        if entry.get("ttl_at") and time.time() > entry["ttl_at"]:
            del self._cache[key]
            return False

        return True

    def clear(self) -> None:
        """Clear all entries from cache."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0
        logger.info("LocalLRUCache cleared")

    def get_stats(self) -> dict:
        """Get cache statistics."""
        total = self._hits + self._misses
        hit_rate = self._hits / total if total > 0 else 0.0

        return {
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": hit_rate,
            "size": len(self._cache),
            "max_size": self.max_size,
            "utilization": len(self._cache) / self.max_size,
        }

    def get_keys(self) -> list[str]:
        """Get all keys in cache."""
        return list(self._cache.keys())

    def get_size_bytes(self) -> int:
        """Estimate cache size in bytes."""
        import sys

        total = 0
        for key, entry in self._cache.items():
            total += sys.getsizeof(key) + sys.getsizeof(entry["value"])
        return total
