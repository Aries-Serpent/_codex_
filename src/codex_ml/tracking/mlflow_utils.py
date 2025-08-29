# [Python]: MLflow utilities
# > Generated: 2025-08-29 19:48:13 | Author: mbaetiong

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, ContextManager, Mapping, Optional

__all__ = [
    "start_run",
    "log_params",
    "log_metrics",
    "log_artifacts",
    "seed_snapshot",
    "ensure_local_artifacts",
]


def start_run(experiment: str, tracking_uri: Optional[str] = None) -> Optional[ContextManager[Any]]:
    """Start an MLflow run if available; otherwise return ``None``.

    Parameters
    ----------
    experiment:
        Experiment name to create/use.
    tracking_uri:
        Optional tracking URI (e.g. "file:./mlruns").
    """
    try:  # pragma: no cover - optional dependency
        import mlflow
    except Exception:
        return None

    if tracking_uri:
        mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment)
    return mlflow.start_run()


def log_params(d: Mapping[str, Any], *, enabled: Optional[bool] = None) -> None:
    """Log parameters if MLflow is available.

    Backward compatible:
    - enabled=None (default): attempt to log (no-op if mlflow missing), swallow errors.
    - enabled=True: attempt to log, swallow errors.
    - enabled=False: do nothing.
    """
    should_log = (enabled is None) or bool(enabled)
    if not should_log:
        return
    try:  # pragma: no cover
        import mlflow

        mlflow.log_params(dict(d))
    except Exception:
        pass


def log_metrics(d: Mapping[str, float], step: Optional[int] = None, *, enabled: Optional[bool] = None) -> None:
    """Log metrics if MLflow is available.

    Backward compatible gating behavior; see log_params.
    """
    should_log = (enabled is None) or bool(enabled)
    if not should_log:
        return
    try:  # pragma: no cover
        import mlflow

        mlflow.log_metrics(dict(d), step=step)
    except Exception:
        pass


def log_artifacts(path: str | Path, *, enabled: Optional[bool] = None) -> None:
    """Log artifacts directory or file if MLflow is available.

    Backward compatible gating behavior; see log_params.
    """
    should_log = (enabled is None) or bool(enabled)
    if not should_log:
        return
    try:  # pragma: no cover
        import mlflow

        mlflow.log_artifacts(str(path))
    except Exception:
        pass


def seed_snapshot(seeds: Mapping[str, Any], out_dir: Path, *, enabled: Optional[bool] = None) -> Path:
    """Write ``seeds.json`` under ``out_dir`` and (optionally) log it as an artifact."""
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "seeds.json"
    path.write_text(json.dumps(dict(seeds), indent=2), encoding="utf-8")
    log_artifacts(path, enabled=enabled)
    return path


def ensure_local_artifacts(run_dir: Path, summary: Mapping[str, Any], seeds: Mapping[str, Any], *, enabled: Optional[bool] = None) -> None:
    """Ensure local artifact files are written, and optionally log via MLflow.

    Writes:
    - summary.json
    - seeds.json
    """
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "summary.json").write_text(json.dumps(dict(summary), indent=2), encoding="utf-8")
    seed_snapshot(seeds, run_dir, enabled=enabled)
    