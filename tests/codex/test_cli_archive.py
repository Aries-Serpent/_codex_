"""Smoke test for codex.cli_archive help output."""

from __future__ import annotations

from click.testing import CliRunner

from codex import cli_archive


def test_cli_archive_help():
    runner = CliRunner()
    result = runner.invoke(cli_archive.app, ["--help"])
    assert result.exit_code == 0, "Result must not be empty"
    assert result.output, "Result must not be empty"
