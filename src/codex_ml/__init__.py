"""Minimal training pipeline stubs for Codex CLI."""

from .config import (
    PretrainingConfig,
    RLHFConfig,
    SFTConfig,
    TrainingWeights,
    ValidationThresholds,
)
from .pipeline import run_codex_pipeline

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
