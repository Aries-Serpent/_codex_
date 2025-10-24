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
    assert any(call[0] == "set_tracking_uri" for call in fake.calls)
    assert ("log_metrics", ({"loss": 0.1}, 1)) in fake.calls
    assert ("end_run", None) in fake.calls


def test_training_engine_handles_missing_mlflow() -> None:
    engine = TrainingEngine(enable_mlflow=True, _mlflow_module=None)
    assert not engine.enable_mlflow
    assert engine.mlflow_error is not None
