"""Tests for agent memory system."""

import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from codex.agents.memory import (
    JSONLMemoryBackend,
    MemoryEntry,
    MemoryManager,
    MemoryQuery,
    SQLiteMemoryBackend,
)


class TestJSONLBackend:
    """Tests for JSONL memory backend."""

    def test_store_and_retrieve(self):
        """Test basic store and retrieve operations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = JSONLMemoryBackend(Path(tmpdir) / "memories.jsonl")

            entry = MemoryEntry(
                content="Test memory",
                agent_id="agent-1",
                session_id="session-1",
            )
            backend.store(entry)

            query = MemoryQuery(agent_id="agent-1")
            results = backend.retrieve(query)

            assert len(results) == 1, "Results must not be empty"
            assert results[0].content == "Test memory", "Result must not be empty"

    def test_text_search(self):
        """Test text-based memory search."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = JSONLMemoryBackend(Path(tmpdir) / "memories.jsonl")

            backend.store(MemoryEntry(content="Python is great"))
            backend.store(MemoryEntry(content="JavaScript is okay"))

            query = MemoryQuery(text="Python")
            results = backend.retrieve(query)

            assert len(results) == 1, "Results must not be empty"
            assert "Python" in results[0].content, "Result must not be empty"

    def test_session_filter(self):
        """Test filtering by session ID."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = JSONLMemoryBackend(Path(tmpdir) / "memories.jsonl")

            backend.store(MemoryEntry(content="Memory 1", session_id="session-1"))
            backend.store(MemoryEntry(content="Memory 2", session_id="session-2"))

            query = MemoryQuery(session_id="session-1")
            results = backend.retrieve(query)

            assert len(results) == 1, "Results must not be empty"
            assert results[0].session_id == "session-1", "Result must not be empty"

    def test_delete(self):
        """Test memory deletion."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = JSONLMemoryBackend(Path(tmpdir) / "memories.jsonl")

            entry = MemoryEntry(content="To be deleted")
            backend.store(entry)

            deleted_first = backend.delete(entry.id)
            assert deleted_first is True, "deleted_first is not valid"

            deleted_second = backend.delete(entry.id)
            assert deleted_second is False, "deleted_second is not valid"

    def test_clear_session(self):
        """Test clearing all memories for a session."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = JSONLMemoryBackend(Path(tmpdir) / "memories.jsonl")

            backend.store(MemoryEntry(content="Memory 1", session_id="session-1"))
            backend.store(MemoryEntry(content="Memory 2", session_id="session-1"))
            backend.store(MemoryEntry(content="Memory 3", session_id="session-2"))

            count = backend.clear_session("session-1")
            assert count == 2, "Count must be greater than zero"

            query = MemoryQuery(session_id="session-2")
            results = backend.retrieve(query)
            assert len(results) == 1, "Results must not be empty"


class TestSQLiteBackend:
    """Tests for SQLite memory backend."""

    def test_store_and_retrieve(self):
        """Test basic store and retrieve operations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = SQLiteMemoryBackend(Path(tmpdir) / "memories.db")

            entry = MemoryEntry(
                content={"key": "value"},
                agent_id="agent-1",
                session_id="session-1",
                metadata={"importance": "high"},
            )
            backend.store(entry)

            query = MemoryQuery(agent_id="agent-1")
            results = backend.retrieve(query)

            assert len(results) == 1, "Results must not be empty"
            assert results[0].content == {"key": "value"}, "Result must not be empty"
            assert results[0].metadata["importance"] == "high", "Result must not be empty"

    def test_time_based_query(self):
        """Test querying by timestamp."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = SQLiteMemoryBackend(Path(tmpdir) / "memories.db")

            old_entry = MemoryEntry(content="Old memory")
            old_entry.timestamp = datetime.now(timezone.utc) - timedelta(days=7)
            backend.store(old_entry)

            backend.store(MemoryEntry(content="Recent memory"))

            query = MemoryQuery(since=datetime.now(timezone.utc) - timedelta(days=1))
            results = backend.retrieve(query)

            assert len(results) == 1, "Results must not be empty"
            assert results[0].content == "Recent memory", "Result must not be empty"

    def test_limit(self):
        """Test result limiting."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = SQLiteMemoryBackend(Path(tmpdir) / "memories.db")

            for i in range(10):
                backend.store(MemoryEntry(content=f"Memory {i}"))

            query = MemoryQuery(limit=5)
            results = backend.retrieve(query)

            assert len(results) == 5, "Results must not be empty"

    def test_stats(self):
        """Test statistics retrieval."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = SQLiteMemoryBackend(Path(tmpdir) / "memories.db")

            stats = backend.get_stats()
            assert stats["entry_count"] == 0, "Count must be greater than zero"

            backend.store(MemoryEntry(content="Test"))

            stats = backend.get_stats()
            assert stats["entry_count"] == 1, "Count must be greater than zero"
            assert stats["backend"] == "sqlite", "Condition must be true"


class TestMemoryManager:
    """Tests for high-level memory manager."""

    def test_store_and_recall(self):
        """Test storing and recalling memories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(
                agent_id="test-agent",
                session_id="test-session",
                storage_dir=Path(tmpdir),
            )

            manager.store("User prefers dark mode", metadata={"importance": "medium"})
            memories = manager.recall("dark mode")

            assert len(memories) > 0, "Memories must not be empty"
            assert "dark mode" in memories[0].content, "Content must not be empty"

    def test_session_management(self):
        """Test session switching."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(
                agent_id="test-agent",
                session_id="session-1",
                storage_dir=Path(tmpdir),
            )

            manager.store("Memory in session 1")

            manager.set_session("session-2")
            manager.store("Memory in session 2")

            # Recall from session 2
            memories = manager.recall_all()
            assert len(memories) == 1, "Memories must not be empty"
            assert memories[0].session_id == "session-2", "session_id is not valid"

            # Recall from session 1
            memories = manager.recall(session_id="session-1")
            assert len(memories) == 1, "Memories must not be empty"
            assert memories[0].session_id == "session-1", "session_id is not valid"

    def test_clear_session(self):
        """Test clearing session memories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(
                agent_id="test-agent",
                session_id="test-session",
                storage_dir=Path(tmpdir),
            )

            manager.store("Memory 1")
            manager.store("Memory 2")

            count = manager.clear_session()
            assert count == 2, "Count must be greater than zero"

            memories = manager.recall_all()
            assert len(memories) == 0, "Memories must not be empty"
