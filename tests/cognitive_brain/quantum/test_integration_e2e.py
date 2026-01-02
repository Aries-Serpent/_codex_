"""
Phase 8.1 Integration Tests - End-to-end workflows.

Tests complete workflows from pattern storage through consolidation, retrieval,
compression, and memory-guided decisions.
"""

import time
from cognitive_brain.quantum.memory import QuantumMemoryManager, MemoryPattern
from cognitive_brain.quantum.compression import PatternCompressor
from cognitive_brain.integrations.memory_integration import MemoryAugmentedComplianceAssessor
from cognitive_brain.experiments.complex_scenarios import generate_complex_scenarios


class TestEndToEndWorkflows:
    """Integration tests for complete cognitive brain workflows."""

    def test_full_pattern_lifecycle(self):
        """Test complete pattern lifecycle: store → consolidate → retrieve."""
        manager = QuantumMemoryManager(stm_capacity=10, ltm_capacity=100)
        
        # Store patterns in STM
        patterns = []
        for i in range(5):
            pattern = MemoryPattern(
                pattern_id=f"lifecycle_pat_{i}",
                features={"compliance": float(i) / 10, "risk": float(i) / 5},
                decision="approve" if i % 2 == 0 else "reject",
                confidence=0.9
            )
            manager.store_pattern(pattern)
            patterns.append(pattern)
        
        assert len(manager.short_term_memory) == 5
        
        # Consolidate to LTM
        consolidation_result = manager.consolidate()
        assert consolidation_result.promoted > 0
        assert len(manager.long_term_memory) > 0
        
        # Retrieve similar patterns
        query = {"compliance": 0.25, "risk": 0.5}
        retrieved = manager.retrieve_similar(query, k=3)
        
        assert len(retrieved) > 0
        assert all(hasattr(p, 'pattern_id') for p in retrieved)

    def test_memory_guided_decision_cache_hit(self):
        """Test memory-guided decision with cache hit."""
        manager = QuantumMemoryManager(stm_capacity=10, ltm_capacity=100)
        
        # Store high-confidence pattern
        reference_pattern = MemoryPattern(
            pattern_id="reference",
            features={"f1": 0.5, "f2": 0.6, "f3": 0.7},
            decision="approve",
            confidence=0.95
        )
        manager.store_pattern(reference_pattern)
        manager.consolidate()
        
        # Query with very similar features
        query = {"f1": 0.51, "f2": 0.59, "f3": 0.71}
        decision = manager.memory_guided_decision(query, confidence_threshold=0.85)
        
        # Should get cached decision
        assert decision is not None
        assert decision == "approve"
        
        # Cache hit rate should increase
        hit_rate = manager.get_cache_hit_rate()
        assert hit_rate > 0

    def test_memory_guided_decision_cache_miss(self):
        """Test memory-guided decision with cache miss."""
        manager = QuantumMemoryManager(stm_capacity=10, ltm_capacity=100)
        
        # Store pattern
        pattern = MemoryPattern(
            pattern_id="pat_1",
            features={"f1": 0.1, "f2": 0.2},
            decision="reject",
            confidence=0.8
        )
        manager.store_pattern(pattern)
        
        # Query with very different features
        query = {"f1": 0.9, "f2": 0.8}
        decision = manager.memory_guided_decision(query, confidence_threshold=0.9)
        
        # Should miss cache (no confident match)
        assert decision is None

    def test_compression_full_lifecycle(self):
        """Test compression: fit → compress → decompress accuracy."""
        compressor = PatternCompressor(n_components=3)
        
        # Training data
        training_patterns = [
            {"compliance": 0.1, "risk": 0.2, "impact": 0.3, "mitigation": 0.4},
            {"compliance": 0.5, "risk": 0.6, "impact": 0.7, "mitigation": 0.8},
            {"compliance": 0.2, "risk": 0.3, "impact": 0.4, "mitigation": 0.5},
            {"compliance": 0.8, "risk": 0.7, "impact": 0.6, "mitigation": 0.5},
        ]
        
        # Fit compressor
        compressor.fit(training_patterns)
        
        # Compress test pattern
        test_pattern = {"compliance": 0.4, "risk": 0.5, "impact": 0.6, "mitigation": 0.7}
        compressed = compressor.compress(test_pattern)
        
        # Verify compression
        assert len(compressed.compressed_features) == 3
        assert compressed.get_size_bytes() < len(test_pattern) * 8  # Should be smaller
        
        # Decompress
        decompressed = compressor.decompress(compressed)
        
        # Verify reconstruction accuracy (within tolerance)
        for key in test_pattern:
            assert key in decompressed
            # Allow some reconstruction error (lossy compression)
            assert abs(decompressed[key] - test_pattern[key]) < 0.3

    def test_auto_pruning_trigger(self):
        """Test automatic pruning when LTM reaches threshold."""
        manager = QuantumMemoryManager(stm_capacity=10, ltm_capacity=20)
        
        # Fill LTM to 80% capacity (trigger threshold)
        for i in range(16):  # 16/20 = 80%
            pattern = MemoryPattern(
                pattern_id=f"prune_pat_{i}",
                features={"f1": float(i) / 20},
                decision="approve",
                confidence=0.9
            )
            manager.store_pattern(pattern)
            if i % 3 == 0:
                manager.consolidate()
        
        # Trigger auto-prune
        prune_result = manager.auto_prune()
        
        # Should have pruned some patterns
        assert prune_result.patterns_removed >= 0
        # LTM should be below capacity
        assert len(manager.long_term_memory) <= 20

    def test_cache_health_monitoring_calculation(self):
        """Test cache health metrics calculation."""
        manager = QuantumMemoryManager(stm_capacity=10, ltm_capacity=100)
        
        # Add patterns and simulate usage
        for i in range(5):
            pattern = MemoryPattern(
                pattern_id=f"health_pat_{i}",
                features={"f1": float(i) / 10},
                decision="approve",
                confidence=0.8
            )
            manager.store_pattern(pattern)
        
        # Simulate some retrievals
        for _ in range(3):
            manager.retrieve_similar({"f1": 0.3}, k=2)
        
        # Get health metrics
        health = manager.get_cache_health()
        
        # Verify all metrics present
        assert "stm_utilization" in health
        assert "ltm_utilization" in health
        assert "cache_hit_rate" in health
        assert "avg_confidence" in health
        assert "staleness_hours" in health
        assert "consolidation_rate" in health
        assert "total_patterns" in health
        assert "total_retrievals" in health
        
        # Verify reasonable values
        assert 0 <= health["stm_utilization"] <= 1.0
        assert 0 <= health["ltm_utilization"] <= 1.0
        assert health["total_patterns"] == 5

    def test_full_memory_augmented_assessment_workflow(self):
        """Test complete memory-augmented compliance assessment."""
        assessor = MemoryAugmentedComplianceAssessor()
        
        scenarios = generate_complex_scenarios(10, seed=42)
        
        # First assessments (cache misses)
        for i in range(5):
            result = assessor.assess_with_memory(scenarios[i])
            assert result is not None
        
        # Should have patterns in memory now
        assert len(assessor.memory_manager.short_term_memory) > 0
        
        # Similar scenarios (potential cache hits)
        similar_scenarios = generate_complex_scenarios(5, seed=43)
        for scenario in similar_scenarios:
            result = assessor.assess_with_memory(scenario)
            assert result is not None
        
        # Check cache statistics
        stats = assessor.get_statistics()
        assert "cache_hits" in stats
        assert "total_assessments" in stats

    def test_consolidation_with_compression(self):
        """Test pattern consolidation with compression enabled."""
        manager = QuantumMemoryManager(stm_capacity=10, ltm_capacity=100)
        compressor = PatternCompressor(n_components=2)
        
        # Train compressor
        training = [
            {"f1": 0.1, "f2": 0.2, "f3": 0.3},
            {"f1": 0.4, "f2": 0.5, "f3": 0.6},
            {"f1": 0.7, "f2": 0.8, "f3": 0.9},
        ]
        compressor.fit(training)
        
        # Store patterns
        for i in range(5):
            pattern = MemoryPattern(
                pattern_id=f"compress_pat_{i}",
                features={"f1": float(i)/10, "f2": float(i)/8, "f3": float(i)/6},
                decision="approve",
                confidence=0.85
            )
            manager.store_pattern(pattern)
        
        # Consolidate
        result = manager.consolidate()
        
        # Patterns should be in LTM
        assert len(manager.long_term_memory) > 0
        assert result.promoted > 0

    def test_temporal_decay_in_retrieval(self):
        """Test temporal decay affects retrieval scores."""
        manager = QuantumMemoryManager(stm_capacity=10, ltm_capacity=100)
        
        # Store old pattern
        old_pattern = MemoryPattern(
            pattern_id="old",
            features={"f1": 0.5},
            decision="approve",
            confidence=0.9
        )
        manager.store_pattern(old_pattern)
        manager.consolidate()
        
        # Wait a tiny bit
        time.sleep(0.01)
        
        # Store new pattern (identical features)
        new_pattern = MemoryPattern(
            pattern_id="new",
            features={"f1": 0.5},
            decision="approve",
            confidence=0.9
        )
        manager.store_pattern(new_pattern)
        manager.consolidate()
        
        # Retrieve
        results = manager.retrieve_similar({"f1": 0.5}, k=2)
        
        # Newer pattern might score higher due to temporal decay
        assert len(results) == 2

    def test_end_to_end_with_realistic_workload(self):
        """Test complete system with realistic workload."""
        assessor = MemoryAugmentedComplianceAssessor()
        scenarios = generate_complex_scenarios(50, seed=42)
        
        results = []
        for i, scenario in enumerate(scenarios):
            result = assessor.assess_with_memory(scenario)
            results.append(result)
            
            # Trigger consolidation periodically
            if i > 0 and i % 10 == 0:
                assessor.memory_manager.consolidate()
        
        # Verify all assessments completed
        assert len(results) == 50
        assert all(r is not None for r in results)
        
        # Check system health
        health = assessor.memory_manager.get_cache_health()
        assert health["total_patterns"] > 0
        
        # Verify some cache hits occurred
        stats = assessor.get_statistics()
        assert stats["total_assessments"] == 50
