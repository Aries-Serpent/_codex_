# BEGIN: CODEX_MLFLOW_UTILS
# MLflow wrappers (no-op if mlflow missing)
from __future__ import annotations

from pathlib import Path
from typing import Iterable


def start_run(tracking_uri: str | None = None, experiment_name: str | None = None):
    """Start an MLflow run using a safe offline default.

    If ``tracking_uri`` is not provided, runs log to ``./mlruns`` to avoid
    accidental network calls. Any import or runtime failure results in a
    silent ``None`` return so training can proceed without MLflow.
    """

    try:
        import mlflow

        mlflow.set_tracking_uri(tracking_uri or "./mlruns")
        if experiment_name:
            mlflow.set_experiment(experiment_name)
        return mlflow.start_run()
    except Exception:
        return None


def log_params(params: dict):
    try:
        import mlflow

        mlflow.log_params(params)
    except Exception:
        pass


def log_metrics(metrics: dict, step: int):
    try:
        import mlflow

        for k, v in metrics.items():
            mlflow.log_metric(k, float(v), step=step)
    except Exception:
        pass


def log_artifacts(paths: Iterable[Path]):
    try:
        import mlflow

        for p in paths:
            mlflow.log_artifact(str(p))
    except Exception:
        pass


# END: CODEX_MLFLOW_UTILS
