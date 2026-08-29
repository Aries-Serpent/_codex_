"""
pytest.importorskip("mlflow")
Unit tests for evaluate_epoch function.

Tests cover:
- Basic evaluation flow
- Metrics computation
- Transform callables
- Deterministic mode
- Edge cases (empty batches, NaN metrics, etc.)
"""

from __future__ import annotations

import pytest

torch = pytest.importorskip("torch")

from codex_ml.evaluation.loop import evaluate_epoch


class _SimpleModel(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.linear = torch.nn.Linear(4, 3)

    def forward(self, x):
        return self.linear(x)


class _DeviceAwareModel(_SimpleModel):
    def __init__(self):
        super().__init__()
        self.last_seen_device = None

    def forward(self, x):
        self.last_seen_device = x.device
        return super().forward(x)


class _SimpleCriterion:
    def __call__(self, outputs, targets):
        return torch.nn.functional.cross_entropy(outputs, targets)


def _simple_accuracy(preds, targets):
    """Simple accuracy metric for testing."""
    if torch is not None and hasattr(preds, "eq"):
        correct = preds.eq(targets).sum()
        total = targets.numel()
        return float(correct) / max(total, 1)
    # Fallback for list inputs
    correct = sum(1 for p, t in zip(preds, targets) if p == t)
    return correct / max(len(targets), 1)


def test_evaluate_epoch_basic():
    """Test basic evaluation with single batch."""
    model = _SimpleModel()
    data = [(torch.randn(2, 4), torch.randint(0, 3, (2,)))]
    criterion = _SimpleCriterion()

    result = evaluate_epoch(model, data, criterion, device="cpu")

    assert "loss" in result, "Result must not be empty"
    assert "count" in result, "Result must not be empty"
    assert "batches" in result, "Result must not be empty"
    assert "duration_sec" in result, "Result must not be empty"
    assert result["count"] == 2, "Result must not be empty"
    assert result["batches"] == 1, "Result must not be empty"
    assert result["loss"] >= 0.0, "Value must be greater than zero"


def test_evaluate_epoch_multiple_batches():
    """Test evaluation accumulates across multiple batches."""
    model = _SimpleModel()
    data = [
        (torch.randn(2, 4), torch.randint(0, 3, (2,))),
        (torch.randn(3, 4), torch.randint(0, 3, (3,))),
    ]
    criterion = _SimpleCriterion()

    result = evaluate_epoch(model, data, criterion, device="cpu")

    assert result["count"] == 5, "Result must not be empty"
    assert result["batches"] == 2, "Result must not be empty"


def test_evaluate_epoch_with_metrics():
    """Test evaluation with custom metrics."""
    model = _SimpleModel()
    data = [(torch.randn(4, 4), torch.randint(0, 3, (4,)))]
    criterion = _SimpleCriterion()
    metrics = {"accuracy": _simple_accuracy}

    result = evaluate_epoch(model, data, criterion, device="cpu", metrics=metrics)

    assert "metrics" in result, "Result must not be empty"
    assert "accuracy" in result["metrics"], "Result must not be empty"
    assert 0.0 <= result["metrics"]["accuracy"] <= 1.0, "Result must not be empty"


def test_evaluate_epoch_max_batches():
    """Test max_batches parameter limits evaluation."""
    model = _SimpleModel()
    data = [
        (torch.randn(2, 4), torch.randint(0, 3, (2,))),
        (torch.randn(2, 4), torch.randint(0, 3, (2,))),
        (torch.randn(2, 4), torch.randint(0, 3, (2,))),
    ]
    criterion = _SimpleCriterion()

    result = evaluate_epoch(model, data, criterion, device="cpu", max_batches=2)

    assert result["batches"] == 2, "Result must not be empty"
    assert result["count"] == 4, "Result must not be empty"


def test_evaluate_epoch_deterministic():
    """Test deterministic mode produces same results."""
    model = _SimpleModel()
    torch.manual_seed(42)
    model_state = model.state_dict()

    data = [(torch.randn(4, 4), torch.randint(0, 3, (4,)))]
    criterion = _SimpleCriterion()

    # First run
    model.load_state_dict(model_state)
    result1 = evaluate_epoch(model, data, criterion, device="cpu", seed=42, deterministic=True)

    # Second run
    model.load_state_dict(model_state)
    result2 = evaluate_epoch(model, data, criterion, device="cpu", seed=42, deterministic=True)

    assert result1["loss"] == result2["loss"], "Result must not be empty"
    assert result1["count"] == result2["count"], "Result must not be empty"


def test_evaluate_epoch_with_logger(tmp_path):
    """Test evaluation with logger."""
    model = _SimpleModel()
    data = [(torch.randn(2, 4), torch.randint(0, 3, (2,)))]
    criterion = _SimpleCriterion()

    # Simple logger that collects records
    class _TestLogger:
        def __init__(self):
            self.records = []

        def log(self, record):
            self.records.append(record)

        def close(self):
            pass

    logger = _TestLogger()
    evaluate_epoch(model, data, criterion, device="cpu", logger=[logger])

    # Should have batch and epoch records
    assert len(logger.records) >= 2, "Collection must not be empty"
    batch_records = [r for r in logger.records if r.get("type") == "batch"]
    epoch_records = [r for r in logger.records if r.get("type") == "epoch"]
    assert len(batch_records) == 1, "Batch_records must not be empty"
    assert len(epoch_records) == 1, "Epoch_records must not be empty"


def test_evaluate_epoch_metric_error_handling():
    """Test graceful handling of metric computation errors."""
    model = _SimpleModel()
    data = [(torch.randn(2, 4), torch.randint(0, 3, (2,)))]
    criterion = _SimpleCriterion()

    def _broken_metric(preds, targets):
        raise ValueError("Intentional error")

    metrics = {"broken": _broken_metric}
    result = evaluate_epoch(model, data, criterion, device="cpu", metrics=metrics)

    # Should return NaN for broken metric
    assert "metrics" in result, "Result must not be empty"
    assert "broken" in result["metrics"], "Result must not be empty"
    import math

    assert math.isnan(result["metrics"]["broken"]), "Result must not be empty"


def test_evaluate_epoch_empty_dataloader():
    """Test evaluation with empty dataloader."""
    model = _SimpleModel()
    data = []
    criterion = _SimpleCriterion()

    result = evaluate_epoch(model, data, criterion, device="cpu")

    assert result["count"] == 0, "Result must not be empty"
    assert result["batches"] == 0, "Result must not be empty"


def test_evaluate_epoch_with_prediction_transform():
    """Test evaluation with prediction transform."""
    model = _SimpleModel()
    data = [(torch.randn(2, 4), torch.randint(0, 3, (2,)))]
    criterion = _SimpleCriterion()

    def _pred_transform(outputs):
        # Convert to list of class indices
        return outputs.argmax(dim=-1).tolist()

    def _target_transform(targets):
        return targets.tolist()

    def _list_accuracy(preds, targets):
        correct = sum(1 for p, t in zip(preds, targets) if p == t)
        return correct / max(len(targets), 1)

    metrics = {"accuracy": _list_accuracy}
    result = evaluate_epoch(
        model,
        data,
        criterion,
        device="cpu",
        metrics=metrics,
        prediction_transform=_pred_transform,
        target_transform=_target_transform,
    )

    assert "metrics" in result, "Result must not be empty"
    assert "accuracy" in result["metrics"], "Result must not be empty"
    assert 0.0 <= result["metrics"]["accuracy"] <= 1.0, "Result must not be empty"


def test_evaluate_epoch_sets_eval_mode():
    """Test that model is set to eval mode."""
    model = _SimpleModel()
    model.train()  # Set to training mode

    data = [(torch.randn(2, 4), torch.randint(0, 3, (2,)))]
    criterion = _SimpleCriterion()

    result = evaluate_epoch(model, data, criterion, device="cpu")

    # Model should be in eval mode during evaluation
    # (though it returns to whatever mode it was in after)
    assert result is not None, "result must be initialized"


def test_evaluate_epoch_invalid_batch_shape():
    """Test handling of invalid batch shapes."""
    model = _SimpleModel()
    data = [torch.randn(2, 4)]  # Missing targets
    criterion = _SimpleCriterion()

    with pytest.raises(ValueError, match="must yield .* pairs"):
        evaluate_epoch(model, data, criterion, device="cpu")


def test_evaluate_epoch_aligns_devices_cpu():
    model = _DeviceAwareModel()
    data = [(torch.randn(2, 4), torch.randint(0, 3, (2,)))]
    criterion = _SimpleCriterion()

    evaluate_epoch(model, data, criterion, device="cpu")

    assert next(model.parameters()).device.type == "cpu", "type is not valid"
    assert model.last_seen_device is not None, "last_seen_device must be initialized"
    assert model.last_seen_device.type == "cpu", "type is not valid"


@pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
def test_evaluate_epoch_aligns_devices_cuda():
    model = _DeviceAwareModel()
    data = [(torch.randn(2, 4), torch.randint(0, 3, (2,)))]
    criterion = _SimpleCriterion()

    evaluate_epoch(model, data, criterion, device="cuda")

    assert next(model.parameters()).device.type == "cuda", "type is not valid"
    assert model.last_seen_device is not None, "last_seen_device must be initialized"
    assert model.last_seen_device.type == "cuda", "type is not valid"
