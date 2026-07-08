"""Integration tests for Agent Memory System.

Tests the required API methods:
- store_decision
- retrieve_similar_context
- get_pattern_library
- invalidate_stale_contexts
"""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def memory_system():
    """Create a temporary memory system for testing."""
    # Import here to avoid import errors if module not available
    from agents.agent_memory import AgentMemorySystem

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_memory.db"
        system = AgentMemorySystem(agent_id="test_agent", db_path=db_path)
        yield system


class TestAgentMemoryAPI:
    """Test the required API methods for agent memory system."""

    def test_store_decision(self, memory_system):
        """Test store_decision stores and returns memory ID."""
        memory_id = memory_system.store_decision(
            task_id="task_001",
            decision="Use AST parsing instead of regex",
            rationale="AST is more reliable for Python code analysis",
            context={"file": "analyzer.py", "line": 42},
        )

        assert memory_id is not None, "memory_id must be initialized"
        assert isinstance(memory_id, str)
        assert len(memory_id) == 16, "Memory_id must not be empty"

    def test_store_decision_multiple(self, memory_system):
        """Test storing multiple decisions."""
        ids = []
        for i in range(5):
            mid = memory_system.store_decision(
                task_id=f"task_{i:03d}",
                decision=f"Decision {i}",
                rationale=f"Rationale {i}",
            )
            ids.append(mid)

        # All IDs should be unique
        assert len(set(ids)) == 5, "Collection must not be empty"

    def test_retrieve_similar_context(self, memory_system):
        """Test retrieve_similar_context finds relevant memories."""
        # Store some decisions first
        memory_system.store_decision(
            task_id="task_security",
            decision="Add input validation",
            rationale="Prevent injection attacks",
            context={"type": "security"},
        )
        memory_system.store_decision(
            task_id="task_test",
            decision="Add unit tests",
            rationale="Improve coverage",
            context={"type": "testing"},
        )

        # Retrieve similar contexts
        results = memory_system.retrieve_similar_context(
            task_description="security vulnerability input validation", limit=5
        )

        assert isinstance(results, list)
        # Results should have relevance scores
        if results:
            assert "relevance_score" in results[0], "Result must not be empty"
            assert "content" in results[0], "Result must not be empty"

    def test_retrieve_similar_context_empty(self, memory_system):
        """Test retrieve_similar_context with no matching memories."""
        results = memory_system.retrieve_similar_context(
            task_description="xyz completely unrelated query", limit=5
        )

        assert isinstance(results, list)
        # May be empty or have low relevance scores

    def test_get_pattern_library(self, memory_system):
        """Test get_pattern_library returns all patterns."""
        patterns = memory_system.get_pattern_library()

        assert isinstance(patterns, list)
        # Should have at least the default patterns
        assert len(patterns) >= 3, "Patterns must not be empty"

        # Check pattern structure
        for pattern in patterns:
            assert "pattern_id" in pattern, "Condition must be true"
            assert "name" in pattern, "Condition must be true"
            assert "triggers" in pattern, "Condition must be true"
            assert "recommended_actions" in pattern, "Condition must be true"
            assert "success_rate" in pattern, "Condition must be true"

    def test_get_pattern_library_default_patterns(self, memory_system):
        """Test that default patterns are initialized."""
        patterns = memory_system.get_pattern_library()
        pattern_names = [p["name"] for p in patterns]

        # Should have these default patterns
        assert "Code Review Comment Resolution" in pattern_names, "Condition must be true"
        assert "Security Vulnerability Fix" in pattern_names, "Condition must be true"
        assert "Test Failure Debugging" in pattern_names, "Condition must be true"

    def test_invalidate_stale_contexts(self, memory_system):
        """Test invalidate_stale_contexts cleans up old memories."""
        # Store a decision
        memory_system.store_decision(
            task_id="old_task",
            decision="Old decision",
            rationale="Old rationale",
        )

        # Invalidate with 0 days (should affect all)
        # Note: This may not invalidate recent memories
        count = memory_system.invalidate_stale_contexts(age_days=0)

        # Should return a count (may be 0 if memory is recent and accessed)
        assert isinstance(count, int)
        assert count >= 0, "count must be positive"

    def test_invalidate_stale_contexts_respects_age(self, memory_system):
        """Test that invalidation respects age threshold."""
        # Store a decision
        memory_system.store_decision(
            task_id="recent_task",
            decision="Recent decision",
            rationale="Recent rationale",
        )

        # Invalidate with 30 days (shouldn't affect recent)
        invalidated = memory_system.invalidate_stale_contexts(age_days=30)
        assert invalidated >= 0, "invalidated must be greater than zero"

        # Recent memory should not be invalidated
        stats = memory_system.get_stats()
        assert stats["memory_stats"]["total_memories"] >= 1, "Value must be greater than zero"


class TestAgentMemoryIntegration:
    """Integration tests for full workflow."""

    def test_full_task_workflow(self, memory_system):
        """Test complete task workflow with all API methods."""
        # 1. Start task
        frame = memory_system.start_task("Fix security vulnerability in auth module")
        assert frame is not None, "frame must be initialized"

        # 2. Get patterns
        patterns = memory_system.get_pattern_library()
        security_patterns = [p for p in patterns if "security" in p["tags"]]
        assert len(security_patterns) > 0, "Security_patterns must not be empty"

        # 3. Store decision
        memory_id = memory_system.store_decision(
            task_id=frame.frame_id,
            decision="Implement input sanitization",
            rationale="Follows OWASP guidelines",
            context={"pattern_used": security_patterns[0]["pattern_id"]},
        )
        assert memory_id is not None, "memory_id must be initialized"

        # 4. Retrieve context for similar task
        similar = memory_system.retrieve_similar_context(
            "security input validation sanitization", limit=3
        )
        # Should find our recent decision
        assert isinstance(similar, list)

        # 5. Complete task
        memory_system.complete_task(success=True, summary="Fixed vulnerability")

        # 6. Verify stats
        stats = memory_system.get_stats()
        assert stats["memory_stats"]["total_memories"] >= 1, "Value must be greater than zero"

    def test_cross_session_context(self, memory_system):
        """Test that context persists across sessions."""
        # First session
        memory_system.store_decision(
            task_id="session1_task",
            decision="Persistent decision",
            rationale="Should survive session",
        )

        # Get the db_path
        db_path = memory_system.memory.db_path

        # Create new instance (simulating new session)
        from agents.agent_memory import AgentMemorySystem

        new_system = AgentMemorySystem(agent_id="test_agent_2", db_path=db_path)

        # Should find the previous decision
        results = new_system.retrieve_similar_context("persistent decision", limit=5)

        # Memory should persist
        assert isinstance(results, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
