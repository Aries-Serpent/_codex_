"""Dataset utilities for splitting and streaming text corpora.

This module provides helper functions to split an iterable of strings into
train and validation subsets deterministically and to stream text from a
file in chunks.  These utilities decouple data handling from the training
engine and ease reproducible experiments.
"""

from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path
from typing import Iterable, Iterator, Tuple, Union

from codex_ml.safety import SafetyConfig, sanitize_prompt


def split_dataset(
    texts: Union[Iterable[str], str, Path],
    train_ratio: float = 0.9,
    seed: int = 0,
    cache_path: str | Path | None = None,
    *,
    filter_enabled: bool = True,
) -> Tuple[list[str], list[str]]:
    """Split ``texts`` into train and validation lists deterministically.

    ``texts`` may be an iterable of strings or a path to a dataset file
    supported by :func:`codex_ml.data.loader.load_dataset`.

    The split can optionally be cached to ``cache_path`` so repeated calls avoid
    recomputing the shuffle.  When ``cache_path`` exists it is loaded and
    returned as-is.
    """
    from codex_ml.data.loader import apply_safety_filter, load_dataset

    if isinstance(texts, (str, Path)):
        items = load_dataset(Path(texts))
    else:
        items = list(texts)
    items = apply_safety_filter(
        items, filter_enabled, lambda t: sanitize_prompt(t, SafetyConfig()).get("text", t)
    )
    data_hash = hashlib.sha256("".join(items).encode("utf-8")).hexdigest()
    if cache_path is not None:
        p = Path(cache_path)
        if p.exists():
            try:
                data = json.loads(p.read_text())
                if data.get("data_hash") == data_hash:
                    return data["train"], data["val"]
            except Exception:
                pass
    rng = random.Random(seed)
    rng.shuffle(items)
    split = int(len(items) * train_ratio)
    train, val = items[:split], items[split:]
    if cache_path is not None:
        try:
            Path(cache_path).write_text(
                json.dumps({"train": train, "val": val, "data_hash": data_hash})
            )
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
