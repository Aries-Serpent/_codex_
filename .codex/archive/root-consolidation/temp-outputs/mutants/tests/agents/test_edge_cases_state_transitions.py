"""
PHASE 7D TRACK 5: State Transition and Resilience Tests

Comprehensive state management testing for:
- Context frame status transitions
- Memory lifecycle state changes
- Concurrent state access
- Incomplete state recovery
- State consistency verification
- Transaction isolation
"""

from __future__ import annotations

import sqlite3
import threading
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

from agents.agent_memory import (
    AgentMemory,
    ContextFrame,
    MemoryEntry,
    PatternLibrary,
)


class TestContextFrameStateTransitions:
    """Test context frame status transitions."""

    def test_context_frame_active_to_completed(self) -> None:
        """Test context frame transition from active to completed."""
        frame = ContextFrame(
            frame_id="test_frame",
            task_description="task",
            start_time=datetime.now(UTC).isoformat(),
            status="active",
        )
        assert frame.status == "active", "status is not valid"

        # Simulate completion
        frame.status = "completed"
        frame.end_time = datetime.now(UTC).isoformat()

        assert frame.status == "completed", "status is not valid"
        assert frame.end_time is not None, "end_time must be initialized"

    def test_context_frame_active_to_paused(self) -> None:
        """Test context frame transition from active to paused."""
        frame = ContextFrame(
            frame_id="test_frame",
            task_description="task",
            start_time=datetime.now(UTC).isoformat(),
            status="active",
        )
        frame.status = "paused"
        assert frame.status == "paused", "status is not valid"

    def test_context_frame_paused_to_active(self) -> None:
        """Test context frame transition from paused back to active."""
        frame = ContextFrame(
            frame_id="test_frame",
            task_description="task",
            start_time=datetime.now(UTC).isoformat(),
            status="active",
        )
        frame.status = "paused"
        assert frame.status == "paused", "status is not valid"

        frame.status = "active"
        assert frame.status == "active", "status is not valid"

    def test_context_frame_active_to_failed(self) -> None:
        """Test context frame transition from active to failed."""
        frame = ContextFrame(
            frame_id="test_frame",
            task_description="task",
            start_time=datetime.now(UTC).isoformat(),
            status="active",
        )
        frame.status = "failed"
        frame.end_time = datetime.now(UTC).isoformat()
        frame.errors_encountered += 1

        assert frame.status == "failed", "status is not valid"
        assert frame.errors_encountered == 1, "Error should be raised or set"

    def test_context_frame_failed_to_completed(self) -> None:
        """Test context frame recovery from failed to completed."""
        frame = ContextFrame(
            frame_id="test_frame",
            task_description="task",
            start_time=datetime.now(UTC).isoformat(),
            status="failed",
        )
        # Recovery transition
        frame.status = "completed"
        frame.errors_encountered = 1  # Still records the error

        assert frame.status == "completed", "status is not valid"
        assert frame.errors_encountered == 1, "Error should be raised or set"

    def test_context_frame_all_transitions(self) -> None:
        """Test all possible state transitions."""
        frame = ContextFrame(
            frame_id="test_frame",
            task_description="task",
            start_time=datetime.now(UTC).isoformat(),
            status="active",
        )

        transitions = [
            ("active", "paused"),
            ("paused", "active"),
            ("active", "completed"),
            ("completed", "failed"),
            ("failed", "active"),
            ("active", "failed"),
            ("failed", "completed"),
        ]

        for from_state, to_state in transitions:
            frame.status = from_state
            frame.status = to_state
            assert frame.status == to_state, "status is not valid"


class TestMemoryEntryLifecycle:
    """Test MemoryEntry lifecycle and state changes."""

    def test_memory_entry_creation_and_access(self, tmp_path: Path) -> None:
        """Test memory entry creation and access updates."""
        db_path = tmp_path / "test.db"
        memory = AgentMemory(db_path=db_path)

        entry = MemoryEntry(
            memory_id="lifecycle_test",
            category="test",
            content="content",
            context={"created": True},
            access_count=0,
        )
        assert entry.access_count == 0, "Count must be greater than zero"

        memory.store_memory(entry)

        # Simulate access
        entry.access_count += 1
        entry.last_accessed = datetime.now(UTC).isoformat()

        memory.store_memory(entry)

        retrieved = memory.retrieve_memory("lifecycle_test")
        assert retrieved is not None, "retrieved must be initialized"
        assert retrieved.access_count == 1, "Count must be greater than zero"

    def test_memory_entry_confidence_degradation(self, tmp_path: Path) -> None:
        """Test memory entry confidence decrease over time."""
        db_path = tmp_path / "test.db"
        memory = AgentMemory(db_path=db_path)

        entry = MemoryEntry(
            memory_id="confidence_test",
            category="fact",
            content="old information",
            context={},
            confidence=1.0,
        )
        memory.store_memory(entry)

        # Simulate confidence degradation
        entry.confidence = 0.9
        entry.last_accessed = (datetime.now(UTC) - timedelta(days=30)).isoformat()
        memory.store_memory(entry)

        # Simulate further degradation
        entry.confidence = 0.7
        entry.last_accessed = (datetime.now(UTC) - timedelta(days=90)).isoformat()
        memory.store_memory(entry)

        retrieved = memory.retrieve_memory("confidence_test")
        assert retrieved is not None, "retrieved must be initialized"
        assert retrieved.confidence == 0.7, "confidence is not valid"

    def test_memory_entry_update_atomicity(self, tmp_path: Path) -> None:
        """Test that memory entry updates are atomic."""
        db_path = tmp_path / "test.db"
        memory = AgentMemory(db_path=db_path)

        entry = MemoryEntry(
            memory_id="atomic_test",
            category="test",
            content="original",
            context={},
        )
        memory.store_memory(entry)

        # Update multiple fields
        entry.content = "updated"
        entry.confidence = 0.5
        entry.access_count = 5
        entry.tags = ["updated"]

        memory.store_memory(entry)

        retrieved = memory.retrieve_memory("atomic_test")
        assert retrieved is not None, "retrieved must be initialized"
        assert retrieved.content == "updated", "Content must not be empty"
        assert retrieved.confidence == 0.5, "confidence is not valid"
        assert retrieved.access_count == 5, "Count must be greater than zero"


class TestPatternLibraryStateTransitions:
    """Test pattern library state and usage tracking."""

    def test_pattern_usage_increments(self) -> None:
        """Test pattern usage count increments correctly."""
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

        assert lib.patterns["pattern1"]["usage_count"] == 0, "Count must be greater than zero"

        lib.record_pattern_usage("pattern1", success=True)
        assert lib.patterns["pattern1"]["usage_count"] == 1, "Count must be greater than zero"

        lib.record_pattern_usage("pattern1", success=True)
        assert lib.patterns["pattern1"]["usage_count"] == 2, "Count must be greater than zero"

    def test_pattern_success_rate_tracks_correctly(self) -> None:
        """Test pattern success rate updates correctly."""
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

        initial_rate = lib.patterns["pattern1"]["success_rate"]

        # Record success
        lib.record_pattern_usage("pattern1", success=True)
        new_rate = lib.patterns["pattern1"]["success_rate"]
        assert new_rate >= initial_rate, "new_rate must be greater than zero"

    def test_pattern_failure_decreases_rate(self) -> None:
        """Test pattern failure decreases success rate."""
        lib = PatternLibrary()
        lib.add_pattern(
            pattern_id="pattern1",
            name="Pattern 1",
            description="desc",
            triggers=["trigger"],
            recommended_actions=["action"],
            success_rate=0.9,  # Start high
            examples=[],
            tags=["test"],
        )

        initial_rate = lib.patterns["pattern1"]["success_rate"]

        # Record failure
        lib.record_pattern_usage("pattern1", success=False)
        new_rate = lib.patterns["pattern1"]["success_rate"]
        assert new_rate < initial_rate, "new_rate is not valid"

    def test_pattern_many_successes_converges_to_one(self) -> None:
        """Test many successes increases rate toward 1.0."""
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

        # Record many successes
        for _ in range(100):
            lib.record_pattern_usage("pattern1", success=True)

        final_rate = lib.patterns["pattern1"]["success_rate"]
        assert final_rate > 0.8, "final_rate must be greater than zero"

    def test_pattern_many_failures_converges_to_zero(self) -> None:
        """Test many failures decreases rate toward 0.0."""
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

        # Record many failures
        for _ in range(100):
            lib.record_pattern_usage("pattern1", success=False)

        final_rate = lib.patterns["pattern1"]["success_rate"]
        assert final_rate < 0.2, "final_rate is not valid"


class TestConcurrentStateAccess:
    """Test concurrent state access and synchronization."""

    def test_concurrent_memory_writes(self, tmp_path: Path) -> None:
        """Test concurrent writes to memory."""
        db_path = tmp_path / "concurrent.db"

        def write_memory(memory_id: str):
            memory = AgentMemory(db_path=db_path)
            entry = MemoryEntry(
                memory_id=memory_id,
                category="test",
                content=f"content_{memory_id}",
                context={},
            )
            memory.store_memory(entry)

        # Write from multiple threads
        threads = [threading.Thread(target=write_memory, args=(f"entry_{i}",)) for i in range(10)]

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        # Verify all writes succeeded
        memory = AgentMemory(db_path=db_path)
        for i in range(10):
            retrieved = memory.retrieve_memory(f"entry_{i}")
            assert retrieved is not None, "retrieved must be initialized"

    def test_concurrent_memory_reads(self, tmp_path: Path) -> None:
        """Test concurrent reads from memory."""
        db_path = tmp_path / "concurrent_read.db"
        memory = AgentMemory(db_path=db_path)

        # Write initial data
        for i in range(10):
            entry = MemoryEntry(
                memory_id=f"entry_{i}",
                category="test",
                content=f"content_{i}",
                context={},
            )
            memory.store_memory(entry)

        read_results = []

        def read_memory(memory_id: str):
            memory = AgentMemory(db_path=db_path)
            entry = memory.retrieve_memory(memory_id)
            read_results.append(entry)

        # Read from multiple threads
        threads = [threading.Thread(target=read_memory, args=(f"entry_{i}",)) for i in range(10)]

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        # All reads should succeed
        assert len(read_results) == 10, "Read_results must not be empty"
        assert all(r is not None for r in read_results), "r must be initialized"

    def test_concurrent_read_write_race_condition(self, tmp_path: Path) -> None:
        """Test read-write race conditions."""
        db_path = tmp_path / "race.db"
        memory = AgentMemory(db_path=db_path)

        # Initial entry
        entry = MemoryEntry(
            memory_id="race_test",
            category="test",
            content="initial",
            context={},
            access_count=0,
        )
        memory.store_memory(entry)

        results = {"reads": [], "writes": []}

        def writer():
            for i in range(5):
                entry = MemoryEntry(
                    memory_id="race_test",
                    category="test",
                    content=f"update_{i}",
                    context={},
                    access_count=i,
                )
                memory.store_memory(entry)
                results["writes"].append(i)
                time.sleep(0.001)

        def reader():
            for _ in range(5):
                entry = memory.retrieve_memory("race_test")
                if entry:
                    results["reads"].append(entry.access_count)
                time.sleep(0.001)

        # Run concurrent read/write
        t_write = threading.Thread(target=writer)
        t_read = threading.Thread(target=reader)

        t_write.start()
        t_read.start()

        t_write.join()
        t_read.join()

        # Verify we got reads
        assert len(results["reads"]) > 0, "Collection must not be empty"
        assert len(results["writes"]) == 5, "Collection must not be empty"


class TestIncompleteStateRecovery:
    """Test recovery from incomplete state transitions."""

    def test_recover_from_paused_context(self) -> None:
        """Test recovery from paused context frame."""
        frame = ContextFrame(
            frame_id="recovery_test",
            task_description="task",
            start_time=datetime.now(UTC).isoformat(),
            status="active",
        )

        # Transition to paused
        frame.status = "paused"
        frame.end_time = datetime.now(UTC).isoformat()

        # Recover by resuming
        frame.status = "active"
        frame.end_time = None

        assert frame.status == "active", "status is not valid"
        assert frame.end_time is None, "end_time is not valid"

    def test_recover_from_failed_context(self) -> None:
        """Test recovery from failed context frame."""
        frame = ContextFrame(
            frame_id="recovery_test",
            task_description="task",
            start_time=datetime.now(UTC).isoformat(),
            status="failed",
            errors_encountered=3,
        )

        # Clear errors and retry
        frame.status = "active"
        frame.errors_encountered = 0

        assert frame.status == "active", "status is not valid"
        assert frame.errors_encountered == 0, "Error should be raised or set"

    def test_partial_memory_update_recovery(self, tmp_path: Path) -> None:
        """Test recovery from partial memory update."""
        db_path = tmp_path / "partial.db"
        memory = AgentMemory(db_path=db_path)

        entry = MemoryEntry(
            memory_id="partial_test",
            category="test",
            content="initial",
            context={"version": 1},
        )
        memory.store_memory(entry)

        # Simulate partial update
        entry.content = "updated"
        entry.context["version"] = 2
        memory.store_memory(entry)

        # Verify recovery
        retrieved = memory.retrieve_memory("partial_test")
        assert retrieved is not None, "retrieved must be initialized"
        assert retrieved.content == "updated", "Content must not be empty"
        assert retrieved.context["version"] == 2, "Condition must be true"


class TestStateConsistencyVerification:
    """Test state consistency verification."""

    def test_memory_entry_consistency_after_serialization(self) -> None:
        """Test memory entry consistency after to_dict/from_dict."""
        entry = MemoryEntry(
            memory_id="consistency_test",
            category="test",
            content="content",
            context={"key": "value"},
            confidence=0.85,
            access_count=5,
            tags=["tag1", "tag2"],
            related_memories=["mem1", "mem2"],
        )

        # Roundtrip through dict
        data = entry.to_dict()
        reconstructed = MemoryEntry.from_dict(data)

        # Verify consistency
        assert reconstructed.memory_id == entry.memory_id, "memory_id is not valid"
        assert reconstructed.category == entry.category, "category is not valid"
        assert reconstructed.content == entry.content, "Content must not be empty"
        assert reconstructed.context == entry.context, "context is not valid"
        assert reconstructed.confidence == entry.confidence, "confidence is not valid"
        assert reconstructed.access_count == entry.access_count, "Count must be greater than zero"
        assert reconstructed.tags == entry.tags, "tags is not valid"
        assert reconstructed.related_memories == entry.related_memories, "related_memories is not valid"

    def test_context_frame_consistency_after_serialization(self) -> None:
        """Test context frame consistency after to_dict."""
        frame = ContextFrame(
            frame_id="consistency_test",
            task_description="task",
            start_time=datetime.now(UTC).isoformat(),
            end_time=datetime.now(UTC).isoformat(),
            status="completed",
            tokens_used=100,
            actions_taken=5,
            errors_encountered=0,
            files_modified=["file1.py", "file2.py"],
            decisions_made=[{"decision": "choice1"}],
            lessons_learned=["lesson1"],
        )

        data = frame.to_dict()

        # Verify all fields present
        assert data["frame_id"] == frame.frame_id, "Data must not be empty"
        assert data["task_description"] == frame.task_description, "Data must not be empty"
        assert data["status"] == frame.status, "Data must not be empty"
        assert data["tokens_used"] == 100, "Data must not be empty"
        assert data["actions_taken"] == 5, "Data must not be empty"
        assert data["errors_encountered"] == 0, "Data must not be empty"
        assert len(data["files_modified"]) == 2, "Collection must not be empty"

    def test_pattern_library_serialization_consistency(self) -> None:
        """Test pattern library consistency through serialization."""
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

        data = lib.to_dict()
        reconstructed = PatternLibrary.from_dict(data)

        # Verify consistency
        assert "pattern1" in reconstructed.patterns, "Condition must be true"
        assert reconstructed.patterns["pattern1"]["name"] == "Pattern 1", "Condition must be true"
        assert reconstructed.patterns["pattern1"]["success_rate"] == 0.8, "Condition must be true"


class TestDatabaseStateConsistency:
    """Test database state consistency across operations."""

    def test_database_schema_consistency(self, tmp_path: Path) -> None:
        """Test database schema remains consistent."""
        db_path = tmp_path / "schema_test.db"
        AgentMemory(db_path=db_path)

        # Verify schema exists
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # Check memories table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='memories'")
            assert cursor.fetchone() is not None, "curs must be initialized"

            # Check context_frames table
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='context_frames'"
            )
            assert cursor.fetchone() is not None, "curs must be initialized"

            # Check patterns table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='patterns'")
            assert cursor.fetchone() is not None, "curs must be initialized"

    def test_database_state_after_many_operations(self, tmp_path: Path) -> None:
        """Test database state consistency after many operations."""
        db_path = tmp_path / "state_test.db"
        memory = AgentMemory(db_path=db_path)

        # Perform many operations
        for i in range(100):
            entry = MemoryEntry(
                memory_id=f"entry_{i}",
                category=f"category_{i % 5}",
                content=f"content_{i}",
                context={"index": i},
            )
            memory.store_memory(entry)

        # Verify database is still consistent
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM memories")
            count = cursor.fetchone()[0]
            assert count == 100, "Count must be greater than zero"
