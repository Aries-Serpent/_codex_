from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse


def _is_remote_uri(uri: str) -> bool:
    """Heuristic: treat non-empty scheme that is not 'file' as remote."""
    try:
        parsed = urlparse(uri)
        if not parsed.scheme:
            return False
        return parsed.scheme.lower() != "file"
    except Exception:
        return True


def _is_allowlisted(host: str, allowlist_csv: str | None) -> bool:
    if not host:
        return False
    if not allowlist_csv:
        return False
    allowed = {h.strip().lower() for h in allowlist_csv.split(",") if h.strip()}
    return host.lower() in allowed


def ensure_mlflow_offline(artifacts_dir: str | Path, *, allowlist_hosts_env: str = "CODEX_ALLOWLIST_HOSTS") -> str:
    """
    Enforce MLflow local file store unless explicit allowlisted remote host is provided.

    Behavior:
    - If MLFLOW_TRACKING_URI is unset -> set to file://<artifacts_dir>/mlruns
    - If set to remote and host is not allowlisted via allowlist_hosts_env -> coerce to file://
    - Returns effective MLFLOW_TRACKING_URI
    """
    artifacts_dir = Path(artifacts_dir)
    mlruns = artifacts_dir / "mlruns"
    mlruns.mkdir(parents=True, exist_ok=True)
    allowlist = os.getenv(allowlist_hosts_env, "")
    current = os.getenv("MLFLOW_TRACKING_URI", "").strip()
    if not current:
        effective = f"file://{mlruns.as_posix()}"
        os.environ["MLFLOW_TRACKING_URI"] = effective
        return effective

    parsed = urlparse(current)
    host = parsed.hostname or ""
    if _is_remote_uri(current) and not _is_allowlisted(host, allowlist):
        effective = f"file://{mlruns.as_posix()}"
        os.environ["MLFLOW_TRACKING_URI"] = effective
        return effective
    # Already local or allowlisted remote
    return current


def ensure_wandb_offline(*, default_mode: str = "offline") -> str:
    """
    Enforce W&B offline mode by default, unless already explicitly set by user.
    Returns the effective WANDB_MODE value.
    """
    val = os.getenv("WANDB_MODE")
    if not val:
        os.environ["WANDB_MODE"] = default_mode
        return default_mode
    return val