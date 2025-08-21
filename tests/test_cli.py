import importlib
from click.testing import CliRunner

cli_module = importlib.import_module("codex.cli")


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
    result = runner.invoke(cli_module.cli, ["run", "ingest"])
    assert result.exit_code == 0
    assert "Ingestion" in result.output
