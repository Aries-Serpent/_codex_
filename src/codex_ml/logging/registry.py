"""Runtime logger registry utilities used by evaluation/CLI flows.

The previous implementation provided a minimal NDJSON writer without any
rotation or GPU telemetry support.  This module now re-uses the canonical
``codex_ml.logging.ndjson_logger.NDJSONLogger`` implementation so that
evaluation logs benefit from the same durability guarantees as the training
pipeline.  Optional system metrics cover RSS/CPU data via :mod:`psutil` and
GPU telemetry when :mod:`pynvml` is available.
"""

from __future__ import annotations

import time
from contextlib import suppress
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping

from .ndjson_logger import NDJSONLogger as CoreNDJSONLogger

try:  # pragma: no cover - optional dependency in offline envs
    import psutil
except ImportError:  # pragma: no cover
    psutil = None  # type: ignore[assignment]

try:  # pragma: no cover - GPU telemetry optional
    import pynvml
except ImportError:  # pragma: no cover
    pynvml = None  # type: ignore[assignment]


class NDJSONLogger:
    """Wrapper that augments :class:`CoreNDJSONLogger` with sys/GPU metrics."""

    def __init__(
        self,
        path: Path,
        *,
        sys_metrics: bool = False,
        max_bytes: int | None = None,
        backup_count: int = 3,
        max_age_s: float | None = None,
        ensure_ascii: bool = False,
    ) -> None:
        self._logger = CoreNDJSONLogger(
            path,
            max_bytes=max_bytes,
            backup_count=backup_count,
            max_age_s=max_age_s,
            ensure_ascii=ensure_ascii,
        )
        self.sys_metrics = sys_metrics
        self._nvml_initialised = False

    # ------------------------------------------------------------------
    # System metrics helpers
    # ------------------------------------------------------------------
    def _ensure_nvml(self) -> None:
        if self._nvml_initialised or pynvml is None:
            return
        try:
            pynvml.nvmlInit()  # type: ignore[attr-defined]
            self._nvml_initialised = True
        except Exception:
            self._nvml_initialised = False

    def _gpu_metrics(self) -> Dict[str, float]:
        if pynvml is None or not self._nvml_initialised:
            return {}
        try:
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)  # type: ignore[attr-defined]
            mem = pynvml.nvmlDeviceGetMemoryInfo(handle)  # type: ignore[attr-defined]
            util = pynvml.nvmlDeviceGetUtilizationRates(handle)  # type: ignore[attr-defined]
            return {
                "gpu_mem_mb": round(mem.used / (1024 * 1024), 2),
                "gpu_util_percent": float(util.gpu),
            }
        except Exception:
            return {}

    def _sys_metrics(self) -> Dict[str, float]:
        if not self.sys_metrics:
            return {}
        metrics: Dict[str, float] = {}
        if psutil is not None:
            try:
                proc = psutil.Process()  # type: ignore[no-untyped-call]
                metrics.update(
                    {
                        "mem_rss_mb": round(proc.memory_info().rss / (1024 * 1024), 2),
                        "cpu_percent": float(psutil.cpu_percent(interval=None)),
                    }
                )
            except Exception:  # pragma: no cover - defensive
                metrics.clear()
        if pynvml is not None:
            self._ensure_nvml()
            metrics.update(self._gpu_metrics())
        return metrics

    # ------------------------------------------------------------------
    # Public API compatible with the previous implementation
    # ------------------------------------------------------------------
    def log(self, record: Mapping[str, Any]) -> None:
        payload = dict(record)
        payload.setdefault("ts", time.time())
        payload.update(self._sys_metrics())
        self._logger.log(payload)

    def log_many(self, records: Iterable[Mapping[str, Any]]) -> None:
        prepared = []
        now = time.time()
        for record in records:
            payload = dict(record)
            payload.setdefault("ts", now)
            payload.update(self._sys_metrics())
            prepared.append(payload)
        if prepared:
            self._logger.log_many(prepared)

    def close(self) -> None:
        self._logger.close()
        if self._nvml_initialised and pynvml is not None:
            with suppress(Exception):  # pragma: no cover - defensive
                pynvml.nvmlShutdown()  # type: ignore[attr-defined]
            self._nvml_initialised = False


class MLflowLogger:  # minimal stub, optional
    def __init__(self, sys_metrics: bool = False):  # pragma: no cover (requires mlflow)
        self.sys_metrics = sys_metrics
        try:
            import mlflow

            mlflow.set_tracking_uri("file:" + str(Path("mlruns").absolute()))
            mlflow.start_run()
            self.mlflow = mlflow
        except Exception:
            self.mlflow = None

    def log(self, record: Mapping[str, Any]) -> None:  # pragma: no cover
        if self.mlflow is None:
            return
        for key, value in record.items():
            if isinstance(value, (int, float)):
                self.mlflow.log_metric(key, value)

    def close(self) -> None:  # pragma: no cover
        if self.mlflow:
            with suppress(Exception):
                self.mlflow.end_run()


def build_loggers(opts: Dict[str, Any]) -> List[Any]:
    output_dir = Path(opts.get("output_dir", "runs/logs"))
    output_dir.mkdir(parents=True, exist_ok=True)
    sys_metrics = bool(opts.get("sys_metrics", False))
    use_mlflow = bool(opts.get("use_mlflow", False))

    ndjson_kwargs = {
        "max_bytes": opts.get("ndjson_max_bytes"),
        "backup_count": int(opts.get("ndjson_backup_count", 3)),
        "max_age_s": opts.get("ndjson_max_age_s"),
        "ensure_ascii": bool(opts.get("ndjson_ensure_ascii", False)),
    }

    ndjson_path = output_dir / "metrics.ndjson"
    logger_instances: List[Any] = [
        NDJSONLogger(ndjson_path, sys_metrics=sys_metrics, **ndjson_kwargs)
    ]

    if use_mlflow:
        try:
            logger_instances.append(MLflowLogger(sys_metrics=sys_metrics))
        except Exception:  # pragma: no cover - mlflow optional
            pass

    return logger_instances


__all__ = ["NDJSONLogger", "MLflowLogger", "build_loggers"]
