import contextlib
from pathlib import Path

import pytest

from codex_ml.tracking import mlflow_utils as MU


class DummyMLF:
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


def test_start_run_and_logging(monkeypatch, tmp_path):
    dummy = DummyMLF()
    monkeypatch.setattr(MU, "_mlf", dummy)
    MU._HAS_MLFLOW = True
    with MU.start_run(
        "exp", tracking_uri=str(tmp_path), run_tags={"a": "b"}, enable_system_metrics=True
    ) as ctx:
        assert ctx == "run"
    MU.log_params({"p": 1}, enabled=True)
    MU.log_metrics({"loss": 1.0, "_step": 2, "bad": 0}, enabled=True)
    f = tmp_path / "f.txt"
    f.write_text("x")
    d = tmp_path / "d"
    d.mkdir()
    (d / "a.txt").write_text("y")
    MU.log_artifacts([f, d], enabled=True)
    MU.seed_snapshot({"s": 1}, tmp_path, enabled=True)
    MU.ensure_local_artifacts(tmp_path, {"m": 1}, {"s": 1}, enabled=True)
    assert dummy.params == {"p": 1}
    assert ("loss", 1.0, 2) in dummy.metrics
    assert "f.txt" in dummy.artifacts and "d" in dummy.artifacts


def test_noop_helpers(tmp_path):
    MU._mlf = None
    MU._HAS_MLFLOW = False
    MU.log_params({"a": 1})
    MU.log_metrics({}, enabled=False)
    MU.log_artifacts(tmp_path, enabled=False)


def test_start_run_disabled():
    with MU.start_run(None) as ctx:
        assert ctx is None


def test_start_run_no_tracking(monkeypatch):
    dummy = DummyMLF()
    monkeypatch.setattr(MU, "_mlf", dummy)
    MU._HAS_MLFLOW = True
    with MU.start_run(MU.MlflowConfig(enable=True, tracking_uri=None)) as ctx:
        assert ctx == "run"


def test_log_params_missing_mlflow(monkeypatch):
    MU._mlf = None
    MU._HAS_MLFLOW = False
    monkeypatch.setattr(
        MU, "_ensure_mlflow_available", lambda: (_ for _ in ()).throw(RuntimeError("no mlflow"))
    )
    with pytest.raises(RuntimeError):
        MU.log_params({"a": 1}, enabled=True)


def test_ensure_mlflow_available(monkeypatch):
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
    cfg = MU._coerce_config(
        MU.MlflowConfig(enable=True, experiment="e"),
        tracking_uri="t",
        experiment="e2",
        run_tags={"a": "b"},
        enable_system_metrics=True,
    )
    assert cfg.enable and cfg.tracking_uri == "t" and cfg.experiment == "e2"
