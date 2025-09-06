import importlib
import json
from pathlib import Path

ie = importlib.import_module("codex_ml.tracking.init_experiment")


class DummyRun:
    def __init__(self, run_id: str = "dummy_run"):
        self.info = type("info", (), {"run_id": run_id})()


class DummyMlflow:
    def __init__(self):
        self.logged = {}

    def set_experiment(self, name):
        self.logged["experiment"] = name

    def start_run(self, run_name=None):
        self.logged["run_name"] = run_name
        run = DummyRun()
        self.logged["run_id"] = run.info.run_id
        return run

    def set_tags(self, tags):
        self.logged["tags"] = tags

    def log_metrics(self, metrics, step=None):
        self.logged["mlflow_metrics"] = (metrics, step)

    def end_run(self, run_id=None):
        self.logged["ended"] = run_id


def test_init_experiment_logging(tmp_path, monkeypatch):
    # Patch optional dependencies with dummy implementations
    dummy_mlflow = DummyMlflow()
    monkeypatch.setattr(ie, "mlflow", dummy_mlflow, raising=False)

    class DummyWandb:
        def __init__(self):
            self.logged = {}

        def init(self, project, config, mode="offline"):
            self.logged["init"] = (project, config, mode)
            return self

        def log(self, metrics, step=None):
            self.logged["metrics"] = (metrics, step)

        def finish(self):
            self.logged["finished"] = True

    dummy_wandb = DummyWandb()
    monkeypatch.setattr(ie, "wandb", dummy_wandb, raising=False)

    class DummyWriter:
        def __init__(self, log_dir):
            self.log_dir = log_dir
            self.events = []

        def add_scalar(self, k, v, step):
            self.events.append((k, v, step))

        def flush(self):
            self.flushed = True

        def close(self):
            self.closed = True

    monkeypatch.setattr(ie, "SummaryWriter", DummyWriter, raising=False)

    cfg = ie.ExperimentConfig(
        name="exp",
        output_dir=str(tmp_path),
        tensorboard=True,
        mlflow=True,
        wandb=True,
        tags={"a": "b"},
    )
    logger = ie.init_experiment(cfg)
    logger.log({"loss": 1.0}, step=1)
    logger.close()

    data = (Path(tmp_path) / "metrics.ndjson").read_text().strip().splitlines()
    assert json.loads(data[0])["loss"] == 1.0
    assert dummy_mlflow.logged["experiment"] == "exp"
    assert dummy_mlflow.logged["ended"] == dummy_mlflow.logged["run_id"]
    assert dummy_wandb.logged["metrics"][0]["loss"] == 1.0
