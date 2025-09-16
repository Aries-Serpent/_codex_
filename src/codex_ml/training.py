"""Compatibility wrapper for :mod:`codex_ml.training` package exports."""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    package_root = Path(__file__).resolve().parent.parent
    if str(package_root) not in sys.path:
        sys.path.append(str(package_root))
    __package__ = "codex_ml"  # type: ignore[assignment]

from .training import (
    OptimizerSettings,
    SafetySettings,
    SchedulerSettings,
    TrainingRunConfig,
    run_functional_training,
)

__all__ = [
    "OptimizerSettings",
    "SafetySettings",
    "SchedulerSettings",
    "TrainingRunConfig",
    "run_functional_training",
]
