import pytest

pytest.importorskip("mlflow")
"""
Test Evaluate Epoch

Test module for evaluate epoch.
"""

from functools import partial

import pytest

pytest.importorskip("torch")


# Skip entire module if torch is not available or unloadable
pytest.importorskip("torch", reason="PyTorch required for tests")
import torch

from codex_ml.evaluation.loop import evaluate_epoch
from codex_ml.metrics.generative import bleu


class DummyModel(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.lin = torch.nn.Linear(4, 3)

    def forward(self, x):
        return self.lin(x)


def test_evaluate_basic():
    model = DummyModel()
    criterion = torch.nn.CrossEntropyLoss()
    # Build simple synthetic dataloader
    inputs = torch.randn(8, 4)
    targets = torch.randint(0, 3, (8,))
    data = list(zip(inputs, targets))
    summary = evaluate_epoch(model, data, criterion, device="cpu")
    assert "loss" in summary and "count" in summary, "Count must be greater than zero"
    assert summary["count"] == 8, "Count must be greater than zero"


def test_evaluate_max_batches():
    model = DummyModel()
    criterion = torch.nn.CrossEntropyLoss()
    inputs = torch.randn(10, 4)
    targets = torch.randint(0, 3, (10,))
    data = list(zip(inputs, targets))
    summary = evaluate_epoch(model, data, criterion, device="cpu", max_batches=2)
    assert summary["batches"] == 2, "Condition must be true"


def test_evaluate_metrics():
    model = DummyModel()
    criterion = torch.nn.CrossEntropyLoss()
    inputs = torch.randn(6, 4)
    targets = torch.randint(0, 3, (6,))
    data = list(zip(inputs, targets))

    def accuracy(preds, t):
        return (preds.argmax(dim=-1) == t).float().mean()

    summary = evaluate_epoch(model, data, criterion, metrics={"acc": accuracy})
    assert "acc" in summary["metrics"], "Condition must be true"


def test_evaluate_metrics_with_partial():
    """Test that functools.partial metrics work (P1 fix)"""
    model = DummyModel()
    criterion = torch.nn.CrossEntropyLoss()
    inputs = torch.randn(6, 4)
    targets = torch.randint(0, 3, (6,))
    data = list(zip(inputs, targets))

    def top_k_accuracy(preds, targets, k=1):
        # Simple top-k accuracy metric
        return (preds.argmax(dim=-1) == targets).float().mean()

    # Create partial with k=1
    top1_acc = partial(top_k_accuracy, k=1)

    # Should not raise AttributeError
    summary = evaluate_epoch(model, data, criterion, metrics={"top1": top1_acc})
    assert "top1" in summary["metrics"], "Condition must be true"


def test_evaluate_metrics_with_callable_class():
    """Test that callable class instances work as metrics (P1 fix)"""
    model = DummyModel()
    criterion = torch.nn.CrossEntropyLoss()
    inputs = torch.randn(6, 4)
    targets = torch.randint(0, 3, (6,))
    data = list(zip(inputs, targets))

    class AccuracyMetric:
        def __call__(self, preds, targets):
            return (preds.argmax(dim=-1) == targets).float().mean()

    acc_metric = AccuracyMetric()

    # Should not raise AttributeError
    summary = evaluate_epoch(model, data, criterion, metrics={"acc": acc_metric})
    assert "acc" in summary["metrics"], "Condition must be true"


def test_evaluate_invalid_batch():
    model = DummyModel()
    criterion = torch.nn.CrossEntropyLoss()
    bad_data = [torch.randn(4, 4)]  # missing targets
    with pytest.raises(ValueError):
        evaluate_epoch(model, bad_data, criterion)


def test_evaluate_with_text_metric():
    model = DummyModel()
    criterion = torch.nn.CrossEntropyLoss()
    inputs = torch.randn(4, 4)
    targets = torch.randint(0, 3, (4,))
    data = list(zip(inputs, targets))

    def prediction_transform(outputs):
        batch = outputs.shape[0]
        return ["hello world" for _ in range(batch)]

    def target_transform(batch_targets):
        batch = batch_targets.shape[0]
        return ["hello world" for _ in range(batch)]

    summary = evaluate_epoch(
        model,
        data,
        criterion,
        metrics={"bleu": bleu},
        prediction_transform=prediction_transform,
        target_transform=target_transform,
    )

    assert pytest.approx(1.0, rel=1e-6) == summary["metrics"]["bleu"]
