"""Best-effort scalar metrics computed from model outputs."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

from collections import Counter  # noqa: E402
from collections.abc import Iterable, Mapping  # noqa: E402

try:  # pragma: no cover - torch optional in tests
    import torch
except (ImportError, AttributeError):  # pragma: no cover - torch optional in tests
    torch = None


def _safe_float(value: object) -> float:
    try:
        if hasattr(value, "item"):
            return float(value.item())
        return float(value)  # type: ignore[arg-type]
    except (ImportError, AttributeError):
        logger.warning("Exception occurred", exc_info=True)
        return 0.0


def _perplexity(avg_loss: float) -> float:
    try:
        import math

        return float(math.exp(avg_loss))
    except (ImportError, AttributeError):
        logger.warning("Exception occurred", exc_info=True)
        return float("inf")


def _as_str_list(candidate: object) -> list[str] | None:
    if candidate is None:
        return None
    if isinstance(candidate, str):
        return [candidate]
    if isinstance(candidate, Iterable) and not isinstance(candidate, Mapping):
        values: list[str] = []
        for item in candidate:
            if item is None:
                continue
            values.append(str(item))
        return values or None
    return None


def _unigram_overlap(pred: Iterable[str], ref: Iterable[str]) -> tuple[int, int, int]:
    pred_counts = Counter(pred)
    ref_counts = Counter(ref)
    overlap = sum((pred_counts & ref_counts).values())
    return overlap, sum(pred_counts.values()), sum(ref_counts.values())


def _exact_match(preds: list[str], refs: list[str]) -> float:
    total = min(len(preds), len(refs))
    if total == 0:
        return 0.0
    matches = sum(1 for p, r in zip(preds, refs, strict=False) if p == r)
    return matches / total


def _bleu1(preds: list[str], refs: list[str]) -> float:
    if not preds or not refs:
        return 0.0
    scores: list[float] = []
    for pred, ref in zip(preds, refs, strict=False):
        pred_tokens = pred.split()
        ref_tokens = ref.split()
        overlap, pred_total, ref_total = _unigram_overlap(pred_tokens, ref_tokens)
        if pred_total == 0:
            scores.append(0.0)
            continue
        precision = overlap / pred_total
        brevity_penalty = (
            1.0 if pred_total > ref_total else (pred_total / ref_total) if ref_total else 0.0
        )
        scores.append(brevity_penalty * precision)
    return float(sum(scores) / len(scores))


def _rouge1_f1(preds: list[str], refs: list[str]) -> float:
    if not preds or not refs:
        return 0.0
    scores: list[float] = []
    for pred, ref in zip(preds, refs, strict=False):
        pred_tokens = pred.split()
        ref_tokens = ref.split()
        overlap, pred_total, ref_total = _unigram_overlap(pred_tokens, ref_tokens)
        if overlap == 0:
            scores.append(0.0)
            continue
        precision = overlap / pred_total if pred_total else 0.0
        recall = overlap / ref_total if ref_total else 0.0
        if precision + recall == 0:
            scores.append(0.0)
        else:
            scores.append(2 * precision * recall / (precision + recall))
    return float(sum(scores) / len(scores))


def batch_metrics(outputs: object, batch: Mapping[str, object] | object) -> dict[str, float]:
    """Derive common scalar metrics from a batch forward pass."""

    record: dict[str, float] = {}

    loss = getattr(outputs, "loss", None)
    if loss is not None:
        loss_value = _safe_float(loss)
        record["loss"] = loss_value
        record["perplexity"] = _perplexity(loss_value)

    logits = getattr(outputs, "logits", None)
    labels = None
    if isinstance(batch, Mapping):
        labels = batch.get("labels")

    if torch is not None and logits is not None and labels is not None:
        try:
            preds = torch.argmax(logits, dim=-1)
            target = labels
            if hasattr(target, "to") and getattr(target, "device", None) != preds.device:
                target = target.to(preds.device)
            common = min(preds.shape[-1], target.shape[-1])  # type: ignore[union-attr]
            if common > 0:
                # Create mask to ignore -100 labels (standard ignore_index)
                mask = target[..., :common] != -100  # type: ignore[index]
                if mask.any():
                    masked_preds = preds[..., :common][mask]
                    masked_target = target[..., :common][mask]  # type: ignore[index]
                    accuracy_tensor = (masked_preds == masked_target).float()
                    record["token_accuracy"] = float(accuracy_tensor.mean().item())
                else:
                    record["token_accuracy"] = 0.0
        except (ValueError, TypeError, RuntimeError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.warning("Exception: <ERROR_TYPE>", exc_info=True)

    text_preds = _as_str_list(getattr(outputs, "predictions", None))
    if text_preds is None and isinstance(outputs, Mapping):
        text_preds = _as_str_list(outputs.get("predictions"))
    text_refs = None
    if isinstance(batch, Mapping):
        for key in ("references", "targets", "labels_text"):
            text_refs = _as_str_list(batch.get(key))
            if text_refs:
                break

    if text_preds and text_refs:
        record["exact_match"] = _exact_match(text_preds, text_refs)
        record["bleu1"] = _bleu1(text_preds, text_refs)
        record["rouge1"] = _rouge1_f1(text_preds, text_refs)

    return record


__all__ = ["batch_metrics"]
