"""
Base cache interface and data structures.

Defines the abstract interface for cache backends and common data structures.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class CacheResult:
    """Result of a cache operation."""

    key: str
    value: Any
    hit: bool  # True if found in cache, False if not found
    ttl_remaining: Optional[int] = None  # Time to live in seconds


class CacheBackend(ABC):
    """Abstract base class for cache backends."""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache by key."""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with optional TTL."""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete key from cache. Returns True if key existed."""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all entries from cache."""
        pass

    @abstractmethod
    def get_stats(self) -> dict:
        """Get cache statistics (hits, misses, size, etc)."""
        pass


def make_cache_key(namespace: str, *parts: str) -> str:
    """
    Create a hierarchical cache key.

    Args:
        namespace: Top-level namespace (e.g., 'rag', 'embedding')
        *parts: Additional key parts to join with ':'

    Returns:
        Cache key string like 'rag:query:abc123'
    """
    return ":".join([namespace] + list(parts))
