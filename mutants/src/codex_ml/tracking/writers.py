"""
Writers Module

This module provides functionality for writers.

Usage:
    from tracking.writers import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import contextlib
import json
import logging
import os
import threading
import time
from abc import ABC, abstractmethod
from collections import OrderedDict
from collections.abc import Iterable
from collections.abc import Mapping as MappingABC
from collections.abc import Sequence as SequenceABC
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse
from uuid import uuid4

from codex.logging.structured_logger import logger
from codex_ml.logging.ndjson_logger import (
    DEFAULT_BACKUP_COUNT,
    DEFAULT_MAX_AGE_S,
    DEFAULT_MAX_BYTES,
    NDJSONLogger,
    is_legacy_mode,
)
from codex_ml.logging.permissions import get_log_file_mode
from codex_ml.tracking.mlflow_guard import bootstrap_offline_tracking_decision
from codex_ml.utils.optional_dependencies import format_optional_dependency_error

DEFAULT_METRIC_SCHEMA_URI = "https://codexml.ai/schemas/run_metrics.schema.json"
SUMMARY_SCHEMA_URI = "https://codexml.ai/schemas/tracking_component.schema.json"
METRICS_MANIFEST_SCHEMA_URI = "https://codexml.ai/schemas/run_metrics_manifest.schema.json"

logger = logging.getLogger(__name__)

_ROTATION_ENV = {
    "CODEX_TRACKING_NDJSON_MAX_BYTES": ("max_bytes", int),
    "CODEX_TRACKING_NDJSON_MAX_AGE_S": ("max_age_s", float),
    "CODEX_TRACKING_NDJSON_BACKUP_COUNT": ("backup_count", int),
}

_SUMMARY_EXTRA_ORDER = (
    "dependencies",
    "tracking_uri",
    "requested_uri",
    "effective_uri",
    "fallback_reason",
    "allow_remote_flag",
    "allow_remote",
    "system_metrics_enabled",
)

_SUMMARY_ROTATORS: dict[Path, _SummaryRotator] = {}
_SUMMARY_ROTATOR_LOCK = threading.Lock()


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


def _parse_reason(reason: str) -> tuple[str, str]:
    head, _, tail = reason.partition(":")
    return head or "unknown", tail or ""


def _ordered_payload(
    record: MappingABC[str, Any], canonical_order: SequenceABC[str]
) -> OrderedDict[str, Any]:
    ordered: OrderedDict[str, Any] = OrderedDict()
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


def _normalise_summary_extra(extra: MappingABC[str, Any]) -> OrderedDict[str, Any]:
    ordered: OrderedDict[str, Any] = OrderedDict()
    for key in _SUMMARY_EXTRA_ORDER:
        if key in extra:
            ordered[key] = _normalise_nested(extra[key])
    for key in sorted(k for k in extra if k not in _SUMMARY_EXTRA_ORDER):
        ordered[key] = _normalise_nested(extra[key])
    return ordered


def _summary_rotation_options() -> dict[str, Any]:
    options: dict[str, Any] = {
        "max_bytes": DEFAULT_MAX_BYTES,
        "max_age_s": DEFAULT_MAX_AGE_S,
        "backup_count": DEFAULT_BACKUP_COUNT,
    }
    for env, (key, caster) in _ROTATION_ENV.items():
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
        except (TypeError, ValueError):  # pragma: no cover - defensive
            continue
    return options


class _SummaryRotator:
    def __init__(
        self,
        path: Path,
        *,
        max_bytes: int | None,
        max_age_s: float | int | None,
        backup_count: int,
    ) -> None:
        self.path = path
        self.max_bytes = self._coerce_threshold(max_bytes)
        self.max_age_s = self._coerce_age(max_age_s)
        self.backup_count = max(0, int(backup_count))
        self._lock = threading.Lock()
        self._rollover_ts = time.time()

    def append(self, payload: str) -> None:
        data = (payload + "\n").encode("utf-8")
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._rotate_if_needed(len(data))
            # Security: See permissions.py for policy documentation
            file_mode = get_log_file_mode()
            fd = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, file_mode)
            try:
                os.write(fd, data)
            finally:
                os.close(fd)
            self._rollover_ts = time.time()

    def _rotate_if_needed(self, incoming_bytes: int) -> None:
        if not self.path.exists():
            self._rollover_ts = time.time()
            return

        if self.max_age_s is not None and self.max_age_s >= 0:
            if time.time() - self._rollover_ts >= self.max_age_s:
                try:
                    size = self.path.stat().st_size
                except FileNotFoundError as e:
                    type(e).__name__
                    logger.debug("FileNotFoundError: <ERROR_TYPE>")
                    size = 0
                if size > 0:
                    self._rotate()
                    return

        if self.max_bytes is None:
            return

        try:
            size = self.path.stat().st_size
        except FileNotFoundError as e:
            type(e).__name__
            logger.debug("FileNotFoundError: <ERROR_TYPE>")
            return
        if size + incoming_bytes <= self.max_bytes:
            return
        self._rotate()

    def _rotate(self) -> None:
        if self.backup_count <= 0:
            with contextlib.suppress(FileNotFoundError):
                self.path.unlink()
            self._rollover_ts = time.time()
            return

        oldest = self.path.with_name(f"{self.path.name}.{self.backup_count}")
        if oldest.exists():
            oldest.unlink()

        for idx in range(self.backup_count - 1, 0, -1):
            src = self.path.with_name(f"{self.path.name}.{idx}")
            if src.exists():
                src.rename(self.path.with_name(f"{self.path.name}.{idx + 1}"))

        if self.path.exists():
            self.path.rename(self.path.with_name(f"{self.path.name}.1"))
        self._rollover_ts = time.time()

    @staticmethod
    def _coerce_threshold(value: int | None) -> int | None:
        if value is None:
            return None
        try:
            numeric = int(value)
        except (TypeError, ValueError):  # pragma: no cover - defensive
            return None
        return numeric if numeric > 0 else None

    @staticmethod
    def _coerce_age(value: float | int | None) -> float | None:
        if value is None:
            return None
        try:
            numeric = float(value)
        except (TypeError, ValueError):  # pragma: no cover - defensive
            return None
        return numeric if numeric >= 0 else None


def _summary_rotator_for(path: Path) -> _SummaryRotator:
    resolved = path.resolve()
    with _SUMMARY_ROTATOR_LOCK:
        rotator = _SUMMARY_ROTATORS.get(resolved)
        if rotator is None:
            options = _summary_rotation_options()
            rotator = _SummaryRotator(
                resolved,
                max_bytes=options.get("max_bytes"),
                max_age_s=options.get("max_age_s"),
                backup_count=options.get("backup_count", DEFAULT_BACKUP_COUNT),
            )
            _SUMMARY_ROTATORS[resolved] = rotator
        return rotator


def _reset_summary_rotation_state_for_tests() -> None:
    with _SUMMARY_ROTATOR_LOCK:
        _SUMMARY_ROTATORS.clear()


def _is_local_mlflow_uri(uri: str) -> bool:
    if not uri:
        return True

    parsed = urlparse(uri)
    if parsed.scheme in {"", "file"}:
        if parsed.scheme == "file":
            netloc = parsed.netloc or ""
            return netloc in {"", "localhost"}
        return True

    return bool("://" not in uri and len(parsed.scheme) == 1)


def _write_deterministic_json(path: Path, record: MappingABC[str, Any]) -> None:
    payload = json.dumps(record, ensure_ascii=True, separators=(",", ":"))
    rotator = _summary_rotator_for(path)
    rotator.append(payload)


def _collect_dependency_flags() -> dict[str, Any]:
    try:
        from codex_ml.monitoring import system_metrics

        psutil_available = bool(getattr(system_metrics, "HAS_PSUTIL", False))
        nvml_available = bool(getattr(system_metrics, "HAS_NVML", False))
    except (ImportError, AttributeError):
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
        payload["extra"] = _normalise_summary_extra(extras)  # type: ignore[assignment]
    else:
        payload["extra"] = OrderedDict()  # type: ignore[assignment]
    _write_deterministic_json(summary_path, payload)


class BaseWriter(ABC):
    """Simple interface for metric writers."""

    @abstractmethod
    def log(self, row: dict[str, Any]) -> None:  # pragma: no cover - interface
        """Persist a single metrics row."""

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

    def log(self, row: dict[str, Any]) -> None:
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
    ) -> tuple[dict[str, Any], Optional[dict[str, Any]]]:
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
                self._manifest_logger.close()  # type: ignore[union-attr]
            except (ValueError, TypeError, RuntimeError):  # pragma: no cover
                logger.debug("Suppressed exception in handler", exc_info=True)
        try:
            self._logger.close()
        except (IOError, OSError):  # pragma: no cover
            logger.debug("Suppressed exception in handler", exc_info=True)


class TensorBoardWriter(BaseWriter):
    def __init__(self, logdir: str | Path, *, summary_path: str | Path | None = None) -> None:
        self._disabled_reason: str | None = None
        self._summary_path = Path(summary_path) if summary_path is not None else None
        try:  # optional dependency
            from torch.utils.tensorboard import SummaryWriter

            self._writer = SummaryWriter(log_dir=str(logdir))
            _emit_summary(
                self._summary_path,
                "tensorboard",
                "enabled",
                extra={"dependencies": _collect_dependency_flags()},
            )
        except (IOError, OSError) as exc:  # pragma: no cover - optional
            logger.debug("TensorBoard writer disabled", exc_info=exc)
            self._writer = None
            if isinstance(exc, ImportError):
                self._disabled_reason = format_optional_dependency_error(
                    "tensorboard",
                    "TensorBoard logging",
                )
            else:
                self._disabled_reason = _exc_reason("tensorboard", exc)
            _emit_summary(
                self._summary_path,
                "tensorboard",
                "disabled",
                reason=self._disabled_reason,
                extra={"dependencies": _collect_dependency_flags()},
            )

    def log(self, row: dict[str, Any]) -> None:
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
            except (IOError, OSError):  # pragma: no cover
                logger.debug("Suppressed exception in handler", exc_info=True)

    def status(self) -> Optional[str]:
        return self._disabled_reason


class MLflowWriter(BaseWriter):
    def __init__(
        self,
        uri: str | None,
        exp_name: str,
        run_name: str,
        tags: dict[str, Any],
        *,
        summary_path: str | Path | None = None,
    ) -> None:
        self._disabled_reason: str | None = None
        self._summary_path = Path(summary_path) if summary_path is not None else None
        provided_uri = (uri or "").strip()
        guard_decision = bootstrap_offline_tracking_decision(requested_uri=provided_uri or None)
        default_uri = guard_decision.effective_uri
        requested_uri = provided_uri or guard_decision.requested_uri
        target_uri = default_uri
        fallback_reason: Optional[str] = guard_decision.fallback_reason
        if provided_uri:
            if _is_local_mlflow_uri(provided_uri) or guard_decision.allow_remote:
                target_uri = provided_uri
                fallback_reason = fallback_reason if fallback_reason else None
            else:
                logger.warning(
                    "Non-file MLflow URI '%s' provided; falling back to %s",
                    provided_uri,
                    default_uri,
                )
                target_uri = default_uri
                fallback_reason = guard_decision.fallback_reason or "non_local_uri"
                if fallback_reason in {"non_file_scheme", "non_local_host"}:
                    fallback_reason = "non_local_uri"
        summary_extra = {
            "dependencies": _collect_dependency_flags(),
            "tracking_uri": target_uri,
            "requested_uri": requested_uri,
            "effective_uri": target_uri,
            "fallback_reason": fallback_reason or "",
            "allow_remote_flag": guard_decision.allow_remote_flag,
            "allow_remote": guard_decision.allow_remote,
            "system_metrics_enabled": guard_decision.system_metrics_enabled,
        }
        try:  # optional dependency
            import mlflow

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
                extra=summary_extra,
            )
        except (IOError, OSError) as exc:  # pragma: no cover - optional
            self._mlflow = None
            self._run = None
            logger.debug("MLflow writer disabled", exc_info=exc)
            if isinstance(exc, ImportError):
                self._disabled_reason = format_optional_dependency_error(
                    "mlflow",
                    "experiment tracking",
                )
            else:
                self._disabled_reason = _exc_reason("mlflow", exc)
            _emit_summary(
                self._summary_path,
                "mlflow",
                "disabled",
                reason=self._disabled_reason,
                extra=summary_extra,
            )

    def log(self, row: dict[str, Any]) -> None:
        if self._mlflow is None:
            return
        val = row.get("value")
        if isinstance(val, (int, float)):
            self._mlflow.log_metric(row["metric"], val, step=int(row["step"]))

    def close(self) -> None:
        if self._mlflow is not None:
            try:
                self._mlflow.end_run()
            except (IOError, OSError):  # pragma: no cover
                logger.debug("Suppressed exception in handler", exc_info=True)

    def status(self) -> Optional[str]:
        return self._disabled_reason


class WandbWriter(BaseWriter):
    def __init__(
        self,
        project: str,
        run_name: str,
        tags: dict[str, Any],
        mode: str = "offline",
        *,
        summary_path: str | Path | None = None,
    ) -> None:
        self._disabled_reason: str | None = None
        self._summary_path = Path(summary_path) if summary_path is not None else None
        try:  # optional dependency
            import wandb

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
        except (IOError, OSError) as exc:  # pragma: no cover - optional
            self._run = None
            logger.debug("Weights & Biases writer disabled", exc_info=exc)
            if isinstance(exc, ImportError):
                self._disabled_reason = format_optional_dependency_error(
                    "wandb",
                    "Weights & Biases logging",
                )
            else:
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

    def log(self, row: dict[str, Any]) -> None:
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
            except (IOError, OSError):  # pragma: no cover
                logger.debug("Suppressed exception in handler", exc_info=True)

    def status(self) -> Optional[str]:
        return self._disabled_reason


class CompositeWriter(BaseWriter):
    """Dispatch to multiple writers, swallowing individual errors."""

    def __init__(self, writers: Iterable[BaseWriter]) -> None:
        self._writers: list[BaseWriter] = list(writers)
        components: list[tuple[str, str]] = []
        for writer in self._writers:
            reason: Optional[str]
            status_getter = getattr(writer, "status", None)
            if callable(status_getter):
                try:
                    reason = status_getter()
                except (IOError, OSError):  # pragma: no cover - defensive
                    reason = getattr(writer, "_disabled_reason", None)
            else:
                reason = getattr(writer, "_disabled_reason", None)
            if reason:
                components.append(_parse_reason(reason))
        self._disabled_components: tuple[tuple[str, str], ...] = tuple(components)
        if self._disabled_components:
            summary = "; ".join(
                f"{name} ({detail})" if detail else name
                for name, detail in self._disabled_components
            )
            logger.error(f"[tracking] degraded writers: {summary}")

    def log(self, row: dict[str, Any]) -> None:
        for w in self._writers:
            try:
                w.log(row)
            except (IOError, OSError) as exc:  # pragma: no cover - robustness
                logger.debug("Writer log error", exc_info=exc)

    def close(self) -> None:
        for w in self._writers:
            try:
                w.close()
            except (IOError, OSError) as exc:  # pragma: no cover - robustness
                logger.debug("Writer close error", exc_info=exc)

    @property
    def disabled_components(self) -> tuple[tuple[str, str], ...]:
        return self._disabled_components


# Enhanced MLflow tracking classes
try:
    from mlflow.tracking import MlflowClient

    MLFLOW_CLIENT_AVAILABLE = True
except ImportError as e:
    error_type = type(e).__name__
    logger.debug("ImportError: <ERROR_TYPE>")
    MlflowClient = None
    MLFLOW_CLIENT_AVAILABLE = False


class MLflowMetricWriter:
    """
    Enhanced MLflow metric writer with better error handling.

    Provides graceful degradation and automatic run management.
    """

    def __init__(
        self,
        tracking_uri: Optional[str] = None,
        experiment_name: Optional[str] = None,
    ):
        """
        Initialize MLflow metric writer.

        Args:
            tracking_uri: MLflow tracking URI (default: mlruns)
            experiment_name: Experiment name for grouping runs
        """
        self.tracking_uri = tracking_uri or os.getenv("MLFLOW_TRACKING_URI", "mlruns")
        self.experiment_name = experiment_name or "codex_default"
        self._client: Optional[MlflowClient] = None
        self._initialized = False

        if MLFLOW_CLIENT_AVAILABLE:
            self._initialize()

    def _initialize(self) -> None:
        """Initialize MLflow connection."""
        if not MLFLOW_CLIENT_AVAILABLE:
            logger.warning("MLflow not available - metrics will not be tracked")
            return

        try:
            import mlflow

            mlflow.set_tracking_uri(self.tracking_uri)
            mlflow.set_experiment(self.experiment_name)
            self._client = MlflowClient(self.tracking_uri)
            self._initialized = True
            logger.info(f"MLflow initialized: {self.tracking_uri}")
        except (IOError, OSError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.error("Failed to initialize MLflow: <ERROR_TYPE>")
            self._initialized = False

    def write(self, metrics: dict[str, float], step: int = 0) -> bool:
        """
        Write metrics to active MLflow run.

        Args:
            metrics: Dictionary of metric name -> value
            step: Training step/epoch number

        Returns:
            True if successful, False otherwise
        """
        if not self._initialized:
            return False

        try:
            import mlflow

            if mlflow.active_run() is None:
                logger.warning("No active MLflow run - cannot log metrics")
                return False

            mlflow.log_metrics(metrics, step=step)
            return True
        except (IOError, OSError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.warning("Failed to log metrics to MLflow: <ERROR_TYPE>")
            return False

    def write_metric(self, key: str, value: float, step: int = 0) -> bool:
        """Write single metric."""
        return self.write({key: value}, step)

    def write_batch(
        self,
        metrics_batch: list[dict[str, Any]],
    ) -> int:
        """
        Write batch of metrics.

        Args:
            metrics_batch: List of {"metrics": {...}, "step": int}

        Returns:
            Number of successfully written batches
        """
        success_count = 0
        for batch in metrics_batch:
            if self.write(batch.get("metrics", {}), batch.get("step", 0)):
                success_count += 1
        return success_count


class MLflowParamWriter:
    """Write parameters to MLflow."""

    def __init__(self, metric_writer: MLflowMetricWriter):
        self._writer = metric_writer

    def write_params(self, params: dict[str, Any]) -> bool:
        """Log parameters to active run."""
        if not self._writer._initialized:
            return False

        try:
            import mlflow

            if mlflow.active_run() is None:
                logger.warning("No active MLflow run - cannot log params")
                return False

            # MLflow params must be strings
            str_params = {k: str(v) for k, v in params.items()}
            mlflow.log_params(str_params)
            return True
        except (IOError, OSError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.warning("Failed to log params: <ERROR_TYPE>")
            return False

    def write_config(self, config: dict[str, Any], prefix: str = "") -> bool:
        """Log nested config with flattened keys."""
        flat_params = self._flatten_dict(config, prefix)
        return self.write_params(flat_params)

    def _escape_key(self, key: str, sep: str = ".") -> str:
        """Escape separator characters in keys.

        NOTE: This is a one-way transformation. Keys with literal backslash-dot
        sequences cannot be distinguished from escaped keys after transformation.

        Args:
            key: Key to escape (any type)
            sep: Separator character to escape

        Returns:
            Escaped string key
        """
        key_str = str(key) if not isinstance(key, str) else key
        return key_str.replace(sep, f"\\{sep}")

    def _flatten_dict(
        self,
        d: dict[str, Any],
        prefix: str = "",
        sep: str = ".",
    ) -> dict[str, Any]:
        """Flatten nested dictionary with key validation and separator escaping."""
        items = {}
        for k, v in d.items():
            escaped_key = self._escape_key(k, sep)
            key = f"{prefix}{sep}{escaped_key}" if prefix else escaped_key
            if isinstance(v, dict):
                items.update(self._flatten_dict(v, key, sep))
            else:
                items[key] = v
        return items


class MLflowArtifactWriter:
    """Write artifacts to MLflow."""

    def __init__(self, metric_writer: MLflowMetricWriter):
        self._writer = metric_writer

    def log_artifact(
        self,
        local_path: str | Path,
        artifact_path: Optional[str] = None,
    ) -> bool:
        """Log a local file as artifact."""
        if not self._writer._initialized:
            return False

        try:
            import mlflow

            if mlflow.active_run() is None:
                logger.warning("No active MLflow run - cannot log artifact")
                return False

            mlflow.log_artifact(str(local_path), artifact_path)
            return True
        except (IOError, OSError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.warning("Failed to log artifact: <ERROR_TYPE>")
            return False

    def log_dict(
        self,
        data: dict[str, Any],
        filename: str,
    ) -> bool:
        """Log dictionary as JSON artifact."""
        if not self._writer._initialized:
            return False

        try:
            import mlflow

            if mlflow.active_run() is None:
                logger.warning("No active MLflow run - cannot log dict")
                return False

            mlflow.log_dict(data, filename)
            return True
        except (IOError, OSError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.warning("Failed to log dict artifact: <ERROR_TYPE>")
            return False

    def log_model(
        self,
        model: Any,
        artifact_path: str = "model",
    ) -> bool:
        """Log model with robust type detection.

        NOTE: Fallback detection may produce false positives for non-sklearn
        models that happen to have fit/predict methods. When sklearn is
        unavailable, use isinstance() checks with your specific model types.

        Args:
            model: Model object to log
            artifact_path: Path within artifact storage (default: "model")

        Returns:
            True if model logged successfully, False otherwise
        """
        if not self._writer._initialized:
            return False

        try:
            import mlflow

            if mlflow.active_run() is None:
                logger.warning("No active MLflow run - cannot log model")
                return False

            # Attempt to detect model type
            if hasattr(model, "save_pretrained"):
                # HuggingFace model
                import tempfile

                with tempfile.TemporaryDirectory() as tmpdir:
                    model.save_pretrained(tmpdir)
                    mlflow.log_artifacts(tmpdir, artifact_path)
            elif hasattr(model, "state_dict"):
                # PyTorch model
                try:
                    import mlflow.pytorch

                    mlflow.pytorch.log_model(model, artifact_path)
                except ImportError as e:
                    type(e).__name__
                    logger.debug("ImportError: <ERROR_TYPE>")
                    logger.warning("mlflow.pytorch is not available; cannot log PyTorch model.")
                    return False
            else:
                # Try robust sklearn detection using isinstance
                is_sklearn = False
                try:
                    from sklearn.base import BaseEstimator

                    is_sklearn = isinstance(model, BaseEstimator)
                except ImportError as e:
                    type(e).__name__
                    logger.debug("ImportError: <ERROR_TYPE>")
                    # Fallback: check characteristic methods (may have false positives)
                    model_module = getattr(type(model), "__module__", "")
                    has_fit = callable(getattr(model, "fit", None))
                    has_predict = callable(getattr(model, "predict", None))
                    is_sklearn = "sklearn" in model_module and has_fit and has_predict

                if is_sklearn:
                    # scikit-learn model
                    try:
                        import mlflow.sklearn

                        mlflow.sklearn.log_model(model, artifact_path)
                    except ImportError as e:
                        type(e).__name__
                        logger.debug("ImportError: <ERROR_TYPE>")
                        logger.warning(
                            "mlflow.sklearn is not available; cannot log scikit-learn model."
                        )
                        return False
                else:
                    logger.warning(f"Unsupported model type for MLflow logging: {type(model)}")
                    return False
            return True
        except (ValueError, TypeError, RuntimeError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.warning("Failed to log model: <ERROR_TYPE>")
            return False


class MLflowRunManager:
    """Context manager for MLflow run lifecycle."""

    def __init__(
        self,
        tracking_uri: Optional[str] = None,
        experiment_name: Optional[str] = None,
        run_name: Optional[str] = None,
        tags: Optional[dict[str, str]] = None,
    ):
        self.metric_writer = MLflowMetricWriter(tracking_uri, experiment_name)
        self.param_writer = MLflowParamWriter(self.metric_writer)
        self.artifact_writer = MLflowArtifactWriter(self.metric_writer)
        self.run_name = run_name
        self.tags = tags or {}
        self._run = None

    def start_run(self) -> "MLflowRunManager":
        """Context manager for MLflow run."""
        return self

    def __enter__(self) -> "MLflowRunManager":
        """Enter context manager."""
        if not MLFLOW_CLIENT_AVAILABLE or not self.metric_writer._initialized:
            return self

        try:
            import mlflow

            self._run = mlflow.start_run(run_name=self.run_name, tags=self.tags)
            self._run.__enter__()  # type: ignore[attr-defined]
        except (ImportError, AttributeError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.warning("Failed to start MLflow run: <ERROR_TYPE>")

        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context manager."""
        if self._run is not None:
            try:
                self._run.__exit__(exc_type, exc_val, exc_tb)
            except (ValueError, TypeError, RuntimeError) as e:
                type(e).__name__
                logger.debug("Exception: <ERROR_TYPE>")
                logger.warning("Failed to end MLflow run: <ERROR_TYPE>")
            finally:
                self._run = None

    @property
    def run_id(self) -> Optional[str]:
        """Get current run ID."""
        if self._run is not None:
            try:
                return self._run.info.run_id
            except (IOError, OSError):
                logger.debug("Suppressed exception in handler", exc_info=True)
        return None

    def log_metrics(self, metrics: dict[str, float], step: int = 0) -> bool:
        """Convenience method to log metrics."""
        return self.metric_writer.write(metrics, step)

    def log_params(self, params: dict[str, Any]) -> bool:
        """Convenience method to log params."""
        return self.param_writer.write_params(params)

    def log_artifact(self, path: str | Path) -> bool:
        """Convenience method to log artifact."""
        return self.artifact_writer.log_artifact(path)


def create_mlflow_tracker(
    tracking_uri: Optional[str] = None,
    experiment_name: Optional[str] = None,
    run_name: Optional[str] = None,
) -> MLflowRunManager:
    """
    Create an MLflow tracker with all writers.

    Usage:
        tracker = create_mlflow_tracker(experiment_name="my_experiment")
        with tracker.start_run():
            tracker.log_params({"lr": 0.001})
            for step in range(100):
                tracker.log_metrics({"loss": 0.5}, step=step)
    """
    return MLflowRunManager(
        tracking_uri=tracking_uri,
        experiment_name=experiment_name,
        run_name=run_name,
    )


__all__ = [
    "BaseWriter",
    "CompositeWriter",
    "MLflowArtifactWriter",
    "MLflowMetricWriter",
    "MLflowParamWriter",
    "MLflowRunManager",
    "MLflowWriter",
    "NdjsonWriter",
    "TensorBoardWriter",
    "WandbWriter",
    "create_mlflow_tracker",
]
