"""Utilities for deterministic dataset splitting."""

from __future__ import annotations

import logging
import os
import random
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

from codex_ml.data.split import DEFAULT_CHECKSUMS_NAME
from codex_ml.utils.repro import record_dataset_checksums

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class SplitPaths:
    """Paths for train/validation/test splits generated from a single dataset."""

    train: Path
    val: Path
    test: Path


def _normalise_ratios(ratios: Iterable[float]) -> tuple[float, float, float]:
    values = tuple(float(r) for r in ratios)
    if len(values) != 3:
        raise ValueError("split ratios must contain exactly three floats")
    if any(r < 0 for r in values):
        raise ValueError("split ratios must be non-negative")
    total = sum(values)
    if not 0.99 <= total <= 1.01:
        raise ValueError("split ratios must sum to 1.0 (allowing minor rounding error)")
    return values  # type: ignore[return-value]


def ensure_split_seed(seed: int | None = None) -> int:
    """Return a deterministic seed with environment overrides."""

    if seed is not None:
        return int(seed)
    env = os.environ.get("CODEX_DATA_SEED")
    if env:
        try:
            return int(env)
        except ValueError:
            pass
    return 42


def split_dataset(
    input_path: str | Path,
    splits: tuple[float, float, float] = (0.8, 0.1, 0.1),
    *,
    seed: int | None = 42,
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
    rng = random.Random(ensure_split_seed(seed))  # noqa: S311 - deterministic seeding
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

    manifest_path = source.parent / DEFAULT_CHECKSUMS_NAME
    try:
        record_dataset_checksums([train_path, val_path, test_path], manifest_path)
    except Exception as exc:  # pragma: no cover - manifest is best-effort
        LOGGER.warning("Failed to record dataset checksums at %s: %s", manifest_path, exc)

    return SplitPaths(train=train_path, val=val_path, test=test_path)


def deterministic_split(
    items: Sequence[object],
    *,
    val_fraction: float = 0.1,
    test_fraction: float = 0.1,
    seed: int | None = 42,
) -> tuple[list[object], list[object], list[object]]:
    """Partition *items* into deterministic train/val/test subsets.

    Fractions are computed relative to the full dataset size. The routine floors
    the validation and test counts individually; any remainder stays in the
    training split. The order of elements inside each split matches the
    shuffled order to preserve randomness while remaining reproducible given a
    fixed ``seed``.
    """

    n_items = len(items)
    if n_items == 0:
        return [], [], []

    if not 0 <= float(val_fraction) <= 1:
        raise ValueError("val_fraction must be between 0 and 1")
    if not 0 <= float(test_fraction) <= 1:
        raise ValueError("test_fraction must be between 0 and 1")
    if val_fraction + test_fraction >= 1:
        raise ValueError("validation and test fractions must leave room for train split")

    indices = list(range(n_items))
    rng = random.Random(ensure_split_seed(seed))  # noqa: S311 - deterministic seeding
    rng.shuffle(indices)

    n_test = int(n_items * float(test_fraction))
    n_val = int(n_items * float(val_fraction))

    test_indices = indices[:n_test]
    val_indices = indices[n_test : n_test + n_val]
    train_indices = indices[n_test + n_val :]

    def _take(idxs: list[int]) -> list[object]:
        return [items[i] for i in idxs]

    return _take(train_indices), _take(val_indices), _take(test_indices)


__all__ = ["SplitPaths", "deterministic_split", "ensure_split_seed", "split_dataset"]
