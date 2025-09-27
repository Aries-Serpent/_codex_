"""Minimal evaluation utilities for functional training loops."""

from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, Optional, Sequence

try:  # pragma: no cover - optional dependency
    import torch
except Exception:  # pragma: no cover - torch may be unavailable in minimal envs
    torch = None  # type: ignore[assignment]
    _HAS_TORCH = False
else:
    _HAS_TORCH = True


Batch = Dict[str, Any] | Sequence[Any] | Any


def _to_device(value, device: torch.device):
    if hasattr(value, "to"):
        try:
            return value.to(device)
        except Exception:
            return value
    if isinstance(value, (list, tuple)):
        return type(value)(_to_device(item, device) for item in value)
    return value


def _prepare_batch(batch: Batch, device: torch.device) -> Batch:
    if isinstance(batch, dict):
        return {k: _to_device(v, device) for k, v in batch.items()}
    if isinstance(batch, (list, tuple)):
        return type(batch)(_to_device(v, device) for v in batch)
    return _to_device(batch, device)


def _call_model(model, batch: Batch):
    if isinstance(batch, dict):
        return model(**batch)
    if isinstance(batch, (list, tuple)):
        return model(*batch)
    return model(batch)


def evaluate(
    model,
    dataloader: Iterable[Batch],
    loss_fn: Callable,
    *,
    device: str | torch.device = "cpu",
    metrics_fn: Optional[Callable[[object, Batch], Dict[str, float]]] = None,
) -> Dict[str, float]:
    """Run evaluation over ``dataloader`` aggregating metrics per batch.

    Parameters
    ----------
    model:
        Model with ``eval``/``train`` methods following the torch API.
    dataloader:
        Iterable yielding batches compatible with ``model``'s forward
        method.  Batches may be dictionaries, sequences or tensors.
    loss_fn:
        Callable returning the loss tensor when invoked as
        ``loss_fn(outputs, batch)``.  If it returns ``None`` the loss is
        skipped.
    device:
        Target device for tensors.  Accepts either a string or
        :class:`torch.device`.
    metrics_fn:
        Optional callable invoked per batch with ``(outputs, batch)``
        expected to return a mapping of metric names to floats.
    """

    if not _HAS_TORCH or torch is None:
        raise ImportError("PyTorch is required for evaluation")

    try:
        target_device = torch.device(device)
    except (TypeError, ValueError):
        target_device = torch.device("cpu")

    was_training = getattr(model, "training", False)
    if hasattr(model, "eval"):
        model.eval()

    sums: Dict[str, float] = {}
    steps = 0

    with torch.no_grad():
        for raw_batch in dataloader:
            prepared = _prepare_batch(raw_batch, target_device)
            outputs = _call_model(model, prepared)

            loss_value = None
            try:
                loss_value = loss_fn(outputs, prepared)
            except Exception:
                loss_value = None
            if loss_value is not None:
                try:
                    loss_float = float(torch.as_tensor(loss_value).detach().cpu().item())
                    sums["eval_loss"] = sums.get("eval_loss", 0.0) + loss_float
                except Exception:
                    pass

            if callable(metrics_fn):
                try:
                    metrics = metrics_fn(outputs, prepared)
                except Exception:
                    metrics = None
                if isinstance(metrics, dict):
                    for key, value in metrics.items():
                        try:
                            sums[key] = sums.get(key, 0.0) + float(value)
                        except Exception:
                            continue

            steps += 1

    if was_training and hasattr(model, "train"):
        model.train(True)

    if steps == 0 or not sums:
        return {}

    denom = float(max(steps, 1))
    return {key: value / denom for key, value in sums.items()}


__all__ = ["evaluate"]
