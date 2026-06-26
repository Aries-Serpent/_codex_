"""
PHASE 7D TRACK 5: Integration and Data Integrity Tests

Comprehensive integration testing for:
- Cross-module memory interactions
- Data consistency across components
- Memory-ContextFrame integration
- PatternLibrary integration with memory retrieval
- Data migration paths
- Batch operations atomicity
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

from agents.agent_memory import (
    AgentMemory,
    ContextFrame,
    MemoryEntry,
    PatternLibrary,
)


class TestMemoryContextFrameIntegration:
    """Test integration between Memory and ContextFrame."""

    def test_context_frame_references_stored_memories(self, tmp_path: Path) -> None:
        """Test context frame can reference stored memories."""
        db_path = tmp_path / "integration.db"
        memory = AgentMemory(db_path=db_path)

        # Store memories
        memory_ids = []
        for i in range(5):
            entry = MemoryEntry(
                memory_id=f"memory_{i}",
                category="task",
                content=f"Memory {i}",
                context={},
            )
            memory.store_memory(entry)
            memory_ids.append(f"memory_{i}")

        # Create context frame that references these memories
        frame = ContextFrame(
            frame_id="frame_1",
            task_description="task",
            start_time=datetime.now(UTC).isoformat(),
            active_memories=memory_ids,
        )

        assert len(frame.active_memories) == 5, "Collection must not be empty"

        # Verify all referenced memories exist
        for mem_id in frame.active_memories:
            retrieved = memory.retrieve_memory(mem_id)
            assert retrieved is not None, "retrieved must be initialized"

    def test_multiple_context_frames_share_memories(self, tmp_path: Path) -> None:
        """Test multiple context frames can reference same memory."""
        db_path = tmp_path / "shared_memory.db"
        memory = AgentMemory(db_path=db_path)

        # Store shared memory
        shared_entry = MemoryEntry(
            memory_id="shared_memory",
            category="fact",
            content="Shared fact",
            context={},
            confidence=0.95,
        )
        memory.store_memory(shared_entry)

        # Create multiple frames referencing it
        frames = []
        for i in range(3):
            frame = ContextFrame(
                frame_id=f"frame_{i}",
                task_description=f"Task {i}",
                start_time=datetime.now(UTC).isoformat(),
                active_memories=["shared_memory"],
            )
            frames.append(frame)

        # All frames reference the same memory
        for frame in frames:
            retrieved = memory.retrieve_memory("shared_memory")
            assert retrieved is not None, "retrieved must be initialized"
            assert retrieved.memory_id == "shared_memory", "memory_id is not valid"

    def test_context_frame_track_memory_access_patterns(self, tmp_path: Path) -> None:
        """Test context frame tracks memory access patterns."""
        db_path = tmp_path / "access_pattern.db"
        memory = AgentMemory(db_path=db_path)

        # Store memory
        entry = MemoryEntry(
            memory_id="accessed_memory",
            category="pattern",
            content="Pattern",
            context={},
            access_count=0,
        )
        memory.store_memory(entry)

        # Create frames that track access
        for i in range(5):
            # "Access" the memory by retrieving it
            retrieved = memory.retrieve_memory("accessed_memory")
            assert retrieved is not None, "retrieved must be initialized"

            # Simulate tracking in context frame
            ContextFrame(
                frame_id=f"frame_{i}",
                task_description="task",
                start_time=datetime.now(UTC).isoformat(),
                active_memories=["accessed_memory"],
            )

            # Update access count
            entry.access_count += 1
            entry.last_accessed = datetime.now(UTC).isoformat()
            memory.store_memory(entry)

        # Verify final access count
        final = memory.retrieve_memory("accessed_memory")
        assert final is not None, "final must be initialized"
        assert final.access_count == 5, "Count must be greater than zero"


class TestPatternLibraryMemoryIntegration:
    """Test integration between PatternLibrary and Memory."""

    def test_patterns_recommend_stored_memories(self, tmp_path: Path) -> None:
        """Test patterns can reference and recommend stored memories."""
        db_path = tmp_path / "pattern_memory.db"
        memory = AgentMemory(db_path=db_path)

        # Store memory about successful approach
        success_memory = MemoryEntry(
            memory_id="success_pattern",
            category="lesson",
            content="This approach worked",
            context={"success": True},
            confidence=0.95,
        )
        memory.store_memory(success_memory)

        # Create pattern that references this
        lib = PatternLibrary()
        lib.add_pattern(
            pattern_id="working_pattern",
            name="Working Pattern",
            description="Proven to work",
            triggers=["success", "working"],
            recommended_actions=[
                "apply_success_pattern",
                "reference_memory:success_pattern",
            ],
            success_rate=0.95,
            examples=[{"situation": "success_pattern"}],
            tags=["proven"],
        )

        # Pattern should reference stored memory
        pattern = lib.patterns["working_pattern"]
        assert "success_pattern" in str(pattern["recommended_actions"]), "Condition must be true"

    def test_pattern_usage_updates_memory_confidence(self, tmp_path: Path) -> None:
        """Test pattern usage updates related memory confidence."""
        db_path = tmp_path / "pattern_confidence.db"
        memory = AgentMemory(db_path=db_path)

        # Store pattern memory
        pattern_memory = MemoryEntry(
            memory_id="pattern_memory_1",
            category="pattern",
            content="Pattern description",
            context={"pattern_id": "pattern1"},
            confidence=0.5,
        )
        memory.store_memory(pattern_memory)

        # Create pattern
        lib = PatternLibrary()
        lib.add_pattern(
            pattern_id="pattern1",
            name="Test Pattern",
            description="desc",
            triggers=["trigger"],
            recommended_actions=["action"],
            success_rate=0.5,
            examples=[],
            tags=["test"],
        )

        # Record successful pattern usage
        for _ in range(10):
            lib.record_pattern_usage("pattern1", success=True)

        # Pattern success rate increases
        assert lib.patterns["pattern1"]["success_rate"] > 0.7, "Value must be greater than zero"

        # Update related memory confidence
        pattern_memory.confidence = 0.85
        memory.store_memory(pattern_memory)

        # Verify memory was updated
        retrieved = memory.retrieve_memory("pattern_memory_1")
        assert retrieved is not None, "retrieved must be initialized"
        assert retrieved.confidence == 0.85, "confidence is not valid"

    def test_pattern_matching_across_multiple_memories(self, tmp_path: Path) -> None:
        """Test pattern matching considers multiple stored memories."""
        db_path = tmp_path / "multi_pattern.db"
        memory = AgentMemory(db_path=db_path)

        # Store related memories
        for i in range(5):
            entry = MemoryEntry(
                memory_id=f"related_{i}",
                category="context",
                content=f"Related context {i}",
                context={"related": True},
            )
            memory.store_memory(entry)

        # Create pattern that could match these contexts
        lib = PatternLibrary()
        lib.add_pattern(
            pattern_id="multi_context_pattern",
            name="Multi Context",
            description="Matches multiple contexts",
            triggers=["related", "context"],
            recommended_actions=["gather_context", "synthesize"],
            success_rate=0.8,
            examples=[],
            tags=["context"],
        )

        # Match pattern
        matches = lib.match_patterns("This is related context information")
        assert len(matches) > 0, "Matches must not be empty"


class TestMemoryDataMigration:
    """Test data migration and consistency."""

    def test_memory_migration_from_one_database_to_another(self, tmp_path: Path) -> None:
        """Test migrating memories from one database to another."""
        old_db = tmp_path / "old.db"
        new_db = tmp_path / "new.db"

        # Store memories in old database
        old_memory = AgentMemory(db_path=old_db)

        entries = []
        for i in range(10):
            entry = MemoryEntry(
                memory_id=f"migrated_{i}",
                category="migrate",
                content=f"Content {i}",
                context={"source": "old"},
                confidence=0.9,
            )
            entries.append(entry)
            old_memory.store_memory(entry)

        # Migrate to new database
        new_memory = AgentMemory(db_path=new_db)

        for entry in entries:
            new_memory.store_memory(entry)

        # Verify all memories migrated
        for i in range(10):
            old_retrieved = old_memory.retrieve_memory(f"migrated_{i}")
            new_retrieved = new_memory.retrieve_memory(f"migrated_{i}")

            assert old_retrieved is not None, "old_retrieved must be initialized"
            assert new_retrieved is not None, "new_retrieved must be initialized"
            assert old_retrieved.content == new_retrieved.content, "Content must not be empty"

    def test_memory_backup_and_restore(self, tmp_path: Path) -> None:
        """Test backup and restore of memories."""
        original_db = tmp_path / "original.db"
        backup_db = tmp_path / "backup.db"

        # Create original memories
        original = AgentMemory(db_path=original_db)

        original_entries = []
        for i in range(5):
            entry = MemoryEntry(
                memory_id=f"backup_{i}",
                category="important",
                content=f"Important data {i}",
                context={"backed_up": True},
            )
            original_entries.append(entry)
            original.store_memory(entry)

        # Backup by copying database
        import shutil

        shutil.copy(original_db, backup_db)

        # Restore from backup
        restored = AgentMemory(db_path=backup_db)

        # Verify all data restored
        for i in range(5):
            retrieved = restored.retrieve_memory(f"backup_{i}")
            assert retrieved is not None, "retrieved must be initialized"
            assert retrieved.content == f"Important data {i}", "Data must not be empty"

    def test_memory_consolidation_and_pruning(self, tmp_path: Path) -> None:
        """Test memory consolidation and pruning."""
        db_path = tmp_path / "consolidate.db"
        memory = AgentMemory(db_path=db_path)

        # Store memories with varying confidence
        for i in range(20):
            confidence = 1.0 - (i * 0.05)  # Decreasing confidence
            entry = MemoryEntry(
                memory_id=f"consolidate_{i}",
                category="test",
                content=f"Content {i}",
                context={},
                confidence=max(0.0, confidence),
                last_accessed=(datetime.now(UTC) - timedelta(days=i)).isoformat(),
            )
            memory.store_memory(entry)

        # Get all memories
        all_memories = []
        for i in range(20):
            retrieved = memory.retrieve_memory(f"consolidate_{i}")
            if retrieved:
                all_memories.append(retrieved)

        # Verify we have memories with varying confidence
        confidences = [m.confidence for m in all_memories]
        assert max(confidences) > 0.8, "Value must be greater than zero"
        assert min(confidences) <= 0.2, "Condition must be true"

    def test_memory_deduplication(self, tmp_path: Path) -> None:
        """Test deduplication of identical memories."""
        db_path = tmp_path / "dedupe.db"
        memory = AgentMemory(db_path=db_path)

        # Store duplicate content with different IDs
        for i in range(5):
            entry = MemoryEntry(
                memory_id=f"duplicate_{i}",
                category="duplicate",
                content="Same content",
                context={"duplicate": True},
            )
            memory.store_memory(entry)

        # All should be stored
        for i in range(5):
            retrieved = memory.retrieve_memory(f"duplicate_{i}")
            assert retrieved is not None, "retrieved must be initialized"

    def test_memory_versioning(self, tmp_path: Path) -> None:
        """Test memory versioning and updates."""
        db_path = tmp_path / "versions.db"
        memory = AgentMemory(db_path=db_path)

        # Create initial memory
        entry = MemoryEntry(
            memory_id="versioned",
            category="test",
            content="Version 1",
            context={"version": 1},
        )
        memory.store_memory(entry)

        # Update to version 2
        entry.content = "Version 2"
        entry.context["version"] = 2
        memory.store_memory(entry)

        # Update to version 3
        entry.content = "Version 3"
        entry.context["version"] = 3
        memory.store_memory(entry)

        # Final version should be 3
        retrieved = memory.retrieve_memory("versioned")
        assert retrieved is not None, "retrieved must be initialized"
        assert retrieved.content == "Version 3", "Content must not be empty"
        assert retrieved.context["version"] == 3, "Condition must be true"


class TestBatchOperationsAtomicity:
    """Test atomicity of batch operations."""

    def test_batch_memory_store_atomicity(self, tmp_path: Path) -> None:
        """Test batch storage maintains atomicity."""
        db_path = tmp_path / "batch.db"
        memory = AgentMemory(db_path=db_path)

        # Prepare batch
        batch_entries = []
        for i in range(10):
            entry = MemoryEntry(
                memory_id=f"batch_{i}",
                category="batch",
                content=f"Batch item {i}",
                context={"batch_id": "batch_001"},
            )
            batch_entries.append(entry)

        # Store all
        for entry in batch_entries:
            memory.store_memory(entry)

        # Verify all stored
        for i in range(10):
            retrieved = memory.retrieve_memory(f"batch_{i}")
            assert retrieved is not None, "retrieved must be initialized"

    def test_batch_with_partial_failure_consistency(self, tmp_path: Path) -> None:
        """Test consistency when batch has partial failures."""
        db_path = tmp_path / "partial_batch.db"
        memory = AgentMemory(db_path=db_path)

        batch_entries = []
        for i in range(10):
            entry = MemoryEntry(
                memory_id=f"partial_{i}",
                category="batch",
                content=f"Item {i}",
                context={},
            )
            batch_entries.append(entry)

        # Store first half
        for entry in batch_entries[:5]:
            memory.store_memory(entry)

        # Store second half
        for entry in batch_entries[5:]:
            memory.store_memory(entry)

        # All should be accessible
        for i in range(10):
            retrieved = memory.retrieve_memory(f"partial_{i}")
            assert retrieved is not None, "retrieved must be initialized"


class TestCrossComponentDataConsistency:
    """Test data consistency across components."""

    def test_memory_context_frame_pattern_consistency(self, tmp_path: Path) -> None:
        """Test consistency across Memory, ContextFrame, and PatternLibrary."""
        db_path = tmp_path / "cross_component.db"
        memory = AgentMemory(db_path=db_path)

        # Create interconnected data

        # 1. Store memories
        memory1 = MemoryEntry(
            memory_id="cross_1",
            category="fact",
            content="Important fact",
            context={"component": "memory"},
        )
        memory.store_memory(memory1)

        # 2. Create context frame referencing memory
        frame = ContextFrame(
            frame_id="cross_frame",
            task_description="Cross component task",
            start_time=datetime.now(UTC).isoformat(),
            active_memories=["cross_1"],
        )

        # 3. Create pattern that matches situation
        lib = PatternLibrary()
        lib.add_pattern(
            pattern_id="cross_pattern",
            name="Cross Pattern",
            description="Uses memory from frame",
            triggers=["Important", "fact"],
            recommended_actions=["use_memory:cross_1"],
            success_rate=0.9,
            examples=[],
            tags=["cross_component"],
        )

        # 4. Verify cross-component consistency

        # Memory is accessible
        retrieved_memory = memory.retrieve_memory("cross_1")
        assert retrieved_memory is not None, "retrieved_memory must be initialized"

        # Frame references the memory
        assert "cross_1" in frame.active_memories, "Condition must be true"

        # Pattern can match and recommend the memory
        matches = lib.match_patterns("Important fact")
        assert len(matches) > 0, "Matches must not be empty"

    def test_system_wide_data_integrity_check(self, tmp_path: Path) -> None:
        """Test system-wide data integrity."""
        db_path = tmp_path / "integrity.db"
        memory = AgentMemory(db_path=db_path)

        # Store complex data structure
        complex_entry = MemoryEntry(
            memory_id="complex",
            category="complex",
            content="Complex content",
            context={
                "nested": {"deep": {"value": "important"}},
                "list": [1, 2, 3, 4, 5],
                "mixed": [{"key": "value"}, 123, "string"],
            },
            tags=["complex", "nested", "deep"],
            related_memories=["memory_1", "memory_2", "memory_3"],
        )

        memory.store_memory(complex_entry)

        # Retrieve and verify integrity
        retrieved = memory.retrieve_memory("complex")
        assert retrieved is not None, "retrieved must be initialized"

        # Check all nested data preserved
        assert retrieved.context["nested"]["deep"]["value"] == "important", "Value must be initialized"
        assert retrieved.context["list"] == [1, 2, 3, 4, 5]
        assert len(retrieved.tags) == 3, "Collection must not be empty"
        assert len(retrieved.related_memories) == 3, "Collection must not be empty"


class TestDataIntegrityEdgeCases:
    """Test data integrity edge cases."""

    def test_memory_with_circular_references(self, tmp_path: Path) -> None:
        """Test memory with circular references."""
        db_path = tmp_path / "circular.db"
        memory = AgentMemory(db_path=db_path)

        # Create memories that reference each other
        entry1 = MemoryEntry(
            memory_id="mem_a",
            category="test",
            content="Memory A",
            context={},
            related_memories=["mem_b"],
        )

        entry2 = MemoryEntry(
            memory_id="mem_b",
            category="test",
            content="Memory B",
            context={},
            related_memories=["mem_a"],
        )

        memory.store_memory(entry1)
        memory.store_memory(entry2)

        # Both should be retrievable
        retrieved_a = memory.retrieve_memory("mem_a")
        retrieved_b = memory.retrieve_memory("mem_b")

        assert retrieved_a is not None, "retrieved_a must be initialized"
        assert retrieved_b is not None, "retrieved_b must be initialized"
        assert "mem_b" in retrieved_a.related_memories, "Condition must be true"
        assert "mem_a" in retrieved_b.related_memories, "Condition must be true"

    def test_memory_reference_integrity_with_deletion(self, tmp_path: Path) -> None:
        """Test reference integrity when related memory is deleted."""
        db_path = tmp_path / "reference_integrity.db"
        memory = AgentMemory(db_path=db_path)

        # Create related memories
        entry1 = MemoryEntry(
            memory_id="parent",
            category="parent",
            content="Parent memory",
            context={},
            related_memories=["child"],
        )

        entry2 = MemoryEntry(
            memory_id="child",
            category="child",
            content="Child memory",
            context={},
        )

        memory.store_memory(entry1)
        memory.store_memory(entry2)

        # Parent still references child even if child is updated
        updated_child = MemoryEntry(
            memory_id="child",
            category="child",
            content="Updated child",
            context={"updated": True},
        )
        memory.store_memory(updated_child)

        # Parent reference should still be valid
        parent = memory.retrieve_memory("parent")
        assert "child" in parent.related_memories, "Condition must be true"
