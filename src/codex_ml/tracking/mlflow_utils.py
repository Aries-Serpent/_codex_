from __future__ import annotations

from pathlib import Path
from typing import Any, ContextManager, Mapping, Optional
import json

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
        Optional tracking URI (e.g. ``"file:./mlruns"``).
    """

    try:  # pragma: no cover - optional dependency
        import mlflow
    except Exception:
        return None
    if tracking_uri:
        mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment)
    return mlflow.start_run()


def log_params(d: Mapping[str, Any]) -> None:
    try:  # pragma: no cover
        import mlflow

        mlflow.log_params(dict(d))
    except Exception:
        pass


def log_metrics(d: Mapping[str, float], step: Optional[int] = None) -> None:
    try:  # pragma: no cover
        import mlflow

        mlflow.log_metrics(dict(d), step=step)
    except Exception:
        pass


def log_artifacts(path: str | Path) -> None:
    try:  # pragma: no cover
        import mlflow

        mlflow.log_artifacts(str(path))
    except Exception:
        pass


def seed_snapshot(seeds: Mapping[str, Any], out_dir: Path) -> Path:
    """Write ``seeds.json`` and log as artifact when possible."""

    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "seeds.json"
    path.write_text(json.dumps(dict(seeds), indent=2), encoding="utf-8")
    log_artifacts(path)
    return path


def ensure_local_artifacts(run_dir: Path, summary: Mapping[str, Any], seeds: Mapping[str, Any]) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "summary.json").write_text(json.dumps(dict(summary), indent=2), encoding="utf-8")
    seed_snapshot(seeds, run_dir)
