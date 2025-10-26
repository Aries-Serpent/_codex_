"""Lightweight logging fanout used by the training utilities."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping

__all__ = ["CodexLoggers", "_codex_log_all", "_codex_logging_bootstrap"]


@dataclass
class CodexLoggers:
    tensorboard: Any | None = None
    wandb: Any | None = None
    mlflow: Any | None = None
    extras: Dict[str, Any] = field(default_factory=dict)


def _codex_logging_bootstrap(args: Any) -> CodexLoggers:
    """Initialise optional loggers when their dependencies are available."""

    loggers = CodexLoggers()
    if getattr(args, "tensorboard", False):
        try:
            from torch.utils.tensorboard import SummaryWriter  # type: ignore

            loggers.tensorboard = SummaryWriter()
        except Exception:
            loggers.tensorboard = None
    if getattr(args, "enable_wandb", False):
        try:
            import wandb  # type: ignore

            wandb.init(mode="disabled")
            loggers.wandb = wandb
        except Exception:
            loggers.wandb = None
    if getattr(args, "mlflow_enable", False):
        try:
            import mlflow  # type: ignore

            loggers.mlflow = mlflow
        except Exception:
            loggers.mlflow = None
    return loggers


def _codex_log_all(step: int, metrics: Mapping[str, float], loggers: CodexLoggers) -> None:
    if loggers.tensorboard is not None:
        try:
            for key, value in metrics.items():
                loggers.tensorboard.add_scalar(key, value, step)
        except Exception:
            pass
    if loggers.wandb is not None:
        try:
            loggers.wandb.log(dict(metrics), step=step)
        except Exception:
            pass
    if loggers.mlflow is not None:
        try:
            loggers.mlflow.log_metrics(dict(metrics), step=step)
        except Exception:
            pass
