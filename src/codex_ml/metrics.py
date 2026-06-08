"""
Minimal metrics utilities used by evaluation/configs.

Exposed callables can be referenced via entrypoint strings like:
  "codex_ml.metrics:accuracy"
"""

from __future__ import annotations

import torch


def accuracy(logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
    """
    Compute classification accuracy from logits and integer targets.
    """
    preds = logits.argmax(dim=-1) if logits.ndim == 2 else logits
    return (preds == targets).float().mean()


def precision(preds: list | torch.Tensor, targets: list | torch.Tensor) -> float:
    """
    Compute binary classification precision.
    """
    if isinstance(preds, list):
        preds = torch.tensor(preds)
    if isinstance(targets, list):
        targets = torch.tensor(targets)

    true_positives = ((preds == 1) & (targets == 1)).sum().item()
    predicted_positives = (preds == 1).sum().item()

    if predicted_positives == 0:
        return 0.0
    return true_positives / predicted_positives


def recall(preds: list | torch.Tensor, targets: list | torch.Tensor) -> float:
    """
    Compute binary classification recall.
    """
    if isinstance(preds, list):
        preds = torch.tensor(preds)
    if isinstance(targets, list):
        targets = torch.tensor(targets)

    true_positives = ((preds == 1) & (targets == 1)).sum().item()
    actual_positives = (targets == 1).sum().item()

    if actual_positives == 0:
        return 0.0
    return true_positives / actual_positives


def f1_score(preds: list | torch.Tensor, targets: list | torch.Tensor) -> float:
    """
    Compute binary classification F1 score.
    """
    prec = precision(preds, targets)
    rec = recall(preds, targets)

    if prec + rec == 0:
        return 0.0
    return 2 * (prec * rec) / (prec + rec)


def perplexity(logits: torch.Tensor, targets: torch.Tensor) -> float:
    """
    Compute perplexity from logits and targets.
    """
    import torch.nn.functional as F

    loss = F.cross_entropy(logits, targets)
    return torch.exp(loss).item()


def token_accuracy(logits: torch.Tensor, targets: torch.Tensor) -> float:
    """
    Compute token-level accuracy.
    """
    preds = logits.argmax(dim=-1)
    return (preds == targets).float().mean().item()


def mean_absolute_error(preds: torch.Tensor, targets: torch.Tensor) -> float:
    """
    Compute mean absolute error.
    """
    import torch.nn.functional as F

    return F.l1_loss(preds.float(), targets.float()).item()


__all__ = [
    "accuracy",
    "f1_score",
    "mean_absolute_error",
    "perplexity",
    "precision",
    "recall",
    "token_accuracy",
]
