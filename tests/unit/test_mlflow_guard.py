from __future__ import annotations

import importlib

from omegaconf import OmegaConf


def test_ensure_local_tracking_file_uri(monkeypatch):
    cfg = OmegaConf.create({"monitor": {"tracking": {"allow_remote": False}}})
    monkeypatch.delenv("MLFLOW_TRACKING_URI", raising=False)

    try:
        ml = importlib.import_module("mlflow")
    except Exception:
        return

    from common.mlflow_guard import ensure_local_tracking

    ensure_local_tracking(cfg)
    uri = ml.get_tracking_uri()
    assert str(uri).startswith("file:")
