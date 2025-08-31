import json
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


def test_compute_metrics_smoke():
    import numpy as np

    from training.engine_hf_trainer import _compute_metrics

    logits = np.zeros((2, 3, 5), dtype=np.float32)
    labels = np.zeros((2, 3), dtype=np.int64)
    metrics = _compute_metrics((logits, labels))
    assert "token_accuracy" in metrics and "perplexity" in metrics
