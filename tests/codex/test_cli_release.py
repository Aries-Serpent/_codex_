"""Smoke test for codex.cli_release Typer app."""

from __future__ import annotations

from typer.testing import CliRunner

from codex import cli_release


def test_cli_release_help():
    runner = CliRunner()
    result = runner.invoke(cli_release.app, ["--help"])
    assert result.exit_code == 0
    assert result.output
