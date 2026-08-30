"""Codex caching layer - unified multi-tier cache hierarchy.

This module provides a sophisticated caching framework with:
- Segmented LRU (hot/warm/cold segments with different TTLs)
- Adaptive TTL extension on access
- Cache warming for cold-start optimization
- Thread-safe concurrent access
- Comprehensive metrics and monitoring

Wave 5 Phase 6 Optimization targets:
- Runtime cache hit rate: 65% → >90%
- Lock contention reduction: -10% throughput loss
- Cold-start optimization: Cache warming pre-loads hot keys
"""

from .unified_cache import CacheEntry, CacheSegment, UnifiedCache, memoize

__all__ = ["UnifiedCache", "CacheSegment", "CacheEntry", "memoize"]
