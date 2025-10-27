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

    def log_params(self, params: dict[str, str]) -> None:
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
    assert any(call[0] == "set_tracking_uri" for call in fake.calls)
    assert ("log_metrics", ({"loss": 0.1}, 1)) in fake.calls
    assert ("end_run", None) in fake.calls


def test_training_engine_handles_missing_mlflow() -> None:
    engine = TrainingEngine(enable_mlflow=True, _mlflow_module=None)
    assert not engine.enable_mlflow
    assert engine.mlflow_error is not None


def test_training_engine_logs_metadata(tmp_path: Path) -> None:
    fake = _FakeMLflow()
    artifact = tmp_path / "artifact.txt"
    artifact.write_text("payload", encoding="utf-8")
    engine = TrainingEngine(
        enable_mlflow=True,
        mlflow_dir=str(tmp_path / "runs"),
        mlflow_experiment="demo",
        _mlflow_module=fake,
    )
    engine.start_run(
        params={"training.lr": 1e-4, "extras": {"warmup": 10}},
        tags={"phase": "train"},
        datasets=["data/train.jsonl", Path("data/eval.jsonl")],
    )
    engine.log_params({"optimizer": "adamw"})
    engine.set_tags({"stage": "pretrain"})
    engine.log_artifact(artifact, artifact_path="checkpoints")
    engine.end_run()

    assert ("log_params", {"optimizer": "adamw"}) in fake.calls
    assert (
        "log_params",
        {"training.lr": "0.0001", "extras": '{"warmup": 10}'},
    ) in fake.calls
    assert any(
        call for call in fake.calls if call[0] == "set_tags" and call[1].get("phase") == "train"
    )
    assert any(
        call
        for call in fake.calls
        if call[0] == "set_tags"
        and "codex.dataset.uris" in call[1]
        and "data/train.jsonl" in call[1]["codex.dataset.uris"]
        and "data/eval.jsonl" in call[1]["codex.dataset.uris"]
    )
    assert ("log_artifact", (str(artifact), "checkpoints")) in fake.calls
