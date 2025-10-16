"""Minimal dataset utilities for text classification experiments."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover - typing only
    from torch.utils.data import Dataset as TorchDatasetType
    from torch.utils.data import Subset

import torch
from utils.error_logging import append_error

try:  # pragma: no cover - optional torch dependency
    import torch
except Exception:  # pragma: no cover - guard for stub environments
    torch = None  # type: ignore[assignment]

try:  # pragma: no cover - guard for stub environments
    _TORCH_DATA_SPEC = util.find_spec("torch.utils.data")
except (ImportError, ValueError):
    _TORCH_DATA_SPEC = None
if _TORCH_DATA_SPEC is not None:  # pragma: no cover - executed when torch provides data utilities
    _torch_data_module = import_module("torch.utils.data")
    TorchDataLoader = getattr(_torch_data_module, "DataLoader", None)
    TorchDataset = getattr(_torch_data_module, "Dataset", None)
    TorchTensorDataset = getattr(_torch_data_module, "TensorDataset", None)
    torch_random_split = getattr(_torch_data_module, "random_split", None)
else:  # pragma: no cover - executed in stub environments
    TorchDataLoader = None  # type: ignore
    TorchDataset = None  # type: ignore
    TorchTensorDataset = None  # type: ignore
    torch_random_split = None  # type: ignore

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


def _compute_lengths(n: int, lengths_or_fracs: Sequence[int | float]) -> list[int]:
    """Normalise a sequence of lengths or fractions to integer lengths."""

    if not lengths_or_fracs:
        raise ValueError("lengths_or_fracs must be non-empty")
    first = lengths_or_fracs[0]
    if isinstance(first, float) or any(isinstance(x, float) for x in lengths_or_fracs):
        fracs = [float(x) for x in lengths_or_fracs]
        total = sum(fracs)
        if not (0.999 <= total <= 1.001):
            raise ValueError("fractions must sum to 1.0")
        lengths = [int(n * frac) for frac in fracs]
        remainder = n - sum(lengths)
        idx = 0
        while remainder > 0:
            lengths[idx % len(lengths)] += 1
            remainder -= 1
            idx += 1
        return lengths
    return [int(x) for x in lengths_or_fracs]


def deterministic_split(
    dataset: TorchDatasetType,
    lengths_or_fracs: Sequence[int | float],
    *,
    seed: int = 1337,
) -> tuple[Subset, ...]:
    """Deterministically split a dataset using a seeded torch.Generator."""

    if torch is None or torch_random_split is None:
        raise RuntimeError("torch is required for deterministic_split")
    count = len(dataset)
    lengths = _compute_lengths(count, lengths_or_fracs)
    generator = torch.Generator().manual_seed(int(seed))
    parts = torch_random_split(dataset, lengths, generator=generator)
    return tuple(parts)


def tiny_tensor_dataset(
    n: int = 32,
    d_in: int = 8,
    n_classes: int = 4,
) -> TorchTensorDataset:
    """Construct a small synthetic dataset for deterministic smoke tests."""

    if torch is None or TorchTensorDataset is None:
        raise RuntimeError("torch is required for tiny_tensor_dataset")
    inputs = torch.randn(n, d_in)
    targets = torch.randint(0, n_classes, (n,))
    return TorchTensorDataset(inputs, targets)


__all__ = [
    "TextClassificationDataset",
    "build_dataloaders",
    "deterministic_split",
    "tiny_tensor_dataset",
]
