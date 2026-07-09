"""Protocol definitions for agent memory system.

Defines the abstract interface that all memory backends must implement.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID, uuid4


@dataclass
class MemoryEntry:
    """Single memory entry with metadata.

    Attributes:
        id: Unique identifier for this memory
        content: The actual memory content (text, dict, etc.)
        timestamp: When this memory was created
        agent_id: ID of the agent that created this memory
        session_id: Session this memory belongs to
        metadata: Additional metadata (tags, importance, etc.)
        embedding: Optional vector embedding for similarity search
    """

    content: str | dict[str, Any]
    id: UUID = field(default_factory=uuid4)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    agent_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    embedding: Optional[list[float]] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert entry to dictionary for serialization."""
        return {
            "id": str(self.id),
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "metadata": self.metadata,
            "embedding": self.embedding,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MemoryEntry:
        """Create entry from dictionary."""
        return cls(
            id=UUID(data["id"]),
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            agent_id=data.get("agent_id"),
            session_id=data.get("session_id"),
            metadata=data.get("metadata", {}),
            embedding=data.get("embedding"),
        )


@dataclass
class MemoryQuery:
    """Query specification for retrieving memories.

    Attributes:
        text: Text query for semantic search
        agent_id: Filter by agent ID
        session_id: Filter by session ID
        limit: Maximum number of results
        since: Only return memories after this timestamp
    """

    text: Optional[str] = None
    agent_id: Optional[str] = None
    session_id: Optional[str] = None
    limit: int = 10
    since: Optional[datetime] = None


class MemoryProtocol(ABC):
    """Abstract protocol for memory storage backends.

    This protocol defines the interface that all memory backends must implement.
    Implementations can use files, databases, or vector stores.
    """

    @abstractmethod
    def store(self, entry: MemoryEntry) -> None:
        """Store a memory entry.

        Args:
            entry: The memory entry to store
        """

    @abstractmethod
    def retrieve(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve memories matching the query.

        Args:
            query: Query specification

        Returns:
            list of matching memory entries, sorted by relevance
        """

    @abstractmethod
    def delete(self, entry_id: UUID) -> bool:
        """Delete a memory entry by ID.

        Args:
            entry_id: ID of the entry to delete

        Returns:
            True if deleted, False if not found
        """

    @abstractmethod
    def clear_session(self, session_id: str) -> int:
        """Clear all memories for a session.

        Args:
            session_id: Session ID to clear

        Returns:
            Number of entries deleted
        """

    @abstractmethod
    def get_stats(self) -> dict[str, Any]:
        """Get statistics about the memory store.

        Returns:
            Dictionary with stats (entry_count, size_bytes, etc.)
        """
