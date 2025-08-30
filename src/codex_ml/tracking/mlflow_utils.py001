"""Lightweight MLflow helpers that tolerate missing dependencies."""
from __future__ import annotations

import contextlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Mapping, Optional


@dataclass
class MlflowConfig:
    enable: bool = False
    tracking_uri: str | None = None
    experiment: str = "codex-experiments"


def start_run(experiment: str, tracking_uri: str | None = None):
    """Attempt to start an MLflow run and return its context manager.

    If MLflow is not installed, a ``contextlib.nullcontext`` is returned so the
    caller can always use the result in a ``with`` statement.
    """

    try:
        import mlflow
    except Exception:  # pragma: no cover - optional dependency missing
        return contextlib.nullcontext(None)
    if tracking_uri:
        mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment)
    return mlflow.start_run()


def log_params(d: Mapping[str, Any], *, enabled: bool = True) -> None:
    if not enabled:
        return
    try:
        import mlflow
        mlflow.log_params(dict(d))
    except Exception:  # pragma: no cover
        pass


def log_metrics(
    d: Mapping[str, float],
    step: Optional[int] = None,
    *,
    enabled: bool = True,
) -> None:
    if not enabled:
        return
    try:
        import mlflow
        mlflow.log_metrics(dict(d), step=step)
    except Exception:  # pragma: no cover
        pass


def log_artifacts(path: str | Path, *, enabled: bool = True) -> None:
    if not enabled:
        return
    try:
        import mlflow
        mlflow.log_artifacts(str(path))
    except Exception:  # pragma: no cover
        pass


def seed_snapshot(
    seeds: Mapping[str, Any], out_dir: Path, *, enabled: bool = True
) -> Path:
    """Write ``seeds.json`` under ``out_dir`` and log it as an artifact."""

    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "seeds.json"
    path.write_text(json.dumps(dict(seeds), indent=2), encoding="utf-8")
    log_artifacts(path, enabled=enabled)
    return path


def ensure_local_artifacts(
    run_dir: Path, summary: Dict[str, Any], seeds: Dict[str, Any]
) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    seed_snapshot(seeds, run_dir)
