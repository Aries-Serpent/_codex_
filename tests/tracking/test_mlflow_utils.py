from __future__ import annotations

import importlib
from pathlib import Path

import pytest


def test_start_run_disabled():
    mod = importlib.import_module("codex_ml.tracking.mlflow_utils")
    cfg = mod.MlflowConfig(enable=False)
    with mod.start_run(cfg) as run:
        assert run is False


def test_start_run_missing(monkeypatch):
    mod = importlib.import_module("codex_ml.tracking.mlflow_utils")
    cfg = mod.MlflowConfig(enable=True)
    monkeypatch.setattr(mod, "_HAS_MLFLOW", False)
    with pytest.raises(RuntimeError):
        mod.start_run(cfg)


def test_seed_snapshot(tmp_path, monkeypatch):
    mod = importlib.import_module("codex_ml.tracking.mlflow_utils")
    called = {}
    def fake_log(path, enabled=False):
        called["path"] = Path(path)
    monkeypatch.setattr(mod, "log_artifacts", fake_log)
    out = mod.seed_snapshot({"a": 1}, tmp_path, enabled=True)
    assert out.exists()
    assert called["path"] == out
