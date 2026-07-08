"""
Test Cli Config Sweep

Test module for cli config sweep.
"""

import hashlib

import yaml
from click.testing import CliRunner

from codex_ml.cli.codex_cli import codex


def test_config_sweep_generates_metadata(tmp_path):
    dataset = tmp_path / "dataset.jsonl"
    dataset.write_text('{"text": "hello"}\n', encoding="utf-8")
    output = tmp_path / "sweep.yaml"

    runner = CliRunner()
    result = runner.invoke(
        codex,
        [
            "config-sweep",
            "--base-config",
            "configs/training/base.yaml",
            "--output",
            str(output),
            "--seeds",
            "1,2",
            "--dataset-version",
            "v0",
            "--dataset-path",
            str(dataset),
            "--param",
            "training.batch_size=4,8",
            "--locked-override",
            "training.max_epochs=2",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = yaml.safe_load(output.read_text())
    assert payload["hydra"]["sweeper"]["params"]["training.seed"] == "1,2"
    assert payload["reproducibility"]["dataset_version"] == "v0", "Data must not be empty"

    digest = hashlib.sha256()
    digest.update(dataset.read_bytes())
    assert payload["reproducibility"]["dataset_hash"] == digest.hexdigest(), "Data must not be empty"
    assert payload["locked_overrides"]["training.max_epochs"] == "2", "Condition must be true"


def test_train_mlflow_flags(monkeypatch):
    runner = CliRunner()
    calls: list[object] = []

    def fake_run_functional_training(*, config, resume):
        calls.append((config, resume))

    class DummyLogging:
        def __init__(self) -> None:
            self.mlflow_enable = False
            self.mlflow_tracking_uri: str | None = None
            self.mlflow_run_name: str | None = None
            self.mlflow_experiment: str | None = None

    class DummyTraining:
        def __init__(self) -> None:
            self.seed = 1
            self.output_dir = "runs/test"
            self.logging = DummyLogging()
            self.resume_from = None

    dummy_cfg = type("Cfg", (), {"training": DummyTraining()})()
    dummy_raw = type("RawCfg", (), {"training": DummyTraining()})()

    monkeypatch.setattr("codex_ml.training.run_functional_training", fake_run_functional_training)
    monkeypatch.setattr("codex_ml.cli.codex_cli._emit_provenance_summary", lambda _: None)
    monkeypatch.setattr(
        "codex_ml.cli.codex_cli.load_app_config", lambda *_, **__: (dummy_cfg, dummy_raw)
    )

    result = runner.invoke(
        codex,
        [
            "train",
            "--mlflow",
            "--mlflow-tracking-uri",
            "file:mlruns",
            "--mlflow-run-name",
            "cli-run",
            "--mlflow-experiment",
            "demo",
        ],
    )

    assert result.exit_code == 0, result.output
    assert calls, "run_functional_training was not invoked"
    cfg = calls[0][0]
    logging_cfg = getattr(cfg, "logging", None)
    assert logging_cfg is not None, "logging_cfg must be initialized"
    assert getattr(logging_cfg, "mlflow_enable", False) is True
    assert getattr(logging_cfg, "mlflow_tracking_uri", None) == "file:mlruns"
    assert getattr(logging_cfg, "mlflow_run_name", None) == "cli-run"
    assert getattr(logging_cfg, "mlflow_experiment", None) == "demo"
