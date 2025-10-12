from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any


class Registry:
    """Simple string-to-callable registry with decorator support."""

    def __init__(self, name: str) -> None:
        self.name = name
        self._store: dict[str, Callable[..., Any]] = {}

    def register(
        self, key: str | None = None
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            registry_key = key or fn.__name__
            if registry_key in self._store:
                raise KeyError(f"{self.name}: key already registered: {registry_key}")
            self._store[registry_key] = fn
            return fn

        return decorator

    def add(self, key: str, fn: Callable[..., Any]) -> None:
        if key in self._store:
            raise KeyError(f"{self.name}: key already registered: {key}")
        self._store[key] = fn

    def get(self, key: str) -> Callable[..., Any]:
        if key not in self._store:
            raise KeyError(f"{self.name}: not found: {key}")
        return self._store[key]

    def keys(self) -> list[str]:
        return list(self._store.keys())

    def __contains__(self, key: str) -> bool:  # pragma: no cover - trivial
        return key in self._store

    def items(self) -> Iterable[tuple[str, Callable[..., Any]]]:  # pragma: no cover - convenience
        return self._store.items()


MODELS = Registry("models")
DATASETS = Registry("datasets")
METRICS = Registry("metrics")
