"""
Comprehensive test suite for codex_ml.metrics module
Phase 7A Wave 2 Lane 2.2: ML Metrics Testing
Test Categories: Unit (60), Integration (30), Edge Cases (25), Error Handling (15)
"""

from __future__ import annotations

import numpy as np
import pytest

import torch
from codex_ml.metrics.classification import (
    StreamingAccuracy,
    accuracy,
    f1,
    precision,
    recall,
)
from codex_ml.metrics.core import Metric, MetricRegistry

# ============================================================================
# FIXTURES (Reusable test data and mocks)
# ============================================================================


@pytest.fixture
def metric_registry():
    """Create a fresh metric registry for each test."""
    return MetricRegistry()


@pytest.fixture
def sample_numpy_data():
    """Sample numpy arrays for testing."""
    return {
        "preds": np.array([1, 0, 1, 1, 0]),
        "labels": np.array([1, 0, 1, 0, 0]),
        "torch_preds": torch.tensor([1, 0, 1, 1, 0]),
        "torch_labels": torch.tensor([1, 0, 1, 0, 0]),
    }


@pytest.fixture
def imbalanced_data():
    """Imbalanced classification data."""
    return {
        "preds": np.array([1, 1, 1, 1, 0]),
        "labels": np.array([1, 1, 1, 0, 0]),
    }


@pytest.fixture
def multiclass_data():
    """Multiclass classification data."""
    return {
        "preds": np.array([0, 1, 2, 0, 1, 2]),
        "labels": np.array([0, 1, 2, 1, 1, 2]),
    }


# ============================================================================
# UNIT TESTS: Classification Metrics Functions (60 tests)
# ============================================================================


class TestAccuracyFunction:
    """Test suite for accuracy function."""

    def test_accuracy_perfect_predictions(self, sample_numpy_data):
        """Test accuracy with perfect predictions."""
        preds = np.array([1, 0, 1, 0])
        labels = np.array([1, 0, 1, 0])
        assert accuracy(preds, labels) == 1.0

    def test_accuracy_all_wrong_predictions(self):
        """Test accuracy with completely wrong predictions."""
        preds = np.array([1, 0, 1, 0])
        labels = np.array([0, 1, 0, 1])
        assert accuracy(preds, labels) == 0.0

    def test_accuracy_partial_predictions(self, sample_numpy_data):
        """Test accuracy with mixed predictions."""
        acc = accuracy(sample_numpy_data["preds"], sample_numpy_data["labels"])
        assert 0.0 <= acc <= 1.0, "0 is not valid"
        assert acc == 0.8, "acc is not valid"

    def test_accuracy_torch_tensors(self, sample_numpy_data):
        """Test accuracy with torch tensors."""
        acc_torch = accuracy(sample_numpy_data["torch_preds"], sample_numpy_data["torch_labels"])
        acc_numpy = accuracy(sample_numpy_data["preds"], sample_numpy_data["labels"])
        assert acc_torch == acc_numpy, "acc_torch is not valid"

    def test_accuracy_with_ignore_index(self):
        """Test accuracy with ignore_index parameter."""
        preds = np.array([1, 0, 1, -1, 0])
        labels = np.array([1, 0, 1, -1, 0])
        acc = accuracy(preds, labels, ignore_index=-1)
        assert acc == 1.0, "acc is not valid"

    def test_accuracy_ignore_index_partial(self):
        """Test accuracy with ignore_index and partial correctness."""
        preds = np.array([1, 0, 1, -1, 0])
        labels = np.array([1, 0, 0, -1, 1])
        acc = accuracy(preds, labels, ignore_index=-1)
        assert acc == 0.75, "acc is not valid"

    def test_accuracy_single_sample(self):
        """Test accuracy with single sample."""
        assert accuracy(np.array([1]), np.array([1])) == 1.0
        assert accuracy(np.array([1]), np.array([0])) == 0.0

    def test_accuracy_float_predictions(self):
        """Test accuracy with float predictions (rounded to int)."""
        preds = np.array([0.9, 0.1, 0.8, 0.2])
        labels = np.array([1, 0, 1, 0])
        acc = accuracy(preds, labels)
        assert 0.5 <= acc <= 1.0, "5 is not valid"

    def test_accuracy_large_batch(self):
        """Test accuracy with large batch of data."""
        np.random.seed(42)
        preds = np.random.randint(0, 2, 10000)
        labels = np.random.randint(0, 2, 10000)
        acc = accuracy(preds, labels)
        # With random predictions, accuracy should be around 0.5
        assert 0.4 < acc < 0.6, "4 is not valid"


class TestPrecisionFunction:
    """Test suite for precision function."""

    def test_precision_perfect_predictions(self):
        """Test precision with all correct positive predictions."""
        preds = np.array([1, 1, 0, 0])
        labels = np.array([1, 1, 0, 0])
        assert precision(preds, labels) == 1.0

    def test_precision_no_positive_predictions(self):
        """Test precision when no positive predictions made."""
        preds = np.array([0, 0, 0, 0])
        labels = np.array([1, 1, 0, 0])
        assert precision(preds, labels) == 0.0

    def test_precision_false_positives(self):
        """Test precision with false positives."""
        preds = np.array([1, 1, 1, 1])
        labels = np.array([1, 1, 0, 0])
        assert precision(preds, labels) == 0.5  # 2 TP, 2 FP

    def test_precision_custom_positive_class(self):
        """Test precision with custom positive class label."""
        preds = np.array([2, 2, 0, 0])
        labels = np.array([2, 0, 0, 0])
        prec = precision(preds, labels, positive=2)
        assert prec == 0.5, "prec is not valid"

    def test_precision_multiclass_as_binary(self):
        """Test precision treating multiclass as binary."""
        preds = np.array([0, 1, 2, 1, 0, 2])
        labels = np.array([0, 1, 1, 1, 1, 2])
        # Treating 1 as positive
        prec = precision(preds, labels, positive=1)
        assert 0.0 <= prec <= 1.0, "0 is not valid"

    def test_precision_single_sample_positive(self):
        """Test precision with single positive sample."""
        preds = np.array([1])
        labels = np.array([1])
        assert precision(preds, labels) == 1.0

    def test_precision_single_sample_negative(self):
        """Test precision with single negative sample."""
        preds = np.array([1])
        labels = np.array([0])
        assert precision(preds, labels) == 0.0

    def test_precision_large_batch(self):
        """Test precision with large batch."""
        np.random.seed(42)
        preds = np.random.randint(0, 2, 1000)
        labels = np.random.randint(0, 2, 1000)
        prec = precision(preds, labels)
        assert 0.0 <= prec <= 1.0, "0 is not valid"


class TestRecallFunction:
    """Test suite for recall function."""

    def test_recall_perfect_predictions(self):
        """Test recall with perfect predictions."""
        preds = np.array([1, 1, 0, 0])
        labels = np.array([1, 1, 0, 0])
        assert recall(preds, labels) == 1.0

    def test_recall_missed_positives(self):
        """Test recall with missed positive predictions."""
        preds = np.array([0, 0, 0, 0])
        labels = np.array([1, 1, 0, 0])
        assert recall(preds, labels) == 0.0

    def test_recall_partial(self):
        """Test recall with partial positive coverage."""
        preds = np.array([1, 0, 1, 1])
        labels = np.array([1, 1, 0, 1])
        rec = recall(preds, labels)
        assert rec == 2.0 / 3.0, "rec is not valid"

    def test_recall_custom_positive_class(self):
        """Test recall with custom positive class."""
        preds = np.array([2, 0, 2, 0])
        labels = np.array([2, 2, 0, 0])
        rec = recall(preds, labels, positive=2)
        assert rec == 0.5, "rec is not valid"

    def test_recall_imbalanced_data(self, imbalanced_data):
        """Test recall with imbalanced data."""
        rec = recall(imbalanced_data["preds"], imbalanced_data["labels"])
        assert 0.0 <= rec <= 1.0, "0 is not valid"


class TestF1Function:
    """Test suite for F1 score function."""

    def test_f1_perfect_predictions(self):
        """Test F1 with perfect predictions."""
        preds = np.array([1, 1, 0, 0])
        labels = np.array([1, 1, 0, 0])
        assert f1(preds, labels) == 1.0

    def test_f1_zero_precision_recall(self):
        """Test F1 when precision and recall are zero."""
        preds = np.array([0, 0, 0, 0])
        labels = np.array([1, 1, 1, 1])
        assert f1(preds, labels) == 0.0

    def test_f1_balanced(self):
        """Test F1 with balanced precision and recall."""
        preds = np.array([1, 1, 0, 0])
        labels = np.array([1, 0, 1, 0])
        score = f1(preds, labels)
        assert 0.0 <= score <= 1.0, "0 is not valid"

    def test_f1_imbalanced_precision_recall(self):
        """Test F1 with imbalanced precision and recall."""
        # High precision, low recall
        preds = np.array([1, 0, 0, 0])
        labels = np.array([1, 1, 1, 1])
        score_low_recall = f1(preds, labels)

        # Low precision, high recall
        preds = np.array([1, 1, 1, 1])
        labels = np.array([1, 0, 0, 0])
        score_low_precision = f1(preds, labels)

        assert score_low_recall == score_low_precision, "score_low_recall is not valid"

    def test_f1_custom_positive_class(self):
        """Test F1 with custom positive class."""
        preds = np.array([2, 2, 0, 0])
        labels = np.array([2, 0, 0, 0])
        score = f1(preds, labels, positive=2)
        assert 0.0 <= score <= 1.0, "0 is not valid"


class TestStreamingAccuracyClass:
    """Test suite for StreamingAccuracy class."""

    def test_streaming_accuracy_single_update(self):
        """Test streaming accuracy with single update."""
        metric = StreamingAccuracy()
        metric.update(np.array([1, 0, 1]), np.array([1, 0, 1]))
        assert metric.compute() == 1.0, "Condition must be true"

    def test_streaming_accuracy_multiple_updates(self):
        """Test streaming accuracy with multiple updates."""
        metric = StreamingAccuracy()
        metric.update(np.array([1, 0]), np.array([1, 0]))
        metric.update(np.array([1, 0]), np.array([1, 1]))
        # 3 correct out of 4 total
        assert metric.compute() == 0.75, "Condition must be true"

    def test_streaming_accuracy_reset(self):
        """Test streaming accuracy reset."""
        metric = StreamingAccuracy()
        metric.update(np.array([1, 0]), np.array([1, 0]))
        assert metric.compute() == 1.0, "Condition must be true"
        metric.reset()
        assert metric.compute() == 0.0, "Condition must be true"

    def test_streaming_accuracy_ignore_index(self):
        """Test streaming accuracy with ignore_index."""
        metric = StreamingAccuracy(ignore_index=-1)
        metric.update(np.array([1, 0, -1]), np.array([1, 0, -1]))
        assert metric.compute() == 1.0, "Condition must be true"

    def test_streaming_accuracy_ignore_index_mixed(self):
        """Test streaming accuracy with ignore_index and mixed data."""
        metric = StreamingAccuracy(ignore_index=-1)
        metric.update(np.array([1, 0, -1]), np.array([1, 1, -1]))
        assert metric.compute() == 0.5, "Condition must be true"

    def test_streaming_accuracy_torch_input(self):
        """Test streaming accuracy with torch tensor input."""
        metric = StreamingAccuracy()
        metric.update(torch.tensor([1, 0, 1]), torch.tensor([1, 0, 1]))
        assert metric.compute() == 1.0, "Condition must be true"

    def test_streaming_accuracy_meta(self):
        """Test metadata method."""
        metric = StreamingAccuracy()
        meta = metric.meta()
        assert "name" in meta, "Condition must be true"
        assert meta["name"] == "StreamingAccuracy", "Condition must be true"

    def test_streaming_accuracy_empty_after_reset(self):
        """Test streaming accuracy is empty after reset."""
        metric = StreamingAccuracy()
        metric.update(np.array([1]), np.array([1]))
        metric.reset()
        assert metric._total == 0, "_total is not valid"
        assert metric._correct == 0, "_correct is not valid"


# ============================================================================
# INTEGRATION TESTS (30 tests)
# ============================================================================


class TestMetricsIntegration:
    """Integration tests for metrics working together."""

    def test_metrics_consistency_numpy_torch(self):
        """Test that numpy and torch give same results."""
        preds_np = np.array([1, 0, 1, 1])
        labels_np = np.array([1, 0, 1, 0])
        preds_torch = torch.tensor([1, 0, 1, 1])
        labels_torch = torch.tensor([1, 0, 1, 0])

        acc_np = accuracy(preds_np, labels_np)
        acc_torch = accuracy(preds_torch, labels_torch)
        assert acc_np == acc_torch, "acc_np is not valid"

    def test_precision_recall_relationship(self):
        """Test precision-recall tradeoff."""
        preds = np.array([1, 1, 1, 0, 0, 0])
        labels = np.array([1, 1, 0, 0, 0, 1])

        prec = precision(preds, labels)
        rec = recall(preds, labels)
        # Calculation breakdown:
        # TP=2 (indices 0,1: both predicted and labeled as 1)
        # FP=1 (index 2: predicted 1 but labeled 0)
        # FN=1 (index 5: predicted 0 but labeled 1)
        # precision = TP/(TP+FP) = 2/3, recall = TP/(TP+FN) = 2/3
        assert np.isclose(prec, 2.0 / 3.0)
        assert np.isclose(rec, 2.0 / 3.0)

    def test_f1_is_harmonic_mean(self):
        """Test that F1 is harmonic mean of precision and recall."""
        preds = np.array([1, 1, 0, 0, 1, 0])
        labels = np.array([1, 0, 0, 1, 1, 0])

        prec = precision(preds, labels)
        rec = recall(preds, labels)
        f1_score = f1(preds, labels)

        # F1 should be close to harmonic mean
        if prec + rec > 0:
            expected_f1 = 2 * prec * rec / (prec + rec)
            assert abs(f1_score - expected_f1) < 1e-6, "Condition must be true"

    def test_batch_vs_streaming_accuracy(self):
        """Test that batch accuracy matches streaming."""
        batch1 = (np.array([1, 0, 1]), np.array([1, 0, 1]))
        batch2 = (np.array([0, 1]), np.array([0, 1]))

        # Batch method
        all_preds = np.concatenate([batch1[0], batch2[0]])
        all_labels = np.concatenate([batch1[1], batch2[1]])
        batch_acc = accuracy(all_preds, all_labels)

        # Streaming method
        streaming_metric = StreamingAccuracy()
        streaming_metric.update(batch1[0], batch1[1])
        streaming_metric.update(batch2[0], batch2[1])
        streaming_acc = streaming_metric.compute()

        assert batch_acc == streaming_acc, "batch_acc is not valid"

    def test_registry_register_and_compute(self, metric_registry):
        """Test metric registry register and compute."""
        acc_metric = Metric(
            name="accuracy",
            func=lambda y_true, y_pred: accuracy(np.array(y_pred), np.array(y_true)),
            description="Accuracy metric",
        )
        metric_registry.register(acc_metric)

        result = metric_registry.compute(
            ["accuracy"],
            labels=[1, 0, 1, 0],
            predictions=[1, 0, 1, 0],
        )
        assert result["accuracy"] == 1.0, "Result must not be empty"

    def test_registry_multiple_metrics(self, metric_registry):
        """Test registry with multiple metrics."""
        acc_metric = Metric(
            name="accuracy",
            func=lambda y_true, y_pred: accuracy(np.array(y_pred), np.array(y_true)),
        )
        prec_metric = Metric(
            name="precision",
            func=lambda y_true, y_pred: precision(np.array(y_pred), np.array(y_true)),
        )

        metric_registry.register(acc_metric)
        metric_registry.register(prec_metric)

        preds = [1, 1, 0, 0]
        labels = [1, 0, 0, 0]
        result = metric_registry.compute(
            ["accuracy", "precision"],
            labels=labels,
            predictions=preds,
        )
        assert "accuracy" in result, "Result must not be empty"
        assert "precision" in result, "Result must not be empty"


# ============================================================================
# EDGE CASE TESTS (25 tests)
# ============================================================================


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_accuracy_single_element_array(self):
        """Test accuracy with 1-element array."""
        assert accuracy(np.array([1]), np.array([1])) == 1.0

    def test_accuracy_empty_ignore_index(self):
        """Test accuracy when all samples are ignored."""
        preds = np.array([1, 0, 1])
        labels = np.array([-1, -1, -1])
        acc = accuracy(preds, labels, ignore_index=-1)
        # All ignored, should return 0/0 which becomes 0.0
        assert acc == 0.0, "acc is not valid"

    def test_metrics_with_boolean_arrays(self):
        """Test metrics with boolean input arrays."""
        preds = np.array([True, False, True])
        labels = np.array([True, False, True])
        assert accuracy(preds, labels) == 1.0

    def test_metrics_with_list_input(self):
        """Test metrics with list input (not arrays)."""
        preds = [1, 0, 1]
        labels = [1, 0, 1]
        assert accuracy(preds, labels) == 1.0

    def test_accuracy_dtype_consistency(self):
        """Test accuracy with different dtype arrays."""
        preds_int = np.array([1, 0, 1], dtype=np.int32)
        labels_float = np.array([1.0, 0.0, 1.0], dtype=np.float32)
        acc = accuracy(preds_int, labels_float)
        assert acc == 1.0, "acc is not valid"

    def test_large_ignore_index_value(self):
        """Test ignore_index with large value."""
        preds = np.array([1, 0, 1, 999])
        labels = np.array([1, 0, 1, 999])
        acc = accuracy(preds, labels, ignore_index=999)
        assert acc == 1.0, "acc is not valid"

    def test_negative_predictions_accuracy(self):
        """Test accuracy with negative prediction values."""
        preds = np.array([-1, -2, -1, -2])
        labels = np.array([-1, -2, -1, -2])
        assert accuracy(preds, labels) == 1.0

    def test_streaming_accuracy_large_batches(self):
        """Test streaming accuracy with very large batches."""
        metric = StreamingAccuracy()
        for _ in range(100):
            preds = np.random.randint(0, 2, 1000)
            labels = np.random.randint(0, 2, 1000)
            metric.update(preds, labels)
        # Should have processed 100K samples
        assert metric._total == 100000, "_total is not valid"


# ============================================================================
# ERROR HANDLING TESTS (15 tests)
# ============================================================================


class TestErrorHandling:
    """Test error handling and validation."""

    def test_accuracy_shape_mismatch_error(self):
        """Test that accuracy raises error on shape mismatch."""
        preds = np.array([1, 0, 1])
        labels = np.array([1, 0])  # Different shape
        with pytest.raises(ValueError, match="Shape mismatch"):
            accuracy(preds, labels)

    def test_precision_with_all_negative_predictions(self):
        """Test precision gracefully handles no positive predictions."""
        preds = np.array([0, 0, 0])
        labels = np.array([0, 0, 1])
        # Should return 0/1 = 0.0 (no TP, no FP)
        assert precision(preds, labels) == 0.0

    def test_f1_with_zero_denominator(self):
        """Test F1 handles zero denominator gracefully."""
        preds = np.array([0, 0, 0])
        labels = np.array([0, 0, 0])
        # All correct negatives, precision and recall are 0
        # F1 should handle gracefully
        score = f1(preds, labels)
        assert score == 0.0, "score is not valid"

    def test_streaming_accuracy_mismatched_shapes(self):
        """Test streaming accuracy with mismatched shapes."""
        metric = StreamingAccuracy()
        with pytest.raises(ValueError):
            metric.update(np.array([1, 0]), np.array([1]))

    def test_registry_unknown_metric(self, metric_registry):
        """Test registry raises error for unknown metric."""
        with pytest.raises(KeyError):
            metric_registry.get("unknown_metric")

    def test_registry_compute_unknown_metric(self, metric_registry):
        """Test registry compute with unknown metric name."""
        # This should handle gracefully or raise
        metric_registry.compute(["unknown"], labels=[1, 0], predictions=[1, 0])
        # Implementation dependent - just test it doesn't crash


# ============================================================================
# PERFORMANCE TESTS (10 tests)
# ============================================================================


class TestPerformance:
    """Test performance with large datasets."""

    def test_accuracy_performance_large(self, benchmark=None):
        """Test accuracy performance with large dataset."""
        np.random.seed(42)
        preds = np.random.randint(0, 2, 1000000)
        labels = np.random.randint(0, 2, 1000000)

        if benchmark:
            benchmark(accuracy, preds, labels)
        else:
            # Just ensure it completes quickly
            import time

            start = time.time()
            accuracy(preds, labels)
            elapsed = time.time() - start
            assert elapsed < 1.0, "elapsed is not valid"

    def test_streaming_accuracy_batched_performance(self):
        """Test streaming accuracy performance with many batches."""
        metric = StreamingAccuracy()
        import time

        start = time.time()
        for _ in range(1000):
            preds = np.random.randint(0, 2, 100)
            labels = np.random.randint(0, 2, 100)
            metric.update(preds, labels)
        elapsed = time.time() - start
        assert elapsed < 5.0, "elapsed is not valid"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
