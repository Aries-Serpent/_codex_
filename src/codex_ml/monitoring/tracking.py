"""Unified experiment tracking helper with offline defaults."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Dict, Optional
from urllib.parse import urlparse

try:  # pragma: no cover - optional dependency
    import mlflow
except Exception:  # pragma: no cover - mlflow optional
    mlflow = None  # type: ignore

try:  # pragma: no cover - optional dependency
    import wandb
except Exception:  # pragma: no cover - wandb optional
    wandb = None  # type: ignore


logger = logging.getLogger(__name__)


class Tracker:
    """Small facade that logs metrics to MLflow and/or Weights & Biases."""

    def __init__(self) -> None:
        self.mlflow_active = False
        self.wandb_active = False

    def start(
        self, run_name: Optional[str] = None, params: Optional[Dict[str, object]] = None
    ) -> None:
        if os.getenv("MLFLOW_ENABLE", "0") == "1" and mlflow is not None:
            from codex_ml.tracking.mlflow_guard import bootstrap_offline_tracking

            requested_uri = os.getenv("MLFLOW_URI")
            safe_uri = bootstrap_offline_tracking(force=True)
            if requested_uri:
                parsed = urlparse(requested_uri)
                if parsed.scheme and parsed.scheme not in {"file", ""}:
                    logger.warning(
                        "Blocking remote MLflow URI '%s'; using local file backend %s",
                        requested_uri,
                        safe_uri,
                    )
                elif parsed.scheme in {"", "file"}:
                    try:
                        if parsed.scheme == "file":
                            safe_uri = requested_uri
                        else:
                            safe_uri = Path(requested_uri).expanduser().resolve().as_uri()
                    except Exception:
                        logger.warning(
                            "Unable to coerce MLflow URI '%s'; using %s",
                            requested_uri,
                            safe_uri,
                        )
            os.environ["MLFLOW_TRACKING_URI"] = safe_uri
            os.environ.setdefault("CODEX_MLFLOW_URI", safe_uri)
            mlflow.set_tracking_uri(safe_uri)
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
