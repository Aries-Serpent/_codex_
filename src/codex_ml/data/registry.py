"""Simple dataset registry for codex_ml."""

from __future__ import annotations

from typing import Any, Callable

from codex_ml.registry.base import Registry

data_loader_registry = Registry("data_loader", entry_point_group="codex_ml.data_loaders")


def register_dataset(
    name: str, *, override: bool = False
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator to register a dataset loader."""

    return data_loader_registry.register(name, override=override)


def get_dataset(name: str, **kwargs: Any) -> Any:
    """Retrieve a dataset by name."""

    loader = data_loader_registry.get(name)
    return loader(**kwargs) if callable(loader) else loader


def list_datasets() -> list[str]:
    return data_loader_registry.list()


@register_dataset("lines")
def load_line_dataset(path: str) -> list[str]:
    """Load a simple line-based text dataset."""
    with open(path, "r", encoding="utf-8") as f:
        return [line.rstrip("\n") for line in f]
