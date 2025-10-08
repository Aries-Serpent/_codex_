from __future__ import annotations

import json
import subprocess
import sys


def test_offline_bootstrap_sets_env_and_dir(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    ml_dir = tmp_path / "mlruns_local"
    cmd = [
        sys.executable,
        "-m",
        "codex_ml",
        "offline-bootstrap",
        "--mlflow-dir",
        str(ml_dir),
        "--wandb-disable",
    ]
    proc = subprocess.run(cmd, check=True, capture_output=True)
    out = json.loads(proc.stdout.decode("utf-8"))
    assert out["mlflow"]["uri"].startswith("file:///")
    assert out["wandb"]["disabled"] is True
    assert ml_dir.exists()
