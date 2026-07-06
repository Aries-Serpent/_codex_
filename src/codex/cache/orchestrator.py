"""
4-Layer Cache Orchestrator: Unified management for L1-L4 cache tiers.

Coordinates:
- L1: Request Cache (in-process, TTL=300s)
- L2: Session Cache (Redis, TTL=3600s)
- L3: Knowledge Cache (disk, TTL=86400s)
- L4: Model Cache (persistent)

Provides:
- Unified get/set interface across all layers
- Automatic promotion/demotion between layers
- Health monitoring and metrics
- Eviction coordination
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from .knowledge_cache_l3 import L3KnowledgeCache, get_l3_cache
from .model_cache_l4 import L4ModelCache, get_l4_cache
from .request_cache import L1RequestCache, get_l1_cache
from .session_cache_l2 import L2SessionCache, get_l2_cache

logger = logging.getLogger(__name__)


class UnifiedCacheOrchestrator:
    """Unified cache orchestrator managing all 4 layers.

    Strategy:
    - L1 (request): Fast path for same-request access
    - L2 (session): Cross-request persistence
    - L3 (knowledge): Large datasets and long-term storage
    - L4 (models): Permanent model weights

    Cache promotion flow:
    - L1 miss → check L2
    - L2 miss → check L3
    - L3 miss → check L4
    - On hit in L2/L3/L4 → promote to L1

    Usage:
        cache = UnifiedCacheOrchestrator()
        cache.set("key", value, tier="L2")  # Store in L2+L1
        value = cache.get("key")  # Searches L1→L2→L3→L4
        stats = cache.get_stats()
    """

    def __init__(
        self,
        l1: Optional[L1RequestCache] = None,
        l2: Optional[L2SessionCache] = None,
        l3: Optional[L3KnowledgeCache] = None,
        l4: Optional[L4ModelCache] = None,
    ):
        """Initialize orchestrator with cache tiers."""
        self.l1 = l1 or get_l1_cache()
        self.l2 = l2 or get_l2_cache()
        self.l3 = l3 or get_l3_cache()
        self.l4 = l4 or get_l4_cache()

        self._stats = {
            "total_hits": 0,
            "total_misses": 0,
            "l1_hits": 0,
            "l2_hits": 0,
            "l3_hits": 0,
            "l4_hits": 0,
            "promotions": 0,
        }

    def get(self, key: str) -> Optional[Any]:
        """Get value from unified cache.

        Search order: L1 → L2 → L3 → L4

        Args:
            key: Cache key

        Returns:
            Cached value if found in any tier, None otherwise
        """
        # Try L1 (fastest)
        value = self.l1.get(key)
        if value is not None:
            self._stats["l1_hits"] += 1
            self._stats["total_hits"] += 1
            logger.debug(f"Unified cache L1 hit: {key}")
            return value

        # Try L2 (Redis)
        value = self.l2.get(key)
        if value is not None:
            self._stats["l2_hits"] += 1
            self._stats["total_hits"] += 1
            # Promote to L1
            self.l1.set(key, value)
            self._stats["promotions"] += 1
            logger.debug(f"Unified cache L2 hit: {key} (promoted to L1)")
            return value

        # Try L3 (disk)
        value = self.l3.get(key)
        if value is not None:
            self._stats["l3_hits"] += 1
            self._stats["total_hits"] += 1
            # Promote to L1 and L2
            self.l1.set(key, value)
            self.l2.set(key, value)
            self._stats["promotions"] += 1
            logger.debug(f"Unified cache L3 hit: {key} (promoted to L1+L2)")
            return value

        # Try L4 (models)
        # L4 is special - typically accessed via model-specific methods
        # but can be accessed generically
        if key.startswith("model:") or key.startswith("artifact:"):
            # Try to extract model_id and version from key
            # Format: model:{model_id}:{version} or artifact:{artifact_id}:{version}
            parts = key.split(":")
            if len(parts) >= 3:
                artifact_type = parts[0]
                artifact_id = parts[1]
                version = parts[2]

                if artifact_type == "model":
                    result = self.l4.get_model(artifact_id, version)
                else:
                    result = self.l4.get_artifact(artifact_id, version)

                if result:
                    self._stats["l4_hits"] += 1
                    self._stats["total_hits"] += 1
                    # Promote to L1 and L2
                    self.l1.set(key, result)
                    self.l2.set(key, result)
                    self._stats["promotions"] += 1
                    logger.debug(f"Unified cache L4 hit: {key} (promoted to L1+L2)")
                    return result

        self._stats["total_misses"] += 1
        logger.debug(f"Unified cache miss: {key}")
        return None

    def set(self, key: str, value: Any, tier: str = "L2") -> None:
        """Set value in unified cache.

        Args:
            key: Cache key
            value: Value to cache
            tier: Which tier to write to ("L1", "L2", "L3", "L4")
                When tier="L2", also writes to L1
                When tier="L3", also writes to L1+L2
        """
        if tier == "L1":
            self.l1.set(key, value)
        elif tier == "L2":
            self.l2.set(key, value)
            # Also promote to L1
            self.l1.set(key, value)
        elif tier == "L3":
            self.l3.set(key, value)
            # Promote to L1 and L2
            self.l1.set(key, value)
            self.l2.set(key, value)
        elif tier == "L4":
            # L4 requires model-specific set operations
            logger.warning("Use model-specific set methods for L4 cache")
        else:
            logger.warning(f"Unknown cache tier: {tier}")

    def delete(self, key: str) -> bool:
        """Delete key from all cache tiers.

        Args:
            key: Cache key

        Returns:
            True if deleted from at least one tier, False otherwise
        """
        result = False
        result = self.l1.delete(key) or result
        result = self.l2.delete(key) or result
        result = self.l3.delete(key) or result
        return result

    def clear(self) -> None:
        """Clear all cache tiers."""
        self.l1.clear()
        self.l2.clear()
        self.l3.clear()
        # Note: L4 is intentionally NOT cleared (persistent storage)

    def get_stats(self) -> dict[str, Any]:
        """Get unified cache statistics across all tiers.

        Returns:
            Dict with hit rates, tier breakdowns, and health info
        """
        total_requests = self._stats["total_hits"] + self._stats["total_misses"]
        overall_hit_rate = (
            self._stats["total_hits"] / total_requests * 100 if total_requests > 0 else 0.0
        )

        return {
            "overall": {
                "hit_rate": f"{overall_hit_rate:.1f}%",
                "total_hits": self._stats["total_hits"],
                "total_misses": self._stats["total_misses"],
                "total_requests": total_requests,
                "promotions": self._stats["promotions"],
            },
            "l1": {
                "hits": self._stats["l1_hits"],
                "stats": self.l1.get_stats(),
            },
            "l2": {
                "hits": self._stats["l2_hits"],
                "stats": self.l2.get_stats(),
            },
            "l3": {
                "hits": self._stats["l3_hits"],
                "stats": self.l3.get_stats(),
            },
            "l4": {
                "hits": self._stats["l4_hits"],
                "stats": self.l4.get_stats(),
            },
        }

    def health_check(self) -> dict[str, Any]:
        """Check health of all cache tiers.

        Returns:
            Dict with health status for each tier
        """
        return {
            "l1": "healthy" if self.l1 else "unavailable",
            "l2": "healthy" if self.l2._connected else "degraded",
            "l3": "healthy",  # SQLite always available
            "l4": "healthy",  # Filesystem always available
        }


# Global orchestrator instance
_orchestrator_instance: Optional[UnifiedCacheOrchestrator] = None


def get_cache_orchestrator() -> UnifiedCacheOrchestrator:
    """Get the global cache orchestrator instance (singleton)."""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = UnifiedCacheOrchestrator()
    return _orchestrator_instance
