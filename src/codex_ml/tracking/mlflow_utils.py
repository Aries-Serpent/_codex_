from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, ContextManager, Dict, Mapping, Optional, Union

__all__ = [
    "MlflowConfig",
    "start_run",
    "log_params",
    "log_metrics",
    "log_artifacts",
    "seed_snapshot",
    "ensure_local_artifacts",
]


@dataclass
class MlflowConfig:
    """Lightweight configuration for optional MLflow tracking."""

    enable: bool = True
    tracking_uri: str | None = None
    experiment: str = "default"


def start_run(
    cfg_or_experiment: Union[MlflowConfig, str], tracking_uri: str | None = None
) -> Optional[ContextManager[Any]]:
    """Start an MLflow run if MLflow is installed; otherwise return ``None``.

    Accepts either a :class:`MlflowConfig` or an experiment name for backward
    compatibility with older helper utilities.
    """

    if isinstance(cfg_or_experiment, MlflowConfig):
        if not cfg_or_experiment.enable:
            return None
        experiment = cfg_or_experiment.experiment
        tracking_uri = cfg_or_experiment.tracking_uri
    else:
        experiment = cfg_or_experiment

    try:
        import mlflow
    except Exception:  # pragma: no cover - optional dep
        return None

    if tracking_uri:
        mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment)
    return mlflow.start_run()


def log_params(d: Mapping[str, Any], *, enabled: bool = False) -> None:
    if not enabled:
        return
    try:
        import mlflow
    except Exception:  # pragma: no cover
        return
    mlflow.log_params(dict(d))


def log_metrics(
    d: Mapping[str, float], step: Optional[int] = None, *, enabled: bool = False
) -> None:
    if not enabled:
        return
    try:
        import mlflow
    except Exception:  # pragma: no cover
        return
    mlflow.log_metrics(dict(d), step=step)


def log_artifacts(path: str | Path, *, enabled: bool = False) -> None:
    if not enabled:
        return
    try:
        import mlflow
    except Exception:  # pragma: no cover
        return
    mlflow.log_artifacts(str(path))


def seed_snapshot(seeds: Mapping[str, Any], out_dir: Path, *, enabled: bool = False) -> Path:
    """Write ``seeds.json`` under ``out_dir`` and log it when enabled."""

    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "seeds.json"
    path.write_text(json.dumps(dict(seeds), indent=2), encoding="utf-8")
    log_artifacts(path, enabled=enabled)
    return path


def ensure_local_artifacts(run_dir: Path, summary: Dict[str, Any], seeds: Dict[str, Any]) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    seed_snapshot(seeds, run_dir)


# END: CODEX_MLFLOW_UTILS
