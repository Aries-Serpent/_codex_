"""Short-term memory (STM) implementation.

Provides working memory with limited capacity and attention mechanisms
for immediate reasoning and decision-making.
"""

from __future__ import annotations

from typing import Any

from .schemas import MemoryEntry


class STMMemory:
    """Short-Term Memory implementation.

    Provides limited-capacity working memory for immediate storage and
    retrieval of information. Uses attention mechanisms and capacity limits
    to manage memory.

    The STM has these characteristics:
    - Limited capacity (default 100 entries)
    - Fast access for recent entries
    - Attention stack for focused memory
    - Integration with LTM for consolidation

    Attributes:
        capacity (int): Maximum number of entries in STM
        entries (list): List of stored memory entries
        attention_stack (list): Stack of focused memory entries
    """

    def __init__(self, capacity: int = 100) -> None:
        """Initialize short-term memory.

        Args:
            capacity: Maximum number of entries (default 100)

        Raises:
            ValueError: If capacity is less than 1
        """
        if capacity < 1:
            raise ValueError("capacity must be at least 1")
        self.capacity = capacity
        self.entries: list[MemoryEntry] = []
        self.attention_stack: list[MemoryEntry] = []

    def store(self, data: Any, importance: float = 0.5, metadata: dict[str, Any] | None = None) -> int:
        """Store data in short-term memory.

        Creates a new MemoryEntry and stores it. If capacity is exceeded,
        removes the least important entry.

        Args:
            data: Data to store
            importance: Importance score (0.0 to 1.0)
            metadata: Optional metadata dictionary

        Returns:
            Index of stored entry

        Raises:
            ValueError: If importance is out of valid range
        """
        if not 0.0 <= importance <= 1.0:
            raise ValueError("importance must be between 0.0 and 1.0")

        entry = MemoryEntry(
            data=data,
            importance=importance,
            metadata=metadata or {}
        )
        self.entries.append(entry)

        # Remove least important entry if capacity exceeded.
        # The newly appended entry (last index) is excluded from eviction
        # to guarantee the caller's returned index is always valid.
        if len(self.entries) > self.capacity:
            last_idx = len(self.entries) - 1
            # Seed the search with any index other than last_idx
            min_idx = 0 if last_idx != 0 else 1
            for i, e in enumerate(self.entries):
                if i != last_idx and e.importance < self.entries[min_idx].importance:
                    min_idx = i
            self.entries.pop(min_idx)
            # min_idx < last_idx always, so the new entry shifted one position left

        return len(self.entries) - 1

    def retrieve(self, index: int) -> Any:
        """Retrieve data from short-term memory by index.

        Args:
            index: Index of the entry to retrieve

        Returns:
            The stored data

        Raises:
            IndexError: If index is out of range
        """
        if index < 0 or index >= len(self.entries):
            raise IndexError(f"Memory index {index} out of range")
        return self.entries[index].data

    def forget(self, index: int) -> None:
        """Remove an entry from short-term memory.

        Args:
            index: Index of the entry to forget

        Raises:
            IndexError: If index is out of range
        """
        if index < 0 or index >= len(self.entries):
            raise IndexError(f"Memory index {index} out of range")
        self.entries.pop(index)

    def consolidate(self, min_importance: float = 0.5) -> list[tuple[Any, float]]:
        """Prepare entries for consolidation to long-term memory.

        Returns a list of entries suitable for consolidation based on
        importance and other criteria.

        Args:
            min_importance: Minimum importance threshold for consolidation
                (0.0–1.0, default 0.5).

        Returns:
            List of (data, importance) tuples ready for LTM consolidation
        """
        consolidatable = [
            (e.data, e.importance)
            for e in self.entries
            if e.importance >= min_importance and e.get_age_seconds() > 1.0
        ]
        return consolidatable

    def push_attention(self, index: int) -> None:
        """Push an entry onto the attention stack.

        Focuses attention on a specific memory entry for active processing.

        Args:
            index: Index of entry to focus on

        Raises:
            IndexError: If index is out of range
        """
        if index < 0 or index >= len(self.entries):
            raise IndexError(f"Memory index {index} out of range")
        self.attention_stack.append(self.entries[index])

    def pop_attention(self) -> MemoryEntry | None:
        """Pop an entry from the attention stack.

        Returns the most recently focused entry.

        Returns:
            MemoryEntry or None if stack is empty
        """
        return self.attention_stack.pop() if self.attention_stack else None

    def get_size(self) -> int:
        """Get current number of entries in STM.

        Returns:
            Number of stored entries
        """
        return len(self.entries)

    def get_attention_size(self) -> int:
        """Get current size of attention stack.

        Returns:
            Number of entries in attention focus
        """
        return len(self.attention_stack)

    def clear(self) -> None:
        """Clear all entries from short-term memory.

        Returns:
            None
        """
        self.entries.clear()
        self.attention_stack.clear()
