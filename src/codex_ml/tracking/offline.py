from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


def _file_uri(p: Path) -> str:
    """Convert path to a RFC 8089-compliant file URI."""
    p = p.resolve()
    return p.as_uri()


@dataclass
class OfflineDecision:
    offline: bool
    reason: str
    mlflow_tracking_uri: str
    wandb_env: dict[str, str]


def decide_offline(
    *,
    prefer_offline: bool = True,
    allow_remote: bool = False,
    mlruns_dir: Optional[str | Path] = None,
) -> OfflineDecision:
    """
    Decide on offline posture for MLflow and W&B.

    If ``prefer_offline`` and remote URIs are not allowed, enforce a local ``file://``
    MLflow tracking URI and configure W&B to operate in offline mode.
    """

    env = os.environ
    default_store = Path(mlruns_dir) if mlruns_dir else (Path.cwd() / "mlruns")

    current_uri = env.get("MLFLOW_TRACKING_URI") or ""
    canonical_current = current_uri
    if current_uri.startswith("file:"):
        remainder = current_uri[len("file:") :]
        if remainder.startswith("///"):
            canonical_current = current_uri
        elif remainder.startswith("//"):
            # file://relative/path -- treat the remainder as a path.
            canonical_current = _file_uri(Path(remainder.lstrip("/")))
        else:
            canonical_current = _file_uri(Path(remainder))

    current_uri = canonical_current

    is_remote = current_uri.startswith(
        (
            "http://",
            "https://",
            "postgresql://",
            "mysql://",
            "sqlite://",
            "databricks",
        )
    )

    if prefer_offline and not allow_remote and (is_remote or not current_uri):
        mlflow_tracking_uri = _file_uri(default_store)
        offline = True
        reason = "prefer_offline=True and remote URIs are disallowed; forcing file:// store"
    else:
        mlflow_tracking_uri = current_uri or _file_uri(default_store)
        offline = prefer_offline
        reason = "respecting existing MLFLOW_TRACKING_URI"

    wandb_env: dict[str, str] = {}
    if prefer_offline and not allow_remote:
        wandb_mode = env.get("WANDB_MODE", "").lower()
        wandb_disabled = env.get("WANDB_DISABLED", "").lower()
        if wandb_mode != "offline" and wandb_disabled not in {"true", "1"}:
            wandb_env["WANDB_MODE"] = "offline"

    return OfflineDecision(
        offline=offline,
        reason=reason,
        mlflow_tracking_uri=mlflow_tracking_uri,
        wandb_env=wandb_env,
    )


def export_env_lines(decision: OfflineDecision) -> str:
    """Return shell ``export`` lines for the offline decision."""

    lines = [f'export MLFLOW_TRACKING_URI="{decision.mlflow_tracking_uri}"']
    for key, value in decision.wandb_env.items():
        lines.append(f'export {key}="{value}"')
    return "\n".join(lines) + "\n"
