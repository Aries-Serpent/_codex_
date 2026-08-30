"""
Metrics Module

This module provides functionality for metrics.

Usage:
    from evaluation.metrics import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping, Sequence

import torch
import torch.nn.functional as F


def accuracy(logits: torch.Tensor, targets: torch.Tensor) -> float:
    preds = torch.argmax(logits, dim=-1)
    return float((preds == targets).float().mean().item())


def precision_recall_f1(logits: torch.Tensor, targets: torch.Tensor) -> tuple[float, float, float]:
    """Return precision, recall and F1 for single-label classification.

    The metrics are computed for the positive class (label ``1``). When there are
    no predicted or true positives, the corresponding metric is reported as
    ``0.0`` to avoid division errors.

    Binary classifiers sometimes emit a single logit or probability per example
    (``(batch,)`` or ``(batch, 1)`` shaped tensors). In those cases we predict the
    positive class when the value is at least ``0`` for logits or ``0.5`` for
    probabilities. For multi-class logits we fall back to ``argmax`` based
    predictions.
    """

    if logits.ndim == 1 or (logits.ndim > 1 and logits.shape[-1] == 1):
        logits_1d = logits.squeeze(-1)

        if logits_1d.dtype.is_floating_point and torch.all((logits_1d >= 0.0) & (logits_1d <= 1.0)):
            preds = (logits_1d >= 0.5).to(targets.dtype)
        else:
            preds = (logits_1d >= 0).to(targets.dtype)
    else:
        preds = torch.argmax(logits, dim=-1)

    positives = targets == 1
    predicted_positives = preds == 1

    tp = torch.logical_and(predicted_positives, positives).sum().item()
    fp = torch.logical_and(predicted_positives, torch.logical_not(positives)).sum().item()
    fn = torch.logical_and(torch.logical_not(predicted_positives), positives).sum().item()

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    return float(precision), float(recall), float(f1)


def cross_entropy(logits: torch.Tensor, targets: torch.Tensor) -> float:
    return float(F.cross_entropy(logits, targets).item())  # type: ignore[misc]


def perplexity(loss: float) -> float:
    # exp of mean loss; clamp for stability
    return float(math.exp(min(50.0, max(-50.0, loss))))


class MetricsAggregator:
    """Aggregate metric functions and return flat dictionaries of results."""

    def __init__(
        self,
        *metric_fns: Callable[
            [torch.Tensor, torch.Tensor],
            float | tuple[float, ...] | Mapping[str, float],
        ],
    ) -> None:
        self._metric_fns = metric_fns

    def __call__(self, logits: torch.Tensor, targets: torch.Tensor) -> dict[str, float]:
        results: dict[str, float] = {}
        for metric_fn in self._metric_fns:
            name = getattr(metric_fn, "__name__", metric_fn.__class__.__name__)
            value = metric_fn(logits, targets)

            if isinstance(value, Mapping):
                for key, val in value.items():
                    results[str(key)] = float(val)
                continue

            if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
                for idx, val in enumerate(value):
                    results[f"{name}_{idx}"] = float(val)
                continue

            results[name] = float(value)

        return results
