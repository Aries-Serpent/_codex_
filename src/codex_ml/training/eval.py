"""Utilities for running evaluation loops during training."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, MutableMapping
from datetime import datetime, timezone
from pathlib import Path

from codex_utils.ndjson import NDJSONLogger

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


def _move_batch_to_device(batch: Mapping[str, object], device: object) -> Mapping[str, object]:
    if device is None:
        return batch
    moved: dict[str, object] = {}
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
    metrics_fn: Callable[[object, Mapping[str, object]], MutableMapping[str, float]] | None = None,
    device: object | None = None,
    ndjson_path: str | Path | None = None,
) -> dict[str, float]:
    """Run a lightweight evaluation loop and return averaged metrics."""

    training_mode = getattr(model, "training", True)
    if torch is not None:
        ctx = torch.no_grad()
    else:  # pragma: no cover - torch optional
        from contextlib import nullcontext

        ctx = nullcontext()

    if hasattr(model, "eval"):
        model.eval()
    totals: dict[str, float] = {}
    batches = 0
    ndjson_logger: NDJSONLogger | None = NDJSONLogger(ndjson_path) if ndjson_path else None

    try:
        with ctx:
            for batch in dataloader:
                batches += 1
                batch_for_device = (
                    _move_batch_to_device(batch, device) if isinstance(batch, Mapping) else batch
                )
                outputs = model(**batch_for_device)
                loss = loss_fn(outputs, batch_for_device)
                if loss is not None:
                    loss_value = _safe_float(loss)
                    totals["eval_loss"] = totals.get("eval_loss", 0.0) + loss_value

                if metrics_fn is not None:
                    try:
                        metrics = metrics_fn(outputs, batch_for_device)
                    except Exception:
                        metrics = {}
                    for key, value in metrics.items():
                        totals[key] = totals.get(key, 0.0) + _safe_float(value)
    finally:
        if hasattr(model, "train"):
            model.train(training_mode)

    if batches == 0:
        return {key: 0.0 for key in totals}
    results = {key: value / batches for key, value in totals.items()}
    if ndjson_logger is not None:
        record: MutableMapping[str, float | int | str] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "batches": batches,
        }
        record.update(results)
        ndjson_logger.write(record)
    return results


__all__ = ["evaluate"]
