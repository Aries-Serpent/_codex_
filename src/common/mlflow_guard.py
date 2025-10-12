from __future__ import annotations

import contextlib
import hashlib
import json
import os
from pathlib import Path
from typing import Any

try:  # pragma: no cover - optional dependency
    import mlflow
except Exception:  # pragma: no cover - mlflow not installed or misconfigured
    mlflow = None  # type: ignore

from omegaconf import DictConfig, OmegaConf

from .provenance import _read_dvc_lock, collect_dvc_stage


def _config_fingerprint(cfg: DictConfig) -> str:
    """Stable SHA256 of resolved config YAML (aligned with provenance)."""
    yml = OmegaConf.to_yaml(cfg, resolve=True)
    return hashlib.sha256(yml.encode("utf-8")).hexdigest()


def _dataset_hash_from_dvc(
    lock_path: Path = Path("dvc.lock"), stage: str = "prepare"
) -> str | None:
    lock = _read_dvc_lock(lock_path)
    st = collect_dvc_stage(lock, stage=stage) if lock else None
    if not st:
        return None
    for _, meta in (st.outs or {}).items():  # type: ignore[attr-defined]
        h = meta.get("md5")
        if h:
            return h
    return None


def ensure_local_tracking(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(cfg, "monitor", None)
        tracking = getattr(monitor, "tracking", None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, "allow_remote", False))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("file:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=True, exist_ok=True)

    return mlflow


def start_run_with_tags(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment(name="hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=True)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def log_artifacts_safe(paths: dict[str, Path]) -> None:
    """Log small artifacts if MLflow available; ignore failures silently."""
    if mlflow is None:
        return

    for name, path in paths.items():
        with contextlib.suppress(Exception):
            if path.is_file():
                mlflow.log_artifact(str(path), artifact_path=name)


def log_dict_safe(payload: Any, artifact_path: str | Path) -> None:
    """Log dictionaries via MLflow if available; fallback to local JSON."""

    target = Path(artifact_path)
    data = payload

    if mlflow is not None:
        with contextlib.suppress(Exception):
            mlflow.log_dict(data, str(target))
            return

    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
