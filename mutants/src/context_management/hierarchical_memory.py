"""
Hierarchical Memory System

Implements three-layer memory architecture based on cognitive science research:
- Episodic Memory: Session-specific context and interactions
- Semantic Memory: Long-term knowledge and learned patterns
- Working Memory: Immediate context for current task

Reference: Anthropic 2024 - Effective Context Engineering for AI Agents
"""

import hashlib
import math
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Optional


class MemoryLayer(Enum):
    """Memory layer types."""

    WORKING = "working"  # Immediate context (high priority, limited capacity)
    EPISODIC = "episodic"  # Session-specific (medium priority, session-scoped)
    SEMANTIC = "semantic"  # Long-term knowledge (low priority, persistent)


@dataclass
class MemoryItem:
    """An item stored in memory."""

    content: str
    layer: MemoryLayer
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_accessed: datetime = field(default_factory=lambda: datetime.now(UTC))
    access_count: int = 0
    importance: float = 1.0
    decay_rate: float = 0.1
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    content_hash: str = ""

    def __post_init__(self):
        if not self.content_hash:
            self.content_hash = hashlib.sha256(self.content.encode()).hexdigest()[:16]

    @property
    def age_seconds(self) -> float:
        """Age of item in seconds."""
        return (datetime.now(UTC) - self.created_at).total_seconds()

    @property
    def staleness_seconds(self) -> float:
        """Time since last access."""
        return (datetime.now(UTC) - self.last_accessed).total_seconds()

    @property
    def effective_importance(self) -> float:
        """
        Calculate importance with temporal decay.

        Implements exponential decay based on age and staleness.
        """
        # Age decay (half-life varies by layer)
        if self.layer == MemoryLayer.WORKING:
            half_life_hours = 0.5  # 30 minutes
        elif self.layer == MemoryLayer.EPISODIC:
            half_life_hours = 24  # 1 day
        else:
            half_life_hours = 168  # 1 week

        age_hours = self.age_seconds / 3600
        age_factor = math.exp(-0.693 * age_hours / half_life_hours)

        # Access recency boost
        stale_hours = self.staleness_seconds / 3600
        recency_factor = math.exp(-0.693 * stale_hours / (half_life_hours / 2))

        # Access frequency boost (log scale)
        frequency_boost = math.log1p(self.access_count) * 0.1

        return self.importance * age_factor * recency_factor + frequency_boost

    @property
    def token_estimate(self) -> int:
        """Estimate token count."""
        return len(self.content) // 4 + 1


@dataclass
class MemoryStats:
    """Statistics for a memory layer."""

    item_count: int
    total_tokens: int
    average_importance: float
    oldest_age_hours: float
    most_accessed_count: int


class HierarchicalMemory:
    """
    Three-layer hierarchical memory system.

    Provides:
    - Automatic promotion/demotion between layers
    - Temporal decay for staleness handling
    - Importance-based retrieval
    - Cross-layer deduplication
    """

    # Default capacity limits (in tokens)
    DEFAULT_WORKING_LIMIT = 8_000
    DEFAULT_EPISODIC_LIMIT = 32_000
    DEFAULT_SEMANTIC_LIMIT = 64_000

    def __init__(
        self,
        working_limit: int = DEFAULT_WORKING_LIMIT,
        episodic_limit: int = DEFAULT_EPISODIC_LIMIT,
        semantic_limit: int = DEFAULT_SEMANTIC_LIMIT,
        auto_promote: bool = True,
        auto_demote: bool = True,
    ):
        """
        Initialize hierarchical memory.

        Args:
            working_limit: Token limit for working memory
            episodic_limit: Token limit for episodic memory
            semantic_limit: Token limit for semantic memory
            auto_promote: Auto-promote frequently accessed items
            auto_demote: Auto-demote stale items
        """
        self.limits = {
            MemoryLayer.WORKING: working_limit,
            MemoryLayer.EPISODIC: episodic_limit,
            MemoryLayer.SEMANTIC: semantic_limit,
        }
        self.auto_promote = auto_promote
        self.auto_demote = auto_demote

        # Storage by layer
        self._memory: dict[MemoryLayer, dict[str, MemoryItem]] = {
            MemoryLayer.WORKING: {},
            MemoryLayer.EPISODIC: {},
            MemoryLayer.SEMANTIC: {},
        }

        # Cross-layer index for deduplication
        self._hash_to_layer: dict[str, MemoryLayer] = {}

    def store(
        self,
        content: str,
        layer: MemoryLayer = MemoryLayer.WORKING,
        importance: float = 1.0,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Store item in memory.

        Args:
            content: Content to store
            layer: Target memory layer
            importance: Importance score (0.0-1.0+)
            tags: Optional tags for retrieval
            metadata: Optional metadata

        Returns:
            tuple of (success, warning/error message)
        """
        # Check for duplicates across all layers
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        if content_hash in self._hash_to_layer:
            existing_layer = self._hash_to_layer[content_hash]
            existing_item = self._memory[existing_layer].get(content_hash)
            if existing_item:
                # Update access info on duplicate
                existing_item.last_accessed = datetime.now(UTC)
                existing_item.access_count += 1
                return (
                    True,
                    f"Duplicate found in {existing_layer.value} memory, updated access",
                )

        # Create item
        item = MemoryItem(
            content=content,
            layer=layer,
            importance=importance,
            tags=tags or [],
            metadata=metadata or {},
            content_hash=content_hash,
        )

        # Check capacity and make room if needed
        warning = self._ensure_capacity(layer, item.token_estimate)

        # Store
        self._memory[layer][content_hash] = item
        self._hash_to_layer[content_hash] = layer

        return True, warning

    def retrieve(
        self,
        query: Optional[str] = None,
        layer: Optional[MemoryLayer] = None,
        tags: Optional[list[str]] = None,
        min_importance: float = 0.0,
        max_items: int = 10,
        max_tokens: Optional[int] = None,
    ) -> list[MemoryItem]:
        """
        Retrieve items from memory.

        Args:
            query: Optional query string for matching
            layer: Specific layer to search (None = all layers)
            tags: Filter by tags
            min_importance: Minimum effective importance
            max_items: Maximum items to return
            max_tokens: Maximum total tokens to return

        Returns:
            list of matching items sorted by effective importance
        """
        results = []

        # Determine layers to search
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            for item in self._memory[lyr].values():
                # Filter by importance
                if item.effective_importance < min_importance:
                    continue

                # Filter by tags
                if tags and not any(t in item.tags for t in tags):
                    continue

                # Filter by query (simple substring match)
                if query and query.lower() not in item.content.lower():
                    continue

                results.append(item)

        # Sort by effective importance (highest first)
        results.sort(key=lambda x: x.effective_importance, reverse=True)

        # Apply limits
        if max_tokens:
            limited = []
            total_tokens = 0
            for item in results:
                if total_tokens + item.token_estimate <= max_tokens:
                    limited.append(item)
                    total_tokens += item.token_estimate
            results = limited

        results = results[:max_items]

        # Update access info
        for item in results:
            item.last_accessed = datetime.now(UTC)
            item.access_count += 1

        # Check for promotions
        if self.auto_promote:
            self._check_promotions()

        return results

    def get_working_context(self, max_tokens: Optional[int] = None) -> list[str]:
        """
        Get current working memory as context strings.

        Args:
            max_tokens: Optional token limit

        Returns:
            list of content strings from working memory
        """
        items = self.retrieve(
            layer=MemoryLayer.WORKING,
            max_items=100,
            max_tokens=max_tokens or self.limits[MemoryLayer.WORKING],
        )
        return [item.content for item in items]

    def promote(self, content_hash: str, target_layer: MemoryLayer) -> bool:
        """
        Promote item to a higher-priority layer.

        Args:
            content_hash: Hash of item to promote
            target_layer: Target layer (must be higher priority)

        Returns:
            True if promoted, False if not found or invalid
        """
        if content_hash not in self._hash_to_layer:
            return False

        current_layer = self._hash_to_layer[content_hash]

        # Validate promotion (working > episodic > semantic in priority)
        layer_priority = {
            MemoryLayer.SEMANTIC: 1,
            MemoryLayer.EPISODIC: 2,
            MemoryLayer.WORKING: 3,
        }

        if layer_priority[target_layer] <= layer_priority[current_layer]:
            return False  # Can only promote to higher priority

        # Move item
        item = self._memory[current_layer].pop(content_hash)
        item.layer = target_layer

        # Ensure capacity in target
        self._ensure_capacity(target_layer, item.token_estimate)

        self._memory[target_layer][content_hash] = item
        self._hash_to_layer[content_hash] = target_layer

        return True

    def demote(self, content_hash: str, target_layer: MemoryLayer) -> bool:
        """
        Demote item to a lower-priority layer.

        Args:
            content_hash: Hash of item to demote
            target_layer: Target layer (must be lower priority)

        Returns:
            True if demoted, False if not found or invalid
        """
        if content_hash not in self._hash_to_layer:
            return False

        current_layer = self._hash_to_layer[content_hash]

        layer_priority = {
            MemoryLayer.SEMANTIC: 1,
            MemoryLayer.EPISODIC: 2,
            MemoryLayer.WORKING: 3,
        }

        if layer_priority[target_layer] >= layer_priority[current_layer]:
            return False  # Can only demote to lower priority

        # Move item
        item = self._memory[current_layer].pop(content_hash)
        item.layer = target_layer

        # Ensure capacity in target
        self._ensure_capacity(target_layer, item.token_estimate)

        self._memory[target_layer][content_hash] = item
        self._hash_to_layer[content_hash] = target_layer

        return True

    def clear_layer(self, layer: MemoryLayer):
        """Clear all items from a layer."""
        for content_hash in list(self._memory[layer].keys()):
            del self._hash_to_layer[content_hash]
        self._memory[layer].clear()

    def clear_all(self):
        """Clear all memory layers."""
        for layer in MemoryLayer:
            self.clear_layer(layer)

    def get_stats(self, layer: Optional[MemoryLayer] = None) -> dict[str, MemoryStats]:
        """
        Get statistics for memory layers.

        Args:
            layer: Specific layer (None = all layers)

        Returns:
            dict mapping layer name to stats
        """
        stats = {}
        layers = [layer] if layer else list(MemoryLayer)

        for lyr in layers:
            items = list(self._memory[lyr].values())
            if not items:
                stats[lyr.value] = MemoryStats(
                    item_count=0,
                    total_tokens=0,
                    average_importance=0.0,
                    oldest_age_hours=0.0,
                    most_accessed_count=0,
                )
            else:
                total_tokens = sum(i.token_estimate for i in items)
                avg_importance = sum(i.effective_importance for i in items) / len(items)
                oldest_age = max(i.age_seconds for i in items) / 3600
                most_accessed = max(i.access_count for i in items)

                stats[lyr.value] = MemoryStats(
                    item_count=len(items),
                    total_tokens=total_tokens,
                    average_importance=avg_importance,
                    oldest_age_hours=oldest_age,
                    most_accessed_count=most_accessed,
                )

        return stats

    def _ensure_capacity(self, layer: MemoryLayer, needed_tokens: int) -> Optional[str]:
        """Ensure capacity in layer, evicting if necessary."""
        current_tokens = sum(i.token_estimate for i in self._memory[layer].values())
        limit = self.limits[layer]

        if current_tokens + needed_tokens <= limit:
            return None

        # Need to evict
        evicted_count = 0
        items = sorted(self._memory[layer].values(), key=lambda x: x.effective_importance)

        while current_tokens + needed_tokens > limit and items:
            item = items.pop(0)

            # Try to demote to lower layer instead of deleting
            if self.auto_demote and layer != MemoryLayer.SEMANTIC:
                lower_layer = (
                    MemoryLayer.EPISODIC if layer == MemoryLayer.WORKING else MemoryLayer.SEMANTIC
                )
                self.demote(item.content_hash, lower_layer)
            else:
                # Delete
                del self._memory[layer][item.content_hash]
                del self._hash_to_layer[item.content_hash]

            current_tokens -= item.token_estimate
            evicted_count += 1

        if evicted_count > 0:
            return f"Evicted/demoted {evicted_count} items from {layer.value} memory"
        return None

    def _check_promotions(self):
        """Check if any items should be promoted based on access patterns."""
        promotion_threshold = 5  # Promote after 5 accesses

        # Check episodic -> working
        for content_hash, item in list(self._memory[MemoryLayer.EPISODIC].items()):
            if item.access_count >= promotion_threshold:
                self.promote(content_hash, MemoryLayer.WORKING)

        # Check semantic -> episodic
        for content_hash, item in list(self._memory[MemoryLayer.SEMANTIC].items()):
            if item.access_count >= promotion_threshold:
                self.promote(content_hash, MemoryLayer.EPISODIC)
