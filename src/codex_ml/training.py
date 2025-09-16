"""Compatibility module re-exporting the functional training API."""

from __future__ import annotations

import importlib

try:  # pragma: no cover - imported as part of package
    from .training import SafetySettings, TrainingRunConfig, run_functional_training
except ImportError:  # pragma: no cover - imported via file path in tests
    _pkg = importlib.import_module("codex_ml.training")
    SafetySettings = _pkg.SafetySettings
    TrainingRunConfig = _pkg.TrainingRunConfig
    run_functional_training = _pkg.run_functional_training

__all__ = ["TrainingRunConfig", "SafetySettings", "run_functional_training"]
