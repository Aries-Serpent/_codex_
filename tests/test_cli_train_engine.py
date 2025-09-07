from click.testing import CliRunner

from codex.cli import cli


def test_cli_train_engine_option():
    runner = CliRunner()
    result = runner.invoke(cli, ["train", "--help"])
    assert "--engine" in result.output


def test_cli_train_custom_engine_forwards_args(monkeypatch):
    runner = CliRunner()
    captured: dict[str, list[str] | None] = {}

    def fake_main(argv=None):
        captured["argv"] = argv

    monkeypatch.setattr("training.functional_training.main", fake_main)
    result = runner.invoke(cli, ["train", "--engine", "custom", "--output-dir", "out"])
    assert result.exit_code == 0
    assert captured["argv"] == ["--output-dir", "out"]
