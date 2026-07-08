"""
Test Streaming Metrics

Comprehensive unit tests for the streaming metrics module.
Tests StreamingLoss class.
"""

from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("numpy")


# Skip if torch not available
torch = pytest.importorskip("torch")

from codex_ml.metrics.streaming import StreamingLoss, _to_numpy


class TestToNumpy:
    """Tests for _to_numpy helper function."""

    def test_numpy_array_passthrough(self) -> None:
        arr = np.array([1.0, 2.0, 3.0])
        result = _to_numpy(arr)
        assert isinstance(result, np.ndarray)
        np.testing.assert_array_equal(result, arr)

    def test_torch_tensor_conversion(self) -> None:
        tensor = torch.tensor([1.0, 2.0, 3.0])
        result = _to_numpy(tensor)
        assert isinstance(result, np.ndarray)
        np.testing.assert_allclose(result, np.array([1.0, 2.0, 3.0]))

    def test_list_conversion(self) -> None:
        lst = [1.0, 2.0, 3.0]
        result = _to_numpy(lst)
        assert isinstance(result, np.ndarray)


class TestStreamingLoss:
    """Tests for StreamingLoss class."""

    def test_basic_loss_accumulation(self) -> None:
        metric = StreamingLoss()

        # Add loss via kwargs
        metric.update(None, None, loss=1.0)
        assert metric.compute() == 1.0, "Condition must be true"

        metric.update(None, None, loss=3.0)
        # Average of 1.0 and 3.0 = 2.0
        assert metric.compute() == 2.0, "Condition must be true"

    def test_reset(self) -> None:
        metric = StreamingLoss()
        metric.update(None, None, loss=5.0)
        assert metric.compute() == 5.0, "Condition must be true"

        metric.reset()
        assert metric.compute() == 0.0, "Condition must be true"

    def test_fallback_to_preds_mean(self) -> None:
        metric = StreamingLoss()
        # When loss kwarg not provided, uses mean of preds
        preds = np.array([2.0, 4.0, 6.0])
        metric.update(preds, None)
        assert metric.compute() == 4.0, "Condition must be true"

    def test_fallback_with_torch_tensor(self) -> None:
        metric = StreamingLoss()
        preds = torch.tensor([1.0, 2.0, 3.0])
        metric.update(preds, None)
        assert metric.compute() == 2.0, "Condition must be true"

    def test_empty_preds_fallback(self) -> None:
        metric = StreamingLoss()
        preds = np.array([])
        metric.update(preds, None)
        # Empty array should result in 0.0 loss
        assert metric.compute() == 0.0, "Condition must be true"

    def test_multiple_batches(self) -> None:
        metric = StreamingLoss()

        losses = [1.0, 2.0, 3.0, 4.0, 5.0]
        for loss in losses:
            metric.update(None, None, loss=loss)

        # Average of [1, 2, 3, 4, 5] = 15 / 5 = 3.0
        assert metric.compute() == 3.0, "Condition must be true"

    def test_with_zero_loss(self) -> None:
        metric = StreamingLoss()
        metric.update(None, None, loss=0.0)
        metric.update(None, None, loss=0.0)
        assert metric.compute() == 0.0, "Condition must be true"

    def test_mixed_loss_sources(self) -> None:
        metric = StreamingLoss()

        # First with explicit loss
        metric.update(None, None, loss=2.0)

        # Second with mean of preds
        preds = np.array([4.0, 4.0, 4.0])
        metric.update(preds, None)

        # Average of 2.0 and 4.0 = 3.0
        assert metric.compute() == 3.0, "Condition must be true"

    def test_streaming_over_training_epoch(self) -> None:
        """Simulate a training epoch with varying batch losses."""
        metric = StreamingLoss()

        # Simulate 10 batches with decreasing loss (training progress)
        batch_losses = [10.0, 9.0, 8.0, 7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0]

        for loss in batch_losses:
            metric.update(None, None, loss=loss)

        # Average = 55 / 10 = 5.5
        assert metric.compute() == 5.5, "Condition must be true"

    def test_compute_without_updates(self) -> None:
        metric = StreamingLoss()
        # Should return 0.0 when no updates
        assert metric.compute() == 0.0, "Condition must be true"
