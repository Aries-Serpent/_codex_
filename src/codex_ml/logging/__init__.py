"""Primary entry points for structured run logging.

Importing :mod:`codex_ml.logging` provides lightweight facades for writing
metrics and parameters as newline-delimited JSON (NDJSON) or CSV files without
pulling in heavier dependencies. The :class:`~codex_ml.logging.RunLogger`
cooperates with ``codex_ml.tracking`` to serialise metrics, while
:class:`~codex_ml.logging.FileLogger` exposes a minimal sink for scripts that
just need to append structured rows.
"""

from __future__ import annotations

from typing import Any

from .file_logger import FileLogger, JsonLogFmt

__all__ = [
    "RunLogger",
    "PARAMS_SCHEMA_URI",
    "METRICS_SCHEMA_URI",
    "FileLogger",
    "JsonLogFmt",
]


def __getattr__(name: str) -> Any:
    if name in {"RunLogger", "PARAMS_SCHEMA_URI", "METRICS_SCHEMA_URI"}:
        from .run_logger import METRICS_SCHEMA_URI, PARAMS_SCHEMA_URI, RunLogger

        globals().update(
            {
                "RunLogger": RunLogger,
                "PARAMS_SCHEMA_URI": PARAMS_SCHEMA_URI,
                "METRICS_SCHEMA_URI": METRICS_SCHEMA_URI,
            }
        )
        return globals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
