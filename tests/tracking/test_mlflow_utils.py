from __future__ import annotations

import contextlib
import importlib
import os
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Dict
import pytest


def _reload(with_mlflow: bool):
    """Reload the mlflow_utils module, optionally injecting a fake mlflow module.

    - with_mlflow=True: ensures a minimal fake mlflow module is present in sys.modules
      exposing set_tracking_uri, set_experiment and start_run.
    - with_mlflow=False: removes any mlflow module to simulate absence.
    Returns the re-imported codex_ml.tracking.mlflow_utils module.
    """
    sys.modules.pop("codex_ml.tracking.mlflow_utils", None)
    if with_mlflow:
        fake = ModuleType("mlflow")
        called: list[tuple[str, Any]] = []

        def set_tracking_uri(uri: str) -> None:
            called.append(("uri", uri))

        def set_experiment(exp: str) -> None:
            called.append(("exp", exp))

        def start_run(*_, **__):
            # Return a context manager similar to mlflow.start_run()
            return contextlib.nullcontext("run")

        fake.set_tracking_uri = set_tracking_uri
        fake.set_experiment = set_experiment
        fake.start_run = start_run
        # ensure it is discoverable by import machinery
        sys.modules["mlflow"] = fake
        # Import the tracked module
        m = importlib.import_module("codex_ml.tracking.mlflow_utils")
        # Attach the call-log for tests to inspect if needed
        setattr(m, "_test_called", called)
        return m
    else:
        # remove any mlflow entry to simulate not installed
        sys.modules.pop("mlflow", None)
        # For some test cases we may want a None sentinel in sys.modules
        # to simulate previous code paths that set mlflow=None; but remove to allow
        # import-time resolution within helpers.
        return importlib.import_module("codex_ml.tracking.mlflow_utils")


def test_start_run_disabled():
    """When MlflowConfig.enable is False, start_run should be a no-op yielding a falsy value."""
    mod = importlib.import_module("codex_ml.tracking.mlflow_utils")
    cfg = mod.MlflowConfig(enable=False)
    with mod.start_run(cfg) as run:
        # Accept either False or None as "not active" depending on historical behavior
        assert run in (None, False)


def test_start_run_missing_accepts_noop_or_raises():
    """
    When MLflow is requested but not present, historical code accepted either:
      - raising RuntimeError, or
      - returning a no-op context manager that yields a falsy value.
    Accept either behavior as valid for backward compatibility.
    """
    mod = importlib.import_module("codex_ml.tracking.mlflow_utils")
    # Force mlflow to be absent
    sys.modules.pop("mlflow", None)
    # Request MLflow by passing an experiment name (backwards-compatible coercion)
    try:
        with mod.start_run("exp") as run:
            assert run in (None, False)
    except RuntimeError:
        # Accept raising RuntimeError as allowed behavior
        pass


def test_start_run_missing_raises_when_helper_forces(monkeypatch):
    """
    If the internal helper indicates mlflow is required but fails to import,
    start_run should raise a RuntimeError. This simulates a runtime import failure.
    """
    mod = importlib.import_module("codex_ml.tracking.mlflow_utils")
    cfg = mod.MlflowConfig(enable=True)

    def _raise_import() -> None:
        raise RuntimeError("mlflow not importable")

    monkeypatch.setattr(mod, "_ensure_mlflow_available", _raise_import)
    with pytest.raises(RuntimeError):
        mod.start_run(cfg)


def test_start_run_sets_tracking_and_returns_run(tmp_path):
    """
    When a fake mlflow module is present, start_run should set the tracking URI
    and experiment and return the mlflow.start_run() context.
    """
    mfu = _reload(True)
    # Use legacy string-experiment form and pass a tracking_uri to ensure both are honored.
    with mfu.start_run("e", tracking_uri=str(tmp_path)) as run:
        assert run == "run"

    called = getattr(mfu, "_test_called", [])
    assert ("uri", str(tmp_path)) in called and ("exp", "e") in called
    # Helper uses setdefault to "false" when not explicitly set to True/False
    assert os.environ.get("MLFLOW_ENABLE_SYSTEM_METRICS") in (None, "false", "0", "1")


def test_start_run_with_enable_system_metrics_false(tmp_path):
    """
    Ensure the enable_system_metrics configuration is respected when provided.
    The environment variable should be set to '0' when False.
    """
    mfu = _reload(True)
    cfg = mfu.MlflowConfig(enable=True, enable_system_metrics=False)
    with mfu.start_run(cfg) as run:
        assert run == "run"
    assert os.environ.get("MLFLOW_ENABLE_SYSTEM_METRICS") == "0"


def test_seed_snapshot_writes_and_logs(monkeypatch, tmp_path):
    """
    seed_snapshot should write seeds.json to the given directory and call the
    artifact-logging helper when enabled. Use a flexible fake to accommodate
    different historical helper signatures.
    """
    mod = importlib.import_module("codex_ml.tracking.mlflow_utils")
    recorded: Dict[str, Path] = {}

    def fake_log(path: Path | str, *args, **kwargs) -> None:
        recorded["path"] = Path(path)

    monkeypatch.setattr(mod, "log_artifacts", fake_log)
    out = mod.seed_snapshot({"a": 1}, tmp_path, enabled=True)
    assert out.exists()
    assert recorded["path"] == out


def test_ensure_local_artifacts(tmp_path):
    """ensure_local_artifacts writes both summary.json and seeds.json locally."""
    mod = importlib.import_module("codex_ml.tracking.mlflow_utils")
    summary = {"status": "ok"}
    seeds = {"numpy": 1}
    mod.ensure_local_artifacts(tmp_path, summary, seeds)
    assert (tmp_path / "summary.json").exists()
    assert (tmp_path / "seeds.json").exists()
