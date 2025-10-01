"""NDJSON logging utilities with atomic appends and simple rotation."""

from __future__ import annotations

import json
import os
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping
from uuid import uuid4

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
        max_bytes: int | None = None,
        max_age_s: int | float | None = None,
        backup_count: int = 5,
        ensure_ascii: bool = False,
        run_id: str | None = None,
    ) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.max_bytes = max_bytes
        self.max_age_s = float(max_age_s) if max_age_s else None
        self.backup_count = max(0, int(backup_count))
        self.ensure_ascii = ensure_ascii
        self.run_id = str(run_id or uuid4())
        self._legacy = is_legacy_mode()
        self._lock = threading.Lock()

    def log(self, record: Mapping[str, Any]) -> Path:
        """Append ``record`` as a single NDJSON line."""

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
            return

        if self.max_age_s:
            try:
                stat = self.path.stat()
            except FileNotFoundError:
                stat = None
            else:
                if stat.st_size > 0 and time.time() - stat.st_mtime >= self.max_age_s:
                    self._rotate()
                    return

        if not self.max_bytes:
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

    def _prepare_record(self, record: Mapping[str, Any]) -> dict[str, Any]:
        payload = dict(record)
        if self._legacy:
            return payload
        payload.setdefault("run_id", self.run_id)
        payload.setdefault("timestamp", self._now())
        return payload

    @staticmethod
    def _now() -> str:
        ts = datetime.now(timezone.utc).isoformat()
        return ts.replace("+00:00", "Z")


def timestamped_record(**data: Any) -> dict[str, Any]:
    """Return ``data`` augmented with an ISO timestamp."""

    payload = dict(data)
    ts = NDJSONLogger._now()
    payload.setdefault("timestamp", ts)
    payload.setdefault("ts", ts)
    return payload


__all__ = ["NDJSONLogger", "timestamped_record", "is_legacy_mode"]
