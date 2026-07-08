"""
Test Subcommands

Test module for subcommands.
"""

import pytest
from click.testing import CliRunner

from codex_ml.cli.codex_cli import codex


def test_metrics_server_help():
    runner = CliRunner()
    result = runner.invoke(codex, ["metrics-server", "--help"])
    assert result.exit_code == 0, "Result must not be empty"


@pytest.mark.skip(reason="Requires configured tokenizer model - integration test, not unit test")
def test_tokenize_command():
    runner = CliRunner()
    result = runner.invoke(codex, ["tokenize", "hello"])
    assert result.exit_code == 0, "Result must not be empty"
    assert "[" in result.output, "Result must not be empty"
