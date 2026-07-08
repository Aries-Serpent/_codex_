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
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Import unified implementations
from codex_ml.metrics.unified_api import (
    compute_accuracy as _compute_accuracy,
)
from codex_ml.metrics.unified_api import (
    compute_bleu as _compute_bleu,
)
from codex_ml.metrics.unified_api import (
    compute_f1 as _compute_f1,
)
from codex_ml.metrics.unified_api import (
    compute_perplexity as _compute_perplexity,
)
from codex_ml.metrics.unified_api import (
    compute_rouge_l as _compute_rouge_l,
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
    return _compute_perplexity(
        logits_or_nll, targets, from_logits=from_logits, ignore_index=ignore_index, epsilon=epsilon
    )


def token_accuracy(
    preds: Sequence,
    targets: Sequence[int],
    ignore_index: int = -100,
) -> float:
    """DEPRECATED: Use metrics.compute_token_accuracy() instead.

    Backward-compatible token accuracy wrapper that uses token_stats.
    """
    _deprecation_warning("token_accuracy", "compute_token_accuracy")
    # Use token_stats for backward compatibility
    stats = token_stats(preds, targets, ignore_index=ignore_index)
    return stats["accuracy"]


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
    pred_tokens: Iterable,
    target_tokens: Iterable[int],
    *,
    ignore_index: int = -100,
) -> dict[str, float]:
    """DEPRECATED: No direct replacement; compute_token_accuracy() covers most use cases.

    Return token-level statistics including accuracy.
    """
    _deprecation_warning("token_stats", "compute_token_accuracy")
    preds = [int(p) for p in _materialise(pred_tokens)]
    targs = [int(t) for t in _materialise(target_tokens)]
    _ensure_equal_length(preds, targs, "token_stats")
    total = 0
    correct = 0
    for p, t in zip(preds, targs, strict=False):
        if t == ignore_index:
            continue
        total += 1
        if p == t:
            correct += 1
    errors = total - correct
    acc = float(correct / total) if total else 0.0
    return {
        "total": float(total),
        "correct": float(correct),
        "errors": float(errors),
        "accuracy": acc,
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

    Measures improvement on new tasks.
    Forward transfer = average(adapted - baseline)
    """
    warnings.warn(
        "eval.metrics.forward_transfer() is not in unified API; using legacy implementation",
        DeprecationWarning,
        stacklevel=2,
    )
    base = [float(x) for x in _materialise(baseline)]
    new = [float(x) for x in _materialise(adapted)]
    _ensure_equal_length(base, new, "forward_transfer")
    improvements = [n - b for b, n in zip(base, new, strict=False)]
    return float(sum(improvements) / len(improvements)) if improvements else 0.0


def backward_transfer(previous: Sequence[float], current: Sequence[float]) -> float:
    """Compute backward transfer metric (no replacement in unified API).

    Backward transfer measures if learning on new tasks hurts performance on old tasks.
    backward_transfer = average(current - previous)
    """
    warnings.warn(
        "eval.metrics.backward_transfer() is not in unified API; using legacy implementation",
        DeprecationWarning,
        stacklevel=2,
    )
    prev = [float(x) for x in _materialise(previous)]
    curr = [float(x) for x in _materialise(current)]
    _ensure_equal_length(prev, curr, "backward_transfer")
    deltas = [curr_i - prev_i for curr_i, prev_i in zip(curr, prev, strict=False)]
    return float(sum(deltas) / len(deltas)) if deltas else 0.0


def average_forgetting(history: Sequence[Sequence[float]]) -> float:
    """Compute average forgetting metric (no replacement in unified API).

    Measures average performance drop on old tasks as new tasks are learned.
    """
    warnings.warn(
        "eval.metrics.average_forgetting() is not in unified API; using legacy implementation",
        DeprecationWarning,
        stacklevel=2,
    )
    stages = [list(float(x) for x in _materialise(stage)) for stage in history]
    if not stages:
        raise MetricError("average_forgetting", "history must contain at least one stage")
    length = len(stages[0])
    for stage in stages[1:]:
        if len(stage) != length:
            raise MetricError("average_forgetting", "all stages must share the same length")
    if len(stages) == 1:
        return 0.0
    latest = stages[-1]
    forgetting = []
    for task_idx in range(length):
        best = max(stage[task_idx] for stage in stages[:-1])
        current = latest[task_idx]
        forgetting.append(max(0.0, best - current))
    return float(sum(forgetting) / len(forgetting)) if forgetting else 0.0


def run_unit_tests(code_str: str, tests_dir: str) -> dict[str, int]:  # pragma: no cover - legacy
    """DEPRECATED: Legacy placeholder for unit test runner."""
    warnings.warn(
        "eval.metrics.run_unit_tests() is legacy and not in unified API",
        DeprecationWarning,
        stacklevel=2,
    )
    import re
    import subprocess
    import tempfile
    from pathlib import Path

    tmpdir = Path(tempfile.mkdtemp())
    try:
        mod = tmpdir / "candidate.py"
        mod.write_text(code_str, encoding="utf-8")
        proc = subprocess.run(
            ["pytest", "-q", tests_dir], cwd=str(tmpdir), capture_output=True, text=True
        )
        out = proc.stdout + proc.stderr

        def _count(pattern: str) -> int:
            matches = re.findall(pattern, out)
            return int(matches[-1]) if matches else 0

        return {
            "passed": _count(r"\b(\d+)\s+passed\b"),
            "failed": _count(r"\b(\d+)\s+failed\b"),
            "errors": _count(r"\b(\d+)\s+errors?\b"),
        }
    finally:
        import shutil

        shutil.rmtree(tmpdir, ignore_errors=True)


def _materialise(sequence: Iterable) -> list[Any]:
    """Convert an iterable to a list (helper function)."""
    return list(sequence)


def _ensure_equal_length(a: Sequence, b: Sequence, metric: str) -> None:
    """Ensure two sequences have equal length (helper function).

    Args:
        a: First sequence
        b: Second sequence
        metric: Metric name for error message

    Raises:
        MetricError: If sequences have different lengths
    """
    if len(a) != len(b):
        raise MetricError(metric, f"expected equal lengths, got {len(a)} and {len(b)}")
