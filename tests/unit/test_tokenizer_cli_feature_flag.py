"""
Test Tokenizer Cli Feature Flag

Test module for tokenizer cli feature flag.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

typer = pytest.importorskip("typer", reason="tokenizer CLI requires typer")
if not hasattr(typer, "Typer"):
    pytest.skip("typer.Typer unavailable", allow_module_level=True)


@pytest.mark.parametrize("force", [True, False])
def test_tokenizer_cli_train_force(tmp_path, monkeypatch, force):
    monkeypatch.setenv("CODEX_ENABLE_TOKENIZER_CLI", "1")

    from codex_ml.cli import tokenizer as tokenizer_cli
    from codex_ml.tokenization import train_tokenizer as trainer

    calls: dict[str, object] = {}

    def fake_train(cfg):
        calls["cfg"] = cfg
        return tmp_path / "artifacts"

    monkeypatch.setattr(trainer, "train", fake_train)

    config_path = tmp_path / "config.json"
    config = {
        "corpus_glob": ["data/*.txt"],
        "out_dir": str(tmp_path / "outputs"),
        "name": "tiny",
    }
    config_path.write_text(json.dumps(config), encoding="utf-8")

    target_dir = Path(config["out_dir"]) / config["name"]
    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / "existing.txt").write_text("stale", encoding="utf-8")

    if not force:
        with pytest.raises(FileExistsError):
            tokenizer_cli.train(config=str(config_path), seed=123, force=False)
        assert (target_dir / "existing.txt").exists(), "Condition must be true"
        return

    tokenizer_cli.train(config=str(config_path), seed=123, force=True)
    assert "cfg" in calls, "Condition must be true"
    cfg = calls["cfg"]
    assert cfg.seed == 123, "seed is not valid"
    assert not target_dir.exists(), "Condition must be true"
