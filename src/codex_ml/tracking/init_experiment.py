from __future__ import annotations

import os
import socket
import subprocess
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from .writers import (
    CompositeWriter,
    MLflowWriter,
    NdjsonWriter,
    TensorBoardWriter,
    WandbWriter,
)


@dataclass
class ExperimentContext:
    """Handle fan-out metric logging across multiple backends."""

    run_id: str
    experiment_name: str
    tags: Dict[str, Any]
    writer: CompositeWriter

    def log_metric(
        self,
        step: int,
        split: str,
        metric: str,
        value: float,
        dataset: Optional[str] = None,
        **extra_tags: Any,
    ) -> None:
        """Log a metric to all configured writers.

        Parameters
        ----------
        step: int
            Global step for the metric.
        split: str
            Data split (e.g. ``train`` or ``val``).
        metric: str
            Metric name (e.g. ``loss``).
        value: float
            Numeric value of the metric.
        dataset: Optional[str]
            Optional dataset identifier.
        extra_tags: Any
            Additional tags to merge with run tags.
        """

        row = {
            "ts": time.time(),
            "run_id": self.run_id,
            "step": int(step),
            "split": split,
            "metric": metric,
            "value": float(value),
            "dataset": dataset,
            "tags": {**self.tags, **extra_tags},
        }
        self.writer.log(row)

    def finalize(self) -> None:
        """Flush and close all underlying writers."""

        self.writer.close()


def _get_git_commit() -> Optional[str]:
    try:
        return (
            subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL
            )
            .decode()
            .strip()
        )
    except Exception:
        return None


def init_experiment(cfg: Any) -> ExperimentContext:
    """Initialise all enabled tracking backends.

    Parameters
    ----------
    cfg: Any
        Configuration object containing ``experiment`` and ``tracking``
        attributes. Only the fields accessed in this function are required.
    """

    run_id = str(getattr(cfg, "run_id", "") or uuid.uuid4())

    exp_name = None
    exp_obj = getattr(cfg, "experiment", None)
    if isinstance(exp_obj, str):
        exp_name = exp_obj
    elif exp_obj is not None:
        exp_name = getattr(exp_obj, "name", None)
    if not exp_name:
        exp_name = "codex"

    tags = {
        "model": getattr(cfg, "model", None),
        "dataset": getattr(cfg, "dataset", None),
        "seed": getattr(cfg, "seed", None),
        "precision": getattr(cfg, "precision", None),
        "lora": getattr(cfg, "lora", None),
        "git_commit": _get_git_commit(),
        "hostname": socket.gethostname(),
    }

    tracking_cfg = getattr(cfg, "tracking", cfg)
    output_dir = Path(getattr(tracking_cfg, "output_dir", "./runs"))
    output_dir.mkdir(parents=True, exist_ok=True)
    ndjson_path = Path(getattr(tracking_cfg, "ndjson_path", output_dir / "metrics.ndjson"))

    writers = [NdjsonWriter(ndjson_path)]

    if getattr(tracking_cfg, "tensorboard", False):
        writers.append(TensorBoardWriter(output_dir / "tb"))

    if getattr(tracking_cfg, "mlflow", False):
        uri = getattr(tracking_cfg, "mlflow_uri", "file:./mlruns")
        writers.append(MLflowWriter(uri, exp_name, run_id, tags))

    if getattr(tracking_cfg, "wandb", False):
        os.environ.setdefault("WANDB_MODE", "offline")
        project = getattr(tracking_cfg, "wandb_project", exp_name)
        writers.append(WandbWriter(project, run_id, tags, mode=os.environ["WANDB_MODE"]))

    ctx = ExperimentContext(
        run_id=run_id,
        experiment_name=exp_name,
        tags=tags,
        writer=CompositeWriter(writers),
    )
    return ctx


__all__ = ["ExperimentContext", "init_experiment"]
