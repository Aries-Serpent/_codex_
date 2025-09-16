"""Minimal training pipeline stubs for Codex CLI."""

from __future__ import annotations

from importlib import import_module
from importlib import metadata as importlib_metadata
from typing import TYPE_CHECKING

try:  # pragma: no cover - package metadata optional in editable installs
    __version__ = importlib_metadata.version("codex")
except importlib_metadata.PackageNotFoundError:  # pragma: no cover - local checkout fallback
    __version__ = "0.0.0"

try:  # pragma: no cover - optional dependency (OmegaConf)
    from .config import (
        PretrainingConfig,
        RLHFConfig,
        SFTConfig,
        TrainingWeights,
        ValidationThresholds,
    )
except Exception:  # pragma: no cover - degrade gracefully when config deps are missing

    class _MissingConfig:
        def __init__(self, name: str):
            self._name = name

        def __getattr__(self, item: str):  # pragma: no cover - defensive
            raise RuntimeError(
                f"Optional dependency for '{self._name}' is missing; install codex-ml[configs]"
            )

        def __call__(self, *args, **kwargs):  # pragma: no cover - defensive
            raise RuntimeError(
                f"Optional dependency for '{self._name}' is missing; install codex-ml[configs]"
            )

    PretrainingConfig = _MissingConfig("PretrainingConfig")  # type: ignore[assignment]
    SFTConfig = _MissingConfig("SFTConfig")  # type: ignore[assignment]
    RLHFConfig = _MissingConfig("RLHFConfig")  # type: ignore[assignment]
    TrainingWeights = _MissingConfig("TrainingWeights")  # type: ignore[assignment]
    ValidationThresholds = _MissingConfig("ValidationThresholds")  # type: ignore[assignment]

try:  # pragma: no cover - optional dependency tree
    from .pipeline import run_codex_pipeline
except Exception:  # pragma: no cover - degrade gracefully when configs missing

    def run_codex_pipeline(*_args, **_kwargs):
        raise RuntimeError("Optional dependencies for run_codex_pipeline are missing")


# Optional imports: symbolic pipeline requires tokenizer/transformers; guard for environments
# without heavy ML deps.
try:  # pragma: no cover - optional path
    from .symbolic_pipeline import (
        ModelHandle,
        PretrainCfg,
        RewardModelCfg,
        RewardModelHandle,
        RLHFCfg,
        SFTCfg,
        Weights,
        run_codex_symbolic_pipeline,
    )


_EXPORT_MAP = {
    "run_codex_pipeline": ("codex_ml.pipeline", "run_codex_pipeline"),
    "TrainingWeights": ("codex_ml.config", "TrainingWeights"),
    "PretrainingConfig": ("codex_ml.config", "PretrainingConfig"),
    "SFTConfig": ("codex_ml.config", "SFTConfig"),
    "RLHFConfig": ("codex_ml.config", "RLHFConfig"),
    "ValidationThresholds": ("codex_ml.config", "ValidationThresholds"),
    "run_codex_symbolic_pipeline": ("codex_ml.symbolic_pipeline", "run_codex_symbolic_pipeline"),
    "Weights": ("codex_ml.symbolic_pipeline", "Weights"),
    "PretrainCfg": ("codex_ml.symbolic_pipeline", "PretrainCfg"),
    "SFTCfg": ("codex_ml.symbolic_pipeline", "SFTCfg"),
    "RewardModelCfg": ("codex_ml.symbolic_pipeline", "RewardModelCfg"),
    "RLHFCfg": ("codex_ml.symbolic_pipeline", "RLHFCfg"),
    "ModelHandle": ("codex_ml.symbolic_pipeline", "ModelHandle"),
    "RewardModelHandle": ("codex_ml.symbolic_pipeline", "RewardModelHandle"),
}


def __getattr__(name: str):
    """Lazily import heavy optional modules on first access."""

    if name not in _EXPORT_MAP:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from None

    module_name, attr_name = _EXPORT_MAP[name]
    try:
        module = import_module(module_name)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = (
            f"{attr_name} is unavailable because importing {module_name!r} failed."
            " Install optional Codex ML dependencies to enable this feature."
        )
        raise ImportError(message) from exc
    return getattr(module, attr_name)


__all__ = sorted(set(__all__))
