"""Memory data structures and schemas.

Defines the core data structures for short-term and long-term memory,
including memory entries and consolidation records.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class MemoryEntry:
    """A single memory entry in the memory system.

    Represents a unit of information stored in memory with associated
    metadata including timestamp, importance, and content.

    Attributes:
        data: The actual data stored in this memory entry
        timestamp: When this entry was created
        importance: Importance score (0.0 to 1.0) for memory consolidation
        metadata: Additional metadata about this entry
    """

    data: Any
    timestamp: datetime = field(default_factory=datetime.now)
    importance: float = 0.5
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate memory entry on initialization.

        Raises:
            ValueError: If importance is not in valid range
        """
        if not 0.0 <= self.importance <= 1.0:
            raise ValueError("importance must be between 0.0 and 1.0")

    def get_age_seconds(self) -> float:
        """Get the age of this memory entry in seconds.

        Returns:
            Age in seconds since creation
        """
        delta = datetime.now() - self.timestamp
        return delta.total_seconds()


@dataclass
class ConsolidationRecord:
    """Record of a memory consolidation operation.

    Tracks when and how memory was consolidated from short-term to
    long-term storage.

    Attributes:
        source_stm_id: Identifier for source STM entries
        target_ltm_id: Identifier for target LTM storage
        timestamp: When consolidation occurred
        num_entries: Number of entries consolidated
        importance_threshold: Minimum importance for consolidation
    """

    source_stm_id: str
    target_ltm_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    num_entries: int = 0
    importance_threshold: float = 0.5
    metadata: dict[str, Any] = field(default_factory=dict)

    def get_time_since_consolidation(self) -> float:
        """Get time elapsed since this consolidation.

        Returns:
            Seconds since consolidation occurred
        """
        delta = datetime.now() - self.timestamp
        return delta.total_seconds()
