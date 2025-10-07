"""Training package public surface."""

from __future__ import annotations

import warnings
from typing import Any, Mapping, Sequence

from .legacy_api import (  # noqa: F401 re-exported via __all__
    OptimizerSettings,
    SafetySettings,
    SchedulerSettings,
    TrainingRunConfig,
    build_dataloader,
    run_functional_training as _legacy_run_functional_training,
)
from .unified_training import UnifiedTrainingConfig, run_unified_training  # re-export

__all__ = [
    "SafetySettings",
    "OptimizerSettings",
    "SchedulerSettings",
    "TrainingRunConfig",
    "UnifiedTrainingConfig",
    "run_functional_training",
    "run_unified_training",
    "run_functional_training",
    "TrainingRunConfig",
    "SafetySettings",
    "OptimizerSettings",
    "SchedulerSettings",
    "build_dataloader",
]


def run_functional_training(
    *args: Any,
    **kwargs: Any,
) -> Mapping[str, Any] | Sequence[Any] | Any:
    """Compatibility shim for the legacy functional training entrypoint.

    The implementation lives in :mod:`codex_ml.training.legacy_api` and mirrors the
    long-standing behaviour that downstream tooling depends on.  Keep delegating to
    the legacy module while nudging callers toward the new unified façade.
    """

    warnings.warn(
        "codex_ml.training.run_functional_training is deprecated; "
        "import from codex_ml.training.legacy_api or use run_unified_training instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return _legacy_run_functional_training(*args, **kwargs)
