"""
RAG Caching Module

Provides production-grade caching for RAG pipeline:
- Query result caching
- Embedding caching
- Multi-level caching (memory, disk, distributed)
- Cache invalidation strategies
"""

from __future__ import annotations

from typing import Any

from .distributed_cache import (
    CacheBackend,
    DistributedCache,
    DistributedCacheConfig,
)
from .query_cache import (
    CacheEntry,
    CacheStats,
    QueryCache,
    QueryCacheConfig,
)

try:
    from .embedding_cache import (
        EmbeddingCache,
        EmbeddingCacheConfig,
    )
except Exception:  # nosec B110 — optional numpy dependency, intentional no-op  # pragma: no cover
    pass

__all__ = [
    # Query cache
    "QueryCache",
    "QueryCacheConfig",
    "CacheEntry",
    "CacheStats",
    # Embedding cache
    "EmbeddingCache",
    "EmbeddingCacheConfig",
    # Distributed cache
    "DistributedCache",
    "DistributedCacheConfig",
    "CacheBackend",
]


def __getattr__(name: str) -> Any:
    if name in {"EmbeddingCache", "EmbeddingCacheConfig"}:
        from .embedding_cache import EmbeddingCache, EmbeddingCacheConfig

        globals().update(
            {
                "EmbeddingCache": EmbeddingCache,
                "EmbeddingCacheConfig": EmbeddingCacheConfig,
            }
        )
        return globals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
