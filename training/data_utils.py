from __future__ import annotations

import random
from typing import Any, List, Mapping, Sequence, Tuple, TypeVar

T = TypeVar("T")


def split_dataset(
    items: Sequence[T] | Mapping[Any, T],
    train_ratio: float = 0.9,
    seed: int = 42,
) -> Tuple[List[T], List[T]]:
    """Split ``items`` deterministically into train and validation lists.

    Args:
        items: Sequence or mapping of items to split.
        train_ratio: Fraction of items to allocate to the training set.
        seed: Random seed controlling the shuffle.

    Returns:
        ``(train_items, val_items)`` as lists.
    """
    if not 0.0 <= train_ratio <= 1.0:
        raise ValueError("train_ratio must be within [0.0, 1.0]")

    if isinstance(items, Mapping):
        seq = list(items.values())
    else:
        seq = list(items)

    indices = list(range(len(seq)))
    rnd = random.Random(seed)
    rnd.shuffle(indices)
    split = int(len(seq) * train_ratio)
    train_idx, val_idx = indices[:split], indices[split:]
    train = [seq[i] for i in train_idx]
    val = [seq[i] for i in val_idx]
    return train, val
