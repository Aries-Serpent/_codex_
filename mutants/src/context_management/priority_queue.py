"""
Context Priority Queue

Priority-based queue for context management with decay scoring,
age-based degradation, and configurable priority levels.
"""

import heapq
import math
from typing import Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum
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


class Priority(IntEnum):
    """Priority levels for context items."""

    CRITICAL = 5  # Must never prune: fresh errors, direct user commands
    HIGH = 4  # Important: current diffs, active task context
    MEDIUM = 3  # Standard: recent tool outputs, intermediate results
    LOW = 2  # Background: historical context, logs
    DISPOSABLE = 1  # Can prune freely: debug output, verbose logs


@dataclass
class PriorityItem:
    """An item in the priority queue."""

    content: str
    priority: Priority
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
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
        return (datetime.now() - self.created_at).total_seconds()

    @property
    def staleness_seconds(self) -> float:
        """Time since last access in seconds."""
        return (datetime.now() - self.last_accessed).total_seconds()

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

    def xǁContextPriorityQueueǁ__init____mutmut_orig(
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

    def xǁContextPriorityQueueǁ__init____mutmut_1(
        self,
        max_items: int = 1001,
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

    def xǁContextPriorityQueueǁ__init____mutmut_2(
        self,
        max_items: int = 1000,
        max_tokens: int = 56001,
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

    def xǁContextPriorityQueueǁ__init____mutmut_3(
        self,
        max_items: int = 1000,
        max_tokens: int = 56000,
        decay_enabled: bool = False,
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

    def xǁContextPriorityQueueǁ__init____mutmut_4(
        self,
        max_items: int = 1000,
        max_tokens: int = 56000,
        decay_enabled: bool = True,
        auto_prune: bool = False,
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

    def xǁContextPriorityQueueǁ__init____mutmut_5(
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
        self.max_items = None
        self.max_tokens = max_tokens
        self.decay_enabled = decay_enabled
        self.auto_prune = auto_prune

        self._items: list[PriorityItem] = []
        self._token_count = 0
        self._item_index: dict[str, int] = {}  # content_hash -> heap index

    def xǁContextPriorityQueueǁ__init____mutmut_6(
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
        self.max_tokens = None
        self.decay_enabled = decay_enabled
        self.auto_prune = auto_prune

        self._items: list[PriorityItem] = []
        self._token_count = 0
        self._item_index: dict[str, int] = {}  # content_hash -> heap index

    def xǁContextPriorityQueueǁ__init____mutmut_7(
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
        self.decay_enabled = None
        self.auto_prune = auto_prune

        self._items: list[PriorityItem] = []
        self._token_count = 0
        self._item_index: dict[str, int] = {}  # content_hash -> heap index

    def xǁContextPriorityQueueǁ__init____mutmut_8(
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
        self.auto_prune = None

        self._items: list[PriorityItem] = []
        self._token_count = 0
        self._item_index: dict[str, int] = {}  # content_hash -> heap index

    def xǁContextPriorityQueueǁ__init____mutmut_9(
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

        self._items: list[PriorityItem] = None
        self._token_count = 0
        self._item_index: dict[str, int] = {}  # content_hash -> heap index

    def xǁContextPriorityQueueǁ__init____mutmut_10(
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
        self._token_count = None
        self._item_index: dict[str, int] = {}  # content_hash -> heap index

    def xǁContextPriorityQueueǁ__init____mutmut_11(
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
        self._token_count = 1
        self._item_index: dict[str, int] = {}  # content_hash -> heap index

    def xǁContextPriorityQueueǁ__init____mutmut_12(
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
        self._item_index: dict[str, int] = None  # content_hash -> heap index
    
    xǁContextPriorityQueueǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextPriorityQueueǁ__init____mutmut_1': xǁContextPriorityQueueǁ__init____mutmut_1, 
        'xǁContextPriorityQueueǁ__init____mutmut_2': xǁContextPriorityQueueǁ__init____mutmut_2, 
        'xǁContextPriorityQueueǁ__init____mutmut_3': xǁContextPriorityQueueǁ__init____mutmut_3, 
        'xǁContextPriorityQueueǁ__init____mutmut_4': xǁContextPriorityQueueǁ__init____mutmut_4, 
        'xǁContextPriorityQueueǁ__init____mutmut_5': xǁContextPriorityQueueǁ__init____mutmut_5, 
        'xǁContextPriorityQueueǁ__init____mutmut_6': xǁContextPriorityQueueǁ__init____mutmut_6, 
        'xǁContextPriorityQueueǁ__init____mutmut_7': xǁContextPriorityQueueǁ__init____mutmut_7, 
        'xǁContextPriorityQueueǁ__init____mutmut_8': xǁContextPriorityQueueǁ__init____mutmut_8, 
        'xǁContextPriorityQueueǁ__init____mutmut_9': xǁContextPriorityQueueǁ__init____mutmut_9, 
        'xǁContextPriorityQueueǁ__init____mutmut_10': xǁContextPriorityQueueǁ__init____mutmut_10, 
        'xǁContextPriorityQueueǁ__init____mutmut_11': xǁContextPriorityQueueǁ__init____mutmut_11, 
        'xǁContextPriorityQueueǁ__init____mutmut_12': xǁContextPriorityQueueǁ__init____mutmut_12
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextPriorityQueueǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁContextPriorityQueueǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁContextPriorityQueueǁ__init____mutmut_orig)
    xǁContextPriorityQueueǁ__init____mutmut_orig.__name__ = 'xǁContextPriorityQueueǁ__init__'

    def xǁContextPriorityQueueǁpush__mutmut_orig(
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

    def xǁContextPriorityQueueǁpush__mutmut_1(
        self,
        content: str,
        priority: Priority = Priority.MEDIUM,
        source: str = "XXXX",
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

    def xǁContextPriorityQueueǁpush__mutmut_2(
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
        token_count = None

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

    def xǁContextPriorityQueueǁpush__mutmut_3(
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
        token_count = len(content) // 4 - 1

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

    def xǁContextPriorityQueueǁpush__mutmut_4(
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
        token_count = len(content) / 4 + 1

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

    def xǁContextPriorityQueueǁpush__mutmut_5(
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
        token_count = len(content) // 5 + 1

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

    def xǁContextPriorityQueueǁpush__mutmut_6(
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
        token_count = len(content) // 4 + 2

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

    def xǁContextPriorityQueueǁpush__mutmut_7(
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
                len(self._items) >= self.max_items and self._token_count + token_count > self.max_tokens
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

    def xǁContextPriorityQueueǁpush__mutmut_8(
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
                len(self._items) > self.max_items
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

    def xǁContextPriorityQueueǁpush__mutmut_9(
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
                or self._token_count - token_count > self.max_tokens
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

    def xǁContextPriorityQueueǁpush__mutmut_10(
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
                or self._token_count + token_count >= self.max_tokens
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

    def xǁContextPriorityQueueǁpush__mutmut_11(
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
                if self._prune_lowest():
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

    def xǁContextPriorityQueueǁpush__mutmut_12(
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
                    return

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

    def xǁContextPriorityQueueǁpush__mutmut_13(
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
        if len(self._items) > self.max_items:
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

    def xǁContextPriorityQueueǁpush__mutmut_14(
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
            return True
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

    def xǁContextPriorityQueueǁpush__mutmut_15(
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
        if self._token_count - token_count > self.max_tokens:
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

    def xǁContextPriorityQueueǁpush__mutmut_16(
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
        if self._token_count + token_count >= self.max_tokens:
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

    def xǁContextPriorityQueueǁpush__mutmut_17(
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
            return True

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

    def xǁContextPriorityQueueǁpush__mutmut_18(
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

        item = None

        heapq.heappush(self._items, item)
        self._token_count += token_count

        return True

    def xǁContextPriorityQueueǁpush__mutmut_19(
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
            content=None,
            priority=priority,
            token_count=token_count,
            source=source,
            tags=tags or [],
            metadata=metadata or {},
        )

        heapq.heappush(self._items, item)
        self._token_count += token_count

        return True

    def xǁContextPriorityQueueǁpush__mutmut_20(
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
            priority=None,
            token_count=token_count,
            source=source,
            tags=tags or [],
            metadata=metadata or {},
        )

        heapq.heappush(self._items, item)
        self._token_count += token_count

        return True

    def xǁContextPriorityQueueǁpush__mutmut_21(
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
            token_count=None,
            source=source,
            tags=tags or [],
            metadata=metadata or {},
        )

        heapq.heappush(self._items, item)
        self._token_count += token_count

        return True

    def xǁContextPriorityQueueǁpush__mutmut_22(
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
            source=None,
            tags=tags or [],
            metadata=metadata or {},
        )

        heapq.heappush(self._items, item)
        self._token_count += token_count

        return True

    def xǁContextPriorityQueueǁpush__mutmut_23(
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
            tags=None,
            metadata=metadata or {},
        )

        heapq.heappush(self._items, item)
        self._token_count += token_count

        return True

    def xǁContextPriorityQueueǁpush__mutmut_24(
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
            metadata=None,
        )

        heapq.heappush(self._items, item)
        self._token_count += token_count

        return True

    def xǁContextPriorityQueueǁpush__mutmut_25(
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
            priority=priority,
            token_count=token_count,
            source=source,
            tags=tags or [],
            metadata=metadata or {},
        )

        heapq.heappush(self._items, item)
        self._token_count += token_count

        return True

    def xǁContextPriorityQueueǁpush__mutmut_26(
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
            token_count=token_count,
            source=source,
            tags=tags or [],
            metadata=metadata or {},
        )

        heapq.heappush(self._items, item)
        self._token_count += token_count

        return True

    def xǁContextPriorityQueueǁpush__mutmut_27(
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
            source=source,
            tags=tags or [],
            metadata=metadata or {},
        )

        heapq.heappush(self._items, item)
        self._token_count += token_count

        return True

    def xǁContextPriorityQueueǁpush__mutmut_28(
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
            tags=tags or [],
            metadata=metadata or {},
        )

        heapq.heappush(self._items, item)
        self._token_count += token_count

        return True

    def xǁContextPriorityQueueǁpush__mutmut_29(
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
            metadata=metadata or {},
        )

        heapq.heappush(self._items, item)
        self._token_count += token_count

        return True

    def xǁContextPriorityQueueǁpush__mutmut_30(
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
            )

        heapq.heappush(self._items, item)
        self._token_count += token_count

        return True

    def xǁContextPriorityQueueǁpush__mutmut_31(
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
            tags=tags and [],
            metadata=metadata or {},
        )

        heapq.heappush(self._items, item)
        self._token_count += token_count

        return True

    def xǁContextPriorityQueueǁpush__mutmut_32(
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
            metadata=metadata and {},
        )

        heapq.heappush(self._items, item)
        self._token_count += token_count

        return True

    def xǁContextPriorityQueueǁpush__mutmut_33(
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

        heapq.heappush(None, item)
        self._token_count += token_count

        return True

    def xǁContextPriorityQueueǁpush__mutmut_34(
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

        heapq.heappush(self._items, None)
        self._token_count += token_count

        return True

    def xǁContextPriorityQueueǁpush__mutmut_35(
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

        heapq.heappush(item)
        self._token_count += token_count

        return True

    def xǁContextPriorityQueueǁpush__mutmut_36(
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

        heapq.heappush(self._items, )
        self._token_count += token_count

        return True

    def xǁContextPriorityQueueǁpush__mutmut_37(
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
        self._token_count = token_count

        return True

    def xǁContextPriorityQueueǁpush__mutmut_38(
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
        self._token_count -= token_count

        return True

    def xǁContextPriorityQueueǁpush__mutmut_39(
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

        return False
    
    xǁContextPriorityQueueǁpush__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextPriorityQueueǁpush__mutmut_1': xǁContextPriorityQueueǁpush__mutmut_1, 
        'xǁContextPriorityQueueǁpush__mutmut_2': xǁContextPriorityQueueǁpush__mutmut_2, 
        'xǁContextPriorityQueueǁpush__mutmut_3': xǁContextPriorityQueueǁpush__mutmut_3, 
        'xǁContextPriorityQueueǁpush__mutmut_4': xǁContextPriorityQueueǁpush__mutmut_4, 
        'xǁContextPriorityQueueǁpush__mutmut_5': xǁContextPriorityQueueǁpush__mutmut_5, 
        'xǁContextPriorityQueueǁpush__mutmut_6': xǁContextPriorityQueueǁpush__mutmut_6, 
        'xǁContextPriorityQueueǁpush__mutmut_7': xǁContextPriorityQueueǁpush__mutmut_7, 
        'xǁContextPriorityQueueǁpush__mutmut_8': xǁContextPriorityQueueǁpush__mutmut_8, 
        'xǁContextPriorityQueueǁpush__mutmut_9': xǁContextPriorityQueueǁpush__mutmut_9, 
        'xǁContextPriorityQueueǁpush__mutmut_10': xǁContextPriorityQueueǁpush__mutmut_10, 
        'xǁContextPriorityQueueǁpush__mutmut_11': xǁContextPriorityQueueǁpush__mutmut_11, 
        'xǁContextPriorityQueueǁpush__mutmut_12': xǁContextPriorityQueueǁpush__mutmut_12, 
        'xǁContextPriorityQueueǁpush__mutmut_13': xǁContextPriorityQueueǁpush__mutmut_13, 
        'xǁContextPriorityQueueǁpush__mutmut_14': xǁContextPriorityQueueǁpush__mutmut_14, 
        'xǁContextPriorityQueueǁpush__mutmut_15': xǁContextPriorityQueueǁpush__mutmut_15, 
        'xǁContextPriorityQueueǁpush__mutmut_16': xǁContextPriorityQueueǁpush__mutmut_16, 
        'xǁContextPriorityQueueǁpush__mutmut_17': xǁContextPriorityQueueǁpush__mutmut_17, 
        'xǁContextPriorityQueueǁpush__mutmut_18': xǁContextPriorityQueueǁpush__mutmut_18, 
        'xǁContextPriorityQueueǁpush__mutmut_19': xǁContextPriorityQueueǁpush__mutmut_19, 
        'xǁContextPriorityQueueǁpush__mutmut_20': xǁContextPriorityQueueǁpush__mutmut_20, 
        'xǁContextPriorityQueueǁpush__mutmut_21': xǁContextPriorityQueueǁpush__mutmut_21, 
        'xǁContextPriorityQueueǁpush__mutmut_22': xǁContextPriorityQueueǁpush__mutmut_22, 
        'xǁContextPriorityQueueǁpush__mutmut_23': xǁContextPriorityQueueǁpush__mutmut_23, 
        'xǁContextPriorityQueueǁpush__mutmut_24': xǁContextPriorityQueueǁpush__mutmut_24, 
        'xǁContextPriorityQueueǁpush__mutmut_25': xǁContextPriorityQueueǁpush__mutmut_25, 
        'xǁContextPriorityQueueǁpush__mutmut_26': xǁContextPriorityQueueǁpush__mutmut_26, 
        'xǁContextPriorityQueueǁpush__mutmut_27': xǁContextPriorityQueueǁpush__mutmut_27, 
        'xǁContextPriorityQueueǁpush__mutmut_28': xǁContextPriorityQueueǁpush__mutmut_28, 
        'xǁContextPriorityQueueǁpush__mutmut_29': xǁContextPriorityQueueǁpush__mutmut_29, 
        'xǁContextPriorityQueueǁpush__mutmut_30': xǁContextPriorityQueueǁpush__mutmut_30, 
        'xǁContextPriorityQueueǁpush__mutmut_31': xǁContextPriorityQueueǁpush__mutmut_31, 
        'xǁContextPriorityQueueǁpush__mutmut_32': xǁContextPriorityQueueǁpush__mutmut_32, 
        'xǁContextPriorityQueueǁpush__mutmut_33': xǁContextPriorityQueueǁpush__mutmut_33, 
        'xǁContextPriorityQueueǁpush__mutmut_34': xǁContextPriorityQueueǁpush__mutmut_34, 
        'xǁContextPriorityQueueǁpush__mutmut_35': xǁContextPriorityQueueǁpush__mutmut_35, 
        'xǁContextPriorityQueueǁpush__mutmut_36': xǁContextPriorityQueueǁpush__mutmut_36, 
        'xǁContextPriorityQueueǁpush__mutmut_37': xǁContextPriorityQueueǁpush__mutmut_37, 
        'xǁContextPriorityQueueǁpush__mutmut_38': xǁContextPriorityQueueǁpush__mutmut_38, 
        'xǁContextPriorityQueueǁpush__mutmut_39': xǁContextPriorityQueueǁpush__mutmut_39
    }
    
    def push(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextPriorityQueueǁpush__mutmut_orig"), object.__getattribute__(self, "xǁContextPriorityQueueǁpush__mutmut_mutants"), args, kwargs, self)
        return result 
    
    push.__signature__ = _mutmut_signature(xǁContextPriorityQueueǁpush__mutmut_orig)
    xǁContextPriorityQueueǁpush__mutmut_orig.__name__ = 'xǁContextPriorityQueueǁpush'

    def xǁContextPriorityQueueǁpop__mutmut_orig(self) -> Optional[PriorityItem]:
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

    def xǁContextPriorityQueueǁpop__mutmut_1(self) -> Optional[PriorityItem]:
        """
        Remove and return lowest priority item.

        Returns:
            Lowest priority item or None if empty
        """
        if self._items:
            return None

        item = heapq.heappop(self._items)
        self._token_count -= item.token_count
        return item

    def xǁContextPriorityQueueǁpop__mutmut_2(self) -> Optional[PriorityItem]:
        """
        Remove and return lowest priority item.

        Returns:
            Lowest priority item or None if empty
        """
        if not self._items:
            return None

        item = None
        self._token_count -= item.token_count
        return item

    def xǁContextPriorityQueueǁpop__mutmut_3(self) -> Optional[PriorityItem]:
        """
        Remove and return lowest priority item.

        Returns:
            Lowest priority item or None if empty
        """
        if not self._items:
            return None

        item = heapq.heappop(None)
        self._token_count -= item.token_count
        return item

    def xǁContextPriorityQueueǁpop__mutmut_4(self) -> Optional[PriorityItem]:
        """
        Remove and return lowest priority item.

        Returns:
            Lowest priority item or None if empty
        """
        if not self._items:
            return None

        item = heapq.heappop(self._items)
        self._token_count = item.token_count
        return item

    def xǁContextPriorityQueueǁpop__mutmut_5(self) -> Optional[PriorityItem]:
        """
        Remove and return lowest priority item.

        Returns:
            Lowest priority item or None if empty
        """
        if not self._items:
            return None

        item = heapq.heappop(self._items)
        self._token_count += item.token_count
        return item
    
    xǁContextPriorityQueueǁpop__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextPriorityQueueǁpop__mutmut_1': xǁContextPriorityQueueǁpop__mutmut_1, 
        'xǁContextPriorityQueueǁpop__mutmut_2': xǁContextPriorityQueueǁpop__mutmut_2, 
        'xǁContextPriorityQueueǁpop__mutmut_3': xǁContextPriorityQueueǁpop__mutmut_3, 
        'xǁContextPriorityQueueǁpop__mutmut_4': xǁContextPriorityQueueǁpop__mutmut_4, 
        'xǁContextPriorityQueueǁpop__mutmut_5': xǁContextPriorityQueueǁpop__mutmut_5
    }
    
    def pop(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextPriorityQueueǁpop__mutmut_orig"), object.__getattribute__(self, "xǁContextPriorityQueueǁpop__mutmut_mutants"), args, kwargs, self)
        return result 
    
    pop.__signature__ = _mutmut_signature(xǁContextPriorityQueueǁpop__mutmut_orig)
    xǁContextPriorityQueueǁpop__mutmut_orig.__name__ = 'xǁContextPriorityQueueǁpop'

    def xǁContextPriorityQueueǁpop_highest__mutmut_orig(self) -> Optional[PriorityItem]:
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

    def xǁContextPriorityQueueǁpop_highest__mutmut_1(self) -> Optional[PriorityItem]:
        """
        Remove and return highest priority item.

        Returns:
            Highest priority item or None if empty
        """
        if self._items:
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

    def xǁContextPriorityQueueǁpop_highest__mutmut_2(self) -> Optional[PriorityItem]:
        """
        Remove and return highest priority item.

        Returns:
            Highest priority item or None if empty
        """
        if not self._items:
            return None

        # Find highest priority item
        max_idx = None
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

    def xǁContextPriorityQueueǁpop_highest__mutmut_3(self) -> Optional[PriorityItem]:
        """
        Remove and return highest priority item.

        Returns:
            Highest priority item or None if empty
        """
        if not self._items:
            return None

        # Find highest priority item
        max_idx = 1
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

    def xǁContextPriorityQueueǁpop_highest__mutmut_4(self) -> Optional[PriorityItem]:
        """
        Remove and return highest priority item.

        Returns:
            Highest priority item or None if empty
        """
        if not self._items:
            return None

        # Find highest priority item
        max_idx = 0
        max_priority = None

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

    def xǁContextPriorityQueueǁpop_highest__mutmut_5(self) -> Optional[PriorityItem]:
        """
        Remove and return highest priority item.

        Returns:
            Highest priority item or None if empty
        """
        if not self._items:
            return None

        # Find highest priority item
        max_idx = 0
        max_priority = self._items[1].effective_priority

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

    def xǁContextPriorityQueueǁpop_highest__mutmut_6(self) -> Optional[PriorityItem]:
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

        for i, item in enumerate(None):
            if item.effective_priority > max_priority:
                max_priority = item.effective_priority
                max_idx = i

        item = self._items[max_idx]
        self._items[max_idx] = self._items[-1]
        self._items.pop()
        heapq.heapify(self._items)

        self._token_count -= item.token_count
        return item

    def xǁContextPriorityQueueǁpop_highest__mutmut_7(self) -> Optional[PriorityItem]:
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
            if item.effective_priority >= max_priority:
                max_priority = item.effective_priority
                max_idx = i

        item = self._items[max_idx]
        self._items[max_idx] = self._items[-1]
        self._items.pop()
        heapq.heapify(self._items)

        self._token_count -= item.token_count
        return item

    def xǁContextPriorityQueueǁpop_highest__mutmut_8(self) -> Optional[PriorityItem]:
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
                max_priority = None
                max_idx = i

        item = self._items[max_idx]
        self._items[max_idx] = self._items[-1]
        self._items.pop()
        heapq.heapify(self._items)

        self._token_count -= item.token_count
        return item

    def xǁContextPriorityQueueǁpop_highest__mutmut_9(self) -> Optional[PriorityItem]:
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
                max_idx = None

        item = self._items[max_idx]
        self._items[max_idx] = self._items[-1]
        self._items.pop()
        heapq.heapify(self._items)

        self._token_count -= item.token_count
        return item

    def xǁContextPriorityQueueǁpop_highest__mutmut_10(self) -> Optional[PriorityItem]:
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

        item = None
        self._items[max_idx] = self._items[-1]
        self._items.pop()
        heapq.heapify(self._items)

        self._token_count -= item.token_count
        return item

    def xǁContextPriorityQueueǁpop_highest__mutmut_11(self) -> Optional[PriorityItem]:
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
        self._items[max_idx] = None
        self._items.pop()
        heapq.heapify(self._items)

        self._token_count -= item.token_count
        return item

    def xǁContextPriorityQueueǁpop_highest__mutmut_12(self) -> Optional[PriorityItem]:
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
        self._items[max_idx] = self._items[+1]
        self._items.pop()
        heapq.heapify(self._items)

        self._token_count -= item.token_count
        return item

    def xǁContextPriorityQueueǁpop_highest__mutmut_13(self) -> Optional[PriorityItem]:
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
        self._items[max_idx] = self._items[-2]
        self._items.pop()
        heapq.heapify(self._items)

        self._token_count -= item.token_count
        return item

    def xǁContextPriorityQueueǁpop_highest__mutmut_14(self) -> Optional[PriorityItem]:
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
        heapq.heapify(None)

        self._token_count -= item.token_count
        return item

    def xǁContextPriorityQueueǁpop_highest__mutmut_15(self) -> Optional[PriorityItem]:
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

        self._token_count = item.token_count
        return item

    def xǁContextPriorityQueueǁpop_highest__mutmut_16(self) -> Optional[PriorityItem]:
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

        self._token_count += item.token_count
        return item
    
    xǁContextPriorityQueueǁpop_highest__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextPriorityQueueǁpop_highest__mutmut_1': xǁContextPriorityQueueǁpop_highest__mutmut_1, 
        'xǁContextPriorityQueueǁpop_highest__mutmut_2': xǁContextPriorityQueueǁpop_highest__mutmut_2, 
        'xǁContextPriorityQueueǁpop_highest__mutmut_3': xǁContextPriorityQueueǁpop_highest__mutmut_3, 
        'xǁContextPriorityQueueǁpop_highest__mutmut_4': xǁContextPriorityQueueǁpop_highest__mutmut_4, 
        'xǁContextPriorityQueueǁpop_highest__mutmut_5': xǁContextPriorityQueueǁpop_highest__mutmut_5, 
        'xǁContextPriorityQueueǁpop_highest__mutmut_6': xǁContextPriorityQueueǁpop_highest__mutmut_6, 
        'xǁContextPriorityQueueǁpop_highest__mutmut_7': xǁContextPriorityQueueǁpop_highest__mutmut_7, 
        'xǁContextPriorityQueueǁpop_highest__mutmut_8': xǁContextPriorityQueueǁpop_highest__mutmut_8, 
        'xǁContextPriorityQueueǁpop_highest__mutmut_9': xǁContextPriorityQueueǁpop_highest__mutmut_9, 
        'xǁContextPriorityQueueǁpop_highest__mutmut_10': xǁContextPriorityQueueǁpop_highest__mutmut_10, 
        'xǁContextPriorityQueueǁpop_highest__mutmut_11': xǁContextPriorityQueueǁpop_highest__mutmut_11, 
        'xǁContextPriorityQueueǁpop_highest__mutmut_12': xǁContextPriorityQueueǁpop_highest__mutmut_12, 
        'xǁContextPriorityQueueǁpop_highest__mutmut_13': xǁContextPriorityQueueǁpop_highest__mutmut_13, 
        'xǁContextPriorityQueueǁpop_highest__mutmut_14': xǁContextPriorityQueueǁpop_highest__mutmut_14, 
        'xǁContextPriorityQueueǁpop_highest__mutmut_15': xǁContextPriorityQueueǁpop_highest__mutmut_15, 
        'xǁContextPriorityQueueǁpop_highest__mutmut_16': xǁContextPriorityQueueǁpop_highest__mutmut_16
    }
    
    def pop_highest(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextPriorityQueueǁpop_highest__mutmut_orig"), object.__getattribute__(self, "xǁContextPriorityQueueǁpop_highest__mutmut_mutants"), args, kwargs, self)
        return result 
    
    pop_highest.__signature__ = _mutmut_signature(xǁContextPriorityQueueǁpop_highest__mutmut_orig)
    xǁContextPriorityQueueǁpop_highest__mutmut_orig.__name__ = 'xǁContextPriorityQueueǁpop_highest'

    def xǁContextPriorityQueueǁpeek_lowest__mutmut_orig(self) -> Optional[PriorityItem]:
        """Peek at lowest priority item without removing."""
        if not self._items:
            return None
        return self._items[0]

    def xǁContextPriorityQueueǁpeek_lowest__mutmut_1(self) -> Optional[PriorityItem]:
        """Peek at lowest priority item without removing."""
        if self._items:
            return None
        return self._items[0]

    def xǁContextPriorityQueueǁpeek_lowest__mutmut_2(self) -> Optional[PriorityItem]:
        """Peek at lowest priority item without removing."""
        if not self._items:
            return None
        return self._items[1]
    
    xǁContextPriorityQueueǁpeek_lowest__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextPriorityQueueǁpeek_lowest__mutmut_1': xǁContextPriorityQueueǁpeek_lowest__mutmut_1, 
        'xǁContextPriorityQueueǁpeek_lowest__mutmut_2': xǁContextPriorityQueueǁpeek_lowest__mutmut_2
    }
    
    def peek_lowest(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextPriorityQueueǁpeek_lowest__mutmut_orig"), object.__getattribute__(self, "xǁContextPriorityQueueǁpeek_lowest__mutmut_mutants"), args, kwargs, self)
        return result 
    
    peek_lowest.__signature__ = _mutmut_signature(xǁContextPriorityQueueǁpeek_lowest__mutmut_orig)
    xǁContextPriorityQueueǁpeek_lowest__mutmut_orig.__name__ = 'xǁContextPriorityQueueǁpeek_lowest'

    def xǁContextPriorityQueueǁpeek_highest__mutmut_orig(self) -> Optional[PriorityItem]:
        """Peek at highest priority item without removing."""
        if not self._items:
            return None
        return max(self._items, key=lambda x: x.effective_priority)

    def xǁContextPriorityQueueǁpeek_highest__mutmut_1(self) -> Optional[PriorityItem]:
        """Peek at highest priority item without removing."""
        if self._items:
            return None
        return max(self._items, key=lambda x: x.effective_priority)

    def xǁContextPriorityQueueǁpeek_highest__mutmut_2(self) -> Optional[PriorityItem]:
        """Peek at highest priority item without removing."""
        if not self._items:
            return None
        return max(None, key=lambda x: x.effective_priority)

    def xǁContextPriorityQueueǁpeek_highest__mutmut_3(self) -> Optional[PriorityItem]:
        """Peek at highest priority item without removing."""
        if not self._items:
            return None
        return max(self._items, key=None)

    def xǁContextPriorityQueueǁpeek_highest__mutmut_4(self) -> Optional[PriorityItem]:
        """Peek at highest priority item without removing."""
        if not self._items:
            return None
        return max(key=lambda x: x.effective_priority)

    def xǁContextPriorityQueueǁpeek_highest__mutmut_5(self) -> Optional[PriorityItem]:
        """Peek at highest priority item without removing."""
        if not self._items:
            return None
        return max(self._items, )

    def xǁContextPriorityQueueǁpeek_highest__mutmut_6(self) -> Optional[PriorityItem]:
        """Peek at highest priority item without removing."""
        if not self._items:
            return None
        return max(self._items, key=lambda x: None)
    
    xǁContextPriorityQueueǁpeek_highest__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextPriorityQueueǁpeek_highest__mutmut_1': xǁContextPriorityQueueǁpeek_highest__mutmut_1, 
        'xǁContextPriorityQueueǁpeek_highest__mutmut_2': xǁContextPriorityQueueǁpeek_highest__mutmut_2, 
        'xǁContextPriorityQueueǁpeek_highest__mutmut_3': xǁContextPriorityQueueǁpeek_highest__mutmut_3, 
        'xǁContextPriorityQueueǁpeek_highest__mutmut_4': xǁContextPriorityQueueǁpeek_highest__mutmut_4, 
        'xǁContextPriorityQueueǁpeek_highest__mutmut_5': xǁContextPriorityQueueǁpeek_highest__mutmut_5, 
        'xǁContextPriorityQueueǁpeek_highest__mutmut_6': xǁContextPriorityQueueǁpeek_highest__mutmut_6
    }
    
    def peek_highest(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextPriorityQueueǁpeek_highest__mutmut_orig"), object.__getattribute__(self, "xǁContextPriorityQueueǁpeek_highest__mutmut_mutants"), args, kwargs, self)
        return result 
    
    peek_highest.__signature__ = _mutmut_signature(xǁContextPriorityQueueǁpeek_highest__mutmut_orig)
    xǁContextPriorityQueueǁpeek_highest__mutmut_orig.__name__ = 'xǁContextPriorityQueueǁpeek_highest'

    def xǁContextPriorityQueueǁget_all_by_priority__mutmut_orig(
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

    def xǁContextPriorityQueueǁget_all_by_priority__mutmut_1(
        self, min_priority: Priority = Priority.DISPOSABLE
    ) -> list[PriorityItem]:
        """
        Get all items at or above minimum priority.

        Args:
            min_priority: Minimum priority level

        Returns:
            list of items sorted by effective priority (highest first)
        """
        filtered = None
        return sorted(filtered, key=lambda x: x.effective_priority, reverse=True)

    def xǁContextPriorityQueueǁget_all_by_priority__mutmut_2(
        self, min_priority: Priority = Priority.DISPOSABLE
    ) -> list[PriorityItem]:
        """
        Get all items at or above minimum priority.

        Args:
            min_priority: Minimum priority level

        Returns:
            list of items sorted by effective priority (highest first)
        """
        filtered = [item for item in self._items if item.priority > min_priority]
        return sorted(filtered, key=lambda x: x.effective_priority, reverse=True)

    def xǁContextPriorityQueueǁget_all_by_priority__mutmut_3(
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
        return sorted(None, key=lambda x: x.effective_priority, reverse=True)

    def xǁContextPriorityQueueǁget_all_by_priority__mutmut_4(
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
        return sorted(filtered, key=None, reverse=True)

    def xǁContextPriorityQueueǁget_all_by_priority__mutmut_5(
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
        return sorted(filtered, key=lambda x: x.effective_priority, reverse=None)

    def xǁContextPriorityQueueǁget_all_by_priority__mutmut_6(
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
        return sorted(key=lambda x: x.effective_priority, reverse=True)

    def xǁContextPriorityQueueǁget_all_by_priority__mutmut_7(
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
        return sorted(filtered, reverse=True)

    def xǁContextPriorityQueueǁget_all_by_priority__mutmut_8(
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
        return sorted(filtered, key=lambda x: x.effective_priority, )

    def xǁContextPriorityQueueǁget_all_by_priority__mutmut_9(
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
        return sorted(filtered, key=lambda x: None, reverse=True)

    def xǁContextPriorityQueueǁget_all_by_priority__mutmut_10(
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
        return sorted(filtered, key=lambda x: x.effective_priority, reverse=False)
    
    xǁContextPriorityQueueǁget_all_by_priority__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextPriorityQueueǁget_all_by_priority__mutmut_1': xǁContextPriorityQueueǁget_all_by_priority__mutmut_1, 
        'xǁContextPriorityQueueǁget_all_by_priority__mutmut_2': xǁContextPriorityQueueǁget_all_by_priority__mutmut_2, 
        'xǁContextPriorityQueueǁget_all_by_priority__mutmut_3': xǁContextPriorityQueueǁget_all_by_priority__mutmut_3, 
        'xǁContextPriorityQueueǁget_all_by_priority__mutmut_4': xǁContextPriorityQueueǁget_all_by_priority__mutmut_4, 
        'xǁContextPriorityQueueǁget_all_by_priority__mutmut_5': xǁContextPriorityQueueǁget_all_by_priority__mutmut_5, 
        'xǁContextPriorityQueueǁget_all_by_priority__mutmut_6': xǁContextPriorityQueueǁget_all_by_priority__mutmut_6, 
        'xǁContextPriorityQueueǁget_all_by_priority__mutmut_7': xǁContextPriorityQueueǁget_all_by_priority__mutmut_7, 
        'xǁContextPriorityQueueǁget_all_by_priority__mutmut_8': xǁContextPriorityQueueǁget_all_by_priority__mutmut_8, 
        'xǁContextPriorityQueueǁget_all_by_priority__mutmut_9': xǁContextPriorityQueueǁget_all_by_priority__mutmut_9, 
        'xǁContextPriorityQueueǁget_all_by_priority__mutmut_10': xǁContextPriorityQueueǁget_all_by_priority__mutmut_10
    }
    
    def get_all_by_priority(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextPriorityQueueǁget_all_by_priority__mutmut_orig"), object.__getattribute__(self, "xǁContextPriorityQueueǁget_all_by_priority__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_all_by_priority.__signature__ = _mutmut_signature(xǁContextPriorityQueueǁget_all_by_priority__mutmut_orig)
    xǁContextPriorityQueueǁget_all_by_priority__mutmut_orig.__name__ = 'xǁContextPriorityQueueǁget_all_by_priority'

    def xǁContextPriorityQueueǁget_by_tags__mutmut_orig(self, tags: list[str]) -> list[PriorityItem]:
        """Get items matching any of the given tags."""
        tag_set = set(tags)
        return [item for item in self._items if tag_set & set(item.tags)]

    def xǁContextPriorityQueueǁget_by_tags__mutmut_1(self, tags: list[str]) -> list[PriorityItem]:
        """Get items matching any of the given tags."""
        tag_set = None
        return [item for item in self._items if tag_set & set(item.tags)]

    def xǁContextPriorityQueueǁget_by_tags__mutmut_2(self, tags: list[str]) -> list[PriorityItem]:
        """Get items matching any of the given tags."""
        tag_set = set(None)
        return [item for item in self._items if tag_set & set(item.tags)]

    def xǁContextPriorityQueueǁget_by_tags__mutmut_3(self, tags: list[str]) -> list[PriorityItem]:
        """Get items matching any of the given tags."""
        tag_set = set(tags)
        return [item for item in self._items if tag_set | set(item.tags)]

    def xǁContextPriorityQueueǁget_by_tags__mutmut_4(self, tags: list[str]) -> list[PriorityItem]:
        """Get items matching any of the given tags."""
        tag_set = set(tags)
        return [item for item in self._items if tag_set & set(None)]
    
    xǁContextPriorityQueueǁget_by_tags__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextPriorityQueueǁget_by_tags__mutmut_1': xǁContextPriorityQueueǁget_by_tags__mutmut_1, 
        'xǁContextPriorityQueueǁget_by_tags__mutmut_2': xǁContextPriorityQueueǁget_by_tags__mutmut_2, 
        'xǁContextPriorityQueueǁget_by_tags__mutmut_3': xǁContextPriorityQueueǁget_by_tags__mutmut_3, 
        'xǁContextPriorityQueueǁget_by_tags__mutmut_4': xǁContextPriorityQueueǁget_by_tags__mutmut_4
    }
    
    def get_by_tags(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextPriorityQueueǁget_by_tags__mutmut_orig"), object.__getattribute__(self, "xǁContextPriorityQueueǁget_by_tags__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_by_tags.__signature__ = _mutmut_signature(xǁContextPriorityQueueǁget_by_tags__mutmut_orig)
    xǁContextPriorityQueueǁget_by_tags__mutmut_orig.__name__ = 'xǁContextPriorityQueueǁget_by_tags'

    def xǁContextPriorityQueueǁprune_to_tokens__mutmut_orig(self, target_tokens: int) -> list[PriorityItem]:
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

    def xǁContextPriorityQueueǁprune_to_tokens__mutmut_1(self, target_tokens: int) -> list[PriorityItem]:
        """
        Prune queue until under target token count.

        Args:
            target_tokens: Target maximum tokens

        Returns:
            list of pruned items
        """
        pruned = None
        while self._token_count > target_tokens and self._items:
            item = self.pop()
            if item:
                pruned.append(item)
        return pruned

    def xǁContextPriorityQueueǁprune_to_tokens__mutmut_2(self, target_tokens: int) -> list[PriorityItem]:
        """
        Prune queue until under target token count.

        Args:
            target_tokens: Target maximum tokens

        Returns:
            list of pruned items
        """
        pruned = []
        while self._token_count > target_tokens or self._items:
            item = self.pop()
            if item:
                pruned.append(item)
        return pruned

    def xǁContextPriorityQueueǁprune_to_tokens__mutmut_3(self, target_tokens: int) -> list[PriorityItem]:
        """
        Prune queue until under target token count.

        Args:
            target_tokens: Target maximum tokens

        Returns:
            list of pruned items
        """
        pruned = []
        while self._token_count >= target_tokens and self._items:
            item = self.pop()
            if item:
                pruned.append(item)
        return pruned

    def xǁContextPriorityQueueǁprune_to_tokens__mutmut_4(self, target_tokens: int) -> list[PriorityItem]:
        """
        Prune queue until under target token count.

        Args:
            target_tokens: Target maximum tokens

        Returns:
            list of pruned items
        """
        pruned = []
        while self._token_count > target_tokens and self._items:
            item = None
            if item:
                pruned.append(item)
        return pruned

    def xǁContextPriorityQueueǁprune_to_tokens__mutmut_5(self, target_tokens: int) -> list[PriorityItem]:
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
                pruned.append(None)
        return pruned
    
    xǁContextPriorityQueueǁprune_to_tokens__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextPriorityQueueǁprune_to_tokens__mutmut_1': xǁContextPriorityQueueǁprune_to_tokens__mutmut_1, 
        'xǁContextPriorityQueueǁprune_to_tokens__mutmut_2': xǁContextPriorityQueueǁprune_to_tokens__mutmut_2, 
        'xǁContextPriorityQueueǁprune_to_tokens__mutmut_3': xǁContextPriorityQueueǁprune_to_tokens__mutmut_3, 
        'xǁContextPriorityQueueǁprune_to_tokens__mutmut_4': xǁContextPriorityQueueǁprune_to_tokens__mutmut_4, 
        'xǁContextPriorityQueueǁprune_to_tokens__mutmut_5': xǁContextPriorityQueueǁprune_to_tokens__mutmut_5
    }
    
    def prune_to_tokens(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextPriorityQueueǁprune_to_tokens__mutmut_orig"), object.__getattribute__(self, "xǁContextPriorityQueueǁprune_to_tokens__mutmut_mutants"), args, kwargs, self)
        return result 
    
    prune_to_tokens.__signature__ = _mutmut_signature(xǁContextPriorityQueueǁprune_to_tokens__mutmut_orig)
    xǁContextPriorityQueueǁprune_to_tokens__mutmut_orig.__name__ = 'xǁContextPriorityQueueǁprune_to_tokens'

    def xǁContextPriorityQueueǁprune_below_priority__mutmut_orig(self, min_priority: Priority) -> list[PriorityItem]:
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

    def xǁContextPriorityQueueǁprune_below_priority__mutmut_1(self, min_priority: Priority) -> list[PriorityItem]:
        """
        Remove all items below minimum priority.

        Args:
            min_priority: Minimum priority to keep

        Returns:
            list of pruned items
        """
        keep = None
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

    def xǁContextPriorityQueueǁprune_below_priority__mutmut_2(self, min_priority: Priority) -> list[PriorityItem]:
        """
        Remove all items below minimum priority.

        Args:
            min_priority: Minimum priority to keep

        Returns:
            list of pruned items
        """
        keep = []
        pruned = None

        for item in self._items:
            if item.priority >= min_priority:
                keep.append(item)
            else:
                pruned.append(item)
                self._token_count -= item.token_count

        self._items = keep
        heapq.heapify(self._items)

        return pruned

    def xǁContextPriorityQueueǁprune_below_priority__mutmut_3(self, min_priority: Priority) -> list[PriorityItem]:
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
            if item.priority > min_priority:
                keep.append(item)
            else:
                pruned.append(item)
                self._token_count -= item.token_count

        self._items = keep
        heapq.heapify(self._items)

        return pruned

    def xǁContextPriorityQueueǁprune_below_priority__mutmut_4(self, min_priority: Priority) -> list[PriorityItem]:
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
                keep.append(None)
            else:
                pruned.append(item)
                self._token_count -= item.token_count

        self._items = keep
        heapq.heapify(self._items)

        return pruned

    def xǁContextPriorityQueueǁprune_below_priority__mutmut_5(self, min_priority: Priority) -> list[PriorityItem]:
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
                pruned.append(None)
                self._token_count -= item.token_count

        self._items = keep
        heapq.heapify(self._items)

        return pruned

    def xǁContextPriorityQueueǁprune_below_priority__mutmut_6(self, min_priority: Priority) -> list[PriorityItem]:
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
                self._token_count = item.token_count

        self._items = keep
        heapq.heapify(self._items)

        return pruned

    def xǁContextPriorityQueueǁprune_below_priority__mutmut_7(self, min_priority: Priority) -> list[PriorityItem]:
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
                self._token_count += item.token_count

        self._items = keep
        heapq.heapify(self._items)

        return pruned

    def xǁContextPriorityQueueǁprune_below_priority__mutmut_8(self, min_priority: Priority) -> list[PriorityItem]:
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

        self._items = None
        heapq.heapify(self._items)

        return pruned

    def xǁContextPriorityQueueǁprune_below_priority__mutmut_9(self, min_priority: Priority) -> list[PriorityItem]:
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
        heapq.heapify(None)

        return pruned
    
    xǁContextPriorityQueueǁprune_below_priority__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextPriorityQueueǁprune_below_priority__mutmut_1': xǁContextPriorityQueueǁprune_below_priority__mutmut_1, 
        'xǁContextPriorityQueueǁprune_below_priority__mutmut_2': xǁContextPriorityQueueǁprune_below_priority__mutmut_2, 
        'xǁContextPriorityQueueǁprune_below_priority__mutmut_3': xǁContextPriorityQueueǁprune_below_priority__mutmut_3, 
        'xǁContextPriorityQueueǁprune_below_priority__mutmut_4': xǁContextPriorityQueueǁprune_below_priority__mutmut_4, 
        'xǁContextPriorityQueueǁprune_below_priority__mutmut_5': xǁContextPriorityQueueǁprune_below_priority__mutmut_5, 
        'xǁContextPriorityQueueǁprune_below_priority__mutmut_6': xǁContextPriorityQueueǁprune_below_priority__mutmut_6, 
        'xǁContextPriorityQueueǁprune_below_priority__mutmut_7': xǁContextPriorityQueueǁprune_below_priority__mutmut_7, 
        'xǁContextPriorityQueueǁprune_below_priority__mutmut_8': xǁContextPriorityQueueǁprune_below_priority__mutmut_8, 
        'xǁContextPriorityQueueǁprune_below_priority__mutmut_9': xǁContextPriorityQueueǁprune_below_priority__mutmut_9
    }
    
    def prune_below_priority(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextPriorityQueueǁprune_below_priority__mutmut_orig"), object.__getattribute__(self, "xǁContextPriorityQueueǁprune_below_priority__mutmut_mutants"), args, kwargs, self)
        return result 
    
    prune_below_priority.__signature__ = _mutmut_signature(xǁContextPriorityQueueǁprune_below_priority__mutmut_orig)
    xǁContextPriorityQueueǁprune_below_priority__mutmut_orig.__name__ = 'xǁContextPriorityQueueǁprune_below_priority'

    def xǁContextPriorityQueueǁrefresh_priorities__mutmut_orig(self):
        """Refresh effective priorities (triggers decay recalculation)."""
        heapq.heapify(self._items)

    def xǁContextPriorityQueueǁrefresh_priorities__mutmut_1(self):
        """Refresh effective priorities (triggers decay recalculation)."""
        heapq.heapify(None)
    
    xǁContextPriorityQueueǁrefresh_priorities__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextPriorityQueueǁrefresh_priorities__mutmut_1': xǁContextPriorityQueueǁrefresh_priorities__mutmut_1
    }
    
    def refresh_priorities(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextPriorityQueueǁrefresh_priorities__mutmut_orig"), object.__getattribute__(self, "xǁContextPriorityQueueǁrefresh_priorities__mutmut_mutants"), args, kwargs, self)
        return result 
    
    refresh_priorities.__signature__ = _mutmut_signature(xǁContextPriorityQueueǁrefresh_priorities__mutmut_orig)
    xǁContextPriorityQueueǁrefresh_priorities__mutmut_orig.__name__ = 'xǁContextPriorityQueueǁrefresh_priorities'

    def xǁContextPriorityQueueǁaccess_item__mutmut_orig(self, content: str) -> bool:
        """
        Mark item as accessed to boost its priority.

        Args:
            content: Content text to find and access

        Returns:
            True if found and updated, False otherwise
        """
        for item in self._items:
            if item.content == content:
                item.last_accessed = datetime.now()
                item.access_count += 1
                heapq.heapify(self._items)
                return True
        return False

    def xǁContextPriorityQueueǁaccess_item__mutmut_1(self, content: str) -> bool:
        """
        Mark item as accessed to boost its priority.

        Args:
            content: Content text to find and access

        Returns:
            True if found and updated, False otherwise
        """
        for item in self._items:
            if item.content != content:
                item.last_accessed = datetime.now()
                item.access_count += 1
                heapq.heapify(self._items)
                return True
        return False

    def xǁContextPriorityQueueǁaccess_item__mutmut_2(self, content: str) -> bool:
        """
        Mark item as accessed to boost its priority.

        Args:
            content: Content text to find and access

        Returns:
            True if found and updated, False otherwise
        """
        for item in self._items:
            if item.content == content:
                item.last_accessed = None
                item.access_count += 1
                heapq.heapify(self._items)
                return True
        return False

    def xǁContextPriorityQueueǁaccess_item__mutmut_3(self, content: str) -> bool:
        """
        Mark item as accessed to boost its priority.

        Args:
            content: Content text to find and access

        Returns:
            True if found and updated, False otherwise
        """
        for item in self._items:
            if item.content == content:
                item.last_accessed = datetime.now()
                item.access_count = 1
                heapq.heapify(self._items)
                return True
        return False

    def xǁContextPriorityQueueǁaccess_item__mutmut_4(self, content: str) -> bool:
        """
        Mark item as accessed to boost its priority.

        Args:
            content: Content text to find and access

        Returns:
            True if found and updated, False otherwise
        """
        for item in self._items:
            if item.content == content:
                item.last_accessed = datetime.now()
                item.access_count -= 1
                heapq.heapify(self._items)
                return True
        return False

    def xǁContextPriorityQueueǁaccess_item__mutmut_5(self, content: str) -> bool:
        """
        Mark item as accessed to boost its priority.

        Args:
            content: Content text to find and access

        Returns:
            True if found and updated, False otherwise
        """
        for item in self._items:
            if item.content == content:
                item.last_accessed = datetime.now()
                item.access_count += 2
                heapq.heapify(self._items)
                return True
        return False

    def xǁContextPriorityQueueǁaccess_item__mutmut_6(self, content: str) -> bool:
        """
        Mark item as accessed to boost its priority.

        Args:
            content: Content text to find and access

        Returns:
            True if found and updated, False otherwise
        """
        for item in self._items:
            if item.content == content:
                item.last_accessed = datetime.now()
                item.access_count += 1
                heapq.heapify(None)
                return True
        return False

    def xǁContextPriorityQueueǁaccess_item__mutmut_7(self, content: str) -> bool:
        """
        Mark item as accessed to boost its priority.

        Args:
            content: Content text to find and access

        Returns:
            True if found and updated, False otherwise
        """
        for item in self._items:
            if item.content == content:
                item.last_accessed = datetime.now()
                item.access_count += 1
                heapq.heapify(self._items)
                return False
        return False

    def xǁContextPriorityQueueǁaccess_item__mutmut_8(self, content: str) -> bool:
        """
        Mark item as accessed to boost its priority.

        Args:
            content: Content text to find and access

        Returns:
            True if found and updated, False otherwise
        """
        for item in self._items:
            if item.content == content:
                item.last_accessed = datetime.now()
                item.access_count += 1
                heapq.heapify(self._items)
                return True
        return True
    
    xǁContextPriorityQueueǁaccess_item__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextPriorityQueueǁaccess_item__mutmut_1': xǁContextPriorityQueueǁaccess_item__mutmut_1, 
        'xǁContextPriorityQueueǁaccess_item__mutmut_2': xǁContextPriorityQueueǁaccess_item__mutmut_2, 
        'xǁContextPriorityQueueǁaccess_item__mutmut_3': xǁContextPriorityQueueǁaccess_item__mutmut_3, 
        'xǁContextPriorityQueueǁaccess_item__mutmut_4': xǁContextPriorityQueueǁaccess_item__mutmut_4, 
        'xǁContextPriorityQueueǁaccess_item__mutmut_5': xǁContextPriorityQueueǁaccess_item__mutmut_5, 
        'xǁContextPriorityQueueǁaccess_item__mutmut_6': xǁContextPriorityQueueǁaccess_item__mutmut_6, 
        'xǁContextPriorityQueueǁaccess_item__mutmut_7': xǁContextPriorityQueueǁaccess_item__mutmut_7, 
        'xǁContextPriorityQueueǁaccess_item__mutmut_8': xǁContextPriorityQueueǁaccess_item__mutmut_8
    }
    
    def access_item(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextPriorityQueueǁaccess_item__mutmut_orig"), object.__getattribute__(self, "xǁContextPriorityQueueǁaccess_item__mutmut_mutants"), args, kwargs, self)
        return result 
    
    access_item.__signature__ = _mutmut_signature(xǁContextPriorityQueueǁaccess_item__mutmut_orig)
    xǁContextPriorityQueueǁaccess_item__mutmut_orig.__name__ = 'xǁContextPriorityQueueǁaccess_item'

    def xǁContextPriorityQueueǁclear__mutmut_orig(self):
        """Clear all items."""
        self._items.clear()
        self._token_count = 0
        self._item_index.clear()

    def xǁContextPriorityQueueǁclear__mutmut_1(self):
        """Clear all items."""
        self._items.clear()
        self._token_count = None
        self._item_index.clear()

    def xǁContextPriorityQueueǁclear__mutmut_2(self):
        """Clear all items."""
        self._items.clear()
        self._token_count = 1
        self._item_index.clear()
    
    xǁContextPriorityQueueǁclear__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextPriorityQueueǁclear__mutmut_1': xǁContextPriorityQueueǁclear__mutmut_1, 
        'xǁContextPriorityQueueǁclear__mutmut_2': xǁContextPriorityQueueǁclear__mutmut_2
    }
    
    def clear(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextPriorityQueueǁclear__mutmut_orig"), object.__getattribute__(self, "xǁContextPriorityQueueǁclear__mutmut_mutants"), args, kwargs, self)
        return result 
    
    clear.__signature__ = _mutmut_signature(xǁContextPriorityQueueǁclear__mutmut_orig)
    xǁContextPriorityQueueǁclear__mutmut_orig.__name__ = 'xǁContextPriorityQueueǁclear'

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

    def xǁContextPriorityQueueǁget_stats__mutmut_orig(self) -> dict:
        """Get queue statistics."""
        if not self._items:
            return {
                "size": 0,
                "token_count": 0,
                "priority_distribution": {},
                "average_age_seconds": 0,
                "average_effective_priority": 0,
            }

        priority_dist = {}
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

    def xǁContextPriorityQueueǁget_stats__mutmut_1(self) -> dict:
        """Get queue statistics."""
        if self._items:
            return {
                "size": 0,
                "token_count": 0,
                "priority_distribution": {},
                "average_age_seconds": 0,
                "average_effective_priority": 0,
            }

        priority_dist = {}
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

    def xǁContextPriorityQueueǁget_stats__mutmut_2(self) -> dict:
        """Get queue statistics."""
        if not self._items:
            return {
                "XXsizeXX": 0,
                "token_count": 0,
                "priority_distribution": {},
                "average_age_seconds": 0,
                "average_effective_priority": 0,
            }

        priority_dist = {}
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

    def xǁContextPriorityQueueǁget_stats__mutmut_3(self) -> dict:
        """Get queue statistics."""
        if not self._items:
            return {
                "SIZE": 0,
                "token_count": 0,
                "priority_distribution": {},
                "average_age_seconds": 0,
                "average_effective_priority": 0,
            }

        priority_dist = {}
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

    def xǁContextPriorityQueueǁget_stats__mutmut_4(self) -> dict:
        """Get queue statistics."""
        if not self._items:
            return {
                "size": 1,
                "token_count": 0,
                "priority_distribution": {},
                "average_age_seconds": 0,
                "average_effective_priority": 0,
            }

        priority_dist = {}
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

    def xǁContextPriorityQueueǁget_stats__mutmut_5(self) -> dict:
        """Get queue statistics."""
        if not self._items:
            return {
                "size": 0,
                "XXtoken_countXX": 0,
                "priority_distribution": {},
                "average_age_seconds": 0,
                "average_effective_priority": 0,
            }

        priority_dist = {}
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

    def xǁContextPriorityQueueǁget_stats__mutmut_6(self) -> dict:
        """Get queue statistics."""
        if not self._items:
            return {
                "size": 0,
                "TOKEN_COUNT": 0,
                "priority_distribution": {},
                "average_age_seconds": 0,
                "average_effective_priority": 0,
            }

        priority_dist = {}
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

    def xǁContextPriorityQueueǁget_stats__mutmut_7(self) -> dict:
        """Get queue statistics."""
        if not self._items:
            return {
                "size": 0,
                "token_count": 1,
                "priority_distribution": {},
                "average_age_seconds": 0,
                "average_effective_priority": 0,
            }

        priority_dist = {}
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

    def xǁContextPriorityQueueǁget_stats__mutmut_8(self) -> dict:
        """Get queue statistics."""
        if not self._items:
            return {
                "size": 0,
                "token_count": 0,
                "XXpriority_distributionXX": {},
                "average_age_seconds": 0,
                "average_effective_priority": 0,
            }

        priority_dist = {}
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

    def xǁContextPriorityQueueǁget_stats__mutmut_9(self) -> dict:
        """Get queue statistics."""
        if not self._items:
            return {
                "size": 0,
                "token_count": 0,
                "PRIORITY_DISTRIBUTION": {},
                "average_age_seconds": 0,
                "average_effective_priority": 0,
            }

        priority_dist = {}
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

    def xǁContextPriorityQueueǁget_stats__mutmut_10(self) -> dict:
        """Get queue statistics."""
        if not self._items:
            return {
                "size": 0,
                "token_count": 0,
                "priority_distribution": {},
                "XXaverage_age_secondsXX": 0,
                "average_effective_priority": 0,
            }

        priority_dist = {}
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

    def xǁContextPriorityQueueǁget_stats__mutmut_11(self) -> dict:
        """Get queue statistics."""
        if not self._items:
            return {
                "size": 0,
                "token_count": 0,
                "priority_distribution": {},
                "AVERAGE_AGE_SECONDS": 0,
                "average_effective_priority": 0,
            }

        priority_dist = {}
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

    def xǁContextPriorityQueueǁget_stats__mutmut_12(self) -> dict:
        """Get queue statistics."""
        if not self._items:
            return {
                "size": 0,
                "token_count": 0,
                "priority_distribution": {},
                "average_age_seconds": 1,
                "average_effective_priority": 0,
            }

        priority_dist = {}
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

    def xǁContextPriorityQueueǁget_stats__mutmut_13(self) -> dict:
        """Get queue statistics."""
        if not self._items:
            return {
                "size": 0,
                "token_count": 0,
                "priority_distribution": {},
                "average_age_seconds": 0,
                "XXaverage_effective_priorityXX": 0,
            }

        priority_dist = {}
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

    def xǁContextPriorityQueueǁget_stats__mutmut_14(self) -> dict:
        """Get queue statistics."""
        if not self._items:
            return {
                "size": 0,
                "token_count": 0,
                "priority_distribution": {},
                "average_age_seconds": 0,
                "AVERAGE_EFFECTIVE_PRIORITY": 0,
            }

        priority_dist = {}
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

    def xǁContextPriorityQueueǁget_stats__mutmut_15(self) -> dict:
        """Get queue statistics."""
        if not self._items:
            return {
                "size": 0,
                "token_count": 0,
                "priority_distribution": {},
                "average_age_seconds": 0,
                "average_effective_priority": 1,
            }

        priority_dist = {}
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

    def xǁContextPriorityQueueǁget_stats__mutmut_16(self) -> dict:
        """Get queue statistics."""
        if not self._items:
            return {
                "size": 0,
                "token_count": 0,
                "priority_distribution": {},
                "average_age_seconds": 0,
                "average_effective_priority": 0,
            }

        priority_dist = None
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

    def xǁContextPriorityQueueǁget_stats__mutmut_17(self) -> dict:
        """Get queue statistics."""
        if not self._items:
            return {
                "size": 0,
                "token_count": 0,
                "priority_distribution": {},
                "average_age_seconds": 0,
                "average_effective_priority": 0,
            }

        priority_dist = {}
        for item in self._items:
            p = None
            priority_dist[p] = priority_dist.get(p, 0) + 1

        return {
            "size": len(self._items),
            "token_count": self._token_count,
            "priority_distribution": priority_dist,
            "average_age_seconds": sum(i.age_seconds for i in self._items) / len(self._items),
            "average_effective_priority": sum(i.effective_priority for i in self._items)
            / len(self._items),
        }

    def xǁContextPriorityQueueǁget_stats__mutmut_18(self) -> dict:
        """Get queue statistics."""
        if not self._items:
            return {
                "size": 0,
                "token_count": 0,
                "priority_distribution": {},
                "average_age_seconds": 0,
                "average_effective_priority": 0,
            }

        priority_dist = {}
        for item in self._items:
            p = item.priority.name
            priority_dist[p] = None

        return {
            "size": len(self._items),
            "token_count": self._token_count,
            "priority_distribution": priority_dist,
            "average_age_seconds": sum(i.age_seconds for i in self._items) / len(self._items),
            "average_effective_priority": sum(i.effective_priority for i in self._items)
            / len(self._items),
        }

    def xǁContextPriorityQueueǁget_stats__mutmut_19(self) -> dict:
        """Get queue statistics."""
        if not self._items:
            return {
                "size": 0,
                "token_count": 0,
                "priority_distribution": {},
                "average_age_seconds": 0,
                "average_effective_priority": 0,
            }

        priority_dist = {}
        for item in self._items:
            p = item.priority.name
            priority_dist[p] = priority_dist.get(p, 0) - 1

        return {
            "size": len(self._items),
            "token_count": self._token_count,
            "priority_distribution": priority_dist,
            "average_age_seconds": sum(i.age_seconds for i in self._items) / len(self._items),
            "average_effective_priority": sum(i.effective_priority for i in self._items)
            / len(self._items),
        }

    def xǁContextPriorityQueueǁget_stats__mutmut_20(self) -> dict:
        """Get queue statistics."""
        if not self._items:
            return {
                "size": 0,
                "token_count": 0,
                "priority_distribution": {},
                "average_age_seconds": 0,
                "average_effective_priority": 0,
            }

        priority_dist = {}
        for item in self._items:
            p = item.priority.name
            priority_dist[p] = priority_dist.get(None, 0) + 1

        return {
            "size": len(self._items),
            "token_count": self._token_count,
            "priority_distribution": priority_dist,
            "average_age_seconds": sum(i.age_seconds for i in self._items) / len(self._items),
            "average_effective_priority": sum(i.effective_priority for i in self._items)
            / len(self._items),
        }

    def xǁContextPriorityQueueǁget_stats__mutmut_21(self) -> dict:
        """Get queue statistics."""
        if not self._items:
            return {
                "size": 0,
                "token_count": 0,
                "priority_distribution": {},
                "average_age_seconds": 0,
                "average_effective_priority": 0,
            }

        priority_dist = {}
        for item in self._items:
            p = item.priority.name
            priority_dist[p] = priority_dist.get(p, None) + 1

        return {
            "size": len(self._items),
            "token_count": self._token_count,
            "priority_distribution": priority_dist,
            "average_age_seconds": sum(i.age_seconds for i in self._items) / len(self._items),
            "average_effective_priority": sum(i.effective_priority for i in self._items)
            / len(self._items),
        }

    def xǁContextPriorityQueueǁget_stats__mutmut_22(self) -> dict:
        """Get queue statistics."""
        if not self._items:
            return {
                "size": 0,
                "token_count": 0,
                "priority_distribution": {},
                "average_age_seconds": 0,
                "average_effective_priority": 0,
            }

        priority_dist = {}
        for item in self._items:
            p = item.priority.name
            priority_dist[p] = priority_dist.get(0) + 1

        return {
            "size": len(self._items),
            "token_count": self._token_count,
            "priority_distribution": priority_dist,
            "average_age_seconds": sum(i.age_seconds for i in self._items) / len(self._items),
            "average_effective_priority": sum(i.effective_priority for i in self._items)
            / len(self._items),
        }

    def xǁContextPriorityQueueǁget_stats__mutmut_23(self) -> dict:
        """Get queue statistics."""
        if not self._items:
            return {
                "size": 0,
                "token_count": 0,
                "priority_distribution": {},
                "average_age_seconds": 0,
                "average_effective_priority": 0,
            }

        priority_dist = {}
        for item in self._items:
            p = item.priority.name
            priority_dist[p] = priority_dist.get(p, ) + 1

        return {
            "size": len(self._items),
            "token_count": self._token_count,
            "priority_distribution": priority_dist,
            "average_age_seconds": sum(i.age_seconds for i in self._items) / len(self._items),
            "average_effective_priority": sum(i.effective_priority for i in self._items)
            / len(self._items),
        }

    def xǁContextPriorityQueueǁget_stats__mutmut_24(self) -> dict:
        """Get queue statistics."""
        if not self._items:
            return {
                "size": 0,
                "token_count": 0,
                "priority_distribution": {},
                "average_age_seconds": 0,
                "average_effective_priority": 0,
            }

        priority_dist = {}
        for item in self._items:
            p = item.priority.name
            priority_dist[p] = priority_dist.get(p, 1) + 1

        return {
            "size": len(self._items),
            "token_count": self._token_count,
            "priority_distribution": priority_dist,
            "average_age_seconds": sum(i.age_seconds for i in self._items) / len(self._items),
            "average_effective_priority": sum(i.effective_priority for i in self._items)
            / len(self._items),
        }

    def xǁContextPriorityQueueǁget_stats__mutmut_25(self) -> dict:
        """Get queue statistics."""
        if not self._items:
            return {
                "size": 0,
                "token_count": 0,
                "priority_distribution": {},
                "average_age_seconds": 0,
                "average_effective_priority": 0,
            }

        priority_dist = {}
        for item in self._items:
            p = item.priority.name
            priority_dist[p] = priority_dist.get(p, 0) + 2

        return {
            "size": len(self._items),
            "token_count": self._token_count,
            "priority_distribution": priority_dist,
            "average_age_seconds": sum(i.age_seconds for i in self._items) / len(self._items),
            "average_effective_priority": sum(i.effective_priority for i in self._items)
            / len(self._items),
        }

    def xǁContextPriorityQueueǁget_stats__mutmut_26(self) -> dict:
        """Get queue statistics."""
        if not self._items:
            return {
                "size": 0,
                "token_count": 0,
                "priority_distribution": {},
                "average_age_seconds": 0,
                "average_effective_priority": 0,
            }

        priority_dist = {}
        for item in self._items:
            p = item.priority.name
            priority_dist[p] = priority_dist.get(p, 0) + 1

        return {
            "XXsizeXX": len(self._items),
            "token_count": self._token_count,
            "priority_distribution": priority_dist,
            "average_age_seconds": sum(i.age_seconds for i in self._items) / len(self._items),
            "average_effective_priority": sum(i.effective_priority for i in self._items)
            / len(self._items),
        }

    def xǁContextPriorityQueueǁget_stats__mutmut_27(self) -> dict:
        """Get queue statistics."""
        if not self._items:
            return {
                "size": 0,
                "token_count": 0,
                "priority_distribution": {},
                "average_age_seconds": 0,
                "average_effective_priority": 0,
            }

        priority_dist = {}
        for item in self._items:
            p = item.priority.name
            priority_dist[p] = priority_dist.get(p, 0) + 1

        return {
            "SIZE": len(self._items),
            "token_count": self._token_count,
            "priority_distribution": priority_dist,
            "average_age_seconds": sum(i.age_seconds for i in self._items) / len(self._items),
            "average_effective_priority": sum(i.effective_priority for i in self._items)
            / len(self._items),
        }

    def xǁContextPriorityQueueǁget_stats__mutmut_28(self) -> dict:
        """Get queue statistics."""
        if not self._items:
            return {
                "size": 0,
                "token_count": 0,
                "priority_distribution": {},
                "average_age_seconds": 0,
                "average_effective_priority": 0,
            }

        priority_dist = {}
        for item in self._items:
            p = item.priority.name
            priority_dist[p] = priority_dist.get(p, 0) + 1

        return {
            "size": len(self._items),
            "XXtoken_countXX": self._token_count,
            "priority_distribution": priority_dist,
            "average_age_seconds": sum(i.age_seconds for i in self._items) / len(self._items),
            "average_effective_priority": sum(i.effective_priority for i in self._items)
            / len(self._items),
        }

    def xǁContextPriorityQueueǁget_stats__mutmut_29(self) -> dict:
        """Get queue statistics."""
        if not self._items:
            return {
                "size": 0,
                "token_count": 0,
                "priority_distribution": {},
                "average_age_seconds": 0,
                "average_effective_priority": 0,
            }

        priority_dist = {}
        for item in self._items:
            p = item.priority.name
            priority_dist[p] = priority_dist.get(p, 0) + 1

        return {
            "size": len(self._items),
            "TOKEN_COUNT": self._token_count,
            "priority_distribution": priority_dist,
            "average_age_seconds": sum(i.age_seconds for i in self._items) / len(self._items),
            "average_effective_priority": sum(i.effective_priority for i in self._items)
            / len(self._items),
        }

    def xǁContextPriorityQueueǁget_stats__mutmut_30(self) -> dict:
        """Get queue statistics."""
        if not self._items:
            return {
                "size": 0,
                "token_count": 0,
                "priority_distribution": {},
                "average_age_seconds": 0,
                "average_effective_priority": 0,
            }

        priority_dist = {}
        for item in self._items:
            p = item.priority.name
            priority_dist[p] = priority_dist.get(p, 0) + 1

        return {
            "size": len(self._items),
            "token_count": self._token_count,
            "XXpriority_distributionXX": priority_dist,
            "average_age_seconds": sum(i.age_seconds for i in self._items) / len(self._items),
            "average_effective_priority": sum(i.effective_priority for i in self._items)
            / len(self._items),
        }

    def xǁContextPriorityQueueǁget_stats__mutmut_31(self) -> dict:
        """Get queue statistics."""
        if not self._items:
            return {
                "size": 0,
                "token_count": 0,
                "priority_distribution": {},
                "average_age_seconds": 0,
                "average_effective_priority": 0,
            }

        priority_dist = {}
        for item in self._items:
            p = item.priority.name
            priority_dist[p] = priority_dist.get(p, 0) + 1

        return {
            "size": len(self._items),
            "token_count": self._token_count,
            "PRIORITY_DISTRIBUTION": priority_dist,
            "average_age_seconds": sum(i.age_seconds for i in self._items) / len(self._items),
            "average_effective_priority": sum(i.effective_priority for i in self._items)
            / len(self._items),
        }

    def xǁContextPriorityQueueǁget_stats__mutmut_32(self) -> dict:
        """Get queue statistics."""
        if not self._items:
            return {
                "size": 0,
                "token_count": 0,
                "priority_distribution": {},
                "average_age_seconds": 0,
                "average_effective_priority": 0,
            }

        priority_dist = {}
        for item in self._items:
            p = item.priority.name
            priority_dist[p] = priority_dist.get(p, 0) + 1

        return {
            "size": len(self._items),
            "token_count": self._token_count,
            "priority_distribution": priority_dist,
            "XXaverage_age_secondsXX": sum(i.age_seconds for i in self._items) / len(self._items),
            "average_effective_priority": sum(i.effective_priority for i in self._items)
            / len(self._items),
        }

    def xǁContextPriorityQueueǁget_stats__mutmut_33(self) -> dict:
        """Get queue statistics."""
        if not self._items:
            return {
                "size": 0,
                "token_count": 0,
                "priority_distribution": {},
                "average_age_seconds": 0,
                "average_effective_priority": 0,
            }

        priority_dist = {}
        for item in self._items:
            p = item.priority.name
            priority_dist[p] = priority_dist.get(p, 0) + 1

        return {
            "size": len(self._items),
            "token_count": self._token_count,
            "priority_distribution": priority_dist,
            "AVERAGE_AGE_SECONDS": sum(i.age_seconds for i in self._items) / len(self._items),
            "average_effective_priority": sum(i.effective_priority for i in self._items)
            / len(self._items),
        }

    def xǁContextPriorityQueueǁget_stats__mutmut_34(self) -> dict:
        """Get queue statistics."""
        if not self._items:
            return {
                "size": 0,
                "token_count": 0,
                "priority_distribution": {},
                "average_age_seconds": 0,
                "average_effective_priority": 0,
            }

        priority_dist = {}
        for item in self._items:
            p = item.priority.name
            priority_dist[p] = priority_dist.get(p, 0) + 1

        return {
            "size": len(self._items),
            "token_count": self._token_count,
            "priority_distribution": priority_dist,
            "average_age_seconds": sum(i.age_seconds for i in self._items) * len(self._items),
            "average_effective_priority": sum(i.effective_priority for i in self._items)
            / len(self._items),
        }

    def xǁContextPriorityQueueǁget_stats__mutmut_35(self) -> dict:
        """Get queue statistics."""
        if not self._items:
            return {
                "size": 0,
                "token_count": 0,
                "priority_distribution": {},
                "average_age_seconds": 0,
                "average_effective_priority": 0,
            }

        priority_dist = {}
        for item in self._items:
            p = item.priority.name
            priority_dist[p] = priority_dist.get(p, 0) + 1

        return {
            "size": len(self._items),
            "token_count": self._token_count,
            "priority_distribution": priority_dist,
            "average_age_seconds": sum(None) / len(self._items),
            "average_effective_priority": sum(i.effective_priority for i in self._items)
            / len(self._items),
        }

    def xǁContextPriorityQueueǁget_stats__mutmut_36(self) -> dict:
        """Get queue statistics."""
        if not self._items:
            return {
                "size": 0,
                "token_count": 0,
                "priority_distribution": {},
                "average_age_seconds": 0,
                "average_effective_priority": 0,
            }

        priority_dist = {}
        for item in self._items:
            p = item.priority.name
            priority_dist[p] = priority_dist.get(p, 0) + 1

        return {
            "size": len(self._items),
            "token_count": self._token_count,
            "priority_distribution": priority_dist,
            "average_age_seconds": sum(i.age_seconds for i in self._items) / len(self._items),
            "XXaverage_effective_priorityXX": sum(i.effective_priority for i in self._items)
            / len(self._items),
        }

    def xǁContextPriorityQueueǁget_stats__mutmut_37(self) -> dict:
        """Get queue statistics."""
        if not self._items:
            return {
                "size": 0,
                "token_count": 0,
                "priority_distribution": {},
                "average_age_seconds": 0,
                "average_effective_priority": 0,
            }

        priority_dist = {}
        for item in self._items:
            p = item.priority.name
            priority_dist[p] = priority_dist.get(p, 0) + 1

        return {
            "size": len(self._items),
            "token_count": self._token_count,
            "priority_distribution": priority_dist,
            "average_age_seconds": sum(i.age_seconds for i in self._items) / len(self._items),
            "AVERAGE_EFFECTIVE_PRIORITY": sum(i.effective_priority for i in self._items)
            / len(self._items),
        }

    def xǁContextPriorityQueueǁget_stats__mutmut_38(self) -> dict:
        """Get queue statistics."""
        if not self._items:
            return {
                "size": 0,
                "token_count": 0,
                "priority_distribution": {},
                "average_age_seconds": 0,
                "average_effective_priority": 0,
            }

        priority_dist = {}
        for item in self._items:
            p = item.priority.name
            priority_dist[p] = priority_dist.get(p, 0) + 1

        return {
            "size": len(self._items),
            "token_count": self._token_count,
            "priority_distribution": priority_dist,
            "average_age_seconds": sum(i.age_seconds for i in self._items) / len(self._items),
            "average_effective_priority": sum(i.effective_priority for i in self._items) * len(self._items),
        }

    def xǁContextPriorityQueueǁget_stats__mutmut_39(self) -> dict:
        """Get queue statistics."""
        if not self._items:
            return {
                "size": 0,
                "token_count": 0,
                "priority_distribution": {},
                "average_age_seconds": 0,
                "average_effective_priority": 0,
            }

        priority_dist = {}
        for item in self._items:
            p = item.priority.name
            priority_dist[p] = priority_dist.get(p, 0) + 1

        return {
            "size": len(self._items),
            "token_count": self._token_count,
            "priority_distribution": priority_dist,
            "average_age_seconds": sum(i.age_seconds for i in self._items) / len(self._items),
            "average_effective_priority": sum(None)
            / len(self._items),
        }
    
    xǁContextPriorityQueueǁget_stats__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextPriorityQueueǁget_stats__mutmut_1': xǁContextPriorityQueueǁget_stats__mutmut_1, 
        'xǁContextPriorityQueueǁget_stats__mutmut_2': xǁContextPriorityQueueǁget_stats__mutmut_2, 
        'xǁContextPriorityQueueǁget_stats__mutmut_3': xǁContextPriorityQueueǁget_stats__mutmut_3, 
        'xǁContextPriorityQueueǁget_stats__mutmut_4': xǁContextPriorityQueueǁget_stats__mutmut_4, 
        'xǁContextPriorityQueueǁget_stats__mutmut_5': xǁContextPriorityQueueǁget_stats__mutmut_5, 
        'xǁContextPriorityQueueǁget_stats__mutmut_6': xǁContextPriorityQueueǁget_stats__mutmut_6, 
        'xǁContextPriorityQueueǁget_stats__mutmut_7': xǁContextPriorityQueueǁget_stats__mutmut_7, 
        'xǁContextPriorityQueueǁget_stats__mutmut_8': xǁContextPriorityQueueǁget_stats__mutmut_8, 
        'xǁContextPriorityQueueǁget_stats__mutmut_9': xǁContextPriorityQueueǁget_stats__mutmut_9, 
        'xǁContextPriorityQueueǁget_stats__mutmut_10': xǁContextPriorityQueueǁget_stats__mutmut_10, 
        'xǁContextPriorityQueueǁget_stats__mutmut_11': xǁContextPriorityQueueǁget_stats__mutmut_11, 
        'xǁContextPriorityQueueǁget_stats__mutmut_12': xǁContextPriorityQueueǁget_stats__mutmut_12, 
        'xǁContextPriorityQueueǁget_stats__mutmut_13': xǁContextPriorityQueueǁget_stats__mutmut_13, 
        'xǁContextPriorityQueueǁget_stats__mutmut_14': xǁContextPriorityQueueǁget_stats__mutmut_14, 
        'xǁContextPriorityQueueǁget_stats__mutmut_15': xǁContextPriorityQueueǁget_stats__mutmut_15, 
        'xǁContextPriorityQueueǁget_stats__mutmut_16': xǁContextPriorityQueueǁget_stats__mutmut_16, 
        'xǁContextPriorityQueueǁget_stats__mutmut_17': xǁContextPriorityQueueǁget_stats__mutmut_17, 
        'xǁContextPriorityQueueǁget_stats__mutmut_18': xǁContextPriorityQueueǁget_stats__mutmut_18, 
        'xǁContextPriorityQueueǁget_stats__mutmut_19': xǁContextPriorityQueueǁget_stats__mutmut_19, 
        'xǁContextPriorityQueueǁget_stats__mutmut_20': xǁContextPriorityQueueǁget_stats__mutmut_20, 
        'xǁContextPriorityQueueǁget_stats__mutmut_21': xǁContextPriorityQueueǁget_stats__mutmut_21, 
        'xǁContextPriorityQueueǁget_stats__mutmut_22': xǁContextPriorityQueueǁget_stats__mutmut_22, 
        'xǁContextPriorityQueueǁget_stats__mutmut_23': xǁContextPriorityQueueǁget_stats__mutmut_23, 
        'xǁContextPriorityQueueǁget_stats__mutmut_24': xǁContextPriorityQueueǁget_stats__mutmut_24, 
        'xǁContextPriorityQueueǁget_stats__mutmut_25': xǁContextPriorityQueueǁget_stats__mutmut_25, 
        'xǁContextPriorityQueueǁget_stats__mutmut_26': xǁContextPriorityQueueǁget_stats__mutmut_26, 
        'xǁContextPriorityQueueǁget_stats__mutmut_27': xǁContextPriorityQueueǁget_stats__mutmut_27, 
        'xǁContextPriorityQueueǁget_stats__mutmut_28': xǁContextPriorityQueueǁget_stats__mutmut_28, 
        'xǁContextPriorityQueueǁget_stats__mutmut_29': xǁContextPriorityQueueǁget_stats__mutmut_29, 
        'xǁContextPriorityQueueǁget_stats__mutmut_30': xǁContextPriorityQueueǁget_stats__mutmut_30, 
        'xǁContextPriorityQueueǁget_stats__mutmut_31': xǁContextPriorityQueueǁget_stats__mutmut_31, 
        'xǁContextPriorityQueueǁget_stats__mutmut_32': xǁContextPriorityQueueǁget_stats__mutmut_32, 
        'xǁContextPriorityQueueǁget_stats__mutmut_33': xǁContextPriorityQueueǁget_stats__mutmut_33, 
        'xǁContextPriorityQueueǁget_stats__mutmut_34': xǁContextPriorityQueueǁget_stats__mutmut_34, 
        'xǁContextPriorityQueueǁget_stats__mutmut_35': xǁContextPriorityQueueǁget_stats__mutmut_35, 
        'xǁContextPriorityQueueǁget_stats__mutmut_36': xǁContextPriorityQueueǁget_stats__mutmut_36, 
        'xǁContextPriorityQueueǁget_stats__mutmut_37': xǁContextPriorityQueueǁget_stats__mutmut_37, 
        'xǁContextPriorityQueueǁget_stats__mutmut_38': xǁContextPriorityQueueǁget_stats__mutmut_38, 
        'xǁContextPriorityQueueǁget_stats__mutmut_39': xǁContextPriorityQueueǁget_stats__mutmut_39
    }
    
    def get_stats(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextPriorityQueueǁget_stats__mutmut_orig"), object.__getattribute__(self, "xǁContextPriorityQueueǁget_stats__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_stats.__signature__ = _mutmut_signature(xǁContextPriorityQueueǁget_stats__mutmut_orig)
    xǁContextPriorityQueueǁget_stats__mutmut_orig.__name__ = 'xǁContextPriorityQueueǁget_stats'

    def xǁContextPriorityQueueǁ_prune_lowest__mutmut_orig(self) -> bool:
        """Prune single lowest priority item."""
        item = self.pop()
        return item is not None

    def xǁContextPriorityQueueǁ_prune_lowest__mutmut_1(self) -> bool:
        """Prune single lowest priority item."""
        item = None
        return item is not None

    def xǁContextPriorityQueueǁ_prune_lowest__mutmut_2(self) -> bool:
        """Prune single lowest priority item."""
        item = self.pop()
        return item is None
    
    xǁContextPriorityQueueǁ_prune_lowest__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextPriorityQueueǁ_prune_lowest__mutmut_1': xǁContextPriorityQueueǁ_prune_lowest__mutmut_1, 
        'xǁContextPriorityQueueǁ_prune_lowest__mutmut_2': xǁContextPriorityQueueǁ_prune_lowest__mutmut_2
    }
    
    def _prune_lowest(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextPriorityQueueǁ_prune_lowest__mutmut_orig"), object.__getattribute__(self, "xǁContextPriorityQueueǁ_prune_lowest__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _prune_lowest.__signature__ = _mutmut_signature(xǁContextPriorityQueueǁ_prune_lowest__mutmut_orig)
    xǁContextPriorityQueueǁ_prune_lowest__mutmut_orig.__name__ = 'xǁContextPriorityQueueǁ_prune_lowest'
