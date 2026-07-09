"""Logging registry scaffolding for _codex_.

Includes a minimal NDJSON logger factory used by evaluation and smoke tests.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

from collections.abc import Callable, Iterable, Mapping  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Any  # noqa: E402

from codex_ml.logging.ndjson_logger import NDJSONLogger as _RawNDJSONLogger  # noqa: E402
from codex_ml.utils.optional import optional_import  # noqa: E402

_LOGGERS: dict[str, Callable[[str], None]] = {}
psutil, _HAS_PSUTIL = optional_import("psutil")


def register_logger(name: str, fn: Callable[[str], None]) -> None:
    _LOGGERS[name] = fn


def get_logger(name: str) -> Callable[[str], None]:
    return _LOGGERS.get(name, lambda msg: None)


class _NDJSONMetricsLogger:
    """Simple NDJSON logger that can append optional system metrics."""

    def __init__(
        self,
        path: Path,
        *,
        sys_metrics: bool = False,  # Support both parameter names
        include_sys_metrics: bool | None = None,
        max_bytes: int | None = None,
        backup_count: int = 1,
        max_age_s: int | float | None = None,
    ) -> None:
        # Support both sys_metrics and include_sys_metrics for compatibility
        if include_sys_metrics is None:
            include_sys_metrics = sys_metrics

        self._logger = _RawNDJSONLogger(
            path,
            max_bytes=max_bytes,
            backup_count=backup_count,
            max_age_s=max_age_s,
        )
        self._include_sys_metrics = bool(include_sys_metrics and psutil is not None)

    def _system_metrics(self) -> dict[str, float]:  # pragma: no cover - env dependent
        if not self._include_sys_metrics:
            return {}
        try:
            proc = psutil.Process()
            mem = proc.memory_info()
            metrics: dict[str, float] = {
                "mem_rss_mb": mem.rss / (1024 * 1024),
            }
            if hasattr(mem, "vms"):
                metrics["mem_vms_mb"] = mem.vms / (1024 * 1024)
            # Add CPU percent if available
            if hasattr(psutil, "cpu_percent"):
                metrics["cpu_percent"] = psutil.cpu_percent(interval=None)
            return metrics
        except (ValueError, TypeError, RuntimeError):
            logger.debug("System metrics unavailable")
            return {}

    def log(self, record: Mapping[str, Any]) -> None:
        payload = dict(record)
        payload.update(self._system_metrics())
        self._logger.log(payload)

    def log_many(self, records: Iterable[Mapping[str, Any]]) -> None:
        prepared = ({**rec, **self._system_metrics()} for rec in records)
        self._logger.log_many(prepared)

    def close(self) -> None:
        self._logger.close()


def build_loggers(opts: Mapping[str, Any]) -> list[_NDJSONMetricsLogger]:
    """Construct NDJSON loggers based on the provided options.

    Parameters
    ----------
    opts:
        Mapping with keys ``output_dir`` and ``sys_metrics``.
    """

    output_dir = Path(opts.get("output_dir", "metrics"))
    output_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_dir / "metrics.ndjson"
    include_sys = bool(opts.get("sys_metrics", False))
    logger = _NDJSONMetricsLogger(log_path, include_sys_metrics=include_sys)
    return [logger]


__all__ = [
    "NDJSONLogger",  # Public alias: metrics-aware wrapper (accepts sys_metrics kwarg)
    "NDJSONMetricsLogger",  # Export the metrics logger for tests
    "build_loggers",
    "get_logger",
    "register_logger",
]

# Export _NDJSONMetricsLogger as NDJSONMetricsLogger for backward compatibility with tests
NDJSONMetricsLogger = _NDJSONMetricsLogger
# Export NDJSONLogger as the metrics-aware wrapper so `registry.NDJSONLogger(path, sys_metrics=True)`  # noqa: E501
# works as expected by tests. Uses a distinct public name to avoid shadowing the internal import.
NDJSONLogger = _NDJSONMetricsLogger  # intentional alias so registry.NDJSONLogger works
