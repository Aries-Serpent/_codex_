from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Tuple

import numpy as np
import torch

try:  # optional import from ingestion utilities
    from ingestion import deterministic_shuffle  # type: ignore
except Exception:  # pragma: no cover - fallback
    import random

    def deterministic_shuffle(seq: Iterable[Any], seed: int) -> List[Any]:
        items = list(seq)
        rnd = random.Random(seed)
        rnd.shuffle(items)
        return items


def split_texts(
    texts: Iterable[str],
    train_ratio: float = 0.9,
    seed: int = 0,
    cache_path: str | None = None,
) -> Tuple[List[str], List[str]]:
    """Deterministically split ``texts`` into train/val lists.

    When ``cache_path`` is provided the split is cached on disk to allow
    reproducible reuse across runs.
    """
    items = list(texts)
    if cache_path is not None:
        p = Path(cache_path)
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                return list(data["train"]), list(data["val"])
            except Exception:
                pass
    shuffled = deterministic_shuffle(items, seed)
    split = int(len(shuffled) * train_ratio)
    train, val = shuffled[:split], shuffled[split:]
    if cache_path is not None:
        try:
            Path(cache_path).write_text(json.dumps({"train": train, "val": val}), encoding="utf-8")
        except Exception:
            pass
    return train, val


@dataclass
class TextDataset(torch.utils.data.Dataset):
    """Minimal text dataset producing next-token labels."""

    texts: List[str]
    tokenizer: Any
    block_size: int = 128

    def __post_init__(self) -> None:  # prepare tensor examples eagerly
        self.examples: List[Dict[str, torch.Tensor]] = []
        for txt in self.texts:
            if hasattr(self.tokenizer, "encode"):
                ids = self.tokenizer.encode(txt)
            else:
                ids = self.tokenizer(txt)["input_ids"]
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
        return {k: v.clone() for k, v in ex.items()}


def cache_dataset(ds: torch.utils.data.Dataset, cache_dir: str) -> None:
    """Cache tokenised dataset ``ds`` under ``cache_dir`` as `.npz` shards."""
    path = Path(cache_dir)
    path.mkdir(parents=True, exist_ok=True)
    for i, sample in enumerate(ds):
        arrs = {k: v.numpy() for k, v in sample.items()}
        np.savez(path / f"{i}.npz", **arrs)


def load_cached(cache_dir: str) -> Iterator[Dict[str, torch.Tensor]]:
    """Yield cached samples stored by :func:`cache_dataset`."""
    path = Path(cache_dir)
    for npz in sorted(path.glob("*.npz")):
        data = np.load(npz)
        yield {k: torch.tensor(data[k]) for k in data.files}
