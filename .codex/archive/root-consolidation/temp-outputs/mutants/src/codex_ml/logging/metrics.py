"""
Metrics Module

This module provides functionality for metrics.

Usage:
    from logging.metrics import ...

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
import time  # noqa: E402
from dataclasses import asdict, dataclass, field  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Optional, TextIO  # noqa: E402

try:  # optional psutil
    import psutil
except (IOError, OSError):  # pragma: no cover
    psutil = None


@dataclass
class MetricRecord:
    step: int
    timestamp: float
    metrics: dict[str, float] = field(default_factory=dict)
    system: Optional[dict[str, float]] = None


class MetricLogger:
    """Append-only NDJSON metric logger."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._fh: Optional[TextIO] = None

    def _ensure_open(self) -> None:
        if self._fh is None:
            self._fh = self.path.open("a", encoding="utf-8")

    def _collect_system_metrics(self) -> Optional[dict[str, float]]:
        if psutil is None:
            return None
        try:
            vm = psutil.virtual_memory()
            return {
                "cpu_percent": float(psutil.cpu_percent(interval=None)),
                "ram_used_mb": float(vm.used) / (1024.0 * 1024.0),
                "ram_percent": float(vm.percent),
            }
        except (IOError, OSError):  # pragma: no cover
            return None

    def log(self, step: int, **scalars: float) -> None:
        self._ensure_open()
        ts = time.time()
        rec = MetricRecord(
            step=step,
            timestamp=ts,
            metrics={k: float(v) for k, v in scalars.items()},
            system=self._collect_system_metrics(),
        )
        if self._fh is None:
            raise RuntimeError("MetricLogger file handle not initialized")
        self._fh.write(json.dumps(asdict(rec)) + os.linesep)
        self._fh.flush()

    def close(self) -> None:
        if self._fh is not None:
            self._fh.close()
            self._fh = None

    def __enter__(self) -> MetricLogger:
        self._ensure_open()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
