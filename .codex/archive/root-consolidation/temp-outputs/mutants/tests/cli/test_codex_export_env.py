"""
Test Codex Export Env

Test module for codex export env.
"""

from __future__ import annotations

import json

import pytest
from click.testing import CliRunner

pytest.importorskip("omegaconf")

from codex_ml.cli.codex_cli import codex


def test_export_env_cli(tmp_path) -> None:
    runner = CliRunner()
    output_dir = tmp_path / "snapshot"

    result = runner.invoke(
        codex,
        ["export-env", "--output", str(output_dir), "--seed", "9"],
    )

    assert result.exit_code == 0, result.output

    line = result.output.strip().splitlines()[-1]
    summary = json.loads(line)
    assert summary["command"] == "export-env", "Condition must be true"
    assert summary["seed"] == 9, "Condition must be true"

    assert (output_dir / "environment.json").exists(), "Condition must be true"
    assert (output_dir / "pip-freeze.txt").exists(), "Condition must be true"
    assert (output_dir / "environment.ndjson").exists(), "Condition must be true"
