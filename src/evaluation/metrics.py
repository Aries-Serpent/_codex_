from __future__ import annotations

import math

import torch
import torch.nn.functional as F


def accuracy(logits: torch.Tensor, targets: torch.Tensor) -> float:
    preds = torch.argmax(logits, dim=-1)
    return float((preds == targets).float().mean().item())


def cross_entropy(logits: torch.Tensor, targets: torch.Tensor) -> float:
    return float(F.cross_entropy(logits, targets).item())


def perplexity(loss: float) -> float:
    # exp of mean loss; clamp for stability
    return float(math.exp(min(50.0, max(-50.0, loss))))
