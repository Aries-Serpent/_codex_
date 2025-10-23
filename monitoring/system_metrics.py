"""System metric logging helpers used during training loops."""

from __future__ import annotations

import importlib
import importlib.util
import time
from dataclasses import dataclass
from typing import Any, Protocol

_PSUTIL: Any | None
if importlib.util.find_spec("psutil") is None:
    _PSUTIL = None
else:  # pragma: no cover - depends on optional dependency
    _PSUTIL = importlib.import_module("psutil")


class ScalarWriter(Protocol):
    """Minimal interface satisfied by TensorBoard and WandB writers."""

    def add_scalar(
        self, tag: str, value: float, global_step: int
    ) -> None:  # pragma: no cover - protocol
        """Record a scalar value."""


@dataclass
class SystemMetricsLogger:
    """Periodically record CPU and memory usage."""

    log_interval: float = 5.0
    prefix: str = "system"

    def __post_init__(self) -> None:
        self._last_ts: float = 0.0

    def log(self, *, step: int | None = None, writer: ScalarWriter | None = None) -> None:
        if _PSUTIL is None:
            return
        now = time.time()
        if self._last_ts and now - self._last_ts < self.log_interval:
            return
        cpu = float(_PSUTIL.cpu_percent())
        memory = float(getattr(_PSUTIL.virtual_memory(), "percent", 0.0))
        if writer is not None:
            writer.add_scalar(f"{self.prefix}/cpu_percent", cpu, step or int(now))
            writer.add_scalar(f"{self.prefix}/memory_percent", memory, step or int(now))
        else:
            resolved_step = step if step is not None else int(now)
            print(
                f"[{self.prefix}] cpu={cpu:.1f}% memory={memory:.1f}% step={resolved_step}",
                flush=True,
            )
        self._last_ts = now


__all__ = ["SystemMetricsLogger", "ScalarWriter"]
