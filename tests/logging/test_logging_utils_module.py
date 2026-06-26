"""
Test Logging Utils Module

Test module for logging utils module.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import pytest

import logging_utils


def test_init_tensorboard_returns_writer(monkeypatch: pytest.MonkeyPatch) -> None:
    created: dict[str, str] = {}

    class FakeWriter:
        def __init__(self, log_dir: str) -> None:
            created["dir"] = log_dir

        def close(self) -> None:  # pragma: no cover - not used in test
            pass

    monkeypatch.setattr(logging_utils, "SummaryWriter", FakeWriter)
    writer = logging_utils.init_tensorboard("logs/tb")
    assert isinstance(writer, FakeWriter)
    assert created["dir"] == "logs/tb", "Condition must be true"


def test_init_mlflow_handles_missing_dependency(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(logging_utils, "mlflow", None)
    mlflow_module, run = logging_utils.init_mlflow("demo-run")
    assert mlflow_module is None, "mlflow_module is not valid"
    assert run is None, "run is not valid"


def test_init_mlflow_start_run(monkeypatch: pytest.MonkeyPatch) -> None:
    recorded: dict[str, object] = {}

    class FakeRun:
        pass

    class FakeMlflow:
        def set_tracking_uri(self, uri: str) -> None:
            recorded["uri"] = uri

        def set_experiment(self, name: str) -> None:
            recorded["experiment"] = name

        def start_run(self, run_name: str, tags: dict[str, str] | None = None) -> FakeRun:
            recorded["run_name"] = run_name
            recorded["tags"] = tags
            return FakeRun()

        def end_run(self) -> None:  # pragma: no cover - not used in tests
            recorded["ended"] = True

    monkeypatch.setattr(logging_utils, "mlflow", FakeMlflow())
    mlflow_module, run = logging_utils.init_mlflow(
        "demo-run", tracking_uri="file:./mlruns", tags={"env": "test"}
    )
    assert isinstance(run, FakeRun)
    assert isinstance(mlflow_module, FakeMlflow)
    assert recorded["experiment"] == "demo-run", "rec is not valid"
    assert recorded["run_name"] == "demo-run", "rec is not valid"
    assert recorded["tags"] == {"env": "test"}, "rec is not valid"
    assert recorded["uri"] == "file:./mlruns", "rec is not valid"
