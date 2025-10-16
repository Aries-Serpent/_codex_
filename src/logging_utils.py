"""Optional logging helpers for TensorBoard and MLflow."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from typing import Any

from codex_ml.utils.error_log import log_error


@dataclass(slots=True)
class MLflowRunHandle:
    """Thin wrapper exposing a minimal MLflow logging surface."""

    client: Any

    def log_metrics(self, metrics: Mapping[str, float], step: int | None = None) -> None:
        try:
            self.client.log_metrics(dict(metrics), step=step)
        except Exception as exc:  # pragma: no cover - runtime logging failure guard
            log_error("logging.mlflow", str(exc), "log_metrics")
            raise

    def log_params(self, params: Mapping[str, Any]) -> None:
        try:
            self.client.log_params(dict(params))
        except Exception as exc:  # pragma: no cover - runtime logging failure guard
            log_error("logging.mlflow", str(exc), "log_params")
            raise

    def end(self) -> None:
        try:
            self.client.end_run()
        except Exception as exc:  # pragma: no cover - runtime logging failure guard
            log_error("logging.mlflow", str(exc), "end_run")
            raise


def init_tensorboard(enabled: bool, log_dir: str | Path = "runs") -> Any | None:
    """Initialise a TensorBoard writer when ``enabled`` is true."""

    if not enabled:
        return None
    try:
        module = import_module("torch.utils.tensorboard")
        summary_writer = module.SummaryWriter
    except (ModuleNotFoundError, AttributeError) as exc:
        log_error("logging.tensorboard", str(exc), "import")
        return None
    try:
        return summary_writer(log_dir=str(log_dir))
    except Exception as exc:  # pragma: no cover - runtime writer failure guard
        log_error("logging.tensorboard", str(exc), f"create:{log_dir}")
        raise


def init_mlflow(
    enabled: bool,
    run_name: str,
    *,
    tracking_uri: str | None = None,
    experiment: str | None = None,
) -> MLflowRunHandle | None:
    """Initialise MLflow when requested and available."""

    if not enabled:
        return None
    try:
        mlflow_module = import_module("mlflow")
    except ModuleNotFoundError as exc:
        log_error("logging.mlflow", str(exc), "import")
        return None
    client = mlflow_module
    if tracking_uri:
        client.set_tracking_uri(tracking_uri)
    if experiment:
        client.set_experiment(experiment)
    client.start_run(run_name=run_name)
    return MLflowRunHandle(client)


def close_tensorboard(writer: Any | None) -> None:
    """Close a TensorBoard writer if it exposes a ``close`` method."""

    if writer is None:
        return
    close = getattr(writer, "close", None)
    if callable(close):
        close()


__all__ = [
    "MLflowRunHandle",
    "close_tensorboard",
    "init_mlflow",
    "init_tensorboard",
]
