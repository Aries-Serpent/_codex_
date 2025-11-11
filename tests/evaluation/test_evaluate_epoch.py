import pytest
import torch
from codex_ml.evaluation.loop import evaluate_epoch


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

    assert "loss" in summary and "count" in summary
    assert summary["count"] == 8


def test_evaluate_max_batches():
    model = DummyModel()
    criterion = torch.nn.CrossEntropyLoss()

    inputs = torch.randn(10, 4)
    targets = torch.randint(0, 3, (10,))
    data = list(zip(inputs, targets))

    summary = evaluate_epoch(model, data, criterion, device="cpu", max_batches=2)

    assert summary["batches"] == 2


def test_evaluate_metrics():
    model = DummyModel()
    criterion = torch.nn.CrossEntropyLoss()

    inputs = torch.randn(6, 4)
    targets = torch.randint(0, 3, (6,))
    data = list(zip(inputs, targets))

    def accuracy(preds, t):
        return (preds.argmax(dim=-1) == t).float().mean()

    summary = evaluate_epoch(model, data, criterion, metrics={"acc": accuracy})

    assert "acc" in summary["metrics"]


def test_evaluate_invalid_batch():
    model = DummyModel()
    criterion = torch.nn.CrossEntropyLoss()

    bad_data = [torch.randn(4, 4)]  # missing targets

    with pytest.raises(ValueError):
        evaluate_epoch(model, bad_data, criterion)
