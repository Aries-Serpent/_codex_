"""
Context Priority Queue

Priority-based queue for context management with decay scoring,
age-based degradation, and configurable priority levels.
"""

import heapq
import math
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import IntEnum
from functools import total_ordering
from typing import Any, Optional


class Priority(IntEnum):
    """Priority levels for context items."""

    CRITICAL = 5  # Must never prune: fresh errors, direct user commands
    HIGH = 4  # Important: current diffs, active task context
    MEDIUM = 3  # Standard: recent tool outputs, intermediate results
    LOW = 2  # Background: historical context, logs
    DISPOSABLE = 1  # Can prune freely: debug output, verbose logs


@total_ordering
@dataclass
class PriorityItem:
    """An item in the priority queue."""

    content: str
    priority: Priority
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_accessed: datetime = field(default_factory=lambda: datetime.now(UTC))
    access_count: int = 0
    token_count: int = 0
    source: str = ""
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __lt__(self, other):
        """Compare for heap ordering (lower score = lower priority)."""
        return self.effective_priority < other.effective_priority

    @property
    def age_seconds(self) -> float:
        """Age of item in seconds."""
        return (datetime.now(UTC) - self.created_at).total_seconds()

    @property
    def staleness_seconds(self) -> float:
        """Time since last access in seconds."""
        return (datetime.now(UTC) - self.last_accessed).total_seconds()

    @property
    def effective_priority(self) -> float:
        """
        Compute effective priority with decay.

        Priority decays based on:
        - Age (older = lower)
        - Staleness (not accessed recently = lower)
        - Access count (less accessed = lower)
        """
        base = float(self.priority)

        # Age decay: half-life of 1 hour
        age_hours = self.age_seconds / 3600
        age_decay = math.exp(-0.693 * age_hours)  # 0.693 = ln(2)

        # Staleness decay: half-life of 30 minutes
        stale_hours = self.staleness_seconds / 1800
        stale_decay = math.exp(-0.693 * stale_hours)

        # Access boost: log scale
        access_boost = math.log1p(self.access_count) * 0.1

        return base * age_decay * stale_decay + access_boost


class ContextPriorityQueue:
    """
    Priority queue for context management.

    Implements priority-based storage with decay scoring,
    token budget awareness, and automatic pruning.
    """

    def __init__(
        self,
        max_items: int = 1000,
        max_tokens: int = 56000,
        decay_enabled: bool = True,
        auto_prune: bool = True,
    ):
        """
        Initialize priority queue.

        Args:
            max_items: Maximum items in queue
            max_tokens: Maximum total tokens
            decay_enabled: Whether to apply priority decay
            auto_prune: Whether to auto-prune when over limits
        """
        self.max_items = max_items
        self.max_tokens = max_tokens
        self.decay_enabled = decay_enabled
        self.auto_prune = auto_prune

        self._items: list[PriorityItem] = []
        self._token_count = 0
        self._item_index: dict[str, int] = {}  # content_hash -> heap index

    def push(
        self,
        content: str,
        priority: Priority = Priority.MEDIUM,
        source: str = "",
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> bool:
        """
        Add item to queue.

        Args:
            content: Content text
            priority: Priority level
            source: Source identifier
            tags: Optional tags for filtering
            metadata: Optional metadata

        Returns:
            True if added, False if rejected
        """
        # Estimate token count (rough: 4 chars per token)
        token_count = len(content) // 4 + 1

        # Check if we need to prune
        if self.auto_prune:
            while (
                len(self._items) >= self.max_items
                or self._token_count + token_count > self.max_tokens
            ):
                if not self._prune_lowest():
                    break

        # Check limits after pruning
        if len(self._items) >= self.max_items:
            return False
        if self._token_count + token_count > self.max_tokens:
            return False

        item = PriorityItem(
            content=content,
            priority=priority,
            token_count=token_count,
            source=source,
            tags=tags or [],
            metadata=metadata or {},
        )

        heapq.heappush(self._items, item)
        self._token_count += token_count

        return True

    def pop(self) -> Optional[PriorityItem]:
        """
        Remove and return lowest priority item.

        Returns:
            Lowest priority item or None if empty
        """
        if not self._items:
            return None

        item = heapq.heappop(self._items)
        self._token_count -= item.token_count
        return item

    def pop_highest(self) -> Optional[PriorityItem]:
        """
        Remove and return highest priority item.

        Returns:
            Highest priority item or None if empty
        """
        if not self._items:
            return None

        # Find highest priority item
        max_idx = 0
        max_priority = self._items[0].effective_priority

        for i, item in enumerate(self._items):
            if item.effective_priority > max_priority:
                max_priority = item.effective_priority
                max_idx = i

        item = self._items[max_idx]
        self._items[max_idx] = self._items[-1]
        self._items.pop()
        heapq.heapify(self._items)

        self._token_count -= item.token_count
        return item

    def peek_lowest(self) -> Optional[PriorityItem]:
        """Peek at lowest priority item without removing."""
        if not self._items:
            return None
        return self._items[0]

    def peek_highest(self) -> Optional[PriorityItem]:
        """Peek at highest priority item without removing."""
        if not self._items:
            return None
        return max(self._items, key=lambda x: x.effective_priority)

    def get_all_by_priority(
        self, min_priority: Priority = Priority.DISPOSABLE
    ) -> list[PriorityItem]:
        """
        Get all items at or above minimum priority.

        Args:
            min_priority: Minimum priority level

        Returns:
            list of items sorted by effective priority (highest first)
        """
        filtered = [item for item in self._items if item.priority >= min_priority]
        return sorted(filtered, key=lambda x: x.effective_priority, reverse=True)

    def get_by_tags(self, tags: list[str]) -> list[PriorityItem]:
        """Get items matching any of the given tags."""
        tag_set = set(tags)
        return [item for item in self._items if tag_set & set(item.tags)]

    def prune_to_tokens(self, target_tokens: int) -> list[PriorityItem]:
        """
        Prune queue until under target token count.

        Args:
            target_tokens: Target maximum tokens

        Returns:
            list of pruned items
        """
        pruned = []
        while self._token_count > target_tokens and self._items:
            item = self.pop()
            if item:
                pruned.append(item)
        return pruned

    def prune_below_priority(self, min_priority: Priority) -> list[PriorityItem]:
        """
        Remove all items below minimum priority.

        Args:
            min_priority: Minimum priority to keep

        Returns:
            list of pruned items
        """
        keep = []
        pruned = []

        for item in self._items:
            if item.priority >= min_priority:
                keep.append(item)
            else:
                pruned.append(item)
                self._token_count -= item.token_count

        self._items = keep
        heapq.heapify(self._items)

        return pruned

    def refresh_priorities(self):
        """Refresh effective priorities (triggers decay recalculation)."""
        heapq.heapify(self._items)

    def access_item(self, content: str) -> bool:
        """
        Mark item as accessed to boost its priority.

        Args:
            content: Content text to find and access

        Returns:
            True if found and updated, False otherwise
        """
        for item in self._items:
            if item.content == content:
                item.last_accessed = datetime.now(UTC)
                item.access_count += 1
                heapq.heapify(self._items)
                return True
        return False

    def clear(self):
        """Clear all items."""
        self._items.clear()
        self._token_count = 0
        self._item_index.clear()

    @property
    def size(self) -> int:
        """Number of items in queue."""
        return len(self._items)

    @property
    def token_count(self) -> int:
        """Total tokens in queue."""
        return self._token_count

    @property
    def is_empty(self) -> bool:
        """Whether queue is empty."""
        return len(self._items) == 0

    def get_stats(self) -> dict:
        """Get queue statistics."""
        if not self._items:
            return {
                "size": 0,
                "token_count": 0,  # nosec B105
                "priority_distribution": {},
                "average_age_seconds": 0,
                "average_effective_priority": 0,
            }

        priority_dist: dict[str, Any] = {}
        for item in self._items:
            p = item.priority.name
            priority_dist[p] = priority_dist.get(p, 0) + 1

        return {
            "size": len(self._items),
            "token_count": self._token_count,
            "priority_distribution": priority_dist,
            "average_age_seconds": sum(i.age_seconds for i in self._items) / len(self._items),
            "average_effective_priority": sum(i.effective_priority for i in self._items)
            / len(self._items),
        }

    def _prune_lowest(self) -> bool:
        """Prune single lowest priority item."""
        item = self.pop()
        return item is not None
