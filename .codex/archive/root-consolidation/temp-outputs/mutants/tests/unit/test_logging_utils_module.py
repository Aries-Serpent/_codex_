"""
pytest.importorskip("tensorboard")
Test Logging Utils Module

Test module for logging utils module.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from src import logging_utils


def test_init_tensorboard(monkeypatch: pytest.MonkeyPatch) -> None:
    created = {}

    class Writer:
        def __init__(self, log_dir: str) -> None:
            created["log_dir"] = log_dir

        def add_scalar(self, *_args, **_kwargs) -> None:  # pragma: no cover - not used
            pass

    original_import = logging_utils.import_module

    monkeypatch.setattr(
        logging_utils,
        "import_module",
        lambda name: (
            SimpleNamespace(SummaryWriter=Writer)
            if name == "torch.utils.tensorboard"
            else original_import(name)
        ),
    )
    writer = logging_utils.init_tensorboard(True, "runs/test")
    assert created["log_dir"] == "runs/test", "Condition must be true"
    assert writer is not None, "writer must be initialized"


def test_init_mlflow(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: dict[str, tuple] = {}

    class FakeMLflow:
        def __init__(self) -> None:
            self.tracking_uri = None
            self.experiment = None

        def set_tracking_uri(self, uri: str) -> None:
            self.tracking_uri = uri

        def set_experiment(self, experiment: str) -> None:
            self.experiment = experiment

        def start_run(self, run_name: str) -> None:
            calls["start_run"] = (run_name,)

        def log_metrics(self, metrics, step=None):
            calls["metrics"] = (dict(metrics), step)

        def log_params(self, params):
            calls["params"] = dict(params)

        def end_run(self):
            calls["ended"] = True

    fake_mlflow = FakeMLflow()
    original_import = logging_utils.import_module

    monkeypatch.setattr(
        logging_utils,
        "import_module",
        lambda name: fake_mlflow if name == "mlflow" else original_import(name),
    )
    handle = logging_utils.init_mlflow(
        True, "demo", tracking_uri="file:./mlruns", experiment="codex"
    )
    assert handle is not None, "handle must be initialized"
    handle.log_metrics({"loss": 1.0}, step=3)
    handle.log_params({"lr": 1e-3})
    handle.end()
    assert fake_mlflow.tracking_uri == "file:./mlruns", "tracking_uri is not valid"
    assert fake_mlflow.experiment == "codex", "experiment is not valid"
    assert calls["start_run"] == ("demo",)
    assert calls["metrics"] == ({"loss": 1.0}, 3)
    assert calls["params"] == {"lr": 1e-3}, "Condition must be true"
    assert calls["ended"] is True, "Condition must be true"


def test_tensorboard_missing_dependency(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        logging_utils, "import_module", lambda name: (_ for _ in ()).throw(ModuleNotFoundError)
    )
    assert logging_utils.init_tensorboard(True) is None, "Condition must be true"
