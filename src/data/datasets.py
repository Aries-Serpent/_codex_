"""Utility datasets and DataLoader builders for lightweight text classification."""

from __future__ import annotations

import csv
import logging
from collections.abc import Mapping, MutableMapping, Sequence
from dataclasses import dataclass
from pathlib import Path

try:  # pragma: no cover - torch may be optional in some environments
    import torch
    from torch.utils.data import DataLoader, Dataset, random_split
except Exception:  # pragma: no cover - align with runtime contract
    torch = None  # type: ignore[assignment]

    class _DatasetStub:  # pragma: no cover - lightweight generic stand-in
        def __class_getitem__(cls, _item):
            return cls

    class _DataLoaderStub:  # pragma: no cover - minimal callable placeholder
        pass

    def _random_split_stub(*_args, **_kwargs):  # pragma: no cover - placeholder
        raise RuntimeError("torch random_split unavailable in stub mode")

    DataLoader = _DataLoaderStub  # type: ignore[assignment]
    Dataset = _DatasetStub  # type: ignore[assignment]
    random_split = _random_split_stub  # type: ignore[assignment]

LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class TextSample:
    text: str
    label: int


class TextClassificationDataset(Dataset[tuple[str, int]]):
    """Dataset backed by a TSV/CSV file with ``text`` and ``label`` columns."""

    def __init__(self, samples: Sequence[TextSample]):
        self._samples = list(samples)

    def __len__(self) -> int:  # pragma: no cover - trivial accessors
        return len(self._samples)

    def __getitem__(self, index: int) -> tuple[str, int]:
        sample = self._samples[index]
        return sample.text, sample.label


def _read_samples(path: Path) -> list[TextSample]:
    if not path.is_file():
        raise FileNotFoundError(f"Dataset file '{path}' does not exist")
    samples: list[TextSample] = []
    try:
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.reader(handle, delimiter="\t")
            for row_num, row in enumerate(reader, start=1):
                if not row:
                    continue
                if len(row) != 2:
                    raise ValueError(
                        f"Expected 2 columns (text, label) at line {row_num}, received {len(row)}"
                    )
                text, label = row
                samples.append(TextSample(text=text, label=int(label)))
    except Exception:
        LOGGER.exception("Failed to parse dataset file '%s'", path)
        raise
    if not samples:
        raise ValueError(f"Dataset file '{path}' did not yield any samples")
    return samples


def load_text_classification_dataset(path: str | Path) -> TextClassificationDataset:
    """Load a text classification dataset from disk."""

    if torch is None:
        raise RuntimeError("torch is required to load the text classification dataset")
    dataset_path = Path(path)
    samples = _read_samples(dataset_path)
    return TextClassificationDataset(samples)


@dataclass(slots=True)
class DataLoaderConfig:
    file_path: str
    batch_size: int = 8
    max_length: int = 128
    validation_split: float = 0.2
    shuffle: bool = True
    seed: int = 42
    num_workers: int = 0


def _encode_batch(
    tokenizer: Mapping[str, object],
    texts: Sequence[str],
    *,
    max_length: int,
) -> MutableMapping[str, torch.Tensor]:
    if hasattr(tokenizer, "batch_encode_plus"):
        encoded = tokenizer.batch_encode_plus(  # type: ignore[attr-defined]
            list(texts),
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
    elif callable(tokenizer):
        encoded = tokenizer(  # type: ignore[call-arg]
            list(texts),
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
    else:  # pragma: no cover - defensive branch for unexpected tokenizers
        raise TypeError("Tokenizer must provide batch_encode_plus or be callable")

    if not isinstance(encoded, Mapping):  # pragma: no cover - sanity guard
        raise TypeError("Tokenizer encoding must return a mapping")
    return {key: value for key, value in encoded.items() if isinstance(value, torch.Tensor)}


def build_text_classification_dataloaders(
    tokenizer: Mapping[str, object],
    config: DataLoaderConfig | Mapping[str, object],
) -> tuple[DataLoader[Mapping[str, torch.Tensor]], DataLoader[Mapping[str, torch.Tensor]] | None]:
    """Create train/validation DataLoaders for a TSV text classification dataset."""

    if torch is None:
        raise RuntimeError("torch is required to build DataLoaders")
    if isinstance(config, DataLoaderConfig):
        resolved = config
    else:
        data: MutableMapping[str, object]
        if hasattr(config, "to_container"):
            data = config.to_container(resolve=True)  # type: ignore[attr-defined]
        else:
            data = dict(config)
        resolved = DataLoaderConfig(**data)

    dataset = load_text_classification_dataset(resolved.file_path)
    val_fraction = max(0.0, min(resolved.validation_split, 1.0))

    if val_fraction == 0.0 or len(dataset) < 2:
        splits = [dataset]
    else:
        val_size = max(1, int(len(dataset) * val_fraction))
        train_size = max(1, len(dataset) - val_size)
        generator = torch.Generator().manual_seed(resolved.seed)
        splits = random_split(dataset, [train_size, val_size], generator=generator)

    def collate(batch: Sequence[tuple[str, int]]) -> Mapping[str, torch.Tensor]:
        texts, labels = zip(*batch, strict=False)
        encoded = _encode_batch(tokenizer, texts, max_length=resolved.max_length)
        encoded["labels"] = torch.tensor(labels, dtype=torch.long)
        return encoded

    train_dataset = splits[0]
    train_loader = DataLoader(
        train_dataset,
        batch_size=resolved.batch_size,
        shuffle=resolved.shuffle,
        num_workers=resolved.num_workers,
        collate_fn=collate,
    )

    val_loader: DataLoader[Mapping[str, torch.Tensor]] | None
    if len(splits) == 2:
        val_dataset = splits[1]
        val_loader = DataLoader(
            val_dataset,
            batch_size=resolved.batch_size,
            shuffle=False,
            num_workers=resolved.num_workers,
            collate_fn=collate,
        )
    else:
        val_loader = None

    return train_loader, val_loader


__all__ = [
    "DataLoaderConfig",
    "TextClassificationDataset",
    "build_text_classification_dataloaders",
    "load_text_classification_dataset",
]
