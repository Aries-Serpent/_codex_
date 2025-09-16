"""Minimal training pipeline stubs for Codex CLI."""

from importlib import metadata as importlib_metadata

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

    __all__ = [
        "run_codex_pipeline",
        "run_codex_symbolic_pipeline",
        "TrainingWeights",
        "PretrainingConfig",
        "SFTConfig",
        "RLHFConfig",
        "ValidationThresholds",
        "Weights",
        "PretrainCfg",
        "SFTCfg",
        "RewardModelCfg",
        "RLHFCfg",
        "ModelHandle",
        "RewardModelHandle",
    ]
except Exception:  # pragma: no cover - degrade gracefully
    __all__ = [
        "run_codex_pipeline",
        "TrainingWeights",
        "PretrainingConfig",
        "SFTConfig",
        "RLHFConfig",
        "ValidationThresholds",
    ]

__all__.append("__version__")
