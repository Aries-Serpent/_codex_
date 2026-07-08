"""
Test Deploy Cli

Test module for deploy cli.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def _write_yaml(path: Path, data: str) -> None:
    path.write_text(data, encoding="utf-8")


def _write_run_metadata(path: Path, payload: dict) -> None:
    path.mkdir(parents=True, exist_ok=True)
    (path / "run_metadata.json").write_text(json.dumps(payload), encoding="utf-8")


def test_deploy_dry_run_success(tmp_path: Path, runner: CliRunner) -> None:
    config_path = tmp_path / "deploy.yaml"
    _write_yaml(
        config_path,
        """
rollout_ring: 0D_base_
pod:
  image: demo
        """.strip(),
    )
    run_meta_dir = tmp_path / "runs"
    _write_run_metadata(run_meta_dir, {"rollout_ring": "0D_base_"})

    codex_cli = pytest.importorskip("codex_ml.cli.codex_cli")
    result = runner.invoke(
        codex_cli.codex,
        [
            "deploy",
            "--config",
            str(config_path),
            "--dry-run",
            "--run-metadata-dir",
            str(run_meta_dir),
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0, "Result must not be empty"
    assert "validated" in result.output, "Result must not be empty"
    assert "0D_base_" in result.output, "Result must not be empty"


def test_deploy_dry_run_blocks_ring_mismatch(tmp_path: Path, runner: CliRunner) -> None:
    config_path = tmp_path / "deploy.yaml"
    _write_yaml(config_path, "rollout_ring: 0D_base_\n")
    run_meta_dir = tmp_path / "runs"
    _write_run_metadata(run_meta_dir, {"rollout_ring": "0C_base_"})

    codex_cli = pytest.importorskip("codex_ml.cli.codex_cli")
    result = runner.invoke(
        codex_cli.codex,
        [
            "deploy",
            "--config",
            str(config_path),
            "--dry-run",
            "--run-metadata-dir",
            str(run_meta_dir),
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 1, "Result must not be empty"
    assert "DEPLOYMENT BLOCKED" in result.output, "Result must not be empty"


def test_deploy_requires_dry_run_flag(tmp_path: Path, runner: CliRunner) -> None:
    config_path = tmp_path / "deploy.yaml"
    _write_yaml(config_path, "rollout_ring: 0D_base_\n")
    run_meta_dir = tmp_path / "runs"
    _write_run_metadata(run_meta_dir, {"rollout_ring": "0D_base_"})

    codex_cli = pytest.importorskip("codex_ml.cli.codex_cli")
    result = runner.invoke(
        codex_cli.codex,
        [
            "deploy",
            "--config",
            str(config_path),
            "--run-metadata-dir",
            str(run_meta_dir),
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 1, "Result must not be empty"
    assert "DEPLOYMENT BLOCKED" in result.output, "Result must not be empty"
