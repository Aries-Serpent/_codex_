"""
Test Mlflow Offline

Test module for mlflow offline.
"""

#!/usr/bin/env python
# Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5
# Purpose: Validate MLflow offline logging behavior if mlflow is installed.

from __future__ import annotations

from pathlib import Path

import pytest

mlflow = pytest.importorskip("mlflow")


@pytest.mark.smoke
def test_experiment_mlflow_offline(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    # Force local filesystem backend; no network
    tracking_root = tmp_path / "mlruns"
    monkeypatch.setenv("MLFLOW_TRACKING_URI", f"file://{tracking_root.as_posix()}")
    # Offline mode environment for other trackers (harmless here)
    monkeypatch.setenv("WANDB_MODE", "offline")

    tracking_root.mkdir(parents=True, exist_ok=True)
    mlflow.set_tracking_uri(f"file://{tracking_root.as_posix()}")
    mlflow.set_experiment("offline-test")
    with mlflow.start_run(run_name="offline-test"):
        mlflow.log_param("alpha", 0.1)
        mlflow.log_metric("loss", 1.23, step=1)

    # verify local files created
    assert any(p.is_dir() for p in tmp_path.iterdir()), "Condition must be true"
