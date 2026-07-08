"""Cache management utilities for session and query result caching.

This module provides utilities for:
- Cache entry management with TTL
- Cache invalidation
- Cache expiration checking
- TTL (Time-To-Live) management
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class CacheEntry(Generic[T]):
    """Represents a cached value with timestamp and TTL support.

    Attributes
    ----------
    data : Any
        Cached data
    timestamp : float
        Unix timestamp when the entry was created
    """

    data: T
    timestamp: float

    def is_expired(self, ttl: int = 300) -> bool:
        """Check if this cache entry has expired.

        Parameters
        ----------
        ttl : int, optional
            Time-to-live in seconds (default: 300 = 5 minutes)

        Returns
        -------
        bool
            True if the entry has expired, False otherwise
        """
        return time.time() - self.timestamp > ttl

    def age_seconds(self) -> float:
        """Get the age of this cache entry in seconds.

        Returns
        -------
        float
            Age in seconds since creation
        """
        return time.time() - self.timestamp

    def get_if_valid(self, ttl: int = 300) -> T | None:
        """Get the cached data if it hasn't expired.

        Parameters
        ----------
        ttl : int, optional
            Time-to-live in seconds (default: 300 = 5 minutes)

        Returns
        -------
        Any | None
            The cached data if valid, None if expired
        """
        if not self.is_expired(ttl):
            return self.data
        return None


class SimpleCache:
    """Simple in-memory cache with TTL support.

    Features:
    - Thread-unsafe but fast
    - Lazy expiration (entries expire on access)
    - Configurable default TTL
    - Manual invalidation support
    """

    def __init__(self, default_ttl: int = 300) -> None:
        """Initialize the cache.

        Parameters
        ----------
        default_ttl : int, optional
            Default time-to-live for cache entries in seconds (default: 300)
        """
        self._cache: dict[str, CacheEntry] = {}
        self.default_ttl = default_ttl
        self.hits = 0
        self.misses = 0

    def get(self, key: str, ttl: int | None = None) -> Any | None:
        """Get a value from the cache.

        Parameters
        ----------
        key : str
            Cache key
        ttl : int, optional
            Time-to-live in seconds. If None, uses default_ttl

        Returns
        -------
        Any | None
            The cached value if found and valid, None otherwise
        """
        if key not in self._cache:
            self.misses += 1
            return None

        entry = self._cache[key]
        ttl_to_use = ttl if ttl is not None else self.default_ttl

        if entry.is_expired(ttl_to_use):
            del self._cache[key]
            self.misses += 1
            return None

        self.hits += 1
        return entry.data

    def set(self, key: str, value: Any) -> None:
        """Set a value in the cache.

        Parameters
        ----------
        key : str
            Cache key
        value : Any
            Value to cache
        """
        self._cache[key] = CacheEntry(data=value, timestamp=time.time())

    def delete(self, key: str) -> bool:
        """Delete a specific cache entry.

        Parameters
        ----------
        key : str
            Cache key

        Returns
        -------
        bool
            True if the entry existed and was deleted, False otherwise
        """
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        self.hits = 0
        self.misses = 0

    def cleanup_expired(self, ttl: int | None = None) -> int:
        """Remove all expired entries from the cache.

        Parameters
        ----------
        ttl : int, optional
            Time-to-live in seconds. If None, uses default_ttl

        Returns
        -------
        int
            Number of entries removed
        """
        ttl_to_use = ttl if ttl is not None else self.default_ttl
        keys_to_delete = [key for key, entry in self._cache.items() if entry.is_expired(ttl_to_use)]
        for key in keys_to_delete:
            del self._cache[key]
        return len(keys_to_delete)

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns
        -------
        dict[str, Any]
            Statistics including size, hits, misses, and hit rate
        """
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0.0
        return {
            "size": len(self._cache),
            "hits": self.hits,
            "misses": self.misses,
            "total_accesses": total,
            "hit_rate": hit_rate,
        }


def validate_ttl(ttl: int, min_ttl: int = 1, max_ttl: int = 86400) -> int:
    """Validate and constrain a TTL value.

    Parameters
    ----------
    ttl : int
        TTL value in seconds
    min_ttl : int, optional
        Minimum allowed TTL (default: 1)
    max_ttl : int, optional
        Maximum allowed TTL (default: 86400 = 1 day)

    Returns
    -------
    int
        Validated TTL value

    Raises
    ------
    ValueError
        If ttl is invalid
    """
    if not isinstance(ttl, int):
        raise ValueError(f"TTL must be an integer, got {type(ttl).__name__}")
    if ttl < min_ttl:
        raise ValueError(f"TTL must be >= {min_ttl}, got {ttl}")
    if ttl > max_ttl:
        raise ValueError(f"TTL must be <= {max_ttl}, got {ttl}")
    return ttl


def convert_ttl_to_seconds(value: int | str, unit: str = "seconds") -> int:
    """Convert a TTL value with unit to seconds.

    Parameters
    ----------
    value : int | str
        TTL value
    unit : str, optional
        Unit of time: 'seconds', 'minutes', 'hours', 'days' (default: 'seconds')

    Returns
    -------
    int
        TTL in seconds

    Raises
    ------
    ValueError
        If unit is not recognized
    """
    multipliers = {
        "seconds": 1,
        "minutes": 60,
        "hours": 3600,
        "days": 86400,
    }

    if unit not in multipliers:
        raise ValueError(f"Unknown TTL unit: {unit}")

    return int(value) * multipliers[unit]
