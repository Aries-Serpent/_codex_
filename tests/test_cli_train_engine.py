import pytest
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
    assert captured["argv"] == ["--engine", "custom", "--output-dir", "out"]


@pytest.mark.skip(reason="conflicting LoRA options under investigation")
def test_cli_train_hf_engine_parses_args(monkeypatch, tmp_path):
    runner = CliRunner()
    captured: dict[str, object] = {}

    def fake_run(texts, output_dir, **kw):
        captured["texts"] = list(texts)
        captured["output_dir"] = output_dir
        captured["kw"] = kw

    monkeypatch.setattr("training.engine_hf_trainer.run_hf_trainer", fake_run)

    result = runner.invoke(
        cli,
        [
            "train",
            "--engine",
            "hf",
            "--texts",
            "hi",
            "--output-dir",
            str(tmp_path),
            "--seed",
            "123",
            "--device",
            "cuda",
            "--dtype",
            "bf16",
        ],
    )
    assert result.exit_code == 0
    assert captured["texts"] == ["hi"]
    assert captured["output_dir"] == tmp_path
    assert captured["kw"]["seed"] == 123
    assert captured["kw"]["device"] == "cuda"
    assert captured["kw"]["dtype"] == "bf16"
