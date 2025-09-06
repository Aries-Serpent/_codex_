from __future__ import annotations

from typing import Dict, Iterable, Iterator, Sequence

import numpy as np
import torch

try:  # optional dependency
    from datasets import Dataset  # type: ignore
except Exception:  # pragma: no cover - optional dep missing
    Dataset = None  # type: ignore[assignment]


def _encode_text(tokenizer, text: str, max_length: int) -> Dict[str, np.ndarray]:
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

    def __init__(self, items: Sequence[str], tokenizer, max_length: int) -> None:
        self.data = [_encode_text(tokenizer, t, max_length) for t in items]

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self.data)

    def __getitem__(self, idx: int) -> Dict[str, np.ndarray]:  # pragma: no cover - trivial
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

    def __iter__(self) -> Iterator[Dict[str, np.ndarray]]:
        if self.prefetch_k <= 0:
            for text in self.stream:
                yield _encode_text(self.tokenizer, text, self.max_length)
        else:
            buf: list[Dict[str, np.ndarray]] = []
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
