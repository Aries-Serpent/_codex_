from __future__ import annotations

import math

try:  # pragma: no cover - optional dependency
    import torch
except Exception:  # pragma: no cover - torch may be unavailable in minimal envs
    torch = None  # type: ignore[assignment]
    _HAS_TORCH = False
else:
    _HAS_TORCH = True

__all__ = ["token_accuracy", "perplexity"]


def token_accuracy(logits: torch.Tensor, targets: torch.Tensor) -> float:
    """Compute token-level accuracy given logits and target ids."""

    if not _HAS_TORCH or torch is None:
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
