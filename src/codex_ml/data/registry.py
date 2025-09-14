"""Simple dataset registry for codex_ml."""

from __future__ import annotations

from typing import Any, Callable, Dict

_DATASETS: Dict[str, Callable[..., Any]] = {}


def register_dataset(name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator to register a dataset loader."""

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        _DATASETS[name] = fn
        return fn

    return decorator


def get_dataset(name: str, **kwargs: Any) -> Any:
    """Retrieve a dataset by name."""
    if name not in _DATASETS:
        raise ValueError(f"Dataset {name} not registered")
    return _DATASETS[name](**kwargs)


@register_dataset("lines")
def load_line_dataset(path: str) -> list[str]:
    """Load a simple line-based text dataset."""
    with open(path, "r", encoding="utf-8") as f:
        return [line.rstrip("\n") for line in f]
