"""Gap-fill tests for the ``codex_ml.metrics`` unified API.

The canonical metric functions live in ``codex_ml.metrics.unified_api`` and are
re-exported from ``codex_ml.metrics``.  Text metrics are corpus-level and take
``(predictions, references)`` sequences; classification metrics take
``(predictions, targets)`` label sequences; perplexity takes
``(logits_or_nll, targets)``.
"""

from __future__ import annotations

import math

import pytest

from codex_ml import metrics
from codex_ml.metrics import (
    batch_metrics_from_outputs,
    compute_accuracy,
    compute_bleu,
    compute_classification_metrics,
    compute_f1,
    compute_perplexity,
    compute_rouge_l,
    compute_token_accuracy,
)


class TestMetricsModule:
    def test_unified_api_exports(self):
        for name in (
            "compute_bleu",
            "compute_rouge_l",
            "compute_perplexity",
            "compute_accuracy",
            "compute_f1",
            "compute_token_accuracy",
            "compute_classification_metrics",
            "batch_metrics_from_outputs",
        ):
            assert name in metrics.__all__
            assert callable(getattr(metrics, name))

    def test_bleu_identical_text_is_one(self):
        score = compute_bleu(["the quick brown fox"], ["the quick brown fox"])

        assert score == pytest.approx(1.0, abs=1e-6)

    def test_bleu_completely_different_text_is_near_zero(self):
        score = compute_bleu(["the quick brown fox"], ["completely different text here"])

        assert 0.0 <= score < 1e-3

    def test_bleu_multiple_references(self):
        score = compute_bleu(
            ["the cat sat on the mat"], [["a dog ran away", "the cat sat on the mat"]]
        )

        assert score == pytest.approx(1.0, abs=1e-6)

    def test_bleu_length_mismatch_raises(self):
        with pytest.raises(ValueError, match="length must match"):
            compute_bleu(["a", "b"], ["a"])

    def test_rouge_l_partial_overlap(self):
        # LCS("the quick fox", "the quick brown fox jumps") = 3
        # precision = 3/3, recall = 3/5 -> F1 = 0.75
        score = compute_rouge_l(["the quick fox"], ["the quick brown fox jumps"])

        assert score == pytest.approx(0.75)

    def test_rouge_l_empty_prediction_is_zero(self):
        assert compute_rouge_l([""], ["reference text"]) == 0.0

    def test_perplexity_from_nll(self):
        nll = [math.log(2.0), math.log(8.0)]

        ppl = compute_perplexity(nll, [0, 0], from_logits=False)

        # exp(mean NLL) = exp(log 4) = 4
        assert ppl == pytest.approx(4.0)

    def test_perplexity_from_uniform_logits(self):
        logits = [[0.0, 0.0, 0.0, 0.0], [1.0, 1.0, 1.0, 1.0]]

        ppl = compute_perplexity(logits, [1, 3], from_logits=True)

        # uniform distribution over 4 classes -> perplexity 4
        assert ppl == pytest.approx(4.0, rel=1e-6)

    def test_perplexity_requires_targets(self):
        with pytest.raises(TypeError):
            compute_perplexity([0.1, 0.2])  # type: ignore[call-arg]


class TestMetricsAggregation:
    def test_batch_metrics_from_outputs_loss_to_perplexity(self):
        class _Outputs:
            loss = math.log(3.0)

        record = batch_metrics_from_outputs(_Outputs(), {})

        assert record["loss"] == pytest.approx(math.log(3.0))
        assert record["perplexity"] == pytest.approx(3.0)

    def test_bleu_with_special_characters(self):
        text = "Price: $100, Tax: 10%"

        assert compute_bleu([text], [text]) == pytest.approx(1.0, abs=1e-6)

    def test_bleu_with_unicode_text(self):
        text = "Café français est très bon"

        assert compute_bleu([text], [text]) == pytest.approx(1.0, abs=1e-6)


class TestClassificationMetrics:
    def test_accuracy(self):
        preds = [1] * 80 + [0] * 20
        targets = [1] * 100

        assert compute_accuracy(preds, targets) == pytest.approx(0.8)

    def test_accuracy_empty_is_zero(self):
        assert compute_accuracy([], []) == 0.0

    def test_accuracy_length_mismatch_raises(self):
        with pytest.raises(ValueError):
            compute_accuracy([1, 0], [1])

    def test_f1_micro_matches_formula(self):
        preds = [0, 1, 1, 0, 1]
        targets = [0, 1, 0, 0, 0]
        # micro over all labels: tp=3, fp=2, fn=2 -> f1 = 0.6
        assert compute_f1(preds, targets) == pytest.approx(0.6)

    def test_f1_macro(self):
        preds = [0, 1, 1, 0]
        targets = [0, 1, 0, 0]
        # class 0: tp=2 fp=0 fn=1 -> 0.8 ; class 1: tp=1 fp=1 fn=0 -> 2/3
        assert compute_f1(preds, targets, average="macro") == pytest.approx((0.8 + 2 / 3) / 2)

    def test_f1_invalid_average(self):
        with pytest.raises(ValueError, match="invalid average"):
            compute_f1([0], [0], average="bogus")

    def test_classification_metrics_bundle(self):
        result = compute_classification_metrics([0, 1, 1], [0, 1, 0])

        assert set(result) == {"accuracy", "f1_micro", "f1_macro"}
        assert result["accuracy"] == pytest.approx(2 / 3)


class TestMetricsEdgeCases:
    def test_bleu_none_inputs_raise(self):
        with pytest.raises(TypeError):
            compute_bleu(None, None)  # type: ignore[arg-type]

    def test_bleu_empty_strings_score_zero(self):
        assert compute_bleu([""], [""]) == 0.0

    def test_bleu_very_long_text(self):
        long_text = " ".join(f"w{i}" for i in range(1000))

        assert compute_bleu([long_text], [long_text]) == pytest.approx(1.0, abs=1e-6)

    def test_metric_consistency_across_calls(self):
        args = (["test hypothesis here"], ["test reference here"])

        assert compute_bleu(*args) == compute_bleu(*args)
        assert compute_rouge_l(*args) == compute_rouge_l(*args)

    def test_token_accuracy_uses_argmax_of_logits(self):
        logits = [[0.1, 0.9], [0.8, 0.2], [0.3, 0.7]]  # argmax -> [1, 0, 1]

        assert compute_token_accuracy(logits, [1, 0, 0]) == pytest.approx(2 / 3)
