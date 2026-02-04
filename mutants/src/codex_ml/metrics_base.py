"""Binary classification metrics used across Codex evaluations."""

from __future__ import annotations

import math
from collections.abc import Iterable, Sequence


def accuracy(preds: Iterable[int], labels: Iterable[int]) -> float:
    """Return the fraction of matching elements between ``preds`` and ``labels``."""

    preds_seq: Sequence[int] = list(preds)
    labels_seq: Sequence[int] = list(labels)
    total = max(1, len(labels_seq))
    correct = sum(int(pred == label) for pred, label in zip(preds_seq, labels_seq, strict=False))
    return correct / total


def perplexity(loss: float) -> float:
    """Compute perplexity from a scalar negative log-likelihood ``loss``."""

    return math.exp(loss)


def precision(preds: Iterable[int], labels: Iterable[int]) -> float:
    """Compute precision for binary classification."""

    preds_seq = [int(bool(value)) for value in preds]
    labels_seq = [int(bool(value)) for value in labels]
    true_positive = sum(
        1 for pred, label in zip(preds_seq, labels_seq, strict=False) if pred == 1 and label == 1
    )
    predicted_positive = sum(preds_seq)
    if predicted_positive == 0:
        return 0.0
    return true_positive / predicted_positive


def recall(preds: Iterable[int], labels: Iterable[int]) -> float:
    """Compute recall for binary classification."""

    preds_seq = [int(bool(value)) for value in preds]
    labels_seq = [int(bool(value)) for value in labels]
    true_positive = sum(
        1 for pred, label in zip(preds_seq, labels_seq, strict=False) if pred == 1 and label == 1
    )
    actual_positive = sum(labels_seq)
    if actual_positive == 0:
        return 0.0
    return true_positive / actual_positive


def f1_score(preds: Iterable[int], labels: Iterable[int]) -> float:
    """Compute the F1 score for binary classification."""

    prec = precision(preds, labels)
    rec = recall(preds, labels)
    denom = prec + rec
    if denom == 0:
        return 0.0
    return 2 * prec * rec / denom


__all__ = ["accuracy", "perplexity", "precision", "recall", "f1_score"]
