"""Utilities for running evaluation loops during training."""

from __future__ import annotations

from typing import Callable, Dict, Iterable, Mapping, MutableMapping, Optional

try:  # pragma: no cover - torch optional in tests
    import torch
except Exception:  # pragma: no cover - torch optional in tests
    torch = None  # type: ignore[assignment]


def _move_batch_to_device(batch: Mapping[str, object], device: object) -> Mapping[str, object]:
    if device is None:
        return batch
    moved: Dict[str, object] = {}
    for key, value in batch.items():
        if hasattr(value, "to"):
            try:
                moved[key] = value.to(device)
                continue
            except Exception:
                pass
        moved[key] = value
    return moved


def evaluate(
    model,
    dataloader: Iterable[Mapping[str, object]],
    *,
    loss_fn: Callable[[object, Mapping[str, object]], object],
    metrics_fn: Optional[
        Callable[[object, Mapping[str, object]], MutableMapping[str, float]]
    ] = None,
    device: object | None = None,
) -> Dict[str, float]:
    """Run a lightweight evaluation loop and return averaged metrics."""

    training_mode = getattr(model, "training", True)
    if torch is not None:
        ctx = torch.no_grad()
    else:  # pragma: no cover - torch optional
        from contextlib import nullcontext

        ctx = nullcontext()

    model.eval()
    totals: Dict[str, float] = {}
    batches = 0

    try:
        with ctx:
            for batch in dataloader:
                batches += 1
                batch_for_device = (
                    _move_batch_to_device(batch, device) if isinstance(batch, Mapping) else batch
                )
                outputs = model(**batch_for_device)
                loss = loss_fn(outputs, batch_for_device)
                loss_value = float(loss.item()) if hasattr(loss, "item") else float(loss)
                totals["eval_loss"] = totals.get("eval_loss", 0.0) + loss_value

                if metrics_fn is not None:
                    try:
                        metrics = metrics_fn(outputs, batch_for_device)
                    except Exception:
                        metrics = {}
                    for key, value in metrics.items():
                        totals[key] = totals.get(key, 0.0) + float(value)
    finally:
        if hasattr(model, "train"):
            model.train(training_mode)

    if batches == 0:
        return {key: 0.0 for key in totals}
    return {key: value / batches for key, value in totals.items()}


__all__ = ["evaluate"]
