"""
Mutation Testing - Agent Memory Module
Phase B Track 1 Lanes 4-5: Strengthened Tests for Mutation Coverage

This test module focuses on catching mutations in critical code paths:
- Boundary condition mutations (comparison operators)
- Default value mutations (numeric and string)
- Collection operation mutations
- Control flow mutations
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from agents.agent_memory import (
    AgentMemory,
    AgentMemorySystem,
    ContextFrame,
    MemoryEntry,
    PatternLibrary,
)


class TestMemoryEntryMutationKillers:
    """Tests specifically designed to catch mutations in MemoryEntry."""

    def test_confidence_default_value_is_exactly_0_8(self) -> None:
        """Catch mutation: confidence: float = 0.8 → 0.7 or 0.9"""
        entry = MemoryEntry(
            memory_id="test",
            category="decision",
            content="test",
            context={},
        )
        # Exact equality check catches numeric mutations
        assert entry.confidence == 0.8
        assert entry.confidence != 0.7
        assert entry.confidence != 0.9

    def test_access_count_default_is_exactly_zero(self) -> None:
        """Catch mutation: access_count: int = 0 → 1"""
        entry = MemoryEntry(
            memory_id="test",
            category="decision",
            content="test",
            context={},
        )
        # Exact zero check catches off-by-one mutations
        assert entry.access_count == 0
        assert entry.access_count != 1
        assert entry.access_count >= 0

    def test_confidence_boundary_just_below_minimum(self) -> None:
        """Catch mutation: >= 0.5 → > 0.5"""
        entry = MemoryEntry(
            memory_id="test",
            category="decision",
            content="test",
            context={"confidence_threshold": 0.5},
            confidence=0.49,
        )
        # Test just below typical minimum threshold
        assert entry.confidence == 0.49
        assert entry.confidence < 0.5

    def test_confidence_boundary_at_minimum(self) -> None:
        """Catch mutation: >= 0.5 → > 0.5 (boundary test)"""
        entry = MemoryEntry(
            memory_id="test",
            category="decision",
            content="test",
            context={},
            confidence=0.5,
        )
        # Test exact boundary
        assert entry.confidence == 0.5
        assert entry.confidence >= 0.5
        assert not (entry.confidence < 0.5)

    def test_confidence_boundary_just_above_minimum(self) -> None:
        """Catch mutation: >= 0.5 → > 0.5 (upper boundary)"""
        entry = MemoryEntry(
            memory_id="test",
            category="decision",
            content="test",
            context={},
            confidence=0.51,
        )
        assert entry.confidence == 0.51
        assert entry.confidence > 0.5

    def test_default_tags_list_is_empty_not_none(self) -> None:
        """Catch mutation: default_factory=list → None"""
        entry = MemoryEntry(
            memory_id="test",
            category="decision",
            content="test",
            context={},
        )
        assert entry.tags == []
        assert entry.tags is not None
        assert isinstance(entry.tags, list)

    def test_default_related_memories_list_is_empty_not_none(self) -> None:
        """Catch mutation: default_factory=list → None"""
        entry = MemoryEntry(
            memory_id="test",
            category="decision",
            content="test",
            context={},
        )
        assert entry.related_memories == []
        assert entry.related_memories is not None
        assert isinstance(entry.related_memories, list)

    def test_last_accessed_default_is_none_not_empty_string(self) -> None:
        """Catch mutation: last_accessed: Optional[str] = None → ""  """
        entry = MemoryEntry(
            memory_id="test",
            category="decision",
            content="test",
            context={},
        )
        assert entry.last_accessed is None
        assert entry.last_accessed != ""


class TestContextFrameStatusMutations:
    """Tests to catch mutations in ContextFrame status field."""

    def test_default_status_is_exactly_active(self) -> None:
        """Catch mutation: status: str = "active" → "pending" or "completed"  """
        frame = ContextFrame(
            frame_id="f1",
            task_description="task",
            start_time="2025-01-01T10:00:00",
        )
        assert frame.status == "active"
        assert frame.status != "pending"
        assert frame.status != "completed"
        assert frame.status != "failed"

    def test_default_end_time_is_none(self) -> None:
        """Catch mutation: end_time: Optional[str] = None → ""  """
        frame = ContextFrame(
            frame_id="f1",
            task_description="task",
            start_time="2025-01-01T10:00:00",
        )
        assert frame.end_time is None

    @pytest.mark.parametrize(
        "status,expected",
        [
            ("active", True),
            ("completed", True),
            ("failed", True),
            ("paused", True),
            ("pending", True),  # Not in docstring but valid
            ("unknown", True),  # No validation in dataclass
        ],
    )
    def test_status_string_values(self, status: str, expected: bool) -> None:
        """Test that status can be set to various values (no validation)."""
        frame = ContextFrame(
            frame_id="f1",
            task_description="task",
            start_time="2025-01-01T10:00:00",
            status=status,
        )
        assert frame.status == status

    def test_default_numeric_fields_are_zero_not_none(self) -> None:
        """Catch mutation: tokens_used/actions_taken/errors = 0 → None or 1"""
        frame = ContextFrame(
            frame_id="f1",
            task_description="task",
            start_time="2025-01-01T10:00:00",
        )
        assert frame.tokens_used == 0
        assert frame.actions_taken == 0
        assert frame.errors_encountered == 0
        assert frame.tokens_used is not None
        assert isinstance(frame.tokens_used, int)


class TestPatternLibraryMutationKillers:
    """Tests specifically designed to catch mutations in PatternLibrary."""

    def test_match_patterns_min_success_rate_boundary_exact(self) -> None:
        """Catch mutation: success_rate < min_success_rate → <="""
        library = PatternLibrary()

        library.add_pattern(
            pattern_id="exactly_at_threshold",
            name="Exactly at Threshold",
            description="",
            triggers=["test"],
            recommended_actions=[],
            success_rate=0.5,  # Exactly at threshold
            examples=[],
            tags=[],
        )

        # With min_success_rate=0.5, patterns with success_rate=0.5 should PASS
        matches = library.match_patterns("test", min_success_rate=0.5)
        assert len(matches) == 1  # Should include the pattern at boundary

    def test_match_patterns_min_success_rate_boundary_just_below(self) -> None:
        """Catch mutation: success_rate < min_success_rate → <="""
        library = PatternLibrary()

        library.add_pattern(
            pattern_id="below_threshold",
            name="Below Threshold",
            description="",
            triggers=["test"],
            recommended_actions=[],
            success_rate=0.49,  # Just below threshold
            examples=[],
            tags=[],
        )

        # With min_success_rate=0.5, patterns with success_rate=0.49 should FAIL
        matches = library.match_patterns("test", min_success_rate=0.5)
        assert len(matches) == 0  # Should exclude the pattern

    def test_match_patterns_min_success_rate_boundary_just_above(self) -> None:
        """Catch mutation: success_rate < min_success_rate → >"""
        library = PatternLibrary()

        library.add_pattern(
            pattern_id="above_threshold",
            name="Above Threshold",
            description="",
            triggers=["test"],
            recommended_actions=[],
            success_rate=0.51,  # Just above threshold
            examples=[],
            tags=[],
        )

        # With min_success_rate=0.5, patterns with success_rate=0.51 should PASS
        matches = library.match_patterns("test", min_success_rate=0.5)
        assert len(matches) == 1  # Should include the pattern

    @pytest.mark.parametrize(
        "pattern_rate,threshold,should_match",
        [
            (0.3, 0.5, False),   # Below threshold
            (0.5, 0.5, True),    # At threshold (boundary)
            (0.7, 0.5, True),    # Above threshold
            (0.0, 0.5, False),   # Zero rate
            (1.0, 0.5, True),    # Max rate
            (0.99, 1.0, False),  # High rate, but below 1.0
            (1.0, 1.0, True),    # Exact max
        ],
    )
    def test_match_patterns_success_rate_threshold_parametrized(
        self, pattern_rate: float, threshold: float, should_match: bool
    ) -> None:
        """Parametrized test for success rate threshold mutations."""
        library = PatternLibrary()

        library.add_pattern(
            pattern_id="p",
            name="Test",
            description="",
            triggers=["test"],
            recommended_actions=[],
            success_rate=pattern_rate,
            examples=[],
            tags=[],
        )

        matches = library.match_patterns("test", min_success_rate=threshold)
        if should_match:
            assert len(matches) == 1
        else:
            assert len(matches) == 0

    def test_pattern_indexing_uses_correct_tags(self) -> None:
        """Catch mutation: tag assignment or indexing logic."""
        library = PatternLibrary()

        library.add_pattern(
            pattern_id="p1",
            name="Pattern 1",
            description="",
            triggers=["a"],
            recommended_actions=[],
            success_rate=0.7,
            examples=[],
            tags=["tag1", "tag2", "tag3"],
        )

        # Verify all tags are indexed
        assert "p1" in library.pattern_index["tag1"]
        assert "p1" in library.pattern_index["tag2"]
        assert "p1" in library.pattern_index["tag3"]
        
        # Verify pattern is indexed under all tags
        assert len([t for t in library.pattern_index if "p1" in library.pattern_index.get(t, [])]) == 3

    def test_record_pattern_usage_increments_count_exactly_once(self) -> None:
        """Catch mutation: usage_count += 1 → += 2 or no increment"""
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

        # Initial count is 0
        assert library.patterns["p1"]["usage_count"] == 0

        # After one usage, count is 1
        library.record_pattern_usage("p1", success=True)
        assert library.patterns["p1"]["usage_count"] == 1

        # After second usage, count is 2
        library.record_pattern_usage("p1", success=True)
        assert library.patterns["p1"]["usage_count"] == 2

        # Verify it increments exactly by 1 each time
        library.record_pattern_usage("p1", success=False)
        assert library.patterns["p1"]["usage_count"] == 3


class TestAgentMemoryMutationKillers:
    """Tests specifically designed to catch mutations in AgentMemory operations."""

    def test_store_memory_retrieval_exact_matching(self, tmp_path) -> None:
        """Catch mutation: field assignments or retrieval logic."""
        db_path = tmp_path / "test_memory.db"
        memory = AgentMemory(db_path=db_path)

        memory.store_memory(
            memory_id="test_entry",
            category="test_category",
            content="test content",
            context={"key": "value"},
            confidence=0.95,
            tags=["t1", "t2"],
        )

        retrieved = memory.retrieve_memory(memory_id="test_entry")
        
        assert retrieved is not None
        assert retrieved.category == "test_category"
        assert retrieved.content == "test content"
        assert retrieved.context == {"key": "value"}
        assert retrieved.confidence == 0.95
        assert retrieved.tags == ["t1", "t2"]

    def test_store_memory_with_tags_exact_matching(self, tmp_path) -> None:
        """Catch mutation: tag storage and retrieval logic."""
        db_path = tmp_path / "test_memory.db"
        memory = AgentMemory(db_path=db_path)

        memory.store_memory(
            memory_id="entry_with_tags",
            category="test",
            content="content",
            context={},
            tags=["python", "testing", "mutation"],
        )

        retrieved = memory.retrieve_memory(memory_id="entry_with_tags")
        assert retrieved is not None
        assert len(retrieved.tags) == 3
        assert "python" in retrieved.tags
        assert "testing" in retrieved.tags
        assert "mutation" in retrieved.tags

    def test_add_memory_alias_works_correctly(self, tmp_path) -> None:
        """Catch mutation: add_memory function aliasing."""
        db_path = tmp_path / "test_memory.db"
        memory = AgentMemory(db_path=db_path)

        # Use add_memory which is an alias for store_memory
        memory.add_memory(
            memory_id="alias_test",
            category="test",
            content="content",
            context={},
            confidence=0.75,
        )

        retrieved = memory.retrieve_memory(memory_id="alias_test")
        assert retrieved is not None
        assert retrieved.confidence == 0.75

    def test_retrieve_content_returns_just_content_string(self, tmp_path) -> None:
        """Catch mutation: retrieve_content implementation."""
        db_path = tmp_path / "test_memory.db"
        memory = AgentMemory(db_path=db_path)

        memory.store_memory(
            memory_id="content_test",
            category="test",
            content="This is the content",
            context={},
        )

        content = memory.retrieve_content("content_test")
        assert isinstance(content, str)
        assert content == "This is the content"

    def test_backward_compatibility_key_parameter(self, tmp_path) -> None:
        """Catch mutation: backward compatibility for key parameter."""
        db_path = tmp_path / "test_memory.db"
        memory = AgentMemory(db_path=db_path)

        memory.store_memory(
            memory_id="key_test",
            category="test",
            content="key content",
            context={},
        )

        # Using key parameter returns content string
        content = memory.retrieve_memory(key="key_test")
        assert isinstance(content, str)
        assert content == "key content"


# ==============================================================================
# Integration Tests - Multi-Component Flows
# ==============================================================================


class TestMemoryPatternLibraryIntegration:
    """Integration tests for memory and pattern library together."""

    def test_pattern_matching_with_stored_patterns(self) -> None:
        """Catch mutations across pattern storage and matching."""
        library = PatternLibrary()

        # Store patterns with different success rates
        for i, rate in enumerate([0.3, 0.5, 0.7, 0.9]):
            library.add_pattern(
                pattern_id=f"p{i}",
                name=f"Pattern {i}",
                description="",
                triggers=["test"],
                recommended_actions=[],
                success_rate=rate,
                examples=[],
                tags=[],
            )

        # Match with threshold 0.5 should return patterns with rate >= 0.5
        matches = library.match_patterns("test", min_success_rate=0.5)
        matched_ids = {m["pattern"]["pattern_id"] for m in matches}

        # Should include p1 (0.5), p2 (0.7), p3 (0.9)
        # Should exclude p0 (0.3)
        assert "p0" not in matched_ids
        assert "p1" in matched_ids
        assert "p2" in matched_ids
        assert "p3" in matched_ids


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
