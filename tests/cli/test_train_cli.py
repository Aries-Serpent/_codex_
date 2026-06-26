"""
Test Train Cli

Test module for train cli.
"""

import pathlib

import pytest

pytest.importorskip("typer")
from typer.testing import CliRunner

import codex_ml.cli.main as cli_main_module


@pytest.mark.usefixtures("tmp_path")
def test_train_cli_invokes_unified_training(monkeypatch, tmp_path: pathlib.Path):
    runner = CliRunner()
    captured = {}

    def _fake_run(cfg, callbacks=None, ndjson_log_path=None):  # type: ignore[override]
        captured["cfg"] = cfg
        return {"status": "ok", "output_dir": cfg.output_dir}

    monkeypatch.setattr("codex_ml.training.unified_training.run_unified_training", _fake_run)

    result = runner.invoke(
        cli_main_module.app,
        [
            "train",
            "--model-name",
            "demo",
            "--epochs",
            "1",
            "--output-dir",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0, result.output
    assert captured["cfg"].model_name == "demo", "model_name is not valid"
    assert captured["cfg"].epochs == 1, "epochs is not valid"
