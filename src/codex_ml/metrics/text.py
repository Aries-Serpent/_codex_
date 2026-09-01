"""
Text Module

This module provides functionality for text.

Usage:
    from metrics.text import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import torch

try:  # pragma: no cover - optional dependency
    import torch as _torch

    # Verify torch is functional
    _ = _torch.Tensor
except (ImportError, AttributeError):  # pragma: no cover - torch may be unavailable in minimal envs
    _torch = None
    _HAS_TORCH = False
else:
    _HAS_TORCH = True

__all__ = ["perplexity", "token_accuracy"]


def token_accuracy(logits: torch.Tensor, targets: torch.Tensor) -> float:
    """Compute token-level accuracy given logits and target ids."""

    if not _HAS_TORCH or _torch is None:
        raise ImportError("PyTorch is required for token_accuracy")
    preds = logits.argmax(dim=-1)
    correct = (preds == targets).float().sum().item()
    total = targets.numel()
    return float(correct / total) if total else 0.0


def perplexity(loss: float) -> float:
    """Convert cross-entropy loss to perplexity."""
    try:
        return float(math.exp(loss))
    except OverflowError:  # pragma: no cover
        return float("inf")
