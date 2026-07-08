"""
Context Cache

Caches static context (system prompts, API schemas, instructions) across requests
to reduce token usage and improve response consistency.

Reference: Context Engineering Guide 2025 - 25-40% token savings through caching
"""

import hashlib
import json
import logging
import os
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """A cached context entry."""

    key: str
    content: str
    content_hash: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_accessed: datetime = field(default_factory=lambda: datetime.now(UTC))
    access_count: int = 0
    ttl_seconds: Optional[int] = None
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def token_estimate(self) -> int:
        """Estimate token count."""
        return len(self.content) // 4 + 1

    @property
    def is_expired(self) -> bool:
        """Check if entry has expired."""
        if self.ttl_seconds is None:
            return False
        age = (datetime.now(UTC) - self.created_at).total_seconds()
        return age > self.ttl_seconds

    @property
    def age_seconds(self) -> float:
        """Age of entry in seconds."""
        return (datetime.now(UTC) - self.created_at).total_seconds()


@dataclass
class CacheStats:
    """Cache statistics."""

    total_entries: int
    total_tokens: int
    hit_count: int
    miss_count: int
    hit_rate: float
    tokens_saved: int  # Estimated tokens saved by cache hits


class ContextCache:
    """
    Cache for static context across requests.

    Provides:
    - In-memory caching with optional disk persistence
    - TTL-based expiration
    - LRU eviction when over capacity
    - Token savings tracking
    """

    DEFAULT_MAX_ENTRIES = 100
    DEFAULT_MAX_TOKENS = 100_000
    DEFAULT_TTL = 3600  # 1 hour

    def __init__(
        self,
        max_entries: int = DEFAULT_MAX_ENTRIES,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        default_ttl: Optional[int] = DEFAULT_TTL,
        persist_path: Optional[str] = None,
    ):
        """
        Initialize context cache.

        Args:
            max_entries: Maximum cache entries
            max_tokens: Maximum total tokens cached
            default_ttl: Default TTL in seconds (None = no expiration)
            persist_path: Optional path for disk persistence
        """
        self.max_entries = max_entries
        self.max_tokens = max_tokens
        self.default_ttl = default_ttl
        self.persist_path = persist_path

        self._cache: dict[str, CacheEntry] = {}
        self._total_tokens = 0
        self._hits = 0
        self._misses = 0
        self._tokens_saved = 0
        self._lock = threading.RLock()

        # Load from disk if path provided
        if persist_path and os.path.exists(persist_path):
            self._load_from_disk()

    def get(self, key: str) -> Optional[str]:
        """
        Get cached content by key.

        Args:
            key: Cache key

        Returns:
            Cached content or None if not found/expired
        """
        with self._lock:
            entry = self._cache.get(key)

            if entry is None:
                self._misses += 1
                return None

            if entry.is_expired:
                self._remove_entry(key)
                self._misses += 1
                return None

            # Update access stats
            entry.last_accessed = datetime.now(UTC)
            entry.access_count += 1
            self._hits += 1
            self._tokens_saved += entry.token_estimate

            return entry.content

    def set(
        self,
        key: str,
        content: str,
        ttl: Optional[int] = None,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> bool:
        """
        Cache content with key.

        Args:
            key: Cache key
            content: Content to cache
            ttl: TTL in seconds (None = use default)
            tags: Optional tags for filtering
            metadata: Optional metadata

        Returns:
            True if cached, False if rejected
        """
        with self._lock:
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            token_count = len(content) // 4 + 1

            # Check if already cached with same content
            existing = self._cache.get(key)
            if existing and existing.content_hash == content_hash:
                existing.last_accessed = datetime.now(UTC)
                existing.access_count += 1
                return True

            # Remove existing entry if different content
            if existing:
                self._remove_entry(key)

            # Ensure capacity
            self._ensure_capacity(token_count)

            # Check limits after eviction
            if len(self._cache) >= self.max_entries:
                return False
            if self._total_tokens + token_count > self.max_tokens:
                return False

            # Create entry
            entry = CacheEntry(
                key=key,
                content=content,
                content_hash=content_hash,
                ttl_seconds=ttl if ttl is not None else self.default_ttl,
                tags=tags or [],
                metadata=metadata or {},
            )

            self._cache[key] = entry
            self._total_tokens += token_count

            # Persist if enabled
            if self.persist_path:
                self._save_to_disk()

            return True

    def get_or_set(
        self,
        key: str,
        content_fn: Callable[..., Any],
        ttl: Optional[int] = None,
        tags: Optional[list[str]] = None,
    ) -> str:
        """
        Get cached content or compute and cache it.

        Args:
            key: Cache key
            content_fn: Function to compute content if not cached
            ttl: TTL in seconds
            tags: Optional tags

        Returns:
            Cached or computed content
        """
        cached = self.get(key)
        if cached is not None:
            return cached

        content = content_fn()
        self.set(key, content, ttl=ttl, tags=tags)
        return content

    def invalidate(self, key: str) -> bool:
        """
        Invalidate (remove) cached entry.

        Args:
            key: Cache key

        Returns:
            True if removed, False if not found
        """
        with self._lock:
            if key in self._cache:
                self._remove_entry(key)
                if self.persist_path:
                    self._save_to_disk()
                return True
            return False

    def invalidate_by_tag(self, tag: str) -> int:
        """
        Invalidate all entries with given tag.

        Args:
            tag: Tag to match

        Returns:
            Number of entries invalidated
        """
        with self._lock:
            keys_to_remove = [key for key, entry in self._cache.items() if tag in entry.tags]
            for key in keys_to_remove:
                self._remove_entry(key)

            if keys_to_remove and self.persist_path:
                self._save_to_disk()

            return len(keys_to_remove)

    def clear(self):
        """Clear all cached entries."""
        with self._lock:
            self._cache.clear()
            self._total_tokens = 0
            if self.persist_path:
                self._save_to_disk()

    def cleanup_expired(self) -> int:
        """
        Remove expired entries.

        Returns:
            Number of entries removed
        """
        with self._lock:
            expired = [key for key, entry in self._cache.items() if entry.is_expired]
            for key in expired:
                self._remove_entry(key)

            if expired and self.persist_path:
                self._save_to_disk()

            return len(expired)

    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests > 0 else 0.0

            return CacheStats(
                total_entries=len(self._cache),
                total_tokens=self._total_tokens,
                hit_count=self._hits,
                miss_count=self._misses,
                hit_rate=hit_rate,
                tokens_saved=self._tokens_saved,
            )

    def get_all_keys(self) -> list[str]:
        """Get all cache keys."""
        with self._lock:
            return list(self._cache.keys())

    def get_by_tag(self, tag: str) -> list[CacheEntry]:
        """Get all entries with given tag."""
        with self._lock:
            return [entry for entry in self._cache.values() if tag in entry.tags]

    def _remove_entry(self, key: str):
        """Remove entry and update token count."""
        entry = self._cache.pop(key, None)
        if entry:
            self._total_tokens -= entry.token_estimate

    def _ensure_capacity(self, needed_tokens: int):
        """Ensure capacity using LRU eviction."""
        # Evict expired first
        self.cleanup_expired()

        # Evict LRU if still over capacity
        while (
            len(self._cache) >= self.max_entries
            or self._total_tokens + needed_tokens > self.max_tokens
        ):
            if not self._cache:
                break

            # Find LRU entry
            lru_key = min(self._cache.keys(), key=lambda k: self._cache[k].last_accessed)
            self._remove_entry(lru_key)

    def _save_to_disk(self):
        """Save cache to disk."""
        if not self.persist_path:
            return

        data = {
            key: {
                "content": entry.content,
                "content_hash": entry.content_hash,
                "created_at": entry.created_at.isoformat(),
                "last_accessed": entry.last_accessed.isoformat(),
                "access_count": entry.access_count,
                "ttl_seconds": entry.ttl_seconds,
                "tags": entry.tags,
                "metadata": entry.metadata,
            }
            for key, entry in self._cache.items()
        }

        Path(self.persist_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.persist_path, "w") as f:
            json.dump(data, f)

    def _load_from_disk(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path) as f:
                data = json.load(f)

            for key, entry_data in data.items():
                entry = CacheEntry(
                    key=key,
                    content=entry_data["content"],
                    content_hash=entry_data["content_hash"],
                    created_at=datetime.fromisoformat(entry_data["created_at"]),
                    last_accessed=datetime.fromisoformat(entry_data["last_accessed"]),
                    access_count=entry_data["access_count"],
                    ttl_seconds=entry_data.get("ttl_seconds"),
                    tags=entry_data.get("tags", []),
                    metadata=entry_data.get("metadata", {}),
                )

                # Skip expired entries
                if not entry.is_expired:
                    self._cache[key] = entry
                    self._total_tokens += entry.token_estimate

        except (json.JSONDecodeError, KeyError, ValueError):
            # Corrupted cache file, start fresh
            self._cache.clear()
            self._total_tokens = 0
