from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from codex_ml.cli import simple_cli


@pytest.mark.infra
def test_cli_infer_uses_codex_model(monkeypatch: pytest.MonkeyPatch) -> None:
    class DummyModel:
        def __init__(self, *args, **kwargs) -> None:
            pass

        def generate(self, prompt: str, **_: object) -> str:
            return f"generated:{prompt}"

    monkeypatch.setattr(simple_cli, "CodexModel", lambda *a, **k: DummyModel())
    runner = CliRunner()
    result = runner.invoke(simple_cli.cli, ["infer", "--model", "foo", "--prompt", "hi"])
    assert result.exit_code == 0
    assert "generated:hi" in result.output


@pytest.mark.infra
def test_cli_train_model_invokes_trainer(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    captured: dict[str, object] = {}

    def fake_train(config: dict[str, object], *, resume: bool) -> None:  # type: ignore[override]
        captured["config"] = config
        captured["resume"] = resume

    monkeypatch.setattr(simple_cli, "run_functional_training", fake_train)
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({"epochs": 1}), encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(
        simple_cli.cli, ["train-model", "--config", str(config_path), "--resume"]
    )
    assert result.exit_code == 0
    assert captured["config"] == {"epochs": 1}
    assert captured["resume"] is True


@pytest.mark.infra
def test_cli_build_tokenizer_invokes_pipeline(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    captured: dict[str, object] = {}

    def fake_run(path: str, *, dry_run: bool | None = None) -> Path:
        captured["path"] = path
        captured["dry_run"] = dry_run
        output = tmp_path / "tokenizer"
        output.write_text("ok", encoding="utf-8")
        return output

    monkeypatch.setattr(simple_cli, "run_tokenizer_train", fake_run)
    config_path = tmp_path / "tokenizer.yaml"
    config_path.write_text("tokenization: {}", encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(
        simple_cli.cli, ["build-tokenizer", "--config", str(config_path), "--dry-run"]
    )
    assert result.exit_code == 0
    assert str(config_path) == captured["path"]
    assert captured["dry_run"] is True
    assert "tokenizer" in result.output
