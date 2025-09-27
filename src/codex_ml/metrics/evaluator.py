"""Best-effort scalar metrics computed from model outputs."""

from __future__ import annotations

from typing import Dict, Mapping

try:  # pragma: no cover - torch optional in tests
    import torch
except Exception:  # pragma: no cover - torch optional in tests
    torch = None  # type: ignore[assignment]


def _safe_float(value: object) -> float:
    try:
        if hasattr(value, "item"):
            return float(value.item())  # type: ignore[arg-type]
        return float(value)  # type: ignore[arg-type]
    except Exception:
        return 0.0


def _perplexity(avg_loss: float) -> float:
    try:
        import math

        return float(math.exp(avg_loss))
    except Exception:
        return float("inf")


def batch_metrics(outputs: object, batch: Mapping[str, object] | object) -> Dict[str, float]:
    """Derive common scalar metrics from a batch forward pass."""

    record: Dict[str, float] = {}

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
            common = min(preds.shape[-1], target.shape[-1])  # type: ignore[arg-type]
            if common > 0:
                accuracy_tensor = (preds[..., :common] == target[..., :common]).float()
                record["token_accuracy"] = float(accuracy_tensor.mean().item())
        except Exception:
            pass

    return record


__all__ = ["batch_metrics"]
