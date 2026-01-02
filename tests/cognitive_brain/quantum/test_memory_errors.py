"""
Phase 8.1 Error Handling Tests - QuantumMemoryManager, PatternCompressor, Memory Integration.

Tests error conditions, edge cases, and robustness of memory management components.
"""

import pytest
import numpy as np
from cognitive_brain.quantum.memory import QuantumMemoryManager, MemoryPattern
from cognitive_brain.quantum.compression import PatternCompressor
from cognitive_brain.integrations.memory_integration import MemoryAugmentedComplianceAssessor


class TestQuantumMemoryManagerErrors:
    """Error handling tests for QuantumMemoryManager."""

    def test_invalid_pattern_none_id(self):
        """Test error when storing pattern with None ID."""
        _manager = QuantumMemoryManager(stm_capacity=100, ltm_capacity=1000)  # Copilot: Context setup
        
        with pytest.raises(ValueError, match="pattern_id cannot be None"):
            _pattern = MemoryPattern(  # Copilot: Exception expected before use
                pattern_id=None,
                features={"f1": 0.5},
                decision="approve",
                confidence=0.8
            )

    def test_invalid_pattern_empty_id(self):
        """Test error when storing pattern with empty string ID."""
        _manager = QuantumMemoryManager(stm_capacity=100, ltm_capacity=1000)  # Copilot: Context setup
        
        with pytest.raises(ValueError, match="pattern_id cannot be empty"):
            _pattern = MemoryPattern(  # Copilot: Exception expected before use
                pattern_id="",
                features={"f1": 0.5},
                decision="approve",
                confidence=0.8
            )

    def test_stm_capacity_overflow(self):
        """Test behavior when STM exceeds capacity."""
        manager = QuantumMemoryManager(stm_capacity=5, ltm_capacity=100)
        
        # Fill STM beyond capacity
        for i in range(10):
            pattern = MemoryPattern(
                pattern_id=f"pat_{i}",
                features={"f1": float(i)},
                decision="approve",
                confidence=0.8
            )
            manager.store_pattern(pattern)
        
        # STM should not exceed capacity (oldest evicted or consolidated)
        assert len(manager.short_term_memory) <= 5

    def test_ltm_capacity_overflow(self):
        """Test behavior when LTM exceeds capacity."""
        manager = QuantumMemoryManager(stm_capacity=10, ltm_capacity=20)
        
        # Fill LTM beyond capacity
        for i in range(30):
            pattern = MemoryPattern(
                pattern_id=f"pat_{i}",
                features={"f1": float(i)},
                decision="approve",
                confidence=0.9  # High confidence for LTM
            )
            manager.store_pattern(pattern)
            if i % 5 == 0:
                manager.consolidate()
        
        # LTM should not exceed capacity
        assert len(manager.long_term_memory) <= 20

    def test_retrieve_from_empty_memory(self):
        """Test retrieval when memory is empty."""
        manager = QuantumMemoryManager(stm_capacity=100, ltm_capacity=1000)
        
        query_features = {"f1": 0.5, "f2": 0.3}
        results = manager.retrieve_similar(query_features, k=5)
        
        # Should return empty list, not crash
        assert results == []

    def test_memory_guided_decision_no_match(self):
        """Test memory-guided decision when no patterns match."""
        manager = QuantumMemoryManager(stm_capacity=100, ltm_capacity=1000)
        
        # Store one pattern
        pattern = MemoryPattern(
            pattern_id="pat_1",
            features={"f1": 0.1, "f2": 0.1},
            decision="approve",
            confidence=0.8
        )
        manager.store_pattern(pattern)
        
        # Query with very different features
        query_features = {"f1": 0.9, "f2": 0.9}
        decision = manager.memory_guided_decision(query_features, confidence_threshold=0.99)
        
        # Should return None (no confident match)
        assert decision is None


class TestPatternCompressorErrors:
    """Error handling tests for PatternCompressor."""

    def test_compress_before_fit(self):
        """Test error when compressing before fitting."""
        compressor = PatternCompressor(n_components=2)
        
        with pytest.raises(ValueError, match="Compressor not fitted"):
            compressor.compress({"f1": 0.5, "f2": 0.3})

    def test_fit_empty_patterns(self):
        """Test error when fitting on empty pattern list."""
        compressor = PatternCompressor(n_components=2)
        
        with pytest.raises(ValueError, match="Cannot fit on empty pattern list"):
            compressor.fit([])

    def test_fit_mismatched_feature_keys(self):
        """Test error when patterns have different feature sets."""
        compressor = PatternCompressor(n_components=2)
        
        patterns = [
            {"f1": 0.5, "f2": 0.3},
            {"f1": 0.6, "f3": 0.4}  # Different keys
        ]
        
        with pytest.raises(ValueError, match="same feature keys"):
            compressor.fit(patterns)

    def test_compress_dimension_mismatch(self):
        """Test error when compressing pattern with wrong dimensions."""
        compressor = PatternCompressor(n_components=2)
        compressor.fit([
            {"f1": 0.5, "f2": 0.3},
            {"f1": 0.6, "f2": 0.4}
        ])
        
        # Try to compress pattern with different features
        with pytest.raises(ValueError, match="Feature mismatch"):
            compressor.compress({"f1": 0.5, "f3": 0.7})

    def test_decompress_invalid_compressed_pattern(self):
        """Test error when decompressing invalid pattern."""
        compressor = PatternCompressor(n_components=2)
        compressor.fit([
            {"f1": 0.5, "f2": 0.3},
            {"f1": 0.6, "f2": 0.4}
        ])
        
        # Create invalid compressed pattern (wrong dimensions)
        from cognitive_brain.quantum.compression import CompressedPattern
        invalid = CompressedPattern(
            compressed_features=np.array([0.1]),  # Wrong size
            metadata={}
        )
        
        with pytest.raises((ValueError, IndexError)):
            compressor.decompress(invalid)

    def test_n_components_exceeds_features(self):
        """Test when n_components > number of features."""
        compressor = PatternCompressor(n_components=10)  # More than features
        
        patterns = [
            {"f1": 0.5, "f2": 0.3},  # Only 2 features
            {"f1": 0.6, "f2": 0.4}
        ]
        
        # Should handle gracefully (use min of n_components and n_features)
        compressor.fit(patterns)
        compressed = compressor.compress({"f1": 0.5, "f2": 0.3})
        assert len(compressed.compressed_features) <= 2


class TestMemoryIntegrationErrors:
    """Error handling tests for MemoryAugmentedComplianceAssessor."""

    def test_assess_with_memory_no_compressor(self):
        """Test error when compressor is not set."""
        assessor = MemoryAugmentedComplianceAssessor()
        assessor.compressor = None  # Force no compressor
        
        from cognitive_brain.experiments.complex_scenarios import generate_complex_scenarios
        scenarios = generate_complex_scenarios(1, seed=42)
        
        # Should handle missing compressor gracefully or raise error
        try:
            result = assessor.assess_with_memory(scenarios[0])
            assert result is not None
        except AttributeError:
            # Expected if compressor is required
            pass

    def test_consolidation_failure_recovery(self):
        """Test recovery from consolidation failures."""
        assessor = MemoryAugmentedComplianceAssessor()
        
        # Force an error during consolidation by corrupting memory
        assessor.memory_manager.short_term_memory.append("invalid_pattern")
        
        # Should handle error gracefully
        try:
            assessor.memory_manager.consolidate()
        except (TypeError, AttributeError):
            # Expected error, should not crash entire system
            pass
        
        # System should still be usable
        assert assessor.memory_manager is not None


class TestCachePruningEdgeCases:
    """Edge case tests for cache pruning."""

    def test_prune_empty_cache(self):
        """Test pruning when cache is empty."""
        manager = QuantumMemoryManager(stm_capacity=100, ltm_capacity=1000)
        
        # Prune empty cache
        result = manager.prune_by_age(max_age_days=30)
        
        assert result.patterns_removed == 0
        assert result.space_freed_bytes == 0

    def test_prune_all_patterns_old(self):
        """Test when all patterns exceed age threshold."""
        manager = QuantumMemoryManager(stm_capacity=100, ltm_capacity=1000)
        
        # Add patterns
        for i in range(10):
            pattern = MemoryPattern(
                pattern_id=f"pat_{i}",
                features={"f1": float(i)},
                decision="approve",
                confidence=0.8
            )
            manager.store_pattern(pattern)
        
        # Prune with very short threshold
        result = manager.prune_by_age(max_age_days=0.000001)  # ~0.1 seconds
        
        # Most or all patterns should be removed
        assert result.patterns_removed > 0

    def test_prune_by_access_empty_ltm(self):
        """Test LRU pruning when LTM is empty."""
        manager = QuantumMemoryManager(stm_capacity=100, ltm_capacity=1000)
        
        result = manager.prune_by_access(keep_top_n=10)
        
        assert result.patterns_removed == 0


class TestDecompressionBackwardCompatibility:
    """Tests for backward compatibility in decompression."""

    def test_decompress_old_format_without_variable_bits(self):
        """Test decompressing patterns from old format."""
        compressor = PatternCompressor(n_components=2)
        compressor.fit([
            {"f1": 0.5, "f2": 0.3, "f3": 0.7},
            {"f1": 0.6, "f2": 0.4, "f3": 0.8}
        ])
        
        # Create old-style compressed pattern (no variable_bits in metadata)
        from cognitive_brain.quantum.compression import CompressedPattern
        old_pattern = CompressedPattern(
            compressed_features=np.array([0.1, 0.2]),
            metadata={"original_size": 3}  # No variable_bits
        )
        
        # Should decompress with fallback to uniform quantization
        decompressed = compressor.decompress(old_pattern)
        assert isinstance(decompressed, dict)
        assert len(decompressed) > 0

    def test_decompress_missing_metadata(self):
        """Test decompression with missing metadata fields."""
        compressor = PatternCompressor(n_components=2)
        compressor.fit([
            {"f1": 0.5, "f2": 0.3},
            {"f1": 0.6, "f2": 0.4}
        ])
        
        from cognitive_brain.quantum.compression import CompressedPattern
        pattern = CompressedPattern(
            compressed_features=np.array([0.1, 0.2]),
            metadata={}  # Empty metadata
        )
        
        # Should use defaults and decompress
        decompressed = compressor.decompress(pattern)
        assert isinstance(decompressed, dict)
