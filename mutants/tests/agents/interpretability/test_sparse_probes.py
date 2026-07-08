"""
Tests for agents.interpretability.sparse_probes module.

This module contains comprehensive tests for sparse linear probes used for
interpretability of agent state vectors.
"""


class TestSparseLinearProbe:
    """Tests for SparseLinearProbe class."""

    def test_default_values(self):
        """Test SparseLinearProbe default values."""
        from agents.interpretability.sparse_probes import SparseLinearProbe

        probe = SparseLinearProbe()

        assert probe.weights == [], "weights is not valid"
        assert probe.bias == [], "bias is not valid"
        assert probe.sparsity_threshold == 0.1, "sparsity_threshold is not valid"
        assert probe.concept_names == [], "concept_names is not valid"

    def test_from_dimensions_basic(self):
        """Test creating probe from dimensions."""
        from agents.interpretability.sparse_probes import SparseLinearProbe

        probe = SparseLinearProbe.from_dimensions(
            num_concepts=5, input_dim=10, sparsity_threshold=0.2, seed=42
        )

        assert len(probe.weights) == 5, "Collection must not be empty"
        assert len(probe.weights[0]) == 10, "Collection must not be empty"
        assert len(probe.bias) == 5, "Collection must not be empty"
        assert probe.sparsity_threshold == 0.2, "sparsity_threshold is not valid"
        assert len(probe.concept_names) == 5, "Collection must not be empty"

    def test_from_dimensions_determinism(self):
        """Test probe initialization is deterministic with same seed."""
        from agents.interpretability.sparse_probes import SparseLinearProbe

        probe1 = SparseLinearProbe.from_dimensions(num_concepts=3, input_dim=4, seed=123)

        probe2 = SparseLinearProbe.from_dimensions(num_concepts=3, input_dim=4, seed=123)

        assert probe1.weights == probe2.weights, "weights is not valid"
        assert probe1.bias == probe2.bias, "bias is not valid"

    def test_from_dimensions_different_seeds(self):
        """Test different seeds produce different weights."""
        from agents.interpretability.sparse_probes import SparseLinearProbe

        probe1 = SparseLinearProbe.from_dimensions(num_concepts=3, input_dim=4, seed=1)

        probe2 = SparseLinearProbe.from_dimensions(num_concepts=3, input_dim=4, seed=2)

        assert probe1.weights != probe2.weights, "weights is not valid"

    def test_concept_names_generated(self):
        """Test concept names are auto-generated."""
        from agents.interpretability.sparse_probes import SparseLinearProbe

        probe = SparseLinearProbe.from_dimensions(num_concepts=3, input_dim=4)

        assert probe.concept_names == ["concept_0", "concept_1", "concept_2"]

    def test_weights_are_small_initialization(self):
        """Test weights are initialized with small values."""
        from agents.interpretability.sparse_probes import SparseLinearProbe

        probe = SparseLinearProbe.from_dimensions(num_concepts=5, input_dim=10, seed=42)

        # Weights should be initialized with std ~ 0.1
        for row in probe.weights:
            for val in row:
                # Values should generally be small (within 3 std devs of 0)
                assert abs(val) < 1.0, "Condition must be true"

    def test_bias_are_small_initialization(self):
        """Test biases are initialized with small values."""
        from agents.interpretability.sparse_probes import SparseLinearProbe

        probe = SparseLinearProbe.from_dimensions(num_concepts=5, input_dim=10, seed=42)

        # Bias should be initialized with std ~ 0.01
        for val in probe.bias:
            assert abs(val) < 0.5, "Condition must be true"


class TestModuleLevelFlags:
    """Tests for module-level flags and imports."""

    def test_numpy_available_flag(self):
        """Test NUMPY_AVAILABLE flag exists."""
        from agents.interpretability import sparse_probes

        assert hasattr(sparse_probes, "NUMPY_AVAILABLE")
        assert isinstance(sparse_probes.NUMPY_AVAILABLE, bool)

    def test_logger_exists(self):
        """Test logger is configured."""
        from agents.interpretability.sparse_probes import logger

        assert logger is not None, "logger must be initialized"
        assert logger.name == "agents.interpretability.sparse_probes", "name is not valid"


class TestEdgeCases:
    """Tests for edge cases."""

    def test_single_concept_single_input(self):
        """Test probe with single concept and single input dimension."""
        from agents.interpretability.sparse_probes import SparseLinearProbe

        probe = SparseLinearProbe.from_dimensions(num_concepts=1, input_dim=1, seed=42)

        assert len(probe.weights) == 1, "Collection must not be empty"
        assert len(probe.weights[0]) == 1, "Collection must not be empty"
        assert len(probe.bias) == 1, "Collection must not be empty"

    def test_large_dimensions(self):
        """Test probe with larger dimensions."""
        from agents.interpretability.sparse_probes import SparseLinearProbe

        probe = SparseLinearProbe.from_dimensions(num_concepts=100, input_dim=50, seed=42)

        assert len(probe.weights) == 100, "Collection must not be empty"
        assert len(probe.weights[0]) == 50, "Collection must not be empty"
        assert len(probe.concept_names) == 100, "Collection must not be empty"

    def test_custom_sparsity_threshold(self):
        """Test probe with custom sparsity threshold."""
        from agents.interpretability.sparse_probes import SparseLinearProbe

        probe = SparseLinearProbe.from_dimensions(
            num_concepts=3, input_dim=4, sparsity_threshold=0.5, seed=42
        )

        assert probe.sparsity_threshold == 0.5, "sparsity_threshold is not valid"
