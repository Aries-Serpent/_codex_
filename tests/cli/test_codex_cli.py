from __future__ import annotations

from click.testing import CliRunner

from codex.cli import cli


def test_codex_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.output
