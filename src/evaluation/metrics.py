"""Basic evaluation metrics used in training/evaluation loops."""

from __future__ import annotations

import math

import torch
import torch.nn.functional as functional


def accuracy(logits: torch.Tensor, targets: torch.Tensor) -> float:
    """Return top-1 accuracy for classification logits."""

    preds = torch.argmax(logits, dim=-1)
    return float((preds == targets).float().mean().item())


def cross_entropy(logits: torch.Tensor, targets: torch.Tensor) -> float:
    """Compute mean cross-entropy loss."""

    return float(functional.cross_entropy(logits, targets).item())


def perplexity(loss: float) -> float:
    """Convert an average loss value into perplexity."""

    return float(math.exp(min(50.0, max(-50.0, loss))))
