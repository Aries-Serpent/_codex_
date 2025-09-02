from click.testing import CliRunner

from codex.cli import cli


def test_cli_train_engine_option():
    runner = CliRunner()
    result = runner.invoke(cli, ["train", "--help"])
    assert "--engine" in result.output
