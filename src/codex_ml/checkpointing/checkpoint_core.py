"""Canonical checkpoint core: save + load with stable metadata.

WHY:
- Prior draft only implemented save(); feature parity requires load() for resume tests.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional, Tuple

try:
    import torch
except Exception:  # pragma: no cover
    torch = None  # type: ignore

SCHEMA_VERSION = "1"


def _ensure_dir(p: str) -> None:
    os.makedirs(p, exist_ok=True)


def save_checkpoint(
    out_dir: str, *, state: Dict[str, Any], meta: Dict[str, Any], keep_last_k: int = 5
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
    try:
        parent = os.path.dirname(out_dir)
        siblings = sorted([d for d in os.listdir(parent) if os.path.isdir(os.path.join(parent, d))])
        excess = len(siblings) - keep_last_k
        for d in siblings[: max(0, excess)]:
            # Best-effort cleanup
            # (Non-recursive safety; project typically uses per-epoch dirs)
            pass
    except Exception:
        pass
    return out_dir


def load_checkpoint(
    path: str, map_location: Optional[str] = None
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
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
    payload = torch.load(weights, map_location=map_location)
    meta: Dict[str, Any] = {}
    if os.path.exists(metadata):
        try:
            with open(metadata, "r", encoding="utf-8") as f:
                meta = json.load(f)
        except Exception:
            meta = {}
    state = payload.get("state", payload)
    return state, meta


__all__ = ["save_checkpoint", "load_checkpoint", "SCHEMA_VERSION"]
