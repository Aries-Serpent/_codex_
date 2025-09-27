from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, Mapping


def evaluate(
    model: Any,
    dataloader: Iterable[Any],
    loss_fn: Callable[[Any, Mapping[str, Any]], Any] | None = None,
    *,
    device: Any | None = None,
) -> Dict[str, float]:
    """Run a minimal evaluation loop returning the average loss."""

    try:
        import torch
    except Exception as exc:  # pragma: no cover - torch is an optional dependency
        raise RuntimeError("evaluate requires PyTorch to be installed") from exc

    was_training = getattr(model, "training", False)
    if hasattr(model, "eval"):
        model.eval()

    resolved_device = device
    if resolved_device is None:
        resolved_device = getattr(model, "device", None)
    if resolved_device is None and hasattr(model, "parameters"):
        try:
            first_param = next(model.parameters())  # type: ignore[attr-defined]
        except StopIteration:
            first_param = None
        except Exception:  # pragma: no cover - models without parameters
            first_param = None
        if first_param is not None:
            resolved_device = getattr(first_param, "device", None)

    if resolved_device is not None and not isinstance(resolved_device, torch.device):
        resolved_device = torch.device(resolved_device)

    total_loss = 0.0
    steps = 0

    with torch.no_grad():
        for batch in dataloader:
            if isinstance(batch, Mapping):
                batch_mapping = batch
            elif isinstance(batch, (list, tuple)) and batch and isinstance(batch[0], Mapping):
                batch_mapping = batch[0]
            else:
                continue

            prepared: Dict[str, Any] = {}
            for key, value in batch_mapping.items():
                if resolved_device is not None and hasattr(value, "to"):
                    prepared[key] = value.to(resolved_device)
                else:
                    prepared[key] = value

            outputs = model(**prepared)
            if loss_fn is not None:
                loss_value_raw = loss_fn(outputs, prepared)
            else:
                loss_value_raw = getattr(outputs, "loss", None)
            if loss_value_raw is None:
                continue

            if hasattr(loss_value_raw, "detach"):
                loss_tensor = loss_value_raw.detach()
            else:
                loss_tensor = torch.tensor(float(loss_value_raw), dtype=torch.float32)

            try:
                loss_scalar = float(loss_tensor.cpu().item())
            except Exception:
                loss_scalar = float(loss_tensor.cpu().float().mean().item())

            total_loss += loss_scalar
            steps += 1

    if hasattr(model, "train"):
        model.train(was_training)

    avg_loss = total_loss / max(steps, 1)
    return {"eval_loss": avg_loss}


__all__ = ["evaluate"]
