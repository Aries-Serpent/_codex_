"""
Unit tests for AttentionScorer class.

Tests attention weight extraction, importance scoring, and attention flow analysis.
"""

from unittest.mock import Mock

import pytest

# Graceful import handling for optional dependencies
try:
    import numpy as np
    import torch

    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False
    torch = None
    np = None
    pytestmark = pytest.mark.skip("Required dependencies (torch, numpy) not available")

# Only import if dependencies are available
if HAS_DEPS:
    from codex.interpretability.attention_scorer import (
        AttentionAnalysis,
        AttentionScorer,
    )
else:
    AttentionScorer = None
    AttentionAnalysis = None


# Conditional class definition - only define if torch is available
if HAS_DEPS and torch is not None:

    class MockTransformerModel(torch.nn.Module):
        """Mock transformer model for testing."""

        def __init__(self, num_layers=2, num_heads=4, seq_len=10, hidden_dim=64):
            super().__init__()
            self.num_layers = num_layers
            self.num_heads = num_heads
            self.seq_len = seq_len
            self.hidden_dim = hidden_dim
            # Pre-generate attention weights to avoid exhaustion
            self._attention_weights = self._generate_mock_attention()
            # Configure model attributes
            self.config = type(
                "Config",
                (),
                {
                    "num_hidden_layers": num_layers,
                    "num_attention_heads": num_heads,
                    "hidden_size": hidden_dim,
                },
            )()

        def _generate_mock_attention(self):
            """Generate realistic attention weight tensors."""
            # Shape: [batch, num_layers, num_heads, seq_len, seq_len]
            weights = []
            for _ in range(self.num_layers):
                layer_weights = torch.softmax(
                    torch.randn(1, self.num_heads, self.seq_len, self.seq_len), dim=-1
                )
                weights.append(layer_weights)
            return weights

        def get_attention_weights(self, layer_idx=None):
            """Return attention weights for specified layer or all layers."""
            if layer_idx is not None:
                return self._attention_weights[layer_idx]
            return self._attention_weights

        def forward(self, input_ids, attention_mask=None, output_attentions=False):
            batch_size = input_ids.size(0)
            seq_len = input_ids.size(1)

            # Generate mock attention weights
            attentions = []
            for _ in range(self.num_layers):
                # Shape: (batch_size, num_heads, seq_len, seq_len)
                attn = torch.softmax(
                    torch.randn(batch_size, self.num_heads, seq_len, seq_len), dim=-1
                )
                attentions.append(attn)

            # Mock output
            mock_output = Mock()
            mock_output.attentions = attentions if output_attentions else None
            mock_output.last_hidden_state = torch.randn(batch_size, seq_len, self.hidden_dim)

            return mock_output

else:
    # Dummy class when torch is not available
    class MockTransformerModel:
        pass


class TestAttentionScorer:
    """Test suite for AttentionScorer."""

    @pytest.fixture
    def mock_model(self):
        """Provide fresh mock transformer model for each test.

        Returns:
            MockTransformerModel: Configured with 2 layers, 4 heads, 10 sequence length
        """
        # Ensure each test gets independent instance
        return MockTransformerModel(num_layers=2, num_heads=4, seq_len=10)

    @pytest.fixture
    def scorer(self, mock_model):
        """Create an AttentionScorer instance."""
        return AttentionScorer(mock_model, device="cpu")

    @pytest.fixture
    def sample_input(self):
        """Create sample input tensors."""
        batch_size = 1
        seq_len = 10
        input_ids = torch.randint(0, 1000, (batch_size, seq_len))
        attention_mask = torch.ones(batch_size, seq_len)
        return input_ids, attention_mask

    def test_initialization(self, mock_model):
        """Test AttentionScorer initialization."""
        scorer = AttentionScorer(mock_model)
        assert scorer.model == mock_model, "model is not valid"
        assert scorer.normalize is True, "normalize is not valid"
        assert isinstance(scorer.device, torch.device)

    def test_initialization_custom_device(self, mock_model):
        """Test initialization with custom device."""
        scorer = AttentionScorer(mock_model, device="cpu")
        assert scorer.device == torch.device("cpu"), "device is not valid"

    def test_extract_attention_weights(self, scorer, sample_input):
        """Test extraction of attention weights."""
        input_ids, attention_mask = sample_input

        attn_weights, layer_names = scorer.extract_attention_weights(input_ids, attention_mask)

        assert isinstance(attn_weights, list)
        assert isinstance(layer_names, list)
        # Enhanced assertion: should extract non-empty attention weights
        assert len(attn_weights) > 0, "Should extract non-empty attention weights"
        assert len(layer_names) == len(attn_weights), "Layer_names must not be empty"
        # Verify we got the expected number of layers
        assert (len(attn_weights) == scorer.model.num_layers, "Attn_weights must not be empty"
        ), f"Expected {scorer.model.num_layers} layers"

        # Check shape of attention weights
        for attn in attn_weights:
            assert attn.dim() == 4, "Condition must be true"
            assert attn.size(0) == 1, "Condition must be true"
            assert attn.size(2) == attn.size(3), "Condition must be true"
            # Verify sequence length matches
            assert attn.size(2) == scorer.model.seq_len, "Sequence length mismatch"

    def test_compute_token_importance_mean(self, scorer):
        """Test token importance computation with mean method."""
        # Create mock attention weights
        batch_size, num_heads, seq_len = 1, 4, 10
        attn_weights = [
            torch.softmax(torch.randn(batch_size, num_heads, seq_len, seq_len), dim=-1)
            for _ in range(2)
        ]

        importance = scorer.compute_token_importance(attn_weights, method="mean")

        assert isinstance(importance, np.ndarray)
        assert importance.shape == (seq_len,)
        assert np.all(importance >= 0), "importance must be greater than zero"
        # Check normalization
        assert np.abs(importance.sum() - 1.0) < 1e-5, "Condition must be true"

    def test_compute_token_importance_invalid_method(self, scorer):
        """Test that invalid method raises error."""
        attn_weights = [torch.randn(1, 4, 10, 10)]

        with pytest.raises(ValueError, match="Unknown method"):
            scorer.compute_token_importance(attn_weights, method="invalid")

    def test_compute_attention_flow_mean(self, scorer):
        """Test attention flow computation with mean aggregation."""
        batch_size, num_heads, seq_len = 1, 4, 10
        attn_weights = [
            torch.softmax(torch.randn(batch_size, num_heads, seq_len, seq_len), dim=-1)
            for _ in range(2)
        ]

        flow = scorer.compute_attention_flow(attn_weights, layer_aggregation="mean")

        assert isinstance(flow, np.ndarray)
        assert flow.shape == (seq_len, seq_len)
        assert np.all(flow >= 0), "flow must be greater than zero"

    def test_analyze_attention(self, scorer, sample_input):
        """Test complete attention analysis."""
        input_ids, attention_mask = sample_input
        tokens = [f"token_{i}" for i in range(input_ids.size(1))]

        analysis = scorer.analyze_attention(
            input_ids=input_ids, attention_mask=attention_mask, tokens=tokens
        )

        assert isinstance(analysis, AttentionAnalysis)
        assert isinstance(analysis.attention_weights, np.ndarray)
        assert isinstance(analysis.token_importance, np.ndarray)
        assert isinstance(analysis.attention_flow, np.ndarray)
        assert isinstance(analysis.layer_names, list)
        assert analysis.tokens == tokens, "tokens is not valid"
        assert analysis.token_ids is not None, "token_ids must be initialized"

    def test_get_top_attended_tokens(self, scorer):
        """Test getting top attended tokens."""
        # Create mock analysis
        seq_len = 10
        analysis = AttentionAnalysis(
            attention_weights=np.random.rand(2, 4, seq_len, seq_len),
            token_importance=np.random.rand(seq_len),
            attention_flow=np.random.rand(seq_len, seq_len),
            layer_names=["layer_0", "layer_1"],
            token_ids=list(range(seq_len)),
            tokens=[f"token_{i}" for i in range(seq_len)],
        )

        top_tokens = scorer.get_top_attended_tokens(analysis, top_k=5)

        assert len(top_tokens) == 5, "Top_tokens must not be empty"
        for idx, score, token_str in top_tokens:
            assert isinstance(idx, int)
            assert isinstance(score, float)
            assert isinstance(token_str, str)
            assert 0 <= idx < seq_len, "0 is not valid"
