import subprocess
import sys
from pathlib import Path


def test_toy_trainer_runs(tmp_path):
    log = tmp_path / "train.log"
    code = subprocess.call(
        [sys.executable, "-m", "src.codex_ml.training.toy_trainer", "--epochs", "1", "--batch-size", "8", "--log", str(log)]
    )
    assert code == 0
    assert log.exists()
    content = log.read_text(encoding="utf-8")
    assert "epoch=1" in content
    assert "loss=" in content
