"""Canonical NDJSON logging utilities used across Codex ML.

`codex_ml.logging.ndjson_logger.NDJSONLogger` is the canonical structured logging sink for training and evaluation flows.
It writes newline-delimited JSON with atomic appends, optional rotation, and deterministic timestamp helpers.
"""

from __future__ import annotations

import json
import os
import threading
import time
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, MutableMapping
from uuid import uuid4

DEFAULT_MAX_BYTES = 64 * 1024 * 1024  # 64 MiB per shard by default
DEFAULT_MAX_AGE_S = 24 * 60 * 60  # rotate at least daily
DEFAULT_BACKUP_COUNT = 5

_LEGACY_ENV_FLAGS = ("CODEX_TRACKING_LEGACY_NDJSON", "LOGGING_NDJSON_LEGACY")


def is_legacy_mode() -> bool:
    for name in _LEGACY_ENV_FLAGS:
        raw = os.getenv(name)
        if raw and raw.strip().lower() in {"1", "true", "yes", "on"}:
            return True
    return False


class NDJSONLogger:
    """Append-only NDJSON logger.

    Parameters
    ----------
    path:
        Target file.  Parent directories are created automatically.
    max_bytes:
        Optional rotation threshold.  When set, the logger rotates the active
        file once its size exceeds ``max_bytes`` by renaming it with a timestamp
        suffix and starting a fresh file.
    ensure_ascii:
        Forwarded to :func:`json.dumps`; defaults to ``False`` for readability.
    """

    def __init__(
        self,
        path: str | Path,
        *,
        max_bytes: int | None = DEFAULT_MAX_BYTES,
        max_age_s: int | float | None = DEFAULT_MAX_AGE_S,
        backup_count: int = DEFAULT_BACKUP_COUNT,
        ensure_ascii: bool = False,
        run_id: str | None = None,
    ) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.max_bytes = self._coerce_threshold(max_bytes)
        self.max_age_s = self._coerce_age(max_age_s)
        self.backup_count = max(0, int(backup_count))
        self.ensure_ascii = ensure_ascii
        self.run_id = str(run_id or uuid4())
        self._legacy = is_legacy_mode()
        self._lock = threading.Lock()
        self._closed = False
        self._rollover_ts = self._initial_rollover_ts()

    def log(self, record: Mapping[str, Any]) -> Path:
        """Append ``record`` as a single NDJSON line."""

        if self._closed:
            raise RuntimeError("NDJSONLogger is closed")
        payload = json.dumps(
            self._prepare_record(record), ensure_ascii=self.ensure_ascii, separators=(",", ":")
        )
        data = (payload + "\n").encode("utf-8")
        with self._lock:
            self._rotate_if_needed(len(data))
            fd = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
            try:
                os.write(fd, data)
            finally:
                os.close(fd)
        return self.path

    def log_many(self, records: Iterable[Mapping[str, Any]]) -> Path:
        """Append multiple records atomically."""

        if self._closed:
            raise RuntimeError("NDJSONLogger is closed")
        prepared = (self._prepare_record(r) for r in records)
        payload = "".join(
            json.dumps(r, ensure_ascii=self.ensure_ascii, separators=(",", ":")) + "\n"
            for r in prepared
        )
        blob = payload.encode("utf-8")
        with self._lock:
            self._rotate_if_needed(len(blob))
            fd = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
            try:
                os.write(fd, blob)
            finally:
                os.close(fd)
        return self.path

    def _rotate_if_needed(self, incoming_bytes: int) -> None:
        if not self.path.exists():
            self._rollover_ts = time.time()
            return

        if self.max_age_s is not None and self.max_age_s >= 0:
            if time.time() - self._rollover_ts >= self.max_age_s:
                try:
                    size = self.path.stat().st_size
                except FileNotFoundError:
                    size = 0
                if size > 0:
                    self._rotate()
                    return

        if self.max_bytes is None:
            return

        try:
            size = self.path.stat().st_size
        except FileNotFoundError:
            return
        if size + incoming_bytes <= self.max_bytes:
            return
        self._rotate()

    def _rotate(self) -> None:
        if self.backup_count <= 0:
            try:
                self.path.unlink()
            except FileNotFoundError:
                pass
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

    def close(self) -> None:
        """Mark the logger as closed to prevent further writes."""

        self._closed = True

    def __enter__(self) -> "NDJSONLogger":  # pragma: no cover - convenience
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:  # pragma: no cover - convenience
        self.close()
        return False

    def _prepare_record(self, record: Mapping[str, Any]) -> MutableMapping[str, Any]:
        payload: MutableMapping[str, Any]
        if isinstance(record, OrderedDict):
            payload = OrderedDict(record)
        else:
            payload = OrderedDict(record.items())
        if self._legacy:
            return payload
        if "run_id" not in payload:
            payload["run_id"] = self.run_id
        if "timestamp" not in payload:
            payload["timestamp"] = self._now()
        return payload

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
    def _coerce_age(value: int | float | None) -> float | None:
        if value is None:
            return None
        try:
            numeric = float(value)
        except (TypeError, ValueError):  # pragma: no cover - defensive
            return None
        return numeric if numeric >= 0 else None

    def _initial_rollover_ts(self) -> float:
        """Return the timestamp to use for age-based rotation tracking."""

        if self.max_age_s is None or self.max_age_s < 0:
            return time.time()

        try:
            return self.path.stat().st_mtime
        except FileNotFoundError:
            return time.time()

    @staticmethod
    def _now() -> str:
        ts = datetime.now(timezone.utc).isoformat()
        return ts.replace("+00:00", "Z")


def timestamped_record(**data: Any) -> dict[str, Any]:
    """Return ``data`` augmented with an ISO timestamp."""

    payload: MutableMapping[str, Any] = OrderedDict(data.items())
    ts = NDJSONLogger._now()
    payload.setdefault("timestamp", ts)
    payload.setdefault("ts", ts)
    return payload


__all__ = ["NDJSONLogger", "timestamped_record", "is_legacy_mode"]
