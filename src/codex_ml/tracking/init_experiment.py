from __future__ import annotations

import json
import os
import socket
import subprocess
import uuid
from dataclasses import asdict, dataclass, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

from codex_ml.logging.ndjson_logger import NDJSONLogger, timestamped_record

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
    run_dir: Path
    params_logger: NDJSONLogger
    config_logger: NDJSONLogger
    provenance_logger: NDJSONLogger
    config_path: Path

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
            "run_id": self.run_id,
            "step": int(step),
            "split": split,
            "metric": metric,
            "value": float(value),
            "dataset": dataset,
            "tags": {**self.tags, **extra_tags},
        }
        row = timestamped_record(**row)
        self.writer.log(row)

    def finalize(self) -> None:
        """Flush and close all underlying writers."""

        self.writer.close()

    def log_params(self, params: Mapping[str, Any]) -> None:
        records = []
        for key, value in params.items():
            records.append(
                timestamped_record(
                    type="param",
                    run_id=self.run_id,
                    name=str(key),
                    value=_to_jsonable(value),
                )
            )
        if records:
            self.params_logger.log_many(records)

    def log_config(self, config: Mapping[str, Any]) -> None:
        payload = _to_jsonable(config)
        record = timestamped_record(type="config", run_id=self.run_id, payload=payload)
        self.config_logger.log(record)
        self.config_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    def log_provenance(self, data: Mapping[str, Any]) -> None:
        record = timestamped_record(
            type="provenance", run_id=self.run_id, payload=_to_jsonable(data)
        )
        self.provenance_logger.log(record)


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


def _slugify(value: str) -> str:
    safe = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "-" for ch in value)
    return safe.strip("-") or "run"


def _bool_env(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _to_jsonable(obj: Any) -> Any:
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, Mapping):
        return {str(k): _to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [_to_jsonable(v) for v in obj]
    if is_dataclass(obj):
        return _to_jsonable(asdict(obj))
    if hasattr(obj, "__dict__"):
        return _to_jsonable({k: v for k, v in vars(obj).items() if not k.startswith("_")})
    try:
        json.dumps(obj)
        return obj
    except TypeError:  # pragma: no cover - best effort
        return repr(obj)


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
    slug = _slugify(str(getattr(tracking_cfg, "run_name", run_id[:8])))
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    run_dir = output_dir / f"{timestamp}-{slug}"
    run_dir.mkdir(parents=True, exist_ok=True)

    ndjson_path = run_dir / "metrics.ndjson"

    writers = [NdjsonWriter(ndjson_path)]

    if getattr(tracking_cfg, "tensorboard", False):
        writers.append(TensorBoardWriter(run_dir / "tb"))

    mlflow_enabled = _bool_env("CODEX_MLFLOW_ENABLE", getattr(tracking_cfg, "mlflow", False))
    if mlflow_enabled:
        uri = os.getenv("CODEX_MLFLOW_URI", getattr(tracking_cfg, "mlflow_uri", "file:./mlruns"))
        writers.append(MLflowWriter(uri, exp_name, run_id, tags))

    wandb_enabled = _bool_env("CODEX_WANDB_ENABLE", getattr(tracking_cfg, "wandb", False))
    if wandb_enabled:
        os.environ.setdefault("WANDB_MODE", "offline")
        project = os.getenv("CODEX_WANDB_PROJECT", getattr(tracking_cfg, "wandb_project", exp_name))
        writers.append(WandbWriter(project, run_id, tags, mode=os.environ["WANDB_MODE"]))

    params_logger = NDJSONLogger(run_dir / "params.ndjson")
    config_logger = NDJSONLogger(run_dir / "config.ndjson")
    provenance_logger = NDJSONLogger(run_dir / "provenance.ndjson")

    ctx = ExperimentContext(
        run_id=run_id,
        experiment_name=exp_name,
        tags=tags,
        writer=CompositeWriter(writers),
        run_dir=run_dir,
        params_logger=params_logger,
        config_logger=config_logger,
        provenance_logger=provenance_logger,
        config_path=run_dir / "config.json",
    )
    ctx.log_params(
        {
            "run_id": run_id,
            "experiment": exp_name,
            **{k: v for k, v in tags.items() if v is not None},
        }
    )
    ctx.log_provenance(
        {
            "git_commit": tags.get("git_commit"),
            "hostname": tags.get("hostname"),
            "cwd": os.getcwd(),
        }
    )
    try:
        from omegaconf import DictConfig, OmegaConf

        if isinstance(cfg, DictConfig):
            resolved = OmegaConf.to_container(cfg, resolve=True)  # type: ignore[arg-type]
        else:
            resolved = cfg
    except Exception:  # pragma: no cover - OmegaConf missing
        resolved = cfg
    serialised = _to_jsonable(resolved)
    if isinstance(serialised, Mapping):
        ctx.log_config(serialised)
    else:
        ctx.log_config({"config": serialised})

    return ctx


__all__ = ["ExperimentContext", "init_experiment"]
