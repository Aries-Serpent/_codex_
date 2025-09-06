from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Mapping, Sequence, Tuple, TypeVar

import numpy as np
import torch

T = TypeVar("T")

# Optional deterministic shuffler import with robust fallback
try:  # pragma: no cover - optional import from ingestion utilities
    from ingestion import deterministic_shuffle  # type: ignore
except Exception:  # pragma: no cover - fallback
    import random

    def deterministic_shuffle(seq: Iterable[Any], seed: int) -> List[Any]:
        items = list(seq)
        rnd = random.Random(seed)
        rnd.shuffle(items)
        return items


def split_dataset(
    items: Sequence[T] | Mapping[Any, T],
    train_ratio: float = 0.9,
    seed: int = 42,
    cache_path: str | Path | None = None,
) -> Tuple[List[T], List[T]]:
    """Split items deterministically into train and validation lists.

    Supports sequences or mappings; mappings are split over their values.
    Optionally caches split indices on disk for reproducible reuse.

    Parameters
    ----------
    items : Sequence[T] | Mapping[Any, T]
        Collection of items to split.
    train_ratio : float, default=0.9
        Fraction of items to allocate to the training set. Must be in [0, 1].
    seed : int, default=42
        Seed for deterministic shuffling.
    cache_path : str | Path | None, default=None
        When provided, cache split indices to JSON at this path and reuse on subsequent runs.
        The cache stores indices, not values, to remain agnostic to item serializability.

    Returns
    -------
    (List[T], List[T])
        Train and validation lists.
    """
    if not 0.0 <= float(train_ratio) <= 1.0:
        raise ValueError("train_ratio must be within [0.0, 1.0]")

    seq: List[T] = list(items.values()) if isinstance(items, Mapping) else list(items)
    n = len(seq)
    if n == 0:
        return [], []

    # Try to reuse cached indices when compatible
    cached_train_idx: List[int] | None = None
    cached_val_idx: List[int] | None = None
    if cache_path is not None:
        p = Path(cache_path)
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                if (
                    isinstance(data, dict)
                    and data.get("length") == n
                    and abs(float(data.get("train_ratio", train_ratio)) - float(train_ratio)) < 1e-12
                    and int(data.get("seed", seed)) == int(seed)
                    and isinstance(data.get("train_idx"), list)
                    and isinstance(data.get("val_idx"), list)
                ):
                    cached_train_idx = [int(i) for i in data["train_idx"]]
                    cached_val_idx = [int(i) for i in data["val_idx"]]
            except Exception:
                # Ignore malformed cache
                cached_train_idx = cached_val_idx = None

    if cached_train_idx is None or cached_val_idx is None:
        # Fresh deterministic indices
        indices = list(range(n))
        indices = deterministic_shuffle(indices, seed)
        split = int(n * float(train_ratio))
        train_idx, val_idx = indices[:split], indices[split:]
    else:
        train_idx, val_idx = cached_train_idx, cached_val_idx

    train = [seq[i] for i in train_idx]
    val = [seq[i] for i in val_idx]

    # Persist indices cache if requested
    if cache_path is not None:
        try:
            Path(cache_path).parent.mkdir(parents=True, exist_ok=True)
            Path(cache_path).write_text(
                json.dumps(
                    {
                        "length": n,
                        "seed": int(seed),
                        "train_ratio": float(train_ratio),
                        "train_idx": train_idx,
                        "val_idx": val_idx,
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
        except Exception:
            # Best-effort cache; ignore failures
            pass

    return train, val


def split_texts(
    texts: Iterable[str],
    train_ratio: float = 0.9,
    seed: int = 0,
    cache_path: str | None = None,
) -> Tuple[List[str], List[str]]:
    """Deterministically split texts into train/val lists.

    When cache_path is provided the split is cached on disk to allow
    reproducible reuse across runs.

    Parameters
    ----------
    texts : Iterable[str]
        Input text samples.
    train_ratio : float, default=0.9
        Fraction of samples placed in the training set.
    seed : int, default=0
        Shuffle seed.
    cache_path : str | None, default=None
        JSON file to persist/reuse the concrete text split.

    Returns
    -------
    (List[str], List[str])
        Train and validation text lists.
    """
    items = list(texts)
    if cache_path is not None:
        p = Path(cache_path)
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                return list(data["train"]), list(data["val"])
            except Exception:
                # fall through to recompute
                pass
    shuffled = deterministic_shuffle(items, seed)
    split = int(len(shuffled) * train_ratio)
    train, val = shuffled[:split], shuffled[split:]
    if cache_path is not None:
        try:
            Path(cache_path).parent.mkdir(parents=True, exist_ok=True)
            Path(cache_path).write_text(
                json.dumps({"train": train, "val": val}, indent=2), encoding="utf-8"
            )
        except Exception:
            pass
    return train, val


@dataclass
class TextDataset(torch.utils.data.Dataset):
    """Minimal text dataset producing next-token labels."""

    texts: List[str]
    tokenizer: Any
    block_size: int = 128

    def __post_init__(self) -> None:
        # Prepare tensor examples eagerly
        self.examples: List[Dict[str, torch.Tensor]] = []
        for txt in self.texts:
            # Support both HF-style tokenizer and simple encode function
            if hasattr(self.tokenizer, "encode"):
                ids = self.tokenizer.encode(txt)
            else:
                ids = self.tokenizer(txt)["input_ids"]
            # Truncate to block_size + next-token label
            ids = ids[: self.block_size + 1]
            if len(ids) < 2:
                continue
            input_ids = ids[:-1]
            labels = ids[1:]
            attn = [1] * len(input_ids)
            self.examples.append(
                {
                    "input_ids": torch.tensor(input_ids, dtype=torch.long),
                    "labels": torch.tensor(labels, dtype=torch.long),
                    "attention_mask": torch.tensor(attn, dtype=torch.long),
                }
            )

    def __len__(self) -> int:
        return len(self.examples)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        ex = self.examples[idx]
        # Return clones to avoid unwanted in-place mutations
        return {k: v.clone() for k, v in ex.items()}


def cache_dataset(ds: torch.utils.data.Dataset, cache_dir: str | Path) -> None:
    """Cache tokenised dataset ds under cache_dir as .npz shards."""
    path = Path(cache_dir)
    path.mkdir(parents=True, exist_ok=True)
    for i, sample in enumerate(ds):
        arrs = {k: v.numpy() if isinstance(v, torch.Tensor) else np.asarray(v) for k, v in sample.items()}
        np.savez(path / f"{i}.npz", **arrs)


def load_cached(cache_dir: str | Path) -> Iterator[Dict[str, torch.Tensor]]:
    """Yield cached samples stored by cache_dataset."""
    path = Path(cache_dir)
    for npz in sorted(path.glob("*.npz")):
        data = np.load(npz)
        yield {k: torch.tensor(data[k]) for k in data.files}


__all__ = [
    "deterministic_shuffle",
    "split_dataset",
    "split_texts",
    "TextDataset",
    "cache_dataset",
    "load_cached",
]
