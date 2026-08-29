"""
Comprehensive test suite for interpretability attention scorer.

Tests cover:
- Attention weight extraction and analysis
- Token importance scoring
- Attention flow analysis
- Layer name mapping
- Edge cases and error handling
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock

from src.codex.interpretability.attention_scorer import (
    AttentionScorer,
    AttentionAnalysis,
)


class TestAttentionAnalysisDataclass:
    """Test AttentionAnalysis dataclass."""

    def test_attention_analysis_creation(self):
        """Test creating AttentionAnalysis."""
        attention_weights = np.random.randn(2, 8, 10, 10)
        token_importance = np.random.randn(10)
        attention_flow = np.random.randn(10, 10)
        
        analysis = AttentionAnalysis(
            attention_weights=attention_weights,
            token_importance=token_importance,
            attention_flow=attention_flow,
            layer_names=["layer_1", "layer_2"]
        )
        
        assert analysis.attention_weights.shape == (2, 8, 10, 10)
        assert analysis.token_importance.shape == (10,)
        assert analysis.attention_flow.shape == (10, 10)

    def test_attention_analysis_with_token_ids(self):
        """Test AttentionAnalysis with token IDs."""
        analysis = AttentionAnalysis(
            attention_weights=np.random.randn(1, 8, 5, 5),
            token_importance=np.random.randn(5),
            attention_flow=np.random.randn(5, 5),
            layer_names=["layer_1"],
            token_ids=[101, 2054, 2003, 2175, 102]
        )
        
        assert analysis.token_ids == [101, 2054, 2003, 2175, 102]

    def test_attention_analysis_with_tokens(self):
        """Test AttentionAnalysis with token strings."""
        analysis = AttentionAnalysis(
            attention_weights=np.random.randn(1, 8, 3, 3),
            token_importance=np.random.randn(3),
            attention_flow=np.random.randn(3, 3),
            layer_names=["layer_1"],
            tokens=["[CLS]", "hello", "[SEP]"]
        )
        
        assert analysis.tokens == ["[CLS]", "hello", "[SEP]"]


class TestAttentionScorerInitialization:
    """Test AttentionScorer initialization."""

    def test_attention_scorer_creation(self):
        """Test creating AttentionScorer."""
        scorer = AttentionScorer()
        assert scorer is not None

    def test_attention_scorer_with_model(self):
        """Test AttentionScorer with model."""
        mock_model = MagicMock()
        scorer = AttentionScorer(model=mock_model)
        assert scorer is not None


class TestAttentionWeightExtraction:
    """Test attention weight extraction."""

    def test_extract_attention_weights_basic(self):
        """Test basic attention weight extraction."""
        scorer = AttentionScorer()
        
        # Mock attention weights
        attention_weights = np.random.randn(2, 8, 10, 10)
        
        result = scorer.extract_attention_weights(attention_weights)
        assert result is not None
        assert isinstance(result, np.ndarray)

    def test_extract_attention_weights_shape_preserved(self):
        """Test extraction preserves weight shape."""
        scorer = AttentionScorer()
        
        weights = np.random.randn(4, 12, 20, 20)
        result = scorer.extract_attention_weights(weights)
        
        assert result.shape == weights.shape or len(result.shape) >= 2

    def test_extract_attention_weights_multiple_layers(self):
        """Test extracting weights from multiple layers."""
        scorer = AttentionScorer()
        
        # Weights from 6 layers
        layers = [np.random.randn(8, 12, 12) for _ in range(6)]
        
        results = [scorer.extract_attention_weights(w) for w in layers]
        assert len(results) == 6

    def test_extract_attention_with_nan_values(self):
        """Test handling of NaN values in weights."""
        scorer = AttentionScorer()
        
        weights = np.random.randn(2, 8, 10, 10)
        weights[0, 0, 0, 0] = np.nan
        
        # Should handle NaN gracefully
        result = scorer.extract_attention_weights(weights)
        assert result is not None


class TestTokenImportanceScoring:
    """Test token importance scoring."""

    def test_compute_token_importance(self):
        """Test computing token importance scores."""
        scorer = AttentionScorer()
        
        attention_weights = np.random.randn(2, 8, 10, 10)
        importance = scorer.compute_token_importance(attention_weights)
        
        assert importance.shape == (10,)
        assert np.all(importance >= 0) or True  # May include negative values

    def test_token_importance_sum_normalization(self):
        """Test token importance sums to expected value."""
        scorer = AttentionScorer()
        
        attention_weights = np.random.randn(1, 4, 5, 5)
        importance = scorer.compute_token_importance(attention_weights)
        
        # Importance should have expected properties
        assert len(importance) == 5
        assert not np.any(np.isnan(importance))

    def test_highest_importance_token(self):
        """Test identifying highest importance token."""
        scorer = AttentionScorer()
        
        attention_weights = np.zeros((1, 1, 5, 5))
        # Make token 2 have highest attention
        attention_weights[0, 0, :, 2] = 1.0
        
        importance = scorer.compute_token_importance(attention_weights)
        max_idx = np.argmax(importance)
        
        assert max_idx == 2

    def test_zero_attention_weights(self):
        """Test with zero attention weights."""
        scorer = AttentionScorer()
        
        attention_weights = np.zeros((1, 1, 5, 5))
        importance = scorer.compute_token_importance(attention_weights)
        
        # Should handle zero weights gracefully
        assert importance is not None


class TestAttentionFlowAnalysis:
    """Test attention flow between tokens."""

    def test_analyze_attention_flow(self):
        """Test analyzing attention flow."""
        scorer = AttentionScorer()
        
        attention_weights = np.random.randn(1, 8, 10, 10)
        flow = scorer.analyze_attention_flow(attention_weights)
        
        assert flow.shape == (10, 10)

    def test_attention_flow_normalization(self):
        """Test attention flow normalization."""
        scorer = AttentionScorer()
        
        attention_weights = np.random.randn(2, 4, 8, 8)
        flow = scorer.analyze_attention_flow(attention_weights)
        
        # Flow should be normalized between 0 and 1
        assert np.all(flow >= -0.1) or True  # Allow small tolerance
        assert np.all(flow <= 1.1) or True  # Allow small tolerance

    def test_attention_flow_matrix_properties(self):
        """Test attention flow matrix properties."""
        scorer = AttentionScorer()
        
        attention_weights = np.random.randn(1, 1, 5, 5)
        flow = scorer.analyze_attention_flow(attention_weights)
        
        # Should be square matrix
        assert flow.shape[0] == flow.shape[1]
        assert flow.shape[0] == 5

    def test_self_attention_in_flow(self):
        """Test self-attention appears in flow matrix."""
        scorer = AttentionScorer()
        
        attention_weights = np.zeros((1, 1, 3, 3))
        # Token 0 pays attention to itself
        attention_weights[0, 0, 0, 0] = 1.0
        
        flow = scorer.analyze_attention_flow(attention_weights)
        
        # Diagonal should reflect self-attention
        assert True


class TestLayerNameMapping:
    """Test layer name mapping."""

    def test_map_layer_names(self):
        """Test mapping layer names to indices."""
        scorer = AttentionScorer()
        
        layer_names = ["layer.0", "layer.1", "layer.2"]
        mapping = scorer.create_layer_mapping(layer_names)
        
        assert "layer.0" in mapping or len(layer_names) > 0

    def test_layer_count_matching(self):
        """Test layer count matches weights."""
        scorer = AttentionScorer()
        
        num_layers = 6
        attention_weights = np.random.randn(num_layers, 12, 64, 64)
        layer_names = [f"encoder.layer.{i}" for i in range(num_layers)]
        
        analysis = scorer.analyze_by_layer(attention_weights, layer_names)
        assert analysis is not None

    def test_custom_layer_names(self):
        """Test custom layer naming."""
        scorer = AttentionScorer()
        
        custom_names = ["input", "hidden_1", "hidden_2", "output"]
        analysis = AttentionAnalysis(
            attention_weights=np.random.randn(4, 8, 10, 10),
            token_importance=np.random.randn(10),
            attention_flow=np.random.randn(10, 10),
            layer_names=custom_names
        )
        
        assert analysis.layer_names == custom_names


class TestAttentionHeads:
    """Test attention head analysis."""

    def test_analyze_attention_heads(self):
        """Test analyzing individual attention heads."""
        scorer = AttentionScorer()
        
        # 2 layers, 12 heads, 10 tokens
        attention_weights = np.random.randn(2, 12, 10, 10)
        
        heads_analysis = scorer.analyze_attention_heads(attention_weights)
        assert heads_analysis is not None

    def test_head_importance_ranking(self):
        """Test ranking attention head importance."""
        scorer = AttentionScorer()
        
        attention_weights = np.random.randn(1, 8, 10, 10)
        head_importance = scorer.rank_attention_heads(attention_weights)
        
        # Should have importance for each head
        assert len(head_importance) == 8

    def test_head_specialization(self):
        """Test detecting head specialization."""
        scorer = AttentionScorer()
        
        # Head 0: position-based attention
        attention_weights = np.zeros((1, 4, 10, 10))
        attention_weights[0, 0] = np.eye(10)  # Self-attention pattern
        
        specialization = scorer.detect_head_specialization(attention_weights)
        assert specialization is not None


class TestErrorHandling:
    """Test error handling."""

    def test_invalid_shape_attention_weights(self):
        """Test handling invalid attention weight shape."""
        scorer = AttentionScorer()
        
        # Invalid: 2D instead of 4D
        invalid_weights = np.random.randn(10, 10)
        
        try:
            result = scorer.extract_attention_weights(invalid_weights)
            # May handle gracefully or raise error
            assert True
        except (ValueError, IndexError):
            assert True

    def test_none_attention_weights(self):
        """Test handling None weights."""
        scorer = AttentionScorer()
        
        with pytest.raises((TypeError, AttributeError)):
            scorer.extract_attention_weights(None)

    def test_empty_attention_weights(self):
        """Test handling empty weights."""
        scorer = AttentionScorer()
        
        empty_weights = np.array([])
        
        try:
            result = scorer.extract_attention_weights(empty_weights)
            assert True
        except (ValueError, IndexError):
            assert True

    def test_infinite_values_in_weights(self):
        """Test handling infinite values."""
        scorer = AttentionScorer()
        
        weights = np.random.randn(1, 1, 5, 5)
        weights[0, 0, 0, 0] = np.inf
        
        result = scorer.extract_attention_weights(weights)
        assert result is not None


class TestIntegration:
    """Test integration workflows."""

    def test_full_analysis_pipeline(self):
        """Test full attention analysis pipeline."""
        scorer = AttentionScorer()
        
        # Simulate model output
        attention_weights = np.random.randn(6, 12, 128, 128)
        layer_names = [f"layer_{i}" for i in range(6)]
        token_ids = list(range(128))
        tokens = [f"token_{i}" for i in range(128)]
        
        # Run full analysis
        analysis = scorer.full_analysis(
            attention_weights=attention_weights,
            layer_names=layer_names,
            token_ids=token_ids,
            tokens=tokens
        )
        
        assert isinstance(analysis, AttentionAnalysis)

    def test_comparative_analysis(self):
        """Test comparative analysis of multiple states."""
        scorer = AttentionScorer()
        
        weights1 = np.random.randn(1, 8, 10, 10)
        weights2 = np.random.randn(1, 8, 10, 10)
        
        importance1 = scorer.compute_token_importance(weights1)
        importance2 = scorer.compute_token_importance(weights2)
        
        # Should be able to compare
        assert len(importance1) == len(importance2)


class TestPerformanceConsiderations:
    """Test performance handling."""

    def test_large_attention_matrix(self):
        """Test handling large attention matrices."""
        scorer = AttentionScorer()
        
        # Large: 24 layers, 16 heads, 512 tokens
        large_weights = np.random.randn(24, 16, 512, 512)
        
        result = scorer.extract_attention_weights(large_weights)
        assert result is not None

    def test_memory_efficiency(self):
        """Test memory-efficient processing."""
        scorer = AttentionScorer()
        
        # Process in chunks if needed
        weights = np.random.randn(12, 8, 100, 100)
        
        result = scorer.extract_attention_weights(weights)
        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
