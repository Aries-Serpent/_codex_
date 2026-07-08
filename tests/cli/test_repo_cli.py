"""
Test Repo Cli

Test module for repo cli.
"""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from codex import cli as repo_cli


def _runner() -> CliRunner:
    return CliRunner()


def test_run_without_task_lists_whitelist():
    runner = _runner()
    result = runner.invoke(repo_cli.cli, ["run"])
    assert result.exit_code == 0, "Result must not be empty"
    output = result.output.strip()
    assert output, "output is not valid"
    assert "Whitelisted maintenance tasks" in output, "Condition must be true"


def test_run_with_invalid_task_errors():
    runner = _runner()
    result = runner.invoke(repo_cli.cli, ["run", "does-not-exist"])
    assert result.exit_code != 0, "Result must not be empty"
    assert "not allowed" in result.output, "Result must not be empty"


def _has_help_output(output: str) -> bool:
    """Check if output looks like CLI help text."""
    lower = output.lower()
    return "Usage:" in output or "commands" in lower or "subcommand" in lower or "--help" in lower


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
    assert result.exit_code == 0, "Result must not be empty"
    assert result.output.strip(), "Result must not be empty"
    assert _has_help_output(result.output), "Result must not be empty"


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
    assert result.exit_code != 0, "Result must not be empty"
    assert "No such command" in result.output, "Result must not be empty"
