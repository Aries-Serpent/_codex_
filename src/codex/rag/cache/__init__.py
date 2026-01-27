"""
RAG Caching Module

Provides production-grade caching for RAG pipeline:
- Query result caching
- Embedding caching
- Multi-level caching (memory, disk, distributed)
- Cache invalidation strategies
"""

from .distributed_cache import (
    CacheBackend,
    DistributedCache,
    DistributedCacheConfig,
)
from .embedding_cache import (
    EmbeddingCache,
    EmbeddingCacheConfig,
)
from .query_cache import (
    CacheEntry,
    CacheStats,
    QueryCache,
    QueryCacheConfig,
)

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
