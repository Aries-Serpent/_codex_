"""
Test Train Script

Test module for train script.
"""

from __future__ import annotations

import json
from pathlib import Path

from scripts import train


def test_train_script_dry_run(monkeypatch, capsys) -> None:
    monkeypatch.setenv("TRAIN_BATCH_SIZE", "5")
    exit_code = train.main(["--config-from-env", "--dry-run"])
    assert exit_code == 0, "exit_code is not valid"
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["batch_size"] == 5, "Data must not be empty"


def test_train_script_runs_training(tmp_path: Path, monkeypatch, capsys) -> None:
    dataset = tmp_path / "train.txt"
    dataset.write_text("hello\nworld\n", encoding="utf-8")
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({"dataset_path": str(dataset)}), encoding="utf-8")

    captured: dict[str, object] = {}

    def fake_run(texts, output_dir, **kwargs):  # type: ignore[no-untyped-def]
        captured["texts"] = list(texts)
        captured["output_dir"] = output_dir
        captured["kwargs"] = kwargs
        return {"loss": 0.25}

    monkeypatch.setattr(train, "run_hf_trainer", fake_run)
    override_dir = tmp_path / "override"
    exit_code = train.main(["--config", str(config_path), "--output", str(override_dir)])
    assert exit_code == 0, "exit_code is not valid"
    assert captured["texts"] == ["hello", "world"]
    assert captured["output_dir"] == override_dir, "Condition must be true"
    result = json.loads(capsys.readouterr().out)
    assert result["loss"] == 0.25, "Result must not be empty"
