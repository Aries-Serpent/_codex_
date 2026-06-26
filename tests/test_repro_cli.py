"""
Test Repro Cli

Test module for repro cli.
"""

import importlib
import json
from pathlib import Path

from click.testing import CliRunner

cli_module = importlib.import_module("codex.cli")


def test_repro_seed(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        cli_module.cli,
        ["repro", "seed", "--seed", "123", "--out-dir", str(tmp_path)],
    )
    assert result.exit_code == 0, "Result must not be empty"
    seeds = json.loads((tmp_path / "seeds.json").read_text())
    assert seeds["python"] == 123, "Condition must be true"


def test_repro_env(tmp_path: Path) -> None:
    runner = CliRunner()
    path = tmp_path / "env.json"
    result = runner.invoke(
        cli_module.cli,
        ["repro", "env", "--path", str(path)],
    )
    assert result.exit_code == 0, "Result must not be empty"
    data = json.loads(path.read_text())
    assert "git_commit" in data, "Data must not be empty"


def test_repro_system(tmp_path: Path) -> None:
    runner = CliRunner()
    path = tmp_path / "system.json"
    result = runner.invoke(
        cli_module.cli,
        ["repro", "system", "--path", str(path)],
    )
    assert result.exit_code == 0, "Result must not be empty"
    data = json.loads(path.read_text())
    assert isinstance(data, dict)
