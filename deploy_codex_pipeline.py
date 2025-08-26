"""Minimal Codex deployment helpers for smoke tests.
This module provides stub logging utilities to exercise offline logging paths."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any, Dict, Optional


def _codex_patch_argparse(ap: argparse.ArgumentParser) -> None:
    """Inject logging-related flags into ``argparse`` parser."""
    ap.add_argument("--enable-wandb", action="store_true", help="enable W&B logging")
    ap.add_argument(
        "--mlflow-enable", action="store_true", help="enable MLflow logging"
    )
    ap.add_argument(
        "--mlflow-experiment", type=str, default=None, help="MLflow experiment name"
    )


def _codex_logging_bootstrap(
    ns: argparse.Namespace, run_dir: Path, params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Best-effort bootstrap for logging backends.

    Returns a dictionary of active logging handles. Missing dependencies are tolerated.
    """
    params = params or {}
    handles: Dict[str, Any] = {}

    # TensorBoard
    try:
        from torch.utils.tensorboard import SummaryWriter  # type: ignore

        tb_dir = run_dir / "tb"
        tb_dir.mkdir(parents=True, exist_ok=True)
        handles["tb"] = SummaryWriter(log_dir=str(tb_dir))
    except Exception:
        handles["tb"] = None

    # W&B (offline)
    if getattr(ns, "enable_wandb", False):
        try:
            import wandb  # type: ignore

            wandb.init(
                project=params.get("wandb_project", "codex-smoke"), dir=str(run_dir)
            )
            handles["wandb"] = wandb
        except Exception:
            handles["wandb"] = None
    else:
        handles["wandb"] = None

    # MLflow
    if getattr(ns, "mlflow_enable", False):
        try:
            import mlflow  # type: ignore

            tracking_uri = "file://" + str(run_dir / "mlruns")
            mlflow.set_tracking_uri(tracking_uri)
            mlflow.set_experiment(ns.mlflow_experiment)
            mlflow.start_run(run_name="codex-smoke")
            handles["mlflow"] = mlflow
        except Exception:
            handles["mlflow"] = None
    else:
        handles["mlflow"] = None

    return handles


def _codex_log_all(
    handles: Dict[str, Any], step: int, metrics: Dict[str, float]
) -> None:
    """Log metrics to all active backends."""
    tb = handles.get("tb")
    if tb is not None:
        for k, v in metrics.items():
            try:
                tb.add_scalar(k, v, step)
            except Exception:
                pass
        try:
            tb.flush()
        except Exception:
            pass

    wb = handles.get("wandb")
    if wb is not None:
        try:
            wb.log(metrics, step=step)
        except Exception:
            pass

    mf = handles.get("mlflow")
    if mf is not None:
        try:
            mf.log_metrics(metrics, step=step)
        except Exception:
            pass


__all__ = [
    "_codex_patch_argparse",
    "_codex_logging_bootstrap",
    "_codex_log_all",
]
