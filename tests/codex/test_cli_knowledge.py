"""Smoke test for codex.cli_knowledge Typer app."""

from __future__ import annotations

from typer.testing import CliRunner

from codex import cli_knowledge


def test_cli_knowledge_help():
    runner = CliRunner()
    result = runner.invoke(cli_knowledge.app, ["--help"])
    assert result.exit_code == 0
    assert result.output
