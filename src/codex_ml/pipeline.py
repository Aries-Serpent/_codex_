"""Fallback-friendly Codex training pipeline."""

from __future__ import annotations

from typing import Any, Dict, Iterable, Optional, Sequence, Tuple
import os

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
    demos: Sequence[Dict[str, str]],
    pairwise_prefs: Sequence[Tuple[str, str, str, int]],
    weights: TrainingWeights,
    pre_cfg: PretrainingConfig,
    sft_cfg: SFTConfig,
    rlhf_cfg: RLHFConfig,
    val_t: ValidationThresholds,
    synth_prompts: Optional[Iterable[str]] = None,
) -> Dict[str, Any]:
    """Run the Codex training pipeline.

    This is a stub implementation that returns synthetic metrics when
    ``CODEX_FALLBACK`` is enabled. If fallback is disabled, a
    ``NotImplementedError`` is raised to signal missing real
    implementations.
    """

    fallback = os.getenv("CODEX_FALLBACK", "1") == "1"
    if not fallback:
        raise NotImplementedError("Real training pipeline not implemented")

    summary = {
        "pretraining_tokens": sum(len(x) for x in corpus),
        "sft_examples": len(list(demos)),
        "rlhf_pairs": len(list(pairwise_prefs)),
        "weights": {
            "alpha": weights.alpha,
            "beta": weights.beta,
            "gamma": weights.gamma,
        },
        "config": {
            "pretraining": {
                "model_size": pre_cfg.model_size,
                "context_length": pre_cfg.context_length,
            },
            "sft": {
                "batch_size": sft_cfg.batch_size,
                "learning_rate": sft_cfg.learning_rate,
                "epochs": sft_cfg.epochs,
            },
            "rlhf": {
                "algorithm": rlhf_cfg.algorithm,
                "kl_penalty": rlhf_cfg.kl_penalty,
                "ppo_epochs": rlhf_cfg.ppo_epochs,
            },
            "validation": {
                "syntax_ok": val_t.syntax_ok,
                "logic_ok": val_t.logic_ok,
                "security_ok": val_t.security_ok,
                "perf_ok": val_t.perf_ok,
            },
        },
    }

    if synth_prompts is not None:
        summary["synth_prompts"] = list(synth_prompts)

    return summary
