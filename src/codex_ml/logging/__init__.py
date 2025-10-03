"""Primary entry points for structured run logging.

The public helpers exposed here aim to make experiment logging ergonomic in
offline environments. :class:`RunLogger` streams metrics and parameters to
newline-delimited JSON (NDJSON) files that can be inspected after a run without
starting an MLflow server, while :class:`FileLogger` offers a zero-dependency
sink for ad-hoc scripts that just need structured append-only files.
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
