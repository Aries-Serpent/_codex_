# [Module]: MLflow offline helper
# > Generated: 2025-08-26 20:36:12 | Author: mbaetiong
import importlib
import os
from contextlib import contextmanager, nullcontext
from typing import Any, Generator, Optional

__all__ = ["mlflow_offline_session"]


def _safe_import_mlflow() -> Optional[Any]:
    """Return the ``mlflow`` module if available, otherwise ``None``."""

    try:  # pragma: no cover - exercised in integration tests
        return importlib.import_module("mlflow")  # type: ignore[return-value]
    except Exception:
        return None


@contextmanager
def mlflow_offline_session(
    artifacts_dir: str = ".artifacts/mlflow",
    *,
    experiment: Optional[str] = "local",
    run_name: Optional[str] = None,
    start_run: bool = True,
    run_tags: Optional[dict[str, str]] = None,
) -> Generator[Optional[Any], None, None]:
    """Context manager that keeps MLflow interactions strictly local.

    Parameters
    ----------
    artifacts_dir:
        Directory used for the local MLflow tracking URI. Created on demand.
    experiment:
        Experiment name configured when MLflow is available.
    run_name:
        Optional run name forwarded to ``mlflow.start_run``.
    start_run:
        When ``True`` (the default) an MLflow run is opened and the active run
        object is yielded. When ``False`` the raw ``mlflow`` module is yielded
        instead so callers can manage the run manually.
    run_tags:
        Optional tag mapping supplied to ``mlflow.start_run`` when a run is
        created inside the context.

    Yields
    ------
    Optional[Any]
        ``None`` when MLflow is unavailable. If MLflow is installed this yields
        the active run when ``start_run`` is ``True`` or the module itself when
        ``start_run`` is ``False``.
    """

    os.makedirs(artifacts_dir, exist_ok=True)
    prev_uri = os.environ.get("MLFLOW_TRACKING_URI")
    env_had_uri = "MLFLOW_TRACKING_URI" in os.environ
    prev_local_dir = os.environ.get("CODEX_MLFLOW_LOCAL_DIR")
    resolved_dir = os.path.abspath(artifacts_dir)
    os.environ["CODEX_MLFLOW_LOCAL_DIR"] = resolved_dir

    from codex_ml.tracking.mlflow_guard import ensure_file_backend

    mlflow = _safe_import_mlflow()
    run_cm: Any
    yielded: Optional[Any]

    try:
        if mlflow is None:
            run_cm = nullcontext(None)
            yielded = None
        else:
            try:
                local_uri = ensure_file_backend(force=True)
                mlflow.set_tracking_uri(local_uri)  # type: ignore[attr-defined]
                if experiment:
                    mlflow.set_experiment(experiment)  # type: ignore[attr-defined]
            except Exception as exc:  # pragma: no cover - defensive guard
                raise RuntimeError("Failed to configure MLflow for offline use") from exc

            if start_run:
                run_cm = mlflow.start_run(run_name=run_name, tags=run_tags or {})
                yielded = run_cm
            else:
                run_cm = nullcontext(mlflow)
                yielded = mlflow

        with run_cm as active:
            if start_run and mlflow is not None:
                yielded = active
            yield yielded
    finally:
        if env_had_uri and prev_uri is not None:
            os.environ["MLFLOW_TRACKING_URI"] = prev_uri
        else:
            os.environ.pop("MLFLOW_TRACKING_URI", None)
        if prev_local_dir is not None:
            os.environ["CODEX_MLFLOW_LOCAL_DIR"] = prev_local_dir
        else:
            os.environ.pop("CODEX_MLFLOW_LOCAL_DIR", None)
