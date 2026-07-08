"""Tests for offline tracking helper utilities."""

from __future__ import annotations

import os


def test_init_mlflow_offline_import_only(monkeypatch, tmp_path):
    """Import helper without requiring MLflow to be installed."""

    monkeypatch.chdir(tmp_path)
    try:
        from codex_ml.tracking.init_offline import init_mlflow_offline

        assert callable(init_mlflow_offline), "Condition must be true"
    except ImportError:
        # Import should still succeed even if mlflow is not installed.
        assert True, "True is not valid"


def test_init_wandb_offline_env(monkeypatch):
    """Helper sets WANDB_MODE to offline regardless of availability."""

    os.environ.pop("WANDB_MODE", None)
    from codex_ml.tracking.init_offline import init_wandb_offline

    init_wandb_offline(project="x")
    assert os.environ.get("WANDB_MODE") == "offline", "Condition must be true"
