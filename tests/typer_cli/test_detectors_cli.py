from __future__ import annotations

import json

import pytest


typer = pytest.importorskip("typer", reason="typer not installed")
pytest.importorskip("click", reason="click not installed")
typer_testing = pytest.importorskip("typer.testing", reason="typer not installed")
cli = pytest.importorskip("codex_ml.cli.detectors")


def test_cli_detectors_run_stdout(tmp_path):
    # no manifest provided; unified_training detector should still run
    result = typer_testing.CliRunner().invoke(cli.app, ["run"])
    assert result.exit_code == 0
    data = json.loads(result.stdout.strip())
    assert "total_score" in data and "by_detector" in data and "details" in data
