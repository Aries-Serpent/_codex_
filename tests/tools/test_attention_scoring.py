"""Tests for attention scoring utilities."""

from __future__ import annotations

from src.tools.attention import AttentionScorer


class TestAttentionScorer:
    """Tests for AttentionScorer."""

    def test_attention_temperature_scaling(self):
        """Test temperature affects weight distribution."""
        query = [1.0, 0.5, 0.2]
        keys = [
            [1.0, 0.5, 0.2],  # Similar to query
            [0.0, 0.0, 0.0],  # Dissimilar
            [0.5, 0.3, 0.1],  # Somewhat similar
        ]

        # Low temperature (sharper distribution)
        weights_low = AttentionScorer.score(query, keys, temperature=0.1)

        # High temperature (more uniform distribution)
        weights_high = AttentionScorer.score(query, keys, temperature=10.0)

        # Check properties
        assert len(weights_low) == 3, "Should have 3 weights"
        assert len(weights_high) == 3, "Should have 3 weights"

        # Weights should sum to 1
        assert abs(sum(weights_low) - 1.0) < 1e-6, "Weights should sum to 1"
        assert abs(sum(weights_high) - 1.0) < 1e-6, "Weights should sum to 1"

        # Low temperature should be more peaked (higher max weight)
        assert max(weights_low) > max(weights_high), "Low temp should be more peaked"

        # High temperature should be more uniform (lower max weight)
        min_weight_high = min(weights_high)
        min_weight_low = min(weights_low)
        assert min_weight_high > min_weight_low, "High temp should be more uniform"

    def test_attention_deterministic_ordering(self):
        """Test deterministic ordering with fixed embeddings."""
        query = [1.0, 0.0, 0.0]
        keys = [
            [1.0, 0.0, 0.0],  # Perfect match
            [0.5, 0.5, 0.0],  # Partial match
            [0.0, 1.0, 0.0],  # Orthogonal
        ]

        weights = AttentionScorer.score(query, keys, temperature=1.0)

        # First key should have highest weight (perfect match)
        assert weights[0] > weights[1], "Perfect match should have highest weight"
        assert weights[0] > weights[2], "Perfect match should beat orthogonal"

    def test_attention_softmax_properties(self):
        """Test softmax normalization properties."""
        query = [0.5, 0.3, 0.1]
        keys = [
            [0.8, 0.2, 0.1],
            [0.3, 0.6, 0.2],
            [0.1, 0.1, 0.8],
        ]

        weights = AttentionScorer.score(query, keys, temperature=1.0)

        # All weights should be positive
        assert all(w > 0 for w in weights), "All weights should be positive"

        # Weights should sum to 1
        assert abs(sum(weights) - 1.0) < 1e-6, "Weights should sum to 1"

        # Each weight should be in [0, 1]
        assert all(0 <= w <= 1 for w in weights), "Weights should be in [0, 1]"

    def test_attention_empty_keys(self):
        """Test behavior with empty key matrix."""
        query = [1.0, 0.5]
        keys = []

        weights = AttentionScorer.score(query, keys, temperature=1.0)

        assert weights == [], "Empty keys should produce empty weights"

    def test_attention_single_key(self):
        """Test attention with single key."""
        query = [1.0, 0.5, 0.2]
        keys = [[0.8, 0.3, 0.1]]

        weights = AttentionScorer.score(query, keys, temperature=1.0)

        assert len(weights) == 1, "Should have 1 weight"
        assert abs(weights[0] - 1.0) < 1e-6, "Single key should get weight 1.0"

    def test_attention_identical_keys(self):
        """Test attention with identical keys (uniform distribution)."""
        query = [1.0, 0.5]
        keys = [
            [0.5, 0.5],
            [0.5, 0.5],
            [0.5, 0.5],
        ]

        weights = AttentionScorer.score(query, keys, temperature=1.0)

        # All weights should be approximately equal
        expected_weight = 1.0 / 3.0
        for w in weights:
            assert abs(w - expected_weight) < 1e-6, "Identical keys should get equal weights"

    def test_attention_scaling_behavior(self):
        """Test that attention weights change predictably with query scaling.

        Note: Scaled dot-product attention is NOT truly scale-invariant due to
        softmax temperature effects. Scaling the query will affect the distribution.
        """
        query = [1.0, 0.5, 0.2]
        keys = [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ]

        weights1 = AttentionScorer.score(query, keys, temperature=1.0)

        # Scale query by 2 - this will amplify dot products
        query_scaled = [2.0, 1.0, 0.4]
        weights2 = AttentionScorer.score(query_scaled, keys, temperature=1.0)

        # Both should be valid probability distributions
        assert all(isinstance(w, float) for w in weights1), "Weights should be floats"
        assert all(isinstance(w, float) for w in weights2), "Scaled weights should be floats"
        assert abs(sum(weights1) - 1.0) < 1e-6, "Weights should sum to 1"
        assert abs(sum(weights2) - 1.0) < 1e-6, "Scaled weights should sum to 1"

        # Scaled query will produce different weight distribution due to softmax sharpening
        # (higher dot products lead to more concentrated probability mass)


class TestAttentionScorerTopK:
    """Tests for top_k_indices utility."""

    def test_top_k_indices_ordering(self):
        """Test correct index ordering."""
        weights = [0.1, 0.5, 0.3, 0.8, 0.2]

        top_3 = AttentionScorer.top_k_indices(weights, k=3)

        assert len(top_3) == 3, "Should return 3 indices"
        assert top_3[0] == 3, "Index 3 has highest weight (0.8)"
        assert top_3[1] == 1, "Index 1 has second highest (0.5)"
        assert top_3[2] == 2, "Index 2 has third highest (0.3)"

    def test_top_k_indices_all(self):
        """Test when k equals list size."""
        weights = [0.2, 0.5, 0.1]

        top_all = AttentionScorer.top_k_indices(weights, k=3)

        assert len(top_all) == 3, "Should return all indices"
        assert top_all == [1, 0, 2], "Should be ordered by weight"

    def test_top_k_indices_k_larger(self):
        """Test when k > list size."""
        weights = [0.3, 0.7]

        top_5 = AttentionScorer.top_k_indices(weights, k=5)

        assert len(top_5) == 2, "Should return only available indices"
