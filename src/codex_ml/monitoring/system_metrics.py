"""Utilities for logging host-level system metrics during offline runs."""

from __future__ import annotations

import atexit
import json
import os
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

try:  # pragma: no cover - optional dependency
    import psutil  # type: ignore
except Exception:  # pragma: no cover - psutil missing
    psutil = None  # type: ignore[assignment]

HAS_PSUTIL = psutil is not None


def _now() -> float:
    return time.time()


def sample_system_metrics() -> Dict[str, Any]:
    """Return a snapshot of CPU/memory utilisation.

    The function is safe to call even when :mod:`psutil` is unavailable – in that
    case an empty payload is returned.
    """

    if psutil is None:  # pragma: no cover - dependency missing
        return {}

    payload: Dict[str, Any] = {
        "ts": _now(),
        "cpu_percent": psutil.cpu_percent(interval=None),
    }

    try:
        payload["memory"] = dict(psutil.virtual_memory()._asdict())
    except Exception:  # pragma: no cover - platform specific
        payload["memory"] = None

    try:
        payload["swap"] = dict(psutil.swap_memory()._asdict())
    except Exception:  # pragma: no cover - platform specific
        payload["swap"] = None

    try:
        payload["load_avg"] = list(os.getloadavg())  # type: ignore[arg-type]
    except Exception:  # pragma: no cover - platform specific
        payload["load_avg"] = None

    try:
        proc = psutil.Process()
        payload["process"] = {
            "cpu_percent": proc.cpu_percent(interval=None),
            "memory_info": dict(proc.memory_info()._asdict()),
        }
    except Exception:  # pragma: no cover - process metrics optional
        payload["process"] = None

    return payload


def _write_record(path: Path, record: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")


def log_system_metrics(out_path: Path | str, interval: float = 60.0) -> None:
    """Continuously append system metrics to ``out_path``.

    This is a blocking helper that only returns when interrupted. It mirrors the
    minimal functionality sketched in the remediation plan so that automation can
    invoke it from a subprocess when needed.
    """

    if psutil is None:  # pragma: no cover - dependency missing
        raise RuntimeError("psutil is required for system metrics logging")

    target = Path(out_path)
    stop_event = threading.Event()

    def _loop() -> None:
        while not stop_event.is_set():
            try:
                _write_record(target, sample_system_metrics())
            except Exception:
                # Avoid killing the loop due to transient psutil errors.
                pass
            stop_event.wait(max(0.1, float(interval)))

    thread = threading.Thread(target=_loop, name="codex-system-metrics", daemon=True)
    thread.start()

    try:
        while thread.is_alive():
            thread.join(timeout=0.5)
    except KeyboardInterrupt:  # pragma: no cover - manual stop
        stop_event.set()
        thread.join()


@dataclass
class SystemMetricsLogger:
    """Background logger that writes metrics to a JSONL file."""

    path: Path | str
    interval: float = 60.0

    def __post_init__(self) -> None:
        if psutil is None:  # pragma: no cover - dependency missing
            raise RuntimeError("psutil is required for system metrics logging")
        self._path = Path(self.path)
        self._interval = max(0.1, float(self.interval))
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._atexit_registered = False

    def start(self) -> None:
        """Start logging metrics in the background."""

        if self._thread is not None and self._thread.is_alive():
            return

        self._stop.clear()
        self._thread = threading.Thread(target=self._run, name="codex-system-metrics", daemon=True)
        self._thread.start()
        if not self._atexit_registered:
            atexit.register(self.stop)
            self._atexit_registered = True

    def stop(self) -> None:
        """Signal the logger to stop and wait for completion."""

        self._stop.set()
        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=self._interval + 1.0)
        self._thread = None

    def __enter__(self) -> "SystemMetricsLogger":  # pragma: no cover - convenience
        self.start()
        return self

    def __exit__(self, *_exc: object) -> None:  # pragma: no cover - convenience
        self.stop()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                _write_record(self._path, sample_system_metrics())
            except Exception:
                pass
            self._stop.wait(self._interval)


__all__ = [
    "HAS_PSUTIL",
    "SystemMetricsLogger",
    "log_system_metrics",
    "sample_system_metrics",
]
