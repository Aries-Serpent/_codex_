"""
Test Train Minimal Cli

Test module for train minimal cli.
"""

from pathlib import Path

from codex_ml.cli import train_minimal


class DummyLoop:
    def __init__(self):
        self.calls = []

    def run_minimal_training(self, config, max_steps, run_dir):
        self.calls.append({"config": config, "max_steps": max_steps, "run_dir": run_dir})


def test_train_minimal_invokes_training_loop(tmp_path, monkeypatch):
    dummy = DummyLoop()

    def fake_import_training_loop():
        return dummy

    monkeypatch.setattr(train_minimal, "_import_training_loop", fake_import_training_loop)

    cfg_file = tmp_path / "conf.yaml"
    cfg_file.write_text("model:\n  hidden_size: 8\n", encoding="utf-8")

    runs_dir = tmp_path / "runs"

    rc = train_minimal.main(
        [
            "--config",
            str(cfg_file),
            "--seed",
            "7",
            "--runs-dir",
            str(runs_dir),
            "--max-steps",
            "3",
        ]
    )

    assert rc == 0, "rc is not valid"
    assert len(dummy.calls) == 1, "Collection must not be empty"
    call = dummy.calls[0]
    assert call["max_steps"] == 3, "Condition must be true"
    assert "hidden_size" in call["config"].get("model", {})
    assert Path(call["run_dir"]).exists(), "Condition must be true"
