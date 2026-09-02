"""
Datasets Module

This module provides functionality for datasets.

Usage:
    from training.datasets import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import hashlib  # noqa: E402
import json  # noqa: E402
from collections.abc import Iterable, Iterator, Sequence  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import torch  # noqa: E402

try:  # optional dependency
    from datasets import Dataset  # type: ignore
except ImportError:  # pragma: no cover - optional dep missing
    Dataset = None


def _encode_text(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", -100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


class TextDataset(torch.utils.data.Dataset):
    """Materialized dataset of tokenized texts."""

    def __init__(
        self,
        items: Sequence[str],
        tokenizer,
        max_length: int,
        *,
        seed_data: int | None = None,
    ) -> None:
        ordered = list(items)
        if seed_data is not None and len(ordered) > 1:
            rng = np.random.default_rng(seed_data)
            rng.shuffle(ordered)
        self.data = [_encode_text(tokenizer, t, max_length) for t in ordered]

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self.data)

    def __getitem__(self, idx: int) -> dict[str, np.ndarray]:  # pragma: no cover - trivial
        return self.data[idx]


class IterableTextDataset(torch.utils.data.IterableDataset):
    """Tokenize a stream of texts on the fly."""

    def __init__(
        self,
        stream: Iterable[str],
        tokenizer,
        max_length: int,
        prefetch_k: int = 0,
    ) -> None:
        super().__init__()
        self.stream = stream
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.prefetch_k = int(prefetch_k)

    def __iter__(self) -> Iterator[dict[str, np.ndarray]]:
        if self.prefetch_k <= 0:
            for text in self.stream:
                yield _encode_text(self.tokenizer, text, self.max_length)
        else:
            buf: list[dict[str, np.ndarray]] = []
            for text in self.stream:
                buf.append(_encode_text(self.tokenizer, text, self.max_length))
                if len(buf) >= self.prefetch_k:
                    for item in buf:
                        yield item
                    buf.clear()
            for item in buf:
                yield item


def to_hf_dataset(items: Sequence[str], tokenizer, max_length: int) -> Dataset:
    """Return a HuggingFace ``Dataset`` of tokenized texts."""
    if Dataset is None:  # pragma: no cover - dependency guard
        raise ImportError("datasets is required for to_hf_dataset")
    data = [_encode_text(tokenizer, t, max_length) for t in items]
    return Dataset.from_list(data)


def compute_dataset_hash(items: Iterable[str]) -> str:
    """Compute a stable SHA256 hash for a collection of text samples."""

    digest = hashlib.sha256()
    for text in items:
        digest.update(text.encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()


def cache_texts(
    items: Sequence[str],
    cache_dir: str | Path,
    *,
    name: str = "dataset",
    include_hash: bool = True,
) -> Path:
    """Persist raw texts to a cache directory with a hash-derived filename."""

    cache_root = Path(cache_dir)
    cache_root.mkdir(parents=True, exist_ok=True)
    ds_hash = compute_dataset_hash(items) if include_hash else "nohash"
    target = cache_root / f"{name}-{ds_hash}.jsonl"
    with target.open("w", encoding="utf-8") as fh:
        for text in items:
            fh.write(json.dumps({"text": text}) + "\n")
    return target


__all__ = [
    "Dataset",
    "IterableTextDataset",
    "TextDataset",
    "cache_texts",
    "compute_dataset_hash",
    "to_hf_dataset",
]
