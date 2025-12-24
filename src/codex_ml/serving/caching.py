"""
Response Caching for Inference Server

Provides LRU cache with TTL for prediction results:
- Content-based cache keys (hash of inputs)
- Time-to-live (TTL) expiration
- Memory-bounded with LRU eviction
- Cache hit rate tracking
"""

import hashlib
import json
import logging
import time
from collections import OrderedDict
from dataclasses import dataclass
from threading import Lock
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class CacheMetrics:
    """Metrics for cache performance

    Attributes:
        hits: Number of cache hits
        misses: Number of cache misses
        evictions: Number of cache evictions
        total_size: Current number of entries in cache
        max_size: Maximum cache size
    """

    hits: int = 0
    misses: int = 0
    evictions: int = 0
    total_size: int = 0
    max_size: int = 1000

    def record_hit(self) -> None:
        """Record a cache hit"""
        self.hits += 1

    def record_miss(self) -> None:
        """Record a cache miss"""
        self.misses += 1

    def record_eviction(self) -> None:
        """Record a cache eviction"""
        self.evictions += 1

    def get_hit_rate(self) -> float:
        """Calculate cache hit rate (0.0 to 1.0)"""
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return self.hits / total

    def to_dict(self) -> dict[str, Any]:
        """Convert metrics to dictionary"""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "hit_rate": self.get_hit_rate(),
            "total_size": self.total_size,
            "max_size": self.max_size,
            "memory_utilization": self.total_size / self.max_size if self.max_size > 0 else 0.0,
        }


@dataclass
class CacheEntry:
    """Single cache entry with TTL

    Attributes:
        value: Cached value
        timestamp: Time when entry was created
        ttl: Time-to-live in seconds
        access_count: Number of times entry has been accessed
    """

    value: Any
    timestamp: float
    ttl: float
    access_count: int = 0

    def is_expired(self) -> bool:
        """Check if entry has expired"""
        if self.ttl <= 0:
            return False  # No expiration
        return time.time() - self.timestamp > self.ttl

    def access(self) -> Any:
        """Access the cache entry and return value"""
        self.access_count += 1
        return self.value


class ResponseCache:
    """LRU cache with TTL for inference responses

    Features:
    - Content-based keys (hash of input data)
    - TTL-based expiration
    - LRU eviction when max_size is reached
    - Thread-safe operations
    - Metrics tracking (hits, misses, evictions)

    Attributes:
        max_size: Maximum number of entries in cache
        default_ttl: Default time-to-live in seconds (0 = no expiration)
        cache: OrderedDict for LRU ordering
        metrics: Cache performance metrics
        lock: Thread lock for synchronization
    """

    def __init__(self, max_size: int = 1000, default_ttl: float = 300.0):
        """Initialize response cache

        Args:
            max_size: Maximum cache entries (LRU eviction when exceeded)
            default_ttl: Default time-to-live in seconds (0 = no expiration)
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.metrics = CacheMetrics(max_size=max_size)
        self.lock = Lock()

        logger.info(f"ResponseCache initialized: max_size={max_size}, default_ttl={default_ttl}s")

    def _generate_key(self, data: Any) -> str:
        """Generate cache key from input data

        Uses content-based hashing for deterministic keys.

        Args:
            data: Input data (will be JSON serialized)

        Returns:
            Hash string as cache key
        """
        # Convert to JSON string for hashing
        json_str = json.dumps(data, sort_keys=True, default=str)
        # Generate SHA256 hash
        hash_obj = hashlib.sha256(json_str.encode())
        return hash_obj.hexdigest()

    def get(self, key_data: Any) -> Optional[Any]:
        """Get value from cache

        Args:
            key_data: Input data to generate cache key

        Returns:
            Cached value if found and not expired, None otherwise
        """
        key = self._generate_key(key_data)

        with self.lock:
            if key not in self.cache:
                self.metrics.record_miss()
                return None

            entry = self.cache[key]

            # Check expiration
            if entry.is_expired():
                logger.debug(f"Cache entry expired: {key[:8]}...")
                del self.cache[key]
                self.metrics.total_size = len(self.cache)
                self.metrics.record_miss()
                return None

            # Move to end (most recently used)
            self.cache.move_to_end(key)

            # Record hit and return value
            self.metrics.record_hit()
            return entry.access()

    def put(self, key_data: Any, value: Any, ttl: Optional[float] = None) -> None:
        """Put value into cache

        Args:
            key_data: Input data to generate cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None = use default_ttl)
        """
        key = self._generate_key(key_data)
        ttl = ttl if ttl is not None else self.default_ttl

        with self.lock:
            # Check if we need to evict
            if key not in self.cache and len(self.cache) >= self.max_size:
                # Evict least recently used (first item)
                evicted_key, _ = self.cache.popitem(last=False)
                self.metrics.record_eviction()
                logger.debug(f"Evicted cache entry: {evicted_key[:8]}...")

            # Add/update entry
            entry = CacheEntry(value=value, timestamp=time.time(), ttl=ttl)
            self.cache[key] = entry

            # Move to end (most recently used)
            if key in self.cache:
                self.cache.move_to_end(key)

            self.metrics.total_size = len(self.cache)
            logger.debug(f"Cached entry: {key[:8]}... (TTL: {ttl}s)")

    def clear(self) -> None:
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()
            self.metrics.total_size = 0
            logger.info("Cache cleared")

    def remove_expired(self) -> int:
        """Remove all expired entries

        Returns:
            Number of entries removed
        """
        removed = 0
        with self.lock:
            keys_to_remove = [key for key, entry in self.cache.items() if entry.is_expired()]
            for key in keys_to_remove:
                del self.cache[key]
                removed += 1

            self.metrics.total_size = len(self.cache)

        if removed > 0:
            logger.info(f"Removed {removed} expired cache entries")

        return removed

    def get_metrics(self) -> dict[str, Any]:
        """Get current cache metrics"""
        with self.lock:
            self.metrics.total_size = len(self.cache)
            return self.metrics.to_dict()

    def __len__(self) -> int:
        """Get current cache size"""
        return len(self.cache)

    def __contains__(self, key_data: Any) -> bool:
        """Check if key is in cache (not expired)"""
        return self.get(key_data) is not None
