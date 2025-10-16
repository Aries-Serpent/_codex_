"""Minimal dataset utilities for text classification experiments."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

import torch
from utils.error_logging import append_error

try:
    from torch.utils.data import DataLoader, Dataset, random_split
except Exception as exc:  # pragma: no cover - torch missing
    append_error("3.5", "import torch utils", str(exc), "torch.utils.data dependency missing")
    DataLoader = None  # type: ignore[assignment]
    random_split = None  # type: ignore[assignment]
    TorchDataset = object  # type: ignore[assignment]
else:
    TorchDataset = Dataset

BaseDataset = TorchDataset


@dataclass(slots=True)
class DataConfig:
    """Configuration describing how to prepare data loaders."""

    dataset_path: str
    validation_path: str | None = None
    batch_size: int = 8
    split_ratio: Sequence[float] = (0.8, 0.2)
    shuffle: bool = True
    max_length: int = 128
    seed: int = 42
    num_workers: int = 0


class TextClassificationDataset(BaseDataset):
    """Simple TSV loader producing ``(text, label)`` tuples."""

    def __init__(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            append_error("3.5", "dataset load", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> tuple[str, int]:
        return self.samples[idx]


def _collate_text_batch(
    tokenizer: Callable[[Sequence[str]], dict],
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[torch.Tensor, torch.Tensor]:
    texts, labels = zip(*batch, strict=False)
    try:
        encodings = tokenizer(
            list(texts),
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
    except Exception as exc:
        append_error("3.5", "tokenize batch", str(exc), f"texts={len(texts)}")
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(labels, dtype=torch.long)


def build_dataloaders(tokenizer, config: DataConfig) -> tuple[DataLoader, DataLoader | None]:
    """Create train/validation dataloaders according to ``config``."""

    if DataLoader is None or random_split is None:
        raise RuntimeError("torch.utils.data is required to build dataloaders")

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_set = TextClassificationDataset(config.validation_path)
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1)) if len(dataset) > 1 else len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_len = len(dataset)
        generator = torch.Generator().manual_seed(config.seed)
        if val_len > 0:
            train_set, val_set = random_split(dataset, [train_len, val_len], generator=generator)
        else:
            train_set = dataset
            val_set = None

    batch_encode = getattr(tokenizer, "batch_encode_plus", None)
    if batch_encode is None and callable(tokenizer):
        batch_encode = tokenizer
    if batch_encode is None:
        raise AttributeError("tokenizer must provide 'batch_encode_plus' or '__call__'")

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[torch.Tensor, torch.Tensor]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = DataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: DataLoader | None
    if val_set is None or len(val_set) == 0:
        val_loader = None
    else:
        val_loader = DataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


__all__ = ["DataConfig", "TextClassificationDataset", "build_dataloaders"]
