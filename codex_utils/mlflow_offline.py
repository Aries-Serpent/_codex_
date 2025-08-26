# [Module]: MLflow offline helper
# > Generated: 2025-08-26 20:36:12 | Author: mbaetiong
import os
from contextlib import contextmanager


@contextmanager
def mlflow_offline_session(
    artifacts_dir: str = ".artifacts/mlflow", experiment: str = "local"
):
    """
    Offline-only MLflow context manager.
    - Forces MLFLOW_TRACKING_URI to a local file store
    - Does not import mlflow if not installed
    """
    os.makedirs(artifacts_dir, exist_ok=True)
    prev_uri = os.environ.get("MLFLOW_TRACKING_URI")
    os.environ["MLFLOW_TRACKING_URI"] = f"file://{os.path.abspath(artifacts_dir)}"
    try:
        try:
            import mlflow  # type: ignore

            mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])
            mlflow.set_experiment(experiment)
        except Exception:
            mlflow = None  # noqa: F841
        yield
    finally:
        if prev_uri is not None:
            os.environ["MLFLOW_TRACKING_URI"] = prev_uri
        else:
            os.environ.pop("MLFLOW_TRACKING_URI", None)
