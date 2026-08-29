"""Unified Metrics API - Single source of truth for all metric computations.

This module consolidates BLEU, ROUGE-L, perplexity, classification, and token
accuracy metrics from 3 fragmented locations:
- src/codex_ml/metrics/ (primary)
- src/codex_ml/eval/metrics.py (secondary)
- src/codex_ml/evaluation/metrics/ (tertiary)

All metrics are normalized to a consistent interface with unified error handling
and optional dependency support.

Author: Codex Team
Version: 1.0.0
Status: Production (Phase 2 consolidation)
"""

from __future__ import annotations

import logging
import math
from collections.abc import Callable, Iterable, Sequence
from typing import Any, Optional

logger = logging.getLogger(__name__)

__all__ = [
    "compute_bleu",
    "compute_rouge_l",
    "compute_perplexity",
    "compute_token_accuracy",
    "compute_accuracy",
    "compute_f1",
    "compute_classification_metrics",
    "batch_metrics_from_outputs",
]


# ============================================================================
# BLEU Metric (consolidated from 4 implementations)
# ============================================================================


def _tokenize(s: str) -> list[str]:
    """Tokenize string into words."""
    return [t for t in s.strip().split() if t]


def _ngram_counts(tokens: list[str], n: int) -> dict[tuple[str, ...], int]:
    """Compute n-gram counts with clipping."""
    counts: dict[tuple[str, ...], int] = {}
    if n <= 0 or len(tokens) < n:
        return counts
    for i in range(len(tokens) - n + 1):
        ngram = tuple(tokens[i : i + n])
        counts[ngram] = counts.get(ngram, 0) + 1
    return counts


def compute_brevity_penalty(
    hypotheses: Sequence[str],
    norm_refs: Sequence[Sequence[str]],
    tokenize: Callable[[str], Iterable[str]] = _tokenize,
) -> float:
    """Compute BLEU brevity penalty (penalizes short hypotheses)."""
    if len(hypotheses) != len(norm_refs):
        raise ValueError("hypotheses and references length must match")

    hyp_len = sum(len(list(tokenize(h))) for h in hypotheses)
    ref_len = 0

    for hyp, refs in zip(hypotheses, norm_refs, strict=False):
        cand_len = len(list(tokenize(hyp)))
        if not refs:
            best = 0
        else:
            ref_candidates = (
                (abs(len(list(tokenize(r))) - cand_len), len(list(tokenize(r)))) for r in refs
            )
            best = min(ref_candidates)[1]
        ref_len += best

    if hyp_len == 0:
        return 0.0
    if hyp_len > ref_len:
        return 1.0
    return math.exp(1.0 - ref_len / hyp_len)


def compute_bleu(
    predictions: Sequence[str],
    references: Sequence[str] | Sequence[Sequence[str]],
    max_n: int = 4,
    smooth: float = 1e-9,
) -> float:
    """
    Compute BLEU score (corpus-level).

    Implements standard BLEU metric with n-gram precision clipping and brevity penalty.
    This is the canonical implementation consolidated from 4 duplicate implementations.

    Args:
        predictions: List of hypothesis strings (len = M)
        references: Either a list of reference strings (len = M), or
                   a list of lists of references per hypothesis
        max_n: Maximum n-gram order (default: 4 for BLEU-4)
        smooth: Smoothing constant for zero-count n-grams (default: 1e-9)

    Returns:
        BLEU score as float in range [0, 1]

    Examples:
        >>> preds = ["the cat sat on the mat"]
        >>> refs = ["the cat is on the mat"]
        >>> score = compute_bleu(preds, refs)
        >>> 0.0 <= score <= 1.0
        True
    """
    # Normalize references input
    norm_refs: list[list[str]] = []
    if len(references) > 0 and isinstance(references[0], str):
        # single reference per hypothesis
        norm_refs = [[r] for r in references]  # type: ignore[list-item]
    else:
        norm_refs = references  # type: ignore

    if len(predictions) != len(norm_refs):
        raise ValueError("predictions and references length must match")

    precisions: list[float] = []
    for n in range(1, max_n + 1):
        num = 0
        den = 0
        for hyp, refs in zip(predictions, norm_refs, strict=False):
            htoks = _tokenize(hyp)
            hcounts = _ngram_counts(htoks, n)
            if not hcounts:
                continue
            # merge reference max counts
            ref_max: dict[tuple[str, ...], int] = {}
            for r in refs:
                rc = _ngram_counts(_tokenize(r), n)
                for k, v in rc.items():
                    ref_max[k] = max(ref_max.get(k, 0), v)
            # clipped counts
            clipped = 0
            total = 0
            for k, hv in hcounts.items():
                clipped += min(hv, ref_max.get(k, 0))
                total += hv
            num += clipped
            den += total
        precisions.append((num + smooth) / (max(1, den) + smooth))

    # geometric mean of precisions
    geo = math.exp(sum(math.log(p) for p in precisions) / max(1, len(precisions)))
    bp = compute_brevity_penalty(predictions, norm_refs, tokenize=_tokenize)
    return float(bp * geo)


# ============================================================================
# ROUGE-L Metric (consolidated from 4 implementations)
# ============================================================================


def compute_rouge_l(
    predictions: Sequence[str],
    references: Sequence[str],
) -> float:
    """
    Compute ROUGE-L F1 score (corpus-level).

    Implements ROUGE-L metric using Longest Common Subsequence (LCS).
    This is the canonical implementation consolidated from 4 duplicate implementations.

    Args:
        predictions: List of hypothesis strings (len = M)
        references: List of reference strings (len = M)

    Returns:
        ROUGE-L F1 score as float in range [0, 1]

    Examples:
        >>> preds = ["the cat sat on the mat"]
        >>> refs = ["the cat is on the mat"]
        >>> score = compute_rouge_l(preds, refs)
        >>> 0.0 <= score <= 1.0
        True
    """

    def lcs(a: list[str], b: list[str]) -> int:
        """Compute longest common subsequence length."""
        m, n = len(a), len(b)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(m):
            for j in range(n):
                if a[i] == b[j]:
                    dp[i + 1][j + 1] = dp[i][j] + 1
                else:
                    dp[i + 1][j + 1] = max(dp[i][j + 1], dp[i + 1][j])
        return dp[m][n]

    scores = []
    for h, r in zip(predictions, references, strict=False):
        ht, rt = _tokenize(h), _tokenize(r)
        if not ht or not rt:
            scores.append(0.0)
            continue
        lcs_len = lcs(ht, rt)
        prec = lcs_len / len(ht)
        rec = lcs_len / len(rt)
        denom = prec + rec if (prec + rec) > 0 else 1e-12
        f = 2 * prec * rec / denom
        scores.append(f)
    return float(sum(scores) / max(1, len(scores)))


# ============================================================================
# Perplexity Metric (consolidated from 3 implementations)
# ============================================================================


def compute_perplexity(
    logits_or_nll: Iterable[Any],
    targets: Iterable[int],
    *,
    from_logits: bool = True,
    ignore_index: int = -100,
    epsilon: float = 1e-12,
) -> float:
    """
    Compute perplexity from logits or NLL.

    This is the canonical implementation consolidated from 3 duplicate implementations.

    Args:
        logits_or_nll: Either logits (2D array-like) or NLL values (1D)
        targets: Target token indices (1D array-like)
        from_logits: If True, compute softmax→NLL. If False, use input as NLL directly.
        ignore_index: Index to ignore in loss computation (default: -100, standard HF value)
        epsilon: Numerical stability constant for log computation

    Returns:
        Perplexity as float (exp(cross_entropy_loss))

    Examples:
        >>> logits = [[1.0, 2.0], [2.0, 3.0]]
        >>> targets = [0, 1]
        >>> ppl = compute_perplexity(logits, targets, from_logits=True)
        >>> ppl > 0.0
        True
    """
    tgt = list(targets)
    if from_logits:
        logits_list = list(logits_or_nll)
        if not logits_list:
            raise ValueError("logit sequence is empty")
        if len(logits_list) != len(tgt):
            raise ValueError(
                f"logits and targets length mismatch: {len(logits_list)} vs {len(tgt)}"
            )

        valid_indices = [i for i, y in enumerate(tgt) if int(y) != ignore_index]
        if not valid_indices:
            raise ValueError("no valid target positions (all ignored)")

        try:
            import numpy as _np

            arr = _np.asarray(logits_list, dtype=float)
            if arr.ndim != 2:
                raise ValueError(f"logits must be 2D, got {arr.ndim}D")
            if arr.shape[0] != len(tgt):
                raise ValueError(f"logits batch mismatch: {arr.shape[0]} vs {len(tgt)}")

            max_vals = _np.max(arr, axis=1, keepdims=True)
            exp = _np.exp(arr - max_vals)
            probs = exp / _np.sum(exp, axis=1, keepdims=True)
            nll_values = []
            vocab = arr.shape[1]
            for idx in valid_indices:
                target = int(tgt[idx])
                if target < 0 or target >= vocab:
                    raise ValueError(f"target index {target} out of vocab range [0, {vocab})")
                prob = float(probs[idx, target])
                nll_values.append(-math.log(max(prob, epsilon)))
        except (ImportError, AttributeError):
            # Fallback to manual computation without numpy
            nll_values = []
            vocab = len(list(logits_list[0])) if logits_list else 0
            for idx in valid_indices:
                row = logits_list[idx]
                if not isinstance(row, Sequence):
                    raise ValueError("logits must be sequences of floats")
                values = list(float(x) for x in row)
                m = max(values)
                exps = [math.exp(v - m) for v in values]
                s = sum(exps)
                if s <= 0:
                    raise ValueError("softmax denominator non-positive")
                target = int(tgt[idx])
                if target < 0 or target >= vocab:
                    raise ValueError(f"target index {target} out of vocab range [0, {vocab})")
                prob = exps[target] / s
                nll_values.append(-math.log(max(prob, epsilon)))

        avg_nll = sum(nll_values) / len(nll_values) if nll_values else 0.0
    else:
        # Input is already NLL
        nll_list = list(logits_or_nll)
        if len(nll_list) != len(tgt):
            raise ValueError(f"NLL and targets length mismatch: {len(nll_list)} vs {len(tgt)}")
        valid_indices = [i for i, y in enumerate(tgt) if int(y) != ignore_index]
        if not valid_indices:
            raise ValueError("no valid target positions (all ignored)")
        valid_nll = [nll_list[i] for i in valid_indices]
        avg_nll = sum(valid_nll) / len(valid_nll) if valid_nll else 0.0

    try:
        return float(math.exp(avg_nll))
    except OverflowError:
        return float("inf")


# ============================================================================
# Token Accuracy Metric (consolidated from 2 implementations)
# ============================================================================


def compute_token_accuracy(
    logits: Any,
    targets: Any,
) -> float:
    """
    Compute token-level accuracy from logits and targets.

    This is the canonical implementation consolidated from 2 duplicate implementations.

    Args:
        logits: Logits tensor or array-like (shape: [batch_size, vocab_size])
        targets: Target token indices (shape: [batch_size])

    Returns:
        Accuracy as float in range [0, 1]

    Examples:
        >>> import numpy as np
        >>> logits = np.array([[1.0, 2.0], [2.0, 3.0]])
        >>> targets = np.array([0, 1])
        >>> acc = compute_token_accuracy(logits, targets)
        >>> 0.0 <= acc <= 1.0
        True
    """
    try:
        import torch

        if torch.is_tensor(logits) and torch.is_tensor(targets):
            preds = logits.argmax(dim=-1)
            correct = (preds == targets).float().sum().item()
            total = targets.numel()
            return float(correct / total) if total else 0.0
    except (ImportError, AttributeError):
        pass

    # Fallback to numpy/list-based computation
    import numpy as _np

    logits_arr = _np.asarray(logits)
    targets_arr = _np.asarray(targets)
    preds = _np.argmax(logits_arr, axis=-1)
    correct = _np.sum(preds == targets_arr).item()
    total = targets_arr.size
    return float(correct / total) if total else 0.0


# ============================================================================
# Classification Metrics (consolidated from 2 implementations)
# ============================================================================


def compute_accuracy(
    predictions: Sequence[int],
    targets: Sequence[int],
) -> float:
    """
    Compute accuracy for classification.

    Args:
        predictions: Predicted class indices
        targets: Ground truth class indices

    Returns:
        Accuracy as float in range [0, 1]
    """
    if len(predictions) != len(targets):
        raise ValueError("predictions and targets length mismatch")
    if len(predictions) == 0:
        return 0.0
    matches = sum(1 for p, t in zip(predictions, targets, strict=False) if p == t)
    return matches / len(predictions)


def _precision_recall_f(tp: int, fp: int, fn: int, beta: float = 1.0) -> float:
    """Compute precision, recall, and F-beta score."""
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    if precision + recall == 0:
        return 0.0
    beta_sq = beta**2
    return float((1 + beta_sq) * precision * recall / (beta_sq * precision + recall))


def compute_f1(
    predictions: Sequence[int],
    targets: Sequence[int],
    labels: Optional[Sequence[int]] = None,
    average: str = "micro",
) -> float:
    """
    Compute F1 score for classification.

    Args:
        predictions: Predicted class indices
        targets: Ground truth class indices
        labels: Classes to include (default: all classes in targets)
        average: One of "micro", "macro", "weighted"

    Returns:
        F1 score as float in range [0, 1]
    """
    if len(predictions) != len(targets):
        raise ValueError("predictions and targets length mismatch")
    if len(predictions) == 0:
        return 0.0

    if labels is None:
        labels = sorted(set(targets))

    if average == "micro":
        # Micro: TP, FP, FN across all classes
        tp = sum(1 for p, t in zip(predictions, targets, strict=False) if p == t and p in labels)
        fp = sum(1 for p, t in zip(predictions, targets, strict=False) if p != t and p in labels)
        fn = sum(1 for p, t in zip(predictions, targets, strict=False) if p != t and t in labels)
        return _precision_recall_f(tp, fp, fn)

    elif average == "macro":
        # Macro: unweighted mean of F1 per class
        scores = []
        for label in labels:
            tp = sum(
                1 for p, t in zip(predictions, targets, strict=False) if p == label and t == label
            )
            fp = sum(
                1 for p, t in zip(predictions, targets, strict=False) if p == label and t != label
            )
            fn = sum(
                1 for p, t in zip(predictions, targets, strict=False) if p != label and t == label
            )
            scores.append(_precision_recall_f(tp, fp, fn))
        return sum(scores) / len(scores) if scores else 0.0

    elif average == "weighted":
        # Weighted: weighted mean of F1 per class
        scores = []
        total = len(targets)
        for label in labels:
            tp = sum(
                1 for p, t in zip(predictions, targets, strict=False) if p == label and t == label
            )
            fp = sum(
                1 for p, t in zip(predictions, targets, strict=False) if p == label and t != label
            )
            fn = sum(
                1 for p, t in zip(predictions, targets, strict=False) if p != label and t == label
            )
            weight = sum(1 for t in targets if t == label) / total if total else 0.0
            scores.append(weight * _precision_recall_f(tp, fp, fn))
        return sum(scores) if scores else 0.0

    else:
        raise ValueError(f"invalid average: {average!r}")


def compute_classification_metrics(
    predictions: Sequence[int],
    targets: Sequence[int],
) -> dict[str, float]:
    """
    Compute all classification metrics (accuracy, F1 variants).

    Args:
        predictions: Predicted class indices
        targets: Ground truth class indices

    Returns:
        Dictionary with "accuracy", "f1_micro", "f1_macro" keys
    """
    return {
        "accuracy": compute_accuracy(predictions, targets),
        "f1_micro": compute_f1(predictions, targets, average="micro"),
        "f1_macro": compute_f1(predictions, targets, average="macro"),
    }


# ============================================================================
# Batch Metrics from Model Outputs
# ============================================================================


def batch_metrics_from_outputs(
    outputs: Any,
    batch: Any,
) -> dict[str, float]:
    """
    Derive common scalar metrics from model forward pass outputs.

    This is a unified interface for computing metrics from model outputs and batch data.
    Supports:
    - Loss → perplexity conversion
    - Logits → token accuracy
    - Text predictions/references → exact match, BLEU-1, ROUGE-1

    Args:
        outputs: Model output object (e.g., from HF transformers)
                 Expected attributes: loss, logits, predictions
        batch: Input batch data
               Expected keys: labels, references/targets/labels_text

    Returns:
        Dictionary of computed metrics
    """
    record: dict[str, float] = {}

    # Loss → perplexity
    loss = getattr(outputs, "loss", None)
    if loss is not None:
        try:
            loss_value = float(loss.item() if hasattr(loss, "item") else loss)
            record["loss"] = loss_value
            record["perplexity"] = compute_perplexity([loss_value], [0], from_logits=False)
        except (ValueError, TypeError, AttributeError):
            pass

    # Logits → token accuracy
    logits = getattr(outputs, "logits", None)
    labels = None
    if isinstance(batch, dict):
        labels = batch.get("labels")

    if logits is not None and labels is not None:
        try:
            import torch

            preds = torch.argmax(logits, dim=-1)
            target = labels
            if hasattr(target, "to") and getattr(target, "device", None) != preds.device:
                target = target.to(preds.device)
            common = min(preds.shape[-1], target.shape[-1])
            if common > 0:
                # Create mask to ignore -100 labels (standard ignore_index)
                mask = target[..., :common] != -100
                if mask.any():
                    masked_preds = preds[..., :common][mask]
                    masked_target = target[..., :common][mask]
                    accuracy_tensor = (masked_preds == masked_target).float()
                    record["token_accuracy"] = float(accuracy_tensor.mean().item())
                else:
                    record["token_accuracy"] = 0.0
        except (ImportError, ValueError, TypeError, AttributeError, RuntimeError):
            pass

    # Text predictions/references → exact match, BLEU-1, ROUGE-1
    text_preds = getattr(outputs, "predictions", None)
    if text_preds is None and isinstance(batch, dict):
        text_preds = batch.get("predictions")

    # Normalize to list of strings
    if text_preds is not None:
        if isinstance(text_preds, str):
            text_preds = [text_preds]
        elif not isinstance(text_preds, Sequence) or isinstance(text_preds, (str, bytes)):
            try:
                text_preds = list(text_preds)
            except (TypeError, ValueError):
                text_preds = None

    text_refs = None
    if isinstance(batch, dict):
        for key in ("references", "targets", "labels_text"):
            ref_value = batch.get(key)
            if ref_value is not None:
                if isinstance(ref_value, str):
                    text_refs = [ref_value]
                elif isinstance(ref_value, Sequence) and not isinstance(ref_value, (str, bytes)):
                    try:
                        text_refs = list(ref_value)
                    except (TypeError, ValueError):
                        pass
                if text_refs:
                    break

    if text_preds and text_refs and len(text_preds) == len(text_refs):
        try:
            # Exact match
            exact_matches = sum(
                1
                for p, r in zip(text_preds, text_refs, strict=False)
                if str(p).strip() == str(r).strip()
            )
            record["exact_match"] = exact_matches / len(text_preds)

            # BLEU-1 (simplified unigram overlap)
            bleu1_scores = []
            for pred, ref in zip(text_preds, text_refs, strict=False):
                pred_tokens = _tokenize(str(pred))
                ref_tokens = _tokenize(str(ref))
                if pred_tokens and ref_tokens:
                    overlap = len(set(pred_tokens) & set(ref_tokens))
                    precision = overlap / len(pred_tokens)
                    brevity = (
                        1.0
                        if len(pred_tokens) >= len(ref_tokens)
                        else len(pred_tokens) / len(ref_tokens)
                    )
                    bleu1_scores.append(brevity * precision)
                else:
                    bleu1_scores.append(0.0)
            record["bleu1"] = sum(bleu1_scores) / len(bleu1_scores) if bleu1_scores else 0.0

            # ROUGE-1 (F1)
            rouge1_scores = []
            for pred, ref in zip(text_preds, text_refs, strict=False):
                pred_tokens = set(_tokenize(str(pred)))  # type: ignore[assignment]
                ref_tokens = set(_tokenize(str(ref)))  # type: ignore[assignment]
                if pred_tokens and ref_tokens:
                    overlap = len(pred_tokens & ref_tokens)  # type: ignore[operator]
                    precision = overlap / len(pred_tokens)
                    recall = overlap / len(ref_tokens)
                    if precision + recall > 0:
                        f1 = 2 * precision * recall / (precision + recall)
                        rouge1_scores.append(f1)
                    else:
                        rouge1_scores.append(0.0)
                else:
                    rouge1_scores.append(0.0)
            record["rouge1"] = sum(rouge1_scores) / len(rouge1_scores) if rouge1_scores else 0.0
        except (ValueError, TypeError, AttributeError):
            pass

    return record
