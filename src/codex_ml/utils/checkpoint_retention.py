from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

__all__ = ["RetainSpec", "retain"]


@dataclass
class RetainSpec:
    """Retention policy for checkpoint directories."""

    keep_last: int = 3
    best_k: int = 0
    best_metric: str = "val_loss"


def _epoch_sort_key(path: Path) -> Tuple[int, str]:
    name = path.name
    try:
        suffix = name.rsplit("-", 1)[-1]
        return int(suffix), name
    except Exception:
        return (10**12, name)


def _load_metric(dir_path: Path, metric: str) -> Optional[float]:
    meta_path = dir_path / "metadata.json"
    if not meta_path.exists():
        return None
    try:
        data = json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    value = data.get(metric)
    if value is None and isinstance(data.get("metrics"), dict):
        value = data["metrics"].get(metric)
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def retain(checkpoints_root: Path, spec: RetainSpec) -> None:
    """Apply retention policy to checkpoint directories under ``checkpoints_root``."""

    if not checkpoints_root.exists():
        return

    dirs: List[Path] = [p for p in checkpoints_root.iterdir() if p.is_dir()]
    if not dirs:
        return
    dirs.sort(key=_epoch_sort_key)
    keep: set[Path] = set()

    keep.add(dirs[-1])

    if spec.keep_last <= 0 and spec.best_k <= 0:
        return

    if spec.keep_last > 0:
        keep.update(dirs[-spec.keep_last :])

    if spec.best_k > 0:
        scored: List[Tuple[float, Path]] = []
        for entry in dirs:
            metric_val = _load_metric(entry, spec.best_metric)
            if metric_val is None:
                continue
            scored.append((metric_val, entry))
        scored.sort(key=lambda item: item[0])
        for _, entry in scored[: spec.best_k]:
            keep.add(entry)

    for entry in dirs:
        if entry in keep:
            continue
        shutil.rmtree(entry, ignore_errors=True)
