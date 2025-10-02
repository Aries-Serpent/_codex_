"""Utilities to keep MLflow tracking pinned to a local file-backed store."""

from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlparse

REPO_ROOT = Path(__file__).resolve().parents[3]

__all__ = ["ensure_file_backend", "bootstrap_offline_tracking"]


def _default_tracking_dir() -> Path:
    candidate = os.environ.get("CODEX_MLFLOW_LOCAL_DIR", "artifacts/mlruns")
    path = Path(candidate).expanduser()
    if not path.is_absolute():
        path = (REPO_ROOT / path).resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


def _as_file_uri(path_like: str) -> str:
    path = Path(path_like).expanduser()
    if not path.is_absolute():
        path = (REPO_ROOT / path).resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path.as_uri()


def _normalise_candidate(uri: str, *, allow_remote: bool) -> str:
    if not uri:
        return _default_tracking_dir().as_uri()

    parsed = urlparse(uri)
    if parsed.scheme in {"", "file"}:
        if parsed.scheme == "file":
            netloc = parsed.netloc or ""
            if netloc not in {"", "localhost"}:
                # Treat non-local netloc as remote; fall back unless explicitly allowed.
                if not allow_remote:
                    return _default_tracking_dir().as_uri()
                return uri
            target = Path(parsed.path or ".")
        else:
            target = Path(uri)
        return _as_file_uri(str(target))

    if allow_remote:
        return uri

    return _default_tracking_dir().as_uri()


def ensure_file_backend(*, allow_remote: bool = False, force: bool = False) -> str:
    """Ensure MLflow uses a ``file:`` URI unless remote backends are allowed."""

    tracking_env = os.environ.get("MLFLOW_TRACKING_URI", "").strip()
    codex_env = os.environ.get("CODEX_MLFLOW_URI", "").strip()
    candidate = tracking_env or codex_env
    normalised = _normalise_candidate(candidate, allow_remote=allow_remote)

    if force or not tracking_env or tracking_env != normalised:
        os.environ["MLFLOW_TRACKING_URI"] = normalised
    if force or not codex_env or codex_env != normalised:
        os.environ["CODEX_MLFLOW_URI"] = normalised

    if "MLFLOW_ENABLE_SYSTEM_METRICS" not in os.environ or force:
        os.environ["MLFLOW_ENABLE_SYSTEM_METRICS"] = "false"

    return normalised


def bootstrap_offline_tracking(*, force: bool = False) -> str:
    """Bootstrap tracking configuration respecting the remote override flag."""

    allow_remote_flag = os.environ.get("MLFLOW_ALLOW_REMOTE", "").strip().lower()
    allow_remote = allow_remote_flag in {"1", "true", "yes", "on"}
    return ensure_file_backend(allow_remote=allow_remote, force=force)
