from __future__ import annotations

import json
import os
import socket
import subprocess
import uuid
from collections.abc import Mapping as MappingABC
from collections.abc import Sequence as SequenceABC
from dataclasses import asdict, dataclass, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Mapping, Optional

from codex_ml.logging.ndjson_logger import NDJSONLogger, timestamped_record
from codex_ml.tracking.mlflow_guard import bootstrap_offline_tracking

if TYPE_CHECKING:  # pragma: no cover
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
    """Container for the active experiment's loggers and metadata.

    The context exposes typed helpers for logging metrics, parameters,
    configuration snapshots and provenance to every configured backend. All
    writers are closed when :meth:`finalize` is called.
    """

    run_id: str
    experiment_name: str
    tags: Dict[str, Any]
    run_logger: "RunLogger"
    writer: CompositeWriter
    run_dir: Path
    params_logger: NDJSONLogger
    config_logger: NDJSONLogger
    provenance_logger: NDJSONLogger
    config_path: Path

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
    """Initialise the standard Codex ML tracking stack.

    Parameters
    ----------
    cfg: Any
        Configuration object containing ``experiment`` and ``tracking``
        attributes. Only the fields accessed in this function are required.

    Returns
    -------
    ExperimentContext
        Object bundling metric loggers, run metadata and helper methods that
        can be used to record params, configs and provenance events.
    """

    bootstrap_offline_tracking()

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

    configured_run_dir = getattr(tracking_cfg, "run_dir", None)
    if configured_run_dir:
        run_dir = Path(configured_run_dir)
        if not run_dir.is_absolute():
            run_dir = output_dir / run_dir
    else:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        base_name = f"{timestamp}-{_slugify(exp_name)}"
        candidate = output_dir / base_name
        if candidate.exists():
            short_id = run_id.split("-")[0]
            candidate = output_dir / f"{base_name}-{short_id}"
            suffix = 1
            while candidate.exists():
                candidate = output_dir / f"{base_name}-{short_id}-{suffix}"
                suffix += 1
        run_dir = candidate

    from codex_ml.logging.run_logger import RunLogger

    run_logger = RunLogger(
        run_dir,
        run_id,
        params_path=params_path,
        metrics_path=metrics_path,
    )
    run_dir = run_logger.run_dir

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
        "tracking": {"output_dir": str(output_dir), "run_dir": str(run_dir)},
    }
    run_logger.log_params(
        cli=cli_payload, config=config_snapshot, derived=derived, metadata=metadata
    )

    writers: list[BaseWriter] = []
    summary_path = run_dir / "tracking_summary.ndjson"

    if getattr(tracking_cfg, "tensorboard", False):
        writers.append(TensorBoardWriter(run_dir / "tb", summary_path=summary_path))

    mlflow_enabled = _bool_env("CODEX_MLFLOW_ENABLE", getattr(tracking_cfg, "mlflow", False))
    if mlflow_enabled:
        uri = os.getenv("CODEX_MLFLOW_URI", getattr(tracking_cfg, "mlflow_uri", "file:./mlruns"))
        writers.append(MLflowWriter(uri, exp_name, run_id, tags, summary_path=summary_path))

    wandb_enabled = _bool_env("CODEX_WANDB_ENABLE", getattr(tracking_cfg, "wandb", False))
    if wandb_enabled:
        os.environ.setdefault("WANDB_MODE", "offline")
        project = os.getenv("CODEX_WANDB_PROJECT", getattr(tracking_cfg, "wandb_project", exp_name))
        writers.append(
            WandbWriter(
                project,
                run_id,
                tags,
                mode=os.environ["WANDB_MODE"],
                summary_path=summary_path,
            )
        )

    # Record ad-hoc context parameters in a separate file so ``params.ndjson``
    # remains compliant with the ``run_params`` schema enforced by ``RunLogger``.
    params_logger = NDJSONLogger(run_dir / "context_params.ndjson", run_id=run_id)
    config_logger = NDJSONLogger(run_dir / "config.ndjson", run_id=run_id)
    provenance_logger = NDJSONLogger(run_dir / "provenance.ndjson", run_id=run_id)

    ctx = ExperimentContext(
        run_id=run_id,
        experiment_name=exp_name,
        tags=tags,
        run_logger=run_logger,
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
