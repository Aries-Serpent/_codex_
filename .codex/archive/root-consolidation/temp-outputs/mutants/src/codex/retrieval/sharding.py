"""Index Sharding for Knowledge Crawler.

This module implements consistent hashing-based index sharding to scale
the Knowledge Crawler to handle massive documentation sets (100k+ articles)
without blocking.

Part of PS-06 Enhancement: Index Sharding - Priority 4
"""

from __future__ import annotations

import bisect
import hashlib
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class ShardInfo:
    """Information about an index shard."""

    shard_id: int
    shard_name: str
    total_documents: int = 0
    size_bytes: int = 0
    last_updated: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "shard_id": self.shard_id,
            "shard_name": self.shard_name,
            "total_documents": self.total_documents,
            "size_bytes": self.size_bytes,
            "last_updated": self.last_updated,
            "metadata": self.metadata,
        }


class ConsistentHashRing:
    """Consistent hashing ring for shard distribution.

    Implements consistent hashing with virtual nodes to prevent
    hotspots and ensure balanced distribution.

    **Performance Note**: This class can optionally use xxhash for faster
    hashing operations. If xxhash is not available, it falls back to MD5
    from the standard library, which is deterministic but slower. For
    production use with high throughput requirements, install xxhash:

        pip install xxhash

    The fallback ensures functionality without optional dependencies, but
    xxhash is recommended for systems processing >10k documents/second.

    Example:
        >>> ring = ConsistentHashRing(num_shards=4, virtual_nodes=150)
        >>> shard_id = ring.get_shard("document-12345")
        >>> logger.info(f"Document maps to shard: {shard_id}")
    """

    def __init__(
        self,
        num_shards: int,
        virtual_nodes: int = 150,
        hash_function: Optional[Callable[[str], int]] = None,
    ):
        """Initialize consistent hash ring.

        Args:
            num_shards: Number of physical shards
            virtual_nodes: Virtual nodes per shard (prevents hotspots)
            hash_function: Optional custom hash function
        """
        self.num_shards = num_shards
        self.virtual_nodes = virtual_nodes
        self.hash_function = hash_function or self._default_hash

        # Ring structure: sorted list of (hash_value, shard_id)
        self._ring: list[int] = []
        self._ring_map: dict[int, int] = {}

        # Build the ring
        self._build_ring()

        logger.info(
            f"Consistent hash ring initialized: "
            f"{num_shards} shards, {virtual_nodes} virtual nodes each, "
            f"{len(self._ring)} total positions"
        )

    def _default_hash(self, key: str) -> int:
        """Default hash function using xxhash or hashlib.

        Args:
            key: Key to hash

        Returns:
            Hash value as integer
        """
        # Try xxhash for speed (if available).
        # Note: xxhash is an optional performance dependency. It should be listed as an
        # extra in packaging metadata (e.g., pyproject.toml / requirements) so users
        # can install it explicitly for faster sharding, while this code continues
        # to work correctly without it.
        try:
            import xxhash

            return xxhash.xxh64(key.encode()).intdigest()
        except ImportError:
            # Fallback to SHA-256 for deterministic hashing across sessions/processes.
            # SHA-256 provides better collision resistance than MD5 while maintaining
            # deterministic behavior. We avoid built-in hash() as it's randomized
            # between Python runs for security reasons.
            import hashlib

            return int.from_bytes(hashlib.sha256(key.encode()).digest()[:8], "big")

    def _build_ring(self) -> None:
        """Build the consistent hash ring with virtual nodes."""
        for shard_id in range(self.num_shards):
            for vnode_id in range(self.virtual_nodes):
                # Create unique key for virtual node
                vnode_key = f"shard-{shard_id}-vnode-{vnode_id}"
                hash_value = self.hash_function(vnode_key)

                # Add to ring
                self._ring.append(hash_value)
                self._ring_map[hash_value] = shard_id

        # Sort ring for binary search
        self._ring.sort()

    def get_shard(self, key: str) -> int:
        """Get shard ID for a given key.

        Uses consistent hashing to determine which shard
        should store the item with the given key.

        Args:
            key: Document ID or key to hash

        Returns:
            Shard ID (0 to num_shards-1)
        """
        if not self._ring:
            raise ValueError("Hash ring is empty")

        # Hash the key
        hash_value = self.hash_function(key)

        # Find position in ring using binary search
        idx = bisect.bisect_right(self._ring, hash_value)

        # Wrap around if necessary
        if idx == len(self._ring):
            idx = 0

        # Get shard ID from ring map
        ring_hash = self._ring[idx]
        return self._ring_map[ring_hash]

    def get_shard_distribution(self, keys: list[str]) -> dict[int, int]:
        """Analyze shard distribution for a list of keys.

        Useful for understanding load distribution and
        identifying potential hotspots.

        Args:
            keys: List of keys to analyze

        Returns:
            Dictionary mapping shard_id to count
        """
        distribution: dict[int, int] = dict.fromkeys(range(self.num_shards), 0)

        for key in keys:
            shard_id = self.get_shard(key)
            distribution[shard_id] += 1

        return distribution

    def add_shard(self) -> int:
        """Add a new shard to the ring.

        Returns:
            ID of the newly added shard
        """
        new_shard_id = self.num_shards
        self.num_shards += 1

        # Add virtual nodes for new shard
        for vnode_id in range(self.virtual_nodes):
            vnode_key = f"shard-{new_shard_id}-vnode-{vnode_id}"
            hash_value = self.hash_function(vnode_key)

            # Insert into ring maintaining sorted order
            idx = bisect.bisect_left(self._ring, hash_value)
            self._ring.insert(idx, hash_value)
            self._ring_map[hash_value] = new_shard_id

        logger.info(f"Added shard {new_shard_id} to ring")
        return new_shard_id

    def remove_shard(self, shard_id: int) -> bool:
        """Remove a shard from the ring.

        Args:
            shard_id: ID of shard to remove

        Returns:
            True if removed successfully
        """
        if shard_id >= self.num_shards:
            return False

        # Remove all virtual nodes for this shard
        positions_to_remove = [pos for pos, sid in self._ring_map.items() if sid == shard_id]

        for pos in positions_to_remove:
            self._ring.remove(pos)
            del self._ring_map[pos]

        logger.info(f"Removed shard {shard_id} from ring")
        return True


def get_shard_for_id(doc_id: str, total_shards: int, use_consistent_hashing: bool = True) -> int:
    """Get shard ID for a document ID.

    Convenience function for simple shard lookup.

    Args:
        doc_id: Document identifier
        total_shards: Total number of shards
        use_consistent_hashing: Use consistent hashing (vs simple modulo)

    Returns:
        Shard ID (0 to total_shards-1)

    Example:
        >>> shard = get_shard_for_id("doc-12345", total_shards=4)
        >>> logger.info(f"Document goes to shard: {shard}")
    """
    if use_consistent_hashing:
        # Use consistent hashing for better distribution
        ring = ConsistentHashRing(total_shards)
        return ring.get_shard(doc_id)
    # Simple modulo hashing - MD5 used for distribution, not security
    # nosec B324 - MD5 used for data distribution hashing, not cryptographic security
    hash_obj = hashlib.md5(doc_id.encode(), usedforsecurity=False)
    hash_int = int.from_bytes(hash_obj.digest()[:4], "big")
    return hash_int % total_shards


class ShardManager:
    """Manager for index shards.

    Handles shard creation, routing, and rebalancing.

    Example:
        >>> manager = ShardManager(num_shards=4)
        >>> shard_id = manager.route_document("doc-12345")
        >>> shard_info = manager.get_shard_info(shard_id)
    """

    def __init__(
        self,
        num_shards: int,
        virtual_nodes: int = 150,
        shard_name_prefix: str = "shard",
    ):
        """Initialize shard manager.

        Args:
            num_shards: Number of shards to create
            virtual_nodes: Virtual nodes per shard for consistent hashing
            shard_name_prefix: Prefix for shard names
        """
        self.num_shards = num_shards
        self.shard_name_prefix = shard_name_prefix

        # Initialize consistent hash ring
        self.hash_ring = ConsistentHashRing(num_shards=num_shards, virtual_nodes=virtual_nodes)

        # Initialize shard info
        self.shards: dict[int, ShardInfo] = {}
        for shard_id in range(num_shards):
            self.shards[shard_id] = ShardInfo(
                shard_id=shard_id, shard_name=f"{shard_name_prefix}_{shard_id:02d}"
            )

        logger.info(f"ShardManager initialized with {num_shards} shards")

    def route_document(self, doc_id: str) -> int:
        """Route document to appropriate shard.

        Args:
            doc_id: Document identifier

        Returns:
            Shard ID
        """
        return self.hash_ring.get_shard(doc_id)

    def get_shard_info(self, shard_id: int) -> Optional[ShardInfo]:
        """Get information about a shard.

        Args:
            shard_id: Shard identifier

        Returns:
            ShardInfo or None if not found
        """
        return self.shards.get(shard_id)

    def get_shard_name(self, shard_id: int) -> str:
        """Get shard name for a shard ID.

        Args:
            shard_id: Shard identifier

        Returns:
            Shard name (e.g., "shard_00", "shard_01")
        """
        shard_info = self.get_shard_info(shard_id)
        if shard_info:
            return shard_info.shard_name
        return f"{self.shard_name_prefix}_{shard_id:02d}"

    def update_shard_stats(
        self,
        shard_id: int,
        doc_count: Optional[int] = None,
        size_bytes: Optional[int] = None,
    ) -> None:
        """Update statistics for a shard.

        Args:
            shard_id: Shard identifier
            doc_count: New document count
            size_bytes: New size in bytes
        """
        if shard_id not in self.shards:
            logger.warning(f"Shard {shard_id} not found")
            return

        if doc_count is not None:
            self.shards[shard_id].total_documents = doc_count

        if size_bytes is not None:
            self.shards[shard_id].size_bytes = size_bytes

    def get_all_shards(self) -> list[ShardInfo]:
        """Get information about all shards.

        Returns:
            List of ShardInfo objects
        """
        return list(self.shards.values())

    def get_load_distribution(self) -> dict[int, dict[str, Any]]:
        """Get load distribution across shards.

        Returns:
            Dictionary mapping shard_id to load metrics
        """
        total_docs = sum(s.total_documents for s in self.shards.values())
        total_size = sum(s.size_bytes for s in self.shards.values())

        distribution = {}
        for shard_id, shard_info in self.shards.items():
            doc_percentage = (
                (shard_info.total_documents / total_docs * 100) if total_docs > 0 else 0
            )
            size_percentage = (shard_info.size_bytes / total_size * 100) if total_size > 0 else 0

            distribution[shard_id] = {
                "shard_name": shard_info.shard_name,
                "documents": shard_info.total_documents,
                "size_bytes": shard_info.size_bytes,
                "doc_percentage": round(doc_percentage, 2),
                "size_percentage": round(size_percentage, 2),
            }

        return distribution


__all__ = [
    "ConsistentHashRing",
    "ShardInfo",
    "ShardManager",
    "get_shard_for_id",
]
