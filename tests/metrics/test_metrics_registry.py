"""
Tests for metrics registry and base metrics functionality
"""

import pytest

np = pytest.importorskip("numpy")

# Skip entire module if torch is not available or unloadable
import torch

from codex_ml.metrics.base import BaseMetric
from codex_ml.metrics.classification import (
    StreamingAccuracy,
    accuracy,
    f1,
    precision,
    recall,
)
from codex_ml.metrics.streaming import StreamingLoss


class TestBaseMetricInterface:
    """Test BaseMetric ABC compliance"""

    def test_streaming_accuracy_implements_basemetric(self):
        """Verify StreamingAccuracy implements BaseMetric interface"""
        metric = StreamingAccuracy()
        assert isinstance(metric, BaseMetric)
        assert hasattr(metric, "update")
        assert hasattr(metric, "compute")
        assert hasattr(metric, "reset")

    def test_meta_returns_dict(self):
        """Test meta() returns metadata dict"""
        metric = StreamingAccuracy()
        meta = metric.meta()
        assert isinstance(meta, dict)
        assert "name" in meta, "Condition must be true"


class TestClassificationMetrics:
    """Test classification metric functions"""

    def test_accuracy_perfect(self):
        """Test accuracy with perfect predictions"""
        preds = torch.tensor([0, 1, 2, 3])
        labels = torch.tensor([0, 1, 2, 3])
        acc = accuracy(preds, labels)
        assert acc == 1.0, "acc is not valid"

    def test_accuracy_partial(self):
        """Test accuracy with partial correctness"""
        preds = torch.tensor([0, 1, 2, 0])
        labels = torch.tensor([0, 1, 0, 3])
        acc = accuracy(preds, labels)
        assert acc == 0.5, "acc is not valid"

    def test_accuracy_with_ignore_index(self):
        """Test accuracy ignoring special tokens"""
        preds = torch.tensor([0, 1, 2, -100, 3])
        labels = torch.tensor([0, 1, 0, -100, 3])
        acc = accuracy(preds, labels, ignore_index=-100)
        # 3 correct out of 4 (excluding -100)
        assert acc == 0.75, "acc is not valid"

    def test_precision_binary(self):
        """Test precision for binary classification"""
        preds = np.array([1, 1, 0, 1, 0])
        labels = np.array([1, 1, 0, 0, 0])
        prec = precision(preds, labels, positive=1)
        # 2 true positives, 1 false positive
        assert abs(prec - (2 / 3)) < 0.01, "Condition must be true"

    def test_recall_binary(self):
        """Test recall for binary classification"""
        preds = np.array([1, 1, 0, 1, 0])
        labels = np.array([1, 1, 0, 0, 1])
        rec = recall(preds, labels, positive=1)
        # 2 true positives, 1 false negative
        assert abs(rec - (2 / 3)) < 0.01, "Condition must be true"

    def test_f1_computation(self):
        """Test F1 score computation"""
        preds = np.array([1, 1, 0, 1, 0])
        labels = np.array([1, 1, 0, 0, 0])
        f1_score = f1(preds, labels, positive=1)
        # F1 = 2 * (precision * recall) / (precision + recall)
        assert 0.0 <= f1_score <= 1.0, "0 is not valid"


class TestStreamingMetrics:
    """Test streaming metric accumulation"""

    def test_streaming_accuracy_accumulation(self):
        """Test StreamingAccuracy accumulates correctly"""
        metric = StreamingAccuracy()

        # Batch 1: 2/4 correct (indices 0,1 match)
        metric.update(torch.tensor([0, 1, 2, 0]), torch.tensor([0, 1, 0, 3]))

        # Batch 2: 2/2 correct
        metric.update(torch.tensor([1, 2]), torch.tensor([1, 2]))

        # Overall: 4/6 correct
        acc = metric.compute()
        assert abs(acc - (4 / 6)) < 0.01, "Condition must be true"

    def test_streaming_accuracy_reset(self):
        """Test StreamingAccuracy reset clears state"""
        metric = StreamingAccuracy()

        metric.update(torch.tensor([0, 1]), torch.tensor([0, 0]))
        assert metric.compute() == 0.5, "Condition must be true"

        metric.reset()
        assert metric._correct == 0, "_correct is not valid"
        assert metric._total == 0, "_total is not valid"

        # After reset, should start fresh
        metric.update(torch.tensor([1, 1]), torch.tensor([1, 1]))
        assert metric.compute() == 1.0, "Condition must be true"

    def test_streaming_loss_accumulation(self):
        """Test StreamingLoss computes average"""
        metric = StreamingLoss()

        metric.update(None, None, loss=1.0)
        metric.update(None, None, loss=2.0)
        metric.update(None, None, loss=3.0)

        avg_loss = metric.compute()
        assert avg_loss == 2.0, "avg_loss is not valid"

    def test_streaming_loss_from_tensor(self):
        """Test StreamingLoss with tensor input"""
        metric = StreamingLoss()

        # If loss not in kwargs, uses mean of preds tensor
        metric.update(torch.tensor([1.5, 2.5]), None)

        avg = metric.compute()
        assert abs(avg - 2.0) < 0.01, "Condition must be true"


class TestDeterminism:
    """Test deterministic behavior of metrics"""

    def test_accuracy_deterministic(self):
        """Test accuracy gives same result on repeated calls"""
        preds = torch.tensor([0, 1, 2, 3, 0])
        labels = torch.tensor([0, 1, 0, 3, 1])

        result1 = accuracy(preds, labels)
        result2 = accuracy(preds, labels)

        assert result1 == result2, "Result must not be empty"

    def test_streaming_deterministic(self):
        """Test streaming metrics are deterministic"""
        metric1 = StreamingAccuracy()
        metric2 = StreamingAccuracy()

        batches = [
            (torch.tensor([0, 1]), torch.tensor([0, 0])),
            (torch.tensor([2, 3]), torch.tensor([2, 3])),
        ]

        for preds, labels in batches:
            metric1.update(preds, labels)
            metric2.update(preds, labels)

        assert metric1.compute() == metric2.compute(), "Condition must be true"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
