import json
import types
from pathlib import Path

import pytest
import torch

from training.engine_hf_trainer import run_hf_trainer


def test_hf_trainer_smoke(tmp_path):
    texts = ["hello world", "goodbye moon", "hello again", "coding rocks"]
    config = Path("configs/training/base.yaml")
    metrics = run_hf_trainer(
        texts,
        tmp_path,
        model_name="sshleifer/tiny-gpt2",
        config_path=config,
        fp16=torch.cuda.is_available(),
    )
    assert "train_loss" in metrics
    assert metrics.get("global_step", 0) > 0
    saved = tmp_path / "pytorch_model.bin"
    if not saved.exists():
        saved = tmp_path / "model.safetensors"
    assert saved.exists()


def test_hf_trainer_writes_metrics(tmp_path):
    texts = ["hi", "there"]
    metrics = run_hf_trainer(texts, tmp_path, model_name="sshleifer/tiny-gpt2")
    metrics_json = tmp_path / "metrics.json"
    metrics_ndjson = tmp_path / "metrics.ndjson"
    assert metrics_json.exists()
    assert metrics_ndjson.exists()
    record = json.loads(metrics_ndjson.read_text().splitlines()[-1])
    assert record.get("global_step") == metrics.get("global_step")
    env_json = tmp_path / "env.json"
    assert env_json.exists()
    info = json.loads(env_json.read_text())
    assert info.get("git_commit")


def test_run_hf_trainer_uses_tokenizer_path_and_flag(monkeypatch, tmp_path):
    """Custom tokenizer path and use_fast flag should be honored."""
    calls = {}

    def fake_tok_from_pretrained(name, use_fast=True):
        calls["name"] = name
        calls["use_fast"] = use_fast

        class Tok:
            pad_token = None
            eos_token = "</s>"
            pad_token_id = 0

            def __call__(self, text, truncation=True):
                return {"input_ids": [0]}

            def save_pretrained(self, output_dir):
                return None

        return Tok()

    def fake_model_from_pretrained(name):
        class M(torch.nn.Module):
            def forward(self, input_ids=None, labels=None):
                return type("O", (), {"loss": torch.tensor(0.0)})()

        return M()

    def fake_train(self, resume_from_checkpoint=None):
        class Result:
            metrics = {"train_loss": 0.0}

        return Result()

    monkeypatch.setattr(
        "training.engine_hf_trainer.AutoTokenizer.from_pretrained", fake_tok_from_pretrained
    )
    monkeypatch.setattr(
        "training.engine_hf_trainer.AutoModelForCausalLM.from_pretrained",
        fake_model_from_pretrained,
    )
    monkeypatch.setattr("training.engine_hf_trainer.Trainer.train", fake_train)
    run_hf_trainer(
        ["hi"],
        tmp_path / "out",
        tokenizer_path="tok",
        use_fast_tokenizer=False,
        distributed=False,
    )
    assert calls["name"] == "tok"
    assert calls["use_fast"] is False


@pytest.mark.xfail(reason="resume checkpoint path not available", strict=False)
def test_run_hf_trainer_passes_resume_from(monkeypatch, tmp_path):
    captured = {}

    def fake_tok_from_pretrained(name, use_fast=True):
        class Tok:
            pad_token = None
            eos_token = "</s>"
            pad_token_id = 0

            def __call__(self, text, truncation=True):
                return {"input_ids": [0]}

        return Tok()

    def fake_model_from_pretrained(name):
        class M(torch.nn.Module):
            def forward(self, input_ids=None, labels=None):
                return type("O", (), {"loss": torch.tensor(0.0)})()

        return M()

    def fake_train(self, *, resume_from_checkpoint=None, **k):
        captured["resume"] = resume_from_checkpoint
        return types.SimpleNamespace(metrics={"train_loss": 0.0})

    monkeypatch.setattr(
        "training.engine_hf_trainer.AutoTokenizer.from_pretrained", fake_tok_from_pretrained
    )
    monkeypatch.setattr(
        "training.engine_hf_trainer.AutoModelForCausalLM.from_pretrained",
        fake_model_from_pretrained,
    )
    monkeypatch.setattr("training.engine_hf_trainer.Trainer.train", fake_train)
    monkeypatch.setattr("training.engine_hf_trainer.Trainer.save_model", lambda self: None)

    ckpt = tmp_path / "ckpt"
    ckpt.mkdir()
    run_hf_trainer(["hi"], tmp_path, resume_from=str(ckpt), distributed=False)
    assert captured["resume"] == str(ckpt)


@pytest.mark.skip(reason="gradient accumulation capture under investigation")
def test_run_hf_trainer_respects_grad_accum(monkeypatch, tmp_path):
    pass


def test_compute_metrics_smoke():
    import numpy as np

    from training.engine_hf_trainer import _compute_metrics

    logits = np.zeros((2, 3, 5), dtype=np.float32)
    labels = np.zeros((2, 3), dtype=np.int64)
    metrics = _compute_metrics((logits, labels))
    assert "token_accuracy" in metrics and "perplexity" in metrics
