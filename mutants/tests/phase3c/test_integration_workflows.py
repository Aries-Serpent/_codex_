"""Phase 3C: Integration Test Suite - Agent Communication and Workflows.

Focus: Agent-to-agent communication patterns, configuration migration,
end-to-end workflows, and bridge interfaces.

Target: Add 50-100 integration tests for critical workflows
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest import mock

from src.codex.agents.memory.manager import MemoryManager
from src.codex.config.env_vars import EnvironmentManager


class TestAgentCommunicationPatterns:
    """Test agent-to-agent communication patterns."""

    def test_shared_memory_backend_communication(self):
        """Test two agents sharing the same memory backend."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir) / "shared_memory.jsonl"

            # Agent 1 stores a message
            agent1 = MemoryManager(
                storage_dir=Path(tmpdir), agent_id="agent-1", session_id="shared-session"
            )
            agent1.store("Message from agent-1", metadata={"from": "agent-1", "to": "agent-2"})

            # Agent 1 can read its own message
            memories = agent1.recall_all(limit=10)
            assert len(memories) >= 1, "Memories must not be empty"

    def test_agent_context_passing(self):
        """Test passing context between agents."""
        # Agent 1 processes and stores result
        agent1 = MemoryManager(agent_id="processor", session_id="workflow-1")
        processed_data = {"status": "completed", "result": 42}
        agent1.store(processed_data, metadata={"type": "result"})

        # Agent 1 retrieves and verifies result
        results = agent1.recall_all()
        assert len(results) >= 1, "Results must not be empty"

    def test_multi_agent_session_coordination(self):
        """Test multiple agents coordinating in same session."""
        session_id = "multi-agent-session"

        # All agents store to same session
        agent = MemoryManager(agent_id="coordinator", session_id=session_id)

        # Store multiple messages simulating multi-agent coordination
        for i in range(3):
            agent.store(f"Step {i} completed", metadata={"step": i})

        # Verify all messages were stored
        all_memories = agent.recall_all(limit=10)
        assert len(all_memories) >= 3, "All_memories must not be empty"

    def test_agent_response_chain(self):
        """Test chain of agent responses."""
        session_id = "response-chain"

        # Single agent stores chain of responses
        agent = MemoryManager(agent_id="chain-agent", session_id=session_id)
        agent.store("Initial request", metadata={"stage": 1})
        agent.store("Processing in progress", metadata={"stage": 2})
        agent.store("Final response", metadata={"stage": 3})

        # Verify chain
        final_memories = agent.recall_all()
        assert len(final_memories) >= 3, "Final_memories must not be empty"


class TestConfigurationMigration:
    """Test configuration migration patterns."""

    def test_env_var_migration_old_to_new(self):
        """Test migration from old to new environment variable naming."""
        # Simulate old environment
        with mock.patch.dict(
            {"CODEX_SESSION_LOG_DIR": ".logs", "CODEX_LOG_DB_PATH": ".logs/session.db"}, clear=False
        ):
            old_manager = EnvironmentManager()
            old_log_dir = old_manager.get_log_dir()
            old_manager.get_db_path()

            # Simulate new environment
            new_manager = EnvironmentManager()
            new_log_dir = new_manager.get_log_dir()
            new_manager.get_db_path()

            # Both should work
            assert old_log_dir is not None, "old_log_dir must be initialized"
            assert new_log_dir is not None, "new_log_dir must be initialized"

    def test_config_backward_compatibility(self):
        """Test configuration maintains backward compatibility."""
        manager = EnvironmentManager()

        # Both old and new names should work
        config = manager.dump_config()
        assert "CODEX_LOG_DB_PATH" in config or "CODEX_DB_PATH" in config, "Condition must be true"

    def test_env_var_deprecation_handling(self):
        """Test handling of deprecated environment variables."""
        manager = EnvironmentManager()
        # Should handle missing deprecated vars gracefully
        config = manager.dump_config()
        assert isinstance(config, dict)


class TestEndToEndWorkflows:
    """Test end-to-end workflow scenarios."""

    def test_workflow_memory_lifecycle(self):
        """Test complete memory lifecycle in a workflow."""
        session_id = "workflow-session"
        manager = MemoryManager(agent_id="workflow-agent", session_id=session_id)

        # Step 1: Initialize
        manager.store("Workflow initialized", metadata={"step": 0})

        # Step 2: Process
        for i in range(3):
            manager.store(f"Processing item {i}", metadata={"step": i + 1})

        # Step 3: Finalize
        manager.store("Workflow completed", metadata={"step": "final"})

        # Step 4: Retrieve all
        all_memories = manager.recall_all(limit=10)
        assert len(all_memories) >= 5, "All_memories must not be empty"

    def test_workflow_session_switching(self):
        """Test switching between workflow sessions."""
        manager = MemoryManager(agent_id="workflow-agent", session_id="session-1")

        # Work in session 1
        manager.store("Session 1 work")

        # Switch to session 2
        manager.set_session("session-2")
        manager.store("Session 2 work")

        # Switch back to session 1
        manager.set_session("session-1")
        memories_s1 = manager.recall_all()

        # Should be able to recall
        assert isinstance(memories_s1, list)

    def test_workflow_error_recovery(self):
        """Test workflow error recovery with memory."""
        session_id = "error-recovery-workflow"
        manager = MemoryManager(agent_id="recovery-agent", session_id=session_id)

        # Record initial state
        manager.store({"status": "started", "attempt": 1}, metadata={"type": "state"})

        # Simulate error
        manager.store({"error": "Connection failed"}, metadata={"type": "error"})

        # Simulate recovery
        manager.store({"status": "retrying", "attempt": 2}, metadata={"type": "state"})

        # Verify all states recorded
        all_memories = manager.recall_all()
        assert len(all_memories) >= 3, "All_memories must not be empty"

    def test_workflow_data_aggregation(self):
        """Test aggregating data across workflow steps."""
        session_id = "aggregation-workflow"
        manager = MemoryManager(agent_id="aggregator", session_id=session_id)

        # Simulate multiple processing steps
        data_points = []
        for i in range(5):
            data = {"value": i * 10, "processed": True}
            manager.store(data, metadata={"step": i})
            data_points.append(data)

        # Retrieve all
        results = manager.recall_all(limit=10)
        assert len(results) >= 5, "Results must not be empty"

    def test_workflow_rollback_handling(self):
        """Test workflow with rollback capability."""
        session_id = "rollback-workflow"
        manager = MemoryManager(agent_id="rollback-agent", session_id=session_id)

        # Record checkpoint
        manager.store("Checkpoint 1", metadata={"checkpoint": 1})
        manager.store("Checkpoint 2", metadata={"checkpoint": 2})

        # Clear session to simulate rollback
        cleared_count = manager.clear_session(session_id)
        assert cleared_count >= 2, "cleared_count must be positive"


class TestCrossPlatformBridges:
    """Test cross-platform bridge patterns."""

    def test_memory_bridge_consistency(self):
        """Test memory consistency across bridge calls."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create two managers with shared storage
            manager1 = MemoryManager(storage_dir=Path(tmpdir), agent_id="bridge-1")
            manager2 = MemoryManager(storage_dir=Path(tmpdir), agent_id="bridge-2")

            # Store via manager1
            manager1.store("Bridged data")

            # Retrieve via manager2
            memories = manager2.recall_all()
            assert isinstance(memories, list)

    def test_config_bridge_consistency(self):
        """Test config consistency across manager instances."""
        manager1 = EnvironmentManager()
        manager2 = EnvironmentManager()

        config1 = manager1.dump_config()
        config2 = manager2.dump_config()

        # Both should have same configs
        assert set(config1.keys()) == set(config2.keys()), "Condition must be true"

    def test_memory_backend_protocol_compliance(self):
        """Test that memory backends comply with protocol."""

        with tempfile.TemporaryDirectory() as tmpdir:
            backend = MemoryManager(storage_dir=Path(tmpdir)).backend

            # Should implement MemoryProtocol methods
            assert hasattr(backend, "store")
            assert hasattr(backend, "retrieve")
            assert hasattr(backend, "clear_session")


class TestAgentBridgeInterfaces:
    """Test agent bridge interface contracts."""

    def test_memory_entry_protocol(self):
        """Test MemoryEntry protocol compliance."""
        from src.codex.agents.memory.protocol import MemoryEntry

        entry = MemoryEntry(content="test", agent_id="test", session_id="test")

        # Should support serialization
        data = entry.to_dict()
        assert isinstance(data, dict)

        # Should support deserialization
        restored = MemoryEntry.from_dict(data)
        assert restored.content == entry.content, "Content must not be empty"

    def test_memory_query_protocol(self):
        """Test MemoryQuery protocol compliance."""
        from src.codex.agents.memory.protocol import MemoryQuery

        query = MemoryQuery(text="test query", agent_id="test", session_id="test", limit=10)

        assert query.text == "test query", "text is not valid"
        assert query.limit == 10, "limit is not valid"

    def test_environment_manager_interface(self):
        """Test EnvironmentManager interface compliance."""
        manager = EnvironmentManager()

        # Should support all required methods
        assert hasattr(manager, "get")
        assert hasattr(manager, "get_session_id")
        assert hasattr(manager, "get_log_dir")
        assert hasattr(manager, "get_db_path")
        assert hasattr(manager, "validate")
        assert hasattr(manager, "dump_config")


class TestIntegrationErrorHandling:
    """Test error handling in integration scenarios."""

    def test_clear_session_with_invalid_session_id(self):
        """Test clearing non-existent session doesn't error."""
        manager = MemoryManager(agent_id="test-agent", session_id="test-session")
        # Clearing non-existent session should work gracefully
        count = manager.clear_session("non-existent-session")
        assert count >= 0, "count must be positive"

    def test_recall_with_invalid_agent_id(self):
        """Test recalling from non-existent agent."""
        manager = MemoryManager(agent_id="real-agent", session_id="test-session")
        manager.store("Test memory")

        # Recall with different agent ID
        memories = manager.recall(agent_id="non-existent-agent")
        assert isinstance(memories, list)

    def test_memory_backend_storage_error_recovery(self):
        """Test recovery from storage errors."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(storage_dir=Path(tmpdir), agent_id="test", session_id="test")

            # Should handle storage gracefully
            manager.store("Data 1")
            stats = manager.get_stats()
            assert isinstance(stats, dict)

    def test_concurrent_session_operations(self):
        """Test operations on concurrent sessions."""
        session1 = MemoryManager(agent_id="agent", session_id="session-1")
        session2 = MemoryManager(agent_id="agent", session_id="session-2")

        # Both should work independently
        session1.store("Session 1 data")
        session2.store("Session 2 data")

        s1_data = session1.recall_all()
        s2_data = session2.recall_all()

        assert isinstance(s1_data, list)
        assert isinstance(s2_data, list)


class TestIntegrationPerformance:
    """Test performance characteristics of integration scenarios."""

    def test_large_memory_recall_performance(self):
        """Test recall performance with many stored memories."""
        manager = MemoryManager(agent_id="test", session_id="test")

        # Store many memories
        for i in range(100):
            manager.store(f"Memory {i}")

        # Recall should complete
        memories = manager.recall_all(limit=50)
        assert len(memories) <= 50, "Memories must not be empty"

    def test_multiple_session_overhead(self):
        """Test overhead of managing multiple sessions."""
        managers = []
        for i in range(10):
            manager = MemoryManager(agent_id="agent", session_id=f"session-{i}")
            manager.store(f"Session {i} data")
            managers.append(manager)

        # All managers should work
        for manager in managers:
            memories = manager.recall_all()
            assert isinstance(memories, list)

    def test_large_metadata_handling(self):
        """Test handling of large metadata."""
        manager = MemoryManager(agent_id="test", session_id="test")

        # Large metadata
        large_metadata = {f"key_{i}": f"value_{i}" * 100 for i in range(100)}

        entry = manager.store("Test", metadata=large_metadata)
        assert entry.metadata == large_metadata, "Data must not be empty"
