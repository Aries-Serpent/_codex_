from pathlib import Path
from types import SimpleNamespace
import contextlib
import importlib
import os

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


def test_start_run_sets_env(monkeypatch, tmp_path):
    mod = importlib.import_module("codex_ml.tracking.mlflow_utils")
    fake = SimpleNamespace(
        set_tracking_uri=lambda uri: None,
        set_experiment=lambda exp: None,
        start_run=lambda: contextlib.nullcontext("run"),
    )
    monkeypatch.setattr(mod, "_HAS_MLFLOW", True)
    monkeypatch.setattr(mod, "_mlf", fake)
    monkeypatch.delenv("MLFLOW_ENABLE_SYSTEM_METRICS", raising=False)
    cfg = mod.MlflowConfig(enable=True, tracking_uri=str(tmp_path), experiment="e")
    with mod.start_run(cfg) as run:
        assert run == "run"
    assert os.environ["MLFLOW_ENABLE_SYSTEM_METRICS"] == "false"
