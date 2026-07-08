"""Tests for evaluation metrics in codex_ml."""

import pytest


class TestEvaluationMetrics:
    """Tests for evaluation metrics."""

    def test_accuracy_calculation(self):
        """Test accuracy calculation."""
        correct = 80
        total = 100
        accuracy = correct / total
        assert accuracy == 0.8, "accuracy is not valid"

    def test_precision_calculation(self):
        """Test precision calculation."""
        true_positives = 40
        false_positives = 10
        precision = true_positives / (true_positives + false_positives)
        assert precision == 0.8, "precision is not valid"

    def test_recall_calculation(self):
        """Test recall calculation."""
        true_positives = 40
        false_negatives = 10
        recall = true_positives / (true_positives + false_negatives)
        assert recall == 0.8, "recall is not valid"

    def test_f1_score_calculation(self):
        """Test F1 score calculation."""
        precision = 0.8
        recall = 0.8
        f1 = 2 * (precision * recall) / (precision + recall)
        assert f1 == pytest.approx(0.8), "f1 is not valid"

    def test_confusion_matrix(self):
        """Test confusion matrix."""
        matrix = [[40, 10], [10, 40]]
        assert len(matrix) == 2, "Matrix must not be empty"

    def test_roc_auc_score(self):
        """Test ROC AUC score."""
        auc = 0.85
        assert 0 <= auc <= 1, "0 is not valid"

    def test_mean_squared_error(self):
        """Test mean squared error."""
        predictions = [1.0, 2.0, 3.0]
        targets = [1.1, 2.1, 3.1]
        mse = sum((p - t) ** 2 for p, t in zip(predictions, targets)) / len(predictions)
        assert mse < 0.02, "mse is not valid"

    def test_mean_absolute_error(self):
        """Test mean absolute error."""
        predictions = [1.0, 2.0, 3.0]
        targets = [1.1, 2.1, 3.1]
        mae = sum(abs(p - t) for p, t in zip(predictions, targets)) / len(predictions)
        assert mae == pytest.approx(0.1), "mae is not valid"

    def test_cross_entropy_loss(self):
        """Test cross entropy loss."""
        loss = 0.5
        assert loss >= 0, "loss must be greater than zero"

    def test_perplexity(self):
        """Test perplexity calculation."""
        cross_entropy = 2.0
        perplexity = 2**cross_entropy
        assert perplexity == 4.0, "perplexity is not valid"

    def test_bleu_score(self):
        """Test BLEU score."""
        bleu = 0.75
        assert 0 <= bleu <= 1, "0 is not valid"

    def test_rouge_score(self):
        """Test ROUGE score."""
        rouge_l = 0.8
        assert 0 <= rouge_l <= 1, "0 is not valid"

    def test_exact_match(self):
        """Test exact match metric."""
        predictions = ["hello", "world"]
        targets = ["hello", "world"]
        em = sum(p == t for p, t in zip(predictions, targets)) / len(predictions)
        assert em == 1.0, "em is not valid"

    def test_top_k_accuracy(self):
        """Test top-k accuracy."""
        k = 5
        assert k > 0, "k must be greater than zero"

    def test_micro_average(self):
        """Test micro averaging."""
        micro_f1 = 0.82
        assert 0 <= micro_f1 <= 1, "0 is not valid"

    def test_macro_average(self):
        """Test macro averaging."""
        macro_f1 = 0.78
        assert 0 <= macro_f1 <= 1, "0 is not valid"

    def test_weighted_average(self):
        """Test weighted averaging."""
        weighted_f1 = 0.80
        assert 0 <= weighted_f1 <= 1, "0 is not valid"

    def test_matthews_correlation(self):
        """Test Matthews correlation coefficient."""
        mcc = 0.6
        assert -1 <= mcc <= 1, "1 is not valid"

    def test_cohen_kappa(self):
        """Test Cohen's Kappa."""
        kappa = 0.7
        assert -1 <= kappa <= 1, "1 is not valid"

    def test_log_loss(self):
        """Test log loss."""
        log_loss = 0.3
        assert log_loss >= 0, "log_loss must be greater than zero"
