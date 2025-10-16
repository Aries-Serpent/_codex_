"""Utility datasets and data loader helpers for Codex smoke tests."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol, cast

from utils.error_logging import append_error

if TYPE_CHECKING:  # pragma: no cover - imported for typing only
    from torch.utils.data import (
        DataLoader as TorchDataLoaderType,
    )
    from torch.utils.data import (
        Dataset as TorchDatasetType,
    )
    from torch.utils.data import (
        Subset,
    )
else:  # pragma: no cover - runtime fallbacks when torch is unavailable
    TorchDataLoaderType = Any
    TorchDatasetType = Any
    Subset = Any


class BatchTokenizer(Protocol):
    """Callable producing tokeniser batches with arbitrary keyword arguments."""

    def __call__(
        self,
        texts: Sequence[str],
        /,
        *args: Any,
        **kwargs: Any,
    ) -> dict[str, Any]: ...


torch: Any
try:  # pragma: no cover - optional dependency guard
    import torch as _torch_mod
except Exception:  # pragma: no cover - allow repository usage without torch
    torch = None
else:
    torch = _torch_mod

try:  # pragma: no cover - guard for environments without torch data utilities
    from torch.utils.data import (
        DataLoader as TorchDataLoader,
    )
    from torch.utils.data import (
        Dataset as TorchDataset,
    )
    from torch.utils.data import (
        TensorDataset as TorchTensorDataset,
    )
    from torch.utils.data import (
        random_split as torch_random_split,
    )
except Exception:  # pragma: no cover - provide graceful degradation
    TorchDataLoader = cast(Any, None)
    TorchDataset = cast(Any, None)
    TorchTensorDataset = cast(Any, None)
    torch_random_split = cast(Any, None)

BaseDataset: type[Any]
if TorchDataset is not None:
    BaseDataset = TorchDataset
else:

    class _FallbackDataset:  # pragma: no cover - simple duck-typed fallback
        pass

    BaseDataset = _FallbackDataset

if TYPE_CHECKING:
    BaseDataset = TorchDatasetType


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

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self.samples)

    def __getitem__(self, idx: int) -> tuple[str, int]:  # pragma: no cover - trivial
        return self.samples[idx]


def _collate_text_batch(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
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


def _coerce_tokenizer(tokenizer: Any) -> BatchTokenizer:
    batch_encode = getattr(tokenizer, "batch_encode_plus", None)
    if batch_encode is None and callable(tokenizer):
        batch_encode = tokenizer
    if batch_encode is None:
        message = "tokenizer must provide 'batch_encode_plus' or be callable"
        raise AttributeError(message)
    return cast(BatchTokenizer, batch_encode)


def build_dataloaders(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
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
    """Deterministically split a dataset using a seeded ``torch.Generator``."""

    if torch is None or torch_random_split is None:
        raise RuntimeError("torch is required for deterministic_split")
    lengths = _compute_lengths(len(dataset), lengths_or_fracs)
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
    "DataConfig",
    "TextClassificationDataset",
    "build_dataloaders",
    "deterministic_split",
    "tiny_tensor_dataset",
]
