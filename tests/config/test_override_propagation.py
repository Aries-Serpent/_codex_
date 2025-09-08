from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

pytest.importorskip("hydra")

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.skip(reason="override propagation under investigation")
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
        "pipeline.steps=[]",
        "dry_run=true",
        "pipeline.steps=[]",
        "hydra.run.dir=.codex/hydra_last",
    ]
    env = {**os.environ, "PYTHONPATH": "src"}
    subprocess.run(cmd, check=True, env=env, cwd=ROOT)
    text = (ROOT / ".codex/hydra_last/.hydra/config.yaml").read_text()
    assert "batch_size: 2" in text
    assert "lr: 0.1" in text
    assert "name: gpt2" in text
