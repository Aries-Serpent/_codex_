"""Deprecated shim for backward compatibility.

The tracking utilities now live under :mod:`codex_ml.tracking.mlflow_utils`.
This module re-exports those symbols and restores the legacy
``maybe_start_run`` helper used by older monitoring code.
"""

from __future__ import annotations

import os
from typing import Optional

from ..tracking import mlflow_utils as _tracking_mlflow_utils
from ..tracking.mlflow_utils import *  # noqa: F401,F403

# Expose the underlying ``mlflow`` module so older call sites and tests that
# patch ``mlflow_utils.mlflow`` continue to work.
mlflow = _tracking_mlflow_utils._mlf

__all__ = _tracking_mlflow_utils.__all__ + ["maybe_start_run", "mlflow"]


def _env_enabled(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def maybe_start_run(
    experiment: Optional[str] = None,
    *,
    enabled: Optional[bool] = None,
):
    """Conditionally start an MLflow run based on environment variables.

    Parameters
    ----------
    experiment : str, optional
        Name for the MLflow run.
    enabled : bool, optional
        Override environment variable check.

    Returns
    -------
    mlflow.ActiveRun | None
        Context manager when tracking is enabled, otherwise ``None``.
    """

    if enabled is None:
        enabled = _env_enabled(os.getenv("CODEX_ENABLE_MLFLOW", "0"))
    if not enabled:
        return None

    tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
    if not tracking_uri:
        return None

    if mlflow is None:  # pragma: no cover - depends on optional dependency
        raise RuntimeError("mlflow is not installed")

    try:
        mlflow.set_tracking_uri(tracking_uri)
    except Exception as exc:  # pragma: no cover - defensive
        raise RuntimeError("Failed to set MLflow tracking URI") from exc

    try:
        return mlflow.start_run(run_name=experiment)
    except Exception as exc:  # pragma: no cover - defensive
        raise RuntimeError("Failed to start MLflow run") from exc
