import os

try:
    import mlflow
except Exception:  # pragma: no cover - optional
    mlflow = None  # type: ignore


def _env_enabled(value: str | None) -> bool:
    """Interpret truthy environment strings."""
    return str(value).lower() in {"1", "true", "yes", "on"}


def maybe_start_run(run_name: str | None = None, *, enabled: bool | None = None):
    """Start an MLflow run when the library and URI are available.

    Parameters
    ----------
    run_name:
        Optional name for the MLflow run.
    enabled:
        If ``True`` MLflow will attempt to start a run regardless of the
        ``CODEX_ENABLE_MLFLOW`` environment variable. When ``None`` (default)
        the environment variable is consulted. Any falsy value prevents
        tracking.

    Returns
    -------
    mlflow.entities.Run | None
        ``None`` when MLflow is missing, tracking is disabled or the
        ``MLFLOW_TRACKING_URI`` environment variable is not set.
    """
    if enabled is None:
        enabled = _env_enabled(os.environ.get("CODEX_ENABLE_MLFLOW"))
    if not enabled:
        return None

    uri = os.environ.get("MLFLOW_TRACKING_URI")
    if not mlflow or not uri:
        return None
    mlflow.set_tracking_uri(uri)
    try:
        return mlflow.start_run(run_name=run_name)
    except Exception:  # pragma: no cover - mlflow runtime errors
        return None
