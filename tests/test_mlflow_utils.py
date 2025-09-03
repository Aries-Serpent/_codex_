import contextlib
import importlib
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

from codex_ml.tracking import mlflow_utils as MU


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
        return contextlib.nullcontext("run")

    fake.set_tracking_uri = set_tracking_uri
    fake.set_experiment = set_experiment
    fake.start_run = start_run
    sys.modules["mlflow"] = fake
    return fake


class DummyMLF:
    """Mock MLflow client for testing purposes."""
    
    def __init__(self):
        self.params = None
        self.metrics = []
        self.artifacts = []
        self.tracking_uri = None
        self.experiment = None
        self.tags = None

    def set_tracking_uri(self, uri):
        self.tracking_uri = uri

    def set_experiment(self, exp):
        self.experiment = exp

    def start_run(self, tags=None):
        self.tags = tags
        return contextlib.nullcontext("run")

    def log_params(self, d):
        self.params = d

    def log_metric(self, k, v, step=None):
        if k == "bad":
            raise ValueError("bad")
        self.metrics.append((k, v, step))

    def log_artifact(self, path):
        self.artifacts.append(Path(path).name)

    def log_artifacts(self, path):
        self.artifacts.append(Path(path).name)


def test_start_run_no_mlflow_accepts_noop_or_raise(monkeypatch):
    """
    When the 'mlflow' package is not present, accept either:
    - no-op context manager yielding a falsy value (None/False), or
    - raising a RuntimeError.
    This preserves compatibility across historical implementations.
    """
    # Import the helper module under test then simulate mlflow missing
    mfu = importlib.import_module("codex_ml.tracking.mlflow_utils")
    monkeypatch.setattr(mfu, "_HAS_MLFLOW", False, raising=False)
    monkeypatch.setattr(mfu, "_mlf", None, raising=False)
    real_import = importlib.import_module

    def fake_import(name, *args, **kwargs):
        if name == "mlflow":
            raise ImportError("mlflow not installed")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(importlib, "import_module", fake_import)
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


def test_start_run_and_logging(monkeypatch, tmp_path):
    """Test comprehensive MLflow step logging with proper step parameter handling."""
    dummy = DummyMLF()
    monkeypatch.setattr(MU, "_mlf", dummy)
    MU._HAS_MLFLOW = True
    
    with MU.start_run(
        "exp", tracking_uri=str(tmp_path), run_tags={"a": "b"}, enable_system_metrics=True
    ) as ctx:
        assert ctx == "run"
    
    # Test parameter logging
    MU.log_params({"p": 1}, enabled=True)
    
    # Test metrics logging with step parameter - this clarifies MLflow step logging expectations
    MU.log_metrics({"loss": 1.0, "_step": 2, "bad": 0}, enabled=True)
    
    # Test artifact logging
    f = tmp_path / "f.txt"
    f.write_text("x")
    d = tmp_path / "d"
    d.mkdir()
    (d / "a.txt").write_text("y")
    MU.log_artifacts([f, d], enabled=True)
    MU.seed_snapshot({"s": 1}, tmp_path, enabled=True)
    MU.ensure_local_artifacts(tmp_path, {"m": 1}, {"s": 1}, enabled=True)
    
    # Verify step logging behavior
    assert dummy.params == {"p": 1}
    assert ("loss", 1.0, 2) in dummy.metrics  # Step parameter should be preserved
    assert "f.txt" in dummy.artifacts and "d" in dummy.artifacts


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


def test_noop_helpers(tmp_path):
    """Test that helpers work correctly when MLflow is not available."""
    MU._mlf = None
    MU._HAS_MLFLOW = False
    MU.log_params({"a": 1})
    MU.log_metrics({}, enabled=False)
    MU.log_artifacts(tmp_path, enabled=False)


def test_start_run_disabled():
    """Test start_run when disabled returns None context."""
    with MU.start_run(None) as ctx:
        assert ctx is None


def test_start_run_no_tracking(monkeypatch):
    """Test start_run without tracking URI but with MLflow available."""
    dummy = DummyMLF()
    monkeypatch.setattr(MU, "_mlf", dummy)
    MU._HAS_MLFLOW = True
    with MU.start_run(MU.MlflowConfig(enable=True, tracking_uri=None)) as ctx:
        assert ctx == "run"


def test_log_params_missing_mlflow(monkeypatch):
    """Test that missing MLflow raises appropriate error when enabled."""
    MU._mlf = None
    MU._HAS_MLFLOW = False
    monkeypatch.setattr(
        MU, "_ensure_mlflow_available", lambda: (_ for _ in ()).throw(RuntimeError("no mlflow"))
    )
    with pytest.raises(RuntimeError):
        MU.log_params({"a": 1}, enabled=True)


def test_ensure_mlflow_available(monkeypatch):
    """Test MLflow availability detection and module loading."""
    import importlib

    MU._mlf = None
    MU._HAS_MLFLOW = False
    dummy = object()
    monkeypatch.setattr(importlib, "import_module", lambda name: dummy)
    MU._ensure_mlflow_available()
    assert MU._mlf is dummy and MU._HAS_MLFLOW

    MU._mlf = None
    MU._HAS_MLFLOW = False
    monkeypatch.setattr(importlib, "import_module", lambda name: (_ for _ in ()).throw(ImportError))
    with pytest.raises(RuntimeError):
        MU._ensure_mlflow_available()


def test_coerce_config_object():
    """Test configuration object coercion with parameter overrides."""
    cfg = MU._coerce_config(
        MU.MlflowConfig(enable=True, experiment="e"),
        tracking_uri="t",
        experiment="e2",
        run_tags={"a": "b"},
        enable_system_metrics=True,
    )
    assert cfg.enable and cfg.tracking_uri == "t" and cfg.experiment == "e2"
