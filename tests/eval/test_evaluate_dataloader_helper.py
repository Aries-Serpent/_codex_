import types
from collections.abc import Iterable
from typing import Any

import pytest

from codex_ml.eval import evaluator


class _FakeTensor:
    def __init__(self, value: float, *, shape: tuple[int, ...] = (1,)) -> None:
        self.value = float(value)
        self.shape = shape

    def to(self, device: Any) -> "_FakeTensor":
        # Record the requested device for inspection if needed.
        self.device = device
        return self

    def detach(self) -> "_FakeTensor":  # pragma: no cover - exercised indirectly
        return self

    def cpu(self) -> "_FakeTensor":  # pragma: no cover - exercised indirectly
        return self

    def item(self) -> float:
        return self.value


class _FakeNoGrad:
    def __enter__(self) -> None:  # pragma: no cover - trivial
        return None

    def __exit__(self, exc_type, exc, tb) -> bool:  # pragma: no cover - trivial
        return False


@pytest.fixture
def fake_torch(monkeypatch):
    module = types.SimpleNamespace()
    module.no_grad = staticmethod(lambda: _FakeNoGrad())
    module.device = staticmethod(lambda spec: spec)
    monkeypatch.setattr(evaluator, "torch", module)
    monkeypatch.setattr(evaluator, "_HAS_TORCH", True)
    yield module
    monkeypatch.setattr(evaluator, "torch", None)
    monkeypatch.setattr(evaluator, "_HAS_TORCH", False)


class _FakeModel:
    def __init__(self) -> None:
        self.training = True

    def eval(self) -> None:
        self.training = False

    def train(self, mode: bool = True) -> None:
        self.training = bool(mode)

    def __call__(self, **batch: Any) -> dict[str, _FakeTensor]:
        loss_val = sum(tensor.value for tensor in batch.values())
        accuracy = loss_val / max(len(batch), 1)
        return {
            "loss": _FakeTensor(loss_val),
            "accuracy": _FakeTensor(accuracy),
        }


def _make_loader() -> Iterable[dict[str, _FakeTensor]]:
    return [
        {"input_ids": _FakeTensor(1.0), "labels": _FakeTensor(1.0)},
        {"input_ids": _FakeTensor(3.0), "labels": _FakeTensor(3.0)},
    ]


@pytest.mark.usefixtures("fake_torch")
def test_evaluate_dataloader_averages_and_restores_training() -> None:
    model = _FakeModel()
    loader = _make_loader()
    metrics = evaluator.evaluate_dataloader(
        model,
        loader,
        {"metric_keys": ["accuracy"]},
        device="cpu",
    )
    # Loss: (2 + 6) / 2 = 4.0
    assert metrics["loss"] == pytest.approx(4.0)
    # Accuracy: (1 + 3) / 2 = 2.0
    assert metrics["accuracy"] == pytest.approx(2.0)
    assert metrics["batches"] == pytest.approx(2)
    assert metrics.get("samples") == pytest.approx(2)
    # Model training mode restored after evaluation.
    assert model.training is True


def test_evaluate_dataloader_requires_torch(monkeypatch) -> None:
    monkeypatch.setattr(evaluator, "torch", None)
    monkeypatch.setattr(evaluator, "_HAS_TORCH", False)
    with pytest.raises(ImportError):
        evaluator.evaluate_dataloader(_FakeModel(), [], {}, device="cpu")
