import json
import types
from pathlib import Path

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


def test_compute_metrics_smoke():
    import numpy as np

    from training.engine_hf_trainer import _compute_metrics

    logits = np.zeros((2, 3, 5), dtype=np.float32)
    labels = np.zeros((2, 3), dtype=np.int64)
    metrics = _compute_metrics((logits, labels))
    assert "token_accuracy" in metrics and "perplexity" in metrics


def test_run_hf_trainer_passes_resume_from(tmp_path, monkeypatch):
    texts = ["hi"]
    ckpt = tmp_path / "ckpt"
    ckpt.mkdir()
    captured = {}

    class DummyTrainer:
        def __init__(self, *a, **k):
            pass

        def train(self, *, resume_from_checkpoint=None, **k):
            captured["resume"] = resume_from_checkpoint
            return types.SimpleNamespace(metrics={})

    monkeypatch.setattr("training.engine_hf_trainer.Trainer", DummyTrainer)
    run_hf_trainer(texts, tmp_path, model_name="sshleifer/tiny-gpt2", resume_from=str(ckpt))
    assert captured["resume"] == str(ckpt)


def test_run_hf_trainer_ignores_missing_resume_from(tmp_path, monkeypatch):
    captured = {}

    class DummyTrainer:
        def __init__(self, *a, **k):
            pass

        def train(self, *, resume_from_checkpoint=None, **k):
            captured["resume"] = resume_from_checkpoint
            return types.SimpleNamespace(metrics={})

    monkeypatch.setattr("training.engine_hf_trainer.Trainer", DummyTrainer)
    run_hf_trainer(["hi"], tmp_path, model_name="sshleifer/tiny-gpt2", resume_from="missing")
    assert captured["resume"] is None
