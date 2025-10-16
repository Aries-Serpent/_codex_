"""Lightweight text classification dataset helpers."""

from __future__ import annotations

import random
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass
from importlib import import_module, util
from pathlib import Path
from typing import Any

from codex_ml.utils.error_log import log_error

try:  # pragma: no cover - guard for stub environments
    _TORCH_DATA_SPEC = util.find_spec("torch.utils.data")
except (ImportError, ValueError):
    _TORCH_DATA_SPEC = None
if _TORCH_DATA_SPEC is not None:  # pragma: no cover - executed when torch provides data utilities
    _torch_data_module = import_module("torch.utils.data")
    TorchDataLoader = getattr(_torch_data_module, "DataLoader", None)
    TorchDataset = getattr(_torch_data_module, "Dataset", None)
else:  # pragma: no cover - executed in stub environments
    TorchDataLoader = None  # type: ignore
    TorchDataset = None  # type: ignore


@dataclass(slots=True)
class TextExample:
    """Simple text/label pair."""

    text: str
    label: int


class TextClassificationDataset:
    """Dataset backed by a TSV file (``text`` TAB ``label``)."""

    def __init__(self, file_path: str | Path) -> None:
        self._path = Path(file_path)
        self._examples: list[TextExample] = []
        self._load()

    def _load(self) -> None:
        try:
            with self._path.open("r", encoding="utf-8") as handle:
                for index, line in enumerate(handle, start=1):
                    stripped = line.strip()
                    if not stripped:
                        continue
                    try:
                        text, label = stripped.split("\t", maxsplit=1)
                        self._examples.append(TextExample(text=text, label=int(label)))
                    except Exception as exc:
                        log_error("data.datasets", str(exc), f"parse_line:{self._path}:{index}")
                        raise
        except OSError as exc:
            log_error("data.datasets", str(exc), f"open:{self._path}")
            raise

    def __len__(self) -> int:  # pragma: no cover - exercised implicitly
        return len(self._examples)

    def __getitem__(self, index: int) -> TextExample:  # pragma: no cover - exercised implicitly
        return self._examples[index]


class _FallbackDataset(TextClassificationDataset):
    """Compatibility shim providing the Dataset protocol when torch is absent."""

    pass


class _SimpleBatchLoader:
    """Minimal DataLoader replacement used when Torch's loader is unavailable."""

    def __init__(
        self,
        dataset: TextClassificationDataset,
        indices: Sequence[int],
        batch_size: int,
        *,
        shuffle: bool,
        collate_fn,
    ) -> None:
        self._dataset = dataset
        self._indices = list(indices)
        self._batch_size = batch_size
        self._shuffle = shuffle
        self._collate = collate_fn

    def __iter__(self) -> Iterator[Any]:
        indices = list(self._indices)
        if self._shuffle:
            random.shuffle(indices)
        for start in range(0, len(indices), self._batch_size):
            batch_indices = indices[start : start + self._batch_size]
            batch = [self._dataset[i] for i in batch_indices]
            yield self._collate(batch)

    def __len__(self) -> int:
        return max(1, (len(self._indices) + self._batch_size - 1) // self._batch_size)


def _resolve_dataset_class() -> type:
    if TorchDataset is None:
        return _FallbackDataset
    try:
        return type("WrappedDataset", (TorchDataset, TextClassificationDataset), {})
    except Exception:  # pragma: no cover - extremely defensive
        return _FallbackDataset


def _resolve_dataloader_class():
    if TorchDataLoader is None:
        return _SimpleBatchLoader
    return TorchDataLoader


class _SubsetDataset:
    """Subset view backed by explicit indices."""

    def __init__(self, dataset: TextClassificationDataset, indices: Sequence[int]) -> None:
        self._dataset = dataset
        self._indices = list(indices)

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self._indices)

    def __getitem__(self, index: int) -> TextExample:  # pragma: no cover - trivial
        return self._dataset[self._indices[index]]


def build_dataloaders(
    file_path: str | Path,
    tokenizer: Any,
    *,
    batch_size: int = 8,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    max_length: int = 128,
) -> tuple[Iterable[Any], Iterable[Any] | None]:
    """Create train/validation dataloaders for a TSV dataset."""

    if abs(sum(split_ratio) - 1.0) > 1e-6:
        raise ValueError("split_ratio must sum to 1.0")
    dataset_cls = _resolve_dataset_class()
    dataset: TextClassificationDataset = dataset_cls(file_path)  # type: ignore[call-arg]
    if len(dataset) == 0:
        raise ValueError("dataset is empty")
    train_size = max(1, int(len(dataset) * split_ratio[0]))
    indices = list(range(len(dataset)))
    random.shuffle(indices)
    train_indices = indices[:train_size]
    val_indices = indices[train_size:]

    def _collate(batch: Sequence[TextExample]) -> tuple[Any, Any]:
        texts = [item.text for item in batch]
        labels = [item.label for item in batch]
        encodings = tokenizer.batch_encode_plus(
            texts,
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
        input_ids = encodings.get("input_ids")
        return input_ids, encodings.get("labels", labels)

    dataloader_cls = _resolve_dataloader_class()
    if dataloader_cls is _SimpleBatchLoader:
        train_loader = dataloader_cls(
            dataset, train_indices, batch_size=batch_size, shuffle=shuffle, collate_fn=_collate
        )
        val_loader = (
            dataloader_cls(
                dataset, val_indices, batch_size=batch_size, shuffle=False, collate_fn=_collate
            )
            if val_indices
            else None
        )
    else:
        train_dataset = _SubsetDataset(dataset, train_indices)
        val_dataset = _SubsetDataset(dataset, val_indices) if val_indices else None
        train_loader = dataloader_cls(
            train_dataset, batch_size=batch_size, shuffle=shuffle, collate_fn=_collate
        )
        val_loader = (
            dataloader_cls(val_dataset, batch_size=batch_size, shuffle=False, collate_fn=_collate)
            if val_dataset
            else None
        )
    return train_loader, val_loader


__all__ = [
    "TextClassificationDataset",
    "build_dataloaders",
]
