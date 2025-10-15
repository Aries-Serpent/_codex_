"""Lightweight logging utilities (TensorBoard + MLflow)."""

from __future__ import annotations

import logging
from collections.abc import Mapping, MutableMapping
from dataclasses import dataclass
from pathlib import Path

LOGGER = logging.getLogger(__name__)

try:  # pragma: no cover - tensorboard is optional in lightweight envs
    from torch.utils.tensorboard import SummaryWriter
except Exception:  # pragma: no cover - fall back to a stub
    SummaryWriter = None  # type: ignore[assignment]

try:  # pragma: no cover - MLflow is optional for offline smoke tests
    import mlflow
except Exception:  # pragma: no cover - guard offline runs that skip mlflow install
    mlflow = None  # type: ignore[assignment]


@dataclass(slots=True)
class LoggingConfig:
    enable_tensorboard: bool = False
    tensorboard_log_dir: str = "runs"
    enable_mlflow: bool = False
    mlflow_run_name: str = "codex-training"
    mlflow_tracking_uri: str | None = None
    mlflow_offline: bool = True


@dataclass(slots=True)
class LoggingSession:
    tensorboard: SummaryWriter | None
    mlflow_active: bool


def _create_tensorboard_writer(log_dir: str) -> SummaryWriter | None:
    if SummaryWriter is None:
        LOGGER.info("TensorBoard unavailable; skipping SummaryWriter initialisation")
        return None
    try:
        Path(log_dir).mkdir(parents=True, exist_ok=True)
    except Exception as exc:  # pragma: no cover - propagate context
        LOGGER.warning("Unable to create TensorBoard log directory '%s': %s", log_dir, exc)
        return None
    try:
        return SummaryWriter(log_dir)
    except Exception as exc:  # pragma: no cover - e.g. tensorboard not installed
        LOGGER.warning("Failed to initialise TensorBoard writer: %s", exc)
        return None


def _start_mlflow_run(config: LoggingConfig) -> bool:
    if not config.enable_mlflow:
        return False
    if mlflow is None:
        LOGGER.info("MLflow unavailable; skipping run creation")
        return False
    try:
        if config.mlflow_tracking_uri:
            mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        elif config.mlflow_offline:
            mlflow.set_tracking_uri("file:./mlruns")
        mlflow.start_run(run_name=config.mlflow_run_name)
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to start MLflow run '%s': %s", config.mlflow_run_name, exc)
        return False
    return True


def setup_logging(config: LoggingConfig | Mapping[str, object] | None) -> LoggingSession:
    """Initialise optional logging backends based on configuration."""

    if config is None:
        resolved = LoggingConfig()
    elif isinstance(config, LoggingConfig):
        resolved = config
    else:
        data: MutableMapping[str, object]
        if hasattr(config, "to_container"):
            data = config.to_container(resolve=True)  # type: ignore[attr-defined]
        else:
            data = dict(config)
        resolved = LoggingConfig(**data)

    writer = (
        _create_tensorboard_writer(resolved.tensorboard_log_dir)
        if resolved.enable_tensorboard
        else None
    )
    mlflow_active = _start_mlflow_run(resolved)
    return LoggingSession(tensorboard=writer, mlflow_active=mlflow_active)


def log_metrics(session: LoggingSession, metrics: Mapping[str, float], step: int) -> None:
    """Log scalar metrics to the configured backends."""

    if not metrics:
        return
    if session.tensorboard is not None:
        for key, value in metrics.items():
            try:
                session.tensorboard.add_scalar(key, value, step)
            except Exception as exc:  # pragma: no cover - robustness guard
                LOGGER.debug("TensorBoard logging failed for %s=%s: %s", key, value, exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("MLflow logging failed at step %s: %s", step, exc)


def shutdown_logging(session: LoggingSession) -> None:
    """Tear down logging resources gracefully."""

    if session.tensorboard is not None:
        try:
            session.tensorboard.flush()
            session.tensorboard.close()
        except Exception as exc:  # pragma: no cover - flush errors should not raise
            LOGGER.debug("TensorBoard writer shutdown encountered an error: %s", exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.end_run()
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("Failed to end MLflow run cleanly: %s", exc)


__all__ = [
    "LoggingConfig",
    "LoggingSession",
    "log_metrics",
    "setup_logging",
    "shutdown_logging",
]
