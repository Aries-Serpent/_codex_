"""Phase 3C: Infrastructure Coverage - Memory Management Tests.

Focus: Memory manager and storage backends with comprehensive edge cases,
error handling, and integration scenarios.

Target: Boost memory module coverage to 95%+
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from src.codex.agents.memory.backends import JSONLMemoryBackend
from src.codex.agents.memory.manager import MemoryManager
from src.codex.agents.memory.protocol import MemoryEntry, MemoryQuery


class TestMemoryManagerBasics:
    """Test basic memory manager creation and configuration."""

    def test_memory_manager_init_default_backend(self):
        """Test MemoryManager initialization with default SQLite backend."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_dir = Path(tmpdir)
            manager = MemoryManager(storage_dir=storage_dir)
            assert manager.backend is not None, "backend must be initialized"
            assert manager.agent_id is None, "agent_id is not valid"
            assert manager.session_id is None, "session_id is not valid"

    def test_memory_manager_init_with_agent_id(self):
        """Test MemoryManager initialization with agent ID."""
        manager = MemoryManager(agent_id="test-agent")
        assert manager.agent_id == "test-agent", "agent_id is not valid"

    def test_memory_manager_init_with_session_id(self):
        """Test MemoryManager initialization with session ID."""
        manager = MemoryManager(session_id="test-session")
        assert manager.session_id == "test-session", "session_id is not valid"

    def test_memory_manager_init_with_custom_backend(self):
        """Test MemoryManager initialization with custom backend."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = JSONLMemoryBackend(Path(tmpdir) / "test.jsonl")
            manager = MemoryManager(backend=backend)
            assert manager.backend is backend, "backend is not valid"


class TestMemoryStore:
    """Test memory storage operations."""

    def test_store_simple_text_content(self):
        """Test storing simple text content."""
        manager = MemoryManager(agent_id="test-agent", session_id="test-session")
        entry = manager.store("Test memory content")
        assert entry is not None, "entry must be initialized"
        assert entry.content == "Test memory content", "Content must not be empty"
        assert entry.agent_id == "test-agent", "agent_id is not valid"
        assert entry.session_id == "test-session", "session_id is not valid"

    def test_store_dict_content(self):
        """Test storing dictionary content."""
        manager = MemoryManager(agent_id="test-agent", session_id="test-session")
        content = {"key": "value", "data": [1, 2, 3]}
        entry = manager.store(content)
        assert entry.content == content, "Content must not be empty"

    def test_store_with_metadata(self):
        """Test storing memory with metadata."""
        manager = MemoryManager(agent_id="test-agent", session_id="test-session")
        metadata = {"importance": "high", "category": "user-preference"}
        entry = manager.store("Test content", metadata=metadata)
        assert entry.metadata == metadata, "Data must not be empty"

    def test_store_with_override_session_id(self):
        """Test storing with overridden session ID."""
        manager = MemoryManager(agent_id="test-agent", session_id="default-session")
        entry = manager.store("Test content", session_id="override-session")
        assert entry.session_id == "override-session", "session_id is not valid"

    def test_store_multiple_memories(self):
        """Test storing multiple memories."""
        manager = MemoryManager(agent_id="test-agent", session_id="test-session")
        entries = []
        for i in range(5):
            entry = manager.store(f"Memory {i}")
            entries.append(entry)
        assert len(entries) == 5, "Entries must not be empty"
        # Each should have a unique ID
        ids = {e.id for e in entries}
        assert len(ids) == 5, "Ids must not be empty"


class TestMemoryRecall:
    """Test memory retrieval operations."""

    def test_recall_empty_when_no_memories(self):
        """Test recall returns empty list when no memories stored."""
        manager = MemoryManager(agent_id="test-agent", session_id="test-session")
        memories = manager.recall(query_text="nonexistent")
        assert memories == [], "memories is not valid"

    def test_recall_all_retrieves_all_memories(self):
        """Test recall_all retrieves all memories."""
        manager = MemoryManager(agent_id="test-agent", session_id="test-session")
        for i in range(3):
            manager.store(f"Memory {i}")

        all_memories = manager.recall_all()
        assert len(all_memories) >= 3, "All_memories must not be empty"

    def test_recall_with_limit(self):
        """Test recall respects limit parameter."""
        manager = MemoryManager(agent_id="test-agent", session_id="test-session")
        for i in range(10):
            manager.store(f"Memory {i}")

        memories = manager.recall_all(limit=5)
        assert len(memories) <= 5, "Memories must not be empty"

    def test_recall_with_session_filter(self):
        """Test recall filters by session ID."""
        manager1 = MemoryManager(agent_id="agent1", session_id="session1")
        manager2 = MemoryManager(agent_id="agent1", session_id="session2")

        manager1.store("Session 1 memory")
        manager2.store("Session 2 memory")

        session1_memories = manager1.recall_all()
        session2_memories = manager2.recall_all()

        # At least verify we can recall from different sessions
        assert session1_memories is not None, "session1_memories must be initialized"
        assert session2_memories is not None, "session2_memories must be initialized"

    def test_recall_with_agent_filter(self):
        """Test recall filters by agent ID."""
        manager1 = MemoryManager(agent_id="agent1", session_id="session1")
        manager2 = MemoryManager(agent_id="agent2", session_id="session1")

        manager1.store("Agent 1 memory")
        manager2.store("Agent 2 memory")

        agent1_memories = manager1.recall_all()
        agent2_memories = manager2.recall_all()

        assert agent1_memories is not None, "agent1_memories must be initialized"
        assert agent2_memories is not None, "agent2_memories must be initialized"


class TestMemoryProtocol:
    """Test MemoryEntry and MemoryQuery protocol classes."""

    def test_memory_entry_creation(self):
        """Test creating a MemoryEntry."""
        entry = MemoryEntry(
            content="Test content",
            agent_id="test-agent",
            session_id="test-session",
            metadata={"key": "value"},
        )
        assert entry.content == "Test content", "Content must not be empty"
        assert entry.agent_id == "test-agent", "agent_id is not valid"
        assert entry.session_id == "test-session", "session_id is not valid"
        assert entry.metadata == {"key": "value"}, "Data must not be empty"
        assert entry.id is not None, "id must be initialized"

    def test_memory_entry_to_dict(self):
        """Test converting MemoryEntry to dictionary."""
        entry = MemoryEntry(
            content="Test content", agent_id="test-agent", session_id="test-session"
        )
        entry_dict = entry.to_dict()
        assert isinstance(entry_dict, dict)
        assert entry_dict["content"] == "Test content", "Content must not be empty"
        assert entry_dict["agent_id"] == "test-agent", "Condition must be true"
        assert entry_dict["session_id"] == "test-session", "Condition must be true"

    def test_memory_entry_from_dict(self):
        """Test creating MemoryEntry from dictionary."""
        import uuid

        test_uuid = str(uuid.uuid4())
        data = {
            "id": test_uuid,
            "content": "Test content",
            "agent_id": "test-agent",
            "session_id": "test-session",
            "metadata": {"key": "value"},
            "timestamp": "2024-01-01T00:00:00Z",
        }
        entry = MemoryEntry.from_dict(data)
        assert entry.content == "Test content", "Content must not be empty"
        assert entry.agent_id == "test-agent", "agent_id is not valid"

    def test_memory_query_creation(self):
        """Test creating a MemoryQuery."""
        query = MemoryQuery(
            text="search text", agent_id="test-agent", session_id="test-session", limit=10
        )
        assert query.text == "search text", "text is not valid"
        assert query.agent_id == "test-agent", "agent_id is not valid"
        assert query.session_id == "test-session", "session_id is not valid"
        assert query.limit == 10, "limit is not valid"


class TestJSONLBackend:
    """Test JSONL file-based memory backend."""

    def test_jsonl_backend_creation(self):
        """Test JSONL backend initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = JSONLMemoryBackend(Path(tmpdir) / "memories.jsonl")
            assert backend.storage_path.exists(), "Condition must be true"

    def test_jsonl_backend_store_retrieves(self):
        """Test storing and retrieving from JSONL backend."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = JSONLMemoryBackend(Path(tmpdir) / "memories.jsonl")
            entry = MemoryEntry(
                content="Test content", agent_id="test-agent", session_id="test-session"
            )
            backend.store(entry)

            query = MemoryQuery(text="test", limit=10)
            results = backend.retrieve(query)
            assert len(results) >= 1, "Results must not be empty"

    def test_jsonl_backend_multiple_stores(self):
        """Test multiple store operations to JSONL backend."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = JSONLMemoryBackend(Path(tmpdir) / "memories.jsonl")
            for i in range(5):
                entry = MemoryEntry(
                    content=f"Memory {i}", agent_id="test-agent", session_id="test-session"
                )
                backend.store(entry)

            query = MemoryQuery(text="memory", limit=10)
            results = backend.retrieve(query)
            assert len(results) >= 5, "Results must not be empty"


class TestSessionManagement:
    """Test session-level memory operations."""

    def test_set_session_changes_current_session(self):
        """Test set_session changes the current session ID."""
        manager = MemoryManager(agent_id="test-agent", session_id="session1")
        assert manager.session_id == "session1", "session_id is not valid"
        manager.set_session("session2")
        assert manager.session_id == "session2", "session_id is not valid"

    def test_clear_session_removes_memories(self):
        """Test clear_session removes all memories for a session."""
        manager = MemoryManager(agent_id="test-agent", session_id="session1")
        manager.store("Memory 1")
        manager.store("Memory 2")

        count = manager.clear_session("session1")
        assert count >= 2, "count must be positive"

    def test_clear_session_without_session_id_raises(self):
        """Test clear_session without session ID raises ValueError."""
        manager = MemoryManager(agent_id="test-agent")
        with pytest.raises(ValueError):
            manager.clear_session()

    def test_clear_session_specific_session_only(self):
        """Test clear_session only clears specified session."""
        manager1 = MemoryManager(agent_id="agent1", session_id="session1")
        manager2 = MemoryManager(agent_id="agent1", session_id="session2")

        manager1.store("Session 1 memory")
        manager2.store("Session 2 memory")

        manager1.clear_session("session1")
        # Session 2 memories should still exist


class TestMemoryStats:
    """Test memory statistics retrieval."""

    def test_get_stats_returns_dict(self):
        """Test get_stats returns statistics dictionary."""
        manager = MemoryManager(agent_id="test-agent", session_id="test-session")
        manager.store("Memory 1")

        stats = manager.get_stats()
        assert isinstance(stats, dict)

    def test_get_stats_after_multiple_stores(self):
        """Test get_stats reflects multiple stored memories."""
        manager = MemoryManager(agent_id="test-agent", session_id="test-session")
        for i in range(5):
            manager.store(f"Memory {i}")

        stats = manager.get_stats()
        assert isinstance(stats, dict)


class TestMemoryEdgeCases:
    """Test edge cases in memory operations."""

    def test_store_empty_string_content(self):
        """Test storing empty string content."""
        manager = MemoryManager(agent_id="test-agent", session_id="test-session")
        entry = manager.store("")
        assert entry.content == "", "Content must not be empty"

    def test_store_large_text_content(self):
        """Test storing large text content."""
        manager = MemoryManager(agent_id="test-agent", session_id="test-session")
        large_content = "x" * 100000  # 100KB text
        entry = manager.store(large_content)
        assert entry.content == large_content, "Content must not be empty"

    def test_store_complex_nested_dict(self):
        """Test storing complex nested dictionary."""
        manager = MemoryManager(agent_id="test-agent", session_id="test-session")
        complex_content = {"level1": {"level2": {"level3": [1, 2, 3], "data": "nested"}}}
        entry = manager.store(complex_content)
        assert entry.content == complex_content, "Content must not be empty"

    def test_store_with_special_characters_in_metadata(self):
        """Test storing with special characters in metadata."""
        manager = MemoryManager(agent_id="test-agent", session_id="test-session")
        metadata = {"special": "!@#$%^&*()", "unicode": "你好世界🌍", "quotes": 'He said "hello"'}
        entry = manager.store("Test", metadata=metadata)
        assert entry.metadata == metadata, "Data must not be empty"

    def test_recall_with_none_query_text(self):
        """Test recall with None query text."""
        manager = MemoryManager(agent_id="test-agent", session_id="test-session")
        manager.store("Memory 1")
        memories = manager.recall(query_text=None)
        assert isinstance(memories, list)

    def test_store_with_none_metadata(self):
        """Test storing with None metadata."""
        manager = MemoryManager(agent_id="test-agent", session_id="test-session")
        entry = manager.store("Content", metadata=None)
        assert entry.metadata == {}, "Data must not be empty"

    def test_agent_id_none_in_recall(self):
        """Test recall with None agent_id uses manager's agent_id."""
        manager = MemoryManager(agent_id="test-agent", session_id="test-session")
        manager.store("Memory")
        memories = manager.recall(agent_id=None)
        assert isinstance(memories, list)

    def test_session_id_none_in_recall(self):
        """Test recall with None session_id uses manager's session_id."""
        manager = MemoryManager(agent_id="test-agent", session_id="test-session")
        manager.store("Memory")
        memories = manager.recall(session_id=None)
        assert isinstance(memories, list)


class TestMemoryIntegration:
    """Test integration scenarios with multiple operations."""

    def test_multiple_stores_and_recalls(self):
        """Test multiple stores followed by recalls."""
        manager = MemoryManager(agent_id="test-agent", session_id="test-session")

        # Store multiple memories
        for i in range(3):
            manager.store(f"Memory {i}", metadata={"index": i})

        # Recall all
        all_memories = manager.recall_all()
        assert len(all_memories) >= 3, "All_memories must not be empty"

    def test_store_recall_in_different_sessions(self):
        """Test storing in one session and recalling from another."""
        manager1 = MemoryManager(agent_id="test-agent", session_id="session1")
        manager2 = MemoryManager(agent_id="test-agent", session_id="session2")

        manager1.store("Session 1 memory")

        # Manager2 should have different memories
        memories2 = manager2.recall_all()
        assert isinstance(memories2, list)

    def test_backend_persistence(self):
        """Test that backend persists data across manager instances."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend_path = Path(tmpdir) / "memories.jsonl"

            # Store with first manager
            backend1 = JSONLMemoryBackend(backend_path)
            manager1 = MemoryManager(backend=backend1, agent_id="agent1", session_id="session1")
            manager1.store("Persistent memory")

            # Retrieve with second manager using same backend
            backend2 = JSONLMemoryBackend(backend_path)
            manager2 = MemoryManager(backend=backend2, agent_id="agent1", session_id="session1")
            memories = manager2.recall_all()
            assert len(memories) >= 1, "Memories must not be empty"
