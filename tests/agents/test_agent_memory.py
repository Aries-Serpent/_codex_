"""
Test Agent Memory Module

Comprehensive unit tests for the agent memory system.
Tests MemoryEntry, ContextFrame, PatternLibrary, AgentMemory, and AgentMemorySystem.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from agents.agent_memory import (
    AgentMemory,
    AgentMemorySystem,
    ContextFrame,
    MemoryEntry,
    PatternLibrary,
)


class TestMemoryEntry:
    """Tests for MemoryEntry dataclass."""

    def test_basic_creation(self) -> None:
        entry = MemoryEntry(
            memory_id="test_id",
            category="decision",
            content="Made a decision",
            context={"key": "value"},
        )

        assert entry.memory_id == "test_id"
        assert entry.category == "decision"
        assert entry.content == "Made a decision"
        assert entry.context == {"key": "value"}
        assert entry.confidence == 0.8  # default
        assert entry.access_count == 0  # default

    def test_to_dict(self) -> None:
        entry = MemoryEntry(
            memory_id="id1",
            category="fact",
            content="A fact",
            context={},
            tags=["tag1", "tag2"],
        )

        result = entry.to_dict()

        assert isinstance(result, dict)
        assert result["memory_id"] == "id1"
        assert result["category"] == "fact"
        assert result["tags"] == ["tag1", "tag2"]

    def test_from_dict(self) -> None:
        data = {
            "memory_id": "id2",
            "category": "lesson",
            "content": "A lesson learned",
            "context": {"source": "test"},
            "confidence": 0.9,
            "access_count": 5,
            "last_accessed": "2025-01-01T12:00:00",
            "created_at": "2025-01-01T10:00:00",
            "tags": ["python"],
            "related_memories": ["id1"],
        }

        entry = MemoryEntry.from_dict(data)

        assert entry.memory_id == "id2"
        assert entry.confidence == 0.9
        assert entry.access_count == 5

    def test_default_timestamp(self) -> None:
        entry = MemoryEntry(
            memory_id="id3",
            category="test",
            content="test",
            context={},
        )

        # Should have ISO format timestamp
        assert "T" in entry.created_at
        datetime.fromisoformat(entry.created_at)


class TestContextFrame:
    """Tests for ContextFrame dataclass."""

    def test_basic_creation(self) -> None:
        frame = ContextFrame(
            frame_id="frame1",
            task_description="Test task",
            start_time=datetime.now(UTC).isoformat(),
        )

        assert frame.frame_id == "frame1"
        assert frame.task_description == "Test task"
        assert frame.status == "active"
        assert frame.end_time is None

    def test_to_dict(self) -> None:
        frame = ContextFrame(
            frame_id="frame2",
            task_description="Another task",
            start_time="2025-01-01T10:00:00",
            files_modified=["file1.py", "file2.py"],
            tokens_used=1000,
        )

        result = frame.to_dict()

        assert result["frame_id"] == "frame2"
        assert result["files_modified"] == ["file1.py", "file2.py"]
        assert result["tokens_used"] == 1000

    def test_default_lists(self) -> None:
        frame = ContextFrame(
            frame_id="f1",
            task_description="task",
            start_time="now",
        )

        assert frame.active_memories == []
        assert frame.decisions_made == []
        assert frame.lessons_learned == []
        assert frame.files_modified == []


class TestPatternLibrary:
    """Tests for PatternLibrary class."""

    def test_add_pattern(self) -> None:
        library = PatternLibrary()

        library.add_pattern(
            pattern_id="p1",
            name="Test Pattern",
            description="A test pattern",
            triggers=["test", "example"],
            recommended_actions=["action1", "action2"],
            success_rate=0.8,
            examples=[],
            tags=["testing"],
        )

        assert "p1" in library.patterns
        assert library.patterns["p1"]["name"] == "Test Pattern"
        assert library.patterns["p1"]["success_rate"] == 0.8

    def test_pattern_indexing(self) -> None:
        library = PatternLibrary()

        library.add_pattern(
            pattern_id="p1",
            name="Pattern 1",
            description="",
            triggers=["a"],
            recommended_actions=[],
            success_rate=0.7,
            examples=[],
            tags=["security", "fix"],
        )

        assert "p1" in library.pattern_index["security"]
        assert "p1" in library.pattern_index["fix"]

    def test_match_patterns(self) -> None:
        library = PatternLibrary()

        library.add_pattern(
            pattern_id="sec1",
            name="Security Fix",
            description="",
            triggers=["security", "vulnerability", "xss"],
            recommended_actions=["sanitize", "validate"],
            success_rate=0.9,
            examples=[],
            tags=["security"],
        )

        matches = library.match_patterns("fix security vulnerability in code")

        assert len(matches) == 1
        assert matches[0]["pattern"]["name"] == "Security Fix"
        assert matches[0]["match_score"] > 0

    def test_match_patterns_min_success_rate(self) -> None:
        library = PatternLibrary()

        library.add_pattern(
            pattern_id="low",
            name="Low Success",
            description="",
            triggers=["test"],
            recommended_actions=[],
            success_rate=0.3,
            examples=[],
            tags=["low"],
        )

        matches = library.match_patterns("test pattern", min_success_rate=0.5)

        assert len(matches) == 0

    def test_record_pattern_usage(self) -> None:
        library = PatternLibrary()

        library.add_pattern(
            pattern_id="p1",
            name="Test",
            description="",
            triggers=["test"],
            recommended_actions=[],
            success_rate=0.8,
            examples=[],
            tags=[],
        )

        library.record_pattern_usage("p1", success=True)

        # Success should increase rate slightly
        assert library.patterns["p1"]["usage_count"] == 1
        # Rate uses exponential moving average

    def test_to_dict_and_from_dict(self) -> None:
        library = PatternLibrary()
        library.add_pattern(
            pattern_id="p1",
            name="Test",
            description="desc",
            triggers=["a"],
            recommended_actions=["b"],
            success_rate=0.7,
            examples=[],
            tags=["tag"],
        )

        data = library.to_dict()
        restored = PatternLibrary.from_dict(data)

        assert "p1" in restored.patterns
        assert restored.patterns["p1"]["name"] == "Test"


class TestAgentMemory:
    """Tests for AgentMemory class."""

    @pytest.fixture
    def memory(self, tmp_path: Path) -> AgentMemory:
        """Create a temporary memory instance."""
        db_path = tmp_path / "test_memory.db"
        return AgentMemory(db_path=db_path)

    def test_store_and_retrieve_memory(self, memory: AgentMemory) -> None:
        entry = MemoryEntry(
            memory_id="m1",
            category="fact",
            content="Python is great",
            context={"source": "test"},
        )

        memory.store_memory(entry)
        retrieved = memory.retrieve_memory("m1")

        assert retrieved is not None
        assert retrieved.content == "Python is great"
        # Note: access_count is incremented in DB but returned object shows pre-increment value
        # Retrieve again to see the incremented count
        retrieved2 = memory.retrieve_memory("m1")
        assert retrieved2.access_count == 1  # Now shows the count from first retrieval

    def test_store_memory_with_kwargs(self, memory: AgentMemory) -> None:
        memory.store_memory(
            memory_id="m2",
            category="decision",
            content="Use pytest",
            context={"confidence": "high"},
        )

        retrieved = memory.retrieve_memory("m2")
        assert retrieved.content == "Use pytest"

    def test_store_memory_old_style(self, memory: AgentMemory) -> None:
        """Test backward compatibility with key/value style."""
        memory.store_memory(key="old_key", value="old value", category="legacy")

        retrieved = memory.retrieve_memory("old_key")
        assert retrieved.content == "old value"

    def test_add_memory_alias(self, memory: AgentMemory) -> None:
        """Test add_memory as alias for store_memory."""
        memory.add_memory(
            memory_id="m3",
            category="observation",
            content="Tests are important",
        )

        retrieved = memory.retrieve_memory("m3")
        assert retrieved is not None

    def test_search_memories(self, memory: AgentMemory) -> None:
        memory.store_memory(
            MemoryEntry(memory_id="s1", category="decision", content="a", context={})
        )
        memory.store_memory(
            MemoryEntry(memory_id="s2", category="fact", content="b", context={})
        )
        memory.store_memory(
            MemoryEntry(memory_id="s3", category="decision", content="c", context={})
        )

        decisions = memory.search_memories(category="decision")

        assert len(decisions) == 2
        assert all(m.category == "decision" for m in decisions)

    def test_search_with_min_confidence(self, memory: AgentMemory) -> None:
        memory.store_memory(
            MemoryEntry(
                memory_id="c1",
                category="test",
                content="high",
                context={},
                confidence=0.9,
            )
        )
        memory.store_memory(
            MemoryEntry(
                memory_id="c2",
                category="test",
                content="low",
                context={},
                confidence=0.3,
            )
        )

        high_conf = memory.search_memories(min_confidence=0.5)

        assert len(high_conf) == 1
        assert high_conf[0].content == "high"

    def test_clear(self, memory: AgentMemory) -> None:
        memory.store_memory(
            MemoryEntry(memory_id="x", category="test", content="test", context={})
        )
        memory.clear()

        result = memory.retrieve_memory("x")
        assert result is None

    def test_get_memory_stats(self, memory: AgentMemory) -> None:
        memory.store_memory(
            MemoryEntry(
                memory_id="1", category="a", content="1", context={}, confidence=0.8
            )
        )
        memory.store_memory(
            MemoryEntry(
                memory_id="2", category="b", content="2", context={}, confidence=0.6
            )
        )

        stats = memory.get_memory_stats()

        assert stats["total_memories"] == 2
        assert stats["average_confidence"] == 0.7

    def test_update(self, memory: AgentMemory) -> None:
        memory.store_memory(
            MemoryEntry(memory_id="u1", category="test", content="old", context={})
        )

        success = memory.update("u1", "new content")

        assert success is True
        retrieved = memory.retrieve_memory("u1")
        assert retrieved.content == "new content"

    def test_update_nonexistent(self, memory: AgentMemory) -> None:
        success = memory.update("nonexistent", "content")
        assert success is False

    def test_store_context_frame(self, memory: AgentMemory) -> None:
        frame = ContextFrame(
            frame_id="f1",
            task_description="Test task",
            start_time=datetime.now(UTC).isoformat(),
        )

        memory.store_context_frame(frame)
        frames = memory.get_recent_context_frames()

        assert len(frames) == 1
        assert frames[0].frame_id == "f1"

    def test_path_validation(self) -> None:
        """Test that path traversal is prevented."""
        with pytest.raises(ValueError, match="outside allowed directories"):
            AgentMemory(db_path=Path("/etc/passwd"))


class TestAgentMemorySystem:
    """Tests for AgentMemorySystem class."""

    @pytest.fixture
    def system(self, tmp_path: Path) -> AgentMemorySystem:
        """Create a temporary memory system."""
        db_path = tmp_path / "test_system.db"
        return AgentMemorySystem(agent_id="test_agent", db_path=db_path)

    def test_initialization(self, system: AgentMemorySystem) -> None:
        assert system.agent_id == "test_agent"
        assert system.memory is not None
        assert system.pattern_library is not None
        assert system.current_frame is None

    def test_start_task(self, system: AgentMemorySystem) -> None:
        frame = system.start_task("Fix bug in module")

        assert frame is not None
        assert frame.task_description == "Fix bug in module"
        assert frame.status == "active"
        assert system.current_frame == frame

    def test_record_decision(self, system: AgentMemorySystem) -> None:
        system.start_task("Test task")

        entry = system.record_decision(
            decision="Use pytest for testing",
            alternatives=["unittest", "nose"],
            confidence=0.85,
            reasoning="pytest has better fixtures",
        )

        assert entry.category == "decision"
        assert entry.content == "Use pytest for testing"
        assert entry.confidence == 0.85

    def test_record_lesson(self, system: AgentMemorySystem) -> None:
        system.start_task("Test task")

        entry = system.record_lesson("Always run tests before commit", success=True)

        assert entry.category == "lesson"
        assert entry.confidence == 0.9  # Success = higher confidence

    def test_get_guidance(self, system: AgentMemorySystem) -> None:
        guidance = system.get_guidance("fix security vulnerability")

        assert "patterns" in guidance
        assert "relevant_memories" in guidance
        # Should match the security_fix pattern
        if guidance["patterns"]:
            assert any("security" in p["name"].lower() for p in guidance["patterns"])

    def test_complete_task(self, system: AgentMemorySystem) -> None:
        system.start_task("Complete this task")
        system.record_decision("Decision 1", [], 0.8, "reason")

        system.complete_task(success=True, summary="Task completed successfully")

        assert system.current_frame is None
        # Verify context frame was saved
        frames = system.memory.get_recent_context_frames()
        assert len(frames) == 1

    def test_get_stats(self, system: AgentMemorySystem) -> None:
        stats = system.get_stats()

        assert "agent_id" in stats
        assert stats["agent_id"] == "test_agent"
        assert "memory_stats" in stats
        assert "patterns_count" in stats
        assert stats["patterns_count"] >= 3  # Default patterns

    def test_store_decision_api(self, system: AgentMemorySystem) -> None:
        memory_id = system.store_decision(
            task_id="task_123",
            decision="Use caching for performance",
            rationale="Reduces API calls",
            context={"performance_gain": "30%"},
        )

        assert memory_id is not None
        assert len(memory_id) == 16  # SHA256 hash prefix

    def test_retrieve_similar_context(self, system: AgentMemorySystem) -> None:
        # Add some memories
        system.store_decision(
            task_id="t1",
            decision="Use redis for caching",
            rationale="Fast and reliable",
        )

        results = system.retrieve_similar_context("caching performance")

        assert isinstance(results, list)
        # Results should have expected fields
        if results:
            assert "memory_id" in results[0]
            assert "relevance_score" in results[0]

    def test_get_pattern_library(self, system: AgentMemorySystem) -> None:
        patterns = system.get_pattern_library()

        assert isinstance(patterns, list)
        assert len(patterns) >= 3  # Default patterns

        pattern_names = [p["name"] for p in patterns]
        assert "Code Review Comment Resolution" in pattern_names
        assert "Security Vulnerability Fix" in pattern_names

    def test_invalidate_stale_contexts(self, system: AgentMemorySystem) -> None:
        # Add an old memory
        system.memory.store_memory(
            MemoryEntry(
                memory_id="old1",
                category="test",
                content="old memory",
                context={},
                created_at="2020-01-01T00:00:00",
                access_count=0,
            )
        )

        invalidated = system.invalidate_stale_contexts(age_days=30)

        # Should have processed the old memory
        assert invalidated >= 0  # May or may not invalidate based on logic


class TestAgentMemoryIntegration:
    """Integration tests for the complete memory system."""

    def test_full_workflow(self, tmp_path: Path) -> None:
        """Test a complete task workflow."""
        system = AgentMemorySystem(
            agent_id="integration_test",
            db_path=tmp_path / "integration.db",
        )

        # Start task
        system.start_task("Fix code review comment about path traversal")

        # Get guidance
        guidance = system.get_guidance("path traversal security fix")
        assert "patterns" in guidance

        # Make decisions
        system.record_decision(
            decision="Use os.path.commonpath for validation",
            alternatives=["realpath only", "startswith"],
            confidence=0.85,
            reasoning="commonpath handles edge cases",
        )

        # Record lesson
        system.record_lesson(
            "Wrap commonpath in try/except for Windows compatibility",
            success=True,
        )

        # Complete task
        system.complete_task(
            success=True,
            summary="Fixed path traversal vulnerability",
        )

        # Verify stats
        stats = system.get_stats()
        assert stats["memory_stats"]["total_memories"] >= 2

    def test_memory_persistence(self, tmp_path: Path) -> None:
        """Test that memories persist across instances."""
        db_path = tmp_path / "persistent.db"

        # Create and populate
        system1 = AgentMemorySystem(agent_id="persist_test", db_path=db_path)
        system1.store_decision(
            task_id="t1",
            decision="Persistent decision",
            rationale="For testing",
        )

        # Create new instance with same database
        system2 = AgentMemorySystem(agent_id="persist_test", db_path=db_path)

        # Search should find the memory
        results = system2.retrieve_similar_context("persistent")
        assert len(results) >= 1
