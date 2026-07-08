"""Smoke tests for :mod:`codex_ml.cli.tracking_cli`."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def test_enable_mlflow_and_wandb(monkeypatch):
    dummy_mlflow = MagicMock()
    monkeypatch.setitem(sys.modules, "mlflow", dummy_mlflow)

    dummy_wandb = MagicMock()
    dummy_run = MagicMock()
    dummy_run.settings.mode = "offline"
    dummy_run.settings._offline = True
    dummy_wandb.init.return_value = dummy_run
    monkeypatch.setitem(sys.modules, "wandb", dummy_wandb)

    from codex_ml.cli import tracking_cli

    mlflow_result = tracking_cli._enable_mlflow("file:/tmp/mlruns")
    wandb_result = tracking_cli._enable_wandb("proj", mode="offline")

    assert mlflow_result["enabled"] is True, "Result must not be empty"
    assert mlflow_result["tracking_uri"], "Result must not be empty"
    assert wandb_result["enabled"] is True, "Result must not be empty"
    assert wandb_result["offline"] is True, "Result must not be empty"
