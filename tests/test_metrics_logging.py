import json
from pathlib import Path

import pytest

pytest.importorskip("omegaconf")
pytest.importorskip("transformers")
pytest.importorskip("torch")

from codex.training import emit_validation_metric_record


def test_emit_validation_metric_record(tmp_path: Path) -> None:
    metrics = tmp_path / "metrics.json"
    payload = {
        "epoch": 0,
        "split": "val",
        "token_accuracy": 0.0,
        "perplexity": 1.0,
        "config": {"val_split": 0.1, "test_split": 0.0, "epoch": 0},
    }
    emit_validation_metric_record(str(metrics), payload)
    assert metrics.exists(), "metrics.json should be created"
    lines = metrics.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) >= 1
    for line in lines:
        rec = json.loads(line)
        assert rec.get("split") == "val"
        assert "token_accuracy" in rec and "perplexity" in rec
