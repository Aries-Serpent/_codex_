from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any
import pytest


def _inject_fake_mlflow(tmp_path: Path) -> ModuleType:
    """Create and inject a minimal fake mlflow module into sys.modules."""
    fake = ModuleType("mlflow")

    def set_tracking_uri(uri: str) -> None:
        # no-op; present to be called by the helper
        return None

    def set_experiment(exp: str) -> None:
        return None

    def start_run(*_, **__):
        # mimic mlflow.start_run as a context manager
        return __import__("contextlib").nullcontext("run")

    fake.set_tracking_uri = set_tracking_uri
    fake.set_experiment = set_experiment
    fake.start_run = start_run
    sys.modules["mlflow"] = fake
    return fake


def test_start_run_no_mlflow_accepts_noop_or_raise(monkeypatch):
    """
    When the 'mlflow' package is not present, accept either:
    - no-op context manager yielding a falsy value (None/False), or
    - raising a RuntimeError.
    This preserves compatibility across historical implementations.
    """
    monkeypatch.setitem(sys.modules, "mlflow", None)
    # Import the helper module under test
    mfu = importlib.import_module("codex_ml.tracking.mlflow_utils")
    try:
        with mfu.start_run("exp") as run:
            assert run in (None, False)
    except RuntimeError:
        pass


def test_start_run_disabled_returns_noop():
    """When MlflowConfig.enable is False, start_run should be a no-op yielding a falsy value."""
    mfu = importlib.import_module("codex_ml.tracking.mlflow_utils")
    cfg = mfu.MlflowConfig(enable=False)
    with mfu.start_run(cfg) as run:
        assert run in (None, False)


def test_seed_snapshot_writes_json(tmp_path: Path) -> None:
    """seed_snapshot writes seeds.json and returns its path."""
    mfu = importlib.import_module("codex_ml.tracking.mlflow_utils")
    seeds = {"python": 0}
    path = mfu.seed_snapshot(seeds, tmp_path)
    assert json.loads(path.read_text(encoding="utf-8")) == seeds


def test_seed_snapshot_logs_artifact_when_enabled(monkeypatch, tmp_path: Path) -> None:
    """
    seed_snapshot should write seeds.json and call the artifact-logging helper.
    We inject a fake mlflow_utils.log_artifacts to capture calls.
    """
    mfu = importlib.import_module("codex_ml.tracking.mlflow_utils")
    logged: dict[str, str] = {}

    def fake_log(p: Path | str, **_: Any) -> None:  # flexible signature
        logged["path"] = str(p)

    monkeypatch.setattr(mfu, "log_artifacts", fake_log)
    out = mfu.seed_snapshot({"seed": 1}, tmp_path, enabled=True)
    assert out.exists() and logged["path"] == str(out)


def test_ensure_local_artifacts_writes_files(tmp_path: Path) -> None:
    """ensure_local_artifacts writes both summary.json and seeds.json locally."""
    mfu = importlib.import_module("codex_ml.tracking.mlflow_utils")
    summary = {"status": "ok"}
    seeds = {"numpy": 1}
    mfu.ensure_local_artifacts(tmp_path, summary, seeds)
    assert json.loads((tmp_path / "summary.json").read_text(encoding="utf-8")) == summary
    assert json.loads((tmp_path / "seeds.json").read_text(encoding="utf-8")) == seeds
