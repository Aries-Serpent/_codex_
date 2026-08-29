"""
Test Metrics Base (metrics_base.py)

Comprehensive unit tests for the binary classification metrics in metrics_base.py.
Tests accuracy, perplexity, precision, recall, and f1_score.
"""

from __future__ import annotations

import math

from codex_ml.metrics_base import accuracy, f1_score, perplexity, precision, recall


class TestAccuracy:
    """Tests for accuracy function in metrics_base."""

    def test_perfect_accuracy(self) -> None:
        preds = [1, 0, 1, 0]
        labels = [1, 0, 1, 0]
        assert accuracy(preds, labels) == 1.0

    def test_zero_accuracy(self) -> None:
        preds = [1, 1, 1, 1]
        labels = [0, 0, 0, 0]
        assert accuracy(preds, labels) == 0.0

    def test_partial_accuracy(self) -> None:
        preds = [1, 0, 1, 0]
        labels = [1, 1, 0, 0]
        assert accuracy(preds, labels) == 0.5

    def test_with_generators(self) -> None:
        # Should work with any iterable
        preds = iter([1, 0, 1, 0])
        labels = iter([1, 0, 1, 0])
        assert accuracy(preds, labels) == 1.0

    def test_empty_inputs(self) -> None:
        # Empty inputs should return 0.0 (total becomes max(1, 0) = 1)
        assert accuracy([], []) == 0.0

    def test_single_element(self) -> None:
        assert accuracy([1], [1]) == 1.0
        assert accuracy([0], [1]) == 0.0


class TestPerplexity:
    """Tests for perplexity function."""

    def test_zero_loss(self) -> None:
        # exp(0) = 1
        assert perplexity(0.0) == 1.0, "Condition must be true"

    def test_positive_loss(self) -> None:
        # exp(1) ≈ 2.718
        result = perplexity(1.0)
        assert abs(result - math.e) < 1e-6, "Result must not be empty"

    def test_large_loss(self) -> None:
        # exp(2) ≈ 7.389
        result = perplexity(2.0)
        assert abs(result - math.exp(2)) < 1e-6, "Result must not be empty"

    def test_negative_loss(self) -> None:
        # exp(-1) ≈ 0.368
        result = perplexity(-1.0)
        assert abs(result - math.exp(-1)) < 1e-6, "Result must not be empty"


class TestPrecision:
    """Tests for precision function in metrics_base."""

    def test_perfect_precision(self) -> None:
        preds = [1, 1, 0, 0]
        labels = [1, 1, 0, 0]
        assert precision(preds, labels) == 1.0

    def test_zero_precision(self) -> None:
        preds = [1, 1, 1, 1]
        labels = [0, 0, 0, 0]
        assert precision(preds, labels) == 0.0

    def test_partial_precision(self) -> None:
        preds = [1, 1, 0, 0]
        labels = [1, 0, 0, 0]
        # 1 true positive, 2 predicted positive
        assert precision(preds, labels) == 0.5

    def test_no_positive_predictions(self) -> None:
        preds = [0, 0, 0, 0]
        labels = [1, 1, 1, 1]
        # No positive predictions, precision is 0
        assert precision(preds, labels) == 0.0

    def test_boolean_coercion(self) -> None:
        # Non-zero values should be treated as 1
        preds = [2, 3, 0, 0]
        labels = [1, 0, 0, 0]
        result = precision(preds, labels)
        assert result == 0.5, "Result must not be empty"


class TestRecall:
    """Tests for recall function in metrics_base."""

    def test_perfect_recall(self) -> None:
        preds = [1, 1, 1, 1]
        labels = [1, 1, 0, 0]
        assert recall(preds, labels) == 1.0

    def test_zero_recall(self) -> None:
        preds = [0, 0, 0, 0]
        labels = [1, 1, 1, 1]
        assert recall(preds, labels) == 0.0

    def test_partial_recall(self) -> None:
        preds = [1, 0, 0, 0]
        labels = [1, 1, 0, 0]
        # 1 true positive, 2 actual positives
        assert recall(preds, labels) == 0.5

    def test_no_positive_labels(self) -> None:
        preds = [1, 1, 1, 1]
        labels = [0, 0, 0, 0]
        # No positive labels, recall is 0
        assert recall(preds, labels) == 0.0

    def test_boolean_coercion(self) -> None:
        preds = [2, 0, 0, 0]
        labels = [1, 1, 0, 0]
        result = recall(preds, labels)
        assert result == 0.5, "Result must not be empty"


class TestF1Score:
    """Tests for f1_score function in metrics_base."""

    def test_perfect_f1(self) -> None:
        preds = [1, 1, 0, 0]
        labels = [1, 1, 0, 0]
        assert f1_score(preds, labels) == 1.0

    def test_zero_f1_no_predictions(self) -> None:
        preds = [0, 0, 0, 0]
        labels = [1, 1, 1, 1]
        assert f1_score(preds, labels) == 0.0

    def test_zero_f1_no_labels(self) -> None:
        preds = [1, 1, 1, 1]
        labels = [0, 0, 0, 0]
        assert f1_score(preds, labels) == 0.0

    def test_partial_f1(self) -> None:
        preds = [1, 1, 0, 0]
        labels = [1, 0, 1, 0]
        # Precision = 1/2, Recall = 1/2
        # F1 = 2 * 0.5 * 0.5 / 1.0 = 0.5
        result = f1_score(preds, labels)
        assert abs(result - 0.5) < 1e-6, "Result must not be empty"

    def test_f1_formula(self) -> None:
        # Test that F1 = 2 * P * R / (P + R)
        preds = [1, 1, 1, 0]
        labels = [1, 1, 0, 0]
        # TP=2, FP=1, FN=0
        # Precision = 2/3, Recall = 1.0
        # F1 = 2 * (2/3) * 1.0 / (2/3 + 1.0) = (4/3) / (5/3) = 4/5 = 0.8
        result = f1_score(preds, labels)
        assert abs(result - 0.8) < 1e-6, "Result must not be empty"


class TestEdgeCases:
    """Edge case tests for metrics_base functions."""

    def test_mismatched_lengths(self) -> None:
        # zip(strict=False) allows different lengths
        preds = [1, 0, 1]
        labels = [1, 0]
        # Should compute on the shorter length
        result = accuracy(preds, labels)
        assert result == 1.0, "Result must not be empty"

    def test_large_inputs(self) -> None:
        preds = [1] * 1000 + [0] * 1000
        labels = [1] * 1000 + [0] * 1000
        assert accuracy(preds, labels) == 1.0

    def test_all_module_exports(self) -> None:
        from codex_ml import metrics_base

        expected_exports = ["accuracy", "perplexity", "precision", "recall", "f1_score"]
        for name in expected_exports:
            assert name in metrics_base.__all__, "Condition must be true"
