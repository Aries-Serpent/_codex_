"""
Query Result Cache Module

Provides in-memory caching for query results with:
- LRU eviction policy
- TTL-based expiration
- Cache statistics tracking
- Thread-safe operations
"""

import hashlib
import logging
import threading
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class CacheStats:
    """Statistics for cache operations."""

    hits: int = 0
    misses: int = 0
    evictions: int = 0
    expirations: int = 0
    size: int = 0
    max_size: int = 0

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return self.hits / total

    @property
    def total_requests(self) -> int:
        """Total number of cache requests."""
        return self.hits + self.misses

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "expirations": self.expirations,
            "hit_rate": self.hit_rate,
            "size": self.size,
            "max_size": self.max_size,
            "total_requests": self.total_requests,
        }


@dataclass
class CacheEntry:
    """A single cache entry."""

    key: str
    value: Any
    created_at: float = field(default_factory=time.time)
    expires_at: Optional[float] = None
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)

    @property
    def is_expired(self) -> bool:
        """Check if entry has expired."""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at

    def touch(self) -> None:
        """Update access time and count."""
        self.access_count += 1
        self.last_accessed = time.time()


@dataclass
class QueryCacheConfig:
    """Configuration for query cache."""

    max_size: int = 1000  # Maximum number of entries
    default_ttl: float = 300.0  # Default TTL in seconds (5 minutes)
    enable_stats: bool = True
    cleanup_interval: float = 60.0  # Cleanup interval in seconds
    thread_safe: bool = True


class QueryCache:
    """
    In-memory query result cache with LRU eviction.

    Features:
    - LRU (Least Recently Used) eviction policy
    - TTL-based expiration
    - Thread-safe operations
    - Cache statistics tracking

    Example:
        cache = QueryCache(QueryCacheConfig(max_size=500))

        # Store result
        cache.put("query1", results, ttl=60.0)

        # Retrieve result
        result = cache.get("query1")

        # Get stats
        stats = cache.get_stats()
        print(f"Hit rate: {stats.hit_rate:.2%}")
    """

    def __init__(
        self,
        config: Optional[QueryCacheConfig] = None,
        *,
        ttl: Optional[float] = None,
    ):
        """Initialize query cache.

        Args:
            config: Optional :class:`QueryCacheConfig` instance.
            ttl: Convenience shorthand for ``config.default_ttl``.  Ignored when
                *config* is provided explicitly.
        """
        if config is None:
            config = QueryCacheConfig(default_ttl=ttl) if ttl is not None else QueryCacheConfig()
        self.config = config

        # Use OrderedDict for LRU ordering
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._stats = CacheStats(max_size=self.config.max_size)

        # Thread safety
        self._lock = threading.RLock() if self.config.thread_safe else None

        # Background cleanup
        self._last_cleanup = time.time()

        logger.debug(
            f"QueryCache initialized: max_size={self.config.max_size}, "
            f"ttl={self.config.default_ttl}s"
        )

    def _acquire_lock(self):
        """Acquire lock if thread-safe mode is enabled."""
        if self._lock:
            self._lock.acquire()

    def _release_lock(self):
        """Release lock if thread-safe mode is enabled."""
        if self._lock:
            self._lock.release()

    def _generate_key(self, query: Any) -> str:
        """Generate cache key from query."""
        if isinstance(query, str):
            data = query.encode()
        else:
            import json

            data = json.dumps(query, sort_keys=True).encode()
        return hashlib.sha256(data).hexdigest()[:16]

    def _maybe_cleanup(self) -> None:
        """Perform cleanup if interval has passed."""
        now = time.time()
        if now - self._last_cleanup >= self.config.cleanup_interval:
            self._cleanup_expired()
            self._last_cleanup = now

    def _cleanup_expired(self) -> None:
        """Remove expired entries."""
        expired_keys = []
        for key, entry in self._cache.items():
            if entry.is_expired:
                expired_keys.append(key)

        for key in expired_keys:
            del self._cache[key]
            self._stats.expirations += 1

        self._stats.size = len(self._cache)

        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired entries")

    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if not self._cache:
            return

        # OrderedDict maintains insertion order; first item is LRU
        oldest_key = next(iter(self._cache))
        del self._cache[oldest_key]
        self._stats.evictions += 1
        self._stats.size = len(self._cache)

        logger.debug(f"Evicted LRU entry: {oldest_key[:16]}...")

    def get(self, query: Any) -> Optional[Any]:
        """
        Get cached result for query.

        Args:
            query: Query string or object

        Returns:
            Cached result or None if not found/expired
        """
        key = self._generate_key(query)

        self._acquire_lock()
        try:
            self._maybe_cleanup()

            if key not in self._cache:
                if self.config.enable_stats:
                    self._stats.misses += 1
                return None

            entry = self._cache[key]

            # Check expiration
            if entry.is_expired:
                del self._cache[key]
                self._stats.expirations += 1
                self._stats.size = len(self._cache)
                if self.config.enable_stats:
                    self._stats.misses += 1
                return None

            # Update access info and move to end (most recently used)
            entry.touch()
            self._cache.move_to_end(key)

            if self.config.enable_stats:
                self._stats.hits += 1

            return entry.value

        finally:
            self._release_lock()

    def put(
        self,
        query: Any,
        value: Any,
        ttl: Optional[float] = None,
    ) -> None:
        """
        Store result in cache.

        Args:
            query: Query string or object
            value: Result to cache
            ttl: Optional TTL in seconds (uses default if not provided)
        """
        key = self._generate_key(query)
        ttl = ttl if ttl is not None else self.config.default_ttl

        self._acquire_lock()
        try:
            # Evict if at capacity
            while len(self._cache) >= self.config.max_size:
                self._evict_lru()

            # Create entry
            now = time.time()
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=now,
                expires_at=now + ttl if ttl > 0 else None,
            )

            # Store and move to end
            self._cache[key] = entry
            self._cache.move_to_end(key)
            self._stats.size = len(self._cache)

        finally:
            self._release_lock()

    def delete(self, query: Any) -> bool:
        """
        Delete entry from cache.

        Args:
            query: Query to delete

        Returns:
            True if entry was deleted, False if not found
        """
        key = self._generate_key(query)

        self._acquire_lock()
        try:
            if key in self._cache:
                del self._cache[key]
                self._stats.size = len(self._cache)
                return True
            return False
        finally:
            self._release_lock()

    def clear(self) -> None:
        """Clear all entries from cache."""
        self._acquire_lock()
        try:
            self._cache.clear()
            self._stats.size = 0
            logger.debug("Cache cleared")
        finally:
            self._release_lock()

    def contains(self, query: Any) -> bool:
        """Check if query is in cache (without updating access time)."""
        key = self._generate_key(query)

        self._acquire_lock()
        try:
            if key not in self._cache:
                return False
            return not self._cache[key].is_expired
        finally:
            self._release_lock()

    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        return self._stats

    def get_entry_info(self, query: Any) -> Optional[dict[str, Any]]:
        """Get information about a cache entry."""
        key = self._generate_key(query)

        self._acquire_lock()
        try:
            if key not in self._cache:
                return None

            entry = self._cache[key]
            return {
                "key": key,
                "created_at": entry.created_at,
                "expires_at": entry.expires_at,
                "access_count": entry.access_count,
                "last_accessed": entry.last_accessed,
                "is_expired": entry.is_expired,
            }
        finally:
            self._release_lock()

    def get_all_keys(self) -> list[str]:
        """Get all cache keys."""
        self._acquire_lock()
        try:
            return list(self._cache.keys())
        finally:
            self._release_lock()

    def warm(self, entries: dict[Any, Any], ttl: Optional[float] = None) -> int:
        """
        Warm the cache with pre-computed entries.

        Args:
            entries: Dictionary of query -> result mappings
            ttl: Optional TTL for all entries

        Returns:
            Number of entries added
        """
        count = 0
        for query, value in entries.items():
            self.put(query, value, ttl)
            count += 1

        logger.info(f"Cache warmed with {count} entries")
        return count

    def __len__(self) -> int:
        """Get number of entries in cache."""
        return self._stats.size

    def __contains__(self, query: Any) -> bool:
        """Check if query is in cache."""
        return self.contains(query)
