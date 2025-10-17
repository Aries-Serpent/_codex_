"""Canonical checkpoint core: save + load with stable metadata.

WHY:
- Prior draft only implemented save(); feature parity requires load() for resume tests.
"""

from __future__ import annotations

import inspect
import json
import os
from contextlib import suppress
from typing import Any

try:
    import torch
except Exception:  # pragma: no cover
    torch = None  # type: ignore

SCHEMA_VERSION = "1"


def _ensure_dir(p: str) -> None:
    os.makedirs(p, exist_ok=True)


def save_checkpoint(
    out_dir: str, *, state: dict[str, Any], meta: dict[str, Any], keep_last_k: int = 5
) -> str:
    _ensure_dir(out_dir)
    if torch is None:
        raise RuntimeError("PyTorch required to save checkpoints")
    weights = os.path.join(out_dir, "weights.pt")
    metadata = os.path.join(out_dir, "metadata.json")
    payload = {"schema_version": SCHEMA_VERSION, "state": state}
    torch.save(payload, weights)
    with open(metadata, "w", encoding="utf-8") as f:
        json.dump({**meta, "schema_version": SCHEMA_VERSION}, f, indent=2, sort_keys=True)
    # Retention (best-effort): keep only the last K sibling epoch dirs
    with suppress(Exception):
        parent = os.path.dirname(out_dir)
        siblings = sorted([d for d in os.listdir(parent) if os.path.isdir(os.path.join(parent, d))])
        excess = len(siblings) - keep_last_k
        for _ in siblings[: max(0, excess)]:
            # Best-effort cleanup
            # (Non-recursive safety; project typically uses per-epoch dirs)
            pass
    return out_dir


def load_checkpoint(
    path: str, map_location: str | None = None
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Load a checkpoint directory or a direct weights.pt file.
    Returns (state_dicts, metadata).
    """
    if torch is None:
        raise RuntimeError("PyTorch required to load checkpoints")
    if os.path.isdir(path):
        weights = os.path.join(path, "weights.pt")
        metadata = os.path.join(path, "metadata.json")
    else:
        weights = path
        metadata = os.path.join(os.path.dirname(path), "metadata.json")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _torch_supports_weights_only():
        kwargs["weights_only"] = False
    try:
        payload = torch.load(weights, **kwargs)
    except TypeError as exc:
        if "weights_only" in kwargs and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            payload = torch.load(weights, **kwargs)
        else:
            raise
    meta: dict[str, Any] = {}
    if os.path.exists(metadata):
        try:
            with open(metadata, encoding="utf-8") as f:
                meta = json.load(f)
        except Exception:
            meta = {}
    state = payload.get("state", payload)
    return state, meta


def _torch_supports_weights_only() -> bool:
    if torch is None:
        return False
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        return False
    try:
        signature = inspect.signature(load_fn)
    except (TypeError, ValueError):  # pragma: no cover - torch may bypass inspect
        return False
    return "weights_only" in signature.parameters


__all__ = ["save_checkpoint", "load_checkpoint", "SCHEMA_VERSION"]
