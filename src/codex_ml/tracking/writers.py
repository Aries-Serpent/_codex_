from __future__ import annotations

import logging
import os
import sys
from collections import OrderedDict
from collections.abc import Mapping as MappingABC
from collections.abc import Sequence as SequenceABC
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, List, Optional, Tuple
from uuid import uuid4

from codex_ml.logging.ndjson_logger import NDJSONLogger, is_legacy_mode
from codex_ml.tracking.mlflow_guard import bootstrap_offline_tracking, last_decision

DEFAULT_METRIC_SCHEMA_URI = "https://codexml.ai/schemas/run_metrics.schema.json"
SUMMARY_SCHEMA_URI = "https://codexml.ai/schemas/tracking_component.schema.json"
METRICS_MANIFEST_SCHEMA_URI = "https://codexml.ai/schemas/run_metrics_manifest.schema.json"

_SUMMARY_ROTATION_ENV = {
    "CODEX_TRACKING_NDJSON_MAX_BYTES": ("max_bytes", int),
    "CODEX_TRACKING_NDJSON_MAX_AGE_S": ("max_age_s", float),
    "CODEX_TRACKING_NDJSON_BACKUP_COUNT": ("backup_count", int),
}

_SUMMARY_LOGGERS: dict[Path, NDJSONLogger] = {}

_SUMMARY_EXTRA_ORDER = (
    "dependencies",
    "requested_uri",
    "effective_uri",
    "tracking_uri",
    "fallback_reason",
    "allow_remote_flag",
    "allow_remote_env",
    "allow_remote",
    "system_metrics_enabled",
)

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


def _summary_rotation_kwargs() -> dict[str, Any]:
    options: dict[str, Any] = {}
    for env, (key, caster) in _SUMMARY_ROTATION_ENV.items():
        raw = os.getenv(env)
        if raw is None:
            continue
        text = str(raw).strip()
        if not text:
            if key in {"max_bytes", "max_age_s"}:
                options[key] = None
            elif key == "backup_count":
                options[key] = 0
            continue
        try:
            options[key] = caster(text)
        except (TypeError, ValueError):  # pragma: no cover - invalid config
            continue
    return options


def _summary_logger(path: Path) -> NDJSONLogger:
    logger = _SUMMARY_LOGGERS.get(path)
    if logger is None or getattr(logger, "_closed", False):
        rotation = _summary_rotation_kwargs()
        logger = NDJSONLogger(path, ensure_ascii=True, **rotation)
        _SUMMARY_LOGGERS[path] = logger
    return logger


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
        ordered_extra = _ordered_payload(
            _normalise_nested(extras),
            _SUMMARY_EXTRA_ORDER,
        )
        payload["extra"] = ordered_extra
    else:
        payload["extra"] = {}
    logger = _summary_logger(summary_path)
    logger.log(payload)


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
        manifest_path: str | Path | None = None,
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
        if self._legacy:
            self._manifest_logger: NDJSONLogger | None = None
        else:
            manifest_target = (
                Path(manifest_path)
                if manifest_path is not None
                else self.path.with_name("metrics_manifest.ndjson")
            )
            manifest_target.parent.mkdir(parents=True, exist_ok=True)
            self._manifest_logger = NDJSONLogger(
                manifest_target,
                run_id=run_id or getattr(self._logger, "run_id", None),
                ensure_ascii=True,
                **rotation,
            )

    def log(self, row: dict) -> None:
        record = dict(row)
        if not self._legacy:
            iso = datetime.now(timezone.utc).isoformat()
            record.setdefault("timestamp", iso.replace("+00:00", "Z"))
            run_identifier = getattr(self._logger, "run_id", None)
            if run_identifier is not None:
                record.setdefault("run_id", run_identifier)
        required = {"step", "split", "metric", "value", "dataset", "tags"}
        if not self._legacy:
            required |= {"timestamp", "run_id"}
        missing = {key for key in required if key not in record}
        if missing:
            raise ValueError(f"missing keys: {missing}")
        record.setdefault("$schema", self.schema_uri)
        record.setdefault("schema_version", self.schema_version)
        tags = record.get("tags", {})
        record["tags"] = _normalise_nested(_jsonify(tags)) if tags is not None else {}
        dataset_value = record.get("dataset")
        record["dataset"] = None if dataset_value is None else str(dataset_value)
        manifest_entry = None
        if not self._legacy:
            record, manifest_entry = self._prepare_manifest(record)
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
        if manifest_entry is not None and self._manifest_logger is not None:
            manifest_ordered = _ordered_payload(
                _normalise_nested(manifest_entry),
                (
                    "$schema",
                    "schema_version",
                    "timestamp",
                    "run_id",
                    "manifest_id",
                    "metric",
                    "step",
                    "split",
                    "dataset",
                    "descriptor",
                ),
            )
            self._manifest_logger.log(manifest_ordered)

    def _prepare_manifest(
        self, record: dict[str, Any]
    ) -> Tuple[dict[str, Any], Optional[dict[str, Any]]]:
        value = record.get("value")
        scalar_value = self._coerce_scalar(value)
        tags_dict = dict(record.get("tags") or {})
        manifest_entry: Optional[dict[str, Any]] = None
        if scalar_value is None and value not in (None,) and self._manifest_logger is not None:
            manifest_id = f"manifest-{uuid4().hex}"
            tags_dict.setdefault("manifest_id", manifest_id)
            descriptor = self._build_descriptor(value)
            manifest_entry = {
                "$schema": METRICS_MANIFEST_SCHEMA_URI,
                "schema_version": record.get("schema_version", self.schema_version),
                "timestamp": record.get("timestamp"),
                "run_id": record.get("run_id"),
                "manifest_id": manifest_id,
                "metric": record.get("metric"),
                "step": record.get("step"),
                "split": record.get("split"),
                "dataset": record.get("dataset"),
                "descriptor": descriptor,
            }
            record["value"] = None
        else:
            record["value"] = scalar_value if scalar_value is not None else value
        record["tags"] = _normalise_nested(tags_dict)
        return record, manifest_entry

    @staticmethod
    def _coerce_scalar(value: Any) -> Optional[float | int]:
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, (int, float)):
            return float(value)
        return None

    def _build_descriptor(self, value: Any) -> dict[str, Any]:
        descriptor: dict[str, Any] = {
            "type": type(value).__name__ if value is not None else "unknown",
            "version": "v1",
        }
        if isinstance(value, MappingABC):
            payload = {str(k): _jsonify(v) for k, v in value.items()}
            if "path" in payload:
                descriptor["path"] = payload["path"]
            if "shape" in payload:
                descriptor["shape"] = payload["shape"]
            descriptor["payload"] = payload
        elif isinstance(value, SequenceABC) and not isinstance(value, (str, bytes, bytearray)):
            descriptor["shape"] = [len(value)] if hasattr(value, "__len__") else []
            descriptor["payload"] = [_jsonify(v) for v in value]
        else:
            descriptor["payload"] = _jsonify(value)
        return descriptor

    def close(self) -> None:
        if getattr(self, "_manifest_logger", None) is not None:
            try:
                self._manifest_logger.close()
            except Exception:  # pragma: no cover
                pass
        try:
            self._logger.close()
        except Exception:  # pragma: no cover
            pass


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
        target_uri = bootstrap_offline_tracking(requested_uri=uri)
        decision = last_decision()
        provided_uri = uri or ""
        fallback_reason = ""
        allow_remote_flag = ""
        allow_remote_env = "MLFLOW_ALLOW_REMOTE"
        allow_remote = False
        system_metrics_enabled = False
        if decision is not None:
            provided_uri = decision.requested_uri or provided_uri
            target_uri = decision.effective_uri or target_uri
            fallback_reason = decision.fallback_reason or ""
            allow_remote_flag = decision.allow_remote_flag
            allow_remote_env = decision.allow_remote_env
            allow_remote = decision.allow_remote
            system_metrics_enabled = decision.system_metrics_enabled
        if provided_uri and provided_uri != target_uri and not allow_remote:
            logger.warning(
                "Non-file MLflow URI '%s' provided; falling back to %s", provided_uri, target_uri
            )
        try:  # optional dependency
            import mlflow  # type: ignore

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
                    "requested_uri": provided_uri,
                    "effective_uri": target_uri,
                    "fallback_reason": fallback_reason,
                    "allow_remote_flag": allow_remote_flag,
                    "allow_remote_env": allow_remote_env,
                    "allow_remote": allow_remote,
                    "system_metrics_enabled": system_metrics_enabled,
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
                    "requested_uri": provided_uri,
                    "effective_uri": target_uri,
                    "fallback_reason": fallback_reason,
                    "allow_remote_flag": allow_remote_flag,
                    "allow_remote_env": allow_remote_env,
                    "allow_remote": allow_remote,
                    "system_metrics_enabled": system_metrics_enabled,
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
