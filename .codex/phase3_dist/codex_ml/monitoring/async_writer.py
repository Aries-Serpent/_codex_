"""
Async Writer Module

This module provides functionality for async writer.

Usage:
    from monitoring.async_writer import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import json  # noqa: E402
import os  # noqa: E402
import queue  # noqa: E402
import threading  # noqa: E402
import time  # noqa: E402
from dataclasses import dataclass  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Any  # noqa: E402


@dataclass
class LogLine:
    """Container for an enqueued log line."""

    ts: float
    data: dict[str, Any]


class AsyncLogFile:
    """Simple asynchronous NDJSON writer.

    Parameters
    ----------
    path:
        Destination path for the NDJSON file. Data is first written to a
        ``.tmp`` sidecar and atomically moved into place on rotation or close.
    rotate_bytes:
        Rotate the file when it grows beyond this many bytes. Rotation keeps a
        single completed file at ``path``.
    fsync:
        ``"never"`` to rely on OS buffering, ``"always"`` for an fsync after
        every write, or ``"interval"`` for periodic fsyncs.
    fsync_interval:
        Seconds between fsync calls when ``fsync="interval"``.
    max_queue:
        Maximum number of queued log lines before backpressure kicks in. The
        oldest entry is dropped when the queue is full.
    """

    def __init__(
        self,
        path: str,
        rotate_bytes: int = 64 * 1024 * 1024,
        fsync: str = "interval",
        fsync_interval: float = 5.0,
        max_queue: int = 1000,
    ) -> None:
        self.path = Path(path)
        self.tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        self.rotate_bytes = int(rotate_bytes)
        self.fsync = fsync
        self.fsync_interval = float(fsync_interval)
        self.q: queue.Queue[LogLine] = queue.Queue(maxsize=max_queue)
        self._stop = threading.Event()
        self._dropped = 0
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    # ------------------------------------------------------------------
    @property
    def dropped(self) -> int:
        """Number of dropped records due to a full queue."""

        return self._dropped

    # ------------------------------------------------------------------
    def write(self, data: dict[str, Any]) -> None:
        """Enqueue ``data`` for asynchronous persistence."""

        line = LogLine(time.time(), dict(data))
        try:
            self.q.put_nowait(line)
        except queue.Full:
            # Drop oldest record to make room
            try:
                _ = self.q.get_nowait()
                self.q.put_nowait(line)
                self._dropped += 1
            except queue.Full:
                self._dropped += 1

    # ------------------------------------------------------------------
    def close(self, timeout: float = 5.0) -> None:
        """Flush all queued records and stop the writer."""

        self._stop.set()
        self._thread.join(timeout)

    # Context manager helpers ------------------------------------------------
    def __enter__(self) -> AsyncLogFile:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # pragma: no cover - trivial
        self.close()

    # ------------------------------------------------------------------
    def _run(self) -> None:
        self.tmp.parent.mkdir(parents=True, exist_ok=True)
        f = self.tmp.open("a", encoding="utf-8")
        size = f.tell()
        last_fsync = time.time()
        while not (self._stop.is_set() and self.q.empty()):
            try:
                item = self.q.get(timeout=0.25)
            except queue.Empty:
                item = None
            if item is not None:
                line = json.dumps({"ts": item.ts, **item.data}, ensure_ascii=True)
                f.write(line + "\n")
                size += len(line) + 1
            if self.rotate_bytes and size >= self.rotate_bytes:
                f.flush()
                os.fsync(f.fileno())
                f.close()
                os.replace(self.tmp, self.path)
                f = self.tmp.open("a", encoding="utf-8")
                size = 0
            now = time.time()
            if self.fsync == "always" or (
                self.fsync == "interval" and now - last_fsync >= self.fsync_interval
            ):
                f.flush()
                os.fsync(f.fileno())
                last_fsync = now
        f.flush()
        os.fsync(f.fileno())
        f.close()
        os.replace(self.tmp, self.path)
