"""Helpers to enforce file-backed MLflow URIs for CLI entry points."""

from __future__ import annotations

import os

from codex_ml.utils.experiment_tracking_mlflow import ensure_local_tracking

__all__ = ["configure_mlflow_uri"]


def configure_mlflow_uri(candidate: str | None = None) -> str:
    """Force MLflow to use a local file-backed URI, blocking remote targets."""

    text = (candidate or "").strip()
    if text:
        os.environ["MLFLOW_TRACKING_URI"] = text
    else:
        os.environ.pop("MLFLOW_TRACKING_URI", None)
    return ensure_local_tracking()
