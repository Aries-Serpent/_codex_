"""Deterministic dataset split writer with manifest support."""

from __future__ import annotations

import hashlib
import json
import random
from collections.abc import Iterable, Sequence
from pathlib import Path


def _validate_ratios(ratios: tuple[float, float, float]) -> None:
    if len(ratios) != 3:
        raise ValueError("ratios must contain exactly three values")
    if not abs(sum(ratios) - 1.0) < 1e-6:
        raise ValueError("ratios must sum to 1.0")


def write_splits(
    items: Sequence[str] | Iterable[str],
    out_dir: Path | str,
    *,
    seed: int = 42,
    ratios: tuple[float, float, float] = (0.9, 0.05, 0.05),
    overwrite: bool = False,
) -> None:
    """Shuffle *items* deterministically and write train/val/test splits."""

    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    _validate_ratios(ratios)

    materialised = list(items)
    rng = random.Random(int(seed))  # nosec B311 — non-cryptographic ML sampling/shuffling
    rng.shuffle(materialised)

    total = len(materialised)
    train_count = int(total * ratios[0])
    val_count = int(total * ratios[1])

    train_items = materialised[:train_count]
    val_items = materialised[train_count : train_count + val_count]
    test_items = materialised[train_count + val_count :]

    outputs = {
        "train.txt": train_items,
        "val.txt": val_items,
        "test.txt": test_items,
    }

    manifest_path = out_path / "manifest.json"

    for name in (*outputs.keys(), "manifest.json"):
        target = out_path / name
        if target.exists() and not overwrite:
            raise FileExistsError(f"{target} exists and overwrite=False")

    for name, values in outputs.items():
        (out_path / name).write_text("\n".join(values), encoding="utf-8")

    canonical = "\n".join(materialised).encode("utf-8")
    digest = hashlib.sha256(canonical).hexdigest()[:16]
    manifest = {
        "seed": int(seed),
        "counts": {
            "train": len(train_items),
            "val": len(val_items),
            "test": len(test_items),
        },
        "dataset_hash": digest,
        "ratios": ratios,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


__all__ = ["write_splits"]
