"""
Registry Module

This module provides functionality for registry.

Usage:
    from data.registry import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import importlib  # noqa: E402
from collections.abc import Callable  # noqa: E402
from typing import Any  # noqa: E402

try:  # pragma: no cover - torch is optional
    import torch

    DataLoader = torch.utils.data.DataLoader
    TensorDataset = torch.utils.data.TensorDataset
    random_split = torch.utils.data.random_split
except (ImportError, AttributeError):  # pragma: no cover - fallback stubs when torch is absent
    torch = None  # type: ignore[assignment]
    DataLoader = None
    TensorDataset = None
    random_split = None

_REGISTRY: dict[str, Callable[..., Any]] = {}


class DatasetRegistryError(RuntimeError):
    """Raised when dataset registry operations fail."""


def register(name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Register ``fn`` under ``name`` and return the original callable."""

    normalized = name.strip().lower()
    if not normalized:
        raise ValueError("dataset name must be a non-empty string")

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        if normalized in _REGISTRY:
            raise DatasetRegistryError(f"Dataset '{name}' already registered")
        _REGISTRY[normalized] = fn
        return fn

    return decorator


def register_dataset(name: str, fn: Callable[..., Any]) -> None:
    """Register ``fn`` explicitly without using the decorator helper."""

    if not callable(fn):
        raise TypeError("dataset builder must be callable")
    register(name)(fn)


def get(name: str) -> Callable[..., Any]:
    """Return the dataset builder registered under ``name``."""

    normalized = name.strip().lower()
    try:
        return _REGISTRY[normalized]
    except KeyError as exc:  # pragma: no cover - small helper
        raise DatasetRegistryError(
            f"Unknown dataset '{name}'. Available: {sorted(_REGISTRY)}"
        ) from exc


def list_datasets() -> list[str]:
    """Return the list of registered dataset names."""

    return sorted(_REGISTRY)


def build(name: str, *args: Any, **kwargs: Any) -> Any:
    """Convenience helper returning ``get(name)(*args, **kwargs)``."""

    builder = get(name)
    return builder(*args, **kwargs)


@register("synthetic_classification")
def _synthetic_classification_dataset(
    *,
    num_samples: int = 32,
    input_dim: int = 8,
    num_classes: int = 2,
    batch_size: int = 8,
    seed: int = 0,
    val_split: float = 0.25,
) -> tuple[Any, Any | None]:
    """Return simple synthetic classification dataloaders for smoke tests."""

    global torch, DataLoader, TensorDataset, random_split
    if torch is None or DataLoader is None or TensorDataset is None:
        try:
            torch = importlib.import_module("torch")
        except (ImportError, AttributeError) as exc:  # pragma: no cover - optional dependency guard
            raise DatasetRegistryError("torch is required for synthetic datasets") from exc
        torch_utils = getattr(torch, "utils", None)
        data_module = getattr(torch_utils, "data", None)
        if data_module is None:
            raise DatasetRegistryError("torch.utils.data not available")
        DataLoader = getattr(data_module, "DataLoader", None)
        TensorDataset = getattr(data_module, "TensorDataset", None)
        random_split = getattr(data_module, "random_split", None)
    if DataLoader is None or TensorDataset is None:
        raise DatasetRegistryError("torch.utils.data components unavailable")
    generator = torch.Generator().manual_seed(int(seed))
    features = torch.randn(num_samples, input_dim, generator=generator)
    labels = torch.randint(num_classes, (num_samples,), generator=generator)
    dataset = TensorDataset(features, labels)
    if val_split <= 0 or random_split is None:
        train_dataset = dataset
        val_dataset = None
    else:
        val_size = max(1, int(len(dataset) * float(val_split)))
        val_size = min(val_size, len(dataset) - 1) if len(dataset) > 1 else val_size
        if val_size <= 0:
            train_dataset = dataset
            val_dataset = None
        else:
            train_size = len(dataset) - val_size
            if train_size <= 0:
                train_size = len(dataset) - 1
                val_size = len(dataset) - train_size
            train_dataset, val_dataset = random_split(
                dataset,
                [train_size, val_size],
                generator=torch.Generator().manual_seed(int(seed) + 1),
            )
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = (
        DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
        if val_dataset is not None
        else None
    )
    return train_loader, val_loader


__all__ = [
    "DatasetRegistryError",
    "build",
    "get",
    "list_datasets",
    "register",
    "register_dataset",
]
