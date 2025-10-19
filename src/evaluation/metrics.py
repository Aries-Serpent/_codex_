from __future__ import annotations

import math
from collections.abc import Callable, Mapping

import torch
import torch.nn.functional as F


def accuracy(logits: torch.Tensor, targets: torch.Tensor) -> float:
    preds = torch.argmax(logits, dim=-1)
    return float((preds == targets).float().mean().item())


def precision_recall_f1(logits: torch.Tensor, targets: torch.Tensor) -> tuple[float, float, float]:
    """Compute precision, recall and F1 for single-label binary classification.

    The metrics are computed for the positive class (label ``1``). When there are
    no predicted or true positives, the corresponding metric is reported as
    ``0.0`` to avoid division errors.
    """

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
    return float(F.cross_entropy(logits, targets).item())


def perplexity(loss: float) -> float:
    # exp of mean loss; clamp for stability
    return float(math.exp(min(50.0, max(-50.0, loss))))


class MetricsAggregator:
    """Aggregate metric functions and return flat dictionaries of results."""

    def __init__(
        self,
        *metric_fns: Callable[
            [torch.Tensor, torch.Tensor], float | tuple[float, ...] | Mapping[str, float]
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

            if isinstance(value, tuple):
                for idx, val in enumerate(value):
                    results[f"{name}_{idx}"] = float(val)
                continue

            results[name] = float(value)

        return results
