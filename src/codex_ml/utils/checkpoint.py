"""Lightweight checkpoint helpers for Codex ML.

These utilities provide a small façade around ``torch.save``/``torch.load``
that preserves model, optimiser and scheduler state dictionaries alongside a
JSON metadata file.  The helpers intentionally avoid any network access and are
safe to use in offline environments.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

import torch

__all__ = ["save_checkpoint", "load_checkpoint"]


def save_checkpoint(
    *,
    model: torch.nn.Module,
    optimizer: Optional[torch.optim.Optimizer],
    scheduler: Optional[Any],
    out_dir: Path,
    metadata: Optional[Dict[str, Any]] = None,
) -> Path:
    """Persist training state into ``out_dir``.

    The directory is created when needed and the function writes four files:

    ``model.pt``
        ``state_dict`` of ``model``.
    ``optimizer.pt``
        ``state_dict`` of ``optimizer`` when provided.
    ``scheduler.pt``
        ``state_dict`` of ``scheduler`` when provided and the object exposes a
        ``state_dict`` method.
    ``metadata.json``
        JSON payload capturing ``metadata`` plus a ``version`` field.
    """

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), out_dir / "model.pt")
    if optimizer is not None:
        torch.save(optimizer.state_dict(), out_dir / "optimizer.pt")
    if scheduler is not None and hasattr(scheduler, "state_dict"):
        torch.save(scheduler.state_dict(), out_dir / "scheduler.pt")
    meta = {"version": 1}
    if metadata:
        meta.update(metadata)
    (out_dir / "metadata.json").write_text(
        json.dumps(meta, indent=2, sort_keys=True), encoding="utf-8"
    )
    return out_dir


def load_checkpoint(
    *,
    model: torch.nn.Module,
    optimizer: Optional[torch.optim.Optimizer],
    scheduler: Optional[Any],
    ckpt_dir: Path,
    map_location: Optional[str] = "cpu",
) -> Dict[str, Any]:
    """Load training state from ``ckpt_dir``.

    Missing optimiser/scheduler files are ignored which keeps the function
    usable for evaluation-only scenarios.  The metadata file is returned as a
    dictionary (empty when the file does not exist).
    """

    ckpt_dir = Path(ckpt_dir)
    state = torch.load(ckpt_dir / "model.pt", map_location=map_location)
    model.load_state_dict(state)
    opt_path = ckpt_dir / "optimizer.pt"
    if optimizer is not None and opt_path.exists():
        optimizer.load_state_dict(torch.load(opt_path, map_location=map_location))
    sched_path = ckpt_dir / "scheduler.pt"
    if scheduler is not None and sched_path.exists():
        scheduler.load_state_dict(torch.load(sched_path, map_location=map_location))
    meta_path = ckpt_dir / "metadata.json"
    if not meta_path.exists():
        return {}
    try:
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
