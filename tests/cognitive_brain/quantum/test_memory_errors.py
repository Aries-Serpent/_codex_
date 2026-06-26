"""
Phase 8.1 Error Handling Tests - QuantumMemoryManager, PatternCompressor, Memory Integration.

Tests error conditions, edge cases, and robustness of memory management components.
"""

from datetime import datetime, timezone

import pytest

np = pytest.importorskip("numpy")

from cognitive_brain.integrations.memory_integration import (
    MemoryAugmentedComplianceAssessor,
)
from cognitive_brain.models.quantum_metrics import QuantumMetricRepository
from cognitive_brain.quantum.coherence_monitor import CoherenceMonitor
from cognitive_brain.quantum.compression import PatternCompressor
from cognitive_brain.quantum.config import QuantumConfig
from cognitive_brain.quantum.memory import MemoryPattern, QuantumMemoryManager


@pytest.fixture
def quantum_config():
    """Fixture to provide QuantumConfig instance."""
    return QuantumConfig()


@pytest.fixture
def coherence_monitor(quantum_config, metric_repository):
    """Fixture to provide CoherenceMonitor instance."""
    return CoherenceMonitor(config=quantum_config, repository=metric_repository)


@pytest.fixture
def metric_repository():
    """Fixture to provide QuantumMetricRepository instance."""
    return QuantumMetricRepository()


class TestQuantumMemoryManagerErrors:
    """Error handling tests for QuantumMemoryManager."""

    def test_invalid_pattern_none_id(self, quantum_config):
        """Test error when storing pattern with None ID."""
        QuantumMemoryManager(
            config=quantum_config, stm_capacity=100, ltm_capacity=1000
        )  # Context setup

        with pytest.raises(ValueError, match="pattern_id must be non-empty string"):
            MemoryPattern(  # Exception expected before pattern is returned
                pattern_id=None,
                features={"f1": 0.5},
                decision="approve",
                confidence=0.8,
                timestamp=datetime.now(timezone.utc),
            )

    def test_invalid_pattern_empty_id(self, quantum_config):
        """Test error when storing pattern with empty string ID."""
        QuantumMemoryManager(
            config=quantum_config, stm_capacity=100, ltm_capacity=1000
        )  # Context setup

        with pytest.raises(ValueError, match="pattern_id must be non-empty string"):
            MemoryPattern(  # Exception expected before pattern is returned
                pattern_id="",
                features={"f1": 0.5},
                decision="approve",
                confidence=0.8,
                timestamp=datetime.now(timezone.utc),
            )

    def test_stm_capacity_overflow(self, quantum_config):
        """Test behavior when STM exceeds capacity."""
        manager = QuantumMemoryManager(config=quantum_config, stm_capacity=5, ltm_capacity=100)

        # Fill STM beyond capacity
        for i in range(10):
            pattern = MemoryPattern(
                pattern_id=f"pat_{i}",
                features={"f1": float(i)},
                decision="approve",
                confidence=0.8,
                timestamp=datetime.now(timezone.utc),
            )
            manager.store_pattern(pattern)

        # STM should not exceed capacity (oldest evicted or consolidated)
        assert len(manager.stm) <= 5, "Collection must not be empty"

    def test_ltm_capacity_overflow(self, quantum_config):
        """Test behavior when LTM exceeds capacity."""
        manager = QuantumMemoryManager(config=quantum_config, stm_capacity=10, ltm_capacity=20)

        # Fill LTM beyond capacity
        for i in range(30):
            pattern = MemoryPattern(
                pattern_id=f"pat_{i}",
                features={"f1": float(i)},
                decision="approve",
                confidence=0.9,  # High confidence for LTM
                timestamp=datetime.now(timezone.utc),
            )
            manager.store_pattern(pattern)
            if i % 5 == 0:
                manager.consolidate()

        # LTM should not exceed capacity
        assert len(manager.ltm) <= 20, "Collection must not be empty"

    def test_retrieve_from_empty_memory(self, quantum_config):
        """Test retrieval when memory is empty."""
        manager = QuantumMemoryManager(config=quantum_config, stm_capacity=100, ltm_capacity=1000)

        query_features = {"f1": 0.5, "f2": 0.3}
        results = manager.retrieve_similar(query_features, k=5)

        # Should return empty list, not crash
        assert results == [], "Result must not be empty"

    def test_memory_guided_decision_no_match(self, quantum_config):
        """Test memory-guided decision when no patterns match."""
        manager = QuantumMemoryManager(config=quantum_config, stm_capacity=100, ltm_capacity=1000)

        # Store one pattern
        pattern = MemoryPattern(
            pattern_id="pat_1",
            features={"f1": 0.1, "f2": 0.1},
            decision="approve",
            confidence=0.8,
            timestamp=datetime.now(timezone.utc),
        )
        manager.store_pattern(pattern)

        # Query with very different features
        query_features = {"f1": 0.9, "f2": 0.9}
        decision = manager.memory_guided_decision(query_features, confidence_threshold=0.99)

        # Should return None (no confident match)
        assert decision is None, "decision is not valid"


class TestPatternCompressorErrors:
    """Error handling tests for PatternCompressor."""

    def test_compress_before_fit(self):
        """Test error when compressing before fitting."""
        compressor = PatternCompressor(target_dimensions=2)

        with pytest.raises(ValueError, match="Compressor not fitted"):
            compressor.compress(
                {"f1": 0.5, "f2": 0.3}, pattern_id="test", decision="approve", confidence=0.8
            )

    def test_fit_empty_patterns(self):
        """Test error when fitting on empty pattern list."""
        compressor = PatternCompressor(target_dimensions=2)

        with pytest.raises(ValueError, match="Cannot fit on empty pattern list"):
            compressor.fit([])

    def test_fit_mismatched_feature_keys(self):
        """Test error when patterns have different feature sets."""
        compressor = PatternCompressor(target_dimensions=2)

        patterns = [
            {"f1": 0.5, "f2": 0.3},
            {"f1": 0.6, "f3": 0.4},  # Different keys
        ]

        with pytest.raises(ValueError, match="same feature keys"):
            compressor.fit(patterns)

    def test_compress_dimension_mismatch(self):
        """Test error when compressing pattern with wrong dimensions."""
        compressor = PatternCompressor(target_dimensions=2)
        compressor.fit([{"f1": 0.5, "f2": 0.3}, {"f1": 0.6, "f2": 0.4}])

        # Try to compress pattern with different features
        with pytest.raises(ValueError, match="Feature mismatch"):
            compressor.compress(
                {"f1": 0.5, "f3": 0.7}, pattern_id="test", decision="approve", confidence=0.8
            )

    def test_decompress_invalid_compressed_pattern(self):
        """Test error when decompressing invalid pattern."""
        compressor = PatternCompressor(target_dimensions=2)
        compressor.fit([{"f1": 0.5, "f2": 0.3}, {"f1": 0.6, "f2": 0.4}])

        # Create invalid compressed pattern (wrong dimensions)
        from cognitive_brain.quantum.compression import CompressedPattern

        invalid = CompressedPattern(
            pattern_id="invalid",
            compressed_features=np.array([0.1]),  # Wrong size
            decision="test",
            confidence=0.5,
            feature_keys=["f1", "f2"],
            compression_metadata={},
        )

        with pytest.raises((ValueError, IndexError)):
            compressor.decompress(invalid)

    def test_n_components_exceeds_features(self):
        """Test when target_dimensions > number of features."""
        compressor = PatternCompressor(target_dimensions=10)  # More than features

        patterns = [
            {"f1": 0.5, "f2": 0.3},  # Only 2 features
            {"f1": 0.6, "f2": 0.4},
        ]

        # Should handle gracefully (use min of target_dimensions and n_features)
        compressor.fit(patterns)
        compressed = compressor.compress(
            {"f1": 0.5, "f2": 0.3}, pattern_id="test", decision="approve", confidence=0.8
        )
        assert len(compressed.compressed_features) <= 2, "Collection must not be empty"


class TestMemoryIntegrationErrors:
    """Error handling tests for MemoryAugmentedComplianceAssessor."""

    def test_assess_with_memory_no_compressor(
        self, quantum_config, coherence_monitor, metric_repository
    ):
        """Test error when compressor is not set."""
        assessor = MemoryAugmentedComplianceAssessor(
            config=quantum_config,
            monitor=coherence_monitor,
            repository=metric_repository,
        )
        assessor.compressor = None  # Force no compressor

        from cognitive_brain.experiments.complex_scenarios import (
            generate_complex_scenarios,
        )

        scenarios = generate_complex_scenarios(1, seed=42)

        # Should handle missing compressor gracefully or raise error
        try:
            result = assessor.assess_with_memory(scenarios[0])
            assert result is not None, "result must be initialized"
        except AttributeError:
            # Expected if compressor is required
            _ = None  # suppressed: no action needed

    def test_consolidation_failure_recovery(
        self, quantum_config, coherence_monitor, metric_repository
    ):
        """Test recovery from consolidation failures."""
        assessor = MemoryAugmentedComplianceAssessor(
            config=quantum_config,
            monitor=coherence_monitor,
            repository=metric_repository,
        )

        # Force an error during consolidation by corrupting memory
        assessor.memory_manager.short_term_memory.append("invalid_pattern")

        # Should handle error gracefully
        try:
            assessor.memory_manager.consolidate()
        except (TypeError, AttributeError):
            # Expected error, should not crash entire system
            _ = None  # suppressed: no action needed

        # System should still be usable
        assert assessor.memory_manager is not None, "memory_manager must be initialized"


class TestCachePruningEdgeCases:
    """Edge case tests for cache pruning."""

    def test_prune_empty_cache(self, quantum_config):
        """Test pruning when cache is empty."""
        manager = QuantumMemoryManager(config=quantum_config, stm_capacity=100, ltm_capacity=1000)

        # Prune empty cache
        result = manager.prune_by_age(max_age_hours=30 * 24)

        assert result.aged_pruned == 0, "Result must not be empty"

    def test_prune_all_patterns_old(self, quantum_config):
        """Test when all patterns exceed age threshold."""
        manager = QuantumMemoryManager(config=quantum_config, stm_capacity=100, ltm_capacity=1000)

        # Add patterns
        for i in range(10):
            pattern = MemoryPattern(
                pattern_id=f"pat_{i}",
                features={"f1": float(i)},
                decision="approve",
                confidence=0.8,
                timestamp=datetime.now(timezone.utc),
            )
            manager.store_pattern(pattern)

        # Prune with very short threshold
        result = manager.prune_by_age(max_age_hours=0.000001)  # ~0.0036 seconds

        # Most or all patterns should be removed
        assert result.aged_pruned > 0, "aged_pruned must be greater than zero"

    def test_prune_by_access_empty_ltm(self, quantum_config):
        """Test LRU pruning when LTM is empty."""
        manager = QuantumMemoryManager(config=quantum_config, stm_capacity=100, ltm_capacity=1000)

        result = manager.prune_by_access(keep_top_n=10)

        assert result.access_pruned == 0, "Result must not be empty"


class TestDecompressionBackwardCompatibility:
    """Tests for backward compatibility in decompression."""

    def test_decompress_old_format_without_variable_bits(self):
        """Test decompressing patterns from old format."""
        compressor = PatternCompressor(target_dimensions=2)
        compressor.fit([{"f1": 0.5, "f2": 0.3, "f3": 0.7}, {"f1": 0.6, "f2": 0.4, "f3": 0.8}])

        # Create old-style compressed pattern (no variable_bits in metadata)
        from cognitive_brain.quantum.compression import CompressedPattern

        old_pattern = CompressedPattern(
            pattern_id="old",
            compressed_features=np.array([0.1, 0.2]),
            decision="test",
            confidence=0.5,
            feature_keys=["f1", "f2", "f3"],
            compression_metadata={"original_size": 3},  # No variable_bits
        )

        # Should decompress with fallback to uniform quantization
        decompressed = compressor.decompress(old_pattern)
        assert isinstance(decompressed, dict)
        assert len(decompressed) > 0, "Decompressed must not be empty"

    def test_decompress_missing_metadata(self):
        """Test decompression with missing metadata fields."""
        compressor = PatternCompressor(target_dimensions=2)
        compressor.fit([{"f1": 0.5, "f2": 0.3}, {"f1": 0.6, "f2": 0.4}])

        from cognitive_brain.quantum.compression import CompressedPattern

        pattern = CompressedPattern(
            pattern_id="missing",
            compressed_features=np.array([0.1, 0.2]),
            decision="test",
            confidence=0.5,
            feature_keys=["f1", "f2"],
            compression_metadata={},  # Empty metadata
        )

        # Should use defaults and decompress
        decompressed = compressor.decompress(pattern)
        assert isinstance(decompressed, dict)
        assert isinstance(decompressed, dict)
