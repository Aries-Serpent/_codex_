from click.testing import CliRunner

from codex_ml.cli.codex_cli import codex


def test_metrics_server_help():
    runner = CliRunner()
    result = runner.invoke(codex, ["metrics-server", "--help"])
    assert result.exit_code == 0


def test_tokenize_command():
    runner = CliRunner()
    result = runner.invoke(codex, ["tokenize", "hello"])
    assert result.exit_code == 0
    assert "[" in result.output
