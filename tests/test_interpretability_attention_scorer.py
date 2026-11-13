"""
Test suite for the interpretability attention scorer.

The scorer wraps a ``torch.nn.Module`` (``AttentionScorer(model, ...)``) and
exposes ``extract_attention_weights``, ``compute_token_importance``,
``compute_attention_flow``, ``analyze_attention`` and
``get_top_attended_tokens``.  Attention tensors use the Hugging Face layout:
one ``(batch, heads, seq, seq)`` tensor per layer.

Tests that need real tensor math are skipped when the repo-local torch stub is
active; they run in CI against real CPU torch.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock

import numpy as np
import pytest

torch = pytest.importorskip("torch")

from codex.interpretability.attention_scorer import (  # noqa: E402
    AttentionAnalysis,
    AttentionScorer,
)

TORCH_STUB = getattr(torch, "__version__", "").endswith("stub")
requires_real_torch = pytest.mark.skipif(
    TORCH_STUB, reason="tensor math requires real torch (stub active)"
)


def _mock_model() -> MagicMock:
    model = MagicMock()
    model.to.return_value = model
    return model


def _layers(array: np.ndarray) -> list:
    """Convert a (layers, heads, seq, seq) array into per-layer batch tensors."""
    return [torch.tensor(layer[None, ...], dtype=torch.float32) for layer in array]


class _FakeAttentionModel(torch.nn.Module if not TORCH_STUB else object):
    """Minimal HF-style model returning fixed ``attentions``."""

    def __init__(self, attentions: list) -> None:
        super().__init__()
        self._attentions = attentions
        self.calls: list[dict] = []

    def forward(self, input_ids=None, attention_mask=None, output_attentions=False):
        self.calls.append({"output_attentions": output_attentions, "mask": attention_mask})
        return SimpleNamespace(attentions=tuple(self._attentions) if output_attentions else None)


class TestAttentionAnalysisDataclass:
    """Test AttentionAnalysis dataclass."""

    def test_attention_analysis_creation(self):
        analysis = AttentionAnalysis(
            attention_weights=np.random.randn(2, 8, 10, 10),
            token_importance=np.random.randn(10),
            attention_flow=np.random.randn(10, 10),
            layer_names=["layer_1", "layer_2"],
        )

        assert analysis.attention_weights.shape == (2, 8, 10, 10)
        assert analysis.token_importance.shape == (10,)
        assert analysis.attention_flow.shape == (10, 10)
        assert analysis.token_ids is None
        assert analysis.tokens is None

    def test_attention_analysis_with_token_ids(self):
        analysis = AttentionAnalysis(
            attention_weights=np.random.randn(1, 8, 5, 5),
            token_importance=np.random.randn(5),
            attention_flow=np.random.randn(5, 5),
            layer_names=["layer_1"],
            token_ids=[101, 2054, 2003, 2175, 102],
        )

        assert analysis.token_ids == [101, 2054, 2003, 2175, 102]

    def test_attention_analysis_with_tokens(self):
        analysis = AttentionAnalysis(
            attention_weights=np.random.randn(1, 8, 3, 3),
            token_importance=np.random.randn(3),
            attention_flow=np.random.randn(3, 3),
            layer_names=["layer_1"],
            tokens=["[CLS]", "hello", "[SEP]"],
        )

        assert analysis.tokens == ["[CLS]", "hello", "[SEP]"]


@requires_real_torch
class TestAttentionScorerInitialization:
    """AttentionScorer requires a model and moves it to the target device."""

    def test_model_is_required(self):
        with pytest.raises(TypeError):
            AttentionScorer()  # type: ignore[call-arg]

    def test_model_moved_to_device_and_eval(self):
        model = _mock_model()
        scorer = AttentionScorer(model, device="cpu")

        assert scorer.model is model
        assert scorer.normalize is True
        assert scorer.epsilon == pytest.approx(1e-10)
        model.to.assert_called_once()
        model.eval.assert_called_once()

    def test_custom_options(self):
        scorer = AttentionScorer(_mock_model(), normalize=False, device="cpu", epsilon=1e-6)

        assert scorer.normalize is False
        assert scorer.epsilon == pytest.approx(1e-6)


@requires_real_torch
class TestTokenImportanceScoring:
    def test_mean_importance_shape_and_normalization(self):
        scorer = AttentionScorer(_mock_model(), device="cpu")
        weights = _layers(np.abs(np.random.randn(2, 8, 10, 10)))

        importance = scorer.compute_token_importance(weights)

        assert importance.shape == (10,)
        assert np.all(importance >= 0)
        assert importance.sum() == pytest.approx(1.0, rel=1e-5)

    def test_highest_importance_token(self):
        scorer = AttentionScorer(_mock_model(), device="cpu")
        array = np.zeros((1, 1, 5, 5))
        array[0, 0, :, 2] = 1.0  # every token attends to token 2

        for method in ("mean", "max", "norm"):
            importance = scorer.compute_token_importance(_layers(array), method=method)
            assert int(np.argmax(importance)) == 2, method

    def test_unnormalized_mean_matches_numpy(self):
        scorer = AttentionScorer(_mock_model(), normalize=False, device="cpu")
        array = np.abs(np.random.randn(3, 4, 6, 6))

        importance = scorer.compute_token_importance(_layers(array))

        np.testing.assert_allclose(importance, array.mean(axis=(0, 1, 2)), rtol=1e-5)

    def test_zero_attention_weights_do_not_produce_nan(self):
        scorer = AttentionScorer(_mock_model(), device="cpu")

        importance = scorer.compute_token_importance(_layers(np.zeros((1, 1, 5, 5))))

        assert not np.any(np.isnan(importance))
        np.testing.assert_array_equal(importance, np.zeros(5))

    def test_unknown_method_raises(self):
        scorer = AttentionScorer(_mock_model(), device="cpu")

        with pytest.raises(ValueError, match="Unknown method"):
            scorer.compute_token_importance(_layers(np.ones((1, 1, 3, 3))), method="bogus")

    def test_empty_weights_raise(self):
        scorer = AttentionScorer(_mock_model(), device="cpu")

        with pytest.raises(ValueError, match="No attention weights"):
            scorer.compute_token_importance([])


@requires_real_torch
class TestAttentionFlowAnalysis:
    def test_flow_shape(self):
        scorer = AttentionScorer(_mock_model(), device="cpu")

        flow = scorer.compute_attention_flow(_layers(np.random.rand(2, 8, 10, 10)))

        assert flow.shape == (10, 10)

    def test_flow_aggregations_match_numpy(self):
        scorer = AttentionScorer(_mock_model(), device="cpu")
        array = np.random.rand(3, 4, 5, 5)
        per_layer = array.mean(axis=1)

        np.testing.assert_allclose(
            scorer.compute_attention_flow(_layers(array), "mean"), per_layer.mean(0), rtol=1e-5
        )
        np.testing.assert_allclose(
            scorer.compute_attention_flow(_layers(array), "last"), per_layer[-1], rtol=1e-5
        )
        np.testing.assert_allclose(
            scorer.compute_attention_flow(_layers(array), "sum"), per_layer.sum(0), rtol=1e-5
        )

    def test_self_attention_on_diagonal(self):
        scorer = AttentionScorer(_mock_model(), device="cpu")

        flow = scorer.compute_attention_flow(_layers(np.eye(3)[None, None, ...]))

        np.testing.assert_allclose(flow, np.eye(3))

    def test_unknown_aggregation_raises(self):
        scorer = AttentionScorer(_mock_model(), device="cpu")

        with pytest.raises(ValueError, match="Unknown aggregation"):
            scorer.compute_attention_flow(_layers(np.ones((1, 1, 2, 2))), "median")

    def test_empty_weights_raise(self):
        scorer = AttentionScorer(_mock_model(), device="cpu")

        with pytest.raises(ValueError, match="No attention weights"):
            scorer.compute_attention_flow([])


@requires_real_torch
class TestModelIntegration:
    def test_extract_attention_weights_from_outputs(self):
        attentions = _layers(np.random.rand(2, 4, 6, 6))
        model = _FakeAttentionModel(attentions)
        scorer = AttentionScorer(model, device="cpu")

        weights, names = scorer.extract_attention_weights(torch.zeros((1, 6), dtype=torch.long))

        assert names == ["layer_0", "layer_1"]
        assert len(weights) == 2
        assert tuple(weights[0].shape) == (1, 4, 6, 6)
        assert model.calls[0]["output_attentions"] is True

    def test_analyze_attention_full_pipeline(self):
        array = np.random.rand(3, 2, 4, 4)
        model = _FakeAttentionModel(_layers(array))
        scorer = AttentionScorer(model, device="cpu")
        input_ids = torch.tensor([[11, 12, 13, 14]])
        tokens = ["a", "b", "c", "d"]

        analysis = scorer.analyze_attention(input_ids, tokens=tokens)

        assert isinstance(analysis, AttentionAnalysis)
        assert analysis.attention_weights.shape == (3, 2, 4, 4)
        np.testing.assert_allclose(analysis.attention_weights, array, rtol=1e-6)
        assert analysis.token_importance.shape == (4,)
        assert analysis.attention_flow.shape == (4, 4)
        assert analysis.layer_names == ["layer_0", "layer_1", "layer_2"]
        assert analysis.token_ids == [11, 12, 13, 14]
        assert analysis.tokens == tokens

    def test_analyze_attention_without_attentions_raises(self):
        model = _FakeAttentionModel([])
        scorer = AttentionScorer(model, device="cpu")

        with pytest.raises(ValueError, match="Failed to extract attention weights"):
            scorer.analyze_attention(torch.zeros((1, 3), dtype=torch.long))


@requires_real_torch
class TestTopAttendedTokens:
    def test_top_k_sorted_with_tokens(self):
        scorer = AttentionScorer(_mock_model(), device="cpu")
        analysis = AttentionAnalysis(
            attention_weights=np.zeros((1, 1, 4, 4)),
            token_importance=np.array([0.1, 0.4, 0.2, 0.3]),
            attention_flow=np.zeros((4, 4)),
            layer_names=["layer_0"],
            tokens=["w", "x", "y", "z"],
        )

        top = scorer.get_top_attended_tokens(analysis, top_k=2)

        assert [(i, t) for i, _, t in top] == [(1, "x"), (3, "z")]
        assert top[0][1] == pytest.approx(0.4)

    def test_top_k_without_tokens(self):
        scorer = AttentionScorer(_mock_model(), device="cpu")
        analysis = AttentionAnalysis(
            attention_weights=np.zeros((1, 1, 3, 3)),
            token_importance=np.array([0.5, 0.2, 0.3]),
            attention_flow=np.zeros((3, 3)),
            layer_names=["layer_0"],
        )

        top = scorer.get_top_attended_tokens(analysis, top_k=3)

        assert [i for i, _, _ in top] == [0, 2, 1]
        assert all(token is None for _, _, token in top)
