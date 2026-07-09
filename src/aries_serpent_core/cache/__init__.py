"""
4-Layer Cache Hierarchy for Phase 13.4 Performance Optimization

L1: Request Cache (in-process, TTL=300s)
L2: Session Cache (Redis, TTL=3600s)
L3: Knowledge Cache (disk-backed, TTL=86400s)
L4: Model Cache (weights, TTL=forever with refresh)

Success Metrics:
- All endpoints <500ms p99 latency
- Cache hit rates >85%
- Zero eviction storms
"""

from .knowledge_cache_l3 import L3KnowledgeCache, get_l3_cache
from .middleware import CacheInstrumentationMiddleware
from .model_cache_l4 import L4ModelCache, get_l4_cache
from .orchestrator import UnifiedCacheOrchestrator, get_cache_orchestrator
from .request_cache import (
    L1CacheDecorator,
    L1RequestCache,
    get_l1_cache,
    reset_l1_cache,
)
from .session_cache_l2 import L2SessionCache, get_l2_cache

__all__ = [
    # L1: Request Cache
    "L1RequestCache",
    "L1CacheDecorator",
    "get_l1_cache",
    "reset_l1_cache",
    # L2: Session Cache
    "L2SessionCache",
    "get_l2_cache",
    # L3: Knowledge Cache
    "L3KnowledgeCache",
    "get_l3_cache",
    # L4: Model Cache
    "L4ModelCache",
    "get_l4_cache",
    # Orchestrator
    "UnifiedCacheOrchestrator",
    "get_cache_orchestrator",
    # Middleware
    "CacheInstrumentationMiddleware",
]
