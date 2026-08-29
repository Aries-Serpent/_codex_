"""Evaluation metrics (CONSOLIDATED - now at codex_ml.metrics.unified_api).

MIGRATION NOTICE (Phase 2 Consolidation - 2026-06-27):
All metric implementations have been consolidated into a single unified API.
This module re-exports from the backward-compatibility wrapper for 1 release cycle.

RECOMMENDED MIGRATION:
    from codex_ml.metrics import (  # NEW (Phase 2+)
        compute_bleu,
        compute_rouge_l,
        compute_perplexity,
        compute_accuracy,
        compute_f1,
    )

DEPRECATED (old imports, still work but emit warnings):
    from codex_ml.eval.metrics import bleu, rouge_l, perplexity, accuracy
    from codex_ml.evaluation.metrics import BleuMetric, RougeMetric

See .codex/ML_METRICS_CONSOLIDATION_PHASE_1.md for full consolidation report.
"""

from __future__ import annotations

# Re-export all deprecated functions for backward compatibility
# Import from the deprecated wrapper module in codex_ml.metrics
from codex_ml.metrics.metrics_deprecated import (  # noqa: F401
    MetricError,
    accuracy,
    average_forgetting,
    backward_transfer,
    bleu,
    classification_f1,
    exact_match_strict,
    forward_transfer,
    macro_f1,
    micro_f1,
    perplexity,
    rouge_l,
    run_unit_tests,
    token_accuracy,
    token_stats,
)

__all__ = [
    "MetricError",
    "accuracy",
    "average_forgetting",
    "backward_transfer",
    "bleu",
    "classification_f1",
    "exact_match_strict",
    "forward_transfer",
    "macro_f1",
    "micro_f1",
    "perplexity",
    "rouge_l",
    "token_accuracy",
    "token_stats",
    "run_unit_tests",
]
