from __future__ import annotations

import json
import subprocess
import sys


def test_track_bootstrap_sets_env(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    root = tmp_path / "runs"
    cmd = [
        sys.executable,
        "-m",
        "codex_ml",
        "track",
        "bootstrap",
        "--root",
        str(root),
        "--mode",
        "disabled",
    ]
    proc = subprocess.run(cmd, check=True, capture_output=True, text=True)
    payload = json.loads(proc.stdout)

    assert payload["ok"] is True
    assert payload["mlflow"]["MLFLOW_TRACKING_URI"].startswith("file:")
    assert payload["wandb"].get("WANDB_DISABLED") == "true"
    assert (root / "mlruns").exists()
    assert (root / "wandb").exists()


def test_track_bootstrap_prints_exports(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    root = tmp_path / "runs"
    cmd = [
        sys.executable,
        "-m",
        "codex_ml",
        "track",
        "bootstrap",
        "--root",
        str(root),
        "--backend",
        "mlflow",
        "--print-exports",
    ]
    proc = subprocess.run(cmd, check=True, capture_output=True, text=True)
    stdout = proc.stdout.strip()
    assert "export MLFLOW_TRACKING_URI=" in stdout
