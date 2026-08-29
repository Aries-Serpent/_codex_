"""
Test Cli Train Engine

Test module for cli train engine.
"""

import pytest
from click.testing import CliRunner

pytest.importorskip("omegaconf")
pytest.importorskip("hydra")
pytest.importorskip("torch")
pytest.importorskip("transformers")
pytest.importorskip("datasets")
pytest.importorskip("accelerate")
pytest.importorskip("yaml")

from codex.cli import cli


def test_cli_train_engine_option():
    runner = CliRunner()
    result = runner.invoke(cli, ["train", "--help"])
    assert result.exit_code == 0, "Result must not be empty"
    assert "--engine" in result.output, "Result must not be empty"


def test_cli_train_custom_engine_forwards_args(monkeypatch):
    import sys

    runner = CliRunner()
    captured: dict[str, list[str] | None] = {}

    def fake_main():
        # Capture sys.argv when main() is called
        captured["argv"] = sys.argv[1:]  # Skip the program name

    monkeypatch.setattr("codex.training.main", fake_main)
    result = runner.invoke(cli, ["train", "--engine", "custom", "--output-dir", "out"])
    assert result.exit_code == 0, "Result must not be empty"
    # The CLI sets sys.argv to include --engine custom plus the engine_args
    assert captured["argv"] == ["--engine", "custom", "--output-dir", "out"]


@pytest.mark.skip(reason="hf trainer CLI requires CUDA drivers in this environment")
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
            "--lora-r",
            "4",
            "--lora-alpha",
            "32",
            "--lora-dropout",
            "0.1",
            "--seed",
            "123",
            "--device",
            "cpu",
            "--dtype",
            "bf16",
        ],
    )
    assert result.exit_code == 0, "Result must not be empty"
    assert captured["texts"] == ["hi"], "Condition must be true"
    assert captured["output_dir"] == tmp_path, "Condition must be true"
    assert captured["kw"]["lora_r"] == 4, "Condition must be true"
    assert captured["kw"]["lora_alpha"] == 32, "Condition must be true"
    assert captured["kw"]["lora_dropout"] == 0.1, "Condition must be true"
    assert captured["kw"]["seed"] == 123, "Condition must be true"
    assert captured["kw"]["device"] == "cpu", "Condition must be true"
    assert captured["kw"]["dtype"] == "bf16", "Condition must be true"
