"""Smoke test for codex.cli_qa Typer app."""

from __future__ import annotations

from typer.testing import CliRunner

from codex import cli_qa


def test_cli_qa_help():
    runner = CliRunner()
    result = runner.invoke(cli_qa.app, ["--help"])
    assert result.exit_code == 0
    assert result.output
