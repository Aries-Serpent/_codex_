import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

pytest.importorskip("datasets")


def test_run_eval_cli(tmp_path):
    data = tmp_path / "data.txt"
    data.write_text("hello world\nsecond line", encoding="utf-8")
    cmd = [
        sys.executable,
        "-m",
        "codex_ml.eval.run_eval",
        "--model",
        "sshleifer/tiny-gpt2",
        "--data",
        str(data),
    ]
    repo_root = Path(__file__).resolve().parents[1]
    env = {"PYTHONPATH": str(repo_root / "src")}
    out = subprocess.check_output(cmd, text=True, cwd=repo_root, env={**env, **os.environ})
    metrics = json.loads(out.strip().splitlines()[0])
    assert "perplexity" in metrics
    assert "token_accuracy" in metrics
