"""Logging registry scaffolding for _codex_.

Includes a minimal NDJSON logger factory used by evaluation and smoke tests.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Mapping

from codex_ml.logging.ndjson_logger import NDJSONLogger
from codex_ml.utils.optional import optional_import

_LOGGERS: Dict[str, Callable[[str], None]] = {}
psutil, _HAS_PSUTIL = optional_import("psutil")


def register_logger(name: str, fn: Callable[[str], None]) -> None:
    _LOGGERS[name] = fn


def get_logger(name: str) -> Callable[[str], None]:
    return _LOGGERS.get(name, lambda msg: None)


class _NDJSONMetricsLogger:
    """Simple NDJSON logger that can append optional system metrics."""

    def __init__(self, path: Path, *, include_sys_metrics: bool = False) -> None:
        self._logger = NDJSONLogger(path)
        self._include_sys_metrics = include_sys_metrics and _HAS_PSUTIL and psutil is not None

    def _system_metrics(self) -> dict[str, float]:  # pragma: no cover - env dependent
        if not self._include_sys_metrics:
            return {}
        try:
            proc = psutil.Process()
            mem = proc.memory_info()
            return {
                "mem_rss_mb": mem.rss / (1024 * 1024),
                "mem_vms_mb": mem.vms / (1024 * 1024),
            }
        except Exception:
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


def build_loggers(opts: Mapping[str, Any]) -> List[_NDJSONMetricsLogger]:
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
    "build_loggers",
    "get_logger",
    "register_logger",
]
