from __future__ import annotations

import contextlib
import importlib
import os
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict

import pytest


def test_start_run_disabled():
    """When MlflowConfig.enable is False, start_run should be a no-op yielding False."""
    mod = importlib.import_module("codex_ml.tracking.mlflow_utils")
    cfg = mod.MlflowConfig(enable=False)
    with mod.start_run(cfg) as run:
        assert run is False


def test_start_run_missing_raises(monkeypatch):
    """
    If MLflow is requested (enabled) but not importable, start_run should raise
    a RuntimeError. Simulate an import failure by forcing the module helper to
    raise.
    """
    mod = importlib.import_module("codex_ml.tracking.mlflow_utils")
    cfg = mod.MlflowConfig(enable=True)

    # Simulate mlflow import failing at runtime inside the helper
    def _raise_import() -> None:
        raise RuntimeError("mlflow not importable")

    monkeypatch.setattr(mod, "_ensure_mlflow_available", _raise_import)
    with pytest.raises(RuntimeError):
        mod.start_run(cfg)


def test_start_run_sets_tracking(monkeypatch, tmp_path):
    """
    When a real (or fake) mlflow module is available, start_run should set the
    tracking URI and experiment and return the mlflow run context.
    """
    mod = importlib.import_module("codex_ml.tracking.mlflow_utils")
    called: list[tuple[str, Any]] = []

    fake = SimpleNamespace(
        set_tracking_uri=lambda uri: called.append(("uri", uri)),
        set_experiment=lambda exp: called.append(("exp", exp)),
        start_run=lambda: contextlib.nullcontext("run"),
    )

    # Inject a fake mlflow into sys.modules so the import inside the helper picks it up.
    monkeypatch.setitem(sys.modules, "mlflow", fake)

    # Use the string-experiment form and pass a tracking_uri to ensure both are honored.
    with mod.start_run("e", tracking_uri=str(tmp_path)) as run:
        assert run == "run"

    # Confirm the calls occurred
    assert ("uri", str(tmp_path)) in called and ("exp", "e") in called
    # Ensure the env var was set (helper uses setdefault to "false")
    assert os.environ.get("MLFLOW_ENABLE_SYSTEM_METRICS") == "false"


def test_seed_snapshot(tmp_path, monkeypatch):
    """
    seed_snapshot should write seeds.json to the given directory and call the
    artifact-logging helper when enabled.
    """
    mod = importlib.import_module("codex_ml.tracking.mlflow_utils")
    called: Dict[str, Path] = {}

    def fake_log(path: Path | str, *args, **kwargs) -> None:
        called["path"] = Path(path)

    # Replace the log_artifacts function with our fake to observe calls.
    monkeypatch.setattr(mod, "log_artifacts", fake_log)

    out = mod.seed_snapshot({"a": 1}, tmp_path, enabled=True)
    assert out.exists()
    assert called["path"] == out
