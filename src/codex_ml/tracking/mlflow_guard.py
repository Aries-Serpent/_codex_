"""Utilities to keep MLflow tracking pinned to a local file-backed store."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

REPO_ROOT = Path(__file__).resolve().parents[3]

__all__ = [
    "GuardDecision",
    "ensure_file_backend",
    "bootstrap_offline_tracking",
    "last_decision",
]


@dataclass(frozen=True)
class GuardDecision:
    """Record the outcome of an MLflow guard evaluation."""

    requested_uri: str
    effective_uri: str
    fallback_reason: str
    allow_remote_env: str
    allow_remote_flag: str
    allow_remote: bool
    system_metrics_enabled: bool


_LAST_DECISION: Optional[GuardDecision] = None


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


def _normalise_candidate(uri: str, *, allow_remote: bool) -> tuple[str, str]:
    """Return the effective URI and fallback reason for a candidate value."""

    if not uri:
        return _default_tracking_dir().as_uri(), ""

    parsed = urlparse(uri)
    if parsed.scheme in {"", "file"}:
        if parsed.scheme == "file":
            netloc = parsed.netloc or ""
            if netloc not in {"", "localhost"}:
                if not allow_remote:
                    return _default_tracking_dir().as_uri(), "remote_disallowed"
                return uri, ""
            target = Path(parsed.path or ".")
        else:
            target = Path(uri)
        return _as_file_uri(str(target)), ""

    if allow_remote:
        return uri, ""

    return _default_tracking_dir().as_uri(), "remote_disallowed"


def _resolve_allow_remote_flag(raw: Optional[str]) -> tuple[str, bool]:
    text = (raw or "").strip()
    allow = text.lower() in {"1", "true", "yes", "on"}
    return text, allow


def last_decision() -> Optional[GuardDecision]:
    """Return the most recent guard decision, if any."""

    return _LAST_DECISION


def ensure_file_backend(
    *,
    allow_remote: bool = False,
    force: bool = False,
    requested_uri: str | None = None,
    allow_remote_flag: str | None = None,
) -> str:
    """Ensure MLflow uses a ``file:`` URI unless remote backends are allowed."""

    tracking_env = os.environ.get("MLFLOW_TRACKING_URI", "").strip()
    codex_env = os.environ.get("CODEX_MLFLOW_URI", "").strip()
    candidate = (requested_uri or "").strip() or tracking_env or codex_env
    normalised, fallback_reason = _normalise_candidate(candidate, allow_remote=allow_remote)

    if force or not tracking_env or tracking_env != normalised:
        os.environ["MLFLOW_TRACKING_URI"] = normalised
    if force or not codex_env or codex_env != normalised:
        os.environ["CODEX_MLFLOW_URI"] = normalised

    if ("MLFLOW_ENABLE_SYSTEM_METRICS" not in os.environ) or force:
        os.environ["MLFLOW_ENABLE_SYSTEM_METRICS"] = "false"

    metrics_enabled = os.environ.get("MLFLOW_ENABLE_SYSTEM_METRICS", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }

    env_name = "MLFLOW_ALLOW_REMOTE"
    if allow_remote_flag is None:
        raw_flag = os.environ.get(env_name)
        if not raw_flag:
            legacy_env = os.environ.get("CODEX_MLFLOW_ALLOW_REMOTE")
            if legacy_env is not None:
                env_name = "CODEX_MLFLOW_ALLOW_REMOTE"
                raw_flag = legacy_env
    else:
        raw_flag = allow_remote_flag
    flag_value, allow_remote_from_flag = _resolve_allow_remote_flag(raw_flag)

    global _LAST_DECISION
    _LAST_DECISION = GuardDecision(
        requested_uri=candidate,
        effective_uri=normalised,
        fallback_reason=fallback_reason,
        allow_remote_env=env_name,
        allow_remote_flag=flag_value,
        allow_remote=allow_remote or allow_remote_from_flag,
        system_metrics_enabled=metrics_enabled,
    )

    return normalised


def bootstrap_offline_tracking(*, force: bool = False, requested_uri: str | None = None) -> str:
    """Bootstrap tracking configuration respecting the remote override flag."""

    allow_remote_env = "MLFLOW_ALLOW_REMOTE"
    raw_flag = os.environ.get(allow_remote_env)
    if not raw_flag:
        legacy_flag = os.environ.get("CODEX_MLFLOW_ALLOW_REMOTE")
        if legacy_flag is not None:
            allow_remote_env = "CODEX_MLFLOW_ALLOW_REMOTE"
            raw_flag = legacy_flag
    flag_text, allow_remote = _resolve_allow_remote_flag(raw_flag)
    return ensure_file_backend(
        allow_remote=allow_remote,
        force=force,
        requested_uri=requested_uri,
        allow_remote_flag=flag_text,
    )
