"""
Test Cli Offline Bootstrap

Test module for cli offline bootstrap.
"""

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

    assert payload["ok"] is True, "Condition must be true"

    # Handle nested JSON structure: mlflow.env.MLFLOW_TRACKING_URI
    mlflow_section = payload.get("mlflow", {})
    mlflow_uri = (
        mlflow_section.get("MLFLOW_TRACKING_URI")
        or (mlflow_section.get("env") or {}).get("MLFLOW_TRACKING_URI")
        or payload.get("MLFLOW_TRACKING_URI")
        or (payload.get("env") or {}).get("MLFLOW_TRACKING_URI")
    )
    assert mlflow_uri and mlflow_uri.startswith("file:"), f"Expected file:// URI, got: {mlflow_uri}"

    wandb_section = payload.get("wandb", {})
    wandb_disabled = (
        wandb_section.get("WANDB_DISABLED")
        or (wandb_section.get("env") or {}).get("WANDB_DISABLED")
        or payload.get("WANDB_DISABLED")
        or (payload.get("env") or {}).get("WANDB_DISABLED")
    )
    assert wandb_disabled == "true", f"Expected WANDB_DISABLED='true', got: {wandb_disabled}"

    assert (root / "mlruns").exists(), "mlruns directory not created"
    assert (root / "wandb").exists(), "wandb directory not created"


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
    assert "export MLFLOW_TRACKING_URI=" in stdout, "Condition must be true"
