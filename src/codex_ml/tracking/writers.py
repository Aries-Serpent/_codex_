from __future__ import annotations

import json
import logging
import sys
from collections import OrderedDict
from collections.abc import Mapping as MappingABC
from collections.abc import Sequence as SequenceABC
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, List, Optional, Tuple

from codex_ml.logging.ndjson_logger import NDJSONLogger, is_legacy_mode
from codex_ml.tracking.mlflow_guard import ensure_file_backend

DEFAULT_METRIC_SCHEMA_URI = "https://codexml.ai/schemas/run_metrics.schema.json"
SUMMARY_SCHEMA_URI = "https://codexml.ai/schemas/tracking_component.schema.json"

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


def _ordered_payload(
    record: MappingABC[str, Any], canonical_order: SequenceABC[str]
) -> "OrderedDict[str, Any]":
    ordered: "OrderedDict[str, Any]" = OrderedDict()
    for key in canonical_order:
        if key in record:
            ordered[key] = record[key]
    for key in sorted(k for k in record if k not in canonical_order):
        ordered[key] = record[key]
    return ordered


def _normalise_nested(value: Any) -> Any:
    if isinstance(value, MappingABC):
        return {str(k): _normalise_nested(v) for k, v in sorted(value.items())}
    if isinstance(value, SequenceABC) and not isinstance(value, (str, bytes, bytearray)):
        return [_normalise_nested(v) for v in value]
    return value


def _write_deterministic_json(path: Path, record: MappingABC[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(record, ensure_ascii=True, separators=(",", ":"))
    with path.open("a", encoding="utf-8") as fh:
        fh.write(payload + "\n")


def _collect_dependency_flags() -> dict[str, Any]:
    try:
        from codex_ml.monitoring import system_metrics  # type: ignore

        psutil_available = bool(getattr(system_metrics, "HAS_PSUTIL", False))
        nvml_available = bool(getattr(system_metrics, "HAS_NVML", False))
    except Exception:
        psutil_available = False
        nvml_available = False
    return {
        "psutil_available": psutil_available,
        "nvml_available": nvml_available,
    }


def _emit_summary(
    summary_path: Optional[Path],
    component: str,
    status: str,
    *,
    reason: Optional[str] = None,
    extra: Optional[MappingABC[str, Any]] = None,
) -> None:
    if summary_path is None:
        return
    payload = OrderedDict(
        (
            ("$schema", SUMMARY_SCHEMA_URI),
            ("schema_version", "v1"),
            ("timestamp", datetime.now(timezone.utc).isoformat()),
            ("component", component),
            ("status", status),
            ("reason", reason or ""),
        )
    )
    extras = dict(extra or {})
    if extras:
        payload["extra"] = _normalise_nested(extras)
    else:
        payload["extra"] = {}
    _write_deterministic_json(summary_path, payload)


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
        run_id: str | None = None,
        max_bytes: int | None = None,
        max_age_s: float | None = None,
        backup_count: int | None = None,
    ) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.schema_uri = schema_uri
        self.schema_version = schema_version
        self._legacy = is_legacy_mode()
        rotation: dict[str, Any] = {}
        if max_bytes is not None:
            rotation["max_bytes"] = max_bytes
        if max_age_s is not None:
            rotation["max_age_s"] = max_age_s
        if backup_count is not None:
            rotation["backup_count"] = backup_count
        self._logger = NDJSONLogger(
            self.path,
            run_id=run_id,
            ensure_ascii=True,
            **rotation,
        )

    def log(self, row: dict) -> None:
        record = dict(row)
        required = {"step", "split", "metric", "value", "dataset", "tags"}
        if not self._legacy:
            required |= {"timestamp", "run_id"}
        missing = required - record.keys()
        if missing:
            raise ValueError(f"missing keys: {missing}")
        if not self._legacy:
            iso = datetime.now(timezone.utc).isoformat()
            record.setdefault("timestamp", iso.replace("+00:00", "Z"))
            record.setdefault("run_id", getattr(self._logger, "run_id", None))
        record.setdefault("$schema", self.schema_uri)
        record.setdefault("schema_version", self.schema_version)
        tags = record.get("tags", {})
        record["tags"] = _normalise_nested(_jsonify(tags)) if tags is not None else {}
        dataset_value = record.get("dataset")
        record["dataset"] = None if dataset_value is None else str(dataset_value)
        ordered = _ordered_payload(
            _normalise_nested(record),
            (
                "$schema",
                "schema_version",
                "timestamp",
                "run_id",
                "step",
                "split",
                "metric",
                "value",
                "dataset",
                "tags",
            ),
        )
        self._logger.log(ordered)


class TensorBoardWriter(BaseWriter):
    def __init__(self, logdir: str | Path, *, summary_path: str | Path | None = None) -> None:
        self._disabled_reason: str | None = None
        self._summary_path = Path(summary_path) if summary_path is not None else None
        try:  # optional dependency
            from torch.utils.tensorboard import SummaryWriter  # type: ignore

            self._writer = SummaryWriter(log_dir=str(logdir))
            _emit_summary(
                self._summary_path,
                "tensorboard",
                "enabled",
                extra={"dependencies": _collect_dependency_flags()},
            )
        except Exception as exc:  # pragma: no cover - optional
            logger.debug("TensorBoard writer disabled", exc_info=exc)
            self._writer = None
            self._disabled_reason = _exc_reason("tensorboard", exc)
            _emit_summary(
                self._summary_path,
                "tensorboard",
                "disabled",
                reason=self._disabled_reason,
                extra={"dependencies": _collect_dependency_flags()},
            )

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
    def __init__(
        self,
        uri: str | None,
        exp_name: str,
        run_name: str,
        tags: dict,
        *,
        summary_path: str | Path | None = None,
    ) -> None:
        self._disabled_reason: str | None = None
        self._summary_path = Path(summary_path) if summary_path is not None else None
        target_uri = uri or ensure_file_backend()
        try:  # optional dependency
            import mlflow  # type: ignore

            ensure_file_backend()
            mlflow.set_tracking_uri(target_uri)
            mlflow.set_experiment(exp_name)
            self._mlflow = mlflow
            self._run = mlflow.start_run(run_name=run_name)
            if tags:
                mlflow.set_tags(tags)
            _emit_summary(
                self._summary_path,
                "mlflow",
                "enabled",
                extra={
                    "dependencies": _collect_dependency_flags(),
                    "tracking_uri": target_uri,
                },
            )
        except Exception as exc:  # pragma: no cover - optional
            self._mlflow = None
            self._run = None
            logger.debug("MLflow writer disabled", exc_info=exc)
            self._disabled_reason = _exc_reason("mlflow", exc)
            _emit_summary(
                self._summary_path,
                "mlflow",
                "disabled",
                reason=self._disabled_reason,
                extra={
                    "dependencies": _collect_dependency_flags(),
                    "tracking_uri": target_uri,
                },
            )

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
    def __init__(
        self,
        project: str,
        run_name: str,
        tags: dict,
        mode: str = "offline",
        *,
        summary_path: str | Path | None = None,
    ) -> None:
        self._disabled_reason: str | None = None
        self._summary_path = Path(summary_path) if summary_path is not None else None
        try:  # optional dependency
            import wandb  # type: ignore

            self._run = wandb.init(
                project=project,
                name=run_name,
                tags=list(tags.values()),
                mode=mode,
                reinit=True,
            )
            _emit_summary(
                self._summary_path,
                "wandb",
                "enabled",
                extra={
                    "dependencies": _collect_dependency_flags(),
                    "mode": mode,
                },
            )
        except Exception as exc:  # pragma: no cover - optional
            self._run = None
            logger.debug("Weights & Biases writer disabled", exc_info=exc)
            self._disabled_reason = _exc_reason("wandb", exc)
            _emit_summary(
                self._summary_path,
                "wandb",
                "disabled",
                reason=self._disabled_reason,
                extra={
                    "dependencies": _collect_dependency_flags(),
                    "mode": mode,
                },
            )

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
