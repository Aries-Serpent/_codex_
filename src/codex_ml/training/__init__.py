"""Training package public surface."""

from __future__ import annotations

import warnings
from typing import Any, Mapping, Sequence

from .device_strategy import DeviceConfig, DeviceMapper
from .dp_config import DifferentialPrivacyConfig, make_private_model
from .legacy_api import (
    OptimizerSettings,
    SafetySettings,
    SchedulerSettings,
    TrainingRunConfig,
    _evaluate_model,  # noqa: F401 - Compatibility exports for tests (PR #3330)
    build_dataloader,
    get_hf_revision,  # noqa: F401 - Compatibility exports for tests (PR #3330)
)
from .legacy_api import (
    run_functional_training as _legacy_run_functional_training,  # noqa: F401 re-exported via __all__
)
from .rng_checkpoint import RNGState, set_seed
from .unified_training import UnifiedTrainingConfig, run_unified_training  # re-export

# Compatibility imports for legacy test patches
# TODO: Remove after test migration
try:
    from codex_ml.utils.experiment_tracking_mlflow import maybe_mlflow

    mlflow_run = maybe_mlflow  # Alias for legacy tests
except ImportError:  # pragma: no cover - mlflow optional
    mlflow_run = None

# Additional compatibility imports for tests (PR #3248)
try:
    from codex_ml.utils.train_helpers import maybe_autocast
except ImportError:  # pragma: no cover - optional
    maybe_autocast = None

try:
    from codex_ml.utils.hf_pinning import load_from_pretrained
except ImportError:  # pragma: no cover - optional
    load_from_pretrained = None

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
    "DifferentialPrivacyConfig",
    "make_private_model",
    "DeviceConfig",
    "DeviceMapper",
    "RNGState",
    "set_seed",
    "maybe_autocast",  # Added for test compatibility (PR #3248)
    "load_from_pretrained",  # Added for test compatibility (PR #3248)
    "_evaluate_model",  # Added for test compatibility (PR #3330)
    "get_hf_revision",  # Added for test compatibility (PR #3330)
    "mlflow_run",  # Added for test compatibility (legacy patch target)
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
