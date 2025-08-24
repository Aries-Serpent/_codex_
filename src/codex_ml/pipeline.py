"""Fallback pipeline implementation for the Codex training CLI."""

from __future__ import annotations

import os
from typing import Any, Iterable, Optional, Sequence

from .config import (
    TrainingWeights,
    PretrainingConfig,
    SFTConfig,
    RLHFConfig,
    ValidationThresholds,
)


def run_codex_pipeline(
    *,
    corpus: Sequence[str],
    demos: Sequence[dict[str, str]],
    pairwise_prefs: Sequence[tuple[str, str, str, int]],
    weights: TrainingWeights,
    pre_cfg: PretrainingConfig,
    sft_cfg: SFTConfig,
    rlhf_cfg: RLHFConfig,
    val_t: ValidationThresholds,
    synth_prompts: Optional[Iterable[str]] = None,
) -> dict[str, Any]:
    """Run the training pipeline or return synthetic metrics in fallback mode."""

    if os.getenv("CODEX_FALLBACK") == "1":
        return {
            "pretraining": {
                "status": "fallback",
                "tokens": sum(len(c) for c in corpus),
            },
            "sft": {"status": "fallback", "demos": len(demos)},
            "rlhf": {"status": "fallback", "pairs": len(pairwise_prefs)},
            "validation": {"status": "fallback", "thresholds": val_t.__dict__},
        }

    raise NotImplementedError("Real training pipeline is not implemented")

