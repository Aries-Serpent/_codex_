"""Evaluation metrics (DEPRECATED - use codex_ml.metrics.unified_api instead).

This module is maintained for backward compatibility only.
All metric implementations have been consolidated into the unified API.

DEPRECATION PATH:
1. eval.metrics.bleu() → metrics.compute_bleu()
2. eval.metrics.rouge_l() → metrics.compute_rouge_l()
3. eval.metrics.perplexity() → metrics.compute_perplexity()
4. eval.metrics.accuracy() → metrics.compute_accuracy()
5. eval.metrics.classification_f1() → metrics.compute_f1()

For new code, import from codex_ml.metrics.unified_api or codex_ml.metrics directly.
"""

from __future__ import annotations

import logging
import warnings
from collections.abc import Iterable, Sequence
from typing import Optional

logger = logging.getLogger(__name__)

# Import unified implementations
from codex_ml.metrics.unified_api import (
    compute_accuracy as _compute_accuracy,
    compute_bleu as _compute_bleu,
    compute_f1 as _compute_f1,
    compute_perplexity as _compute_perplexity,
    compute_rouge_l as _compute_rouge_l,
    compute_token_accuracy as _compute_token_accuracy,
)

__all__ = [
    "MetricError",
    "_materialise",
    "_ensure_equal_length",
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
    "run_unit_tests",
    "token_accuracy",
    "token_stats",
]


class MetricError(ValueError):
    """Raised when metric computation fails due to invalid inputs."""

    def __init__(self, metric: str, message: str) -> None:
        super().__init__(f"{metric}: {message}")
        self.metric = metric


def _deprecation_warning(old_func: str, new_func: str) -> None:
    """Emit deprecation warning for metric functions."""
    warnings.warn(
        f"eval.metrics.{old_func}() is deprecated; use metrics.{new_func}() instead",
        DeprecationWarning,
        stacklevel=3,
    )


def perplexity(
    logits_or_nll: Iterable,
    targets: Iterable[int],
    *,
    from_logits: bool = True,
    ignore_index: int = -100,
    epsilon: float = 1e-12,
) -> float:
    """DEPRECATED: Use metrics.compute_perplexity() instead."""
    _deprecation_warning("perplexity", "compute_perplexity")
    return _compute_perplexity(logits_or_nll, targets, from_logits=from_logits, ignore_index=ignore_index, epsilon=epsilon)


def token_accuracy(
    preds: Sequence,
    targets: Sequence[int],
) -> float:
    """DEPRECATED: Use metrics.compute_token_accuracy() instead."""
    _deprecation_warning("token_accuracy", "compute_token_accuracy")
    return _compute_token_accuracy(preds, targets)


def accuracy(predictions: Iterable[int], targets: Iterable[int]) -> float:
    """DEPRECATED: Use metrics.compute_accuracy() instead."""
    _deprecation_warning("accuracy", "compute_accuracy")
    return _compute_accuracy(list(predictions), list(targets))


def bleu(
    predictions: Sequence[str],
    references: Sequence[str] | Sequence[Sequence[str]],
    use_sacrebleu: bool = True,
) -> float:
    """DEPRECATED: Use metrics.compute_bleu() instead."""
    _deprecation_warning("bleu", "compute_bleu")
    # Note: use_sacrebleu parameter ignored; unified_api uses best-of-breed implementation
    return _compute_bleu(predictions, references)


def rouge_l(predictions: Sequence[str], references: Sequence[str]) -> float:
    """DEPRECATED: Use metrics.compute_rouge_l() instead."""
    _deprecation_warning("rouge_l", "compute_rouge_l")
    return _compute_rouge_l(predictions, references)


def token_stats(
    preds: Sequence[int],
    targets: Sequence[int],
    *,
    ignore_index: int = -100,
) -> dict[str, int]:
    """DEPRECATED: No direct replacement; compute_token_accuracy() covers most use cases."""
    _deprecation_warning("token_stats", "compute_token_accuracy")
    # Legacy implementation: count valid, masked tokens
    valid_indices = [i for i, y in enumerate(targets) if int(y) != ignore_index]
    return {
        "total_tokens": len(targets),
        "valid_tokens": len(valid_indices),
        "ignored_tokens": len(targets) - len(valid_indices),
    }


def exact_match_strict(pred: str, ref: str) -> float:
    """DEPRECATED: No direct replacement; use string equality comparison instead."""
    _deprecation_warning("exact_match_strict", "string equality")
    return 1.0 if pred == ref else 0.0


def classification_f1(
    predictions: Iterable[int],
    targets: Iterable[int],
    labels: Optional[Sequence[int]] = None,
    *,
    average: str = "micro",
) -> float:
    """DEPRECATED: Use metrics.compute_f1() instead."""
    _deprecation_warning("classification_f1", "compute_f1")
    pred_list = list(predictions)
    tgt_list = list(targets)
    labels_list = list(labels) if labels else None
    return _compute_f1(pred_list, tgt_list, labels=labels_list, average=average)


def micro_f1(predictions: Iterable[int], targets: Iterable[int]) -> float:
    """DEPRECATED: Use metrics.compute_f1(..., average='micro') instead."""
    _deprecation_warning("micro_f1", "compute_f1(..., average='micro')")
    return _compute_f1(list(predictions), list(targets), average="micro")


def macro_f1(predictions: Iterable[int], targets: Iterable[int]) -> float:
    """DEPRECATED: Use metrics.compute_f1(..., average='macro') instead."""
    _deprecation_warning("macro_f1", "compute_f1(..., average='macro')")
    return _compute_f1(list(predictions), list(targets), average="macro")


def forward_transfer(baseline: Sequence[float], adapted: Sequence[float]) -> float:
    """Compute forward transfer metric (no replacement in unified API).

    Forward transfer = (adapted_loss - baseline_loss) / baseline_loss

    This metric is not consolidated into unified API as it's task-specific.
    """
    warnings.warn(
        "eval.metrics.forward_transfer() is not in unified API; using legacy implementation",
        DeprecationWarning,
        stacklevel=2,
    )
    if not baseline or not adapted:
        return 0.0
    if len(baseline) != len(adapted):
        raise MetricError("forward_transfer", "expected equal lengths")

    baseline_loss = sum(baseline) / len(baseline)
    adapted_loss = sum(adapted) / len(adapted)

    if baseline_loss == 0:
        return 0.0
    return float((baseline_loss - adapted_loss) / baseline_loss)


def backward_transfer(previous: Sequence[float], current: Sequence[float]) -> float:
    """Compute backward transfer metric (no replacement in unified API).

    Backward transfer measures if learning on new tasks hurts performance on old tasks.
    """
    warnings.warn(
        "eval.metrics.backward_transfer() is not in unified API; using legacy implementation",
        DeprecationWarning,
        stacklevel=2,
    )
    if not previous or not current:
        return 0.0
    if len(previous) != len(current):
        raise MetricError("backward_transfer", "expected equal lengths")

    prev_acc = sum(previous) / len(previous)
    curr_acc = sum(current) / len(current)
    return float(prev_acc - curr_acc)


def average_forgetting(history: Sequence[Sequence[float]]) -> float:
    """Compute average forgetting metric (no replacement in unified API).

    Measures average performance drop on old tasks as new tasks are learned.
    """
    warnings.warn(
        "eval.metrics.average_forgetting() is not in unified API; using legacy implementation",
        DeprecationWarning,
        stacklevel=2,
    )
    if not history or len(history) < 2:
        return 0.0

    total_forgetting = 0.0
    num_tasks = len(history)

    for i in range(num_tasks):
        peak = max(history[i])
        final = history[i][-1]
        forgetting = max(0.0, peak - final)
        total_forgetting += forgetting

    return float(total_forgetting / num_tasks)


def run_unit_tests(code_str: str, tests_dir: str) -> dict[str, int]:  # pragma: no cover - legacy
    """DEPRECATED: Legacy placeholder for unit test runner."""
    warnings.warn(
        "eval.metrics.run_unit_tests() is legacy and not in unified API",
        DeprecationWarning,
        stacklevel=2,
    )
    return {"passed": 0, "failed": 0, "errors": 0}
