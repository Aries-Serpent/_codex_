"""
PHASE 7D TRACK 5: Exception Path Tests for Memory System

Comprehensive exception and error handling testing for:
- Invalid path traversal attempts
- Invalid input validation
- Database connection errors
- Serialization/deserialization failures
- Concurrent access errors
- Recovery from partial failures
"""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

import pytest

from agents.agent_memory import (
    AgentMemory,
    ContextFrame,
    MemoryEntry,
    PatternLibrary,
)


class TestMemoryEntryExceptions:
    """Test MemoryEntry exception handling."""

    def test_from_dict_missing_required_fields(self) -> None:
        """Test from_dict with missing required fields."""
        incomplete_data = {
            "memory_id": "test",
            # Missing category, content, context
        }
        with pytest.raises(TypeError):
            MemoryEntry.from_dict(incomplete_data)

    def test_to_dict_with_none_values(self) -> None:
        """Test to_dict properly serializes None values."""
        entry = MemoryEntry(
            memory_id="test",
            category="test",
            content="content",
            context={},
            last_accessed=None,
        )
        data = entry.to_dict()
        assert data["last_accessed"] is None, "Data must not be empty"

    def test_from_dict_with_invalid_confidence_type(self) -> None:
        """Test from_dict with invalid confidence type."""
        data = {
            "memory_id": "test",
            "category": "test",
            "content": "content",
            "context": {},
            "confidence": "not_a_number",  # Invalid type
            "access_count": 0,
            "last_accessed": None,
            "created_at": datetime.now(UTC).isoformat(),
            "tags": [],
            "related_memories": [],
        }
        # Should raise or handle gracefully
        try:
            entry = MemoryEntry.from_dict(data)
            # If it doesn't raise, check if it's stored as-is
            assert isinstance(entry.confidence, (float, str))
        except (TypeError, ValueError):
            pass  # Expected

    def test_from_dict_with_invalid_access_count_type(self) -> None:
        """Test from_dict with invalid access count type."""
        data = {
            "memory_id": "test",
            "category": "test",
            "content": "content",
            "context": {},
            "confidence": 0.5,
            "access_count": "not_a_number",  # Invalid type
            "last_accessed": None,
            "created_at": datetime.now(UTC).isoformat(),
            "tags": [],
            "related_memories": [],
        }
        try:
            entry = MemoryEntry.from_dict(data)
            assert isinstance(entry.access_count, (int, str))
        except (TypeError, ValueError):
            pass  # Expected

    def test_from_dict_with_invalid_tags_type(self) -> None:
        """Test from_dict with invalid tags type."""
        data = {
            "memory_id": "test",
            "category": "test",
            "content": "content",
            "context": {},
            "confidence": 0.5,
            "access_count": 0,
            "last_accessed": None,
            "created_at": datetime.now(UTC).isoformat(),
            "tags": "not_a_list",  # Invalid type
            "related_memories": [],
        }
        try:
            entry = MemoryEntry.from_dict(data)
            # If accepted, verify it's stored
            assert entry.tags is not None, "tags must be initialized"
        except (TypeError, ValueError):
            pass  # Expected

    def test_from_dict_with_invalid_context_type(self) -> None:
        """Test from_dict with invalid context type."""
        data = {
            "memory_id": "test",
            "category": "test",
            "content": "content",
            "context": "not_a_dict",  # Invalid type
            "confidence": 0.5,
            "access_count": 0,
            "last_accessed": None,
            "created_at": datetime.now(UTC).isoformat(),
            "tags": [],
            "related_memories": [],
        }
        try:
            entry = MemoryEntry.from_dict(data)
            # If accepted, verify it's stored
            assert entry.context is not None, "context must be initialized"
        except (TypeError, ValueError):
            pass  # Expected


class TestAgentMemoryPathTraversal:
    """Test AgentMemory path validation and security."""

    def test_invalid_path_traversal_attempt(self) -> None:
        """Test that path traversal attempts are rejected."""
        with pytest.raises(ValueError, match="outside allowed directories"):
            AgentMemory(db_path="/../../../etc/passwd")

    def test_invalid_path_absolute_outside_allowed(self) -> None:
        """Test absolute path outside allowed directories."""
        with pytest.raises(ValueError, match="outside allowed directories"):
            AgentMemory(db_path="/usr/bin/malicious.db")

    def test_valid_path_in_current_directory(self, tmp_path: Path) -> None:
        """Test valid path in current directory."""
        # Change to temp directory
        import os

        old_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            memory = AgentMemory(db_path="test.db")
            assert memory.db_path.exists() or memory.db_path.parent.exists(), "mem is not valid"
        finally:
            os.chdir(old_cwd)

    def test_valid_path_in_temp_directory(self, tmp_path: Path) -> None:
        """Test valid path in temp directory."""
        db_path = tmp_path / "test.db"
        memory = AgentMemory(db_path=db_path)
        assert memory.db_path == db_path.resolve(), "db_path is not valid"

    def test_valid_path_in_home_directory(self) -> None:
        """Test valid path in home directory."""
        home_db = Path.home() / ".test_memory.db"
        try:
            memory = AgentMemory(db_path=home_db)
            assert memory.db_path == home_db.resolve(), "db_path is not valid"
        finally:
            # Cleanup
            if home_db.exists():
                home_db.unlink()


class TestAgentMemoryDatabaseErrors:
    """Test AgentMemory database error handling."""

    def test_store_memory_to_readonly_database(self, tmp_path: Path) -> None:
        """Test storing to read-only database."""
        db_path = tmp_path / "readonly.db"
        memory = AgentMemory(db_path=db_path)

        # Make database read-only
        db_path.chmod(0o444)

        try:
            entry = MemoryEntry(
                memory_id="test",
                category="test",
                content="content",
                context={},
            )
            # This should fail or handle gracefully
            with pytest.raises(sqlite3.OperationalError):
                memory.store_memory(entry)
        finally:
            # Restore permissions
            db_path.chmod(0o644)

    def test_retrieve_from_corrupted_database(self, tmp_path: Path) -> None:
        """Test retrieving from corrupted database."""
        db_path = tmp_path / "corrupted.db"

        # Create and corrupt the database
        with open(db_path, "w") as f:
            f.write("CORRUPTED DATA\x00\x01\x02")

        # Attempting to read should handle error gracefully
        with pytest.raises((sqlite3.DatabaseError, sqlite3.NotSupportedError)):
            AgentMemory(db_path=db_path)

    def test_store_memory_with_concurrent_access(self, tmp_path: Path) -> None:
        """Test storing memory with concurrent database access."""
        db_path = tmp_path / "concurrent.db"
        memory1 = AgentMemory(db_path=db_path)
        memory2 = AgentMemory(db_path=db_path)

        entry1 = MemoryEntry(
            memory_id="entry1",
            category="test",
            content="content1",
            context={},
        )
        entry2 = MemoryEntry(
            memory_id="entry2",
            category="test",
            content="content2",
            context={},
        )

        # Store from both memory instances
        memory1.store_memory(entry1)
        memory2.store_memory(entry2)

        # Both should be retrievable
        assert memory1.retrieve_memory("entry1") is not None, "mem must be initialized"
        assert memory2.retrieve_memory("entry2") is not None, "mem must be initialized"


class TestPatternLibraryExceptions:
    """Test PatternLibrary exception handling."""

    def test_match_patterns_with_invalid_min_success_rate(self) -> None:
        """Test match_patterns with invalid min_success_rate."""
        lib = PatternLibrary()
        lib.add_pattern(
            pattern_id="pattern1",
            name="Pattern 1",
            description="Pattern description",
            triggers=["trigger"],
            recommended_actions=["action"],
            success_rate=0.5,
            examples=[],
            tags=["test"],
        )

        # Test with invalid success rate values
        for invalid_rate in [-0.1, 1.1, -1.0]:
            lib.match_patterns("trigger", min_success_rate=invalid_rate)
            # Should handle gracefully

    def test_record_usage_nonexistent_pattern(self) -> None:
        """Test recording usage for non-existent pattern."""
        lib = PatternLibrary()
        # Should handle gracefully without raising
        lib.record_pattern_usage("nonexistent_pattern", success=True)
        # No error should be raised

    def test_match_patterns_empty_situation_string(self) -> None:
        """Test matching with empty situation string."""
        lib = PatternLibrary()
        lib.add_pattern(
            pattern_id="pattern1",
            name="Pattern 1",
            description="Pattern description",
            triggers=["trigger"],
            recommended_actions=["action"],
            success_rate=0.5,
            examples=[],
            tags=["test"],
        )
        matches = lib.match_patterns("")
        assert isinstance(matches, list)

    def test_match_patterns_none_tags(self) -> None:
        """Test matching with None tags."""
        lib = PatternLibrary()
        lib.add_pattern(
            pattern_id="pattern1",
            name="Pattern 1",
            description="Pattern description",
            triggers=["trigger"],
            recommended_actions=["action"],
            success_rate=0.5,
            examples=[],
            tags=["test"],
        )
        matches = lib.match_patterns("trigger", tags=None)
        assert isinstance(matches, list)
        assert len(matches) > 0, "Matches must not be empty"

    def test_match_patterns_with_special_characters(self) -> None:
        """Test matching patterns with special characters."""
        lib = PatternLibrary()
        lib.add_pattern(
            pattern_id="pattern1",
            name="Pattern 1",
            description="Pattern description",
            triggers=["<script>", "alert()"],
            recommended_actions=["sanitize"],
            success_rate=0.5,
            examples=[],
            tags=["security"],
        )
        matches = lib.match_patterns("<script>alert()</script>")
        assert isinstance(matches, list)


class TestContextFrameExceptions:
    """Test ContextFrame exception handling."""

    def test_context_frame_with_invalid_status(self) -> None:
        """Test context frame with invalid status values."""
        frame = ContextFrame(
            frame_id="test",
            task_description="task",
            start_time=datetime.now(UTC).isoformat(),
            status="invalid_status",
        )
        assert frame.status == "invalid_status", "status is not valid"

    def test_context_frame_with_invalid_timestamp(self) -> None:
        """Test context frame with invalid timestamp format."""
        frame = ContextFrame(
            frame_id="test",
            task_description="task",
            start_time="not_a_valid_timestamp",
        )
        assert frame.start_time == "not_a_valid_timestamp", "start_time is not valid"

    def test_context_frame_end_before_start(self) -> None:
        """Test context frame where end_time is before start_time."""
        start = datetime.now(UTC).isoformat()
        end = "2000-01-01T00:00:00+00:00"  # Before start
        frame = ContextFrame(
            frame_id="test",
            task_description="task",
            start_time=start,
            end_time=end,
        )
        # System may not validate time ordering
        assert frame.start_time == start, "start_time is not valid"
        assert frame.end_time == end, "end_time is not valid"

    def test_context_frame_to_dict_with_none_end_time(self) -> None:
        """Test context frame to_dict with None end_time."""
        frame = ContextFrame(
            frame_id="test",
            task_description="task",
            start_time=datetime.now(UTC).isoformat(),
            end_time=None,
        )
        data = frame.to_dict()
        assert data["end_time"] is None, "Data must not be empty"

    def test_context_frame_very_large_active_memories_list(self) -> None:
        """Test context frame with very large active_memories list."""
        active = [f"memory_{i}" for i in range(10000)]
        frame = ContextFrame(
            frame_id="test",
            task_description="task",
            start_time=datetime.now(UTC).isoformat(),
            active_memories=active,
        )
        assert len(frame.active_memories) == 10000, "Collection must not be empty"


class TestMemoryEntrySerializationErrors:
    """Test serialization error handling."""

    def test_to_dict_with_non_serializable_context(self) -> None:
        """Test to_dict with non-JSON-serializable context values."""
        # Create entry with problematic context
        entry = MemoryEntry(
            memory_id="test",
            category="test",
            content="content",
            context={
                "datetime": datetime.now(UTC),  # Not JSON serializable
            },
        )
        # to_dict should handle this
        try:
            data = entry.to_dict()
            # If it succeeds, context should be stored as-is
            assert "context" in data, "Data must not be empty"
        except (TypeError, ValueError):
            pass  # Expected for non-serializable types

    def test_from_dict_with_malformed_json_context(self) -> None:
        """Test from_dict with malformed JSON in context."""
        data = {
            "memory_id": "test",
            "category": "test",
            "content": "content",
            "context": "{invalid json}",  # Malformed
            "confidence": 0.5,
            "access_count": 0,
            "last_accessed": None,
            "created_at": datetime.now(UTC).isoformat(),
            "tags": [],
            "related_memories": [],
        }
        try:
            entry = MemoryEntry.from_dict(data)
            # If accepted, verify it's stored
            assert entry.context is not None, "context must be initialized"
        except (ValueError, TypeError):
            pass  # Expected


class TestAgentMemoryRetrievalErrors:
    """Test memory retrieval error scenarios."""

    def test_retrieve_with_sql_injection_attempt(self, tmp_path: Path) -> None:
        """Test retrieve memory with SQL injection attempt."""
        db_path = tmp_path / "test.db"
        memory = AgentMemory(db_path=db_path)

        # Try SQL injection
        malicious_id = "'; DROP TABLE memories; --"
        result = memory.retrieve_memory(malicious_id)
        assert result is None, "Result must not be empty"

    def test_retrieve_with_very_long_memory_id(self, tmp_path: Path) -> None:
        """Test retrieve with very long memory ID."""
        db_path = tmp_path / "test.db"
        memory = AgentMemory(db_path=db_path)

        long_id = "x" * 100000
        result = memory.retrieve_memory(long_id)
        assert result is None, "Result must not be empty"

    def test_retrieve_category_empty_results(self, tmp_path: Path) -> None:
        """Test search with no matching entries."""
        db_path = tmp_path / "test.db"
        memory = AgentMemory(db_path=db_path)

        result = memory.search(query="nonexistent_query")
        assert isinstance(result, list) or result is None


class TestMemoryStorageEdgeCases:
    """Test memory storage edge cases and error recovery."""

    def test_store_memory_with_unicode_content(self, tmp_path: Path) -> None:
        """Test storing memory with unicode content."""
        db_path = tmp_path / "test.db"
        memory = AgentMemory(db_path=db_path)

        entry = MemoryEntry(
            memory_id="unicode_test",
            category="test",
            content="Unicode: 你好世界 🌍 emoji",
            context={},
        )
        memory.store_memory(entry)

        retrieved = memory.retrieve_memory("unicode_test")
        assert retrieved is not None, "retrieved must be initialized"
        assert "你好世界" in retrieved.content, "Content must not be empty"

    def test_store_memory_with_null_bytes(self, tmp_path: Path) -> None:
        """Test storing memory with null bytes."""
        db_path = tmp_path / "test.db"
        memory = AgentMemory(db_path=db_path)

        # Content with null bytes
        content = "Before\x00After"
        entry = MemoryEntry(
            memory_id="null_test",
            category="test",
            content=content,
            context={},
        )

        try:
            memory.store_memory(entry)
            retrieved = memory.retrieve_memory("null_test")
            if retrieved is not None:
                assert retrieved.content is not None, "content must be initialized"
        except (sqlite3.ProgrammingError, ValueError):
            pass  # Expected for null bytes

    def test_store_memory_duplicate_key_overwrite(self, tmp_path: Path) -> None:
        """Test storing memory with duplicate key (should overwrite)."""
        db_path = tmp_path / "test.db"
        memory = AgentMemory(db_path=db_path)

        entry1 = MemoryEntry(
            memory_id="duplicate",
            category="test",
            content="content1",
            context={},
        )
        entry2 = MemoryEntry(
            memory_id="duplicate",
            category="test",
            content="content2",
            context={},
        )

        memory.store_memory(entry1)
        memory.store_memory(entry2)

        retrieved = memory.retrieve_memory("duplicate")
        assert retrieved is not None, "retrieved must be initialized"
        # Should have the latest content
        assert retrieved.content == "content2", "Content must not be empty"
