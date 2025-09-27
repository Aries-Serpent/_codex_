"""Lightweight evaluation helpers for batch metrics.

This module intentionally keeps dependencies minimal while providing
basic metrics that are commonly required across training and evaluation
workflows.  It focuses on torch-based causal language modelling tasks
where labels may be masked with ``-100`` (the default ignore index used
by PyTorch).
"""

from __future__ import annotations

import math
from typing import Dict, Iterable, Sequence

try:  # pragma: no cover - optional dependency
    import torch
except Exception:  # pragma: no cover - torch may be unavailable in minimal envs
    torch = None  # type: ignore[assignment]
    _HAS_TORCH = False
else:
    _HAS_TORCH = True


def _token_accuracy_from_logits(
    logits: torch.Tensor,
    labels: torch.Tensor,
    *,
    ignore_index: int = -100,
) -> float:
    """Compute token-level accuracy ignoring masked labels.

    Args:
        logits: Model logits with shape ``(..., vocab_size)``.
        labels: Target token ids matching ``logits`` without the final
            vocabulary dimension.
        ignore_index: Label value used to mark tokens that should be
            excluded from accuracy calculations (defaults to ``-100``).

    Returns:
        Accuracy as a floating-point value in ``[0.0, 1.0]``.  When no
        unmasked labels are present the function returns ``0.0``.
    """

    if not _HAS_TORCH or torch is None:
        raise ImportError("PyTorch is required for token accuracy computation")

    if logits.ndim == labels.ndim:
        # Align shapes when ``logits`` already squeezed by the caller.
        logits = logits.unsqueeze(-1)
    preds = logits.argmax(dim=-1)
    mask = labels.ne(ignore_index)
    total = mask.sum().item()
    if total == 0:
        return 0.0
    correct = preds.eq(labels).masked_select(mask).float().sum().item()
    return float(correct / total)


def _f1_em(pred: str, ref: str) -> Dict[str, float]:
    """Compute whitespace token F1 and exact match."""

    pred_tokens = pred.split()
    ref_tokens = ref.split()
    pred_set = set(pred_tokens)
    ref_set = set(ref_tokens)
    overlap = len(pred_set & ref_set)
    precision = overlap / max(len(pred_tokens), 1)
    recall = overlap / max(len(ref_tokens), 1)
    f1 = 0.0 if precision + recall == 0 else (2 * precision * recall) / (precision + recall)
    em = 1.0 if pred.strip() == ref.strip() else 0.0
    return {"f1": float(f1), "exact_match": float(em)}


def _resolve_text_pairs(
    predictions: Iterable[str] | str | None,
    references: Iterable[str] | str | None,
) -> Sequence[tuple[str, str]]:
    if predictions is None or references is None:
        return []
    if isinstance(predictions, str) and isinstance(references, str):
        return [(predictions, references)]
    if isinstance(predictions, Iterable) and isinstance(references, Iterable):
        pairs = []
        for pred, ref in zip(predictions, references):
            if pred is None or ref is None:
                continue
            pairs.append((str(pred), str(ref)))
        return pairs
    return []


def batch_metrics(outputs, batch, *, tokenizer=None) -> Dict[str, float]:
    """Compute minimal metrics for a batch of model outputs.

    Parameters
    ----------
    outputs:
        Object returned by the model.  The function expects ``loss`` and
        ``logits`` attributes (or dict keys) but guards against their
        absence.  ``logits`` should be a :class:`torch.Tensor`.
    batch:
        Input batch passed to the model, typically a mapping containing
        ``labels`` with masked tokens.
    tokenizer:
        Reserved for future use; accepted for signature compatibility.

    Returns
    -------
    Dict[str, float]
        Dictionary containing available metrics.  Always attempts to
        return ``loss`` and ``perplexity`` if a scalar loss is present,
        ``token_accuracy`` when logits and labels are provided, and
        optional ``f1``/``exact_match`` scores for string targets.
    """

    if not _HAS_TORCH or torch is None:
        raise ImportError("PyTorch is required for batch metric computation")

    metrics: Dict[str, float] = {}

    loss = getattr(outputs, "loss", None)
    if isinstance(outputs, dict):  # support HF-like output dicts
        loss = outputs.get("loss", loss)
    if loss is not None:
        try:
            value = float(torch.as_tensor(loss).detach().cpu().item())
            metrics["loss"] = value
            metrics["perplexity"] = float(math.exp(value))
        except Exception:
            pass

    logits = getattr(outputs, "logits", None)
    if isinstance(outputs, dict):
        logits = outputs.get("logits", logits)
    labels = None
    if isinstance(batch, dict):
        labels = batch.get("labels")
    if logits is not None and isinstance(labels, torch.Tensor):
        try:
            metrics["token_accuracy"] = _token_accuracy_from_logits(
                torch.as_tensor(logits).detach(),
                torch.as_tensor(labels).detach(),
            )
        except Exception:
            pass

    if isinstance(batch, dict):
        pred_text = batch.get("pred_text")
        target_text = batch.get("target_text")
    else:
        pred_text = target_text = None

    for pred, ref in _resolve_text_pairs(pred_text, target_text):
        metrics.setdefault("f1", 0.0)
        metrics.setdefault("exact_match", 0.0)
        scores = _f1_em(pred, ref)
        metrics["f1"] += scores["f1"]
        metrics["exact_match"] += scores["exact_match"]
    if "f1" in metrics and isinstance(batch, dict):
        pairs = _resolve_text_pairs(pred_text, target_text)
        if pairs:
            count = float(len(pairs))
            metrics["f1"] /= count
            metrics["exact_match"] /= count
        else:
            metrics.pop("f1", None)
            metrics.pop("exact_match", None)

    return metrics


__all__ = ["batch_metrics"]
