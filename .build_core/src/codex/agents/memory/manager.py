"""High-level memory manager for agent memory operations.

Provides a convenient API for agents to interact with the memory system.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional

from .backends import SQLiteMemoryBackend
from .protocol import MemoryEntry, MemoryProtocol, MemoryQuery

logger = logging.getLogger(__name__)


class MemoryManager:
    """High-level manager for agent memory operations.

    Provides a simple API for storing and retrieving memories with automatic
    session management and context tracking.

    Args:
        backend: Memory storage backend (defaults to SQLite)
        agent_id: ID of the agent using this manager
        session_id: Current session ID (optional)

    Examples:
        >>> manager = MemoryManager(agent_id="assistant-1")
        >>> manager.store("User prefers concise responses", metadata={"importance": "high"})
        >>> memories = manager.recall("user preferences")
    """

    def __init__(
        self,
        backend: Optional[MemoryProtocol] = None,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None,
        storage_dir: Optional[Path] = None,
    ):
        if backend is None:
            # Default to SQLite backend
            storage_dir = storage_dir or Path(".codex/agent_memory")
            storage_dir.mkdir(parents=True, exist_ok=True)
            backend = SQLiteMemoryBackend(storage_dir / "memories.db")

        self.backend = backend
        self.agent_id = agent_id
        self.session_id = session_id

    def store(
        self,
        content: str | dict[str, Any],
        metadata: Optional[dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> MemoryEntry:
        """Store a new memory.

        Args:
            content: The memory content (text or structured data)
            metadata: Optional metadata (importance, tags, etc.)
            session_id: Override session ID for this memory

        Returns:
            The stored memory entry
        """
        entry = MemoryEntry(
            content=content,
            agent_id=self.agent_id,
            session_id=session_id or self.session_id,
            metadata=metadata or {},
        )

        self.backend.store(entry)
        logger.debug(f"Stored memory: {entry.id}")
        return entry

    def recall(
        self,
        query_text: Optional[str] = None,
        limit: int = 10,
        session_id: Optional[str] = None,
        agent_id: Optional[str] = None,
    ) -> list[MemoryEntry]:
        """Retrieve memories matching the query.

        Args:
            query_text: Text to search for in memory content
            limit: Maximum number of results
            session_id: Filter by session ID (None = current session)
            agent_id: Filter by agent ID (None = current agent)

        Returns:
            list of matching memories, sorted by relevance
        """
        query = MemoryQuery(
            text=query_text,
            agent_id=agent_id or self.agent_id,
            session_id=session_id if session_id is not None else self.session_id,
            limit=limit,
        )

        results = self.backend.retrieve(query)
        logger.debug(f"Recalled {len(results)} memories for query: {query_text}")
        return results

    def recall_all(self, limit: int = 100) -> list[MemoryEntry]:
        """Retrieve all memories for current agent/session.

        Args:
            limit: Maximum number of results

        Returns:
            list of all memories
        """
        return self.recall(query_text=None, limit=limit)

    def clear_session(self, session_id: Optional[str] = None) -> int:
        """Clear all memories for a session.

        Args:
            session_id: Session to clear (defaults to current session)

        Returns:
            Number of memories deleted
        """
        sid = session_id or self.session_id
        if not sid:
            raise ValueError("No session_id specified")

        count = self.backend.clear_session(sid)
        logger.info(f"Cleared {count} memories from session {sid}")
        return count

    def get_stats(self) -> dict[str, Any]:
        """Get memory storage statistics.

        Returns:
            Dictionary with statistics
        """
        return self.backend.get_stats()

    def set_session(self, session_id: str) -> None:
        """Change the current session ID.

        Args:
            session_id: New session ID
        """
        self.session_id = session_id
        logger.debug(f"Session changed to: {session_id}")
