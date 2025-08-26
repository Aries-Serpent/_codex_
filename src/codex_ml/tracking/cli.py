# BEGIN: CODEX_MLFLOW_CLI
from __future__ import annotations

import argparse

from .mlflow_utils import MlflowConfig


def add_mlflow_flags(parser: argparse.ArgumentParser) -> None:
    """Attach MLflow tracking flags to an existing parser."""
    group = parser.add_argument_group("MLflow")
    group.add_argument(
        "--mlflow-enable",
        action="store_true",
        default=False,
        help="Enable MLflow logging (no-op if dependency missing)",
    )
    group.add_argument(
        "--mlflow-tracking-uri",
        default="./mlruns",
        help="Tracking URI or path (default: ./mlruns)",
    )
    group.add_argument(
        "--mlflow-experiment",
        default="codex-experiments",
        help="Experiment name (default: codex-experiments)",
    )


def mlflow_from_args(args: argparse.Namespace) -> MlflowConfig:
    """Build :class:`MlflowConfig` from parsed args."""
    return MlflowConfig(
        enable=bool(getattr(args, "mlflow_enable", False)),
        tracking_uri=str(getattr(args, "mlflow_tracking_uri", "./mlruns")),
        experiment=str(getattr(args, "mlflow_experiment", "codex-experiments")),
    )


__all__ = ["add_mlflow_flags", "mlflow_from_args", "MlflowConfig"]
# END: CODEX_MLFLOW_CLI
