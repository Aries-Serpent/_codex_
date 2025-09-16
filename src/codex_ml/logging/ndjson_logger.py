"""NDJSON logging utilities with atomic appends and simple rotation."""

from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping


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
        self, path: str | Path, *, max_bytes: int | None = None, ensure_ascii: bool = False
    ) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.max_bytes = max_bytes
        self.ensure_ascii = ensure_ascii
        self._lock = threading.Lock()

    def log(self, record: Mapping[str, Any]) -> Path:
        """Append ``record`` as a single NDJSON line."""

        payload = json.dumps(record, ensure_ascii=self.ensure_ascii)
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

        payload = "".join(json.dumps(r, ensure_ascii=self.ensure_ascii) + "\n" for r in records)
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
        if not self.max_bytes:
            return
        try:
            size = self.path.stat().st_size
        except FileNotFoundError:
            return
        if size + incoming_bytes <= self.max_bytes:
            return
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        rotated = self.path.with_suffix(self.path.suffix + f".{timestamp}")
        counter = 0
        while rotated.exists():
            counter += 1
            rotated = self.path.with_suffix(self.path.suffix + f".{timestamp}.{counter}")
        self.path.rename(rotated)


def timestamped_record(**data: Any) -> dict[str, Any]:
    """Return ``data`` augmented with an ISO timestamp."""

    payload = dict(data)
    payload.setdefault("ts", datetime.now(timezone.utc).isoformat())
    return payload


__all__ = ["NDJSONLogger", "timestamped_record"]
