"""Deprecated shim for backward compatibility.

The tracking utilities now live under :mod:`codex_ml.tracking.mlflow_utils`.
This module re-exports those symbols and restores the legacy
``maybe_start_run`` helper used by older monitoring code.
"""

from __future__ import annotations

import os
from typing import Optional

from ..tracking import mlflow_utils as _tracking_mlflow_utils
from ..tracking.mlflow_guard import ensure_file_backend
from ..tracking.mlflow_utils import *  # noqa: F401,F403

# Expose the underlying ``mlflow`` module so older call sites and tests that
# patch ``mlflow_utils.mlflow`` continue to work.
mlflow = _tracking_mlflow_utils._mlf

__all__ = _tracking_mlflow_utils.__all__ + ["maybe_start_run", "mlflow"]


def _env_enabled(value: Optional[str]) -> bool:
    """Return ``True`` if *value* represents a truthy setting.

    Accepts common representations such as ``1``, ``true``, ``yes``, ``y`` and ``on``
    (case-insensitive). Any other value is treated as ``False``.
    """
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


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
        enabled = _env_enabled(os.environ.get("CODEX_ENABLE_MLFLOW"))
    if not enabled:
        return None

    tracking_uri = ensure_file_backend()
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
