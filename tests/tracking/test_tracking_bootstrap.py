from __future__ import annotations

import os

import pytest

from codex_ml.utils.tracking_bootstrap import init_mlflow_offline, init_wandb_offline


def test_mlflow_offline_env_defaults() -> None:
    os.environ.pop("MLFLOW_TRACKING_URI", None)
    env = init_mlflow_offline()
    # Should set a local file store by default (no server)
    if env == {"mlflow": "unavailable"}:
        pytest.skip("mlflow not installed")
    assert "MLFLOW_TRACKING_URI" in env
    assert env["MLFLOW_TRACKING_URI"].startswith("file:")


def test_wandb_offline_default() -> None:
    os.environ.pop("WANDB_MODE", None)
    env = init_wandb_offline(project="codex-offline-test")
    if env == {"wandb": "unavailable"}:
        pytest.skip("wandb not installed")
    assert env.get("WANDB_MODE", "") == "offline"
