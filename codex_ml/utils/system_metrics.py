"""Collect basic host metrics without external dependencies."""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Dict, Iterator, Optional

__all__ = ["collect_metrics"]


def collect_metrics() -> Dict[str, float]:
    """Return a small set of CPU/memory metrics when available."""

    metrics: Dict[str, float] = {}
    try:
        metrics["load_avg_1m"] = os.getloadavg()[0]
    except Exception:  # pragma: no cover - getloadavg not supported
        pass
    try:
        import psutil  # type: ignore

        metrics["cpu_percent"] = float(psutil.cpu_percent(interval=0.0))
        metrics["mem_percent"] = float(psutil.virtual_memory().percent)
    except Exception:
        pass
    return metrics
