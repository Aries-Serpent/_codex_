from __future__ import annotations

import json

import pytest

from codex_ml.metrics.registry import get_metric


def test_weighted_accuracy_offline(tmp_path):
    weights_file = tmp_path / "weights.json"
    weights_file.write_text(json.dumps({"0": 1.0, "1": 2.0}), encoding="utf-8")

    metric = get_metric("offline:weighted-accuracy")
    score = metric([0, 1, 1], [0, 1, 0], weights_path=str(weights_file))
    assert pytest.approx(score) == 0.75


def test_weighted_accuracy_missing(tmp_path, monkeypatch):
    missing = tmp_path / "missing.json"
    monkeypatch.delenv("CODEX_ML_WEIGHTED_ACCURACY_PATH", raising=False)
    monkeypatch.setenv("CODEX_ML_OFFLINE_METRICS_DIR", str(tmp_path / "other"))

    metric = get_metric("offline:weighted-accuracy")
    with pytest.raises(FileNotFoundError):
        metric([1], [1], weights_path=str(missing))
