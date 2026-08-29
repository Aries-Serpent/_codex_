"""Comprehensive tests for session checkpoint and resume system.

Tests cover:
- Checkpoint creation and compression
- State serialization and validation
- Restore operations with fallback
- Performance and latency
- Error handling and recovery

Author: cognitive-brain-session-injector
Phase: 10.1 - Session Checkpoint/Resume System
"""

# Import modules under test
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import pytest  # pragma: allowlist secret

sys.path.insert(0, str(Path(__file__).parent.parent / "cognitive"))

from session_checkpoint_manager import (
    CheckpointNotFoundError,
    SessionCheckpointManager,
    StorageError,
)
from session_resume_engine import (
    ContextProvider,
    SessionResumeEngine,
)

# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def temp_storage():
    """Create temporary storage directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def checkpoint_manager(temp_storage):
    """Create checkpoint manager with temp storage."""
    return SessionCheckpointManager(
        storage_path=str(temp_storage / "checkpoints"),
        compression_algorithm="zstd",
        retention_days=30,
    )


@pytest.fixture
def resume_engine(checkpoint_manager):
    """Create resume engine with checkpoint manager."""
    return SessionResumeEngine(
        checkpoint_manager=checkpoint_manager,
        enable_warmup=True,
    )


@pytest.fixture
def sample_checkpoint_state():
    """Sample checkpoint state for testing."""
    return {
        "session_id": "S001",
        "agent_state": {
            "agent_id": "test-agent",
            "status": "in_progress",
            "current_file": "test.py",
            "line": 42,
        },
        "memory_snapshot": {
            "short_term_memory": [
                {
                    "pattern_id": "p_001",
                    "category": "optimization",
                    "content": "Use list comprehension",
                    "relevance_score": 0.95,
                    "last_used": datetime.utcnow().isoformat(),
                    "usage_count": 5,
                }
            ],
            "long_term_memory": [],
            "total_patterns": 1,
            "memory_usage_bytes": 1024,
        },
        "execution_progress": {
            "current_task": "refactor_search",
            "completed_tasks": ["analyze", "design"],
            "pending_tasks": ["implement", "test"],
            "blocked_tasks": {},
            "task_completion_percent": 40.0,
        },
        "decision_history": [
            {
                "decision_id": "d_001",
                "timestamp": datetime.utcnow().isoformat(),
                "decision_type": "code_change",
                "description": "Refactored search algorithm",
                "confidence": 0.92,
                "outcome": "success",
            }
        ],
        "repository_state": {
            "branch": "main",
            "commit_sha": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
            "uncommitted_changes": 0,
        },
        "context_state": {
            "ooda_cycle": "decide",
            "decision_history": [],
        },
    }


# ============================================================================
# Checkpoint Creation Tests
# ============================================================================

class TestCheckpointCreation:
    """Tests for checkpoint creation and storage."""
    
    def test_create_basic_checkpoint(self, checkpoint_manager, sample_checkpoint_state):
        """Test creating a basic checkpoint."""
        meta = checkpoint_manager.create_checkpoint(
            session_id=sample_checkpoint_state["session_id"],
            agent_state=sample_checkpoint_state["agent_state"],
            memory_snapshot=sample_checkpoint_state["memory_snapshot"],
            execution_progress=sample_checkpoint_state["execution_progress"],
            compress=True,
        )
        
        assert meta.checkpoint_id.startswith("cp_")
        assert meta.session_id == "S001"
        assert meta.compressed is True
        assert meta.compression_ratio > 1.0
        assert meta.uncompressed_size_bytes > 0
        assert meta.compressed_size_bytes > 0
        assert len(meta.checksum_sha256) == 64  # SHA256 hex length
    
    def test_checkpoint_compression_ratio(self, checkpoint_manager, sample_checkpoint_state):
        """Test that compression achieves target ratio."""
        meta = checkpoint_manager.create_checkpoint(
            session_id=sample_checkpoint_state["session_id"],
            agent_state=sample_checkpoint_state["agent_state"],
            memory_snapshot=sample_checkpoint_state["memory_snapshot"],
            execution_progress=sample_checkpoint_state["execution_progress"],
            compress=True,
        )
        
        # Target: > 2:1 compression for JSON data
        assert meta.compression_ratio > 2.0, \
            f"Compression ratio {meta.compression_ratio:.2f}:1 below target 2:1"
    
    def test_checkpoint_without_compression(self, checkpoint_manager, sample_checkpoint_state):
        """Test creating checkpoint without compression."""
        meta = checkpoint_manager.create_checkpoint(
            session_id=sample_checkpoint_state["session_id"],
            agent_state=sample_checkpoint_state["agent_state"],
            memory_snapshot=sample_checkpoint_state["memory_snapshot"],
            execution_progress=sample_checkpoint_state["execution_progress"],
            compress=False,
        )
        
        assert meta.compressed is False
        assert meta.compression_ratio == 1.0
        assert meta.compressed_size_bytes == meta.uncompressed_size_bytes
    
    def test_checkpoint_with_tags(self, checkpoint_manager, sample_checkpoint_state):
        """Test checkpoint creation with custom tags."""
        meta = checkpoint_manager.create_checkpoint(
            session_id=sample_checkpoint_state["session_id"],
            agent_state=sample_checkpoint_state["agent_state"],
            memory_snapshot=sample_checkpoint_state["memory_snapshot"],
            execution_progress=sample_checkpoint_state["execution_progress"],
            metadata={"milestone": "phase1", "priority": "high"},
        )
        
        assert meta.tags.get("milestone") == "phase1"
        assert meta.tags.get("priority") == "high"

    def test_checkpoint_keeps_lane_and_cost_metadata_fidelity(self, checkpoint_manager, sample_checkpoint_state):
        """Lane/cost metadata must round-trip without losing valid zeroes."""
        meta = checkpoint_manager.create_checkpoint(
            session_id=sample_checkpoint_state["session_id"],
            agent_state=sample_checkpoint_state["agent_state"],
            memory_snapshot=sample_checkpoint_state["memory_snapshot"],
            execution_progress=sample_checkpoint_state["execution_progress"],
            lane_bucket="P2",
            checkpoint_state="verified",
            budget_remaining=0,
            estimated_cost=0,
            cost_score=0,
            task_id="task-123",
            last_successful_stage="audit",
            resume_from_checkpoint_id="cp_prev",
        )

        assert meta.lane_bucket == "P2"
        assert meta.checkpoint_state == "verified"
        assert meta.budget_remaining == 0
        assert meta.estimated_cost == 0
        assert meta.cost_score == 0
        assert meta.tags["budget_remaining"] == 0
        assert meta.tags["estimated_cost"] == 0
        assert meta.tags["cost_score"] == 0

    def test_list_checkpoints_normalizes_double_suffix_checkpoint_ids(self, checkpoint_manager, sample_checkpoint_state):
        """List output should return the canonical cp_* ID, even for .json.zst files."""
        meta = checkpoint_manager.create_checkpoint(
            session_id=sample_checkpoint_state["session_id"],
            agent_state=sample_checkpoint_state["agent_state"],
            memory_snapshot=sample_checkpoint_state["memory_snapshot"],
            execution_progress=sample_checkpoint_state["execution_progress"],
            compress=True,
        )

        listed = checkpoint_manager.list_checkpoints(session_id=sample_checkpoint_state["session_id"])

        assert [item.checkpoint_id for item in listed] == [meta.checkpoint_id]

    def test_checkpoint_with_full_state(self, checkpoint_manager, sample_checkpoint_state):
        """Test checkpoint with all optional fields."""
        meta = checkpoint_manager.create_checkpoint(
            session_id=sample_checkpoint_state["session_id"],
            agent_state=sample_checkpoint_state["agent_state"],
            memory_snapshot=sample_checkpoint_state["memory_snapshot"],
            execution_progress=sample_checkpoint_state["execution_progress"],
            decision_history=sample_checkpoint_state["decision_history"],
            repository_state=sample_checkpoint_state["repository_state"],
            context_state=sample_checkpoint_state["context_state"],
        )
        
        assert meta.checkpoint_id is not None
        assert len(meta.checksum_sha256) == 64
    
    def test_checkpoint_uniqueness(self, checkpoint_manager, sample_checkpoint_state):
        """Test that each checkpoint gets a unique ID."""
        meta1 = checkpoint_manager.create_checkpoint(
            session_id="S001",
            agent_state={},
            memory_snapshot={},
            execution_progress={},
        )
        
        meta2 = checkpoint_manager.create_checkpoint(
            session_id="S001",
            agent_state={},
            memory_snapshot={},
            execution_progress={},
        )
        
        assert meta1.checkpoint_id != meta2.checkpoint_id

    @pytest.mark.parametrize(
        "malicious_session_id",
        [
            "../../escape",
            "..\\..\\escape",
            "/tmp/escape",
            "C:\\tmp\\escape",
            "session/../../escape",
            "session\\..\\escape",
            "..",
            "",
            "   ",
        ],
    )
    def test_rejects_session_id_path_traversal(self, checkpoint_manager, sample_checkpoint_state, malicious_session_id):
        """Traversal and absolute-path variants must not escape the session checkpoint root."""
        with pytest.raises(StorageError, match="Invalid session_id"):
            checkpoint_manager.create_checkpoint(
                session_id=malicious_session_id,
                agent_state=sample_checkpoint_state["agent_state"],
                memory_snapshot=sample_checkpoint_state["memory_snapshot"],
                execution_progress=sample_checkpoint_state["execution_progress"],
            )

        with pytest.raises(StorageError, match="Invalid session_id"):
            checkpoint_manager.list_checkpoints(session_id=malicious_session_id)

        with pytest.raises(StorageError, match="Invalid session_id"):
            checkpoint_manager.restore_checkpoint("cp_ignored", session_id=malicious_session_id)


# ============================================================================
# Checkpoint Restore Tests
# ============================================================================

class TestCheckpointRestore:
    """Tests for checkpoint restoration."""
    
    def test_restore_basic_checkpoint(self, checkpoint_manager, sample_checkpoint_state):
        """Test restoring a checkpoint."""
        meta = checkpoint_manager.create_checkpoint(
            session_id="S001",
            agent_state=sample_checkpoint_state["agent_state"],
            memory_snapshot=sample_checkpoint_state["memory_snapshot"],
            execution_progress=sample_checkpoint_state["execution_progress"],
        )
        
        restored = checkpoint_manager.restore_checkpoint(meta.checkpoint_id)
        
        assert restored["session_id"] == "S001"
        assert restored["agent_state"]["status"] == "in_progress"
        assert len(restored["memory_snapshot"]["short_term_memory"]) == 1

    def test_warm_start_preserves_zero_cost_metadata(self, resume_engine, checkpoint_manager, sample_checkpoint_state):
        """Warm start must retain valid zero values for budget and cost fields."""
        meta = checkpoint_manager.create_checkpoint(
            session_id="S001",
            agent_state=sample_checkpoint_state["agent_state"],
            memory_snapshot=sample_checkpoint_state["memory_snapshot"],
            execution_progress=sample_checkpoint_state["execution_progress"],
            lane_bucket="S1",
            checkpoint_state="verified",
            budget_remaining=0,
            estimated_cost=0,
            cost_score=0,
        )

        context = resume_engine.warm_start(checkpoint_id=meta.checkpoint_id)
        assert context.lane_bucket == "S1"
        assert context.checkpoint_state == "verified"
        assert context.budget_remaining == 0
        assert context.estimated_cost == 0
        assert context.cost_score == 0
    
    def test_restore_nonexistent_checkpoint(self, checkpoint_manager):
        """Test restoring nonexistent checkpoint raises error."""
        with pytest.raises(CheckpointNotFoundError):
            checkpoint_manager.restore_checkpoint("cp_nonexistent")
    
    def test_restore_with_session_validation(self, checkpoint_manager, sample_checkpoint_state):
        """Test restore with session ID validation."""
        meta = checkpoint_manager.create_checkpoint(
            session_id="S001",
            agent_state=sample_checkpoint_state["agent_state"],
            memory_snapshot=sample_checkpoint_state["memory_snapshot"],
            execution_progress=sample_checkpoint_state["execution_progress"],
        )
        
        # Restore with correct session
        restored = checkpoint_manager.restore_checkpoint(
            meta.checkpoint_id,
            session_id="S001"
        )
        assert restored["session_id"] == "S001"
    
    def test_restore_preserves_memory_state(self, checkpoint_manager, sample_checkpoint_state):
        """Test that memory state is fully preserved."""
        original_memory = sample_checkpoint_state["memory_snapshot"]
        
        meta = checkpoint_manager.create_checkpoint(
            session_id="S001",
            agent_state={},
            memory_snapshot=original_memory,
            execution_progress={},
        )
        
        restored = checkpoint_manager.restore_checkpoint(meta.checkpoint_id)
        restored_memory = restored["memory_snapshot"]
        
        assert restored_memory["total_patterns"] == original_memory["total_patterns"]
        assert len(restored_memory["short_term_memory"]) == len(original_memory["short_term_memory"])
        assert restored_memory["short_term_memory"][0]["pattern_id"] == "p_001"
    
    def test_restore_preserves_execution_progress(self, checkpoint_manager, sample_checkpoint_state):
        """Test that execution progress is fully preserved."""
        original_progress = sample_checkpoint_state["execution_progress"]
        
        meta = checkpoint_manager.create_checkpoint(
            session_id="S001",
            agent_state={},
            memory_snapshot={},
            execution_progress=original_progress,
        )
        
        restored = checkpoint_manager.restore_checkpoint(meta.checkpoint_id)
        restored_progress = restored["execution_progress"]
        
        assert restored_progress["current_task"] == "refactor_search"
        assert restored_progress["completed_tasks"] == ["analyze", "design"]
        assert restored_progress["task_completion_percent"] == 40.0


# ============================================================================
# Checkpoint Validation Tests
# ============================================================================

class TestCheckpointValidation:
    """Tests for checkpoint validation."""
    
    def test_validate_valid_checkpoint(self, checkpoint_manager, sample_checkpoint_state):
        """Test validating a valid checkpoint."""
        meta = checkpoint_manager.create_checkpoint(
            session_id="S001",
            agent_state=sample_checkpoint_state["agent_state"],
            memory_snapshot=sample_checkpoint_state["memory_snapshot"],
            execution_progress=sample_checkpoint_state["execution_progress"],
        )
        
        result = checkpoint_manager.validate_checkpoint(meta.checkpoint_id)
        
        assert result.is_valid is True
        assert result.integrity_score >= 0.95
        assert len(result.errors) == 0
        assert result.recommended_action == "restore"
    
    def test_validate_nonexistent_checkpoint(self, checkpoint_manager):
        """Test validating nonexistent checkpoint."""
        result = checkpoint_manager.validate_checkpoint("cp_nonexistent")
        
        assert result.is_valid is False
        assert result.integrity_score == 0.0
        assert len(result.errors) > 0
        assert result.recoverable is False
    
    def test_validate_quick_check(self, checkpoint_manager, sample_checkpoint_state):
        """Test quick validation mode."""
        meta = checkpoint_manager.create_checkpoint(
            session_id="S001",
            agent_state=sample_checkpoint_state["agent_state"],
            memory_snapshot=sample_checkpoint_state["memory_snapshot"],
            execution_progress=sample_checkpoint_state["execution_progress"],
        )
        
        result = checkpoint_manager.validate_checkpoint(
            meta.checkpoint_id,
            quick_check=True
        )
        
        assert result.validation_time_ms < 100  # Should be fast


# ============================================================================
# Checkpoint Listing Tests
# ============================================================================

class TestCheckpointListing:
    """Tests for listing checkpoints."""
    
    def test_list_empty_checkpoints(self, checkpoint_manager):
        """Test listing when no checkpoints exist."""
        checkpoints = checkpoint_manager.list_checkpoints()
        assert len(checkpoints) == 0
    
    def test_list_checkpoints_by_session(self, checkpoint_manager):
        """Test listing checkpoints for specific session."""
        # Create checkpoints for different sessions
        for session_id in ["S001", "S002"]:
            for i in range(3):
                checkpoint_manager.create_checkpoint(
                    session_id=session_id,
                    agent_state={},
                    memory_snapshot={},
                    execution_progress={},
                )
        
        # List for S001
        checkpoints = checkpoint_manager.list_checkpoints(session_id="S001")
        assert len(checkpoints) == 3
        assert all(cp.session_id == "S001" for cp in checkpoints)
    
    def test_list_with_limit_and_offset(self, checkpoint_manager):
        """Test pagination in listing."""
        # Create 10 checkpoints
        for i in range(10):
            checkpoint_manager.create_checkpoint(
                session_id="S001",
                agent_state={},
                memory_snapshot={},
                execution_progress={},
            )
        
        # Get first 3
        page1 = checkpoint_manager.list_checkpoints(limit=3, offset=0)
        assert len(page1) == 3
        
        # Get next 3
        page2 = checkpoint_manager.list_checkpoints(limit=3, offset=3)
        assert len(page2) == 3
        
        # Ensure different checkpoints
        ids1 = {cp.checkpoint_id for cp in page1}
        ids2 = {cp.checkpoint_id for cp in page2}
        assert len(ids1 & ids2) == 0


# ============================================================================
# Checkpoint Deletion Tests
# ============================================================================

class TestCheckpointDeletion:
    """Tests for checkpoint deletion."""
    
    def test_delete_checkpoint(self, checkpoint_manager, sample_checkpoint_state):
        """Test deleting a checkpoint."""
        meta = checkpoint_manager.create_checkpoint(
            session_id="S001",
            agent_state=sample_checkpoint_state["agent_state"],
            memory_snapshot=sample_checkpoint_state["memory_snapshot"],
            execution_progress=sample_checkpoint_state["execution_progress"],
        )
        
        result = checkpoint_manager.delete_checkpoint(meta.checkpoint_id)
        
        assert result.success is True
        assert result.checkpoint_id == meta.checkpoint_id
        assert result.bytes_freed > 0
        
        # Verify it's deleted
        with pytest.raises(CheckpointNotFoundError):
            checkpoint_manager.restore_checkpoint(meta.checkpoint_id)
    
    def test_delete_nonexistent_checkpoint(self, checkpoint_manager):
        """Test deleting nonexistent checkpoint."""
        with pytest.raises(CheckpointNotFoundError):
            checkpoint_manager.delete_checkpoint("cp_nonexistent")
    
    def test_delete_with_audit_reason(self, checkpoint_manager, sample_checkpoint_state):
        """Test deletion with audit trail."""
        meta = checkpoint_manager.create_checkpoint(
            session_id="S001",
            agent_state=sample_checkpoint_state["agent_state"],
            memory_snapshot=sample_checkpoint_state["memory_snapshot"],
            execution_progress=sample_checkpoint_state["execution_progress"],
        )
        
        result = checkpoint_manager.delete_checkpoint(
            meta.checkpoint_id,
            audit_reason="Exceeded retention window"
        )
        
        assert result.reason == "Exceeded retention window"


# ============================================================================
# Session Resume Tests
# ============================================================================

class TestSessionResume:
    """Tests for session resume engine."""
    
    def test_warm_start_basic(self, resume_engine, checkpoint_manager, sample_checkpoint_state):
        """Test basic warm-start from checkpoint."""
        meta = checkpoint_manager.create_checkpoint(
            session_id="S001",
            agent_state=sample_checkpoint_state["agent_state"],
            memory_snapshot=sample_checkpoint_state["memory_snapshot"],
            execution_progress=sample_checkpoint_state["execution_progress"],
        )
        
        context = resume_engine.warm_start(checkpoint_id=meta.checkpoint_id)
        
        assert context.is_valid() is True
        assert context.session_id == "S001"
        assert context.checkpoint_id == meta.checkpoint_id
        assert context.warmup_complete is True
    
    def test_warm_start_with_context_provider(
        self,
        resume_engine,
        checkpoint_manager,
        sample_checkpoint_state
    ):
        """Test warm-start with context provider."""
        meta = checkpoint_manager.create_checkpoint(
            session_id="S001",
            agent_state=sample_checkpoint_state["agent_state"],
            memory_snapshot=sample_checkpoint_state["memory_snapshot"],
            execution_progress=sample_checkpoint_state["execution_progress"],
        )
        
        provider = ContextProvider()
        context = resume_engine.warm_start(
            checkpoint_id=meta.checkpoint_id,
            context_provider=provider
        )
        
        assert context.observation_data is not None
        assert context.orientation_data is not None
        assert context.decision_context is not None
    
    def test_warm_start_preserves_decision_history(
        self,
        resume_engine,
        checkpoint_manager,
        sample_checkpoint_state
    ):
        """Test that decision history is preserved in resume."""
        meta = checkpoint_manager.create_checkpoint(
            session_id="S001",
            agent_state=sample_checkpoint_state["agent_state"],
            memory_snapshot=sample_checkpoint_state["memory_snapshot"],
            execution_progress=sample_checkpoint_state["execution_progress"],
            decision_history=sample_checkpoint_state["decision_history"],
        )
        
        context = resume_engine.warm_start(checkpoint_id=meta.checkpoint_id)
        
        assert len(context.decision_history) == 1
        assert context.decision_history[0]["decision_id"] == "d_001"
    
    def test_validate_and_recover(self, resume_engine, checkpoint_manager, sample_checkpoint_state):
        """Test validate_and_recover with valid checkpoint."""
        meta = checkpoint_manager.create_checkpoint(
            session_id="S001",
            agent_state=sample_checkpoint_state["agent_state"],
            memory_snapshot=sample_checkpoint_state["memory_snapshot"],
            execution_progress=sample_checkpoint_state["execution_progress"],
        )
        
        doc = resume_engine.validate_and_recover(checkpoint_id=meta.checkpoint_id)
        
        assert doc["session_id"] == "S001"
        assert "_recovery_metadata" in doc or doc["session_id"] == "S001"


# ============================================================================
# Performance Tests
# ============================================================================

class TestPerformance:
    """Tests for performance characteristics."""
    
    def test_checkpoint_creation_latency(self, checkpoint_manager, sample_checkpoint_state):
        """Test checkpoint creation is fast."""
        import time
        
        start = time.time()
        meta = checkpoint_manager.create_checkpoint(
            session_id="S001",
            agent_state=sample_checkpoint_state["agent_state"],
            memory_snapshot=sample_checkpoint_state["memory_snapshot"],
            execution_progress=sample_checkpoint_state["execution_progress"],
        )
        elapsed_ms = (time.time() - start) * 1000
        
        # Target: < 50ms for checkpoint creation
        assert elapsed_ms < 50, f"Creation took {elapsed_ms:.1f}ms (target < 50ms)"
    
    def test_checkpoint_restore_latency(self, checkpoint_manager, sample_checkpoint_state):
        """Test checkpoint restore is fast."""
        import time
        
        meta = checkpoint_manager.create_checkpoint(
            session_id="S001",
            agent_state=sample_checkpoint_state["agent_state"],
            memory_snapshot=sample_checkpoint_state["memory_snapshot"],
            execution_progress=sample_checkpoint_state["execution_progress"],
        )
        
        start = time.time()
        doc = checkpoint_manager.restore_checkpoint(meta.checkpoint_id)
        elapsed_ms = (time.time() - start) * 1000
        
        # Target: < 100ms for restore
        assert elapsed_ms < 100, f"Restore took {elapsed_ms:.1f}ms (target < 100ms)"
    
    def test_large_checkpoint_handling(self, checkpoint_manager):
        """Test handling large checkpoints."""
        # Create checkpoint with large memory state
        large_memory = {
            "short_term_memory": [
                {
                    "pattern_id": f"p_{i:04d}",
                    "category": "optimization",
                    "content": "x" * 1000,
                    "relevance_score": 0.9,
                    "last_used": datetime.utcnow().isoformat(),
                    "usage_count": 10,
                }
                for i in range(100)
            ],
            "long_term_memory": [],
            "total_patterns": 100,
        }
        
        meta = checkpoint_manager.create_checkpoint(
            session_id="S001",
            agent_state={},
            memory_snapshot=large_memory,
            execution_progress={},
        )
        
        # Should compress efficiently
        assert meta.compression_ratio > 3.0
        
        # Should restore without issues
        restored = checkpoint_manager.restore_checkpoint(meta.checkpoint_id)
        assert len(restored["memory_snapshot"]["short_term_memory"]) == 100


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for complete workflows."""
    
    def test_complete_checkpoint_restore_cycle(
        self,
        checkpoint_manager,
        resume_engine,
        sample_checkpoint_state
    ):
        """Test complete checkpoint -> restore -> resume cycle."""
        # 1. Create checkpoint
        meta = checkpoint_manager.create_checkpoint(
            session_id="S001",
            agent_state=sample_checkpoint_state["agent_state"],
            memory_snapshot=sample_checkpoint_state["memory_snapshot"],
            execution_progress=sample_checkpoint_state["execution_progress"],
            decision_history=sample_checkpoint_state["decision_history"],
        )
        
        # 2. Validate checkpoint
        validation = checkpoint_manager.validate_checkpoint(meta.checkpoint_id)
        assert validation.is_valid is True
        
        # 3. Warm-start from checkpoint
        context = resume_engine.warm_start(checkpoint_id=meta.checkpoint_id)
        assert context.is_valid() is True
        
        # 4. Verify all state is present
        assert context.agent_state["status"] == "in_progress"
        assert context.memory_snapshot["total_patterns"] == 1
        assert context.execution_progress["current_task"] == "refactor_search"
        assert len(context.decision_history) == 1
    
    def test_multiple_sessions_isolation(
        self,
        checkpoint_manager,
        sample_checkpoint_state
    ):
        """Test that multiple sessions don't interfere."""
        # Create checkpoints for different sessions
        meta_s1 = checkpoint_manager.create_checkpoint(
            session_id="S001",
            agent_state={"id": "s1"},
            memory_snapshot={},
            execution_progress={"current_task": "task_s1"},
        )
        
        meta_s2 = checkpoint_manager.create_checkpoint(
            session_id="S002",
            agent_state={"id": "s2"},
            memory_snapshot={},
            execution_progress={"current_task": "task_s2"},
        )
        
        # Restore both
        doc_s1 = checkpoint_manager.restore_checkpoint(meta_s1.checkpoint_id)
        doc_s2 = checkpoint_manager.restore_checkpoint(meta_s2.checkpoint_id)
        
        # Verify isolation
        assert doc_s1["session_id"] == "S001"
        assert doc_s2["session_id"] == "S002"
        assert doc_s1["execution_progress"]["current_task"] == "task_s1"
        assert doc_s2["execution_progress"]["current_task"] == "task_s2"


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
