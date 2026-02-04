"""
Context Cache

Caches static context (system prompts, API schemas, instructions) across requests
to reduce token usage and improve response consistency.

Reference: Context Engineering Guide 2025 - 25-40% token savings through caching
"""

import hashlib
import logging
logger = logging.getLogger(__name__)
import json
import os
from typing import Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import threading
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


@dataclass
class CacheEntry:
    """A cached context entry."""

    key: str
    content: str
    content_hash: str
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
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
        age = (datetime.now() - self.created_at).total_seconds()
        return age > self.ttl_seconds

    @property
    def age_seconds(self) -> float:
        """Age of entry in seconds."""
        return (datetime.now() - self.created_at).total_seconds()


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

    def xǁContextCacheǁ__init____mutmut_orig(
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

    def xǁContextCacheǁ__init____mutmut_1(
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
        self.max_entries = None
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

    def xǁContextCacheǁ__init____mutmut_2(
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
        self.max_tokens = None
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

    def xǁContextCacheǁ__init____mutmut_3(
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
        self.default_ttl = None
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

    def xǁContextCacheǁ__init____mutmut_4(
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
        self.persist_path = None

        self._cache: dict[str, CacheEntry] = {}
        self._total_tokens = 0
        self._hits = 0
        self._misses = 0
        self._tokens_saved = 0
        self._lock = threading.RLock()

        # Load from disk if path provided
        if persist_path and os.path.exists(persist_path):
            self._load_from_disk()

    def xǁContextCacheǁ__init____mutmut_5(
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

        self._cache: dict[str, CacheEntry] = None
        self._total_tokens = 0
        self._hits = 0
        self._misses = 0
        self._tokens_saved = 0
        self._lock = threading.RLock()

        # Load from disk if path provided
        if persist_path and os.path.exists(persist_path):
            self._load_from_disk()

    def xǁContextCacheǁ__init____mutmut_6(
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
        self._total_tokens = None
        self._hits = 0
        self._misses = 0
        self._tokens_saved = 0
        self._lock = threading.RLock()

        # Load from disk if path provided
        if persist_path and os.path.exists(persist_path):
            self._load_from_disk()

    def xǁContextCacheǁ__init____mutmut_7(
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
        self._total_tokens = 1
        self._hits = 0
        self._misses = 0
        self._tokens_saved = 0
        self._lock = threading.RLock()

        # Load from disk if path provided
        if persist_path and os.path.exists(persist_path):
            self._load_from_disk()

    def xǁContextCacheǁ__init____mutmut_8(
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
        self._hits = None
        self._misses = 0
        self._tokens_saved = 0
        self._lock = threading.RLock()

        # Load from disk if path provided
        if persist_path and os.path.exists(persist_path):
            self._load_from_disk()

    def xǁContextCacheǁ__init____mutmut_9(
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
        self._hits = 1
        self._misses = 0
        self._tokens_saved = 0
        self._lock = threading.RLock()

        # Load from disk if path provided
        if persist_path and os.path.exists(persist_path):
            self._load_from_disk()

    def xǁContextCacheǁ__init____mutmut_10(
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
        self._misses = None
        self._tokens_saved = 0
        self._lock = threading.RLock()

        # Load from disk if path provided
        if persist_path and os.path.exists(persist_path):
            self._load_from_disk()

    def xǁContextCacheǁ__init____mutmut_11(
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
        self._misses = 1
        self._tokens_saved = 0
        self._lock = threading.RLock()

        # Load from disk if path provided
        if persist_path and os.path.exists(persist_path):
            self._load_from_disk()

    def xǁContextCacheǁ__init____mutmut_12(
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
        self._tokens_saved = None
        self._lock = threading.RLock()

        # Load from disk if path provided
        if persist_path and os.path.exists(persist_path):
            self._load_from_disk()

    def xǁContextCacheǁ__init____mutmut_13(
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
        self._tokens_saved = 1
        self._lock = threading.RLock()

        # Load from disk if path provided
        if persist_path and os.path.exists(persist_path):
            self._load_from_disk()

    def xǁContextCacheǁ__init____mutmut_14(
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
        self._lock = None

        # Load from disk if path provided
        if persist_path and os.path.exists(persist_path):
            self._load_from_disk()

    def xǁContextCacheǁ__init____mutmut_15(
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
        if persist_path or os.path.exists(persist_path):
            self._load_from_disk()

    def xǁContextCacheǁ__init____mutmut_16(
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
        if persist_path and os.path.exists(None):
            self._load_from_disk()
    
    xǁContextCacheǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextCacheǁ__init____mutmut_1': xǁContextCacheǁ__init____mutmut_1, 
        'xǁContextCacheǁ__init____mutmut_2': xǁContextCacheǁ__init____mutmut_2, 
        'xǁContextCacheǁ__init____mutmut_3': xǁContextCacheǁ__init____mutmut_3, 
        'xǁContextCacheǁ__init____mutmut_4': xǁContextCacheǁ__init____mutmut_4, 
        'xǁContextCacheǁ__init____mutmut_5': xǁContextCacheǁ__init____mutmut_5, 
        'xǁContextCacheǁ__init____mutmut_6': xǁContextCacheǁ__init____mutmut_6, 
        'xǁContextCacheǁ__init____mutmut_7': xǁContextCacheǁ__init____mutmut_7, 
        'xǁContextCacheǁ__init____mutmut_8': xǁContextCacheǁ__init____mutmut_8, 
        'xǁContextCacheǁ__init____mutmut_9': xǁContextCacheǁ__init____mutmut_9, 
        'xǁContextCacheǁ__init____mutmut_10': xǁContextCacheǁ__init____mutmut_10, 
        'xǁContextCacheǁ__init____mutmut_11': xǁContextCacheǁ__init____mutmut_11, 
        'xǁContextCacheǁ__init____mutmut_12': xǁContextCacheǁ__init____mutmut_12, 
        'xǁContextCacheǁ__init____mutmut_13': xǁContextCacheǁ__init____mutmut_13, 
        'xǁContextCacheǁ__init____mutmut_14': xǁContextCacheǁ__init____mutmut_14, 
        'xǁContextCacheǁ__init____mutmut_15': xǁContextCacheǁ__init____mutmut_15, 
        'xǁContextCacheǁ__init____mutmut_16': xǁContextCacheǁ__init____mutmut_16
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextCacheǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁContextCacheǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁContextCacheǁ__init____mutmut_orig)
    xǁContextCacheǁ__init____mutmut_orig.__name__ = 'xǁContextCacheǁ__init__'

    def xǁContextCacheǁget__mutmut_orig(self, key: str) -> Optional[str]:
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
            entry.last_accessed = datetime.now()
            entry.access_count += 1
            self._hits += 1
            self._tokens_saved += entry.token_estimate

            return entry.content

    def xǁContextCacheǁget__mutmut_1(self, key: str) -> Optional[str]:
        """
        Get cached content by key.

        Args:
            key: Cache key

        Returns:
            Cached content or None if not found/expired
        """
        with self._lock:
            entry = None

            if entry is None:
                self._misses += 1
                return None

            if entry.is_expired:
                self._remove_entry(key)
                self._misses += 1
                return None

            # Update access stats
            entry.last_accessed = datetime.now()
            entry.access_count += 1
            self._hits += 1
            self._tokens_saved += entry.token_estimate

            return entry.content

    def xǁContextCacheǁget__mutmut_2(self, key: str) -> Optional[str]:
        """
        Get cached content by key.

        Args:
            key: Cache key

        Returns:
            Cached content or None if not found/expired
        """
        with self._lock:
            entry = self._cache.get(None)

            if entry is None:
                self._misses += 1
                return None

            if entry.is_expired:
                self._remove_entry(key)
                self._misses += 1
                return None

            # Update access stats
            entry.last_accessed = datetime.now()
            entry.access_count += 1
            self._hits += 1
            self._tokens_saved += entry.token_estimate

            return entry.content

    def xǁContextCacheǁget__mutmut_3(self, key: str) -> Optional[str]:
        """
        Get cached content by key.

        Args:
            key: Cache key

        Returns:
            Cached content or None if not found/expired
        """
        with self._lock:
            entry = self._cache.get(key)

            if entry is not None:
                self._misses += 1
                return None

            if entry.is_expired:
                self._remove_entry(key)
                self._misses += 1
                return None

            # Update access stats
            entry.last_accessed = datetime.now()
            entry.access_count += 1
            self._hits += 1
            self._tokens_saved += entry.token_estimate

            return entry.content

    def xǁContextCacheǁget__mutmut_4(self, key: str) -> Optional[str]:
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
                self._misses = 1
                return None

            if entry.is_expired:
                self._remove_entry(key)
                self._misses += 1
                return None

            # Update access stats
            entry.last_accessed = datetime.now()
            entry.access_count += 1
            self._hits += 1
            self._tokens_saved += entry.token_estimate

            return entry.content

    def xǁContextCacheǁget__mutmut_5(self, key: str) -> Optional[str]:
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
                self._misses -= 1
                return None

            if entry.is_expired:
                self._remove_entry(key)
                self._misses += 1
                return None

            # Update access stats
            entry.last_accessed = datetime.now()
            entry.access_count += 1
            self._hits += 1
            self._tokens_saved += entry.token_estimate

            return entry.content

    def xǁContextCacheǁget__mutmut_6(self, key: str) -> Optional[str]:
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
                self._misses += 2
                return None

            if entry.is_expired:
                self._remove_entry(key)
                self._misses += 1
                return None

            # Update access stats
            entry.last_accessed = datetime.now()
            entry.access_count += 1
            self._hits += 1
            self._tokens_saved += entry.token_estimate

            return entry.content

    def xǁContextCacheǁget__mutmut_7(self, key: str) -> Optional[str]:
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
                self._remove_entry(None)
                self._misses += 1
                return None

            # Update access stats
            entry.last_accessed = datetime.now()
            entry.access_count += 1
            self._hits += 1
            self._tokens_saved += entry.token_estimate

            return entry.content

    def xǁContextCacheǁget__mutmut_8(self, key: str) -> Optional[str]:
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
                self._misses = 1
                return None

            # Update access stats
            entry.last_accessed = datetime.now()
            entry.access_count += 1
            self._hits += 1
            self._tokens_saved += entry.token_estimate

            return entry.content

    def xǁContextCacheǁget__mutmut_9(self, key: str) -> Optional[str]:
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
                self._misses -= 1
                return None

            # Update access stats
            entry.last_accessed = datetime.now()
            entry.access_count += 1
            self._hits += 1
            self._tokens_saved += entry.token_estimate

            return entry.content

    def xǁContextCacheǁget__mutmut_10(self, key: str) -> Optional[str]:
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
                self._misses += 2
                return None

            # Update access stats
            entry.last_accessed = datetime.now()
            entry.access_count += 1
            self._hits += 1
            self._tokens_saved += entry.token_estimate

            return entry.content

    def xǁContextCacheǁget__mutmut_11(self, key: str) -> Optional[str]:
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
            entry.last_accessed = None
            entry.access_count += 1
            self._hits += 1
            self._tokens_saved += entry.token_estimate

            return entry.content

    def xǁContextCacheǁget__mutmut_12(self, key: str) -> Optional[str]:
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
            entry.last_accessed = datetime.now()
            entry.access_count = 1
            self._hits += 1
            self._tokens_saved += entry.token_estimate

            return entry.content

    def xǁContextCacheǁget__mutmut_13(self, key: str) -> Optional[str]:
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
            entry.last_accessed = datetime.now()
            entry.access_count -= 1
            self._hits += 1
            self._tokens_saved += entry.token_estimate

            return entry.content

    def xǁContextCacheǁget__mutmut_14(self, key: str) -> Optional[str]:
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
            entry.last_accessed = datetime.now()
            entry.access_count += 2
            self._hits += 1
            self._tokens_saved += entry.token_estimate

            return entry.content

    def xǁContextCacheǁget__mutmut_15(self, key: str) -> Optional[str]:
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
            entry.last_accessed = datetime.now()
            entry.access_count += 1
            self._hits = 1
            self._tokens_saved += entry.token_estimate

            return entry.content

    def xǁContextCacheǁget__mutmut_16(self, key: str) -> Optional[str]:
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
            entry.last_accessed = datetime.now()
            entry.access_count += 1
            self._hits -= 1
            self._tokens_saved += entry.token_estimate

            return entry.content

    def xǁContextCacheǁget__mutmut_17(self, key: str) -> Optional[str]:
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
            entry.last_accessed = datetime.now()
            entry.access_count += 1
            self._hits += 2
            self._tokens_saved += entry.token_estimate

            return entry.content

    def xǁContextCacheǁget__mutmut_18(self, key: str) -> Optional[str]:
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
            entry.last_accessed = datetime.now()
            entry.access_count += 1
            self._hits += 1
            self._tokens_saved = entry.token_estimate

            return entry.content

    def xǁContextCacheǁget__mutmut_19(self, key: str) -> Optional[str]:
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
            entry.last_accessed = datetime.now()
            entry.access_count += 1
            self._hits += 1
            self._tokens_saved -= entry.token_estimate

            return entry.content
    
    xǁContextCacheǁget__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextCacheǁget__mutmut_1': xǁContextCacheǁget__mutmut_1, 
        'xǁContextCacheǁget__mutmut_2': xǁContextCacheǁget__mutmut_2, 
        'xǁContextCacheǁget__mutmut_3': xǁContextCacheǁget__mutmut_3, 
        'xǁContextCacheǁget__mutmut_4': xǁContextCacheǁget__mutmut_4, 
        'xǁContextCacheǁget__mutmut_5': xǁContextCacheǁget__mutmut_5, 
        'xǁContextCacheǁget__mutmut_6': xǁContextCacheǁget__mutmut_6, 
        'xǁContextCacheǁget__mutmut_7': xǁContextCacheǁget__mutmut_7, 
        'xǁContextCacheǁget__mutmut_8': xǁContextCacheǁget__mutmut_8, 
        'xǁContextCacheǁget__mutmut_9': xǁContextCacheǁget__mutmut_9, 
        'xǁContextCacheǁget__mutmut_10': xǁContextCacheǁget__mutmut_10, 
        'xǁContextCacheǁget__mutmut_11': xǁContextCacheǁget__mutmut_11, 
        'xǁContextCacheǁget__mutmut_12': xǁContextCacheǁget__mutmut_12, 
        'xǁContextCacheǁget__mutmut_13': xǁContextCacheǁget__mutmut_13, 
        'xǁContextCacheǁget__mutmut_14': xǁContextCacheǁget__mutmut_14, 
        'xǁContextCacheǁget__mutmut_15': xǁContextCacheǁget__mutmut_15, 
        'xǁContextCacheǁget__mutmut_16': xǁContextCacheǁget__mutmut_16, 
        'xǁContextCacheǁget__mutmut_17': xǁContextCacheǁget__mutmut_17, 
        'xǁContextCacheǁget__mutmut_18': xǁContextCacheǁget__mutmut_18, 
        'xǁContextCacheǁget__mutmut_19': xǁContextCacheǁget__mutmut_19
    }
    
    def get(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextCacheǁget__mutmut_orig"), object.__getattribute__(self, "xǁContextCacheǁget__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get.__signature__ = _mutmut_signature(xǁContextCacheǁget__mutmut_orig)
    xǁContextCacheǁget__mutmut_orig.__name__ = 'xǁContextCacheǁget'

    def xǁContextCacheǁset__mutmut_orig(
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
                existing.last_accessed = datetime.now()
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

    def xǁContextCacheǁset__mutmut_1(
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
            content_hash = None
            token_count = len(content) // 4 + 1

            # Check if already cached with same content
            existing = self._cache.get(key)
            if existing and existing.content_hash == content_hash:
                existing.last_accessed = datetime.now()
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

    def xǁContextCacheǁset__mutmut_2(
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
            content_hash = hashlib.sha256(None).hexdigest()
            token_count = len(content) // 4 + 1

            # Check if already cached with same content
            existing = self._cache.get(key)
            if existing and existing.content_hash == content_hash:
                existing.last_accessed = datetime.now()
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

    def xǁContextCacheǁset__mutmut_3(
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
            token_count = None

            # Check if already cached with same content
            existing = self._cache.get(key)
            if existing and existing.content_hash == content_hash:
                existing.last_accessed = datetime.now()
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

    def xǁContextCacheǁset__mutmut_4(
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
            token_count = len(content) // 4 - 1

            # Check if already cached with same content
            existing = self._cache.get(key)
            if existing and existing.content_hash == content_hash:
                existing.last_accessed = datetime.now()
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

    def xǁContextCacheǁset__mutmut_5(
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
            token_count = len(content) / 4 + 1

            # Check if already cached with same content
            existing = self._cache.get(key)
            if existing and existing.content_hash == content_hash:
                existing.last_accessed = datetime.now()
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

    def xǁContextCacheǁset__mutmut_6(
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
            token_count = len(content) // 5 + 1

            # Check if already cached with same content
            existing = self._cache.get(key)
            if existing and existing.content_hash == content_hash:
                existing.last_accessed = datetime.now()
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

    def xǁContextCacheǁset__mutmut_7(
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
            token_count = len(content) // 4 + 2

            # Check if already cached with same content
            existing = self._cache.get(key)
            if existing and existing.content_hash == content_hash:
                existing.last_accessed = datetime.now()
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

    def xǁContextCacheǁset__mutmut_8(
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
            existing = None
            if existing and existing.content_hash == content_hash:
                existing.last_accessed = datetime.now()
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

    def xǁContextCacheǁset__mutmut_9(
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
            existing = self._cache.get(None)
            if existing and existing.content_hash == content_hash:
                existing.last_accessed = datetime.now()
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

    def xǁContextCacheǁset__mutmut_10(
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
            if existing or existing.content_hash == content_hash:
                existing.last_accessed = datetime.now()
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

    def xǁContextCacheǁset__mutmut_11(
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
            if existing and existing.content_hash != content_hash:
                existing.last_accessed = datetime.now()
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

    def xǁContextCacheǁset__mutmut_12(
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
                existing.last_accessed = None
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

    def xǁContextCacheǁset__mutmut_13(
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
                existing.last_accessed = datetime.now()
                existing.access_count = 1
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

    def xǁContextCacheǁset__mutmut_14(
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
                existing.last_accessed = datetime.now()
                existing.access_count -= 1
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

    def xǁContextCacheǁset__mutmut_15(
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
                existing.last_accessed = datetime.now()
                existing.access_count += 2
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

    def xǁContextCacheǁset__mutmut_16(
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
                existing.last_accessed = datetime.now()
                existing.access_count += 1
                return False

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

    def xǁContextCacheǁset__mutmut_17(
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
                existing.last_accessed = datetime.now()
                existing.access_count += 1
                return True

            # Remove existing entry if different content
            if existing:
                self._remove_entry(None)

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

    def xǁContextCacheǁset__mutmut_18(
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
                existing.last_accessed = datetime.now()
                existing.access_count += 1
                return True

            # Remove existing entry if different content
            if existing:
                self._remove_entry(key)

            # Ensure capacity
            self._ensure_capacity(None)

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

    def xǁContextCacheǁset__mutmut_19(
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
                existing.last_accessed = datetime.now()
                existing.access_count += 1
                return True

            # Remove existing entry if different content
            if existing:
                self._remove_entry(key)

            # Ensure capacity
            self._ensure_capacity(token_count)

            # Check limits after eviction
            if len(self._cache) > self.max_entries:
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

    def xǁContextCacheǁset__mutmut_20(
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
                existing.last_accessed = datetime.now()
                existing.access_count += 1
                return True

            # Remove existing entry if different content
            if existing:
                self._remove_entry(key)

            # Ensure capacity
            self._ensure_capacity(token_count)

            # Check limits after eviction
            if len(self._cache) >= self.max_entries:
                return True
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

    def xǁContextCacheǁset__mutmut_21(
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
                existing.last_accessed = datetime.now()
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
            if self._total_tokens - token_count > self.max_tokens:
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

    def xǁContextCacheǁset__mutmut_22(
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
                existing.last_accessed = datetime.now()
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
            if self._total_tokens + token_count >= self.max_tokens:
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

    def xǁContextCacheǁset__mutmut_23(
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
                existing.last_accessed = datetime.now()
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
                return True

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

    def xǁContextCacheǁset__mutmut_24(
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
                existing.last_accessed = datetime.now()
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
            entry = None

            self._cache[key] = entry
            self._total_tokens += token_count

            # Persist if enabled
            if self.persist_path:
                self._save_to_disk()

            return True

    def xǁContextCacheǁset__mutmut_25(
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
                existing.last_accessed = datetime.now()
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
                key=None,
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

    def xǁContextCacheǁset__mutmut_26(
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
                existing.last_accessed = datetime.now()
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
                content=None,
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

    def xǁContextCacheǁset__mutmut_27(
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
                existing.last_accessed = datetime.now()
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
                content_hash=None,
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

    def xǁContextCacheǁset__mutmut_28(
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
                existing.last_accessed = datetime.now()
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
                ttl_seconds=None,
                tags=tags or [],
                metadata=metadata or {},
            )

            self._cache[key] = entry
            self._total_tokens += token_count

            # Persist if enabled
            if self.persist_path:
                self._save_to_disk()

            return True

    def xǁContextCacheǁset__mutmut_29(
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
                existing.last_accessed = datetime.now()
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
                tags=None,
                metadata=metadata or {},
            )

            self._cache[key] = entry
            self._total_tokens += token_count

            # Persist if enabled
            if self.persist_path:
                self._save_to_disk()

            return True

    def xǁContextCacheǁset__mutmut_30(
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
                existing.last_accessed = datetime.now()
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
                metadata=None,
            )

            self._cache[key] = entry
            self._total_tokens += token_count

            # Persist if enabled
            if self.persist_path:
                self._save_to_disk()

            return True

    def xǁContextCacheǁset__mutmut_31(
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
                existing.last_accessed = datetime.now()
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

    def xǁContextCacheǁset__mutmut_32(
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
                existing.last_accessed = datetime.now()
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

    def xǁContextCacheǁset__mutmut_33(
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
                existing.last_accessed = datetime.now()
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

    def xǁContextCacheǁset__mutmut_34(
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
                existing.last_accessed = datetime.now()
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
                tags=tags or [],
                metadata=metadata or {},
            )

            self._cache[key] = entry
            self._total_tokens += token_count

            # Persist if enabled
            if self.persist_path:
                self._save_to_disk()

            return True

    def xǁContextCacheǁset__mutmut_35(
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
                existing.last_accessed = datetime.now()
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
                metadata=metadata or {},
            )

            self._cache[key] = entry
            self._total_tokens += token_count

            # Persist if enabled
            if self.persist_path:
                self._save_to_disk()

            return True

    def xǁContextCacheǁset__mutmut_36(
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
                existing.last_accessed = datetime.now()
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
                )

            self._cache[key] = entry
            self._total_tokens += token_count

            # Persist if enabled
            if self.persist_path:
                self._save_to_disk()

            return True

    def xǁContextCacheǁset__mutmut_37(
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
                existing.last_accessed = datetime.now()
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
                ttl_seconds=ttl if ttl is None else self.default_ttl,
                tags=tags or [],
                metadata=metadata or {},
            )

            self._cache[key] = entry
            self._total_tokens += token_count

            # Persist if enabled
            if self.persist_path:
                self._save_to_disk()

            return True

    def xǁContextCacheǁset__mutmut_38(
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
                existing.last_accessed = datetime.now()
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
                tags=tags and [],
                metadata=metadata or {},
            )

            self._cache[key] = entry
            self._total_tokens += token_count

            # Persist if enabled
            if self.persist_path:
                self._save_to_disk()

            return True

    def xǁContextCacheǁset__mutmut_39(
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
                existing.last_accessed = datetime.now()
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
                metadata=metadata and {},
            )

            self._cache[key] = entry
            self._total_tokens += token_count

            # Persist if enabled
            if self.persist_path:
                self._save_to_disk()

            return True

    def xǁContextCacheǁset__mutmut_40(
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
                existing.last_accessed = datetime.now()
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

            self._cache[key] = None
            self._total_tokens += token_count

            # Persist if enabled
            if self.persist_path:
                self._save_to_disk()

            return True

    def xǁContextCacheǁset__mutmut_41(
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
                existing.last_accessed = datetime.now()
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
            self._total_tokens = token_count

            # Persist if enabled
            if self.persist_path:
                self._save_to_disk()

            return True

    def xǁContextCacheǁset__mutmut_42(
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
                existing.last_accessed = datetime.now()
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
            self._total_tokens -= token_count

            # Persist if enabled
            if self.persist_path:
                self._save_to_disk()

            return True

    def xǁContextCacheǁset__mutmut_43(
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
                existing.last_accessed = datetime.now()
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

            return False
    
    xǁContextCacheǁset__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextCacheǁset__mutmut_1': xǁContextCacheǁset__mutmut_1, 
        'xǁContextCacheǁset__mutmut_2': xǁContextCacheǁset__mutmut_2, 
        'xǁContextCacheǁset__mutmut_3': xǁContextCacheǁset__mutmut_3, 
        'xǁContextCacheǁset__mutmut_4': xǁContextCacheǁset__mutmut_4, 
        'xǁContextCacheǁset__mutmut_5': xǁContextCacheǁset__mutmut_5, 
        'xǁContextCacheǁset__mutmut_6': xǁContextCacheǁset__mutmut_6, 
        'xǁContextCacheǁset__mutmut_7': xǁContextCacheǁset__mutmut_7, 
        'xǁContextCacheǁset__mutmut_8': xǁContextCacheǁset__mutmut_8, 
        'xǁContextCacheǁset__mutmut_9': xǁContextCacheǁset__mutmut_9, 
        'xǁContextCacheǁset__mutmut_10': xǁContextCacheǁset__mutmut_10, 
        'xǁContextCacheǁset__mutmut_11': xǁContextCacheǁset__mutmut_11, 
        'xǁContextCacheǁset__mutmut_12': xǁContextCacheǁset__mutmut_12, 
        'xǁContextCacheǁset__mutmut_13': xǁContextCacheǁset__mutmut_13, 
        'xǁContextCacheǁset__mutmut_14': xǁContextCacheǁset__mutmut_14, 
        'xǁContextCacheǁset__mutmut_15': xǁContextCacheǁset__mutmut_15, 
        'xǁContextCacheǁset__mutmut_16': xǁContextCacheǁset__mutmut_16, 
        'xǁContextCacheǁset__mutmut_17': xǁContextCacheǁset__mutmut_17, 
        'xǁContextCacheǁset__mutmut_18': xǁContextCacheǁset__mutmut_18, 
        'xǁContextCacheǁset__mutmut_19': xǁContextCacheǁset__mutmut_19, 
        'xǁContextCacheǁset__mutmut_20': xǁContextCacheǁset__mutmut_20, 
        'xǁContextCacheǁset__mutmut_21': xǁContextCacheǁset__mutmut_21, 
        'xǁContextCacheǁset__mutmut_22': xǁContextCacheǁset__mutmut_22, 
        'xǁContextCacheǁset__mutmut_23': xǁContextCacheǁset__mutmut_23, 
        'xǁContextCacheǁset__mutmut_24': xǁContextCacheǁset__mutmut_24, 
        'xǁContextCacheǁset__mutmut_25': xǁContextCacheǁset__mutmut_25, 
        'xǁContextCacheǁset__mutmut_26': xǁContextCacheǁset__mutmut_26, 
        'xǁContextCacheǁset__mutmut_27': xǁContextCacheǁset__mutmut_27, 
        'xǁContextCacheǁset__mutmut_28': xǁContextCacheǁset__mutmut_28, 
        'xǁContextCacheǁset__mutmut_29': xǁContextCacheǁset__mutmut_29, 
        'xǁContextCacheǁset__mutmut_30': xǁContextCacheǁset__mutmut_30, 
        'xǁContextCacheǁset__mutmut_31': xǁContextCacheǁset__mutmut_31, 
        'xǁContextCacheǁset__mutmut_32': xǁContextCacheǁset__mutmut_32, 
        'xǁContextCacheǁset__mutmut_33': xǁContextCacheǁset__mutmut_33, 
        'xǁContextCacheǁset__mutmut_34': xǁContextCacheǁset__mutmut_34, 
        'xǁContextCacheǁset__mutmut_35': xǁContextCacheǁset__mutmut_35, 
        'xǁContextCacheǁset__mutmut_36': xǁContextCacheǁset__mutmut_36, 
        'xǁContextCacheǁset__mutmut_37': xǁContextCacheǁset__mutmut_37, 
        'xǁContextCacheǁset__mutmut_38': xǁContextCacheǁset__mutmut_38, 
        'xǁContextCacheǁset__mutmut_39': xǁContextCacheǁset__mutmut_39, 
        'xǁContextCacheǁset__mutmut_40': xǁContextCacheǁset__mutmut_40, 
        'xǁContextCacheǁset__mutmut_41': xǁContextCacheǁset__mutmut_41, 
        'xǁContextCacheǁset__mutmut_42': xǁContextCacheǁset__mutmut_42, 
        'xǁContextCacheǁset__mutmut_43': xǁContextCacheǁset__mutmut_43
    }
    
    def set(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextCacheǁset__mutmut_orig"), object.__getattribute__(self, "xǁContextCacheǁset__mutmut_mutants"), args, kwargs, self)
        return result 
    
    set.__signature__ = _mutmut_signature(xǁContextCacheǁset__mutmut_orig)
    xǁContextCacheǁset__mutmut_orig.__name__ = 'xǁContextCacheǁset'

    def xǁContextCacheǁget_or_set__mutmut_orig(
        self,
        key: str,
        content_fn: callable,
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

    def xǁContextCacheǁget_or_set__mutmut_1(
        self,
        key: str,
        content_fn: callable,
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
        cached = None
        if cached is not None:
            return cached

        content = content_fn()
        self.set(key, content, ttl=ttl, tags=tags)
        return content

    def xǁContextCacheǁget_or_set__mutmut_2(
        self,
        key: str,
        content_fn: callable,
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
        cached = self.get(None)
        if cached is not None:
            return cached

        content = content_fn()
        self.set(key, content, ttl=ttl, tags=tags)
        return content

    def xǁContextCacheǁget_or_set__mutmut_3(
        self,
        key: str,
        content_fn: callable,
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
        if cached is None:
            return cached

        content = content_fn()
        self.set(key, content, ttl=ttl, tags=tags)
        return content

    def xǁContextCacheǁget_or_set__mutmut_4(
        self,
        key: str,
        content_fn: callable,
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

        content = None
        self.set(key, content, ttl=ttl, tags=tags)
        return content

    def xǁContextCacheǁget_or_set__mutmut_5(
        self,
        key: str,
        content_fn: callable,
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
        self.set(None, content, ttl=ttl, tags=tags)
        return content

    def xǁContextCacheǁget_or_set__mutmut_6(
        self,
        key: str,
        content_fn: callable,
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
        self.set(key, None, ttl=ttl, tags=tags)
        return content

    def xǁContextCacheǁget_or_set__mutmut_7(
        self,
        key: str,
        content_fn: callable,
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
        self.set(key, content, ttl=None, tags=tags)
        return content

    def xǁContextCacheǁget_or_set__mutmut_8(
        self,
        key: str,
        content_fn: callable,
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
        self.set(key, content, ttl=ttl, tags=None)
        return content

    def xǁContextCacheǁget_or_set__mutmut_9(
        self,
        key: str,
        content_fn: callable,
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
        self.set(content, ttl=ttl, tags=tags)
        return content

    def xǁContextCacheǁget_or_set__mutmut_10(
        self,
        key: str,
        content_fn: callable,
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
        self.set(key, ttl=ttl, tags=tags)
        return content

    def xǁContextCacheǁget_or_set__mutmut_11(
        self,
        key: str,
        content_fn: callable,
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
        self.set(key, content, tags=tags)
        return content

    def xǁContextCacheǁget_or_set__mutmut_12(
        self,
        key: str,
        content_fn: callable,
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
        self.set(key, content, ttl=ttl, )
        return content
    
    xǁContextCacheǁget_or_set__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextCacheǁget_or_set__mutmut_1': xǁContextCacheǁget_or_set__mutmut_1, 
        'xǁContextCacheǁget_or_set__mutmut_2': xǁContextCacheǁget_or_set__mutmut_2, 
        'xǁContextCacheǁget_or_set__mutmut_3': xǁContextCacheǁget_or_set__mutmut_3, 
        'xǁContextCacheǁget_or_set__mutmut_4': xǁContextCacheǁget_or_set__mutmut_4, 
        'xǁContextCacheǁget_or_set__mutmut_5': xǁContextCacheǁget_or_set__mutmut_5, 
        'xǁContextCacheǁget_or_set__mutmut_6': xǁContextCacheǁget_or_set__mutmut_6, 
        'xǁContextCacheǁget_or_set__mutmut_7': xǁContextCacheǁget_or_set__mutmut_7, 
        'xǁContextCacheǁget_or_set__mutmut_8': xǁContextCacheǁget_or_set__mutmut_8, 
        'xǁContextCacheǁget_or_set__mutmut_9': xǁContextCacheǁget_or_set__mutmut_9, 
        'xǁContextCacheǁget_or_set__mutmut_10': xǁContextCacheǁget_or_set__mutmut_10, 
        'xǁContextCacheǁget_or_set__mutmut_11': xǁContextCacheǁget_or_set__mutmut_11, 
        'xǁContextCacheǁget_or_set__mutmut_12': xǁContextCacheǁget_or_set__mutmut_12
    }
    
    def get_or_set(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextCacheǁget_or_set__mutmut_orig"), object.__getattribute__(self, "xǁContextCacheǁget_or_set__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_or_set.__signature__ = _mutmut_signature(xǁContextCacheǁget_or_set__mutmut_orig)
    xǁContextCacheǁget_or_set__mutmut_orig.__name__ = 'xǁContextCacheǁget_or_set'

    def xǁContextCacheǁinvalidate__mutmut_orig(self, key: str) -> bool:
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

    def xǁContextCacheǁinvalidate__mutmut_1(self, key: str) -> bool:
        """
        Invalidate (remove) cached entry.

        Args:
            key: Cache key

        Returns:
            True if removed, False if not found
        """
        with self._lock:
            if key not in self._cache:
                self._remove_entry(key)
                if self.persist_path:
                    self._save_to_disk()
                return True
            return False

    def xǁContextCacheǁinvalidate__mutmut_2(self, key: str) -> bool:
        """
        Invalidate (remove) cached entry.

        Args:
            key: Cache key

        Returns:
            True if removed, False if not found
        """
        with self._lock:
            if key in self._cache:
                self._remove_entry(None)
                if self.persist_path:
                    self._save_to_disk()
                return True
            return False

    def xǁContextCacheǁinvalidate__mutmut_3(self, key: str) -> bool:
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
                return False
            return False

    def xǁContextCacheǁinvalidate__mutmut_4(self, key: str) -> bool:
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
            return True
    
    xǁContextCacheǁinvalidate__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextCacheǁinvalidate__mutmut_1': xǁContextCacheǁinvalidate__mutmut_1, 
        'xǁContextCacheǁinvalidate__mutmut_2': xǁContextCacheǁinvalidate__mutmut_2, 
        'xǁContextCacheǁinvalidate__mutmut_3': xǁContextCacheǁinvalidate__mutmut_3, 
        'xǁContextCacheǁinvalidate__mutmut_4': xǁContextCacheǁinvalidate__mutmut_4
    }
    
    def invalidate(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextCacheǁinvalidate__mutmut_orig"), object.__getattribute__(self, "xǁContextCacheǁinvalidate__mutmut_mutants"), args, kwargs, self)
        return result 
    
    invalidate.__signature__ = _mutmut_signature(xǁContextCacheǁinvalidate__mutmut_orig)
    xǁContextCacheǁinvalidate__mutmut_orig.__name__ = 'xǁContextCacheǁinvalidate'

    def xǁContextCacheǁinvalidate_by_tag__mutmut_orig(self, tag: str) -> int:
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

    def xǁContextCacheǁinvalidate_by_tag__mutmut_1(self, tag: str) -> int:
        """
        Invalidate all entries with given tag.

        Args:
            tag: Tag to match

        Returns:
            Number of entries invalidated
        """
        with self._lock:
            keys_to_remove = None
            for key in keys_to_remove:
                self._remove_entry(key)

            if keys_to_remove and self.persist_path:
                self._save_to_disk()

            return len(keys_to_remove)

    def xǁContextCacheǁinvalidate_by_tag__mutmut_2(self, tag: str) -> int:
        """
        Invalidate all entries with given tag.

        Args:
            tag: Tag to match

        Returns:
            Number of entries invalidated
        """
        with self._lock:
            keys_to_remove = [key for key, entry in self._cache.items() if tag not in entry.tags]
            for key in keys_to_remove:
                self._remove_entry(key)

            if keys_to_remove and self.persist_path:
                self._save_to_disk()

            return len(keys_to_remove)

    def xǁContextCacheǁinvalidate_by_tag__mutmut_3(self, tag: str) -> int:
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
                self._remove_entry(None)

            if keys_to_remove and self.persist_path:
                self._save_to_disk()

            return len(keys_to_remove)

    def xǁContextCacheǁinvalidate_by_tag__mutmut_4(self, tag: str) -> int:
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

            if keys_to_remove or self.persist_path:
                self._save_to_disk()

            return len(keys_to_remove)
    
    xǁContextCacheǁinvalidate_by_tag__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextCacheǁinvalidate_by_tag__mutmut_1': xǁContextCacheǁinvalidate_by_tag__mutmut_1, 
        'xǁContextCacheǁinvalidate_by_tag__mutmut_2': xǁContextCacheǁinvalidate_by_tag__mutmut_2, 
        'xǁContextCacheǁinvalidate_by_tag__mutmut_3': xǁContextCacheǁinvalidate_by_tag__mutmut_3, 
        'xǁContextCacheǁinvalidate_by_tag__mutmut_4': xǁContextCacheǁinvalidate_by_tag__mutmut_4
    }
    
    def invalidate_by_tag(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextCacheǁinvalidate_by_tag__mutmut_orig"), object.__getattribute__(self, "xǁContextCacheǁinvalidate_by_tag__mutmut_mutants"), args, kwargs, self)
        return result 
    
    invalidate_by_tag.__signature__ = _mutmut_signature(xǁContextCacheǁinvalidate_by_tag__mutmut_orig)
    xǁContextCacheǁinvalidate_by_tag__mutmut_orig.__name__ = 'xǁContextCacheǁinvalidate_by_tag'

    def xǁContextCacheǁclear__mutmut_orig(self):
        """Clear all cached entries."""
        with self._lock:
            self._cache.clear()
            self._total_tokens = 0
            if self.persist_path:
                self._save_to_disk()

    def xǁContextCacheǁclear__mutmut_1(self):
        """Clear all cached entries."""
        with self._lock:
            self._cache.clear()
            self._total_tokens = None
            if self.persist_path:
                self._save_to_disk()

    def xǁContextCacheǁclear__mutmut_2(self):
        """Clear all cached entries."""
        with self._lock:
            self._cache.clear()
            self._total_tokens = 1
            if self.persist_path:
                self._save_to_disk()
    
    xǁContextCacheǁclear__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextCacheǁclear__mutmut_1': xǁContextCacheǁclear__mutmut_1, 
        'xǁContextCacheǁclear__mutmut_2': xǁContextCacheǁclear__mutmut_2
    }
    
    def clear(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextCacheǁclear__mutmut_orig"), object.__getattribute__(self, "xǁContextCacheǁclear__mutmut_mutants"), args, kwargs, self)
        return result 
    
    clear.__signature__ = _mutmut_signature(xǁContextCacheǁclear__mutmut_orig)
    xǁContextCacheǁclear__mutmut_orig.__name__ = 'xǁContextCacheǁclear'

    def xǁContextCacheǁcleanup_expired__mutmut_orig(self) -> int:
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

    def xǁContextCacheǁcleanup_expired__mutmut_1(self) -> int:
        """
        Remove expired entries.

        Returns:
            Number of entries removed
        """
        with self._lock:
            expired = None
            for key in expired:
                self._remove_entry(key)

            if expired and self.persist_path:
                self._save_to_disk()

            return len(expired)

    def xǁContextCacheǁcleanup_expired__mutmut_2(self) -> int:
        """
        Remove expired entries.

        Returns:
            Number of entries removed
        """
        with self._lock:
            expired = [key for key, entry in self._cache.items() if entry.is_expired]
            for key in expired:
                self._remove_entry(None)

            if expired and self.persist_path:
                self._save_to_disk()

            return len(expired)

    def xǁContextCacheǁcleanup_expired__mutmut_3(self) -> int:
        """
        Remove expired entries.

        Returns:
            Number of entries removed
        """
        with self._lock:
            expired = [key for key, entry in self._cache.items() if entry.is_expired]
            for key in expired:
                self._remove_entry(key)

            if expired or self.persist_path:
                self._save_to_disk()

            return len(expired)
    
    xǁContextCacheǁcleanup_expired__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextCacheǁcleanup_expired__mutmut_1': xǁContextCacheǁcleanup_expired__mutmut_1, 
        'xǁContextCacheǁcleanup_expired__mutmut_2': xǁContextCacheǁcleanup_expired__mutmut_2, 
        'xǁContextCacheǁcleanup_expired__mutmut_3': xǁContextCacheǁcleanup_expired__mutmut_3
    }
    
    def cleanup_expired(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextCacheǁcleanup_expired__mutmut_orig"), object.__getattribute__(self, "xǁContextCacheǁcleanup_expired__mutmut_mutants"), args, kwargs, self)
        return result 
    
    cleanup_expired.__signature__ = _mutmut_signature(xǁContextCacheǁcleanup_expired__mutmut_orig)
    xǁContextCacheǁcleanup_expired__mutmut_orig.__name__ = 'xǁContextCacheǁcleanup_expired'

    def xǁContextCacheǁget_stats__mutmut_orig(self) -> CacheStats:
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

    def xǁContextCacheǁget_stats__mutmut_1(self) -> CacheStats:
        """Get cache statistics."""
        with self._lock:
            total_requests = None
            hit_rate = self._hits / total_requests if total_requests > 0 else 0.0

            return CacheStats(
                total_entries=len(self._cache),
                total_tokens=self._total_tokens,
                hit_count=self._hits,
                miss_count=self._misses,
                hit_rate=hit_rate,
                tokens_saved=self._tokens_saved,
            )

    def xǁContextCacheǁget_stats__mutmut_2(self) -> CacheStats:
        """Get cache statistics."""
        with self._lock:
            total_requests = self._hits - self._misses
            hit_rate = self._hits / total_requests if total_requests > 0 else 0.0

            return CacheStats(
                total_entries=len(self._cache),
                total_tokens=self._total_tokens,
                hit_count=self._hits,
                miss_count=self._misses,
                hit_rate=hit_rate,
                tokens_saved=self._tokens_saved,
            )

    def xǁContextCacheǁget_stats__mutmut_3(self) -> CacheStats:
        """Get cache statistics."""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = None

            return CacheStats(
                total_entries=len(self._cache),
                total_tokens=self._total_tokens,
                hit_count=self._hits,
                miss_count=self._misses,
                hit_rate=hit_rate,
                tokens_saved=self._tokens_saved,
            )

    def xǁContextCacheǁget_stats__mutmut_4(self) -> CacheStats:
        """Get cache statistics."""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = self._hits * total_requests if total_requests > 0 else 0.0

            return CacheStats(
                total_entries=len(self._cache),
                total_tokens=self._total_tokens,
                hit_count=self._hits,
                miss_count=self._misses,
                hit_rate=hit_rate,
                tokens_saved=self._tokens_saved,
            )

    def xǁContextCacheǁget_stats__mutmut_5(self) -> CacheStats:
        """Get cache statistics."""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests >= 0 else 0.0

            return CacheStats(
                total_entries=len(self._cache),
                total_tokens=self._total_tokens,
                hit_count=self._hits,
                miss_count=self._misses,
                hit_rate=hit_rate,
                tokens_saved=self._tokens_saved,
            )

    def xǁContextCacheǁget_stats__mutmut_6(self) -> CacheStats:
        """Get cache statistics."""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests > 1 else 0.0

            return CacheStats(
                total_entries=len(self._cache),
                total_tokens=self._total_tokens,
                hit_count=self._hits,
                miss_count=self._misses,
                hit_rate=hit_rate,
                tokens_saved=self._tokens_saved,
            )

    def xǁContextCacheǁget_stats__mutmut_7(self) -> CacheStats:
        """Get cache statistics."""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests > 0 else 1.0

            return CacheStats(
                total_entries=len(self._cache),
                total_tokens=self._total_tokens,
                hit_count=self._hits,
                miss_count=self._misses,
                hit_rate=hit_rate,
                tokens_saved=self._tokens_saved,
            )

    def xǁContextCacheǁget_stats__mutmut_8(self) -> CacheStats:
        """Get cache statistics."""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests > 0 else 0.0

            return CacheStats(
                total_entries=None,
                total_tokens=self._total_tokens,
                hit_count=self._hits,
                miss_count=self._misses,
                hit_rate=hit_rate,
                tokens_saved=self._tokens_saved,
            )

    def xǁContextCacheǁget_stats__mutmut_9(self) -> CacheStats:
        """Get cache statistics."""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests > 0 else 0.0

            return CacheStats(
                total_entries=len(self._cache),
                total_tokens=None,
                hit_count=self._hits,
                miss_count=self._misses,
                hit_rate=hit_rate,
                tokens_saved=self._tokens_saved,
            )

    def xǁContextCacheǁget_stats__mutmut_10(self) -> CacheStats:
        """Get cache statistics."""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests > 0 else 0.0

            return CacheStats(
                total_entries=len(self._cache),
                total_tokens=self._total_tokens,
                hit_count=None,
                miss_count=self._misses,
                hit_rate=hit_rate,
                tokens_saved=self._tokens_saved,
            )

    def xǁContextCacheǁget_stats__mutmut_11(self) -> CacheStats:
        """Get cache statistics."""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests > 0 else 0.0

            return CacheStats(
                total_entries=len(self._cache),
                total_tokens=self._total_tokens,
                hit_count=self._hits,
                miss_count=None,
                hit_rate=hit_rate,
                tokens_saved=self._tokens_saved,
            )

    def xǁContextCacheǁget_stats__mutmut_12(self) -> CacheStats:
        """Get cache statistics."""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests > 0 else 0.0

            return CacheStats(
                total_entries=len(self._cache),
                total_tokens=self._total_tokens,
                hit_count=self._hits,
                miss_count=self._misses,
                hit_rate=None,
                tokens_saved=self._tokens_saved,
            )

    def xǁContextCacheǁget_stats__mutmut_13(self) -> CacheStats:
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
                tokens_saved=None,
            )

    def xǁContextCacheǁget_stats__mutmut_14(self) -> CacheStats:
        """Get cache statistics."""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests > 0 else 0.0

            return CacheStats(
                total_tokens=self._total_tokens,
                hit_count=self._hits,
                miss_count=self._misses,
                hit_rate=hit_rate,
                tokens_saved=self._tokens_saved,
            )

    def xǁContextCacheǁget_stats__mutmut_15(self) -> CacheStats:
        """Get cache statistics."""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests > 0 else 0.0

            return CacheStats(
                total_entries=len(self._cache),
                hit_count=self._hits,
                miss_count=self._misses,
                hit_rate=hit_rate,
                tokens_saved=self._tokens_saved,
            )

    def xǁContextCacheǁget_stats__mutmut_16(self) -> CacheStats:
        """Get cache statistics."""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests > 0 else 0.0

            return CacheStats(
                total_entries=len(self._cache),
                total_tokens=self._total_tokens,
                miss_count=self._misses,
                hit_rate=hit_rate,
                tokens_saved=self._tokens_saved,
            )

    def xǁContextCacheǁget_stats__mutmut_17(self) -> CacheStats:
        """Get cache statistics."""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests > 0 else 0.0

            return CacheStats(
                total_entries=len(self._cache),
                total_tokens=self._total_tokens,
                hit_count=self._hits,
                hit_rate=hit_rate,
                tokens_saved=self._tokens_saved,
            )

    def xǁContextCacheǁget_stats__mutmut_18(self) -> CacheStats:
        """Get cache statistics."""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests > 0 else 0.0

            return CacheStats(
                total_entries=len(self._cache),
                total_tokens=self._total_tokens,
                hit_count=self._hits,
                miss_count=self._misses,
                tokens_saved=self._tokens_saved,
            )

    def xǁContextCacheǁget_stats__mutmut_19(self) -> CacheStats:
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
                )
    
    xǁContextCacheǁget_stats__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextCacheǁget_stats__mutmut_1': xǁContextCacheǁget_stats__mutmut_1, 
        'xǁContextCacheǁget_stats__mutmut_2': xǁContextCacheǁget_stats__mutmut_2, 
        'xǁContextCacheǁget_stats__mutmut_3': xǁContextCacheǁget_stats__mutmut_3, 
        'xǁContextCacheǁget_stats__mutmut_4': xǁContextCacheǁget_stats__mutmut_4, 
        'xǁContextCacheǁget_stats__mutmut_5': xǁContextCacheǁget_stats__mutmut_5, 
        'xǁContextCacheǁget_stats__mutmut_6': xǁContextCacheǁget_stats__mutmut_6, 
        'xǁContextCacheǁget_stats__mutmut_7': xǁContextCacheǁget_stats__mutmut_7, 
        'xǁContextCacheǁget_stats__mutmut_8': xǁContextCacheǁget_stats__mutmut_8, 
        'xǁContextCacheǁget_stats__mutmut_9': xǁContextCacheǁget_stats__mutmut_9, 
        'xǁContextCacheǁget_stats__mutmut_10': xǁContextCacheǁget_stats__mutmut_10, 
        'xǁContextCacheǁget_stats__mutmut_11': xǁContextCacheǁget_stats__mutmut_11, 
        'xǁContextCacheǁget_stats__mutmut_12': xǁContextCacheǁget_stats__mutmut_12, 
        'xǁContextCacheǁget_stats__mutmut_13': xǁContextCacheǁget_stats__mutmut_13, 
        'xǁContextCacheǁget_stats__mutmut_14': xǁContextCacheǁget_stats__mutmut_14, 
        'xǁContextCacheǁget_stats__mutmut_15': xǁContextCacheǁget_stats__mutmut_15, 
        'xǁContextCacheǁget_stats__mutmut_16': xǁContextCacheǁget_stats__mutmut_16, 
        'xǁContextCacheǁget_stats__mutmut_17': xǁContextCacheǁget_stats__mutmut_17, 
        'xǁContextCacheǁget_stats__mutmut_18': xǁContextCacheǁget_stats__mutmut_18, 
        'xǁContextCacheǁget_stats__mutmut_19': xǁContextCacheǁget_stats__mutmut_19
    }
    
    def get_stats(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextCacheǁget_stats__mutmut_orig"), object.__getattribute__(self, "xǁContextCacheǁget_stats__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_stats.__signature__ = _mutmut_signature(xǁContextCacheǁget_stats__mutmut_orig)
    xǁContextCacheǁget_stats__mutmut_orig.__name__ = 'xǁContextCacheǁget_stats'

    def xǁContextCacheǁget_all_keys__mutmut_orig(self) -> list[str]:
        """Get all cache keys."""
        with self._lock:
            return list(self._cache.keys())

    def xǁContextCacheǁget_all_keys__mutmut_1(self) -> list[str]:
        """Get all cache keys."""
        with self._lock:
            return list(None)
    
    xǁContextCacheǁget_all_keys__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextCacheǁget_all_keys__mutmut_1': xǁContextCacheǁget_all_keys__mutmut_1
    }
    
    def get_all_keys(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextCacheǁget_all_keys__mutmut_orig"), object.__getattribute__(self, "xǁContextCacheǁget_all_keys__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_all_keys.__signature__ = _mutmut_signature(xǁContextCacheǁget_all_keys__mutmut_orig)
    xǁContextCacheǁget_all_keys__mutmut_orig.__name__ = 'xǁContextCacheǁget_all_keys'

    def xǁContextCacheǁget_by_tag__mutmut_orig(self, tag: str) -> list[CacheEntry]:
        """Get all entries with given tag."""
        with self._lock:
            return [entry for entry in self._cache.values() if tag in entry.tags]

    def xǁContextCacheǁget_by_tag__mutmut_1(self, tag: str) -> list[CacheEntry]:
        """Get all entries with given tag."""
        with self._lock:
            return [entry for entry in self._cache.values() if tag not in entry.tags]
    
    xǁContextCacheǁget_by_tag__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextCacheǁget_by_tag__mutmut_1': xǁContextCacheǁget_by_tag__mutmut_1
    }
    
    def get_by_tag(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextCacheǁget_by_tag__mutmut_orig"), object.__getattribute__(self, "xǁContextCacheǁget_by_tag__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_by_tag.__signature__ = _mutmut_signature(xǁContextCacheǁget_by_tag__mutmut_orig)
    xǁContextCacheǁget_by_tag__mutmut_orig.__name__ = 'xǁContextCacheǁget_by_tag'

    def xǁContextCacheǁ_remove_entry__mutmut_orig(self, key: str):
        """Remove entry and update token count."""
        entry = self._cache.pop(key, None)
        if entry:
            self._total_tokens -= entry.token_estimate

    def xǁContextCacheǁ_remove_entry__mutmut_1(self, key: str):
        """Remove entry and update token count."""
        entry = None
        if entry:
            self._total_tokens -= entry.token_estimate

    def xǁContextCacheǁ_remove_entry__mutmut_2(self, key: str):
        """Remove entry and update token count."""
        entry = self._cache.pop(None, None)
        if entry:
            self._total_tokens -= entry.token_estimate

    def xǁContextCacheǁ_remove_entry__mutmut_3(self, key: str):
        """Remove entry and update token count."""
        entry = self._cache.pop(None)
        if entry:
            self._total_tokens -= entry.token_estimate

    def xǁContextCacheǁ_remove_entry__mutmut_4(self, key: str):
        """Remove entry and update token count."""
        entry = self._cache.pop(key, )
        if entry:
            self._total_tokens -= entry.token_estimate

    def xǁContextCacheǁ_remove_entry__mutmut_5(self, key: str):
        """Remove entry and update token count."""
        entry = self._cache.pop(key, None)
        if entry:
            self._total_tokens = entry.token_estimate

    def xǁContextCacheǁ_remove_entry__mutmut_6(self, key: str):
        """Remove entry and update token count."""
        entry = self._cache.pop(key, None)
        if entry:
            self._total_tokens += entry.token_estimate
    
    xǁContextCacheǁ_remove_entry__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextCacheǁ_remove_entry__mutmut_1': xǁContextCacheǁ_remove_entry__mutmut_1, 
        'xǁContextCacheǁ_remove_entry__mutmut_2': xǁContextCacheǁ_remove_entry__mutmut_2, 
        'xǁContextCacheǁ_remove_entry__mutmut_3': xǁContextCacheǁ_remove_entry__mutmut_3, 
        'xǁContextCacheǁ_remove_entry__mutmut_4': xǁContextCacheǁ_remove_entry__mutmut_4, 
        'xǁContextCacheǁ_remove_entry__mutmut_5': xǁContextCacheǁ_remove_entry__mutmut_5, 
        'xǁContextCacheǁ_remove_entry__mutmut_6': xǁContextCacheǁ_remove_entry__mutmut_6
    }
    
    def _remove_entry(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextCacheǁ_remove_entry__mutmut_orig"), object.__getattribute__(self, "xǁContextCacheǁ_remove_entry__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _remove_entry.__signature__ = _mutmut_signature(xǁContextCacheǁ_remove_entry__mutmut_orig)
    xǁContextCacheǁ_remove_entry__mutmut_orig.__name__ = 'xǁContextCacheǁ_remove_entry'

    def xǁContextCacheǁ_ensure_capacity__mutmut_orig(self, needed_tokens: int):
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

    def xǁContextCacheǁ_ensure_capacity__mutmut_1(self, needed_tokens: int):
        """Ensure capacity using LRU eviction."""
        # Evict expired first
        self.cleanup_expired()

        # Evict LRU if still over capacity
        while (
            len(self._cache) >= self.max_entries and self._total_tokens + needed_tokens > self.max_tokens
        ):
            if not self._cache:
                break

            # Find LRU entry
            lru_key = min(self._cache.keys(), key=lambda k: self._cache[k].last_accessed)
            self._remove_entry(lru_key)

    def xǁContextCacheǁ_ensure_capacity__mutmut_2(self, needed_tokens: int):
        """Ensure capacity using LRU eviction."""
        # Evict expired first
        self.cleanup_expired()

        # Evict LRU if still over capacity
        while (
            len(self._cache) > self.max_entries
            or self._total_tokens + needed_tokens > self.max_tokens
        ):
            if not self._cache:
                break

            # Find LRU entry
            lru_key = min(self._cache.keys(), key=lambda k: self._cache[k].last_accessed)
            self._remove_entry(lru_key)

    def xǁContextCacheǁ_ensure_capacity__mutmut_3(self, needed_tokens: int):
        """Ensure capacity using LRU eviction."""
        # Evict expired first
        self.cleanup_expired()

        # Evict LRU if still over capacity
        while (
            len(self._cache) >= self.max_entries
            or self._total_tokens - needed_tokens > self.max_tokens
        ):
            if not self._cache:
                break

            # Find LRU entry
            lru_key = min(self._cache.keys(), key=lambda k: self._cache[k].last_accessed)
            self._remove_entry(lru_key)

    def xǁContextCacheǁ_ensure_capacity__mutmut_4(self, needed_tokens: int):
        """Ensure capacity using LRU eviction."""
        # Evict expired first
        self.cleanup_expired()

        # Evict LRU if still over capacity
        while (
            len(self._cache) >= self.max_entries
            or self._total_tokens + needed_tokens >= self.max_tokens
        ):
            if not self._cache:
                break

            # Find LRU entry
            lru_key = min(self._cache.keys(), key=lambda k: self._cache[k].last_accessed)
            self._remove_entry(lru_key)

    def xǁContextCacheǁ_ensure_capacity__mutmut_5(self, needed_tokens: int):
        """Ensure capacity using LRU eviction."""
        # Evict expired first
        self.cleanup_expired()

        # Evict LRU if still over capacity
        while (
            len(self._cache) >= self.max_entries
            or self._total_tokens + needed_tokens > self.max_tokens
        ):
            if self._cache:
                break

            # Find LRU entry
            lru_key = min(self._cache.keys(), key=lambda k: self._cache[k].last_accessed)
            self._remove_entry(lru_key)

    def xǁContextCacheǁ_ensure_capacity__mutmut_6(self, needed_tokens: int):
        """Ensure capacity using LRU eviction."""
        # Evict expired first
        self.cleanup_expired()

        # Evict LRU if still over capacity
        while (
            len(self._cache) >= self.max_entries
            or self._total_tokens + needed_tokens > self.max_tokens
        ):
            if not self._cache:
                return

            # Find LRU entry
            lru_key = min(self._cache.keys(), key=lambda k: self._cache[k].last_accessed)
            self._remove_entry(lru_key)

    def xǁContextCacheǁ_ensure_capacity__mutmut_7(self, needed_tokens: int):
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
            lru_key = None
            self._remove_entry(lru_key)

    def xǁContextCacheǁ_ensure_capacity__mutmut_8(self, needed_tokens: int):
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
            lru_key = min(None, key=lambda k: self._cache[k].last_accessed)
            self._remove_entry(lru_key)

    def xǁContextCacheǁ_ensure_capacity__mutmut_9(self, needed_tokens: int):
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
            lru_key = min(self._cache.keys(), key=None)
            self._remove_entry(lru_key)

    def xǁContextCacheǁ_ensure_capacity__mutmut_10(self, needed_tokens: int):
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
            lru_key = min(key=lambda k: self._cache[k].last_accessed)
            self._remove_entry(lru_key)

    def xǁContextCacheǁ_ensure_capacity__mutmut_11(self, needed_tokens: int):
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
            lru_key = min(self._cache.keys(), )
            self._remove_entry(lru_key)

    def xǁContextCacheǁ_ensure_capacity__mutmut_12(self, needed_tokens: int):
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
            lru_key = min(self._cache.keys(), key=lambda k: None)
            self._remove_entry(lru_key)

    def xǁContextCacheǁ_ensure_capacity__mutmut_13(self, needed_tokens: int):
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
            self._remove_entry(None)
    
    xǁContextCacheǁ_ensure_capacity__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextCacheǁ_ensure_capacity__mutmut_1': xǁContextCacheǁ_ensure_capacity__mutmut_1, 
        'xǁContextCacheǁ_ensure_capacity__mutmut_2': xǁContextCacheǁ_ensure_capacity__mutmut_2, 
        'xǁContextCacheǁ_ensure_capacity__mutmut_3': xǁContextCacheǁ_ensure_capacity__mutmut_3, 
        'xǁContextCacheǁ_ensure_capacity__mutmut_4': xǁContextCacheǁ_ensure_capacity__mutmut_4, 
        'xǁContextCacheǁ_ensure_capacity__mutmut_5': xǁContextCacheǁ_ensure_capacity__mutmut_5, 
        'xǁContextCacheǁ_ensure_capacity__mutmut_6': xǁContextCacheǁ_ensure_capacity__mutmut_6, 
        'xǁContextCacheǁ_ensure_capacity__mutmut_7': xǁContextCacheǁ_ensure_capacity__mutmut_7, 
        'xǁContextCacheǁ_ensure_capacity__mutmut_8': xǁContextCacheǁ_ensure_capacity__mutmut_8, 
        'xǁContextCacheǁ_ensure_capacity__mutmut_9': xǁContextCacheǁ_ensure_capacity__mutmut_9, 
        'xǁContextCacheǁ_ensure_capacity__mutmut_10': xǁContextCacheǁ_ensure_capacity__mutmut_10, 
        'xǁContextCacheǁ_ensure_capacity__mutmut_11': xǁContextCacheǁ_ensure_capacity__mutmut_11, 
        'xǁContextCacheǁ_ensure_capacity__mutmut_12': xǁContextCacheǁ_ensure_capacity__mutmut_12, 
        'xǁContextCacheǁ_ensure_capacity__mutmut_13': xǁContextCacheǁ_ensure_capacity__mutmut_13
    }
    
    def _ensure_capacity(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextCacheǁ_ensure_capacity__mutmut_orig"), object.__getattribute__(self, "xǁContextCacheǁ_ensure_capacity__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _ensure_capacity.__signature__ = _mutmut_signature(xǁContextCacheǁ_ensure_capacity__mutmut_orig)
    xǁContextCacheǁ_ensure_capacity__mutmut_orig.__name__ = 'xǁContextCacheǁ_ensure_capacity'

    def xǁContextCacheǁ_save_to_disk__mutmut_orig(self):
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

    def xǁContextCacheǁ_save_to_disk__mutmut_1(self):
        """Save cache to disk."""
        if self.persist_path:
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

    def xǁContextCacheǁ_save_to_disk__mutmut_2(self):
        """Save cache to disk."""
        if not self.persist_path:
            return

        data = None

        Path(self.persist_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.persist_path, "w") as f:
            json.dump(data, f)

    def xǁContextCacheǁ_save_to_disk__mutmut_3(self):
        """Save cache to disk."""
        if not self.persist_path:
            return

        data = {
            key: {
                "XXcontentXX": entry.content,
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

    def xǁContextCacheǁ_save_to_disk__mutmut_4(self):
        """Save cache to disk."""
        if not self.persist_path:
            return

        data = {
            key: {
                "CONTENT": entry.content,
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

    def xǁContextCacheǁ_save_to_disk__mutmut_5(self):
        """Save cache to disk."""
        if not self.persist_path:
            return

        data = {
            key: {
                "content": entry.content,
                "XXcontent_hashXX": entry.content_hash,
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

    def xǁContextCacheǁ_save_to_disk__mutmut_6(self):
        """Save cache to disk."""
        if not self.persist_path:
            return

        data = {
            key: {
                "content": entry.content,
                "CONTENT_HASH": entry.content_hash,
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

    def xǁContextCacheǁ_save_to_disk__mutmut_7(self):
        """Save cache to disk."""
        if not self.persist_path:
            return

        data = {
            key: {
                "content": entry.content,
                "content_hash": entry.content_hash,
                "XXcreated_atXX": entry.created_at.isoformat(),
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

    def xǁContextCacheǁ_save_to_disk__mutmut_8(self):
        """Save cache to disk."""
        if not self.persist_path:
            return

        data = {
            key: {
                "content": entry.content,
                "content_hash": entry.content_hash,
                "CREATED_AT": entry.created_at.isoformat(),
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

    def xǁContextCacheǁ_save_to_disk__mutmut_9(self):
        """Save cache to disk."""
        if not self.persist_path:
            return

        data = {
            key: {
                "content": entry.content,
                "content_hash": entry.content_hash,
                "created_at": entry.created_at.isoformat(),
                "XXlast_accessedXX": entry.last_accessed.isoformat(),
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

    def xǁContextCacheǁ_save_to_disk__mutmut_10(self):
        """Save cache to disk."""
        if not self.persist_path:
            return

        data = {
            key: {
                "content": entry.content,
                "content_hash": entry.content_hash,
                "created_at": entry.created_at.isoformat(),
                "LAST_ACCESSED": entry.last_accessed.isoformat(),
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

    def xǁContextCacheǁ_save_to_disk__mutmut_11(self):
        """Save cache to disk."""
        if not self.persist_path:
            return

        data = {
            key: {
                "content": entry.content,
                "content_hash": entry.content_hash,
                "created_at": entry.created_at.isoformat(),
                "last_accessed": entry.last_accessed.isoformat(),
                "XXaccess_countXX": entry.access_count,
                "ttl_seconds": entry.ttl_seconds,
                "tags": entry.tags,
                "metadata": entry.metadata,
            }
            for key, entry in self._cache.items()
        }

        Path(self.persist_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.persist_path, "w") as f:
            json.dump(data, f)

    def xǁContextCacheǁ_save_to_disk__mutmut_12(self):
        """Save cache to disk."""
        if not self.persist_path:
            return

        data = {
            key: {
                "content": entry.content,
                "content_hash": entry.content_hash,
                "created_at": entry.created_at.isoformat(),
                "last_accessed": entry.last_accessed.isoformat(),
                "ACCESS_COUNT": entry.access_count,
                "ttl_seconds": entry.ttl_seconds,
                "tags": entry.tags,
                "metadata": entry.metadata,
            }
            for key, entry in self._cache.items()
        }

        Path(self.persist_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.persist_path, "w") as f:
            json.dump(data, f)

    def xǁContextCacheǁ_save_to_disk__mutmut_13(self):
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
                "XXttl_secondsXX": entry.ttl_seconds,
                "tags": entry.tags,
                "metadata": entry.metadata,
            }
            for key, entry in self._cache.items()
        }

        Path(self.persist_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.persist_path, "w") as f:
            json.dump(data, f)

    def xǁContextCacheǁ_save_to_disk__mutmut_14(self):
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
                "TTL_SECONDS": entry.ttl_seconds,
                "tags": entry.tags,
                "metadata": entry.metadata,
            }
            for key, entry in self._cache.items()
        }

        Path(self.persist_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.persist_path, "w") as f:
            json.dump(data, f)

    def xǁContextCacheǁ_save_to_disk__mutmut_15(self):
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
                "XXtagsXX": entry.tags,
                "metadata": entry.metadata,
            }
            for key, entry in self._cache.items()
        }

        Path(self.persist_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.persist_path, "w") as f:
            json.dump(data, f)

    def xǁContextCacheǁ_save_to_disk__mutmut_16(self):
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
                "TAGS": entry.tags,
                "metadata": entry.metadata,
            }
            for key, entry in self._cache.items()
        }

        Path(self.persist_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.persist_path, "w") as f:
            json.dump(data, f)

    def xǁContextCacheǁ_save_to_disk__mutmut_17(self):
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
                "XXmetadataXX": entry.metadata,
            }
            for key, entry in self._cache.items()
        }

        Path(self.persist_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.persist_path, "w") as f:
            json.dump(data, f)

    def xǁContextCacheǁ_save_to_disk__mutmut_18(self):
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
                "METADATA": entry.metadata,
            }
            for key, entry in self._cache.items()
        }

        Path(self.persist_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.persist_path, "w") as f:
            json.dump(data, f)

    def xǁContextCacheǁ_save_to_disk__mutmut_19(self):
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

        Path(self.persist_path).parent.mkdir(parents=None, exist_ok=True)
        with open(self.persist_path, "w") as f:
            json.dump(data, f)

    def xǁContextCacheǁ_save_to_disk__mutmut_20(self):
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

        Path(self.persist_path).parent.mkdir(parents=True, exist_ok=None)
        with open(self.persist_path, "w") as f:
            json.dump(data, f)

    def xǁContextCacheǁ_save_to_disk__mutmut_21(self):
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

        Path(self.persist_path).parent.mkdir(exist_ok=True)
        with open(self.persist_path, "w") as f:
            json.dump(data, f)

    def xǁContextCacheǁ_save_to_disk__mutmut_22(self):
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

        Path(self.persist_path).parent.mkdir(parents=True, )
        with open(self.persist_path, "w") as f:
            json.dump(data, f)

    def xǁContextCacheǁ_save_to_disk__mutmut_23(self):
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

        Path(None).parent.mkdir(parents=True, exist_ok=True)
        with open(self.persist_path, "w") as f:
            json.dump(data, f)

    def xǁContextCacheǁ_save_to_disk__mutmut_24(self):
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

        Path(self.persist_path).parent.mkdir(parents=False, exist_ok=True)
        with open(self.persist_path, "w") as f:
            json.dump(data, f)

    def xǁContextCacheǁ_save_to_disk__mutmut_25(self):
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

        Path(self.persist_path).parent.mkdir(parents=True, exist_ok=False)
        with open(self.persist_path, "w") as f:
            json.dump(data, f)

    def xǁContextCacheǁ_save_to_disk__mutmut_26(self):
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
        with open(None, "w") as f:
            json.dump(data, f)

    def xǁContextCacheǁ_save_to_disk__mutmut_27(self):
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
        with open(self.persist_path, None) as f:
            json.dump(data, f)

    def xǁContextCacheǁ_save_to_disk__mutmut_28(self):
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
        with open("w") as f:
            json.dump(data, f)

    def xǁContextCacheǁ_save_to_disk__mutmut_29(self):
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
        with open(self.persist_path, ) as f:
            json.dump(data, f)

    def xǁContextCacheǁ_save_to_disk__mutmut_30(self):
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
        with open(self.persist_path, "XXwXX") as f:
            json.dump(data, f)

    def xǁContextCacheǁ_save_to_disk__mutmut_31(self):
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
        with open(self.persist_path, "W") as f:
            json.dump(data, f)

    def xǁContextCacheǁ_save_to_disk__mutmut_32(self):
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
            json.dump(None, f)

    def xǁContextCacheǁ_save_to_disk__mutmut_33(self):
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
            json.dump(data, None)

    def xǁContextCacheǁ_save_to_disk__mutmut_34(self):
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
            json.dump(f)

    def xǁContextCacheǁ_save_to_disk__mutmut_35(self):
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
            json.dump(data, )
    
    xǁContextCacheǁ_save_to_disk__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextCacheǁ_save_to_disk__mutmut_1': xǁContextCacheǁ_save_to_disk__mutmut_1, 
        'xǁContextCacheǁ_save_to_disk__mutmut_2': xǁContextCacheǁ_save_to_disk__mutmut_2, 
        'xǁContextCacheǁ_save_to_disk__mutmut_3': xǁContextCacheǁ_save_to_disk__mutmut_3, 
        'xǁContextCacheǁ_save_to_disk__mutmut_4': xǁContextCacheǁ_save_to_disk__mutmut_4, 
        'xǁContextCacheǁ_save_to_disk__mutmut_5': xǁContextCacheǁ_save_to_disk__mutmut_5, 
        'xǁContextCacheǁ_save_to_disk__mutmut_6': xǁContextCacheǁ_save_to_disk__mutmut_6, 
        'xǁContextCacheǁ_save_to_disk__mutmut_7': xǁContextCacheǁ_save_to_disk__mutmut_7, 
        'xǁContextCacheǁ_save_to_disk__mutmut_8': xǁContextCacheǁ_save_to_disk__mutmut_8, 
        'xǁContextCacheǁ_save_to_disk__mutmut_9': xǁContextCacheǁ_save_to_disk__mutmut_9, 
        'xǁContextCacheǁ_save_to_disk__mutmut_10': xǁContextCacheǁ_save_to_disk__mutmut_10, 
        'xǁContextCacheǁ_save_to_disk__mutmut_11': xǁContextCacheǁ_save_to_disk__mutmut_11, 
        'xǁContextCacheǁ_save_to_disk__mutmut_12': xǁContextCacheǁ_save_to_disk__mutmut_12, 
        'xǁContextCacheǁ_save_to_disk__mutmut_13': xǁContextCacheǁ_save_to_disk__mutmut_13, 
        'xǁContextCacheǁ_save_to_disk__mutmut_14': xǁContextCacheǁ_save_to_disk__mutmut_14, 
        'xǁContextCacheǁ_save_to_disk__mutmut_15': xǁContextCacheǁ_save_to_disk__mutmut_15, 
        'xǁContextCacheǁ_save_to_disk__mutmut_16': xǁContextCacheǁ_save_to_disk__mutmut_16, 
        'xǁContextCacheǁ_save_to_disk__mutmut_17': xǁContextCacheǁ_save_to_disk__mutmut_17, 
        'xǁContextCacheǁ_save_to_disk__mutmut_18': xǁContextCacheǁ_save_to_disk__mutmut_18, 
        'xǁContextCacheǁ_save_to_disk__mutmut_19': xǁContextCacheǁ_save_to_disk__mutmut_19, 
        'xǁContextCacheǁ_save_to_disk__mutmut_20': xǁContextCacheǁ_save_to_disk__mutmut_20, 
        'xǁContextCacheǁ_save_to_disk__mutmut_21': xǁContextCacheǁ_save_to_disk__mutmut_21, 
        'xǁContextCacheǁ_save_to_disk__mutmut_22': xǁContextCacheǁ_save_to_disk__mutmut_22, 
        'xǁContextCacheǁ_save_to_disk__mutmut_23': xǁContextCacheǁ_save_to_disk__mutmut_23, 
        'xǁContextCacheǁ_save_to_disk__mutmut_24': xǁContextCacheǁ_save_to_disk__mutmut_24, 
        'xǁContextCacheǁ_save_to_disk__mutmut_25': xǁContextCacheǁ_save_to_disk__mutmut_25, 
        'xǁContextCacheǁ_save_to_disk__mutmut_26': xǁContextCacheǁ_save_to_disk__mutmut_26, 
        'xǁContextCacheǁ_save_to_disk__mutmut_27': xǁContextCacheǁ_save_to_disk__mutmut_27, 
        'xǁContextCacheǁ_save_to_disk__mutmut_28': xǁContextCacheǁ_save_to_disk__mutmut_28, 
        'xǁContextCacheǁ_save_to_disk__mutmut_29': xǁContextCacheǁ_save_to_disk__mutmut_29, 
        'xǁContextCacheǁ_save_to_disk__mutmut_30': xǁContextCacheǁ_save_to_disk__mutmut_30, 
        'xǁContextCacheǁ_save_to_disk__mutmut_31': xǁContextCacheǁ_save_to_disk__mutmut_31, 
        'xǁContextCacheǁ_save_to_disk__mutmut_32': xǁContextCacheǁ_save_to_disk__mutmut_32, 
        'xǁContextCacheǁ_save_to_disk__mutmut_33': xǁContextCacheǁ_save_to_disk__mutmut_33, 
        'xǁContextCacheǁ_save_to_disk__mutmut_34': xǁContextCacheǁ_save_to_disk__mutmut_34, 
        'xǁContextCacheǁ_save_to_disk__mutmut_35': xǁContextCacheǁ_save_to_disk__mutmut_35
    }
    
    def _save_to_disk(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextCacheǁ_save_to_disk__mutmut_orig"), object.__getattribute__(self, "xǁContextCacheǁ_save_to_disk__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _save_to_disk.__signature__ = _mutmut_signature(xǁContextCacheǁ_save_to_disk__mutmut_orig)
    xǁContextCacheǁ_save_to_disk__mutmut_orig.__name__ = 'xǁContextCacheǁ_save_to_disk'

    def xǁContextCacheǁ_load_from_disk__mutmut_orig(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
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

    def xǁContextCacheǁ_load_from_disk__mutmut_1(self):
        """Load cache from disk."""
        if not self.persist_path and not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
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

    def xǁContextCacheǁ_load_from_disk__mutmut_2(self):
        """Load cache from disk."""
        if self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
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

    def xǁContextCacheǁ_load_from_disk__mutmut_3(self):
        """Load cache from disk."""
        if not self.persist_path or os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
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

    def xǁContextCacheǁ_load_from_disk__mutmut_4(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(None):
            return

        try:
            with open(self.persist_path, "r") as f:
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

    def xǁContextCacheǁ_load_from_disk__mutmut_5(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(None, "r") as f:
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

    def xǁContextCacheǁ_load_from_disk__mutmut_6(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, None) as f:
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

    def xǁContextCacheǁ_load_from_disk__mutmut_7(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open("r") as f:
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

    def xǁContextCacheǁ_load_from_disk__mutmut_8(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, ) as f:
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

    def xǁContextCacheǁ_load_from_disk__mutmut_9(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "XXrXX") as f:
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

    def xǁContextCacheǁ_load_from_disk__mutmut_10(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "R") as f:
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

    def xǁContextCacheǁ_load_from_disk__mutmut_11(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
                data = None

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

    def xǁContextCacheǁ_load_from_disk__mutmut_12(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
                data = json.load(None)

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

    def xǁContextCacheǁ_load_from_disk__mutmut_13(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
                data = json.load(f)

            for key, entry_data in data.items():
                entry = None

                # Skip expired entries
                if not entry.is_expired:
                    self._cache[key] = entry
                    self._total_tokens += entry.token_estimate

        except (json.JSONDecodeError, KeyError, ValueError):
            # Corrupted cache file, start fresh
            self._cache.clear()
            self._total_tokens = 0

    def xǁContextCacheǁ_load_from_disk__mutmut_14(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
                data = json.load(f)

            for key, entry_data in data.items():
                entry = CacheEntry(
                    key=None,
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

    def xǁContextCacheǁ_load_from_disk__mutmut_15(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
                data = json.load(f)

            for key, entry_data in data.items():
                entry = CacheEntry(
                    key=key,
                    content=None,
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

    def xǁContextCacheǁ_load_from_disk__mutmut_16(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
                data = json.load(f)

            for key, entry_data in data.items():
                entry = CacheEntry(
                    key=key,
                    content=entry_data["content"],
                    content_hash=None,
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

    def xǁContextCacheǁ_load_from_disk__mutmut_17(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
                data = json.load(f)

            for key, entry_data in data.items():
                entry = CacheEntry(
                    key=key,
                    content=entry_data["content"],
                    content_hash=entry_data["content_hash"],
                    created_at=None,
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

    def xǁContextCacheǁ_load_from_disk__mutmut_18(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
                data = json.load(f)

            for key, entry_data in data.items():
                entry = CacheEntry(
                    key=key,
                    content=entry_data["content"],
                    content_hash=entry_data["content_hash"],
                    created_at=datetime.fromisoformat(entry_data["created_at"]),
                    last_accessed=None,
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

    def xǁContextCacheǁ_load_from_disk__mutmut_19(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
                data = json.load(f)

            for key, entry_data in data.items():
                entry = CacheEntry(
                    key=key,
                    content=entry_data["content"],
                    content_hash=entry_data["content_hash"],
                    created_at=datetime.fromisoformat(entry_data["created_at"]),
                    last_accessed=datetime.fromisoformat(entry_data["last_accessed"]),
                    access_count=None,
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

    def xǁContextCacheǁ_load_from_disk__mutmut_20(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
                data = json.load(f)

            for key, entry_data in data.items():
                entry = CacheEntry(
                    key=key,
                    content=entry_data["content"],
                    content_hash=entry_data["content_hash"],
                    created_at=datetime.fromisoformat(entry_data["created_at"]),
                    last_accessed=datetime.fromisoformat(entry_data["last_accessed"]),
                    access_count=entry_data["access_count"],
                    ttl_seconds=None,
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

    def xǁContextCacheǁ_load_from_disk__mutmut_21(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
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
                    tags=None,
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

    def xǁContextCacheǁ_load_from_disk__mutmut_22(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
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
                    metadata=None,
                )

                # Skip expired entries
                if not entry.is_expired:
                    self._cache[key] = entry
                    self._total_tokens += entry.token_estimate

        except (json.JSONDecodeError, KeyError, ValueError):
            # Corrupted cache file, start fresh
            self._cache.clear()
            self._total_tokens = 0

    def xǁContextCacheǁ_load_from_disk__mutmut_23(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
                data = json.load(f)

            for key, entry_data in data.items():
                entry = CacheEntry(
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

    def xǁContextCacheǁ_load_from_disk__mutmut_24(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
                data = json.load(f)

            for key, entry_data in data.items():
                entry = CacheEntry(
                    key=key,
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

    def xǁContextCacheǁ_load_from_disk__mutmut_25(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
                data = json.load(f)

            for key, entry_data in data.items():
                entry = CacheEntry(
                    key=key,
                    content=entry_data["content"],
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

    def xǁContextCacheǁ_load_from_disk__mutmut_26(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
                data = json.load(f)

            for key, entry_data in data.items():
                entry = CacheEntry(
                    key=key,
                    content=entry_data["content"],
                    content_hash=entry_data["content_hash"],
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

    def xǁContextCacheǁ_load_from_disk__mutmut_27(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
                data = json.load(f)

            for key, entry_data in data.items():
                entry = CacheEntry(
                    key=key,
                    content=entry_data["content"],
                    content_hash=entry_data["content_hash"],
                    created_at=datetime.fromisoformat(entry_data["created_at"]),
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

    def xǁContextCacheǁ_load_from_disk__mutmut_28(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
                data = json.load(f)

            for key, entry_data in data.items():
                entry = CacheEntry(
                    key=key,
                    content=entry_data["content"],
                    content_hash=entry_data["content_hash"],
                    created_at=datetime.fromisoformat(entry_data["created_at"]),
                    last_accessed=datetime.fromisoformat(entry_data["last_accessed"]),
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

    def xǁContextCacheǁ_load_from_disk__mutmut_29(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
                data = json.load(f)

            for key, entry_data in data.items():
                entry = CacheEntry(
                    key=key,
                    content=entry_data["content"],
                    content_hash=entry_data["content_hash"],
                    created_at=datetime.fromisoformat(entry_data["created_at"]),
                    last_accessed=datetime.fromisoformat(entry_data["last_accessed"]),
                    access_count=entry_data["access_count"],
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

    def xǁContextCacheǁ_load_from_disk__mutmut_30(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
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

    def xǁContextCacheǁ_load_from_disk__mutmut_31(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
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
                    )

                # Skip expired entries
                if not entry.is_expired:
                    self._cache[key] = entry
                    self._total_tokens += entry.token_estimate

        except (json.JSONDecodeError, KeyError, ValueError):
            # Corrupted cache file, start fresh
            self._cache.clear()
            self._total_tokens = 0

    def xǁContextCacheǁ_load_from_disk__mutmut_32(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
                data = json.load(f)

            for key, entry_data in data.items():
                entry = CacheEntry(
                    key=key,
                    content=entry_data["XXcontentXX"],
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

    def xǁContextCacheǁ_load_from_disk__mutmut_33(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
                data = json.load(f)

            for key, entry_data in data.items():
                entry = CacheEntry(
                    key=key,
                    content=entry_data["CONTENT"],
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

    def xǁContextCacheǁ_load_from_disk__mutmut_34(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
                data = json.load(f)

            for key, entry_data in data.items():
                entry = CacheEntry(
                    key=key,
                    content=entry_data["content"],
                    content_hash=entry_data["XXcontent_hashXX"],
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

    def xǁContextCacheǁ_load_from_disk__mutmut_35(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
                data = json.load(f)

            for key, entry_data in data.items():
                entry = CacheEntry(
                    key=key,
                    content=entry_data["content"],
                    content_hash=entry_data["CONTENT_HASH"],
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

    def xǁContextCacheǁ_load_from_disk__mutmut_36(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
                data = json.load(f)

            for key, entry_data in data.items():
                entry = CacheEntry(
                    key=key,
                    content=entry_data["content"],
                    content_hash=entry_data["content_hash"],
                    created_at=datetime.fromisoformat(None),
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

    def xǁContextCacheǁ_load_from_disk__mutmut_37(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
                data = json.load(f)

            for key, entry_data in data.items():
                entry = CacheEntry(
                    key=key,
                    content=entry_data["content"],
                    content_hash=entry_data["content_hash"],
                    created_at=datetime.fromisoformat(entry_data["XXcreated_atXX"]),
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

    def xǁContextCacheǁ_load_from_disk__mutmut_38(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
                data = json.load(f)

            for key, entry_data in data.items():
                entry = CacheEntry(
                    key=key,
                    content=entry_data["content"],
                    content_hash=entry_data["content_hash"],
                    created_at=datetime.fromisoformat(entry_data["CREATED_AT"]),
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

    def xǁContextCacheǁ_load_from_disk__mutmut_39(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
                data = json.load(f)

            for key, entry_data in data.items():
                entry = CacheEntry(
                    key=key,
                    content=entry_data["content"],
                    content_hash=entry_data["content_hash"],
                    created_at=datetime.fromisoformat(entry_data["created_at"]),
                    last_accessed=datetime.fromisoformat(None),
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

    def xǁContextCacheǁ_load_from_disk__mutmut_40(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
                data = json.load(f)

            for key, entry_data in data.items():
                entry = CacheEntry(
                    key=key,
                    content=entry_data["content"],
                    content_hash=entry_data["content_hash"],
                    created_at=datetime.fromisoformat(entry_data["created_at"]),
                    last_accessed=datetime.fromisoformat(entry_data["XXlast_accessedXX"]),
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

    def xǁContextCacheǁ_load_from_disk__mutmut_41(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
                data = json.load(f)

            for key, entry_data in data.items():
                entry = CacheEntry(
                    key=key,
                    content=entry_data["content"],
                    content_hash=entry_data["content_hash"],
                    created_at=datetime.fromisoformat(entry_data["created_at"]),
                    last_accessed=datetime.fromisoformat(entry_data["LAST_ACCESSED"]),
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

    def xǁContextCacheǁ_load_from_disk__mutmut_42(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
                data = json.load(f)

            for key, entry_data in data.items():
                entry = CacheEntry(
                    key=key,
                    content=entry_data["content"],
                    content_hash=entry_data["content_hash"],
                    created_at=datetime.fromisoformat(entry_data["created_at"]),
                    last_accessed=datetime.fromisoformat(entry_data["last_accessed"]),
                    access_count=entry_data["XXaccess_countXX"],
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

    def xǁContextCacheǁ_load_from_disk__mutmut_43(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
                data = json.load(f)

            for key, entry_data in data.items():
                entry = CacheEntry(
                    key=key,
                    content=entry_data["content"],
                    content_hash=entry_data["content_hash"],
                    created_at=datetime.fromisoformat(entry_data["created_at"]),
                    last_accessed=datetime.fromisoformat(entry_data["last_accessed"]),
                    access_count=entry_data["ACCESS_COUNT"],
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

    def xǁContextCacheǁ_load_from_disk__mutmut_44(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
                data = json.load(f)

            for key, entry_data in data.items():
                entry = CacheEntry(
                    key=key,
                    content=entry_data["content"],
                    content_hash=entry_data["content_hash"],
                    created_at=datetime.fromisoformat(entry_data["created_at"]),
                    last_accessed=datetime.fromisoformat(entry_data["last_accessed"]),
                    access_count=entry_data["access_count"],
                    ttl_seconds=entry_data.get(None),
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

    def xǁContextCacheǁ_load_from_disk__mutmut_45(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
                data = json.load(f)

            for key, entry_data in data.items():
                entry = CacheEntry(
                    key=key,
                    content=entry_data["content"],
                    content_hash=entry_data["content_hash"],
                    created_at=datetime.fromisoformat(entry_data["created_at"]),
                    last_accessed=datetime.fromisoformat(entry_data["last_accessed"]),
                    access_count=entry_data["access_count"],
                    ttl_seconds=entry_data.get("XXttl_secondsXX"),
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

    def xǁContextCacheǁ_load_from_disk__mutmut_46(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
                data = json.load(f)

            for key, entry_data in data.items():
                entry = CacheEntry(
                    key=key,
                    content=entry_data["content"],
                    content_hash=entry_data["content_hash"],
                    created_at=datetime.fromisoformat(entry_data["created_at"]),
                    last_accessed=datetime.fromisoformat(entry_data["last_accessed"]),
                    access_count=entry_data["access_count"],
                    ttl_seconds=entry_data.get("TTL_SECONDS"),
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

    def xǁContextCacheǁ_load_from_disk__mutmut_47(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
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
                    tags=entry_data.get(None, []),
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

    def xǁContextCacheǁ_load_from_disk__mutmut_48(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
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
                    tags=entry_data.get("tags", None),
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

    def xǁContextCacheǁ_load_from_disk__mutmut_49(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
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
                    tags=entry_data.get([]),
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

    def xǁContextCacheǁ_load_from_disk__mutmut_50(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
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
                    tags=entry_data.get("tags", ),
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

    def xǁContextCacheǁ_load_from_disk__mutmut_51(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
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
                    tags=entry_data.get("XXtagsXX", []),
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

    def xǁContextCacheǁ_load_from_disk__mutmut_52(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
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
                    tags=entry_data.get("TAGS", []),
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

    def xǁContextCacheǁ_load_from_disk__mutmut_53(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
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
                    metadata=entry_data.get(None, {}),
                )

                # Skip expired entries
                if not entry.is_expired:
                    self._cache[key] = entry
                    self._total_tokens += entry.token_estimate

        except (json.JSONDecodeError, KeyError, ValueError):
            # Corrupted cache file, start fresh
            self._cache.clear()
            self._total_tokens = 0

    def xǁContextCacheǁ_load_from_disk__mutmut_54(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
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
                    metadata=entry_data.get("metadata", None),
                )

                # Skip expired entries
                if not entry.is_expired:
                    self._cache[key] = entry
                    self._total_tokens += entry.token_estimate

        except (json.JSONDecodeError, KeyError, ValueError):
            # Corrupted cache file, start fresh
            self._cache.clear()
            self._total_tokens = 0

    def xǁContextCacheǁ_load_from_disk__mutmut_55(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
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
                    metadata=entry_data.get({}),
                )

                # Skip expired entries
                if not entry.is_expired:
                    self._cache[key] = entry
                    self._total_tokens += entry.token_estimate

        except (json.JSONDecodeError, KeyError, ValueError):
            # Corrupted cache file, start fresh
            self._cache.clear()
            self._total_tokens = 0

    def xǁContextCacheǁ_load_from_disk__mutmut_56(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
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
                    metadata=entry_data.get("metadata", ),
                )

                # Skip expired entries
                if not entry.is_expired:
                    self._cache[key] = entry
                    self._total_tokens += entry.token_estimate

        except (json.JSONDecodeError, KeyError, ValueError):
            # Corrupted cache file, start fresh
            self._cache.clear()
            self._total_tokens = 0

    def xǁContextCacheǁ_load_from_disk__mutmut_57(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
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
                    metadata=entry_data.get("XXmetadataXX", {}),
                )

                # Skip expired entries
                if not entry.is_expired:
                    self._cache[key] = entry
                    self._total_tokens += entry.token_estimate

        except (json.JSONDecodeError, KeyError, ValueError):
            # Corrupted cache file, start fresh
            self._cache.clear()
            self._total_tokens = 0

    def xǁContextCacheǁ_load_from_disk__mutmut_58(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
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
                    metadata=entry_data.get("METADATA", {}),
                )

                # Skip expired entries
                if not entry.is_expired:
                    self._cache[key] = entry
                    self._total_tokens += entry.token_estimate

        except (json.JSONDecodeError, KeyError, ValueError):
            # Corrupted cache file, start fresh
            self._cache.clear()
            self._total_tokens = 0

    def xǁContextCacheǁ_load_from_disk__mutmut_59(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
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
                if entry.is_expired:
                    self._cache[key] = entry
                    self._total_tokens += entry.token_estimate

        except (json.JSONDecodeError, KeyError, ValueError):
            # Corrupted cache file, start fresh
            self._cache.clear()
            self._total_tokens = 0

    def xǁContextCacheǁ_load_from_disk__mutmut_60(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
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
                    self._cache[key] = None
                    self._total_tokens += entry.token_estimate

        except (json.JSONDecodeError, KeyError, ValueError):
            # Corrupted cache file, start fresh
            self._cache.clear()
            self._total_tokens = 0

    def xǁContextCacheǁ_load_from_disk__mutmut_61(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
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
                    self._total_tokens = entry.token_estimate

        except (json.JSONDecodeError, KeyError, ValueError):
            # Corrupted cache file, start fresh
            self._cache.clear()
            self._total_tokens = 0

    def xǁContextCacheǁ_load_from_disk__mutmut_62(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
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
                    self._total_tokens -= entry.token_estimate

        except (json.JSONDecodeError, KeyError, ValueError):
            # Corrupted cache file, start fresh
            self._cache.clear()
            self._total_tokens = 0

    def xǁContextCacheǁ_load_from_disk__mutmut_63(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
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
            self._total_tokens = None

    def xǁContextCacheǁ_load_from_disk__mutmut_64(self):
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return

        try:
            with open(self.persist_path, "r") as f:
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
            self._total_tokens = 1
    
    xǁContextCacheǁ_load_from_disk__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextCacheǁ_load_from_disk__mutmut_1': xǁContextCacheǁ_load_from_disk__mutmut_1, 
        'xǁContextCacheǁ_load_from_disk__mutmut_2': xǁContextCacheǁ_load_from_disk__mutmut_2, 
        'xǁContextCacheǁ_load_from_disk__mutmut_3': xǁContextCacheǁ_load_from_disk__mutmut_3, 
        'xǁContextCacheǁ_load_from_disk__mutmut_4': xǁContextCacheǁ_load_from_disk__mutmut_4, 
        'xǁContextCacheǁ_load_from_disk__mutmut_5': xǁContextCacheǁ_load_from_disk__mutmut_5, 
        'xǁContextCacheǁ_load_from_disk__mutmut_6': xǁContextCacheǁ_load_from_disk__mutmut_6, 
        'xǁContextCacheǁ_load_from_disk__mutmut_7': xǁContextCacheǁ_load_from_disk__mutmut_7, 
        'xǁContextCacheǁ_load_from_disk__mutmut_8': xǁContextCacheǁ_load_from_disk__mutmut_8, 
        'xǁContextCacheǁ_load_from_disk__mutmut_9': xǁContextCacheǁ_load_from_disk__mutmut_9, 
        'xǁContextCacheǁ_load_from_disk__mutmut_10': xǁContextCacheǁ_load_from_disk__mutmut_10, 
        'xǁContextCacheǁ_load_from_disk__mutmut_11': xǁContextCacheǁ_load_from_disk__mutmut_11, 
        'xǁContextCacheǁ_load_from_disk__mutmut_12': xǁContextCacheǁ_load_from_disk__mutmut_12, 
        'xǁContextCacheǁ_load_from_disk__mutmut_13': xǁContextCacheǁ_load_from_disk__mutmut_13, 
        'xǁContextCacheǁ_load_from_disk__mutmut_14': xǁContextCacheǁ_load_from_disk__mutmut_14, 
        'xǁContextCacheǁ_load_from_disk__mutmut_15': xǁContextCacheǁ_load_from_disk__mutmut_15, 
        'xǁContextCacheǁ_load_from_disk__mutmut_16': xǁContextCacheǁ_load_from_disk__mutmut_16, 
        'xǁContextCacheǁ_load_from_disk__mutmut_17': xǁContextCacheǁ_load_from_disk__mutmut_17, 
        'xǁContextCacheǁ_load_from_disk__mutmut_18': xǁContextCacheǁ_load_from_disk__mutmut_18, 
        'xǁContextCacheǁ_load_from_disk__mutmut_19': xǁContextCacheǁ_load_from_disk__mutmut_19, 
        'xǁContextCacheǁ_load_from_disk__mutmut_20': xǁContextCacheǁ_load_from_disk__mutmut_20, 
        'xǁContextCacheǁ_load_from_disk__mutmut_21': xǁContextCacheǁ_load_from_disk__mutmut_21, 
        'xǁContextCacheǁ_load_from_disk__mutmut_22': xǁContextCacheǁ_load_from_disk__mutmut_22, 
        'xǁContextCacheǁ_load_from_disk__mutmut_23': xǁContextCacheǁ_load_from_disk__mutmut_23, 
        'xǁContextCacheǁ_load_from_disk__mutmut_24': xǁContextCacheǁ_load_from_disk__mutmut_24, 
        'xǁContextCacheǁ_load_from_disk__mutmut_25': xǁContextCacheǁ_load_from_disk__mutmut_25, 
        'xǁContextCacheǁ_load_from_disk__mutmut_26': xǁContextCacheǁ_load_from_disk__mutmut_26, 
        'xǁContextCacheǁ_load_from_disk__mutmut_27': xǁContextCacheǁ_load_from_disk__mutmut_27, 
        'xǁContextCacheǁ_load_from_disk__mutmut_28': xǁContextCacheǁ_load_from_disk__mutmut_28, 
        'xǁContextCacheǁ_load_from_disk__mutmut_29': xǁContextCacheǁ_load_from_disk__mutmut_29, 
        'xǁContextCacheǁ_load_from_disk__mutmut_30': xǁContextCacheǁ_load_from_disk__mutmut_30, 
        'xǁContextCacheǁ_load_from_disk__mutmut_31': xǁContextCacheǁ_load_from_disk__mutmut_31, 
        'xǁContextCacheǁ_load_from_disk__mutmut_32': xǁContextCacheǁ_load_from_disk__mutmut_32, 
        'xǁContextCacheǁ_load_from_disk__mutmut_33': xǁContextCacheǁ_load_from_disk__mutmut_33, 
        'xǁContextCacheǁ_load_from_disk__mutmut_34': xǁContextCacheǁ_load_from_disk__mutmut_34, 
        'xǁContextCacheǁ_load_from_disk__mutmut_35': xǁContextCacheǁ_load_from_disk__mutmut_35, 
        'xǁContextCacheǁ_load_from_disk__mutmut_36': xǁContextCacheǁ_load_from_disk__mutmut_36, 
        'xǁContextCacheǁ_load_from_disk__mutmut_37': xǁContextCacheǁ_load_from_disk__mutmut_37, 
        'xǁContextCacheǁ_load_from_disk__mutmut_38': xǁContextCacheǁ_load_from_disk__mutmut_38, 
        'xǁContextCacheǁ_load_from_disk__mutmut_39': xǁContextCacheǁ_load_from_disk__mutmut_39, 
        'xǁContextCacheǁ_load_from_disk__mutmut_40': xǁContextCacheǁ_load_from_disk__mutmut_40, 
        'xǁContextCacheǁ_load_from_disk__mutmut_41': xǁContextCacheǁ_load_from_disk__mutmut_41, 
        'xǁContextCacheǁ_load_from_disk__mutmut_42': xǁContextCacheǁ_load_from_disk__mutmut_42, 
        'xǁContextCacheǁ_load_from_disk__mutmut_43': xǁContextCacheǁ_load_from_disk__mutmut_43, 
        'xǁContextCacheǁ_load_from_disk__mutmut_44': xǁContextCacheǁ_load_from_disk__mutmut_44, 
        'xǁContextCacheǁ_load_from_disk__mutmut_45': xǁContextCacheǁ_load_from_disk__mutmut_45, 
        'xǁContextCacheǁ_load_from_disk__mutmut_46': xǁContextCacheǁ_load_from_disk__mutmut_46, 
        'xǁContextCacheǁ_load_from_disk__mutmut_47': xǁContextCacheǁ_load_from_disk__mutmut_47, 
        'xǁContextCacheǁ_load_from_disk__mutmut_48': xǁContextCacheǁ_load_from_disk__mutmut_48, 
        'xǁContextCacheǁ_load_from_disk__mutmut_49': xǁContextCacheǁ_load_from_disk__mutmut_49, 
        'xǁContextCacheǁ_load_from_disk__mutmut_50': xǁContextCacheǁ_load_from_disk__mutmut_50, 
        'xǁContextCacheǁ_load_from_disk__mutmut_51': xǁContextCacheǁ_load_from_disk__mutmut_51, 
        'xǁContextCacheǁ_load_from_disk__mutmut_52': xǁContextCacheǁ_load_from_disk__mutmut_52, 
        'xǁContextCacheǁ_load_from_disk__mutmut_53': xǁContextCacheǁ_load_from_disk__mutmut_53, 
        'xǁContextCacheǁ_load_from_disk__mutmut_54': xǁContextCacheǁ_load_from_disk__mutmut_54, 
        'xǁContextCacheǁ_load_from_disk__mutmut_55': xǁContextCacheǁ_load_from_disk__mutmut_55, 
        'xǁContextCacheǁ_load_from_disk__mutmut_56': xǁContextCacheǁ_load_from_disk__mutmut_56, 
        'xǁContextCacheǁ_load_from_disk__mutmut_57': xǁContextCacheǁ_load_from_disk__mutmut_57, 
        'xǁContextCacheǁ_load_from_disk__mutmut_58': xǁContextCacheǁ_load_from_disk__mutmut_58, 
        'xǁContextCacheǁ_load_from_disk__mutmut_59': xǁContextCacheǁ_load_from_disk__mutmut_59, 
        'xǁContextCacheǁ_load_from_disk__mutmut_60': xǁContextCacheǁ_load_from_disk__mutmut_60, 
        'xǁContextCacheǁ_load_from_disk__mutmut_61': xǁContextCacheǁ_load_from_disk__mutmut_61, 
        'xǁContextCacheǁ_load_from_disk__mutmut_62': xǁContextCacheǁ_load_from_disk__mutmut_62, 
        'xǁContextCacheǁ_load_from_disk__mutmut_63': xǁContextCacheǁ_load_from_disk__mutmut_63, 
        'xǁContextCacheǁ_load_from_disk__mutmut_64': xǁContextCacheǁ_load_from_disk__mutmut_64
    }
    
    def _load_from_disk(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextCacheǁ_load_from_disk__mutmut_orig"), object.__getattribute__(self, "xǁContextCacheǁ_load_from_disk__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _load_from_disk.__signature__ = _mutmut_signature(xǁContextCacheǁ_load_from_disk__mutmut_orig)
    xǁContextCacheǁ_load_from_disk__mutmut_orig.__name__ = 'xǁContextCacheǁ_load_from_disk'
