"""Tests for deterministic inference pipeline stages (v1.0.0)."""

from __future__ import annotations

import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

np = pytest.importorskip("numpy")
torch = pytest.importorskip("torch")

from scripts import inference_pipeline as pipeline


class DummyTokenizer:
    def __init__(self):
        self.pad_token_id = 0
        self.model_max_length = 256

    def __call__(
        self,
        text: str,
        return_tensors: str = "pt",
        truncation: bool = True,
        max_length: int = 128,
        padding: bool = False,
    ):
        tokens = [len(text.split())]
        input_ids = torch.tensor([tokens], dtype=torch.long)
        attention_mask = torch.ones_like(input_ids)
        return {"input_ids": input_ids, "attention_mask": attention_mask}

    def decode(self, ids, skip_special_tokens: bool = True):
        if isinstance(ids, torch.Tensor):
            ids = ids.tolist()
        if isinstance(ids, (list, tuple)):
            return " ".join(str(v) for v in ids)
        return str(ids)

    def batch_decode(self, ids, skip_special_tokens: bool = True):
        return [self.decode(item, skip_special_tokens=skip_special_tokens) for item in ids]


class DummyModel(torch.nn.Module):
    def forward(self, input_ids=None, attention_mask=None):
        batch, seq_len = input_ids.shape
        vocab = max(int(input_ids.max().item()) + 2, 4)
        logits = torch.zeros((batch, seq_len, vocab), dtype=torch.float)
        logits[:, :, -1] = 1.0
        return SimpleNamespace(logits=logits)


class DummyAutoTokenizer:
    @classmethod
    def from_pretrained(cls, *_, **__):
        return DummyTokenizer()


class DummyAutoModel:
    @classmethod
    def from_pretrained(cls, *_, **__):
        return DummyModel()


class NamedDummyTokenizer(DummyTokenizer):
    def __init__(self, name):
        super().__init__()
        self.name_or_path = name


def _write_config(tmp_path: Path, model_dir: Path) -> Path:
    cfg = {
        "inference": {
            "model_path": str(model_dir),
            "seed": 42,
            "deterministic": True,
            "max_input_length": 64,
        }
    }
    config_path = tmp_path / "config.yaml"
    config_path.write_text(json.dumps(cfg))
    return config_path


def _write_input(tmp_path: Path, text: str = "hello world") -> Path:
    input_path = tmp_path / "input.json"
    input_path.write_text(json.dumps({"text": text}))
    return input_path


def test_pipeline_runs_deterministically(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    os.environ["WANDB_MODE"] = "offline"
    model_dir = tmp_path / "model"
    model_dir.mkdir()
    (model_dir / "config.json").write_text("{}")

    monkeypatch.setattr(pipeline, "AutoTokenizer", DummyAutoTokenizer)
    monkeypatch.setattr(pipeline, "AutoModelForCausalLM", DummyAutoModel)

    config_path = _write_config(tmp_path, model_dir)
    input_path = _write_input(tmp_path)

    out1_path = tmp_path / "out1.json"
    out2_path = tmp_path / "out2.json"

    out1 = pipeline.run_pipeline(config_path, input_path, out1_path)
    out2 = pipeline.run_pipeline(config_path, input_path, out2_path)

    assert out1["output_hash"] == out2["output_hash"], "Condition must be true"
    assert out1["payload"]["input_hash"] == out2["payload"]["input_hash"], "Condition must be true"


def test_missing_model_path_raises(tmp_path: Path):
    cfg = pipeline.InferenceConfig(model_path=tmp_path / "does_not_exist")
    with pytest.raises(ValueError):
        pipeline.stage_i1_load_model(cfg)


def test_invalid_input_rejected(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    cfg = pipeline.InferenceConfig(model_path=tmp_path)
    tokenizer = DummyTokenizer()
    context = {"tokenizer": tokenizer}
    with pytest.raises(ValueError):
        pipeline.stage_i2_preprocess({}, context, cfg)


def test_token_cache_keys_include_tokenizer_and_model(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    os.environ["WANDB_MODE"] = "offline"
    pipeline.TOKEN_CACHE.clear()
    cfg = pipeline.InferenceConfig(model_path=tmp_path / "model", max_input_length=16)
    context_a = {"tokenizer": NamedDummyTokenizer("tok-a"), "model_hash": "hash-a"}
    context_b = {"tokenizer": NamedDummyTokenizer("tok-b"), "model_hash": "hash-b"}
    inputs = {"text": "hello world"}

    res_a = pipeline.stage_i2_preprocess(inputs, context_a, cfg)
    res_b = pipeline.stage_i2_preprocess(inputs, context_b, cfg)

    assert res_a["tokens"]["input_ids"].shape == res_b["tokens"]["input_ids"].shape, "shape is not valid"
    assert len(pipeline.TOKEN_CACHE) == 2, "Collection must not be empty"


def test_allow_online_flag_bypasses_enforcement(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    # Ensure pipeline can be invoked with allow_online when WANDB_MODE is not set
    os.environ.pop("WANDB_MODE", None)
    model_dir = tmp_path / "model"
    model_dir.mkdir()
    (model_dir / "config.json").write_text("{}")

    monkeypatch.setattr(pipeline, "AutoTokenizer", DummyAutoTokenizer)
    monkeypatch.setattr(pipeline, "AutoModelForCausalLM", DummyAutoModel)

    config_path = _write_config(tmp_path, model_dir)
    input_path = _write_input(tmp_path)
    out_path = tmp_path / "out.json"

    result = pipeline.run_pipeline(config_path, input_path, out_path, allow_online=True)
    assert "output_hash" in result, "Result must not be empty"
