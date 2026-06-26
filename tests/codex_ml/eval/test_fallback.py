"""
Test Eval Fallback Module

Tests for the fallback evaluation metrics module.
Tests synthetic data metrics, token encoding, and perplexity proxy.
"""

from __future__ import annotations

import math

import pytest

from codex_ml.eval.fallback import (
    IGNORE_INDEX,
    SyntheticSummary,
    _encode_tokens,
    _perplexity_proxy,
    synthetic_alignment,
)


class TestSyntheticSummary:
    """Tests for SyntheticSummary dataclass."""

    def test_creation(self) -> None:
        """Test SyntheticSummary creation."""
        summary = SyntheticSummary(
            token_accuracy=0.85,
            perplexity_proxy=2.5,
            exact_match=0.7,
            avg_length=10.5,
            samples=100,
        )

        assert summary.token_accuracy == 0.85, "token_accuracy is not valid"
        assert summary.perplexity_proxy == 2.5, "perplexity_proxy is not valid"
        assert summary.exact_match == 0.7, "exact_match is not valid"
        assert summary.avg_length == 10.5, "Length must be greater than zero"
        assert summary.samples == 100, "samples is not valid"

    def test_as_dict(self) -> None:
        """Test conversion to dictionary."""
        summary = SyntheticSummary(
            token_accuracy=0.9,
            perplexity_proxy=1.5,
            exact_match=0.8,
            avg_length=5.0,
            samples=50,
        )

        result = summary.as_dict()

        assert result["token_accuracy"] == 0.9, "Result must not be empty"
        assert result["perplexity_proxy"] == 1.5, "Result must not be empty"
        assert result["exact_match"] == 0.8, "Result must not be empty"
        assert result["avg_length"] == 5.0, "Result must not be empty"
        assert result["samples"] == 50.0, "Result must not be empty"

    def test_frozen(self) -> None:
        """Test that SyntheticSummary is frozen (immutable)."""
        summary = SyntheticSummary(
            token_accuracy=0.9,
            perplexity_proxy=1.5,
            exact_match=0.8,
            avg_length=5.0,
            samples=50,
        )

        with pytest.raises(AttributeError):
            summary.token_accuracy = 0.5  # type: ignore


class TestEncodeTokens:
    """Tests for _encode_tokens function."""

    def test_basic_encoding(self) -> None:
        """Test basic token encoding."""
        sequences = ["hello world", "world hello"]
        encoded, vocab = _encode_tokens(sequences)

        assert len(encoded) == 2, "Encoded must not be empty"
        assert len(vocab) == 2, "Vocab must not be empty"
        assert "hello" in vocab, "Condition must be true"
        assert "world" in vocab, "Condition must be true"

    def test_empty_sequences(self) -> None:
        """Test encoding empty sequences."""
        sequences: list[str] = []
        encoded, vocab = _encode_tokens(sequences)

        assert encoded == [], "encoded is not valid"
        assert vocab == {}, "vocab is not valid"

    def test_with_existing_vocab(self) -> None:
        """Test encoding with existing vocabulary."""
        vocab = {"hello": 0, "world": 1}
        sequences = ["hello world"]
        encoded, result_vocab = _encode_tokens(sequences, vocab)

        assert encoded == [[0, 1]]
        assert result_vocab == vocab, "Result must not be empty"

    def test_extend_vocab(self) -> None:
        """Test extending vocabulary with new tokens."""
        vocab = {"hello": 0}
        sequences = ["hello world"]
        _encoded, result_vocab = _encode_tokens(sequences, vocab)

        assert len(result_vocab) == 2, "Result_vocab must not be empty"
        assert result_vocab["hello"] == 0, "Result must not be empty"
        assert result_vocab["world"] == 1, "Result must not be empty"

    def test_disallow_new_tokens(self) -> None:
        """Test error when new tokens not allowed."""
        vocab = {"hello": 0}
        sequences = ["hello world"]

        with pytest.raises(KeyError, match="Token 'world' not found"):
            _encode_tokens(sequences, vocab, allow_new_tokens=False)

    def test_single_token_sequences(self) -> None:
        """Test sequences with single tokens."""
        sequences = ["a", "b", "c"]
        encoded, _vocab = _encode_tokens(sequences)

        assert len(encoded) == 3, "Encoded must not be empty"
        assert all(len(seq) == 1 for seq in encoded), "Seq must not be empty"

    def test_empty_string(self) -> None:
        """Test encoding empty string."""
        sequences = [""]
        encoded, vocab = _encode_tokens(sequences)

        assert encoded == [[]], "encoded is not valid"
        assert vocab == {}, "vocab is not valid"


class TestPerplexityProxy:
    """Tests for _perplexity_proxy function."""

    def test_perfect_prediction(self) -> None:
        """Test perplexity with perfect prediction."""
        predicted = [0, 1, 2]
        targets = [0, 1, 2]

        result = _perplexity_proxy(predicted, targets)

        # Should be low but not 1.0 due to counting
        assert result > 0, "result must be greater than zero"
        assert result < float("inf"), "Result must not be empty"

    def test_empty_predictions(self) -> None:
        """Test perplexity with empty predictions."""
        predicted: list[int] = []
        targets: list[int] = []

        result = _perplexity_proxy(predicted, targets)

        assert result == float("inf"), "Result must not be empty"

    def test_all_ignored(self) -> None:
        """Test perplexity when all predictions are ignored."""
        predicted = [IGNORE_INDEX, IGNORE_INDEX]
        targets = [0, 1]

        result = _perplexity_proxy(predicted, targets)

        assert result == float("inf"), "Result must not be empty"

    def test_all_targets_ignored(self) -> None:
        """Test perplexity when all targets are ignored."""
        predicted = [0, 1]
        targets = [IGNORE_INDEX, IGNORE_INDEX]

        result = _perplexity_proxy(predicted, targets)

        assert result == float("inf"), "Result must not be empty"

    def test_mixed_predictions(self) -> None:
        """Test perplexity with mixed predictions."""
        predicted = [0, 0, 1, 1]
        targets = [0, 1, 0, 1]

        result = _perplexity_proxy(predicted, targets)

        assert result > 0, "result must be greater than zero"
        assert result < float("inf"), "Result must not be empty"


class TestSyntheticAlignment:
    """Tests for synthetic_alignment function."""

    def test_perfect_alignment(self) -> None:
        """Test alignment with perfect predictions."""
        predictions = ["hello world", "foo bar"]
        references = ["hello world", "foo bar"]

        result = synthetic_alignment(predictions, references)

        assert result.exact_match == 1.0, "Result must not be empty"
        assert result.token_accuracy == 1.0, "Result must not be empty"
        assert result.samples == 2, "Result must not be empty"

    def test_no_alignment(self) -> None:
        """Test alignment with completely different predictions."""
        predictions = ["a b c", "d e f"]
        references = ["x y z", "u v w"]

        result = synthetic_alignment(predictions, references)

        assert result.exact_match == 0.0, "Result must not be empty"
        assert result.token_accuracy == 0.0, "Result must not be empty"
        assert result.samples == 2, "Result must not be empty"

    def test_partial_alignment(self) -> None:
        """Test alignment with partial matches."""
        predictions = ["hello world", "foo bar"]
        references = ["hello there", "foo baz"]

        result = synthetic_alignment(predictions, references)

        assert result.exact_match == 0.0, "Result must not be empty"
        assert 0 < result.token_accuracy < 1, "Result must not be empty"
        assert result.samples == 2, "Result must not be empty"

    def test_mismatched_length_raises(self) -> None:
        """Test error when predictions and references have different lengths."""
        predictions = ["a", "b"]
        references = ["x"]

        with pytest.raises(ValueError, match="same length"):
            synthetic_alignment(predictions, references)

    def test_empty_inputs(self) -> None:
        """Test alignment with empty inputs."""
        predictions: list[str] = []
        references: list[str] = []

        result = synthetic_alignment(predictions, references)

        assert result.samples == 0, "Result must not be empty"
        assert result.avg_length == 0.0, "Result must not be empty"

    def test_single_sample(self) -> None:
        """Test alignment with single sample."""
        predictions = ["hello world"]
        references = ["hello world"]

        result = synthetic_alignment(predictions, references)

        assert result.samples == 1, "Result must not be empty"
        assert result.exact_match == 1.0, "Result must not be empty"

    def test_avg_length_calculation(self) -> None:
        """Test average length calculation."""
        predictions = ["a b c", "d e"]
        references = ["x y z", "u v"]

        result = synthetic_alignment(predictions, references)

        assert result.avg_length > 0, "avg_length must be positive"
        assert result.samples == 2, "Result must not be empty"

    def test_perplexity_is_finite(self) -> None:
        """Test that perplexity is finite for valid inputs."""
        predictions = ["hello world", "foo bar"]
        references = ["hello there", "foo baz"]

        result = synthetic_alignment(predictions, references)

        assert math.isfinite(result.perplexity_proxy), "Result must not be empty"


class TestIgnoreIndex:
    """Tests for IGNORE_INDEX constant."""

    def test_ignore_index_value(self) -> None:
        """Test that IGNORE_INDEX is -1."""
        assert IGNORE_INDEX == -1, "IGNORE_INDEX is not valid"

    def test_ignore_index_in_encoding(self) -> None:
        """Test that IGNORE_INDEX doesn't appear in normal encoding."""
        sequences = ["hello world"]
        encoded, _ = _encode_tokens(sequences)

        for seq in encoded:
            for token_id in seq:
                assert token_id != IGNORE_INDEX, "token_id is not valid"
