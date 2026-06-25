"""Tests for sparse probes and interpretability utilities."""

from __future__ import annotations

from agents.interpretability.sparse_probes import (
    SparseLinearProbe,
    UnembeddingHead,
    interpret_state_vector,
    top_k_labels,
)


class TestSparseLinearProbe:
    """Tests for SparseLinearProbe."""

    def test_sparse_probe_fixed_size_outputs(self):
        """Test deterministic output size."""
        probe = SparseLinearProbe.from_dimensions(num_concepts=3, input_dim=4)
        outputs = probe.transform([0.2, 0.1, 0.0, 0.5])
        assert len(outputs) == 3, "Output should have 3 concepts"

    def test_sparse_probe_sparsity_effect(self):
        """Test L1 sparsity increases zero ratio."""
        probe_sparse = SparseLinearProbe.from_dimensions(
            num_concepts=5, input_dim=4, sparsity_threshold=0.5
        )
        probe_dense = SparseLinearProbe.from_dimensions(
            num_concepts=5, input_dim=4, sparsity_threshold=0.0
        )

        test_vec = [0.1, 0.2, 0.3, 0.4]

        outputs_sparse = probe_sparse.transform(test_vec)
        outputs_dense = probe_dense.transform(test_vec)

        # Count zeros
        zeros_sparse = sum(1 for x in outputs_sparse if abs(x) < 1e-9)
        zeros_dense = sum(1 for x in outputs_dense if abs(x) < 1e-9)

        assert zeros_sparse >= zeros_dense, "Sparse probe should have more zeros"

    def test_sparse_probe_top_concepts(self):
        """Test top-k concept extraction."""
        probe = SparseLinearProbe.from_dimensions(num_concepts=5, input_dim=3)
        test_vec = [1.0, 0.5, 0.2]

        top_concepts = probe.top_concepts(test_vec, k=3)

        assert len(top_concepts) == 3, "Should return exactly 3 concepts"
        assert all(isinstance(name, str) for name, _ in top_concepts), "Names should be strings"
        assert all(isinstance(score, float) for _, score in top_concepts), "Scores should be floats"

        # Check ordering (by absolute value)
        scores = [abs(score) for _, score in top_concepts]
        assert scores == sorted(scores, reverse=True), "Should be sorted by magnitude"

    def test_sparse_probe_deterministic(self):
        """Test deterministic initialization."""
        probe1 = SparseLinearProbe.from_dimensions(num_concepts=3, input_dim=4, seed=42)
        probe2 = SparseLinearProbe.from_dimensions(num_concepts=3, input_dim=4, seed=42)

        test_vec = [0.5, 0.3, 0.1, 0.7]

        outputs1 = probe1.transform(test_vec)
        outputs2 = probe2.transform(test_vec)

        assert outputs1 == outputs2, "Same seed should produce identical outputs"

    def test_sparse_probe_sparsity_ratio(self):
        """Test sparsity ratio calculation."""
        probe = SparseLinearProbe.from_dimensions(num_concepts=3, input_dim=4)

        ratio = probe.sparsity_ratio()

        assert 0.0 <= ratio <= 1.0, "Sparsity ratio should be in [0, 1]"


class TestUnembeddingHead:
    """Tests for UnembeddingHead."""

    def test_unembedding_top_k_labels_ordering(self):
        """Test top-k label ordering correctness."""
        head = UnembeddingHead.from_dimensions(num_labels=5, input_dim=3)
        test_vec = [1.0, 0.5, 0.2]

        logits = head.project(test_vec)
        top_labels = top_k_labels(logits, head.label_names, k=3)

        assert len(top_labels) == 3, "Should return exactly 3 labels"

        # Check ordering (descending by logit)
        logit_values = [logit for _, logit in top_labels]
        assert logit_values == sorted(logit_values, reverse=True), "Should be sorted descending"

    def test_unembedding_deterministic(self):
        """Test deterministic projection."""
        head1 = UnembeddingHead.from_dimensions(num_labels=4, input_dim=3, seed=42)
        head2 = UnembeddingHead.from_dimensions(num_labels=4, input_dim=3, seed=42)

        test_vec = [0.7, 0.3, 0.1]

        logits1 = head1.project(test_vec)
        logits2 = head2.project(test_vec)

        assert logits1 == logits2, "Same seed should produce identical logits"

    def test_unembedding_output_size(self):
        """Test output dimension matches num_labels."""
        head = UnembeddingHead.from_dimensions(num_labels=10, input_dim=5)
        test_vec = [0.1] * 5

        logits = head.project(test_vec)

        assert len(logits) == 10, "Output should have 10 logits"


class TestInterpretStateVector:
    """Tests for interpret_state_vector orchestrator."""

    def test_interpret_with_probe_only(self):
        """Test interpretation with probe only."""
        probe = SparseLinearProbe.from_dimensions(num_concepts=3, input_dim=4)
        test_vec = [0.5, 0.3, 0.1, 0.7]

        result = interpret_state_vector(test_vec, probe=probe, top_k=2)

        assert "concepts" in result, "Should have concepts key"
        assert "labels" in result, "Should have labels key"
        assert "confidence" in result, "Should have confidence key"

        assert len(result["concepts"]) == 2, "Should have 2 top concepts"
        assert len(result["labels"]) == 0, "Should have no labels (no unembedding)"
        assert result["confidence"] >= 0.0, "Confidence should be non-negative"

    def test_interpret_with_unembedding_only(self):
        """Test interpretation with unembedding only."""
        head = UnembeddingHead.from_dimensions(num_labels=5, input_dim=4)
        test_vec = [0.5, 0.3, 0.1, 0.7]

        result = interpret_state_vector(test_vec, unembedding=head, top_k=3)

        assert len(result["concepts"]) == 0, "Should have no concepts (no probe)"
        assert len(result["labels"]) == 3, "Should have 3 top labels"
        assert 0.0 <= result["confidence"] <= 1.0, "Confidence should be in [0, 1]"

    def test_interpret_with_both(self):
        """Test interpretation with both probe and unembedding."""
        probe = SparseLinearProbe.from_dimensions(num_concepts=4, input_dim=5)
        head = UnembeddingHead.from_dimensions(num_labels=6, input_dim=5)
        test_vec = [0.8, 0.4, 0.2, 0.1, 0.05]

        result = interpret_state_vector(test_vec, probe=probe, unembedding=head, top_k=3)

        assert len(result["concepts"]) == 3, "Should have 3 top concepts"
        assert len(result["labels"]) == 3, "Should have 3 top labels"
        assert result["confidence"] > 0.0, "Confidence should be positive"

    def test_interpret_empty_vector(self):
        """Test interpretation with zero vector."""
        probe = SparseLinearProbe.from_dimensions(num_concepts=3, input_dim=4)
        test_vec = [0.0, 0.0, 0.0, 0.0]

        result = interpret_state_vector(test_vec, probe=probe, top_k=2)

        assert "concepts" in result, "Should handle zero vector gracefully"
        assert len(result["concepts"]) == 2, "Should still return top-k concepts"


class TestTopKLabels:
    """Tests for top_k_labels utility."""

    def test_top_k_labels_ordering(self):
        """Test correct ordering."""
        logits = [0.5, 1.2, 0.3, 2.0, 0.8]
        names = ["a", "b", "c", "d", "e"]

        top_3 = top_k_labels(logits, names, k=3)

        assert len(top_3) == 3, "Should return 3 labels"
        assert top_3[0][0] == "d", "Highest logit should be first"
        assert top_3[1][0] == "b", "Second highest should be second"
        assert top_3[2][0] == "e", "Third highest should be third"

    def test_top_k_labels_k_larger_than_size(self):
        """Test when k > number of labels."""
        logits = [0.5, 1.2]
        names = ["a", "b"]

        top_5 = top_k_labels(logits, names, k=5)

        assert len(top_5) == 2, "Should return all available labels"
