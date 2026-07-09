"""Tokenization cache with TTL and invalidation strategy."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Any, Optional


class TokenizationCache:
    """Cache for tokenization results with time-to-live and invalidation.

    This cache helps avoid re-tokenizing the same text repeatedly, while
    ensuring that cached results don't become stale when tokenizer
    configuration changes.

    Attributes:
        DEFAULT_TTL_HOURS: Default time-to-live for cache entries in hours
    """

    DEFAULT_TTL_HOURS = 24

    def __init__(self, ttl_hours: int = DEFAULT_TTL_HOURS):
        """Initialize tokenization cache.

        Args:
            ttl_hours: Time-to-live for cache entries in hours
        """
        self.cache: dict[str, dict[str, Any]] = {}
        self.ttl = timedelta(hours=ttl_hours)

    def _get_cache_key(self, text: str, tokenizer_config: dict[str, Any]) -> str:
        """Generate cache key from text and tokenizer config.

        The key is a hash of both the text and the tokenizer configuration
        to ensure that changing tokenizer settings invalidates the cache.

        Args:
            text: Text to be tokenized
            tokenizer_config: Tokenizer configuration dict

        Returns:
            SHA256 hash as hex string
        """
        config_str = json.dumps(tokenizer_config, sort_keys=True)
        combined = f"{text}|{config_str}"
        return hashlib.sha256(combined.encode()).hexdigest()

    def get(self, text: str, tokenizer_config: dict[str, Any]) -> Optional[list[Any]]:
        """Get tokens from cache if available and not expired.

        Args:
            text: Text to look up
            tokenizer_config: Tokenizer configuration dict

        Returns:
            Cached tokens if available and not expired, None otherwise
        """
        key = self._get_cache_key(text, tokenizer_config)
        if key in self.cache:
            entry = self.cache[key]
            if datetime.now(timezone.utc) - entry["timestamp"] < self.ttl:
                return entry["tokens"]
            # Cache expired, remove entry
            del self.cache[key]
        return None

    def set(self, text: str, tokenizer_config: dict[str, Any], tokens: list[Any]) -> None:
        """Store tokens in cache.

        Args:
            text: Text that was tokenized
            tokenizer_config: Tokenizer configuration dict
            tokens: Tokenization result to cache
        """
        key = self._get_cache_key(text, tokenizer_config)
        self.cache[key] = {"tokens": tokens, "timestamp": datetime.now(timezone.utc)}

    def invalidate_all(self) -> None:
        """Invalidate all cached entries.

        Use this when making global changes to tokenization configuration
        that should invalidate all existing cache entries.
        """
        self.cache.clear()

    def invalidate_expired(self) -> int:
        """Remove all expired entries from cache.

        Returns:
            Number of entries removed
        """
        expired_keys = []
        now = datetime.now(timezone.utc)

        for key, entry in self.cache.items():
            if now - entry["timestamp"] >= self.ttl:
                expired_keys.append(key)

        for key in expired_keys:
            del self.cache[key]

        return len(expired_keys)

    def size(self) -> int:
        """Get number of entries in cache.

        Returns:
            Number of cached entries
        """
        return len(self.cache)

    def stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            dict containing cache statistics including size and oldest entry age
        """
        if not self.cache:
            return {"size": 0, "oldest_entry_age_seconds": 0, "expired_count": 0}

        now = datetime.now(timezone.utc)
        ages = [(now - entry["timestamp"]).total_seconds() for entry in self.cache.values()]
        expired = sum(1 for age in ages if timedelta(seconds=age) >= self.ttl)

        return {
            "size": len(self.cache),
            "oldest_entry_age_seconds": max(ages) if ages else 0,
            "expired_count": expired,
        }


# Global cache instance for convenience
_global_cache: Optional[TokenizationCache] = None


def get_global_cache(
    ttl_hours: int = TokenizationCache.DEFAULT_TTL_HOURS,
) -> TokenizationCache:
    """Get or create the global tokenization cache instance.

    Args:
        ttl_hours: TTL for cache entries if creating new instance

    Returns:
        Global TokenizationCache instance
    """
    global _global_cache
    if _global_cache is None:
        _global_cache = TokenizationCache(ttl_hours=ttl_hours)
    return _global_cache


def reset_global_cache() -> None:
    """Reset the global cache instance.

    Useful for testing or when you want to completely clear the cache.
    """
    global _global_cache
    _global_cache = None


__all__ = [
    "TokenizationCache",
    "get_global_cache",
    "reset_global_cache",
]
