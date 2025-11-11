"""Lightweight checkpoint save/load helpers with pruning support."""

from __future__ import annotations

import os
import pickle
from pathlib import Path
from typing import Any

try:  # pragma: no cover - optional torch dependency
    import torch
except Exception:  # pragma: no cover - torch missing
    torch = None  # type: ignore[assignment]

__all__ = ["save_checkpoint", "load_checkpoint"]


def save_checkpoint(
    state: dict[str, Any], path: str | os.PathLike[str], *, keep_last_k: int = 3
) -> Path:
    """Persist ``state`` to ``path`` and prune older checkpoints."""

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if torch is not None and hasattr(torch, "save"):
        torch.save(state, target)
    else:  # pragma: no cover - exercised when torch is unavailable
        with target.open("wb") as handle:
            pickle.dump(state, handle)

    if keep_last_k <= 0:
        return target

    checkpoints = sorted(
        target.parent.glob("*.pt"),
        key=lambda candidate: (os.path.getmtime(candidate), candidate.name),
    )
    while len(checkpoints) > keep_last_k:
        oldest = checkpoints.pop(0)
        try:
            oldest.unlink()
        except FileNotFoundError:  # pragma: no cover - race condition guard
            continue
    return target


def load_checkpoint(path: str | os.PathLike[str]) -> dict[str, Any]:
    """Load a checkpoint previously written by :func:`save_checkpoint`."""

    target = Path(path)
    if not target.exists():
        raise FileNotFoundError(path)
    if torch is not None and hasattr(torch, "load"):
        try:
            data = torch.load(target, map_location="cpu")
        except (RuntimeError, pickle.UnpicklingError, EOFError, AttributeError) as torch_error:
            with target.open("rb") as handle:
                try:
                    data = pickle.load(handle)
                except Exception:
                    raise torch_error
    else:  # pragma: no cover - exercised when torch is unavailable
        with target.open("rb") as handle:
            data = pickle.load(handle)
    if not isinstance(data, dict):
        raise TypeError("checkpoint payload must be a mapping")
    return data
