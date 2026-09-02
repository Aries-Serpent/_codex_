"""Training package public surface."""

from __future__ import annotations

import warnings
from collections.abc import Mapping, Sequence
from typing import Any


def _missing_training_dependency(*_args: Any, **_kwargs: Any) -> Any:
    """Raise a clear runtime error when optional ML training deps are unavailable."""

    raise RuntimeError(
        "Optional training dependencies are unavailable in this environment; "
        "install the training extras required for the legacy training stack."
    )


try:
    from . import legacy_api as _legacy_api_module
    from .device_strategy import DeviceConfig, DeviceMapper
    from .dp_config import DifferentialPrivacyConfig, make_private_model
    from .legacy_api import (
        OptimizerSettings,
        SafetySettings,
        SchedulerSettings,
        TrainingRunConfig,
        _evaluate_model,
        build_dataloader,
        export_environment,
        get_hf_revision,
        sanitize_prompt,
        set_reproducible,
    )
    from .legacy_api import run_functional_training as _legacy_run_functional_training
    from .rng_checkpoint import RNGState, set_seed
    from .unified_training import UnifiedTrainingConfig, run_unified_training  # re-export
except (ImportError, AttributeError, ModuleNotFoundError, RuntimeError):  # pragma: no cover
    _legacy_api_module = None
    _legacy_run_functional_training = None
    DeviceConfig = None  # type: ignore[assignment]
    DeviceMapper = None  # type: ignore[assignment]
    DifferentialPrivacyConfig = None  # type: ignore[assignment]
    make_private_model = _missing_training_dependency
    OptimizerSettings = None  # type: ignore[assignment]
    SafetySettings = None  # type: ignore[assignment]
    SchedulerSettings = None  # type: ignore[assignment]
    TrainingRunConfig = None  # type: ignore[assignment]
    _evaluate_model = _missing_training_dependency
    build_dataloader = _missing_training_dependency
    export_environment = _missing_training_dependency
    get_hf_revision = _missing_training_dependency
    sanitize_prompt = _missing_training_dependency
    set_reproducible = _missing_training_dependency
    RNGState = None  # type: ignore[assignment]
    set_seed = _missing_training_dependency
    UnifiedTrainingConfig = None  # type: ignore[assignment]
    run_unified_training = _missing_training_dependency

# Compatibility imports for legacy test patches
# NOTE: mlflow_run alias is intentionally kept — legacy tests still patch this symbol.
#       Remove once test_training_integration_flags.py migrates to patching maybe_mlflow directly.
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
    "DeviceConfig",
    "DeviceMapper",
    "DifferentialPrivacyConfig",
    "OptimizerSettings",
    "OptimizerSettings",
    "RNGState",
    "SafetySettings",
    "SafetySettings",
    "SchedulerSettings",
    "SchedulerSettings",
    "TrainingRunConfig",
    "TrainingRunConfig",
    "UnifiedTrainingConfig",
    "_evaluate_model",  # Added for test compatibility (PR #3330)
    "build_dataloader",
    "get_hf_revision",  # Added for test compatibility (PR #3330)
    "load_from_pretrained",  # Added for test compatibility (PR #3248)
    "make_private_model",
    "maybe_autocast",  # Added for test compatibility (PR #3248)
    "mlflow_run",  # Added for test compatibility (legacy patch target)
    "run_functional_training",
    "run_functional_training",
    "run_unified_training",
    "sanitize_prompt",
    "set_reproducible",
    "export_environment",
    "set_seed",
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
    if _legacy_run_functional_training is None:
        raise RuntimeError(
            "The legacy training stack is unavailable in this environment because optional "
            "ML dependencies are missing. Install the training extras or use the unified "
            "training API instead."
        )
    if _legacy_api_module is not None:
        _legacy_api_module.sanitize_prompt = sanitize_prompt
        _legacy_api_module.set_reproducible = set_reproducible
        _legacy_api_module.export_environment = export_environment
    return _legacy_run_functional_training(*args, **kwargs)
