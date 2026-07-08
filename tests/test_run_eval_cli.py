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


@pytest.mark.slow
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
    subprocess_env = {
        k: v
        for k, v in os.environ.items()
        if k not in ("HF_REVISION", "CODEX_HF_REVISION", "HF_MODEL_REVISION")
    }
    existing_pythonpath = subprocess_env.get("PYTHONPATH", "")
    subprocess_env["PYTHONPATH"] = (
        f"{src_path}:{existing_pythonpath}" if existing_pythonpath else src_path
    )
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=repo_root, env=subprocess_env)
    # Exit 2 = HFModelUnavailableError (cache miss + network unreachable) — skip
    if result.returncode == 2:
        pytest.skip(
            f"Model unavailable (cache miss + network unreachable): {result.stderr.strip()}"
        )
    if "Evaluation requires optional packages:" in result.stderr:
        pytest.skip(f"Optional eval dependencies unavailable: {result.stderr.strip()}")
    if result.returncode != 0:
        raise AssertionError(
            f"run_eval subprocess failed (exit {result.returncode}):\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
    metrics = json.loads(result.stdout.strip().splitlines()[0])
    assert "perplexity" in metrics, "Condition must be true"
    assert "token_accuracy" in metrics, "Condition must be true"
