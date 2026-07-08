"""Smoke tests for classification, streaming, reward, generation, and evaluator metrics."""

from __future__ import annotations

import sys
from types import SimpleNamespace

import pytest

np = pytest.importorskip("numpy")


@pytest.fixture(autouse=True)
def stub_torch(monkeypatch):
    """Provide a lightweight torch stub to satisfy metric imports."""

    class FakeTensor:
        def __init__(self, data):
            self._data = np.asarray(data)

        def detach(self):
            return self

        def cpu(self):
            return self

        def numpy(self):  # pragma: no cover - compatibility shim
            return self._data

        @property
        def device(self):
            return "cpu"

        @property
        def shape(self):
            return self._data.shape

        def to(self, device):
            return self

        def __getitem__(self, key):
            return FakeTensor(self._data[key])

        def any(self):
            return np.any(self._data)

        def float(self):
            return FakeTensor(self._data.astype(np.float32))

        def mean(self):
            return FakeTensor(np.mean(self._data))

        def item(self):
            return float(np.asarray(self._data).item())

    def fake_argmax(tensor, dim=-1):
        return FakeTensor(np.argmax(tensor._data if hasattr(tensor, "_data") else tensor, axis=dim))

    fake_torch = SimpleNamespace(
        Tensor=FakeTensor,
        argmax=fake_argmax,
        is_tensor=lambda x: isinstance(x, FakeTensor),
    )
    monkeypatch.setitem(sys.modules, "torch", fake_torch)
    yield fake_torch
    sys.modules.pop("torch", None)


def test_classification_metrics_numpy():
    """Classification helpers operate on numpy arrays and handle ignore_index."""

    from codex_ml.metrics import classification

    preds = np.array([1, 0, 1])
    labels = np.array([1, 1, 0])
    assert classification.accuracy(preds, labels, ignore_index=None) == pytest.approx(1 / 3)
    assert classification.precision(preds, labels, positive=1) == pytest.approx(0.5)
    assert classification.recall(preds, labels, positive=1) == pytest.approx(0.5)
    streaming = classification.StreamingAccuracy(ignore_index=None)
    streaming.update(preds, labels)
    assert streaming.compute() == pytest.approx(1 / 3), "Condition must be true"
    streaming.reset()
    assert streaming.compute() == 0.0, "Condition must be true"


def test_streaming_loss_from_kwargs():
    """StreamingLoss consumes scalar losses or tensor-like payloads."""

    from codex_ml.metrics.streaming import StreamingLoss

    metric = StreamingLoss()
    metric.update(preds=None, labels=None, loss=0.5)
    metric.update(preds=np.array([0.0, 1.0]), labels=None)
    assert metric.compute() > 0, "Value must be greater than zero"
    metric.reset()
    assert metric.compute() == 0.0, "Condition must be true"


def test_reward_metrics():
    """Reward helpers coerce mappings and thresholds."""

    from codex_ml.metrics import reward

    predictions = [{"reward": 0.4}, {"reward": 0.6}, 0.8]
    assert reward.reward_mean(predictions, None) == pytest.approx((0.4 + 0.6 + 0.8) / 3)
    assert reward.reward_success_rate(predictions, None, threshold=0.5) == pytest.approx(2 / 3)


def test_generation_scores():
    """BLEU and ROUGE utilities return bounded values."""

    from codex_ml.metrics import generation

    hyps = ["a b c", "hello world"]
    refs = [["a b c"], ["hello there"]]
    bp = generation.compute_brevity_penalty(hyps, refs)
    bleu = generation.bleu(hyps, refs)
    rouge = generation.rouge_l(hyps, ["a b c", "hello there"])
    assert 0.0 <= bp <= 1.0, "0 is not valid"
    assert 0.0 <= bleu <= 1.0, "0 is not valid"
    assert 0.0 <= rouge <= 1.0, "0 is not valid"


def test_evaluator_batch_metrics_text_and_loss():
    """batch_metrics derives text metrics and perplexity when available."""

    from codex_ml.metrics import evaluator

    outputs = SimpleNamespace(loss=0.0, predictions=["a", "b"])
    batch = {"references": ["a", "c"]}
    record = evaluator.batch_metrics(outputs, batch)
    assert "perplexity" in record and record["perplexity"] >= 0, "Value must be greater than zero"
    assert record.get("exact_match") is not None, "rec must be initialized"
