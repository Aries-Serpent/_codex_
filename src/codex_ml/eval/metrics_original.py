"""Evaluation metrics used across Codex ML evaluation tooling."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import math  # noqa: E402
from collections.abc import Iterable, Sequence  # noqa: E402
from typing import Any, Optional  # noqa: E402

try:  # Optional dependency for efficiency
    import numpy as _np
except (ImportError, AttributeError):  # pragma: no cover - numpy is optional
    _np = None

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
]


class MetricError(ValueError):
    """Raised when metric computation fails due to invalid inputs."""

    def __init__(self, metric: str, message: str) -> None:
        super().__init__(f"{metric}: {message}")
        self.metric = metric


def _materialise(sequence: Iterable) -> list[Any]:
    return list(sequence)


def _ensure_equal_length(a: Sequence, b: Sequence, metric: str) -> None:
    if len(a) != len(b):
        raise MetricError(metric, f"expected equal lengths, got {len(a)} and {len(b)}")


def perplexity(
    logits_or_nll: Iterable,
    targets: Iterable[int],
    *,
    from_logits: bool = True,
    ignore_index: int = -100,
    epsilon: float = 1e-12,
) -> float:
    """Compute perplexity for a batch of predictions."""

    tgt = _materialise(targets)
    if from_logits:
        logits_list = _materialise(logits_or_nll)
        if not logits_list:
            raise MetricError("perplexity", "logit sequence is empty")
        _ensure_equal_length(logits_list, tgt, "perplexity")
        valid_indices = [i for i, y in enumerate(tgt) if int(y) != ignore_index]
        if not valid_indices:
            raise MetricError("perplexity", "no valid target positions")
        if _np is not None:
            arr = _np.asarray(logits_list, dtype=float)
            if arr.ndim != 2:
                raise MetricError("perplexity", "logits must be a 2D array")
            if arr.shape[0] != len(tgt):
                raise MetricError("perplexity", "logits batch dimension mismatch")
            max_vals = _np.max(arr, axis=1, keepdims=True)
            exp = _np.exp(arr - max_vals)
            probs = exp / _np.sum(exp, axis=1, keepdims=True)
            nll_values = []
            vocab = arr.shape[1]
            for idx in valid_indices:
                target = int(tgt[idx])
                if target < 0 or target >= vocab:
                    raise MetricError("perplexity", f"target index {target} out of range")
                prob = float(probs[idx, target])
                nll_values.append(-math.log(max(prob, epsilon)))
        else:
            nll_values = []
            for idx in valid_indices:
                row = logits_list[idx]
                if not isinstance(row, Sequence):
                    raise MetricError("perplexity", "logits must be sequences of floats")
                values = list(float(x) for x in row)
                m = max(values)
                exps = [math.exp(v - m) for v in values]
                s = sum(exps)
                if s <= 0:
                    raise MetricError("perplexity", "softmax denominator non-positive")
                probs = [v / s for v in exps]
                target = int(tgt[idx])
                if target < 0 or target >= len(probs):
                    raise MetricError("perplexity", f"target index {target} out of range")
                prob = probs[target]
                nll_values.append(-math.log(max(prob, epsilon)))
    else:
        nll_values = []
        losses = _materialise(logits_or_nll)
        _ensure_equal_length(losses, tgt, "perplexity")
        for value, target in zip(losses, tgt, strict=False):
            if int(target) == ignore_index:
                continue
            try:
                nll_values.append(float(value))
            except (TypeError, ValueError) as exc:
                type(exc).__name__
                logger.debug("Exception: <ERROR_TYPE>")
                raise MetricError("perplexity", f"invalid NLL value: {exc}") from exc
    if not nll_values:
        raise MetricError("perplexity", "no valid loss values to average")
    avg_nll = sum(nll_values) / len(nll_values)
    return float(math.exp(avg_nll))


def accuracy(predictions: Iterable[int], targets: Iterable[int]) -> float:
    """Compute classification accuracy."""

    preds = _materialise(predictions)
    targs = _materialise(targets)
    if not preds:
        raise MetricError("accuracy", "no predictions provided")
    _ensure_equal_length(preds, targs, "accuracy")
    correct = sum(int(p == t) for p, t in zip(preds, targs, strict=False))
    return float(correct / len(preds))


def token_stats(
    pred_tokens: Iterable[int],
    target_tokens: Iterable[int],
    *,
    ignore_index: int = -100,
) -> dict[str, float]:
    """Return token-level statistics including accuracy."""

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


def token_accuracy(
    pred_ids: Iterable[int], target_ids: Iterable[int], ignore_index: int = -100
) -> float:
    """Backward-compatible token accuracy wrapper."""

    return token_stats(pred_ids, target_ids, ignore_index=ignore_index)["accuracy"]


def forward_transfer(baseline: Sequence[float], adapted: Sequence[float]) -> float:
    base = [float(x) for x in _materialise(baseline)]
    new = [float(x) for x in _materialise(adapted)]
    _ensure_equal_length(base, new, "forward_transfer")
    improvements = [n - b for b, n in zip(base, new, strict=False)]
    return float(sum(improvements) / len(improvements)) if improvements else 0.0


def backward_transfer(previous: Sequence[float], current: Sequence[float]) -> float:
    prev = [float(x) for x in _materialise(previous)]
    curr = [float(x) for x in _materialise(current)]
    _ensure_equal_length(prev, curr, "backward_transfer")
    deltas = [curr_i - prev_i for curr_i, prev_i in zip(curr, prev, strict=False)]
    return float(sum(deltas) / len(deltas)) if deltas else 0.0


def average_forgetting(history: Sequence[Sequence[float]]) -> float:
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


def exact_match_strict(pred: str, ref: str) -> float:
    """Return 1.0 if ``pred`` equals ``ref`` after normalisation."""

    def norm(s: str) -> str:
        return " ".join(str(s).strip().split())

    return 1.0 if norm(pred) == norm(ref) else 0.0


def _precision_recall_f(tp: int, fp: int, fn: int, beta: float) -> float:
    if tp == 0 and fp == 0 and fn == 0:
        return 0.0
    precision = tp / (tp + fp) if tp + fp > 0 else 0.0
    recall = tp / (tp + fn) if tp + fn > 0 else 0.0
    if precision == 0.0 and recall == 0.0:
        return 0.0
    beta_sq = beta * beta
    denom = beta_sq * precision + recall
    if denom == 0:
        return 0.0
    return (1 + beta_sq) * precision * recall / denom


def classification_f1(
    predictions: Iterable[int],
    targets: Iterable[int],
    *,
    average: str = "micro",
    labels: Optional[Sequence[int]] = None,
    beta: float = 1.0,
) -> float:
    """Compute F1 score with configurable averaging."""

    preds = [int(p) for p in _materialise(predictions)]
    targs = [int(t) for t in _materialise(targets)]
    _ensure_equal_length(preds, targs, "f1")
    if not preds:
        raise MetricError("f1", "no predictions provided")
    if beta <= 0:
        raise MetricError("f1", "beta must be positive")
    label_set = sorted(set(labels) if labels is not None else set(preds) | set(targs))
    if not label_set:
        raise MetricError("f1", "no labels present")
    counts: dict[int, dict[str, int]] = {label: {"tp": 0, "fp": 0, "fn": 0} for label in label_set}
    for p, t in zip(preds, targs, strict=False):
        if p == t:
            if p in counts:
                counts[p]["tp"] += 1
        else:
            if p in counts:
                counts[p]["fp"] += 1
            if t in counts:
                counts[t]["fn"] += 1
    if average == "micro":
        tp = sum(c["tp"] for c in counts.values())
        fp = sum(c["fp"] for c in counts.values())
        fn = sum(c["fn"] for c in counts.values())
        return _precision_recall_f(tp, fp, fn, beta)
    scores: list[float] = []
    weights: list[int] = []
    for label in label_set:
        c = counts[label]
        score = _precision_recall_f(c["tp"], c["fp"], c["fn"], beta)
        scores.append(score)
        weights.append(c["tp"] + c["fn"])
    if average == "macro":
        return sum(scores) / len(scores)
    if average == "weighted":
        total = sum(weights)
        if total == 0:
            return 0.0
        return sum(s * w for s, w in zip(scores, weights, strict=False)) / total
    raise MetricError("f1", f"unknown averaging method: {average}")


def micro_f1(predictions: Iterable[int], targets: Iterable[int]) -> float:
    return classification_f1(predictions, targets, average="micro")


def macro_f1(predictions: Iterable[int], targets: Iterable[int]) -> float:
    return classification_f1(predictions, targets, average="macro")


def bleu(
    candidates: Sequence[str],
    references: Sequence[str],
    *,
    lowercase: bool = True,
) -> Optional[float]:
    """Compute corpus BLEU score if dependencies are available."""

    if len(candidates) != len(references):
        raise MetricError("bleu", "candidates and references length mismatch")

    # Try sacrebleu first (faster, more accurate)
    try:
        import sacrebleu

        hyp = [c.lower() if lowercase else c for c in candidates]
        ref = [r.lower() if lowercase else r for r in references]
        score = sacrebleu.BLEU(effective_order=True).corpus_score(hyp, [ref])
        result = float(score.score / 100.0)
        # Clamp to [0, 1] — sacrebleu can return values marginally above 1.0
        # due to floating-point arithmetic (e.g. 1.0000000000000004).
        return max(0.0, min(1.0, result))
    except (ImportError, AttributeError):
        logger.warning(
            "sacrebleu import or computation failed, falling back to NLTK",
            exc_info=True,
        )

    # Fall back to NLTK
    try:
        from nltk.translate.bleu_score import SmoothingFunction, corpus_bleu
    except (ImportError, AttributeError):
        logger.warning("NLTK not available", exc_info=True)
        return None

    hyp_tok = [(c.lower() if lowercase else c).split() for c in candidates]
    ref_tok = [[(r.lower() if lowercase else r).split()] for r in references]
    smoothie = SmoothingFunction().method3

    try:
        # NLTK corpus_bleu expects (list_of_references, list_of_hypotheses) order
        score = corpus_bleu(ref_tok, hyp_tok, smoothing_function=smoothie)
        result = float(score)
        # Sanity check: BLEU scores should be in [0, 1]
        if 0.0 <= result <= 1.0:
            return result
        logger.warning(f"NLTK corpus_bleu returned unexpected value: {result}")
        return None
    except (ValueError, TypeError, RuntimeError):
        logger.warning("NLTK BLEU computation failed", exc_info=True)
        return None


def rouge_l(
    candidates: Sequence[str],
    references: Sequence[str],
    *,
    lowercase: bool = True,
) -> Optional[dict[str, float]]:
    """Compute ROUGE-L F1 if ``rouge_score`` is installed."""

    if len(candidates) != len(references):
        raise MetricError("rouge_l", "candidates and references length mismatch")
    try:
        from rouge_score import rouge_scorer
    except (ImportError, AttributeError):
        logger.warning("Exception occurred", exc_info=True)
        return None
    scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)
    scores: list[float] = []
    for cand, ref in zip(candidates, references, strict=False):
        c = cand.lower() if lowercase else cand
        r = ref.lower() if lowercase else ref
        result = scorer.score(r, c)["rougeL"].fmeasure
        scores.append(float(result))
    if not scores:
        raise MetricError("rouge_l", "no candidate pairs to evaluate")
    return {"rougeL_f": float(sum(scores) / len(scores))}


def run_unit_tests(code_str: str, tests_dir: str) -> dict[str, int]:  # pragma: no cover - legacy
    import re
    import subprocess
    import tempfile
    from pathlib import Path

    tmpdir = Path(tempfile.mkdtemp())
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
