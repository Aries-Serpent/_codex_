"""Training package public surface."""

from __future__ import annotations

import warnings
from typing import Any, Mapping, Sequence

from codex.training import run_functional_training as _legacy_run_functional_training

from .unified_training import UnifiedTrainingConfig, run_unified_training  # re-export

__all__ = [
    "UnifiedTrainingConfig",
    "run_unified_training",
    "run_functional_training",
]


def run_functional_training(
    *args: Any,
    **kwargs: Any,
) -> Mapping[str, Any] | Sequence[Any] | Any:
    """Compatibility shim for legacy functional training entrypoint.

    Downstream callers still rely on :mod:`codex_ml.training` exporting
    :func:`run_functional_training`.  Keep delegating to the ``codex`` package
    implementation while nudging callers toward the new unified façade.
    """

    warnings.warn(
        "codex_ml.training.run_functional_training is deprecated; "
        "import from codex.training or use run_unified_training instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return _legacy_run_functional_training(*args, **kwargs)
