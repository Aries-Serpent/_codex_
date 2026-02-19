"""
Test Run Eval Cli

Test module for run eval cli.
"""

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
    # Build clean env: start from os.environ, strip HF_REVISION vars so
    # KNOWN_MODEL_REVISIONS is used (not the abcdef0 test stub injected by
    # models/conftest.py), and prepend repo src/ to PYTHONPATH.
    src_path = str(repo_root / "src")
    subprocess_env = {k: v for k, v in os.environ.items()
                      if k not in ("HF_REVISION", "CODEX_HF_REVISION", "HF_MODEL_REVISION")}
    existing_pythonpath = subprocess_env.get("PYTHONPATH", "")
    subprocess_env["PYTHONPATH"] = (
        f"{src_path}:{existing_pythonpath}" if existing_pythonpath else src_path
    )
    out = subprocess.check_output(cmd, text=True, cwd=repo_root, env=subprocess_env)
    metrics = json.loads(out.strip().splitlines()[0])
    assert "perplexity" in metrics
    assert "token_accuracy" in metrics
