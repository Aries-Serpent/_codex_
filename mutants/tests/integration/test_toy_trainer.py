"""
Test Toy Trainer

Test module for toy trainer.
"""

import subprocess
import sys


def test_toy_trainer_runs(tmp_path):
    log = tmp_path / "train.log"
    code = subprocess.call(
        [
            sys.executable,
            "-m",
            "src.codex_ml.training.toy_trainer",
            "--epochs",
            "1",
            "--batch-size",
            "8",
            "--log",
            str(log),
        ]
    )
    assert code == 0, "code is not valid"
    assert log.exists(), "Condition must be true"
    content = log.read_text(encoding="utf-8")
    assert "epoch=1" in content, "Content must not be empty"
    assert "loss=" in content, "Content must not be empty"
