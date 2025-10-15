"""Utility helpers for optional experiment logging backends."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from utils.error_logging import append_error

try:  # pragma: no cover - optional dependency guard
    from torch.utils.tensorboard import SummaryWriter
except Exception:  # pragma: no cover - keep API usable without tensorboard
    SummaryWriter = None  # type: ignore[assignment]

try:  # pragma: no cover - optional dependency guard
    import mlflow
except Exception:  # pragma: no cover - keep API usable without mlflow
    mlflow = None  # type: ignore[assignment]


@dataclass(slots=True)
class LoggingConfig:
    """Configuration flags shared between the extended trainer and CLI."""

    enable_tensorboard: bool = False
    tensorboard_log_dir: str = ".codex/tensorboard"
    enable_mlflow: bool = False
    mlflow_run_name: str = "codex-trainer"
    mlflow_tracking_uri: str | None = "file:./mlruns"
    mlflow_tags: dict[str, str] = field(default_factory=dict)


def init_tensorboard(log_dir: str) -> SummaryWriter | None:
    """Initialise a ``SummaryWriter`` if tensorboard is available."""

    if SummaryWriter is None:
        append_error("3.3", "tensorboard init", "tensorboard is not installed", log_dir)
        return None
    try:
        return SummaryWriter(log_dir)
    except Exception as exc:  # pragma: no cover - defensive guard
        append_error("3.3", "tensorboard init", str(exc), log_dir)
        return None


def init_mlflow(
    run_name: str,
    tracking_uri: str | None = "file:./mlruns",
    tags: dict[str, str] | None = None,
) -> tuple[Any | None, Any | None]:
    """Initialise an MLflow run when the dependency is present.

    Returns a tuple of ``(mlflow_module, active_run)``. Both entries are
    ``None`` when MLflow is unavailable.
    """

    if mlflow is None:
        append_error("3.3", "mlflow init", "mlflow is not installed", run_name)
        return None, None
    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(run_name)
        active = mlflow.start_run(run_name=run_name, tags=tags)
        return mlflow, active
    except Exception as exc:  # pragma: no cover - defensive guard
        append_error("3.3", "mlflow init", str(exc), run_name)
        return mlflow, None
