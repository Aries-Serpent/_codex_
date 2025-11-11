"""
Minimal metrics utilities used by evaluation/configs.

Exposed callables can be referenced via entrypoint strings like:
  "codex_ml.metrics:accuracy"
"""
from __future__ import annotations
import torch

def accuracy(logits: "torch.Tensor", targets: "torch.Tensor") -> "torch.Tensor":
    """
    Compute classification accuracy from logits and integer targets.
    """
    if logits.ndim == 2:
        preds = logits.argmax(dim=-1)
    else:
        preds = logits
    return (preds == targets).float().mean()