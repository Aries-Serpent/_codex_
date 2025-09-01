import importlib
from pathlib import Path

from click.testing import CliRunner

cli_module = importlib.import_module("codex.cli")


def test_cli_help() -> None:
    runner = CliRunner()
    result = runner.invoke(cli_module.cli, ["--help"])
    assert result.exit_code == 0
    assert "Codex CLI entry point" in result.output


def test_cli_list_tasks() -> None:
    runner = CliRunner()
    result = runner.invoke(cli_module.cli, ["tasks"])
    assert result.exit_code == 0
    out = result.output.strip().split()
    assert "ingest" in out


def test_cli_run_invalid() -> None:
    runner = CliRunner()
    result = runner.invoke(cli_module.cli, ["run", "invalid_task"])
    assert result.exit_code != 0
    assert "not allowed" in result.output


def test_cli_run_valid() -> None:
    runner = CliRunner()
    with runner.isolated_filesystem():
        data_dir = Path("data")
        data_dir.mkdir()
        (data_dir / "example.jsonl").write_text("{}", encoding="utf-8")
        result = runner.invoke(cli_module.cli, ["run", "ingest"])
        assert result.exit_code == 0
        assert "Ingested" in result.output
