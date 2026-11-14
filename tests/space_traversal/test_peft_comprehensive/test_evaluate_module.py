"""
Test Evaluate Module

Test module for evaluate module.
"""

from __future__ import annotations

import pytest

pytest.importorskip("numpy", reason="numpy required")

import json
from pathlib import Path

from training.evaluate import _loss_to_float, evaluate


class _DummyTensor:
    def __init__(self, value: float) -> None:
        self.value = value

    def to(self, _device: str) -> "_DummyTensor":
        return self

    def detach(self) -> "_DummyTensor":
        return self

    def cpu(self) -> "_DummyTensor":
        return self

    def item(self) -> float:
        return float(self.value)


class _DummyOutputs:
    def __init__(self, loss: float) -> None:
        self.loss = _DummyTensor(loss)


class _DummyModel:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []
        self.evaluated = False
        self.device = "cpu"

    def eval(self) -> "_DummyModel":
        self.evaluated = True
        return self

    def __call__(self, **kwargs):
        self.calls.append(kwargs)
        return _DummyOutputs(0.5)


class _DummyTokenizer:
    def __call__(self, text: str, **_kwargs):
        return {"input_ids": _DummyTensor(len(text))}


def test_evaluate_records_losses(tmp_path: Path) -> None:
    model = _DummyModel()
    tokenizer = _DummyTokenizer()
    dataset = [{"text": "hello"}, {"text": "world"}]
    out_file = tmp_path / "metrics.ndjson"

    metrics = evaluate(model, tokenizer, dataset, output_path=out_file)

    assert metrics["count"] == 2, "Count must be greater than zero"
    assert metrics["loss"] == pytest.approx(0.5), "Condition must be true"

    with out_file.open("r", encoding="utf-8") as handle:
        lines = [json.loads(line) for line in handle]
    assert len(lines) == 2, "Lines must not be empty"
    assert all("loss" in line for line in lines), "Condition must be true"


def test_evaluate_skips_empty_samples(tmp_path: Path) -> None:
    model = _DummyModel()
    tokenizer = _DummyTokenizer()
    dataset = [{"text": ""}, {"text": None}, "manual"]
    out_file = tmp_path / "metrics.ndjson"

    metrics = evaluate(model, tokenizer, dataset, output_path=out_file)
    assert metrics["count"] == 1, "Count must be greater than zero"


def test_loss_conversion_propagates_scalar_conversion_errors():
    class NonScalar:
        def item(self):
            raise ValueError("not scalar")

    with pytest.raises(ValueError, match="not scalar"):
        _loss_to_float(NonScalar())
    with pytest.raises(TypeError, match="Cannot convert loss"):
        _loss_to_float(object())
