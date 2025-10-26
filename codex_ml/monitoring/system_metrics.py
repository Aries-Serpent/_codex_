"""Periodic system metric logger."""

from __future__ import annotations

import json
import threading
import time
from pathlib import Path
from typing import Callable

from codex_ml.utils.system_metrics import collect_metrics

__all__ = ["SystemMetricsLogger"]


class SystemMetricsLogger:
    def __init__(self, path: str | Path, *, interval: float = 5.0) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.interval = max(0.5, float(interval))
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=1.0)

    def _run(self) -> None:
        while not self._stop.is_set():
            metrics = collect_metrics()
            if metrics:
                with self.path.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps(metrics, ensure_ascii=False) + "\n")
            self._stop.wait(self.interval)
