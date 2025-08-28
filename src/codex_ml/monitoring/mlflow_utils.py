import os

try:
    import mlflow
except Exception:  # pragma: no cover - optional
    mlflow = None  # type: ignore


def maybe_start_run(run_name: str | None = None):
    if not mlflow or not os.environ.get("MLFLOW_TRACKING_URI"):
        return None
    mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])
    return mlflow.start_run(run_name=run_name)
