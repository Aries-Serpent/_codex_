from __future__ import annotations

import json
import logging
import sys
from collections.abc import Mapping as MappingABC
from collections.abc import Sequence as SequenceABC
from pathlib import Path
from typing import Any, Iterable, List, Optional, Tuple

from codex_ml.logging.ndjson_logger import NDJSONLogger

DEFAULT_METRIC_SCHEMA_URI = "https://codexml.ai/schemas/run_metrics.schema.json"

logger = logging.getLogger(__name__)


def _jsonify(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, MappingABC):
        return {str(k): _jsonify(v) for k, v in value.items()}
    if isinstance(value, SequenceABC) and not isinstance(value, (str, bytes, bytearray)):
        return [_jsonify(v) for v in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _exc_reason(component: str, exc: Exception) -> str:
    detail = exc.__class__.__name__
    message = str(exc).strip().splitlines()[0]
    if message:
        message = message.replace(":", " ").strip()
        detail = f"{detail}({message})"
    return f"{component}:{detail}"


def _parse_reason(reason: str) -> Tuple[str, str]:
    head, _, tail = reason.partition(":")
    return head or "unknown", tail or ""


class BaseWriter:
    """Simple interface for metric writers."""

    def log(self, row: dict) -> None:  # pragma: no cover - interface
        raise NotImplementedError

    def close(self) -> None:  # pragma: no cover - interface
        pass


class NdjsonWriter(BaseWriter):
    """Append metrics to a local NDJSON file enforcing a standard schema."""

    def __init__(
        self,
        path: str | Path,
        *,
        schema_uri: str = DEFAULT_METRIC_SCHEMA_URI,
        schema_version: str = "v1",
    ) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.schema_uri = schema_uri
        self.schema_version = schema_version
        self._logger = NDJSONLogger(self.path)

    def log(self, row: dict) -> None:
        required = {"timestamp", "run_id", "step", "split", "metric", "value", "dataset", "tags"}
        missing = required - row.keys()
        if missing:
            raise ValueError(f"missing keys: {missing}")
        record = dict(row)
        record.setdefault("$schema", self.schema_uri)
        record.setdefault("schema_version", self.schema_version)
        record["tags"] = _jsonify(record.get("tags", {}))
        record["dataset"] = (
            record.get("dataset") if record.get("dataset") is None else str(record.get("dataset"))
        )
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(_jsonify(record), ensure_ascii=True) + "\n")


class TensorBoardWriter(BaseWriter):
    def __init__(self, logdir: str | Path) -> None:
        self._disabled_reason: str | None = None
        try:  # optional dependency
            from torch.utils.tensorboard import SummaryWriter  # type: ignore

            self._writer = SummaryWriter(log_dir=str(logdir))
        except Exception as exc:  # pragma: no cover - optional
            logger.debug("TensorBoard writer disabled", exc_info=exc)
            self._writer = None
            self._disabled_reason = _exc_reason("tensorboard", exc)

    def log(self, row: dict) -> None:
        if self._writer is None:
            return
        val = row.get("value")
        if isinstance(val, (int, float)):
            tag = f"{row.get('split')}/{row.get('metric')}"
            self._writer.add_scalar(tag, val, row.get("step"))

    def close(self) -> None:
        if self._writer is not None:
            try:
                self._writer.flush()
                self._writer.close()
            except Exception:  # pragma: no cover
                pass

    def status(self) -> Optional[str]:
        return self._disabled_reason


class MLflowWriter(BaseWriter):
    def __init__(self, uri: str, exp_name: str, run_name: str, tags: dict) -> None:
        self._disabled_reason: str | None = None
        try:  # optional dependency
            import mlflow  # type: ignore

            mlflow.set_tracking_uri(uri)
            mlflow.set_experiment(exp_name)
            self._mlflow = mlflow
            self._run = mlflow.start_run(run_name=run_name)
            if tags:
                mlflow.set_tags(tags)
        except Exception as exc:  # pragma: no cover - optional
            self._mlflow = None
            self._run = None
            logger.debug("MLflow writer disabled", exc_info=exc)
            self._disabled_reason = _exc_reason("mlflow", exc)

    def log(self, row: dict) -> None:
        if self._mlflow is None:
            return
        val = row.get("value")
        if isinstance(val, (int, float)):
            self._mlflow.log_metric(row["metric"], val, step=int(row["step"]))

    def close(self) -> None:
        if self._mlflow is not None:
            try:
                self._mlflow.end_run()
            except Exception:  # pragma: no cover
                pass

    def status(self) -> Optional[str]:
        return self._disabled_reason


class WandbWriter(BaseWriter):
    def __init__(self, project: str, run_name: str, tags: dict, mode: str = "offline") -> None:
        self._disabled_reason: str | None = None
        try:  # optional dependency
            import wandb  # type: ignore

            self._run = wandb.init(
                project=project,
                name=run_name,
                tags=list(tags.values()),
                mode=mode,
                reinit=True,
            )
        except Exception as exc:  # pragma: no cover - optional
            self._run = None
            logger.debug("Weights & Biases writer disabled", exc_info=exc)
            self._disabled_reason = _exc_reason("wandb", exc)

    def log(self, row: dict) -> None:
        if self._run is None:
            return
        val = row.get("value")
        if isinstance(val, (int, float)):
            tag = f"{row.get('split')}/{row.get('metric')}"
            self._run.log({tag: val, "step": int(row["step"])})

    def close(self) -> None:
        if self._run is not None:
            try:
                self._run.finish()
            except Exception:  # pragma: no cover
                pass

    def status(self) -> Optional[str]:
        return self._disabled_reason


class CompositeWriter(BaseWriter):
    """Dispatch to multiple writers, swallowing individual errors."""

    def __init__(self, writers: Iterable[BaseWriter]) -> None:
        self._writers: List[BaseWriter] = list(writers)
        components: list[Tuple[str, str]] = []
        for writer in self._writers:
            reason: Optional[str]
            status_getter = getattr(writer, "status", None)
            if callable(status_getter):
                try:
                    reason = status_getter()
                except Exception:  # pragma: no cover - defensive
                    reason = getattr(writer, "_disabled_reason", None)
            else:
                reason = getattr(writer, "_disabled_reason", None)
            if reason:
                components.append(_parse_reason(reason))
        self._disabled_components: Tuple[Tuple[str, str], ...] = tuple(components)
        if self._disabled_components:
            summary = "; ".join(
                f"{name} ({detail})" if detail else name
                for name, detail in self._disabled_components
            )
            print(f"[tracking] degraded writers: {summary}", file=sys.stderr)

    def log(self, row: dict) -> None:
        for w in self._writers:
            try:
                w.log(row)
            except Exception as exc:  # pragma: no cover - robustness
                logger.debug("Writer log error", exc_info=exc)

    def close(self) -> None:
        for w in self._writers:
            try:
                w.close()
            except Exception as exc:  # pragma: no cover - robustness
                logger.debug("Writer close error", exc_info=exc)

    @property
    def disabled_components(self) -> Tuple[Tuple[str, str], ...]:
        return self._disabled_components


__all__ = [
    "BaseWriter",
    "NdjsonWriter",
    "TensorBoardWriter",
    "MLflowWriter",
    "WandbWriter",
    "CompositeWriter",
]
