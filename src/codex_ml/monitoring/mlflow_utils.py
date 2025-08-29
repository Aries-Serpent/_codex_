import os

try:
    import mlflow
except Exception:  # pragma: no cover - optional
    mlflow = None  # type: ignore


def maybe_start_run(run_name: str | None = None):
    """Start an MLflow run when the library and URI are available.

    Returns ``None`` when MLflow is missing or the ``MLFLOW_TRACKING_URI``
    environment variable is not set.
    """
    uri = os.environ.get("MLFLOW_TRACKING_URI")
    if not mlflow or not uri:
        return None
    mlflow.set_tracking_uri(uri)
    return mlflow.start_run(run_name=run_name)
