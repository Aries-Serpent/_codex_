from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

import pytest


def _reload(with_mlflow: bool):
    sys.modules.pop("codex_ml.tracking.mlflow_utils", None)
    if not with_mlflow:
        sys.modules.pop("mlflow", None)
        sys.modules["mlflow"] = None  # type: ignore
    return importlib.import_module("codex_ml.tracking.mlflow_utils")


def test_start_run_no_mlflow(tmp_path: Path) -> None:
    mfu = _reload(False)
    cfg = mfu.MlflowConfig(tracking_uri=f"file:{tmp_path.as_posix()}", experiment="exp")
    with mfu.start_run(cfg) as run:
        assert run is None


def test_start_run_with_mlflow(tmp_path: Path) -> None:
    pytest.importorskip("mlflow")
    mfu = _reload(True)
    cfg = mfu.MlflowConfig(
        tracking_uri=f"file:{tmp_path.as_posix()}", experiment="exp", enable_system_metrics=False
    )
    with mfu.start_run(cfg) as run:
        assert run is not None
        assert os.environ.get("MLFLOW_ENABLE_SYSTEM_METRICS") == "0"
