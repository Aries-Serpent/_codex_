"""Data utilities for `_codex_`.

Focus:
- Deterministic train/eval splitting given an ID list and seed.
- Simple helpers for mapping IDs to splits per config.
"""

from __future__ import annotations

import random
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass
class SplitConfig:
    """Configuration for splitting a dataset into train/eval.

    fraction_train: float in (0, 1), fraction to allocate to train.
    seed: random seed controlling the permutation.
    """

    fraction_train: float = 0.9
    seed: int = 123


def deterministic_split_ids(
    ids: Sequence[str],
    split_cfg: SplitConfig,
) -> tuple[list[str], list[str]]:
    """Deterministically split IDs into train and eval sets.

    Steps:
    - Copy IDs into a list.
    - Shuffle using Random(split_cfg.seed).
    - Take first N for train, remainder for eval.
    """

    if not 0.0 < split_cfg.fraction_train < 1.0:
        raise ValueError("fraction_train must be in (0, 1)")
    ids_list = list(ids)
    rng = random.Random(split_cfg.seed)  # nosec B311 — non-cryptographic ML sampling/shuffling
    rng.shuffle(ids_list)
    n_train = int(round(len(ids_list) * split_cfg.fraction_train))
    train_ids = ids_list[:n_train]
    eval_ids = ids_list[n_train:]
    return train_ids, eval_ids


def assign_split_map(
    ids: Sequence[str],
    split_cfg: SplitConfig,
) -> dict[str, str]:
    """Return a mapping id -> split_name ('train' or 'eval')."""

    train_ids, eval_ids = deterministic_split_ids(ids, split_cfg)
    out: dict[str, str] = {}
    for _id in train_ids:
        out[_id] = "train"
    for _id in eval_ids:
        out[_id] = "eval"
    return out
