"""Utilities that force offline tracking defaults for MLflow and Weights & Biases."""

from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlparse

__all__ = [
    "_is_allowlisted",
    "_is_remote_uri",
    "ensure_mlflow_offline",
    "ensure_wandb_offline",
]


def _is_remote_uri(uri: str) -> bool:
    """Return ``True`` when ``uri`` looks like a remote MLflow tracking target."""
    try:
        parsed = urlparse(uri)
    except Exception:
        return True

    if not parsed.scheme:
        return False
    return parsed.scheme.lower() != "file"


def _is_allowlisted(host: str, allowlist_csv: str | None) -> bool:
    if not host:
        return False
    if not allowlist_csv:
        return False
    allowed = {h.strip().lower() for h in allowlist_csv.split(",") if h.strip()}
    return host.lower() in allowed


def ensure_mlflow_offline(
    artifacts_dir: str | Path,
    *,
    allowlist_hosts_env: str = "CODEX_ALLOWLIST_HOSTS",
) -> str:
    """Coerce MLflow to use a local ``file://`` backend unless explicitly allowlisted."""
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

    # Already local or explicitly allowlisted remote URI.
    return current


def ensure_wandb_offline(*, default_mode: str = "offline") -> str:
    """Default WANDB_MODE to ``offline`` when the user did not choose a value."""
    val = os.getenv("WANDB_MODE")
    if not val:
        os.environ["WANDB_MODE"] = default_mode
        return default_mode
    return val
