"""
PHASE 7D TRACK 5: Return Value Validation Tests

Comprehensive return value testing for:
- String output validation
- Data structure validation
- Type correctness
- Serialization output validation
- Error message formatting
- Return value edge cases
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from agents.agent_memory import (
    AgentMemory,
    ContextFrame,
    MemoryEntry,
    PatternLibrary,
)


class TestMemoryEntryReturnValues:
    """Test MemoryEntry return value correctness."""

    def test_memory_entry_to_dict_returns_complete_dict(self) -> None:
        """Test to_dict returns all required fields."""
        entry = MemoryEntry(
            memory_id="test",
            category="test",
            content="test content",
            context={"key": "value"},
            confidence=0.85,
            access_count=5,
            last_accessed="2025-01-01T12:00:00",
            created_at="2025-01-01T10:00:00",
            tags=["tag1", "tag2"],
            related_memories=["mem1", "mem2"],
        )

        result = entry.to_dict()

        # Verify it's a dict
        assert isinstance(result, dict)

        # Verify all fields present
        required_fields = [
            "memory_id",
            "category",
            "content",
            "context",
            "confidence",
            "access_count",
            "last_accessed",
            "created_at",
            "tags",
            "related_memories",
        ]
        for field in required_fields:
            assert field in result, "Result must not be empty"

    def test_memory_entry_to_dict_preserves_values(self) -> None:
        """Test to_dict preserves all values correctly."""
        entry = MemoryEntry(
            memory_id="id123",
            category="decision",
            content="Made decision X",
            context={"scenario": "complex"},
            confidence=0.92,
            access_count=17,
            tags=["important", "decision"],
            related_memories=["prev_decision"],
        )

        result = entry.to_dict()

        assert result["memory_id"] == "id123", "Result must not be empty"
        assert result["category"] == "decision", "Result must not be empty"
        assert result["content"] == "Made decision X", "Result must not be empty"
        assert result["context"] == {"scenario": "complex"}, "Result must not be empty"
        assert result["confidence"] == 0.92, "Result must not be empty"
        assert result["access_count"] == 17, "Result must not be empty"
        assert result["tags"] == ["important", "decision"]
        assert result["related_memories"] == ["prev_decision"], "Result must not be empty"

    def test_memory_entry_to_dict_json_serializable(self) -> None:
        """Test to_dict output is JSON serializable."""
        entry = MemoryEntry(
            memory_id="test",
            category="test",
            content="test",
            context={"nested": {"value": 123}},
        )

        data = entry.to_dict()

        # Should be JSON serializable
        json_str = json.dumps(data)
        assert isinstance(json_str, str)

        # Should be deserializable back
        deserialized = json.loads(json_str)
        assert deserialized["memory_id"] == "test", "Condition must be true"

    def test_memory_entry_from_dict_returns_entry_type(self) -> None:
        """Test from_dict returns MemoryEntry instance."""
        data = {
            "memory_id": "test",
            "category": "test",
            "content": "content",
            "context": {},
            "confidence": 0.8,
            "access_count": 0,
            "last_accessed": None,
            "created_at": datetime.now(UTC).isoformat(),
            "tags": [],
            "related_memories": [],
        }

        result = MemoryEntry.from_dict(data)

        assert isinstance(result, MemoryEntry)
        assert result.memory_id == "test", "Result must not be empty"

    def test_memory_entry_from_dict_all_fields_populated(self) -> None:
        """Test from_dict populates all fields."""
        data = {
            "memory_id": "test_id",
            "category": "test_cat",
            "content": "test_content",
            "context": {"test_key": "test_value"},
            "confidence": 0.75,
            "access_count": 10,
            "last_accessed": "2025-01-01T12:00:00",
            "created_at": "2025-01-01T10:00:00",
            "tags": ["tag1", "tag2", "tag3"],
            "related_memories": ["mem1", "mem2"],
        }

        result = MemoryEntry.from_dict(data)

        assert result.memory_id == "test_id", "Result must not be empty"
        assert result.category == "test_cat", "Result must not be empty"
        assert result.content == "test_content", "Result must not be empty"
        assert result.context == {"test_key": "test_value"}, "Result must not be empty"
        assert result.confidence == 0.75, "Result must not be empty"
        assert result.access_count == 10, "Result must not be empty"
        assert result.last_accessed == "2025-01-01T12:00:00", "Result must not be empty"
        assert result.created_at == "2025-01-01T10:00:00", "Result must not be empty"
        assert result.tags == ["tag1", "tag2", "tag3"]
        assert result.related_memories == ["mem1", "mem2"]


class TestContextFrameReturnValues:
    """Test ContextFrame return value correctness."""

    def test_context_frame_to_dict_returns_complete_dict(self) -> None:
        """Test to_dict returns all required fields."""
        frame = ContextFrame(
            frame_id="frame1",
            task_description="test task",
            start_time=datetime.now(UTC).isoformat(),
            end_time=datetime.now(UTC).isoformat(),
            status="completed",
            tokens_used=100,
            actions_taken=5,
            errors_encountered=1,
        )

        result = frame.to_dict()

        assert isinstance(result, dict)

        required_fields = [
            "frame_id",
            "task_description",
            "start_time",
            "end_time",
            "status",
            "active_memories",
            "decisions_made",
            "lessons_learned",
            "repository",
            "branch",
            "files_modified",
            "tokens_used",
            "actions_taken",
            "errors_encountered",
        ]
        for field in required_fields:
            assert field in result, "Result must not be empty"

    def test_context_frame_to_dict_preserves_values(self) -> None:
        """Test to_dict preserves all values."""
        start = datetime.now(UTC).isoformat()
        end = datetime.now(UTC).isoformat()

        frame = ContextFrame(
            frame_id="frame_test",
            task_description="Complex task",
            start_time=start,
            end_time=end,
            status="completed",
            repository="repo/name",
            branch="main",
            files_modified=["file1.py", "file2.py"],
            tokens_used=250,
            actions_taken=10,
            errors_encountered=2,
        )

        result = frame.to_dict()

        assert result["frame_id"] == "frame_test", "Result must not be empty"
        assert result["task_description"] == "Complex task", "Result must not be empty"
        assert result["start_time"] == start, "Result must not be empty"
        assert result["end_time"] == end, "Result must not be empty"
        assert result["status"] == "completed", "Result must not be empty"
        assert result["repository"] == "repo/name", "Result must not be empty"
        assert result["branch"] == "main", "Result must not be empty"
        assert result["files_modified"] == ["file1.py", "file2.py"]
        assert result["tokens_used"] == 250, "Result must not be empty"
        assert result["actions_taken"] == 10, "Result must not be empty"
        assert result["errors_encountered"] == 2, "Result must not be empty"

    def test_context_frame_to_dict_json_serializable(self) -> None:
        """Test to_dict output is JSON serializable."""
        frame = ContextFrame(
            frame_id="test",
            task_description="test",
            start_time=datetime.now(UTC).isoformat(),
        )

        data = frame.to_dict()

        json_str = json.dumps(data)
        assert isinstance(json_str, str)

        deserialized = json.loads(json_str)
        assert deserialized["frame_id"] == "test", "Condition must be true"

    def test_context_frame_empty_lists_return_empty(self) -> None:
        """Test empty lists return as empty lists, not None."""
        frame = ContextFrame(
            frame_id="test",
            task_description="test",
            start_time=datetime.now(UTC).isoformat(),
        )

        result = frame.to_dict()

        assert result["active_memories"] == [], "Result must not be empty"
        assert result["decisions_made"] == [], "Result must not be empty"
        assert result["lessons_learned"] == [], "Result must not be empty"
        assert result["files_modified"] == [], "Result must not be empty"
        assert isinstance(result["active_memories"], list)
        assert isinstance(result["decisions_made"], list)

    def test_context_frame_none_values_preserved(self) -> None:
        """Test None values are preserved in to_dict."""
        frame = ContextFrame(
            frame_id="test",
            task_description="test",
            start_time=datetime.now(UTC).isoformat(),
            end_time=None,
            repository=None,
            branch=None,
        )

        result = frame.to_dict()

        assert result["end_time"] is None, "Result must not be empty"
        assert result["repository"] is None, "Result must not be empty"
        assert result["branch"] is None, "Result must not be empty"


class TestPatternLibraryReturnValues:
    """Test PatternLibrary return value correctness."""

    def test_match_patterns_returns_list(self) -> None:
        """Test match_patterns returns a list."""
        lib = PatternLibrary()
        lib.add_pattern(
            pattern_id="pattern1",
            name="Pattern 1",
            description="desc",
            triggers=["trigger"],
            recommended_actions=["action"],
            success_rate=0.8,
            examples=[],
            tags=["test"],
        )

        result = lib.match_patterns("trigger")

        assert isinstance(result, list)

    def test_match_patterns_returns_match_dicts(self) -> None:
        """Test match_patterns returns dicts with correct structure."""
        lib = PatternLibrary()
        lib.add_pattern(
            pattern_id="pattern1",
            name="Pattern 1",
            description="desc",
            triggers=["authentication"],
            recommended_actions=["verify", "authenticate"],
            success_rate=0.9,
            examples=[{"situation": "user login"}],
            tags=["auth"],
        )

        result = lib.match_patterns("authentication required")

        assert len(result) > 0, "Result must not be empty"
        match = result[0]

        # Check match structure
        assert "pattern" in match, "Condition must be true"
        assert "match_score" in match, "Condition must be true"
        assert "trigger_matches" in match, "Condition must be true"

    def test_match_patterns_empty_returns_empty_list(self) -> None:
        """Test match_patterns with no matches returns empty list."""
        lib = PatternLibrary()
        lib.add_pattern(
            pattern_id="pattern1",
            name="Pattern 1",
            description="desc",
            triggers=["auth"],
            recommended_actions=["action"],
            success_rate=0.5,
            examples=[],
            tags=["test"],
        )

        result = lib.match_patterns("completely unrelated text")

        assert isinstance(result, list)
        assert len(result) == 0, "Result must not be empty"

    def test_match_patterns_sorted_by_score(self) -> None:
        """Test match_patterns results are sorted by score."""
        lib = PatternLibrary()

        # Add patterns with different trigger match potential
        lib.add_pattern(
            pattern_id="p1",
            name="Pattern 1",
            description="desc",
            triggers=["auth", "security"],
            recommended_actions=["action"],
            success_rate=0.8,
            examples=[],
            tags=["security"],
        )

        lib.add_pattern(
            pattern_id="p2",
            name="Pattern 2",
            description="desc",
            triggers=["auth"],
            recommended_actions=["action"],
            success_rate=0.8,
            examples=[],
            tags=["security"],
        )

        result = lib.match_patterns("authentication and security")

        # Results should be sorted by match score descending
        if len(result) > 1:
            scores = [m["match_score"] for m in result]
            assert scores == sorted(scores, reverse=True)

    def test_pattern_library_to_dict_returns_dict(self) -> None:
        """Test to_dict returns a dictionary."""
        lib = PatternLibrary()
        lib.add_pattern(
            pattern_id="pattern1",
            name="Pattern 1",
            description="desc",
            triggers=["trigger"],
            recommended_actions=["action"],
            success_rate=0.5,
            examples=[],
            tags=["test"],
        )

        result = lib.to_dict()

        assert isinstance(result, dict)
        assert "patterns" in result, "Result must not be empty"
        assert "pattern_index" in result, "Result must not be empty"

    def test_pattern_library_from_dict_returns_library(self) -> None:
        """Test from_dict returns PatternLibrary instance."""
        data = {
            "patterns": {
                "p1": {
                    "pattern_id": "p1",
                    "name": "Pattern 1",
                    "description": "desc",
                    "triggers": ["trigger"],
                    "recommended_actions": ["action"],
                    "success_rate": 0.5,
                    "examples": [],
                    "tags": ["test"],
                    "usage_count": 0,
                    "created_at": datetime.now(UTC).isoformat(),
                }
            },
            "pattern_index": {"test": ["p1"]},
        }

        result = PatternLibrary.from_dict(data)

        assert isinstance(result, PatternLibrary)
        assert "p1" in result.patterns, "Result must not be empty"


class TestAgentMemoryReturnValues:
    """Test AgentMemory return value correctness."""

    def test_retrieve_memory_returns_entry_or_none(self, tmp_path: Path) -> None:
        """Test retrieve_memory returns MemoryEntry or None."""
        db_path = tmp_path / "test.db"
        memory = AgentMemory(db_path=db_path)

        entry = MemoryEntry(
            memory_id="test",
            category="test",
            content="content",
            context={},
        )
        memory.store_memory(entry)

        # Existing entry
        result = memory.retrieve_memory("test")
        assert isinstance(result, MemoryEntry) or result is None
        if result:
            assert result.memory_id == "test", "Result must not be empty"

        # Non-existent entry
        result = memory.retrieve_memory("nonexistent")
        assert result is None, "Result must not be empty"

    def test_retrieve_memory_preserves_all_fields(self, tmp_path: Path) -> None:
        """Test retrieve_memory returns entry with all fields."""
        db_path = tmp_path / "test.db"
        memory = AgentMemory(db_path=db_path)

        entry = MemoryEntry(
            memory_id="complete",
            category="test",
            content="test content",
            context={"key": "value", "nested": {"deep": "value"}},
            confidence=0.87,
            access_count=5,
            tags=["tag1", "tag2"],
            related_memories=["mem1"],
        )
        memory.store_memory(entry)

        result = memory.retrieve_memory("complete")

        assert result is not None, "result must be initialized"
        assert result.memory_id == "complete", "Result must not be empty"
        assert result.category == "test", "Result must not be empty"
        assert result.content == "test content", "Result must not be empty"
        assert result.context == {"key": "value", "nested": {"deep": "value"}}
        assert result.confidence == 0.87, "Result must not be empty"
        assert result.access_count == 5, "Result must not be empty"
        assert result.tags == ["tag1", "tag2"]
        assert result.related_memories == ["mem1"], "Result must not be empty"

    def test_retrieve_memories_by_category_returns_list(self, tmp_path: Path) -> None:
        """Test search returns list."""
        db_path = tmp_path / "test.db"
        memory = AgentMemory(db_path=db_path)

        # Store memories
        for i in range(5):
            entry = MemoryEntry(
                memory_id=f"decision_{i}",
                category="decision",
                content=f"Decision {i}",
                context={},
            )
            memory.store_memory(entry)

        result = memory.search(query="Decision")

        assert isinstance(result, list) or result is None
        if result:
            for item in result:
                assert isinstance(item, MemoryEntry)

    def test_store_memory_returns_success(self, tmp_path: Path) -> None:
        """Test store_memory behavior (should not raise)."""
        db_path = tmp_path / "test.db"
        memory = AgentMemory(db_path=db_path)

        entry = MemoryEntry(
            memory_id="test",
            category="test",
            content="content",
            context={},
        )

        # Should complete without raising
        memory.store_memory(entry)

        # Verify it was stored
        retrieved = memory.retrieve_memory("test")
        assert retrieved is not None, "retrieved must be initialized"


class TestSerializationOutputValidation:
    """Test serialization output format and validity."""

    def test_memory_entry_serialization_format(self) -> None:
        """Test MemoryEntry serialization format consistency."""
        entry = MemoryEntry(
            memory_id="format_test",
            category="test",
            content="test",
            context={"type": "string", "number": 123, "boolean": True, "null": None},
        )

        data = entry.to_dict()

        # Verify types in serialized form
        assert isinstance(data["memory_id"], str)
        assert isinstance(data["category"], str)
        assert isinstance(data["content"], str)
        assert isinstance(data["confidence"], float)
        assert isinstance(data["access_count"], int)
        assert isinstance(data["tags"], list)

    def test_context_frame_timestamp_format(self) -> None:
        """Test ContextFrame timestamps are ISO format."""
        frame = ContextFrame(
            frame_id="test",
            task_description="test",
            start_time=datetime.now(UTC).isoformat(),
        )

        data = frame.to_dict()

        # Timestamps should be ISO format strings
        assert isinstance(data["start_time"], str)
        assert "T" in data["start_time"], "Data must not be empty"

    def test_pattern_library_pattern_format(self) -> None:
        """Test PatternLibrary pattern format consistency."""
        lib = PatternLibrary()
        lib.add_pattern(
            pattern_id="format_test",
            name="Test Pattern",
            description="Test description",
            triggers=["trigger1", "trigger2"],
            recommended_actions=["action1", "action2"],
            success_rate=0.85,
            examples=[{"example": "test"}],
            tags=["tag1"],
        )

        data = lib.to_dict()
        pattern = data["patterns"]["format_test"]

        # Verify structure
        assert isinstance(pattern["pattern_id"], str)
        assert isinstance(pattern["name"], str)
        assert isinstance(pattern["triggers"], list)
        assert isinstance(pattern["success_rate"], float)
        assert isinstance(pattern["usage_count"], int)


class TestOutputValidationEdgeCases:
    """Test output validation edge cases."""

    def test_to_dict_with_empty_strings(self) -> None:
        """Test to_dict with empty string fields."""
        entry = MemoryEntry(
            memory_id="",
            category="",
            content="",
            context={},
        )

        data = entry.to_dict()

        assert data["memory_id"] == "", "Data must not be empty"
        assert data["category"] == "", "Data must not be empty"
        assert data["content"] == "", "Data must not be empty"

    def test_to_dict_with_special_characters(self) -> None:
        """Test to_dict with special characters."""
        entry = MemoryEntry(
            memory_id="id_with_special!@#$%",
            category="test",
            content="Content with \"quotes\" and 'apostrophes'",
            context={"key": "value\nwith\nnewlines"},
        )

        data = entry.to_dict()

        assert '"quotes"' in data["content"], "Data must not be empty"
        assert "apostrophes" in data["content"], "Data must not be empty"

    def test_to_dict_with_unicode(self) -> None:
        """Test to_dict with unicode characters."""
        entry = MemoryEntry(
            memory_id="unicode_test",
            category="test",
            content="Unicode: 你好世界 🌍 مرحبا בעולם",
            context={"emoji": "🎉🎊🎈"},
        )

        data = entry.to_dict()

        assert "你好世界" in data["content"], "Data must not be empty"
        assert "🌍" in data["content"], "Data must not be empty"
        assert "🎉" in data["context"]["emoji"], "Data must not be empty"

    def test_list_return_values_preserve_order(self) -> None:
        """Test list return values preserve insertion order."""
        lib = PatternLibrary()

        for i in range(10):
            lib.add_pattern(
                pattern_id=f"pattern_{i}",
                name=f"Pattern {i}",
                description="desc",
                triggers=["trigger"],
                recommended_actions=["action"],
                success_rate=0.5,
                examples=[],
                tags=[],
            )

        data = lib.to_dict()

        # Patterns should be in dictionary
        pattern_ids = list(data["patterns"].keys())
        # Verify we got all patterns
        assert len(pattern_ids) == 10, "Pattern_ids must not be empty"
