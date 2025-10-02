"""Public shim that mirrors :mod:`codex_ml.logging.ndjson_logger` helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, Mapping

from codex_ml.logging.ndjson_logger import (  # re-exported for backwards compat
    NDJSONLogger as _CoreNDJSONLogger,
    is_legacy_mode,
    timestamped_record,
)

__all__ = ["NDJSONLogger", "timestamped_record", "is_legacy_mode"]


class NDJSONLogger(_CoreNDJSONLogger):
    """Compatibility wrapper around the core NDJSON logger implementation.

    Historically :mod:`codex_utils.ndjson` exposed a hand-rolled writer with
    ``write``/``write_many`` helpers.  Downstream utilities (tests, examples)
    still import this module, so we extend the richer core implementation with
    aliases to preserve the previous interface while gaining rotation and
    schema support (``run_id``/``timestamp`` fields, legacy toggle, etc.).
    """

    def __init__(
        self,
        path: str | Path = ".artifacts/metrics.ndjson",
        *,
        max_bytes: int | None = None,
        max_age_s: float | None = None,
        backup_count: int | None = None,
        ensure_ascii: bool = False,
        run_id: str | None = None,
    ) -> None:
        rotation: Dict[str, Any] = {}
        if max_bytes is not None:
            rotation["max_bytes"] = max_bytes
        if max_age_s is not None:
            rotation["max_age_s"] = max_age_s
        if backup_count is not None:
            rotation["backup_count"] = backup_count
        super().__init__(
            path,
            ensure_ascii=ensure_ascii,
            run_id=run_id,
            **rotation,
        )

    # ------------------------------------------------------------------
    # Backwards compatible aliases (write/write_many previously exposed)
    # ------------------------------------------------------------------
    def write(self, record: Mapping[str, Any]) -> Path:
        """Alias for :meth:`log` to preserve the historical API."""

        return self.log(record)

    def write_many(self, records: Iterable[Mapping[str, Any]]) -> Path:
        """Alias for :meth:`log_many` to preserve the historical API."""

        return self.log_many(records)

