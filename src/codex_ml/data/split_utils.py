"""Utilities for deterministic JSONL dataset splitting."""

from __future__ import annotations

import random
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Tuple


@dataclass(frozen=True)
class SplitPaths:
    """Paths for train/validation/test splits generated from a single dataset."""

    train: Path
    val: Path
    test: Path


def _normalise_ratios(ratios: Iterable[float]) -> Tuple[float, float, float]:
    values = tuple(float(r) for r in ratios)
    if len(values) != 3:
        raise ValueError("split ratios must contain exactly three floats")
    if any(r < 0 for r in values):
        raise ValueError("split ratios must be non-negative")
    total = sum(values)
    if not 0.99 <= total <= 1.01:
        raise ValueError("split ratios must sum to 1.0 (allowing minor rounding error)")
    return values  # type: ignore[return-value]


def split_dataset(
    input_path: str | Path,
    splits: Tuple[float, float, float] = (0.8, 0.1, 0.1),
    *,
    seed: int = 42,
) -> SplitPaths:
    """Split ``input_path`` JSONL file into train/val/test subsets deterministically."""

    source = Path(input_path)
    if not source.exists():
        raise FileNotFoundError(f"dataset not found: {source}")
    ratios = _normalise_ratios(splits)
    lines = [
        line.rstrip("\n")
        for line in source.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if not lines:
        raise ValueError(f"dataset {source} is empty")
    rng = random.Random(seed)
    rng.shuffle(lines)
    total = len(lines)
    train_n = int(total * ratios[0])
    val_n = int(total * ratios[1])
    test_n = total - train_n - val_n
    if min(train_n, val_n, test_n) <= 0:
        raise ValueError("split ratios produce empty subset; adjust ratios or dataset size")

    def _write_subset(target: Path, subset: Iterable[str]) -> Path:
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", encoding="utf-8") as handle:
            for item in subset:
                handle.write(item + "\n")
        return target

    train_path = Path(f"{source}.train.jsonl")
    val_path = Path(f"{source}.val.jsonl")
    test_path = Path(f"{source}.test.jsonl")

    _write_subset(train_path, lines[:train_n])
    _write_subset(val_path, lines[train_n : train_n + val_n])
    _write_subset(test_path, lines[train_n + val_n :])

    return SplitPaths(train=train_path, val=val_path, test=test_path)


__all__ = ["SplitPaths", "split_dataset"]
