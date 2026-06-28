"""Utility metrics for codex_ml.

This module provides consolidated access to all metrics via the unified API.
Canonical implementations are consolidated from 3 duplicate locations:
- src/codex_ml/metrics/ (primary)
- src/codex_ml/eval/metrics.py (secondary, deprecated)
- src/codex_ml/evaluation/metrics/ (tertiary, deprecated)

For new code, import from unified_api or use the top-level exports below.
"""

from codex_ml.metrics_base import accuracy, f1_score, mean_absolute_error, precision, recall

from .api import (
    get_metric,
    list_metrics,
    register_metric,
    summarize_ndjson_to_csv,
    summarize_ndjson_to_sqlite,
)
from .evaluator import batch_metrics

# Backward compatibility: legacy imports still available
from .generative import bleu, rouge_l
from .metric_implementations import (
    BLEUScore,
    F1Score,
    MetricRegistry,
    RecallScore,
    TokenAccuracy,
)
from .reward import reward_mean, reward_success_rate
from .text import perplexity, token_accuracy

# Import unified API - these are the canonical implementations
from .unified_api import (
    batch_metrics_from_outputs,
    compute_accuracy,
    compute_bleu,
    compute_classification_metrics,
    compute_f1,
    compute_perplexity,
    compute_rouge_l,
    compute_token_accuracy,
)

__all__ = [
    # Unified API (canonical implementations) - PREFERRED
    "batch_metrics_from_outputs",
    "compute_accuracy",
    "compute_bleu",
    "compute_classification_metrics",
    "compute_f1",
    "compute_perplexity",
    "compute_rouge_l",
    "compute_token_accuracy",
    # Legacy (backward compat)
    "BLEUScore",
    "F1Score",
    "MetricRegistry",
    "RecallScore",
    "TokenAccuracy",
    "accuracy",
    "batch_metrics",
    "bleu",
    "f1_score",
    "get_metric",
    "list_metrics",
    "mean_absolute_error",
    "perplexity",
    "precision",
    "recall",
    "register_metric",
    "reward_mean",
    "reward_success_rate",
    "rouge_l",
    "summarize_ndjson_to_csv",
    "summarize_ndjson_to_sqlite",
    "token_accuracy",
]
