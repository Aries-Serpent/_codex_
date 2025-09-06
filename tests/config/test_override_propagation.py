from __future__ import annotations

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_override_file(tmp_path: Path) -> None:
    override_file = tmp_path / "ovr.txt"
    override_file.write_text("train.batch_size=2\ntrain.lr=0.1\n")
    cmd = [
        "python",
        "-m",
        "codex_ml.cli.main",
        f"--override-file={override_file}",
        "--set",
        "tokenizer.name=gpt2",
        "dry_run=true",
    ]
    env = {**os.environ, "PYTHONPATH": "src"}
    subprocess.run(cmd, check=True, env=env, cwd=ROOT)
    text = (ROOT / ".codex/hydra_last/config.yaml").read_text()
    assert "batch_size: 2" in text
    assert "lr: 0.1" in text
    assert "name: gpt2" in text
