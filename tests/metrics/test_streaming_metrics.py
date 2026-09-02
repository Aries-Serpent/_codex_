"""
Tests for streaming metrics functionality
"""

import pytest

np = pytest.importorskip("numpy")

# Skip entire module if torch is not available or unloadable
import torch

from codex_ml.metrics.classification import StreamingAccuracy
from codex_ml.metrics.streaming import StreamingLoss


class TestStreamingLoss:
    """Test StreamingLoss metric"""

    def test_initialization(self):
        """Test StreamingLoss initializes with zero state"""
        metric = StreamingLoss()
        assert metric._sum == 0.0, "_sum is not valid"
        assert metric._count == 0, "Count must be greater than zero"
        assert metric.compute() == 0.0, "Condition must be true"

    def test_single_update(self):
        """Test single loss update"""
        metric = StreamingLoss()
        metric.update(None, None, loss=1.5)
        assert metric.compute() == 1.5, "Condition must be true"

    def test_multiple_updates(self):
        """Test averaging over multiple updates"""
        metric = StreamingLoss()
        losses = [1.0, 2.0, 3.0, 4.0]

        for loss in losses:
            metric.update(None, None, loss=loss)

        expected_avg = sum(losses) / len(losses)
        assert metric.compute() == expected_avg, "Condition must be true"

    def test_reset_clears_state(self):
        """Test reset returns to initial state"""
        metric = StreamingLoss()
        metric.update(None, None, loss=5.0)
        metric.update(None, None, loss=3.0)

        assert metric.compute() == 4.0, "Condition must be true"

        metric.reset()
        assert metric._sum == 0.0, "_sum is not valid"
        assert metric._count == 0, "Count must be greater than zero"
        assert metric.compute() == 0.0, "Condition must be true"

    def test_tensor_fallback(self):
        """Test fallback to tensor mean when loss not provided"""
        metric = StreamingLoss()

        # Pass tensor as preds
        tensor_loss = torch.tensor([1.0, 2.0, 3.0])
        metric.update(tensor_loss, None)

        assert abs(metric.compute() - 2.0) < 0.01, "Condition must be true"

    def test_numpy_fallback(self):
        """Test works with numpy arrays"""
        metric = StreamingLoss()

        arr_loss = np.array([2.0, 4.0, 6.0])
        metric.update(arr_loss, None)

        assert abs(metric.compute() - 4.0) < 0.01, "Condition must be true"


class TestStreamingAccuracyAdvanced:
    """Advanced tests for StreamingAccuracy"""

    def test_empty_batches_handled(self):
        """Test handling of empty batches"""
        metric = StreamingAccuracy()

        # Empty tensors
        metric.update(torch.tensor([]), torch.tensor([]))

        # Should return 0 for empty
        assert metric.compute() == 0.0, "Condition must be true"

    def test_large_batch_accumulation(self):
        """Test accumulation over many large batches"""
        metric = StreamingAccuracy()

        # Simulate 100 batches of 32 samples each
        np.random.seed(42)
        for _ in range(100):
            preds = np.random.randint(0, 10, size=32)
            labels = preds.copy()
            # Flip 25% of predictions
            flip_indices = np.random.choice(32, size=8, replace=False)
            preds[flip_indices] = (preds[flip_indices] + 1) % 10

            metric.update(preds, labels)

        # Should be around 75% accuracy (since we flipped 25%)
        acc = metric.compute()
        assert 0.7 < acc < 0.8, "7 is not valid"

    def test_ignore_index_partial_masking(self):
        """Test ignore_index masks only specific tokens"""
        metric = StreamingAccuracy(ignore_index=-1)

        preds = torch.tensor([0, 1, 2, 3, 4])
        labels = torch.tensor([0, -1, 2, -1, 5])

        metric.update(preds, labels)

        # Only indices 0, 2, 4 count: 2 correct (0, 2) out of 3
        expected = 2.0 / 3.0
        assert abs(metric.compute() - expected) < 0.01, "Condition must be true"

    def test_mixed_correct_incorrect_batches(self):
        """Test mixed batches with varying accuracy"""
        metric = StreamingAccuracy()

        # Batch 1: 100% accuracy
        metric.update(torch.tensor([1, 2, 3]), torch.tensor([1, 2, 3]))

        # Batch 2: 0% accuracy
        metric.update(torch.tensor([0, 0, 0]), torch.tensor([1, 1, 1]))

        # Batch 3: 50% accuracy
        metric.update(torch.tensor([1, 0]), torch.tensor([1, 1]))

        # Overall: 4 correct out of 8
        assert metric.compute() == 0.5, "Condition must be true"


class TestStreamingMetricInteraction:
    """Test interaction between different streaming metrics"""

    def test_independent_metrics(self):
        """Test multiple streaming metrics maintain independent state"""
        loss_metric = StreamingLoss()
        acc_metric = StreamingAccuracy()

        # Update both with different data
        loss_metric.update(None, None, loss=1.0)
        acc_metric.update(torch.tensor([1, 1]), torch.tensor([1, 0]))

        loss_metric.update(None, None, loss=3.0)
        acc_metric.update(torch.tensor([2, 2]), torch.tensor([2, 2]))

        # Each should have its own correct values
        assert loss_metric.compute() == 2.0, "Condition must be true"
        assert acc_metric.compute() == 0.75, "Condition must be true"

    def test_reset_one_doesnt_affect_other(self):
        """Test resetting one metric doesn't affect another"""
        metric1 = StreamingLoss()
        metric2 = StreamingLoss()

        metric1.update(None, None, loss=5.0)
        metric2.update(None, None, loss=3.0)

        metric1.reset()

        assert metric1.compute() == 0.0, "Condition must be true"
        assert metric2.compute() == 3.0, "Condition must be true"


class TestStreamingEdgeCases:
    """Test edge cases for streaming metrics"""

    def test_zero_division_protection(self):
        """Test metrics handle zero counts gracefully"""
        acc = StreamingAccuracy()
        loss = StreamingLoss()

        # Compute without any updates
        assert acc.compute() == 0.0, "Condition must be true"
        assert loss.compute() == 0.0, "Condition must be true"

    def test_very_small_values(self):
        """Test handling of very small loss values"""
        metric = StreamingLoss()

        small_losses = [1e-10, 1e-9, 1e-8]
        for loss in small_losses:
            metric.update(None, None, loss=loss)

        result = metric.compute()
        assert result > 0, "result must be greater than zero"
        assert result < 1e-7, "Result must not be empty"

    def test_very_large_batches(self):
        """Test handling large batch sizes"""
        metric = StreamingAccuracy()

        # 10,000 samples
        large_preds = torch.randint(0, 100, (10000,))
        large_labels = torch.randint(0, 100, (10000,))

        metric.update(large_preds, large_labels)

        result = metric.compute()
        # Should be around 1% accuracy for random 100-class
        assert 0.0 <= result <= 0.05, "Result must not be empty"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
