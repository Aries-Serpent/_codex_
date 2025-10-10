#!/usr/bin/env python
# Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5
# Purpose: Validate MLflow offline logging behavior if mlflow is installed.

from __future__ import annotations

import os
from pathlib import Path

import pytest

mlflow = pytest.importorskip("mlflow")


@pytest.mark.smoke
def test_experiment_mlflow_offline(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    # Force local filesystem backend; no network
    monkeypatch.setenv("MLFLOW_TRACKING_URI", f"file://{tmp_path.as_posix()}")
    # Offline mode environment for other trackers (harmless here)
    monkeypatch.setenv("WANDB_MODE", "offline")

    with mlflow.start_run(run_name="offline-test"):
        mlflow.log_param("alpha", 0.1)
        mlflow.log_metric("loss", 1.23, step=1)

    # verify local files created
    assert any(p.is_dir() for p in tmp_path.iterdir())
