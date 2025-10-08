"""Common evaluation metrics for language modelling and classification."""

from __future__ import annotations

import math
from typing import Iterable, Sequence


def accuracy(preds: Iterable[int], labels: Iterable[int]) -> float:
    """Return the fraction of matching elements between ``preds`` and ``labels``."""

    preds_seq: Sequence[int] = list(preds)
    labels_seq: Sequence[int] = list(labels)
    total = max(1, len(labels_seq))
    correct = sum(int(pred == label) for pred, label in zip(preds_seq, labels_seq))
    return correct / total


def perplexity(loss: float) -> float:
    """Compute perplexity from a scalar negative log-likelihood ``loss``."""

    return math.exp(loss)
