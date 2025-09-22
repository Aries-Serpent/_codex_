from __future__ import annotations

import pytest
from click.testing import CliRunner

from codex import cli as repo_cli


def _runner() -> CliRunner:
    return CliRunner()


def test_run_without_task_lists_whitelist():
    runner = _runner()
    result = runner.invoke(repo_cli.cli, ["run"])
    assert result.exit_code == 0
    output = result.output.strip()
    assert output
    assert "Whitelisted maintenance tasks" in output


def test_run_with_invalid_task_errors():
    runner = _runner()
    result = runner.invoke(repo_cli.cli, ["run", "does-not-exist"])
    assert result.exit_code != 0
    assert "not allowed" in result.output


@pytest.mark.parametrize(
    "args",
    [
        [],
        ["logs"],
        ["tokenizer"],
        ["repro"],
    ],
)
def test_groups_emit_help_when_no_subcommand(args):
    runner = _runner()
    result = runner.invoke(repo_cli.cli, args)
    assert result.exit_code == 0
    assert result.output.strip()
    assert "Usage:" in result.output


@pytest.mark.parametrize(
    "args",
    [
        ["bogus"],
        ["logs", "bogus"],
        ["tokenizer", "bogus"],
        ["repro", "bogus"],
    ],
)
def test_invalid_subcommands_exit_non_zero(args):
    runner = _runner()
    result = runner.invoke(repo_cli.cli, args)
    assert result.exit_code != 0
    assert "No such command" in result.output
