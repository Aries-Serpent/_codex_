"""Dataset utilities for splitting and streaming text corpora.

This module provides helper functions to split an iterable of strings into
train and validation subsets deterministically and to stream text from a
file in chunks. These utilities decouple data handling from the training
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
    checksum_path: str | Path | None = None,
    *,
    filter_enabled: bool = True,
) -> Tuple[list[str], list[str]]:
    """Split texts into train and validation lists deterministically.

    Parameters
    ----------
    texts : Iterable[str] | str | Path
        An iterable of strings, or a path to a dataset file supported by
        codex_ml.data.loader.load_dataset.
    train_ratio : float, default=0.9
        Fraction of items placed in the training set.
    seed : int, default=0
        Random seed for deterministic shuffling.
    cache_path : str | Path | None, default=None
        When provided, cache the computed split to this path and reuse it
        on subsequent calls when inputs match.
    checksum_path : str | Path | None, default=None
        When provided, write the dataset checksum to this path for
        reproducibility tracking.
    filter_enabled : bool, default=True
        If True, apply the safety filter prior to splitting.

    Returns
    -------
    (list[str], list[str])
        Train and validation lists.
    """
    from codex_ml.data.loader import apply_safety_filter, load_dataset

    # Load items
    if isinstance(texts, (str, Path)):
        items = load_dataset(Path(texts))
    else:
        items = list(texts)
    from codex_ml.safety import SafetyConfig, sanitize_prompt

    items = apply_safety_filter(
        items, filter_enabled, lambda t: sanitize_prompt(t, SafetyConfig()).get("text", t)
    )

    # Stable checksum over individual items to detect any content change
    def _checksum(seq: Iterable[str]) -> str:
        h = hashlib.sha256()
        for item in seq:
            h.update(item.encode("utf-8"))
        return h.hexdigest()

    checksum = _checksum(items)
    if checksum_path is not None:
        try:
            Path(checksum_path).write_text(checksum, encoding="utf-8")
        except Exception:
            pass

    # Try cache (support legacy keys for backward compatibility)
    if cache_path is not None:
        p = Path(cache_path)
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                cached_sig = data.get("checksum") or data.get("sha256") or data.get("data_hash")
                if cached_sig == checksum:
                    return list(data["train"]), list(data["val"])
            except Exception:
                # Ignore malformed cache and recompute
                pass

    # Deterministic shuffle and split
    rng = random.Random(seed)
    items_shuffled = list(items)
    rng.shuffle(items_shuffled)
    split_idx = int(len(items_shuffled) * float(train_ratio))
    train, val = items_shuffled[:split_idx], items_shuffled[split_idx:]

    # Persist cache
    if cache_path is not None:
        try:
            Path(cache_path).parent.mkdir(parents=True, exist_ok=True)
            Path(cache_path).write_text(
                json.dumps({"train": train, "val": val, "checksum": checksum}, ensure_ascii=False),
                encoding="utf-8",
            )
        except Exception:
            # Best-effort cache only
            pass

    return train, val


def stream_texts(
    path: str | Path, chunk_size: int = 4096, encoding: str = "utf-8"
) -> Iterator[str]:
    """Stream text from path in chunks of size chunk_size.

    Parameters
    ----------
    path : str | Path
        Path to a text file.
    chunk_size : int, default=4096
        Number of characters per yielded chunk.
    encoding : str, default="utf-8"
        Text encoding used for reading.

    Yields
    ------
    str
        Chunks of the file as strings.
    """
    p = Path(path)
    with p.open("r", encoding=encoding) as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk
