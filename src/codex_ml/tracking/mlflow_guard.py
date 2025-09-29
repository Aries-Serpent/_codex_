"""Utilities to keep MLflow tracking in a local file-backed store by default."""

from __future__ import annotations

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RELATIVE_DIR = Path(os.environ.get("CODEX_MLFLOW_LOCAL_DIR", "artifacts/mlruns"))

__all__ = ["ensure_file_backend"]


def _resolve_tracking_dir() -> Path:
    base = DEFAULT_RELATIVE_DIR.expanduser()
    if base.is_absolute():
        target = base
    else:
        target = (REPO_ROOT / base).resolve()
    target.mkdir(parents=True, exist_ok=True)
    return target


def ensure_file_backend(force: bool = False) -> str:
    """Ensure MLflow writes to a local ``file:`` backend unless overridden.

    Parameters
    ----------
    force:
        When ``True`` the guard updates ``MLFLOW_TRACKING_URI`` and
        ``CODEX_MLFLOW_URI`` even if they are already set.

    Returns
    -------
    str
        The tracking URI that should be used for MLflow operations.
    """

    tracking_env = os.environ.get("MLFLOW_TRACKING_URI")
    codex_env = os.environ.get("CODEX_MLFLOW_URI")
    if not force and (tracking_env or codex_env):
        return tracking_env or codex_env or ""

    tracking_dir = _resolve_tracking_dir()
    uri = tracking_dir.as_uri()
    if force:
        os.environ["MLFLOW_TRACKING_URI"] = uri
        os.environ["CODEX_MLFLOW_URI"] = uri
    else:
        os.environ.setdefault("MLFLOW_TRACKING_URI", uri)
        os.environ.setdefault("CODEX_MLFLOW_URI", uri)
    if force or "MLFLOW_ENABLE_SYSTEM_METRICS" not in os.environ:
        os.environ["MLFLOW_ENABLE_SYSTEM_METRICS"] = "false"
    return uri
