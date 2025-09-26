"""Unified experiment tracking helper with offline defaults."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Optional

try:  # pragma: no cover - optional dependency
    import mlflow
except Exception:  # pragma: no cover - mlflow optional
    mlflow = None  # type: ignore

try:  # pragma: no cover - optional dependency
    import wandb
except Exception:  # pragma: no cover - wandb optional
    wandb = None  # type: ignore


class Tracker:
    """Small facade that logs metrics to MLflow and/or Weights & Biases."""

    def __init__(self) -> None:
        self.mlflow_active = False
        self.wandb_active = False

    def start(
        self, run_name: Optional[str] = None, params: Optional[Dict[str, object]] = None
    ) -> None:
        if os.getenv("MLFLOW_ENABLE", "0") == "1" and mlflow is not None:
            uri = os.getenv("MLFLOW_URI", f"file:{Path('artifacts/mlruns').resolve()}")
            mlflow.set_tracking_uri(uri)
            experiment = os.getenv("MLFLOW_EXPERIMENT", "codex")
            mlflow.set_experiment(experiment)
            mlflow.start_run(run_name=run_name)
            if params:
                mlflow.log_params(params)
            self.mlflow_active = True
        if os.getenv("WANDB_ENABLE", "0") == "1" and wandb is not None:
            os.environ.setdefault("WANDB_MODE", "offline")
            project = os.getenv("WANDB_PROJECT", "codex")
            wandb_dir = Path(os.getenv("WANDB_DIR", "artifacts/wandb"))
            wandb_dir.mkdir(parents=True, exist_ok=True)
            wandb.init(project=project, dir=str(wandb_dir), name=run_name, reinit=True)
            if params:
                wandb.config.update(params, allow_val_change=True)
            self.wandb_active = True

    def log_metrics(self, metrics: Dict[str, float], step: Optional[int] = None) -> None:
        if self.mlflow_active and mlflow is not None:
            mlflow.log_metrics(metrics, step=step)
        if self.wandb_active and wandb is not None:
            payload = dict(metrics)
            if step is not None:
                payload["step"] = step
            wandb.log(payload)

    def log_artifact(self, path: str | Path) -> None:
        if self.mlflow_active and mlflow is not None:
            mlflow.log_artifact(str(path))
        if self.wandb_active and wandb is not None:
            wandb.save(str(path))

    def end(self) -> None:
        if self.mlflow_active and mlflow is not None:
            mlflow.end_run()
            self.mlflow_active = False
        if self.wandb_active and wandb is not None:
            wandb.finish()
            self.wandb_active = False


__all__ = ["Tracker"]
