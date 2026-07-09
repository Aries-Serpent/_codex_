"""Minimal data handling utilities for `_codex_`.

This module provides a tiny "spine" for data handling:

- DatasetSpec: describes a logical dataset.
- A registry mapping dataset_name -> DatasetSpec.
- A simple line-based text dataset loader as an example.

The intent is not to cover all data sources, but to:

- Provide a stable place for dataset definitions.
- Support deterministic splits via IDs.
- Keep everything local/offline and dependency-light.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

from collections.abc import Callable, Iterable, Sequence  # noqa: E402
from dataclasses import dataclass, field  # noqa: E402
from pathlib import Path  # noqa: E402


@dataclass
class DatasetSpec:
    """Description of a dataset used in `_codex_`.

    Fields:
        name: Logical name (e.g. "dummy", "local_text").
        root: Root directory or file path.
        loader: Callable that returns an iterable of records.
        description: Human-readable description.
    """

    name: str
    root: Path
    loader: Callable[[Path], Iterable[str]]
    description: str = ""
    tags: list[str] = field(default_factory=list)


# Global registry: dataset_name -> spec
_DATASET_REGISTRY: dict[str, DatasetSpec] = {}


def register_dataset(spec: DatasetSpec, overwrite: bool = False) -> None:
    """Register a dataset spec by name."""

    if not overwrite and spec.name in _DATASET_REGISTRY:
        raise ValueError(f"Dataset {spec.name!r} already registered")
    _DATASET_REGISTRY[spec.name] = spec


def get_dataset_spec(name: str) -> DatasetSpec:
    """Return the DatasetSpec for a given dataset name."""

    try:
        return _DATASET_REGISTRY[name]
    except KeyError as e:
        type(e).__name__
        logger.debug("KeyError: <ERROR_TYPE>")
        logger.warning("KeyError: <ERROR_TYPE>", exc_info=True)
        raise KeyError(f"Dataset {name!r} is not registered") from None


def list_datasets() -> Sequence[str]:
    """Return the names of all registered datasets."""

    return sorted(_DATASET_REGISTRY.keys())


def _load_line_text_dataset(root: Path) -> Iterable[str]:
    """Example text dataset loader.

    If `root` is a file:
        - Return its non-empty lines.
    If `root` is a directory:
        - Recursively find `*.txt` files and yield non-empty lines.
    """

    root = root.expanduser().resolve()
    paths = [root] if root.is_file() else sorted(root.rglob("*.txt"))
    for p in paths:
        for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line:
                continue
            yield line


def ensure_default_datasets(data_root: Path | None = None) -> None:
    """Ensure a small set of default DatasetSpec entries.

    This is safe to call multiple times.
    """

    base = Path(data_root or "data").expanduser().resolve()

    dummy_root = base / "dummy"
    register_dataset(
        DatasetSpec(
            name="dummy",
            root=dummy_root,
            loader=_load_line_text_dataset,
            description="Dummy local text dataset under data/dummy.",
            tags=["local", "text", "example"],
        ),
        overwrite=True,
    )

    local_text_root = base / "local_text"
    register_dataset(
        DatasetSpec(
            name="local_text",
            root=local_text_root,
            loader=_load_line_text_dataset,
            description="Generic local text dataset under data/local_text.",
            tags=["local", "text"],
        ),
        overwrite=True,
    )
