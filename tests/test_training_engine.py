import pytest

pytest.importorskip("mlflow")
"""
Test Training Engine

Test module for training engine.
"""

from __future__ import annotations

from pathlib import Path

from codex_ml.training.engine import TrainingEngine


class _FakeMLflow:
    def __init__(self) -> None:
        self.calls: list[tuple[str, object]] = []

    def set_tracking_uri(self, uri: str) -> None:
        self.calls.append(("set_tracking_uri", uri))

    def set_experiment(self, name: str) -> None:
        self.calls.append(("set_experiment", name))

    def start_run(self, **kwargs: object) -> str:
        self.calls.append(("start_run", kwargs))
        return "run"

    def log_metrics(self, metrics: dict[str, float], step: int | None = None) -> None:
        self.calls.append(("log_metrics", (metrics, step)))

    def log_params(self, params: dict[str, object]) -> None:
        self.calls.append(("log_params", dict(params)))

    def set_tags(self, tags: dict[str, str]) -> None:
        self.calls.append(("set_tags", dict(tags)))

    def log_artifact(self, path: str, artifact_path: str | None = None) -> None:
        self.calls.append(("log_artifact", (path, artifact_path)))

    def end_run(self) -> None:
        self.calls.append(("end_run", None))


def test_training_engine_configures_mlflow(tmp_path: Path) -> None:
    fake = _FakeMLflow()
    engine = TrainingEngine(
        enable_mlflow=True,
        mlflow_dir=str(tmp_path / "runs"),
        mlflow_experiment="demo",
        mlflow_run_name="unit-test",
        _mlflow_module=fake,
    )
    engine.start_run()
    engine.log_metrics({"loss": 0.1}, step=1)
    engine.end_run()
    assert any(call[0] == "set_tracking_uri" for call in fake.calls), "Condition must be true"
    assert ("log_metrics", ({"loss": 0.1}, 1)) in fake.calls
    assert ("end_run", None) in fake.calls


def test_training_engine_handles_missing_mlflow() -> None:
    engine = TrainingEngine(enable_mlflow=True, _mlflow_module=None)
    assert not engine.enable_mlflow, "Condition must be true"
    assert engine.mlflow_error is not None, "mlflow_error must be initialized"


def test_training_engine_logs_params_tags_and_artifacts(tmp_path: Path) -> None:
    fake = _FakeMLflow()
    engine = TrainingEngine(
        enable_mlflow=True,
        _mlflow_module=fake,
        mlflow_run_name="demo",
        mlflow_tags={"env": "dev"},
    )
    engine.log_params({"lr": 0.001, "epochs": 4, "amp": True, "skip": None})
    engine.set_tags({"stage": "warmup", "empty": None})
    engine.register_dataset("tiny", version="v1", uri=tmp_path / "train.jsonl")
    artifact = tmp_path / "metrics.json"
    artifact.write_text("{}", encoding="utf-8")
    engine.start_run()
    engine.log_artifact(artifact)
    engine.log_metrics({"loss": 0.1}, step=1)
    engine.end_run()

    log_params_calls = [payload for name, payload in fake.calls if name == "log_params"]
    assert log_params_calls, fake.calls
    assert any(call["amp"] == 1 for call in log_params_calls), "Condition must be true"
    assert all("skip" not in call for call in log_params_calls), "Condition must be true"

    tag_calls = [payload for name, payload in fake.calls if name == "set_tags"]
    assert tag_calls, "tag_calls is not valid"
    assert any("dataset.0.name" in call for call in tag_calls), "Data must not be empty"

    assert ("log_artifact", (str(artifact), None)) in fake.calls
