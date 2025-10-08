"""Tracking/Logging guards for offline-first enforcement.

WHY:
- Prevent silent remote egress when users expect offline/local tracking.
- Normalize MLflow URIs to file:// scheme under offline modes.
- Provide a structured decision object for auditability.

RISK:
- Overzealous blocking could surprise users who *intentionally* configured remote endpoints.
  Mitigation: explicit allow-remote env override.

ROLLBACK:
- Set CODEX_ALLOW_REMOTE_TRACKING=1 to disable enforcement without removing this module.

References:
- MLflow tracking URI schemes (remote vs local): https://mlflow.org/docs/latest/ml/tracking/   # see "Tracking"
- Weights & Biases offline modes: https://docs.wandb.ai/guides/track/environment-variables/    # WANDB_MODE
- W&B offline guide: https://docs.wandb.ai/support/run_wandb_offline/
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

REMOTE_SCHEMES = ("http://", "https://", "databricks://")
LOCAL_SCHEMES = ("file://", "sqlite://", "postgresql+sqlite://")
LEGACY_ALLOW_REMOTE_ENVIRONMENTS = ("MLFLOW_ALLOW_REMOTE", "CODEX_MLFLOW_ALLOW_REMOTE")


def _as_mlflow_file_uri(p: Path | str) -> str:
    """Return MLflow's canonical file URI form (``file:///abs/path``)."""

    return Path(p).resolve().as_uri()


DEFAULT_LOCAL_URI = _as_mlflow_file_uri(Path.cwd() / "mlruns")


def _local_runs_uri_from_env(env: Mapping[str, str]) -> str:
    override = (env.get("CODEX_MLFLOW_LOCAL_DIR") or "").strip()
    if override:
        return _as_mlflow_file_uri(override)
    return DEFAULT_LOCAL_URI


def _truthy(val: Optional[str]) -> bool:
    if val is None:
        return False
    return val.strip().lower() in {"1", "true", "yes", "y", "on", "enabled"}


def _is_remote_uri(uri: str) -> bool:
    return uri.startswith(REMOTE_SCHEMES)


def _is_local_uri(uri: str) -> bool:
    return uri.startswith(LOCAL_SCHEMES) or uri.startswith("file:")


@dataclass(frozen=True)
class TrackingDecision:
    uri: Optional[str]
    blocked: bool
    reason: str
    details: Dict[str, Any]


def normalize_mlflow_uri(uri: Optional[str]) -> Optional[str]:
    """
    If `uri` is a bare path or relative dir, convert to file:// absolute.
    If already a file:// or sqlite:// (local DB) URI, leave as-is.
    """
    if uri is None or uri == "":
        return None
    if _is_local_uri(uri) or _is_remote_uri(uri):
        return uri
    # Treat as path-like -> upgrade to file:// absolute
    return _as_mlflow_file_uri(Path(uri))


def decide_mlflow_tracking_uri(
    env: Optional[Dict[str, str]] = None,
    allow_remote_env: str = "CODEX_ALLOW_REMOTE_TRACKING",
    additional_allow_remote_envs: tuple[str, ...] = LEGACY_ALLOW_REMOTE_ENVIRONMENTS,
) -> TrackingDecision:
    """
    Enforce offline-first behavior.

    Logic:
      1) If allow-remote override is set truthy -> return configured URI unchanged.
      2) Determine offline mode via any of:
           - MLFLOW_OFFLINE truthy
           - WANDB_MODE in {"offline", "disabled"} OR WANDB_DISABLED truthy
      3) If offline and a remote URI is set -> rewrite to file:// (absolute ./mlruns)
      4) If offline and no URI -> fill a default file:// (absolute ./mlruns)
      5) Otherwise: normalize local paths to file:// absolute for consistency.
    """
    e = os.environ if env is None else env

    allow_remote_env_names: tuple[str, ...]
    if additional_allow_remote_envs:
        allow_remote_env_names = (allow_remote_env,) + tuple(additional_allow_remote_envs)
    else:
        allow_remote_env_names = (allow_remote_env,)

    allow_remote = False
    allow_remote_source: Optional[str] = None
    allow_remote_values: Dict[str, str] = {}
    for env_name in allow_remote_env_names:
        raw_value = e.get(env_name)
        if raw_value is not None:
            allow_remote_values[env_name] = raw_value
            if not allow_remote and _truthy(raw_value):
                allow_remote = True
                allow_remote_source = env_name
    if allow_remote and allow_remote_source is None:
        # Defensive: default to the primary flag name if we somehow
        # recorded a truthy value without the source.
        allow_remote_source = allow_remote_env
    mlflow_uri = e.get("MLFLOW_TRACKING_URI")
    mlflow_uri_norm = normalize_mlflow_uri(mlflow_uri)

    # Offline signals
    wandb_mode = (e.get("WANDB_MODE") or "").strip().lower()
    wandb_disabled = _truthy(e.get("WANDB_DISABLED"))
    mlflow_offline = _truthy(e.get("MLFLOW_OFFLINE"))
    offline = mlflow_offline or wandb_mode in {"offline", "disabled"} or wandb_disabled

    if allow_remote:
        # Explicit opt-out of enforcement
        return TrackingDecision(
            uri=mlflow_uri_norm,
            blocked=False,
            reason="explicit_allow",
            details={
                "allow_env": allow_remote_source or allow_remote_env,
                "offline": offline,
                "allow_env_values": allow_remote_values,
            },
        )

    # Enforce offline
    if offline:
        # Remote -> rewrite to local
        if mlflow_uri_norm and _is_remote_uri(mlflow_uri_norm):
            local_uri = _local_runs_uri_from_env(e)
            return TrackingDecision(
                uri=local_uri,
                blocked=True,
                reason="offline_enforced_rewrite_remote_to_local",
                details={"original": mlflow_uri_norm},
            )
        # None -> set default local
        if not mlflow_uri_norm:
            local_uri = _local_runs_uri_from_env(e)
            return TrackingDecision(
                uri=local_uri,
                blocked=False,
                reason="offline_default_local_uri",
                details={},
            )
        # Already local -> normalize path-like
        return TrackingDecision(
            uri=normalize_mlflow_uri(mlflow_uri_norm),
            blocked=False,
            reason="offline_local_ok",
            details={},
        )

    # Not offline: still normalize path-like to file:// absolute
    if mlflow_uri_norm and not (_is_remote_uri(mlflow_uri_norm) or _is_local_uri(mlflow_uri_norm)):
        mlflow_uri_norm = normalize_mlflow_uri(mlflow_uri_norm)

    return TrackingDecision(
        uri=mlflow_uri_norm,
        blocked=False,
        reason="no_enforcement",
        details={"offline": offline},
    )


__all__ = [
    "TrackingDecision",
    "decide_mlflow_tracking_uri",
    "normalize_mlflow_uri",
]
