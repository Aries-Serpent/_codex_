"""
Test Eval Minimal Cli

Test module for eval minimal cli.
"""

from pathlib import Path

from codex_ml.cli import eval_minimal


class DummyLoop:
    def __init__(self):
        self.calls = []

    def run_minimal_evaluation(self, config, checkpoint, run_dir):
        self.calls.append({"config": config, "checkpoint": checkpoint, "run_dir": run_dir})


def test_eval_minimal_invokes_eval_loop(tmp_path, monkeypatch):
    dummy = DummyLoop()

    def fake_import_training_loop():
        return dummy

    monkeypatch.setattr(eval_minimal, "_import_training_loop", fake_import_training_loop)

    cfg_file = tmp_path / "conf_eval.yaml"
    cfg_file.write_text("eval:\n  batch_size: 4\n", encoding="utf-8")

    runs_dir = tmp_path / "runs"
    ckpt = tmp_path / "fake_ckpt"

    rc = eval_minimal.main(
        [
            "--config",
            str(cfg_file),
            "--seed",
            "11",
            "--runs-dir",
            str(runs_dir),
            "--checkpoint",
            str(ckpt),
        ]
    )

    assert rc == 0, "rc is not valid"
    assert len(dummy.calls) == 1, "Collection must not be empty"
    call = dummy.calls[0]
    assert call["checkpoint"] == str(ckpt), "Condition must be true"
    assert "batch_size" in call["config"].get("eval", {})
    assert Path(call["run_dir"]).exists(), "Condition must be true"
