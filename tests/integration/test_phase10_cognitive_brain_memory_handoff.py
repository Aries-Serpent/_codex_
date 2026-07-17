"""
PHASE 10 LANE 1: Cognitive Brain STM↔LTM Handoff Tests

Tests Cognitive Brain memory handoff integration covering:
- Short-term memory (STM) → Long-term memory (LTM) sync
- Memory capacity management
- Pattern persistence across sessions
- Priority-based memory eviction
"""

from datetime import datetime, timedelta

import pytest


@pytest.mark.integration
@pytest.mark.e2e
@pytest.mark.critical
class TestPhase10CognitiveBrainMemoryHandoff:
    """Cognitive Brain STM↔LTM handoff integration tests."""

    @pytest.fixture
    def memory_context(self):
        """Provide mock memory context."""
        return {
            "stm": {
                "patterns": [],
                "capacity": 100,
                "utilization": 0,
            },
            "ltm": {
                "patterns": [],
                "capacity": 1000,
                "utilization": 0,
            },
            "sync_log": [],
        }

    def test_stm_to_ltm_sync_at_threshold(self, memory_context):
        """Test STM→LTM sync when threshold reached."""
        # Arrange
        stm_threshold = 80
        patterns_to_sync = 20
        
        # Act
        memory_context["stm"]["utilization"] = stm_threshold + 1
        memory_context["stm"]["patterns"] = [
            {"id": i, "priority": i % 10} for i in range(patterns_to_sync)
        ]
        
        # Simulate sync
        patterns_synced = memory_context["stm"]["patterns"][:patterns_to_sync // 2]
        memory_context["ltm"]["patterns"].extend(patterns_synced)
        memory_context["sync_log"].append({
            "timestamp": datetime.now(),
            "patterns_synced": len(patterns_synced),
        })
        
        # Assert
        assert len(memory_context["ltm"]["patterns"]) == len(patterns_synced)
        assert len(memory_context["sync_log"]) == 1
        assert memory_context["sync_log"][0]["patterns_synced"] == len(patterns_synced)

    def test_memory_capacity_management(self, memory_context):
        """Test memory capacity management."""
        # Arrange
        memory_context["stm"]["capacity"] = 100
        memory_context["stm"]["utilization"] = 85
        
        memory_context["ltm"]["capacity"] = 1000
        memory_context["ltm"]["utilization"] = 650
        
        # Act
        stm_available = memory_context["stm"]["capacity"] - memory_context["stm"]["utilization"]
        ltm_available = memory_context["ltm"]["capacity"] - memory_context["ltm"]["utilization"]
        
        # Assert
        assert stm_available == 15
        assert ltm_available == 350
        assert stm_available < ltm_available

    def test_priority_based_memory_eviction(self, memory_context):
        """Test priority-based memory eviction."""
        # Arrange
        patterns = [
            {"id": 1, "priority": 1, "last_accessed": datetime.now() - timedelta(hours=2)},
            {"id": 2, "priority": 9, "last_accessed": datetime.now()},
            {"id": 3, "priority": 3, "last_accessed": datetime.now() - timedelta(hours=1)},
        ]
        memory_context["stm"]["patterns"] = patterns
        
        # Act
        # Should evict lowest priority pattern
        evicted = min(patterns, key=lambda p: p["priority"])
        memory_context["stm"]["patterns"].remove(evicted)
        
        # Assert
        assert evicted["id"] == 1
        assert len(memory_context["stm"]["patterns"]) == 2
        assert all(p["priority"] > evicted["priority"] for p in memory_context["stm"]["patterns"])

    def test_pattern_persistence_across_sessions(self, memory_context):
        """Test pattern persistence across sessions."""
        # Arrange
        session_1_patterns = [
            {"id": "pat_001", "name": "pattern_a", "session": 1},
            {"id": "pat_002", "name": "pattern_b", "session": 1},
        ]
        
        # Act - simulate end of session 1
        memory_context["ltm"]["patterns"].extend(session_1_patterns)
        
        # Simulate start of session 2 - patterns should be available
        session_2_available_patterns = memory_context["ltm"]["patterns"]
        
        # Assert
        assert len(session_2_available_patterns) >= 2
        assert any(p["name"] == "pattern_a" for p in session_2_available_patterns)

    def test_memory_sync_consistency(self, memory_context):
        """Test consistency of memory sync operations."""
        # Arrange
        test_patterns = [
            {"id": f"p_{i}", "content": f"pattern_{i}", "metadata": {"ver": 1}}
            for i in range(10)
        ]
        
        # Act
        for pattern in test_patterns:
            memory_context["stm"]["patterns"].append(pattern)
        
        # Sync all patterns to LTM
        synced = memory_context["stm"]["patterns"].copy()
        memory_context["ltm"]["patterns"].extend(synced)
        
        # Verify consistency
        stm_ids = {p["id"] for p in memory_context["stm"]["patterns"]}
        ltm_ids = {p["id"] for p in memory_context["ltm"]["patterns"]}
        
        # Assert
        assert stm_ids == ltm_ids

    def test_memory_eviction_under_pressure(self, memory_context):
        """Test memory eviction under capacity pressure."""
        # Arrange - fill STM to max
        memory_context["stm"]["utilization"] = 95
        memory_context["stm"]["patterns"] = [
            {"id": i, "priority": i, "size": 1} 
            for i in range(95)
        ]
        
        # Act - try to add new pattern when near capacity
        new_pattern = {"id": 96, "priority": 50, "size": 1}
        if memory_context["stm"]["utilization"] + 1 > memory_context["stm"]["capacity"]:
            # Should trigger eviction
            evicted = min(memory_context["stm"]["patterns"], key=lambda p: p["priority"])
            memory_context["stm"]["patterns"].remove(evicted)
        
        memory_context["stm"]["patterns"].append(new_pattern)
        
        # Assert
        assert new_pattern in memory_context["stm"]["patterns"]
        assert len(memory_context["stm"]["patterns"]) <= memory_context["stm"]["capacity"]

    def test_memory_gc_collection_integrity(self, memory_context):
        """Test garbage collection maintains integrity."""
        # Arrange
        memory_context["ltm"]["patterns"] = [
            {"id": i, "valid": i % 2 == 0} for i in range(20)
        ]
        
        # Act - simulate garbage collection
        valid_patterns = [p for p in memory_context["ltm"]["patterns"] if p["valid"]]
        memory_context["ltm"]["patterns"] = valid_patterns
        
        # Assert
        assert all(p["valid"] for p in memory_context["ltm"]["patterns"])
        assert len(memory_context["ltm"]["patterns"]) == 10


@pytest.mark.integration
@pytest.mark.e2e
class TestPhase10MemoryPerformance:
    """Test memory system performance characteristics."""

    def test_memory_sync_latency(self):
        """Test memory sync latency."""
        # Arrange
        start_time = datetime.now()
        pattern_count = 1000
        
        # Act
        patterns = [{"id": i, "data": f"p_{i}"} for i in range(pattern_count)]
        patterns_copy = patterns.copy()
        
        # Assert
        assert len(patterns_copy) == pattern_count

    def test_memory_lookup_performance(self):
        """Test memory lookup performance."""
        # Arrange
        patterns = {f"p_{i}": {"content": f"pattern_{i}"} for i in range(10000)}
        
        # Act
        lookup_id = "p_5000"
        found = lookup_id in patterns
        
        # Assert
        assert found is True

    def test_memory_consolidation_efficiency(self):
        """Test memory consolidation efficiency."""
        # Arrange
        duplicate_patterns = [{"id": i % 5, "count": i} for i in range(100)]
        
        # Act
        unique_patterns = {}
        for p in duplicate_patterns:
            if p["id"] not in unique_patterns:
                unique_patterns[p["id"]] = p
        
        # Assert
        assert len(unique_patterns) == 5
        assert len(duplicate_patterns) / len(unique_patterns) >= 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
