"""Dataset utilities for splitting and streaming text corpora.

This module provides helper functions to split an iterable of strings into
train and validation subsets deterministically and to stream text from a
file in chunks.  These utilities decouple data handling from the training
engine and ease reproducible experiments.
"""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Iterable, Iterator, Tuple


def split_dataset(
    texts: Iterable[str],
    train_ratio: float = 0.9,
    seed: int = 0,
    cache_path: str | Path | None = None,
) -> Tuple[list[str], list[str]]:
    """Split ``texts`` into train and validation lists deterministically.

    The split can optionally be cached to ``cache_path`` so repeated calls avoid
    recomputing the shuffle.  When ``cache_path`` exists it is loaded and
    returned as-is.

    Args:
        texts: Iterable of strings.
        train_ratio: Fraction of examples to allocate to the training set.
        seed: Random seed for deterministic shuffling.
        cache_path: Optional path to a JSON file used to cache the split.

    Returns:
        ``(train_texts, val_texts)``
    """
    items = list(texts)
    if cache_path is not None:
        p = Path(cache_path)
        if p.exists():
            try:
                data = json.loads(p.read_text())
                return data["train"], data["val"]
            except Exception:
                pass
    rng = random.Random(seed)
    rng.shuffle(items)
    split = int(len(items) * train_ratio)
    train, val = items[:split], items[split:]
    if cache_path is not None:
        try:
            Path(cache_path).write_text(json.dumps({"train": train, "val": val}))
        except Exception:
            pass
    return train, val


def stream_texts(
    path: str | Path, chunk_size: int = 4096, encoding: str = "utf-8"
) -> Iterator[str]:
    """Stream text from ``path`` in chunks of size ``chunk_size``.

    Args:
        path: Path to a text file.
        chunk_size: Number of characters per yielded chunk.
        encoding: Text encoding to use when reading.

    Yields:
        Chunks of the file as strings.
    """
    p = Path(path)
    with p.open("r", encoding=encoding) as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk
