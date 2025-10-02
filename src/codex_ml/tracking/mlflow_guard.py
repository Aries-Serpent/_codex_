"""Utilities to keep MLflow tracking in a local file-backed store by default."""

from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlparse

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


def _normalise_local_uri(uri: str) -> str:
    """Return a ``file:`` URI for local paths and ensure the directory exists."""

    parsed = urlparse(uri)
    if parsed.scheme == "file":
        return uri
    if parsed.scheme:
        # Non-file schemes (http, https, databricks, etc.) are passed through as-is.
        return uri

    path = Path(uri).expanduser()
    if not path.is_absolute():
        path = (REPO_ROOT / path).resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path.as_uri()


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

    if tracking_env:
        normalised = _normalise_local_uri(tracking_env)
        if normalised != tracking_env or force:
            os.environ["MLFLOW_TRACKING_URI"] = normalised
        tracking_env = normalised
        os.environ.setdefault("CODEX_MLFLOW_URI", tracking_env)

    if codex_env:
        normalised = _normalise_local_uri(codex_env)
        if normalised != codex_env or force:
            os.environ["CODEX_MLFLOW_URI"] = normalised
        codex_env = normalised
        if not tracking_env:
            os.environ.setdefault("MLFLOW_TRACKING_URI", codex_env)
            tracking_env = codex_env

    if not force and (tracking_env or codex_env):
        if tracking_env:
            return tracking_env
        if codex_env:
            return codex_env
        return ""

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
