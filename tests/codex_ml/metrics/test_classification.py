"""
Test Classification Metrics

Comprehensive unit tests for the classification metrics module.
Tests accuracy, precision, recall, F1 score, and StreamingAccuracy.
"""

from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("numpy")


# Skip if torch not available
torch = pytest.importorskip("torch")

from codex_ml.metrics.classification import (
    StreamingAccuracy,
    _to_numpy,
    accuracy,
    f1,
    precision,
    recall,
)


class TestToNumpy:
    """Tests for _to_numpy helper function."""

    def test_numpy_array_passthrough(self) -> None:
        arr = np.array([1, 2, 3])
        result = _to_numpy(arr)
        assert isinstance(result, np.ndarray)
        np.testing.assert_array_equal(result, arr)

    def test_torch_tensor_conversion(self) -> None:
        tensor = torch.tensor([1, 2, 3])
        result = _to_numpy(tensor)
        assert isinstance(result, np.ndarray)
        np.testing.assert_array_equal(result, np.array([1, 2, 3]))

    def test_list_conversion(self) -> None:
        lst = [1, 2, 3]
        result = _to_numpy(lst)
        assert isinstance(result, np.ndarray)
        np.testing.assert_array_equal(result, np.array([1, 2, 3]))

    def test_gpu_tensor_to_cpu(self) -> None:
        # Test that GPU tensors are moved to CPU correctly
        tensor = torch.tensor([1.0, 2.0, 3.0])
        result = _to_numpy(tensor)
        assert isinstance(result, np.ndarray)


class TestAccuracy:
    """Tests for accuracy function."""

    def test_perfect_accuracy(self) -> None:
        preds = np.array([1, 0, 1, 0])
        labels = np.array([1, 0, 1, 0])
        assert accuracy(preds, labels) == 1.0

    def test_zero_accuracy(self) -> None:
        preds = np.array([1, 1, 1, 1])
        labels = np.array([0, 0, 0, 0])
        assert accuracy(preds, labels) == 0.0

    def test_partial_accuracy(self) -> None:
        preds = np.array([1, 0, 1, 0])
        labels = np.array([1, 1, 0, 0])
        assert accuracy(preds, labels) == 0.5

    def test_with_ignore_index(self) -> None:
        preds = np.array([1, 0, 1, 0, 1])
        labels = np.array([1, 0, -100, 0, -100])
        result = accuracy(preds, labels, ignore_index=-100)
        # Only 3 valid labels, all correct
        assert result == 1.0, "Result must not be empty"

    def test_ignore_index_partial(self) -> None:
        preds = np.array([1, 0, 1, 1])
        labels = np.array([1, 1, -100, 1])
        result = accuracy(preds, labels, ignore_index=-100)
        # 3 valid: [1==1, 0!=1, 1==1] = 2/3
        assert abs(result - 2 / 3) < 1e-6, "Result must not be empty"

    def test_shape_mismatch_raises(self) -> None:
        preds = np.array([1, 0, 1])
        labels = np.array([1, 0])
        with pytest.raises(ValueError, match="Shape mismatch"):
            accuracy(preds, labels)

    def test_with_torch_tensors(self) -> None:
        preds = torch.tensor([1, 0, 1, 0])
        labels = torch.tensor([1, 0, 1, 0])
        assert accuracy(preds, labels) == 1.0

    def test_empty_tensors(self) -> None:
        # Edge case: empty arrays should return 0.0 (division by max(1, 0))
        preds = np.array([])
        labels = np.array([])
        result = accuracy(preds, labels)
        assert result == 0.0, "Result must not be empty"


class TestPrecision:
    """Tests for precision function."""

    def test_perfect_precision(self) -> None:
        preds = np.array([1, 1, 0, 0])
        labels = np.array([1, 1, 0, 0])
        assert precision(preds, labels) == 1.0

    def test_zero_precision(self) -> None:
        preds = np.array([1, 1, 1, 1])
        labels = np.array([0, 0, 0, 0])
        assert precision(preds, labels) == 0.0

    def test_partial_precision(self) -> None:
        # 2 predicted positive, 1 true positive
        preds = np.array([1, 1, 0, 0])
        labels = np.array([1, 0, 0, 0])
        assert precision(preds, labels) == 0.5

    def test_no_positive_predictions(self) -> None:
        preds = np.array([0, 0, 0, 0])
        labels = np.array([1, 1, 0, 0])
        # No positive predictions, precision should be 0
        assert precision(preds, labels) == 0.0

    def test_custom_positive_label(self) -> None:
        preds = np.array([2, 2, 0, 0])
        labels = np.array([2, 0, 0, 0])
        result = precision(preds, labels, positive=2)
        assert result == 0.5, "Result must not be empty"


class TestRecall:
    """Tests for recall function."""

    def test_perfect_recall(self) -> None:
        preds = np.array([1, 1, 1, 1])
        labels = np.array([1, 1, 0, 0])
        assert recall(preds, labels) == 1.0

    def test_zero_recall(self) -> None:
        preds = np.array([0, 0, 0, 0])
        labels = np.array([1, 1, 1, 1])
        assert recall(preds, labels) == 0.0

    def test_partial_recall(self) -> None:
        preds = np.array([1, 0, 0, 0])
        labels = np.array([1, 1, 0, 0])
        assert recall(preds, labels) == 0.5

    def test_no_positive_labels(self) -> None:
        preds = np.array([1, 1, 1, 1])
        labels = np.array([0, 0, 0, 0])
        # No positive labels, recall should be 0
        assert recall(preds, labels) == 0.0

    def test_custom_positive_label(self) -> None:
        preds = np.array([2, 0, 0, 0])
        labels = np.array([2, 2, 0, 0])
        result = recall(preds, labels, positive=2)
        assert result == 0.5, "Result must not be empty"


class TestF1:
    """Tests for F1 score function."""

    def test_perfect_f1(self) -> None:
        preds = np.array([1, 1, 0, 0])
        labels = np.array([1, 1, 0, 0])
        assert f1(preds, labels) == 1.0

    def test_zero_f1(self) -> None:
        preds = np.array([0, 0, 0, 0])
        labels = np.array([1, 1, 1, 1])
        assert f1(preds, labels) == 0.0

    def test_partial_f1(self) -> None:
        # Precision = 1/2, Recall = 1/2, F1 = 2 * 0.5 * 0.5 / 1.0 = 0.5
        preds = np.array([1, 1, 0, 0])
        labels = np.array([1, 0, 1, 0])
        result = f1(preds, labels)
        assert abs(result - 0.5) < 1e-6, "Result must not be empty"

    def test_custom_positive_label(self) -> None:
        preds = np.array([2, 2, 0, 0])
        labels = np.array([2, 2, 0, 0])
        result = f1(preds, labels, positive=2)
        assert result == 1.0, "Result must not be empty"


class TestStreamingAccuracy:
    """Tests for StreamingAccuracy class."""

    def test_basic_streaming(self) -> None:
        metric = StreamingAccuracy()

        # First batch
        metric.update(np.array([1, 0, 1]), np.array([1, 0, 1]))
        assert metric.compute() == 1.0, "Condition must be true"

        # Second batch (different accuracy)
        metric.update(np.array([1, 1]), np.array([0, 0]))
        # Total: 3 correct out of 5
        assert metric.compute() == 0.6, "Condition must be true"

    def test_reset(self) -> None:
        metric = StreamingAccuracy()
        metric.update(np.array([1, 0]), np.array([1, 0]))
        assert metric.compute() == 1.0, "Condition must be true"

        metric.reset()
        assert metric.compute() == 0.0, "Condition must be true"

    def test_with_ignore_index(self) -> None:
        metric = StreamingAccuracy(ignore_index=-100)
        preds = np.array([1, 0, 1, 0])
        labels = np.array([1, 0, -100, -100])
        metric.update(preds, labels)
        # Only 2 valid labels, both correct
        assert metric.compute() == 1.0, "Condition must be true"

    def test_empty_update(self) -> None:
        metric = StreamingAccuracy()
        assert metric.compute() == 0.0, "Condition must be true"

    def test_with_torch_tensors(self) -> None:
        metric = StreamingAccuracy()
        preds = torch.tensor([1, 0, 1, 0])
        labels = torch.tensor([1, 0, 0, 0])
        metric.update(preds, labels)
        assert metric.compute() == 0.75, "Condition must be true"

    def test_multiple_batches_streaming(self) -> None:
        metric = StreamingAccuracy()

        # Simulate training loop with multiple batches
        batches = [
            (np.array([1, 1, 1]), np.array([1, 1, 0])),  # 2/3 correct
            (np.array([0, 0, 0]), np.array([0, 0, 1])),  # 2/3 correct
            (np.array([1, 0]), np.array([1, 0])),  # 2/2 correct
        ]

        for preds, labels in batches:
            metric.update(preds, labels)

        # Total: 6 correct out of 8
        assert metric.compute() == 0.75, "Condition must be true"
