"""Agent memory system for persistent context across invocations.

This module provides a memory abstraction layer that allows agents to:
- Store and retrieve context between invocations
- Maintain conversation history
- Access long-term knowledge
- Support future vector database integration

The system uses a pluggable backend design with file-based storage by default.

Examples:
    Basic usage with default SQLite backend:

    >>> from codex.agents.memory import MemoryManager
    >>>
    >>> manager = MemoryManager(agent_id="assistant-1", session_id="session-123")
    >>> manager.store("User prefers Python over JavaScript", metadata={"importance": "high"})
    >>> memories = manager.recall("programming preferences")
    >>> logger.info(memories[0].content)

    Using JSONL backend for simple file-based storage:

    >>> from codex.agents.memory import JSONLMemoryBackend, MemoryManager
    >>> from pathlib import Path
    >>>
    >>> backend = JSONLMemoryBackend(Path(".codex/memories.jsonl"))
    >>> manager = MemoryManager(backend=backend, agent_id="assistant-1")
    >>> manager.store({"user_id": "alice", "preference": "dark_mode"})
"""

from .backends import JSONLMemoryBackend, SQLiteMemoryBackend
from .manager import MemoryManager
from .protocol import MemoryEntry, MemoryProtocol, MemoryQuery

__all__ = [
    "JSONLMemoryBackend",
    "MemoryEntry",
    "MemoryManager",
    "MemoryProtocol",
    "MemoryQuery",
    "SQLiteMemoryBackend",
]

__version__ = "0.1.0"
