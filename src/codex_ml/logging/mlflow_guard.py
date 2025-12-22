"""Offline-friendly MLflow helpers with graceful fallbacks."""

from __future__ import annotations

import logging
logger = logging.getLogger(__name__)
import os
from typing import Any, Mapping

try:  # pragma: no cover - optional import
    import mlflow
except Exception:  # pragma: no cover - environments without mlflow
    mlflow = None

from codex_ml.tracking.mlflow_guard import ensure_file_backend

LOGGER = logging.getLogger(__name__)


def _coerce_bool(value: str | None) -> bool:
    if value is None:
        return False
    text = value.strip().lower()
    return text in {"1", "true", "yes", "on"}


def init_mlflow_safe(offline_mode: bool | None = None) -> bool:
    """Initialise MLflow if available, respecting offline guardrails."""

    if offline_mode is None:
        offline_mode = _coerce_bool(os.environ.get("CODEX_OFFLINE_MODE"))

    if offline_mode:
        LOGGER.info("[codex] MLflow disabled: offline mode active")
        return False

    if mlflow is None:
        LOGGER.info("[codex] MLflow unavailable; continuing without experiment tracking")
        return False

    try:
        uri = ensure_file_backend(force=True)
        if mlflow.active_run():
            LOGGER.debug("[codex] MLflow run already active at %s", uri)
            return True
        mlflow.set_tracking_uri(uri)
        mlflow.start_run()
        LOGGER.info("[codex] MLflow initialised (uri=%s)", uri)
        return True
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.warning("[codex] MLflow initialisation failed: %s", exc)
        return False


def log_metric_safe(key: str, value: float, *, step: int | None = None) -> None:
    """Log an MLflow metric if the dependency and run are available."""

    if mlflow is None:
        return
    try:
        if mlflow.active_run():
            mlflow.log_metric(key, float(value), step=step)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("[codex] MLflow metric logging failed (%s): %s", key, exc)


def log_params_safe(params: Mapping[str, Any]) -> None:
    """Log a mapping of parameters if MLflow is active."""

    if mlflow is None:
        return
    try:
        if mlflow.active_run():
            mlflow.log_params(dict(params))
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("[codex] MLflow parameter logging failed: %s", exc)


def log_artifact_safe(path: str) -> None:
    """Log an artifact path with graceful degradation."""

    if mlflow is None:
        return
    try:
        if mlflow.active_run():
            mlflow.log_artifact(path)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("[codex] MLflow artifact logging failed for %s: %s", path, exc)


__all__ = [
    "init_mlflow_safe",
    "log_metric_safe",
    "log_params_safe",
    "log_artifact_safe",
]
