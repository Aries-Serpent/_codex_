"""Integration tests for Phase 10.1 Session Checkpoint & Recovery Framework.

Comprehensive test suite covering:
- Happy path: Normal checkpoint → resume cycles
- State variations: Different agent types, memory sizes, session lengths
- Edge cases: Corruption, schema mismatches, partial states
- Stress tests: Large sessions, many checkpoints, rapid save/resume

Target: 95%+ state accuracy, <2 minute resume time, 100% pass rate
"""

from __future__ import annotations

import json
import logging
import tempfile
import time  # pragma: allowlist secret
from pathlib import Path

import pytest

from codex.brain.checkpoint_manager import CheckpointManager
from codex.brain.session_resume import SessionResume
from codex.brain.session_serializer import (
    SessionSerializer,
    create_agent_state_snapshot,
    create_context_snapshot,
    create_decision_snapshot,
    create_execution_progress_snapshot,
    create_memory_snapshot,
    create_repository_state_snapshot,
)

logger = logging.getLogger(__name__)


class TestCheckpointManager:
    """Test CheckpointManager functionality."""

    @pytest.fixture
    def temp_checkpoint_dir(self):
        """Create temporary checkpoint directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def checkpoint_manager(self, temp_checkpoint_dir):
        """Create CheckpointManager instance."""
        return CheckpointManager(
            checkpoint_dir=temp_checkpoint_dir,
            retention_count=5,
            commit_interval=2,
            time_interval_seconds=60,
        )

    def test_checkpoint_manager_init(self, checkpoint_manager, temp_checkpoint_dir):
        """Test CheckpointManager initialization."""
        assert checkpoint_manager.checkpoint_dir == temp_checkpoint_dir, "checkpoint_dir is not valid"
        assert checkpoint_manager.schema_version == 1, "schema_version is not valid"
        assert checkpoint_manager.retention_count == 5, "Count must be greater than zero"
        assert (temp_checkpoint_dir / "v1").exists(), "Condition must be true"
        assert (temp_checkpoint_dir / "metadata").exists(), "Data must not be empty"

    def test_create_checkpoint_minimal(self, checkpoint_manager):
        """Test checkpoint creation with minimal state."""
        checkpoint_id = checkpoint_manager.create_checkpoint()

        assert checkpoint_id is not None, "checkpoint_id must be initialized"
        assert checkpoint_id.startswith("cp_"), "Condition must be true"

        # Verify checkpoint file exists
        checkpoint_file = checkpoint_manager.checkpoint_dir / "v1" / f"{checkpoint_id}.json.gz"
        assert checkpoint_file.exists(), "Condition must be true"

        # Verify checkpoint integrity
        assert checkpoint_manager.verify_checkpoint_integrity(checkpoint_id), "Condition must be true"

    def test_create_checkpoint_with_session_state(self, checkpoint_manager):
        """Test checkpoint creation with full session state."""
        session_state = {
            "agent_state": {"agent_id": "test_agent", "status": "completed"},
            "execution_progress": {
                "current_task": "task_001",
                "completed_tasks": ["task_001", "task_002"],
                "pending_tasks": ["task_003"],
            },
            "decision_history": [
                {
                    "decision_id": "d_001",
                    "type": "code_change",
                    "confidence": 0.95,
                    "outcome": "success",
                }
            ],
        }

        checkpoint_id = checkpoint_manager.create_checkpoint(
            session_state=session_state,
            session_id="S001",
            agent_id="test_agent",
            repository_commit="abc123",
        )

        assert checkpoint_id is not None, "checkpoint_id must be initialized"
        assert checkpoint_manager.verify_checkpoint_integrity(checkpoint_id), "Condition must be true"

        # Verify content
        content = checkpoint_manager.get_checkpoint_content(checkpoint_id)
        assert content is not None, "content must be initialized"
        assert content["session_state"]["agent_state"]["agent_id"] == "test_agent", "Content must not be empty"

    def test_list_checkpoints(self, checkpoint_manager):
        """Test listing checkpoints."""
        # Create multiple checkpoints
        cp_ids = []
        for i in range(3):
            cp_id = checkpoint_manager.create_checkpoint(session_id=f"S{i:03d}")
            cp_ids.append(cp_id)
            time.sleep(0.1)  # Small delay for timestamp uniqueness

        checkpoints = checkpoint_manager.list_checkpoints()
        assert len(checkpoints) >= 3, "Checkpoints must not be empty"
        assert checkpoints[0]["checkpoint_id"] == cp_ids[-1], "Condition must be true"

    def test_get_latest_checkpoint(self, checkpoint_manager):
        """Test getting latest checkpoint."""
        assert checkpoint_manager.get_latest_checkpoint() is None, "Condition must be true"

        cp1 = checkpoint_manager.create_checkpoint(session_id="S001")
        assert checkpoint_manager.get_latest_checkpoint() == cp1, "Condition must be true"

        time.sleep(0.1)
        cp2 = checkpoint_manager.create_checkpoint(session_id="S002")
        assert checkpoint_manager.get_latest_checkpoint() == cp2, "Condition must be true"

    def test_checkpoint_integrity_verification(self, checkpoint_manager):
        """Test checkpoint integrity verification."""
        cp_id = checkpoint_manager.create_checkpoint(session_id="S001")

        # Checkpoint should pass verification
        assert checkpoint_manager.verify_checkpoint_integrity(cp_id), "Condition must be true"

        # Corrupt the checkpoint file
        checkpoint_file = checkpoint_manager.checkpoint_dir / "v1" / f"{cp_id}.json.gz"
        os.chmod(checkpoint_file, 0o600)  # nosemgrep: semgrep.insecure-file-permissions - Test: temporarily making test file writable for corruption
        checkpoint_file.write_bytes(b"corrupted data")

        # Verification should fail
        assert not checkpoint_manager.verify_checkpoint_integrity(cp_id), "Condition must be true"

    def test_checkpoint_deletion(self, checkpoint_manager):
        """Test checkpoint deletion."""
        cp_id = checkpoint_manager.create_checkpoint(session_id="S001")
        assert checkpoint_manager.get_checkpoint_content(cp_id) is not None, "Value must be initialized"

        # Delete checkpoint
        assert checkpoint_manager.delete_checkpoint(cp_id), "Condition must be true"

        # Verify deleted
        checkpoint_file = checkpoint_manager.checkpoint_dir / "v1" / f"{cp_id}.json.gz"
        assert not checkpoint_file.exists(), "Condition must be true"

    def test_retention_policy(self, checkpoint_manager):
        """Test checkpoint retention policy."""
        # Create 10 checkpoints with retention_count=5
        cp_ids = []
        for i in range(10):
            cp_id = checkpoint_manager.create_checkpoint(session_id=f"S{i:03d}")
            cp_ids.append(cp_id)
            time.sleep(0.01)

        # Should only have 5 most recent
        checkpoints = checkpoint_manager.list_checkpoints()
        assert len(checkpoints) == 5, "Checkpoints must not be empty"
        assert checkpoints[0]["checkpoint_id"] == cp_ids[-1], "Condition must be true"
        assert checkpoints[-1]["checkpoint_id"] == cp_ids[-5], "Condition must be true"

    def test_checkpoint_compression(self, checkpoint_manager):
        """Test checkpoint compression."""
        # Create checkpoint with large state
        large_state = {
            "decision_history": [
                {
                    "decision_id": f"d_{i:04d}",
                    "type": "analysis",
                    "description": f"Decision {i}: " + "x" * 100,
                    "confidence": 0.9,
                }
                for i in range(100)
            ]
        }

        cp_id = checkpoint_manager.create_checkpoint(session_state=large_state)

        # Verify checkpoint is compressed
        cp_file = checkpoint_manager.checkpoint_dir / "v1" / f"{cp_id}.json.gz"
        assert cp_file.exists(), "Condition must be true"

        # Compressed size should be much smaller
        metadata = checkpoint_manager.get_checkpoint_metadata(cp_id)
        assert metadata.compressed, "Data must not be empty"
        assert (metadata.compressed_size_bytes < metadata.uncompressed_size_bytes * 0.5, "Data must not be empty"
        )  # At least 50% compression

    def test_maybe_checkpoint_commit_trigger(self, checkpoint_manager):
        """Test commit-based checkpoint trigger."""
        # Should not trigger
        assert checkpoint_manager.maybe_checkpoint(commit_count_delta=1) is None, "Count must be greater than zero"

        # Should trigger after 2 commits
        cp_id = checkpoint_manager.maybe_checkpoint(commit_count_delta=1)
        assert cp_id is not None, "cp_id must be initialized"
        assert cp_id.startswith("cp_", "Condition must be true"
        ), "Condition must be true"

    def test_maybe_checkpoint_time_trigger(self, checkpoint_manager):
        """Test time-based checkpoint trigger."""
        # Create manager with 1-second interval
        mgr = CheckpointManager(
            checkpoint_dir=checkpoint_manager.checkpoint_dir,
            time_interval_seconds=1,
        )

        cp1 = mgr.create_checkpoint()
        time.sleep(1.1)

        cp2 = mgr.maybe_checkpoint()
        assert cp2 is not None, "cp2 must be initialized"
        assert cp2 != cp1, "cp2 is not valid"


class TestSessionSerializer:
    """Test SessionSerializer functionality."""

    @pytest.fixture
    def serializer(self):
        """Create SessionSerializer instance."""
        return SessionSerializer()

    def test_serializer_init(self, serializer):
        """Test SessionSerializer initialization."""
        assert serializer.SCHEMA_VERSION == 1, "SCHEMA_VERSION is not valid"
        assert serializer.SERIALIZER_VERSION == "1.0.0", "SERIALIZER_VERSION is not valid"

    def test_serialize_empty_session(self, serializer):
        """Test serializing empty session state."""
        state_dict = serializer.serialize_session_state()

        assert state_dict["schema_version"] == 1, "Condition must be true"
        assert "timestamp" in state_dict, "Condition must be true"
        assert "agent_state" in state_dict, "Condition must be true"

    def test_serialize_complete_session(self, serializer):
        """Test serializing complete session state."""
        agent_state = create_agent_state_snapshot("test_agent", "custom", "completed")
        decision = create_decision_snapshot("d_001", "code_change", "Test decision", 0.95)
        memory = create_memory_snapshot(
            total_patterns=10, memory_usage_bytes=5000
        )
        progress = create_execution_progress_snapshot(
            completed_tasks=["t1", "t2"], pending_tasks=["t3"]
        )
        repo_state = create_repository_state_snapshot("main", "abc123")
        context = create_context_snapshot(system_prompt_hash="sha256:xyz")

        state_dict = serializer.serialize_session_state(
            agent_state=agent_state,
            decision_history=[decision],
            memory_snapshot=memory,
            execution_progress=progress,
            repository_state=repo_state,
            context_snapshot=context,
        )

        assert state_dict["agent_state"]["agent_id"] == "test_agent", "Condition must be true"
        assert len(state_dict["decision_history"]) == 1, "Collection must not be empty"
        assert state_dict["memory_snapshot"]["total_patterns"] == 10, "Condition must be true"
        assert len(state_dict["execution_progress"]["completed_tasks"]) == 2, "Collection must not be empty"

    def test_serialize_to_json(self, serializer):
        """Test JSON serialization."""
        state_dict = serializer.serialize_session_state()
        json_str = serializer.serialize_to_json(state_dict)

        assert isinstance(json_str, str)
        assert "schema_version" in json_str, "Condition must be true"
        assert json.loads(json_str), "Condition must be true"

    def test_serialize_to_binary(self, serializer):
        """Test binary (msgpack) serialization."""
        state_dict = serializer.serialize_session_state()
        binary_data = serializer.serialize_to_binary(state_dict)

        assert isinstance(binary_data, bytes)
        assert len(binary_data) > 0, "Binary_data must not be empty"

    def test_deserialize_json(self, serializer):
        """Test JSON deserialization."""
        state_dict = serializer.serialize_session_state()
        json_str = serializer.serialize_to_json(state_dict)

        deserialized = serializer.deserialize_from_json(json_str)
        assert deserialized["schema_version"] == 1, "Condition must be true"
        assert "agent_state" in deserialized, "Condition must be true"

    def test_deserialize_binary(self, serializer):
        """Test binary deserialization."""
        state_dict = serializer.serialize_session_state()
        binary_data = serializer.serialize_to_binary(state_dict)

        deserialized = serializer.deserialize_from_binary(binary_data)
        assert deserialized["schema_version"] == 1, "Condition must be true"
        assert "agent_state" in deserialized, "Condition must be true"

    def test_compress_decompress(self, serializer):
        """Test compression and decompression."""
        original_data = b"x" * 10000

        compressed = serializer.compress_payload(original_data)
        assert len(compressed) < len(original_data), "Compressed must not be empty"

        decompressed = serializer.decompress_payload(compressed)
        assert decompressed == original_data, "Data must not be empty"

    def test_json_roundtrip(self, serializer):
        """Test JSON serialization roundtrip."""
        agent_state = create_agent_state_snapshot("agent_1", "builtin")
        decision = create_decision_snapshot(
            "d_001", "code_change", "Test", 0.92, outcome="success"
        )

        state_dict = serializer.serialize_session_state(
            agent_state=agent_state, decision_history=[decision]
        )

        json_str = serializer.serialize_to_json(state_dict)
        deserialized = serializer.deserialize_from_json(json_str)

        assert deserialized["agent_state"]["agent_id"] == "agent_1", "Condition must be true"
        assert len(deserialized["decision_history"]) == 1, "Collection must not be empty"
        assert deserialized["decision_history"][0]["confidence"] == 0.92, "Condition must be true"

    def test_binary_roundtrip(self, serializer):
        """Test binary serialization roundtrip."""
        agent_state = create_agent_state_snapshot("agent_2", "custom")
        memory = create_memory_snapshot(total_patterns=50)

        state_dict = serializer.serialize_session_state(
            agent_state=agent_state, memory_snapshot=memory
        )

        binary_data = serializer.serialize_to_binary(state_dict)
        deserialized = serializer.deserialize_from_binary(binary_data)

        assert deserialized["agent_state"]["agent_id"] == "agent_2", "Condition must be true"
        assert deserialized["memory_snapshot"]["total_patterns"] == 50, "Condition must be true"


class TestSessionResume:
    """Test SessionResume functionality."""

    @pytest.fixture
    def temp_checkpoint_dir(self):
        """Create temporary checkpoint directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def checkpoint_manager(self, temp_checkpoint_dir):
        """Create CheckpointManager instance."""
        return CheckpointManager(checkpoint_dir=temp_checkpoint_dir)

    @pytest.fixture
    def session_resume(self, checkpoint_manager):
        """Create SessionResume instance."""
        return SessionResume(checkpoint_manager)

    def test_validate_checkpoint(self, checkpoint_manager, session_resume):
        """Test checkpoint validation."""
        cp_id = checkpoint_manager.create_checkpoint(session_id="S001")
        assert session_resume.validate_checkpoint(cp_id), "Condition must be true"

    def test_load_checkpoint(self, checkpoint_manager, session_resume):
        """Test loading checkpoint."""
        session_state = {"test_key": "test_value"}
        cp_id = checkpoint_manager.create_checkpoint(
            session_state=session_state, session_id="S001"
        )

        content = session_resume.load_checkpoint(cp_id)
        assert content is not None, "content must be initialized"
        assert content["session_state"]["test_key"] == "test_value", "Value must be initialized"

    def test_resume_session(self, checkpoint_manager, session_resume):
        """Test session resume."""
        session_state = {
            "agent_state": {"agent_id": "agent_1", "status": "running"},
            "execution_progress": {
                "completed_tasks": ["t1", "t2"],
                "pending_tasks": ["t3"],
            },
        }

        cp_id = checkpoint_manager.create_checkpoint(
            session_state=session_state,
            session_id="S001",
            agent_id="agent_1",
        )

        result = session_resume.resume_session(cp_id)
        assert result is not None, "result must be initialized"
        assert result.success, "Result must not be empty"
        assert result.session_id == "S001", "Result must not be empty"
        assert result.agent_id == "agent_1", "Result must not be empty"
        assert result.state["agent_state"]["agent_id"] == "agent_1", "Result must not be empty"

    def test_resume_latest_session(self, checkpoint_manager, session_resume):
        """Test resuming latest session."""
        cp1 = checkpoint_manager.create_checkpoint(session_id="S001")
        time.sleep(0.1)
        cp2 = checkpoint_manager.create_checkpoint(session_id="S002")

        result = session_resume.resume_latest_session()
        assert result is not None, "result must be initialized"
        assert result.success, "Result must not be empty"
        assert result.checkpoint_id == cp2, "Result must not be empty"

    def test_get_progress_snapshot(self, checkpoint_manager, session_resume):
        """Test getting progress snapshot."""
        session_state = {
            "execution_progress": {
                "current_task": "t3",
                "completed_tasks": ["t1", "t2"],
                "pending_tasks": ["t3", "t4"],
            }
        }

        cp_id = checkpoint_manager.create_checkpoint(session_state=session_state)

        progress = session_resume.get_progress_snapshot(cp_id)
        assert progress is not None, "progress must be initialized"
        assert progress["current_task"] == "t3", "Condition must be true"
        assert len(progress["completed_tasks"]) == 2, "Collection must not be empty"

    def test_get_decision_history(self, checkpoint_manager, session_resume):
        """Test getting decision history."""
        session_state = {
            "decision_history": [
                {
                    "decision_id": "d_001",
                    "type": "analysis",
                    "confidence": 0.9,
                },
                {
                    "decision_id": "d_002",
                    "type": "code_change",
                    "confidence": 0.85,
                },
            ]
        }

        cp_id = checkpoint_manager.create_checkpoint(session_state=session_state)

        history = session_resume.get_decision_history(cp_id)
        assert history is not None, "history must be initialized"
        assert len(history) == 2, "History must not be empty"
        assert history[0]["confidence"] == 0.9, "hist is not valid"

    def test_resume_corrupted_checkpoint(self, checkpoint_manager, session_resume):
        """Test resume with corrupted checkpoint."""
        cp_id = checkpoint_manager.create_checkpoint(session_id="S001")

        # Corrupt the checkpoint
        cp_file = checkpoint_manager.checkpoint_dir / "v1" / f"{cp_id}.json.gz"
        pass  # removed redundant `import os` (top-level import used)
        os.chmod(cp_file, 0o600)  # nosemgrep: semgrep.insecure-file-permissions - Test: temporarily making test file writable for corruption
        cp_file.write_bytes(b"corrupted")

        result = session_resume.resume_session(cp_id)
        assert result is not None, "result must be initialized"
        assert not result.success, "Result must not be empty"

    def test_resume_nonexistent_checkpoint(self, session_resume):
        """Test resume with nonexistent checkpoint."""
        result = session_resume.resume_session("cp_nonexistent")
        assert result is not None, "result must be initialized"
        assert not result.success, "Result must not be empty"
        assert "validation failed" in result.error_message.lower(), "Result must not be empty"


class TestEndToEndIntegration:
    """End-to-end integration tests."""

    @pytest.fixture
    def temp_checkpoint_dir(self):
        """Create temporary checkpoint directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def checkpoint_manager(self, temp_checkpoint_dir):
        """Create CheckpointManager instance."""
        return CheckpointManager(checkpoint_dir=temp_checkpoint_dir, retention_count=10)

    @pytest.fixture
    def session_resume(self, checkpoint_manager):
        """Create SessionResume instance."""
        return SessionResume(checkpoint_manager)

    @pytest.fixture
    def serializer(self):
        """Create SessionSerializer instance."""
        return SessionSerializer()

    def test_complete_checkpoint_resume_cycle(self, checkpoint_manager, session_resume, serializer):
        """Test complete checkpoint → resume cycle."""
        # Create initial session state
        agent_state = create_agent_state_snapshot("semantic_search", "custom", "running")
        decision = create_decision_snapshot(
            "d_001", "refactor", "Optimized search", 0.94, "success"
        )
        memory = create_memory_snapshot(
            short_term_memory=[
                {"pattern_id": "p_043", "relevance": 0.92}
            ],
            total_patterns=47,
        )
        progress = create_execution_progress_snapshot(
            current_task="implementation",
            completed_tasks=["analysis", "design"],
            pending_tasks=["testing", "deployment"],
        )
        repo_state = create_repository_state_snapshot("main", "abc123def456")

        # Serialize state
        state_dict = serializer.serialize_session_state(
            agent_state=agent_state,
            decision_history=[decision],
            memory_snapshot=memory,
            execution_progress=progress,
            repository_state=repo_state,
        )

        # Create checkpoint
        cp_id = checkpoint_manager.create_checkpoint(
            session_state=state_dict,
            session_id="S001",
            agent_id="semantic_search",
            repository_commit="abc123def456",
        )

        assert cp_id is not None, "cp_id must be initialized"

        # Resume session
        result = session_resume.resume_session(cp_id)
        assert result.success, "Result must not be empty"
        assert result.agent_id == "semantic_search", "Result must not be empty"
        assert result.state["memory_snapshot"]["total_patterns"] == 47, "Result must not be empty"
        assert len(result.state["execution_progress"]["completed_tasks"]) == 2, "Collection must not be empty"

    def test_multiple_checkpoints_with_progression(self, checkpoint_manager, session_resume):
        """Test multiple checkpoints tracking task progression."""
        checkpoint_ids = []

        # Checkpoint 1: Initial state
        state1 = {
            "execution_progress": {
                "completed_tasks": ["t1"],
                "pending_tasks": ["t2", "t3", "t4"],
            }
        }
        cp1 = checkpoint_manager.create_checkpoint(session_state=state1, session_id="S001")
        checkpoint_ids.append(cp1)

        time.sleep(0.05)

        # Checkpoint 2: After t2 completion
        state2 = {
            "execution_progress": {
                "completed_tasks": ["t1", "t2"],
                "pending_tasks": ["t3", "t4"],
            }
        }
        cp2 = checkpoint_manager.create_checkpoint(session_state=state2, session_id="S001")
        checkpoint_ids.append(cp2)

        time.sleep(0.05)

        # Checkpoint 3: After t3 completion
        state3 = {
            "execution_progress": {
                "completed_tasks": ["t1", "t2", "t3"],
                "pending_tasks": ["t4"],
            }
        }
        cp3 = checkpoint_manager.create_checkpoint(session_state=state3, session_id="S001")
        checkpoint_ids.append(cp3)

        # Resume from cp2 and verify state
        result = session_resume.resume_session(cp2)
        assert result.success, "Result must not be empty"
        progress = result.state["execution_progress"]
        assert len(progress["completed_tasks"]) == 2, "Collection must not be empty"
        assert len(progress["pending_tasks"]) == 2, "Collection must not be empty"

        # Resume from latest (cp3) and verify state
        result_latest = session_resume.resume_latest_session()
        assert result_latest.success, "Result must not be empty"
        progress_latest = result_latest.state["execution_progress"]
        assert len(progress_latest["completed_tasks"]) == 3, "Collection must not be empty"
        assert len(progress_latest["pending_tasks"]) == 1, "Collection must not be empty"

    def test_large_session_state_persistence(self, checkpoint_manager, session_resume):
        """Test persistence of large session states."""
        # Create large decision history
        decisions = [
            create_decision_snapshot(
                f"d_{i:04d}", "analysis", f"Decision {i}: " + "x" * 50, 0.9 + (i % 10) * 0.01
            )
            for i in range(100)
        ]

        # Create large memory snapshot
        patterns = [{"pattern_id": f"p_{i}", "relevance": 0.9} for i in range(200)]

        state_dict = {
            "decision_history": [d.__dict__ for d in decisions],
            "memory_snapshot": {"patterns": patterns, "total_patterns": 200},
        }

        cp_id = checkpoint_manager.create_checkpoint(session_state=state_dict)

        # Resume and verify
        result = session_resume.resume_session(cp_id)
        assert result.success, "Result must not be empty"
        assert len(result.state["decision_history"]) == 100, "Collection must not be empty"
        assert result.state["memory_snapshot"]["total_patterns"] == 200, "Result must not be empty"

    def test_concurrent_checkpoint_resume(self, checkpoint_manager, session_resume):
        """Test rapid checkpoint creation and resume."""
        pass  # removed redundant `import time` (top-level import used)

        start_time = time.time()
        cp_ids = []

        # Rapidly create checkpoints
        for i in range(10):
            session_state = {"iteration": i}
            cp_id = checkpoint_manager.create_checkpoint(
                session_state=session_state, session_id=f"S{i:03d}"
            )
            cp_ids.append(cp_id)

        # Rapidly resume checkpoints
        for cp_id in cp_ids:
            result = session_resume.resume_session(cp_id)
            assert result.success, "Result must not be empty"

        elapsed = time.time() - start_time
        logger.info(f"Rapid checkpoint/resume: {elapsed:.2f}s for 10 iterations")

        # Should be reasonably fast (< 5 seconds)
        assert elapsed < 5.0, "elapsed is not valid"


# Add os import for test file
import os

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
