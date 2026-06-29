"""
Evaluate Module

This module provides functionality for evaluate.

Usage:
    from training.evaluate import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


import contextlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
from collections.abc import Iterable, Mapping  # noqa: E402
from importlib import import_module  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Any  # noqa: E402


def _require_torch():
    return import_module("torch")


def _infer_device(model: Any) -> str | None:
    if hasattr(model, "device"):
        device = model.device
        return str(device)
    parameters = getattr(model, "parameters", None)
    if callable(parameters):
        iterator = parameters()
        try:
            first = next(iterator)
        except StopIteration:
            logger.debug("Exception caught, returning", exc_info=True)
            return None
        dev = getattr(first, "device", None)
        return str(dev) if dev is not None else None
    return None


def _encoding_to_mapping(batch: Any) -> Mapping[str, Any]:
    if isinstance(batch, Mapping):
        return batch
    data = getattr(batch, "data", None)
    if isinstance(data, Mapping):
        return data
    raise TypeError(f"Unsupported batch encoding type: {type(batch)!r}")


def _to_device(batch: Mapping[str, Any], device: str | None) -> dict[str, Any]:
    if device is None:
        return dict(batch)
    moved: dict[str, Any] = {}
    for key, value in batch.items():
        if hasattr(value, "to"):
            moved[key] = value.to(device)
        else:
            moved[key] = value
    return moved


def _loss_to_float(loss: Any) -> float:
    if isinstance(loss, (int, float)):
        return float(loss)
    if hasattr(loss, "detach"):
        detached = loss.detach()
        return _loss_to_float(detached)
    if hasattr(loss, "cpu"):
        cpu = loss.cpu()
        return _loss_to_float(cpu)
    if hasattr(loss, "item"):
        return float(loss.item())
    raise TypeError(f"Cannot convert loss of type {type(loss)!r} to float")


def _resolve_text(sample: Any, text_key: str) -> str | None:
    if sample is None:
        return None
    if isinstance(sample, str):
        return sample
    if isinstance(sample, Mapping):
        value = sample.get(text_key)
        if value is None:
            return None
        if isinstance(value, str):
            return value
        return str(value)
    return str(sample)


def evaluate(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
    writer_ctx = (
        path.open("w", encoding="utf-8") if path is not None else contextlib.nullcontext(None)
    )

    losses: list[float] = []
    with writer_ctx as writer:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        type(e).__name__
        logger.warning("OverflowError: <ERROR_TYPE>", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


__all__ = ["evaluate"]
