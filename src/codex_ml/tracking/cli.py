# BEGIN: CODEX_MLFLOW_CLI
from __future__ import annotations

import argparse

from .mlflow_utils import MlflowConfig


def add_mlflow_flags(parser: argparse.ArgumentParser) -> None:
    g = parser.add_argument_group("MLflow")
    g.add_argument(
        "--mlflow-enable",
        action="store_true",
        default=False,
        help="Enable MLflow logging (optional dependency).",
    )
    g.add_argument(
        "--mlflow-tracking-uri",
        default="./mlruns",
        help="MLflow tracking URI or path (default: ./mlruns).",
    )
    g.add_argument(
        "--mlflow-experiment",
        default="codex-experiments",
        help="MLflow experiment name.",
    )


def mlflow_from_args(args) -> MlflowConfig:
    return MlflowConfig(
        enable=bool(getattr(args, "mlflow_enable", False)),
        tracking_uri=str(getattr(args, "mlflow_tracking_uri", "./mlruns")),
        experiment=str(getattr(args, "mlflow_experiment", "codex-experiments")),
    )


# END: CODEX_MLFLOW_CLI
