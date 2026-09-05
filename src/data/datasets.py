"""Utility datasets and data loader helpers for Codex smoke tests."""

from __future__ import annotations

import logging
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol, cast

from utils.error_logging import append_error

logger = logging.getLogger(__name__)

if TYPE_CHECKING:  # pragma: no cover - imported for typing only
    from torch.utils.data import DataLoader as TorchDataLoaderType
    from torch.utils.data import Dataset as TorchDatasetType
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
    ) -> dict[str, Any]:
        pass


torch: Any
try:  # pragma: no cover - optional dependency guard
    import torch as _torch_mod
except (ImportError, AttributeError):  # pragma: no cover - allow repository usage without torch
    torch = None
else:
    torch = _torch_mod

try:  # pragma: no cover - guard for environments without torch data utilities
    from torch.utils.data import DataLoader as TorchDataLoader
    from torch.utils.data import Dataset as TorchDataset
    from torch.utils.data import TensorDataset as TorchTensorDataset
    from torch.utils.data import random_split as torch_random_split
except (ImportError, AttributeError):  # pragma: no cover - provide graceful degradation
    TorchDataLoader = cast(Any, None)  # type: ignore[misc]
    TorchDataset = cast(Any, None)  # type: ignore[misc]
    TorchTensorDataset = cast(Any, None)  # type: ignore[misc]
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


@dataclass(slots=True)
class DataLoaderConfig:
    """User-facing config for text classification helpers."""

    file_path: str = ""
    batch_size: int = 8
    max_length: int = 128
    validation_split: float = 0.2
    seed: int = 42
    num_workers: int = 0

    def __post_init__(self) -> None:
        if int(self.batch_size) <= 0:
            raise ValueError("batch_size must be positive")
        if int(self.num_workers) < 0:
            raise ValueError("num_workers must be non-negative")

    def to_data_config(self) -> DataConfig:
        if not 0 <= float(self.validation_split) < 1:
            raise ValueError("validation_split must be in [0, 1)")
        split_ratio = (1 - float(self.validation_split), float(self.validation_split))
        return DataConfig(
            dataset_path=self.file_path,
            validation_path=None,
            batch_size=int(self.batch_size),
            split_ratio=split_ratio,
            shuffle=True,
            max_length=int(self.max_length),
            seed=int(self.seed),
            num_workers=0,
        )


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
                    except (IOError, OSError, ModuleNotFoundError, ImportError) as exc:
                        type(exc).__name__
                        logger.debug("Exception: <ERROR_TYPE>")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except (IOError, OSError, ModuleNotFoundError, ImportError) as exc:
            type(exc).__name__
            logger.debug("Exception: <ERROR_TYPE>")
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
) -> dict[str, Any]:
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
    except (ValueError, TypeError, RuntimeError) as exc:
        type(exc).__name__
        logger.debug("Exception: <ERROR_TYPE>")
        append_error("3.5", "tokenize batch", str(exc), f"texts={len(texts)}")
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    labels_tensor = torch.tensor(labels, dtype=torch.long)
    return input_ids, labels_tensor


def _coerce_tokenizer(tokenizer: Any) -> BatchTokenizer:
    batch_encode = getattr(tokenizer, "batch_encode_plus", None)
    if batch_encode is None and callable(tokenizer):
        batch_encode = tokenizer
    if batch_encode is None:
        message = "tokenizer must provide 'batch_encode_plus' or be callable"
        raise AttributeError(message)
    return cast(BatchTokenizer, batch_encode)


def _build_dataloaders_from_config(
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
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)  # type: ignore[return-value]

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


def build_dataloaders(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        if any(r <= 0 for r in split_ratio):
            raise ValueError("split ratios must be positive")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split ratios must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def build_text_classification_dataloaders(
    tokenizer: Any, config: DataLoaderConfig
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Compat shim that accepts :class:`DataLoaderConfig` inputs."""

    return _build_dataloaders_from_config(tokenizer, config.to_data_config())


def load_text_classification_dataset(path: str | Path) -> TextClassificationDataset:
    """Load a TSV text classification dataset."""

    return TextClassificationDataset(str(path))


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


def split_dataset(
    dataset: TorchDatasetType,
    split_ratio: Sequence[float] = (0.8, 0.2),
    *,
    seed: int = 42,
) -> tuple[Any, ...]:
    """Split a torch Dataset into subsets by ratio.

    Args:
        dataset:     Dataset to split.
        split_ratio: Fractions for each split (must sum to 1.0).
        seed:        Random seed for reproducibility.

    Returns:
        Tuple of dataset subsets matching ``split_ratio`` length.

    Raises:
        ValueError: If the dataset is empty, ratios are invalid, or the
                    dataset is too small to produce valid splits.
    """
    if torch is None or torch_random_split is None:
        raise RuntimeError("torch is required for split_dataset")
    try:
        n = len(dataset)
    except Exception:
        n = 0
    if n == 0:
        raise ValueError("Cannot split empty dataset")
    lengths = _compute_lengths(n, split_ratio)
    if any(ln == 0 for ln in lengths[1:]):
        raise ValueError("Insufficient samples for validation split")
    generator = torch.Generator().manual_seed(int(seed))
    parts = torch_random_split(dataset, lengths, generator=generator)
    return tuple(parts)


def default_collate(batch: list[dict[str, Any]]) -> dict[str, Any]:
    """Collate a list of dicts into a batched dict of tensors.

    Requires every sample to contain an ``input_ids`` key.

    Args:
        batch: List of sample dicts, each containing tensor values.

    Returns:
        Dict with each key mapped to a stacked tensor.

    Raises:
        KeyError: If any sample is missing the ``input_ids`` key.
    """
    if not batch:
        return {}
    # Validate required key
    for sample in batch:
        if "input_ids" not in sample:
            raise KeyError("input_ids")
    keys = batch[0].keys()
    if torch is None:
        raise RuntimeError("torch is required for default_collate")
    return {k: torch.stack([s[k] for s in batch]) for k in keys}


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


def parse_tsv_dataset(path: str | Path) -> list[tuple[str, int]]:
    """Parse TSV file with text and labels (text<tab>label format).

    Args:
        path: Path to TSV file.

    Returns:
        List of (text, label) tuples.  Malformed rows (no tab) are skipped
        unless the *first* non-empty line is malformed, in which case a
        ``ValueError`` is raised so callers can detect corrupt files early.

    Raises:
        ValueError: If the file contains no tab-separated rows at all and
                    at least one non-empty line exists (``"Invalid TSV format"``).
    """
    result: list[tuple[str, int]] = []
    has_any_line = False
    file_path = Path(path)
    with file_path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            has_any_line = True
            parts = line.split("\t")
            if len(parts) < 2:
                if not result:
                    raise ValueError(
                        f"Invalid TSV format: no tab separator found in line: {line!r}"
                    )
                continue  # skip malformed rows after valid ones
            text = parts[0]
            try:
                label = int(parts[1])
            except ValueError:
                continue
            result.append((text, label))
    if has_any_line and not result:
        raise ValueError("Invalid TSV format: no valid tab-separated rows found")
    return result


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
    "parse_tsv_dataset",  # Added for test compatibility
    "tiny_tensor_dataset",
]
