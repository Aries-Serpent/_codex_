from __future__ import annotations

import json
from pathlib import Path

import pytest

typer = pytest.importorskip("typer", reason="typer not installed")
from typer.testing import CliRunner  # type: ignore  # noqa: E402

from codex_ml.cli import checkpoint_validate  # noqa: E402
from codex_ml.utils import checkpoint_core  # noqa: E402


def _write_checkpoint(tmp_path: Path) -> Path:
    ckpt_dir = tmp_path / "epoch-1"
    payload = {"model_state": {"w": [1, 2, 3]}, "optimizer_state": {"lr": 0.1}}
    metadata = {"metrics": {"val_loss": 0.42}}
    checkpoint_core.save_checkpoint(ckpt_dir, payload=payload, metadata=metadata)
    return ckpt_dir


def test_cli_checkpoint_validate_success(tmp_path: Path) -> None:
    ckpt_dir = _write_checkpoint(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        checkpoint_validate.app,
        ["validate", "--path", str(ckpt_dir), "--show"],
    )
    assert result.exit_code == 0, result.stdout
    info = json.loads(result.stdout)
    assert info["schema_version"] == checkpoint_core.SCHEMA_VERSION
    assert info["metrics"]["val_loss"] == 0.42
    assert Path(info["checkpoint"]).exists()


def test_cli_checkpoint_validate_missing_payload(tmp_path: Path) -> None:
    ckpt_dir = tmp_path / "missing"
    ckpt_dir.mkdir()
    (ckpt_dir / "metadata.json").write_text("{}", encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(
        checkpoint_validate.app,
        ["validate", "--path", str(ckpt_dir)],
    )
    assert result.exit_code == 2
    assert "missing checkpoint payload" in result.stdout or result.stderr
