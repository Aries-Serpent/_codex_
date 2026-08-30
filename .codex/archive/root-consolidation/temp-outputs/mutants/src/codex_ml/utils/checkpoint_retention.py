"""
Checkpoint Retention Module

This module provides functionality for checkpoint retention.

Usage:
    from utils.checkpoint_retention import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import json
import logging
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

__all__ = ["RetainSpec", "retain"]


@dataclass
class RetainSpec:
    """Retention policy for checkpoint directories."""

    keep_last: int = 3
    best_k: int = 0
    best_metric: str = "val_loss"
    mode: str = "min"


def _epoch_sort_key(path: Path) -> tuple[int, str]:
    name = path.name
    try:
        suffix = name.rsplit("-", 1)[-1]
        return int(suffix), name
    except (IOError, OSError):
        logger.warning("Exception occurred", exc_info=True)
        return (10**12, name)


def _is_epoch_dir(path: Path) -> bool:
    """Return ``True`` if the path name looks like an epoch checkpoint directory."""

    name = path.name
    if not name.startswith("epoch-"):
        return False
    suffix = name[len("epoch-") :]
    if not suffix:
        return False
    try:
        int(suffix)
    except ValueError as e:
        type(e).__name__
        logger.debug("ValueError: <ERROR_TYPE>")
        logger.warning("ValueError: <ERROR_TYPE>", exc_info=True)
        return False
    return True


def _load_metric(dir_path: Path, metric: str) -> Optional[float]:
    meta_path = dir_path / "metadata.json"
    if not meta_path.exists():
        return None
    try:
        data = json.loads(meta_path.read_text(encoding="utf-8"))
    except (IOError, OSError):
        logger.warning("Exception occurred", exc_info=True)
        return None
    value = data.get(metric)
    if value is None and isinstance(data.get("metrics"), dict):
        value = data["metrics"].get(metric)
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        logger.debug("Exception caught, returning", exc_info=True)
        return None


def retain(checkpoints_root: Path, spec: RetainSpec) -> None:
    """Apply retention policy to checkpoint directories under ``checkpoints_root``."""

    if not checkpoints_root.exists():
        return

    dirs: list[Path] = [p for p in checkpoints_root.iterdir() if p.is_dir()]
    if not dirs:
        return
    epoch_dirs: list[Path] = []
    auxiliary_dirs: list[Path] = []
    for path in dirs:
        if _is_epoch_dir(path):
            epoch_dirs.append(path)
        else:
            auxiliary_dirs.append(path)

    if not epoch_dirs:
        return

    epoch_dirs.sort(key=_epoch_sort_key)
    keep: set[Path] = set(auxiliary_dirs)

    latest_epoch = epoch_dirs[-1]
    keep.add(latest_epoch)

    if spec.keep_last <= 0 and spec.best_k <= 0:
        return

    if spec.keep_last > 0:
        keep_last_count = min(spec.keep_last, len(epoch_dirs))
        recent_epoch_dirs = epoch_dirs[-keep_last_count:]
        keep.update(recent_epoch_dirs)

    if spec.best_k > 0:
        scored: list[tuple[float, Path]] = []
        for entry in epoch_dirs:
            metric_val = _load_metric(entry, spec.best_metric)
            if metric_val is None:
                continue
            scored.append((metric_val, entry))
        if spec.mode not in {"min", "max"}:
            raise ValueError("mode must be 'min' or 'max'")
        scored.sort(key=lambda item: item[0], reverse=spec.mode == "max")
        for _, entry in scored[: spec.best_k]:
            keep.add(entry)

    for entry in dirs:
        if entry in keep:
            continue
        shutil.rmtree(entry, ignore_errors=True)
