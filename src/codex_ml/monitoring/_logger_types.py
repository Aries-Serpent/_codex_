"""Reusable telemetry logger container types.

This module is intentionally isolated so that :mod:`codex_ml.monitoring.codex_logging`
can be reloaded during tests without redefining the dataclasses. Some tests
capture references to :class:`CodexLoggers` during collection and later reload
``codex_logging``; keeping the dataclass definition in a separate module ensures
identity stability across those reloads.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Tuple

from codex_ml.monitoring.system_metrics import SamplerStatus


@dataclass(frozen=True)
class TelemetryComponentStatus:
    """Simple container describing availability of a telemetry sink."""

    name: str
    available: bool
    detail: Optional[str] = None


@dataclass
class CodexLoggers:
    """Container for optional logger handles used throughout monitoring."""

    tb: Any = None
    wb: Any = None
    mlflow_active: bool = False
    gpu: bool = False
    degradations: Tuple[TelemetryComponentStatus, ...] = ()
    system_status: "SamplerStatus | None" = None
    prometheus: Tuple[bool, Optional[Path], Optional[str]] | None = None

    # Back-compat convenience: allow dict-like access for common keys.
    def __getitem__(self, key: str) -> Any:  # pragma: no cover - convenience
        if key == "tb":
            return self.tb
        if key == "wb":
            return self.wb
        if key in {"mlflow", "mlflow_active"}:
            return self.mlflow_active
        if key == "gpu":
            return self.gpu
        raise KeyError(key)


__all__ = ["TelemetryComponentStatus", "CodexLoggers", "SamplerStatus"]
