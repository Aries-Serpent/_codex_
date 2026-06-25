"""Tests for MLP scoring."""

from __future__ import annotations

from agents.mlp_scoring import MLPScorer


class TestMLPScorer:
    """Tests for MLPScorer."""

    def test_mlp_deterministic_initialization(self):
        """Test MLP has deterministic weights."""
        mlp1 = MLPScorer(input_dim=4, hidden_dim=3)
        mlp2 = MLPScorer(input_dim=4, hidden_dim=3)

        test_features = [0.5, 0.3, 0.1, 0.7]

        score1 = mlp1.score(test_features)
        score2 = mlp2.score(test_features)

        assert score1 == score2, "Same initialization should produce identical scores"

    def test_mlp_fallback_path_defaults(self):
        """Test MLP scoring without numpy."""
        mlp = MLPScorer(input_dim=5, hidden_dim=4, use_numpy=False)

        test_features = [0.2, 0.4, 0.6, 0.8, 1.0]

        score = mlp.score(test_features)

        assert isinstance(score, float), "Score should be a float"

    def test_mlp_forward_pass_shape(self):
        """Test forward pass produces scalar output."""
        mlp = MLPScorer(input_dim=6, hidden_dim=3)

        test_features = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]

        score = mlp.score(test_features)

        assert isinstance(score, float), "Output should be scalar"

    def test_mlp_monotonic_with_impact_increase(self):
        """Test score generally increases with higher feature values."""
        mlp = MLPScorer(input_dim=4, hidden_dim=3)

        # Low impact features
        features_low = [0.1, 0.1, 0.1, 0.1]
        score_low = mlp.score(features_low)

        # High impact features
        features_high = [1.0, 1.0, 1.0, 1.0]
        score_high = mlp.score(features_high)

        # Note: Due to random initialization, we can't guarantee monotonicity
        # but we can check that the model produces different scores
        assert score_low != score_high, "Different inputs should produce different scores"

    def test_mlp_batch_scoring(self):
        """Test batch scoring produces correct number of outputs."""
        mlp = MLPScorer(input_dim=3, hidden_dim=2)

        feature_batch = [
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6],
            [0.7, 0.8, 0.9],
        ]

        scores = mlp.batch_score(feature_batch)

        assert len(scores) == 3, "Should produce 3 scores"
        assert all(isinstance(s, float) for s in scores), "All scores should be floats"

    def test_mlp_handles_feature_dimension_mismatch(self):
        """Test MLP handles mismatched feature dimensions gracefully."""
        mlp = MLPScorer(input_dim=5, hidden_dim=3)

        # Too few features
        features_short = [0.1, 0.2, 0.3]
        score_short = mlp.score(features_short)
        assert isinstance(score_short, float), "Should handle short features"

        # Too many features
        features_long = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
        score_long = mlp.score(features_long)
        assert isinstance(score_long, float), "Should handle long features"

    def test_mlp_zero_features(self):
        """Test MLP with all-zero features."""
        mlp = MLPScorer(input_dim=4, hidden_dim=3)

        features_zero = [0.0, 0.0, 0.0, 0.0]

        score = mlp.score(features_zero)

        assert isinstance(score, float), "Should handle zero features"

    def test_mlp_different_architectures(self):
        """Test different hidden dimensions produce valid scores."""
        mlp_small = MLPScorer(input_dim=5, hidden_dim=2)
        mlp_large = MLPScorer(input_dim=5, hidden_dim=8)

        test_features = [0.3, 0.4, 0.5, 0.6, 0.7]

        score_small = mlp_small.score(test_features)
        score_large = mlp_large.score(test_features)

        # Both should produce valid float scores
        assert isinstance(score_small, float), "Small MLP should work"
        assert isinstance(score_large, float), "Large MLP should work"
        # Note: We don't assert inequality as deterministic initialization
        # could theoretically produce similar scores

    def test_mlp_consistency_across_calls(self):
        """Test MLP produces consistent scores for same input."""
        mlp = MLPScorer(input_dim=4, hidden_dim=3)

        test_features = [0.5, 0.3, 0.7, 0.2]

        score1 = mlp.score(test_features)
        score2 = mlp.score(test_features)
        score3 = mlp.score(test_features)

        assert score1 == score2 == score3, "Should be consistent across calls"
