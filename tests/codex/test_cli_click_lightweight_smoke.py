from __future__ import annotations

from click.testing import CliRunner

from codex import cli as codex_cli


def test_click_cli_help_lists_subcommands(monkeypatch):
    monkeypatch.setenv("CODEX_CLI_LIGHTWEIGHT", "1")
    runner = CliRunner()
    result = runner.invoke(codex_cli.cli, [])
    assert result.exit_code == 0
    assert "Available subcommands:" in result.output
    assert "tasks" in result.output
    assert "run" in result.output


def test_click_cli_run_branches(monkeypatch):
    monkeypatch.setenv("CODEX_CLI_LIGHTWEIGHT", "1")
    runner = CliRunner()

    list_result = runner.invoke(codex_cli.cli, ["run"])
    assert list_result.exit_code == 0
    assert "Whitelisted maintenance tasks" in list_result.output

    invalid_result = runner.invoke(codex_cli.cli, ["run", "not-allowed"])
    assert invalid_result.exit_code == 1
    assert "is not allowed" in invalid_result.output
