"""
pytest.importorskip("tensorboard")
Test Resume

Test module for resume.
"""

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from codex.cli import cli
from src.training.engine_hf_trainer import run_hf_trainer
from tests.test_engine_hf_trainer import _install_minimal_hf_stubs

pytest.importorskip("torch")
pytest.importorskip("transformers")
pytest.importorskip("datasets")
pytest.importorskip("accelerate")
pytest.importorskip("yaml")


def write_manifest(
    run_dir: Path, *, config=None, config_path=None, manifest_version: int | None = 1
):
    manifest = {
        "manifest_version": manifest_version,
        "checkpoint_dir": str(run_dir / "checkpoints"),
        "last_checkpoint": None,
        "best_checkpoint": None,
        "global_step": 0,
        "resume_from": None,
        "config_path": config_path,
        "copied_config_path": None,
        "config": config,
    }
    manifest_path = run_dir / "resume_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")


def test_resume_prefers_manifest_snapshot(monkeypatch, tmp_path):
    monkeypatch.setenv("DISABLE_MLFLOW_INTEGRATION", "1")
    monkeypatch.setenv("MLFLOW_TRACKING_URI", "")
    _install_minimal_hf_stubs(monkeypatch, tmp_path)
    run_dir = tmp_path / "run1"
    hydra_cfg = {"model_name": "tiny-gpt", "training": {"lr": 0.001}}
    run_hf_trainer(
        ["hello", "world"],
        run_dir,
        model_name="sshleifer/tiny-gpt2",
        hydra_cfg=hydra_cfg,
        distributed=False,
        metrics_writer="none",
    )

    runner = CliRunner()
    result = runner.invoke(cli, ["resume", str(run_dir)])
    assert result.exit_code == 0, "Result must not be empty"
    assert "config snapshot" in result.output, "Result must not be empty"
    assert '"lr": 0.001' in result.output, "Result must not be empty"


def test_resume_uses_copied_config_file_when_snapshot_missing(tmp_path):
    runner = CliRunner()
    run_dir = tmp_path / "run2"
    run_dir.mkdir()
    write_manifest(run_dir, config=None, config_path="configs/training/base.yaml")
    copied = run_dir / "resume_config.yaml"
    copied.write_text("learning_rate: 0.002\nbatch_size: 4", encoding="utf-8")

    result = runner.invoke(cli, ["resume", str(run_dir)])
    assert result.exit_code == 0, "Result must not be empty"
    assert "Using copied config file" in result.output, "Result must not be empty"
    assert "learning_rate: 0.002" in result.output, "Result must not be empty"


def test_resume_fails_when_no_snapshot_or_path(tmp_path):
    runner = CliRunner()
    run_dir = tmp_path / "run3"
    run_dir.mkdir()
    write_manifest(run_dir, config=None, config_path=None)

    result = runner.invoke(cli, ["resume", str(run_dir)])
    assert result.exit_code != 0, "Result must not be empty"
    assert "ERROR: No configuration snapshot or config_path available" in result.output, "Result must not be empty"
