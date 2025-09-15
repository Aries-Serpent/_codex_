from __future__ import annotations

import os
import socket
import subprocess
import uuid
from collections.abc import Mapping as MappingABC
from collections.abc import Sequence as SequenceABC
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from codex_ml.logging.run_logger import RunLogger

from .writers import (
    BaseWriter,
    CompositeWriter,
    MLflowWriter,
    TensorBoardWriter,
    WandbWriter,
)


@dataclass
class ExperimentContext:
    """Handle fan-out metric logging across multiple backends."""

    run_id: str
    experiment_name: str
    tags: Dict[str, Any]
    run_logger: RunLogger
    writer: CompositeWriter

    @property
    def params_path(self) -> Path:
        return self.run_logger.params_path

    @property
    def metrics_path(self) -> Path:
        return self.run_logger.metrics_path

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

        combined_tags = {**self.tags, **extra_tags}
        record = self.run_logger.log_metric(
            step=int(step),
            split=split,
            metric=metric,
            value=value,
            dataset=dataset,
            tags=combined_tags,
        )
        self.writer.log(record)

    def finalize(self) -> None:
        """Flush and close all underlying writers."""

        self.run_logger.close()
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
    params_path = getattr(tracking_cfg, "params_path", None)
    metrics_path = getattr(tracking_cfg, "ndjson_path", None)
    run_logger = RunLogger(
        output_dir,
        run_id,
        params_path=params_path,
        metrics_path=metrics_path,
    )

    cli_args = getattr(cfg, "cli_args", [])
    if isinstance(cli_args, SequenceABC) and not isinstance(cli_args, (str, bytes, bytearray)):
        argv = [str(arg) for arg in cli_args]
    elif cli_args:
        argv = [str(cli_args)]
    else:
        argv = []
    cli_options = getattr(cfg, "cli_options", None)
    if isinstance(cli_options, MappingABC):
        cli_payload: Any = {"argv": argv, "options": dict(cli_options)}
    elif cli_options is not None:
        cli_payload = {"argv": argv, "options": {"raw": cli_options}}
    else:
        cli_payload = argv

    config_snapshot: Dict[str, Any] = {}
    for attr in ("config_snapshot", "config_dict", "config"):
        maybe = getattr(cfg, attr, None)
        if isinstance(maybe, MappingABC):
            config_snapshot = {str(k): maybe[k] for k in maybe}
            break
        getter = getattr(maybe, "to_dict", None)
        if callable(getter):
            try:
                converted = getter()
            except Exception:
                continue
            if isinstance(converted, MappingABC):
                config_snapshot = {str(k): converted[k] for k in converted}
                break

    derived: Dict[str, Any] = {}
    provided = getattr(cfg, "derived_params", None)
    if isinstance(provided, MappingABC):
        derived.update({str(k): provided[k] for k in provided})
    seed_val = getattr(cfg, "seed", None)
    if seed_val is not None and "seed" not in derived:
        derived["seed"] = seed_val
    batch_size = getattr(cfg, "batch_size", None)
    grad_accum = getattr(cfg, "gradient_accumulation", None)
    if isinstance(batch_size, (int, float)) and isinstance(grad_accum, (int, float)):
        derived.setdefault("effective_batch_size", int(batch_size) * int(grad_accum))

    metadata = {
        "experiment": exp_name,
        "tracking": {"output_dir": str(output_dir)},
    }
    run_logger.log_params(
        cli=cli_payload, config=config_snapshot, derived=derived, metadata=metadata
    )

    writers: list[BaseWriter] = []
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
        run_logger=run_logger,
        writer=CompositeWriter(writers),
    )
    return ctx


__all__ = ["ExperimentContext", "init_experiment"]
