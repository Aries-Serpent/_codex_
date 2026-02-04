"""Tests for CLI config override behaviour in ``codex_ml.cli.main``."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import codex_ml.cli.main as cli_main
import codex_ml.training.unified_training as unified_training
import yaml
from typer.testing import CliRunner

pytest.importorskip("typer")
pytest.importorskip("yaml")


def _write_training_config(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(yaml.safe_dump(payload), encoding="utf-8")


def test_train_command_uses_config_defaults(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Ensure YAML config values populate the training dataclass."""

    config_payload = {
        "training": {
            "model_name": "offline-config-model",
            "epochs": 3,
            "batch_size": 16,
            "gradient_accumulation_steps": 4,
            "learning_rate": 1.0e-4,
            "seed": 123,
            "output_dir": str(tmp_path / "outputs"),
            "backend": "functional",
            "grad_clip_norm": 0.5,
            "dtype": "bf16",
            "resume_from": "checkpoint.pt",
            "mlflow_enable": True,
            "wandb_enable": True,
        }
    }
    config_path = tmp_path / "config.yaml"
    _write_training_config(config_path, config_payload)

    captured: dict[str, Any] = {}

    def _fake_run(cfg):
        captured["config"] = cfg
        return {"status": "ok"}

    monkeypatch.setattr(unified_training, "run_unified_training", _fake_run)

    runner = CliRunner()
    result = runner.invoke(cli_main.app, ["train", "--config", str(config_path)])

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    cfg = captured["config"]
    assert cfg.model_name == "offline-config-model"
    assert cfg.epochs == 3
    assert cfg.batch_size == 16
    assert cfg.grad_accum == 4
    assert cfg.learning_rate == pytest.approx(1.0e-4)
    assert cfg.seed == 123
    assert cfg.output_dir.endswith("outputs")
    assert cfg.backend == "functional"
    assert cfg.grad_clip_norm == pytest.approx(0.5)
    assert cfg.dtype == "bf16"
    assert cfg.resume_from == "checkpoint.pt"
    assert cfg.mlflow_enable is True
    assert cfg.wandb_enable is True


def test_train_command_prefers_cli_overrides(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """CLI options should take precedence over config defaults."""

    config_payload = {
        "training": {
            "model_name": "config-model",
            "epochs": 2,
            "batch_size": 4,
            "gradient_accumulation_steps": 2,
            "learning_rate": 5.0e-4,
            "seed": 11,
            "output_dir": str(tmp_path / "config-out"),
            "backend": "legacy",
            "grad_clip_norm": 1.5,
            "dtype": "fp32",
            "resume_from": "config.ckpt",
        }
    }
    config_path = tmp_path / "train.yaml"
    _write_training_config(config_path, config_payload)

    captured: dict[str, Any] = {}

    def _fake_run(cfg):
        captured["config"] = cfg
        return {"status": "overridden"}

    monkeypatch.setattr(unified_training, "run_unified_training", _fake_run)

    cli_output_dir = tmp_path / "cli-out"
    runner = CliRunner()
    result = runner.invoke(
        cli_main.app,
        [
            "train",
            "--config",
            str(config_path),
            "--model-name",
            "cli-model",
            "--epochs",
            "9",
            "--batch-size",
            "64",
            "--grad-accum",
            "3",
            "--learning-rate",
            "0.001",
            "--seed",
            "7",
            "--output-dir",
            str(cli_output_dir),
            "--backend",
            "functional",
            "--grad-clip-norm",
            "0.25",
            "--dtype",
            "fp16",
            "--resume-from",
            "cli.ckpt",
            "--mlflow",
            "--wandb",
        ],
    )

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    cfg = captured["config"]
    assert cfg.model_name == "cli-model"
    assert cfg.epochs == 9
    assert cfg.batch_size == 64
    assert cfg.grad_accum == 3
    assert cfg.learning_rate == pytest.approx(0.001)
    assert cfg.seed == 7
    assert Path(cfg.output_dir) == cli_output_dir
    assert cfg.backend == "functional"
    assert cfg.grad_clip_norm == pytest.approx(0.25)
    assert cfg.dtype == "fp16"
    assert cfg.resume_from == "cli.ckpt"
    assert cfg.mlflow_enable is True
    assert cfg.wandb_enable is True
