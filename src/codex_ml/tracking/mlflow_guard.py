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
    "ensure_file_backend_decision",
    "bootstrap_offline_tracking",
    "bootstrap_offline_tracking_decision",
]


@dataclass(frozen=True)
class GuardDecision:
    """Outcome of an MLflow guard evaluation."""

    requested_uri: str
    effective_uri: str
    fallback_reason: Optional[str]
    allow_remote_flag: str
    allow_remote: bool
    system_metrics_enabled: bool

    @property
    def uri(self) -> str:
        """Return the effective tracking URI."""

        return self.effective_uri


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


def _normalise_candidate(uri: str, *, allow_remote: bool) -> tuple[str, Optional[str]]:
    if not uri:
        return _default_tracking_dir().as_uri(), None

    parsed = urlparse(uri)
    if parsed.scheme in {"", "file"}:
        if parsed.scheme == "file":
            netloc = parsed.netloc or ""
            if netloc not in {"", "localhost"}:
                if not allow_remote:
                    return _default_tracking_dir().as_uri(), "non_local_host"
                return uri, None
            target = Path(parsed.path or ".")
        else:
            target = Path(uri)
        return _as_file_uri(str(target)), None

    if allow_remote:
        return uri, None

    return _default_tracking_dir().as_uri(), "non_file_scheme"


def _coerce_bool_flag(value: Optional[str]) -> bool:
    if value is None:
        return False
    text = value.strip().lower()
    return text in {"1", "true", "yes", "on"}


def _record_decision(decision: GuardDecision) -> GuardDecision:
    global _LAST_DECISION
    _LAST_DECISION = decision
    return decision


def _apply_guard(
    *, allow_remote: bool, allow_remote_flag: Optional[str], force: bool
) -> GuardDecision:
    tracking_env = os.environ.get("MLFLOW_TRACKING_URI", "").strip()
    codex_env = os.environ.get("CODEX_MLFLOW_URI", "").strip()
    candidate = tracking_env or codex_env
    normalised, fallback_reason = _normalise_candidate(candidate, allow_remote=allow_remote)

    if force or not tracking_env or tracking_env != normalised:
        os.environ["MLFLOW_TRACKING_URI"] = normalised
    if force or not codex_env or codex_env != normalised:
        os.environ["CODEX_MLFLOW_URI"] = normalised

    if ("MLFLOW_ENABLE_SYSTEM_METRICS" not in os.environ) or force:
        os.environ["MLFLOW_ENABLE_SYSTEM_METRICS"] = "false"

    system_metrics_enabled = _coerce_bool_flag(os.environ.get("MLFLOW_ENABLE_SYSTEM_METRICS"))
    flag_value = allow_remote_flag or ("1" if allow_remote else "")
    decision = GuardDecision(
        requested_uri=candidate or "",
        effective_uri=normalised,
        fallback_reason=fallback_reason,
        allow_remote_flag=flag_value,
        allow_remote=allow_remote,
        system_metrics_enabled=system_metrics_enabled,
    )
    return _record_decision(decision)


_LAST_DECISION: Optional[GuardDecision] = None


def ensure_file_backend(
    *, allow_remote: bool = False, force: bool = False, allow_remote_flag: Optional[str] = None
) -> str:
    """Ensure MLflow uses a ``file:`` URI unless remote backends are allowed."""

    decision = _apply_guard(
        allow_remote=allow_remote, allow_remote_flag=allow_remote_flag, force=force
    )
    return decision.effective_uri


def ensure_file_backend_decision(
    *, allow_remote: bool = False, force: bool = False, allow_remote_flag: Optional[str] = None
) -> GuardDecision:
    """Return the full guard decision while enforcing the MLflow backend."""

    return _apply_guard(allow_remote=allow_remote, allow_remote_flag=allow_remote_flag, force=force)


def bootstrap_offline_tracking(*, force: bool = False, requested_uri: str | None = None) -> str:
    """Bootstrap tracking configuration respecting the remote override flag."""

    allow_remote_flag = os.environ.get("MLFLOW_ALLOW_REMOTE", "").strip()
    allow_remote = _coerce_bool_flag(allow_remote_flag)
    return ensure_file_backend(
        allow_remote=allow_remote, allow_remote_flag=allow_remote_flag, force=force
    )


def bootstrap_offline_tracking_decision(*, force: bool = False) -> GuardDecision:
    """Return the guard decision used during bootstrap."""

    allow_remote_flag = os.environ.get("MLFLOW_ALLOW_REMOTE", "").strip()
    allow_remote = _coerce_bool_flag(allow_remote_flag)
    return ensure_file_backend_decision(
        allow_remote=allow_remote, allow_remote_flag=allow_remote_flag, force=force
    )
