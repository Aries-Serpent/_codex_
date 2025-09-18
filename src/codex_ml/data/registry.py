"""Simple dataset registry for codex_ml."""

from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path
from typing import Any, Callable, Dict


class _DatasetRegistry:
    """Lightweight registry used for built-in dataset loaders."""

    def __init__(self) -> None:
        self._items: Dict[str, Any] = {}

    def register(
        self, name: str, obj: Any | None = None, *, override: bool = False
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(target: Callable[..., Any]) -> Callable[..., Any]:
            if not override and name in self._items:
                raise ValueError(f"dataset '{name}' already registered")
            self._items[name] = target
            return target

        if obj is not None:
            return decorator(obj)
        return decorator

    def get(self, name: str) -> Any:
        if name not in self._items:
            raise KeyError(f"dataset '{name}' is not registered")
        return self._items[name]

    def list(self) -> list[str]:
        return sorted(self._items.keys())


data_loader_registry = _DatasetRegistry()


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


MANIFEST_SCHEMA = "https://codexml.ai/schemas/dataset_manifest.v1"


@register_dataset("lines")
def load_line_dataset(
    path: str,
    *,
    seed: int = 42,
    shuffle: bool = True,
    write_manifest: bool = True,
    manifest_path: str | Path | None = None,
) -> list[str]:
    """Load a line-based dataset with deterministic shuffling and manifest logging."""

    dataset_path = Path(path)
    if not dataset_path.exists():
        raise FileNotFoundError(f"dataset not found: {dataset_path}")

    lines = dataset_path.read_text(encoding="utf-8").splitlines()
    if shuffle:
        rng = random.Random(seed)
        rng.shuffle(lines)

    if write_manifest:
        manifest_target: Path
        if manifest_path is not None:
            manifest_target = Path(manifest_path)
        elif dataset_path.suffix:
            manifest_target = dataset_path.with_suffix(f"{dataset_path.suffix}.manifest.json")
        else:
            manifest_target = dataset_path.with_name(dataset_path.name + ".manifest.json")
        manifest_target.parent.mkdir(parents=True, exist_ok=True)
        manifest_payload = {
            "schema": MANIFEST_SCHEMA,
            "source": str(dataset_path.resolve()),
            "num_records": len(lines),
            "seed": seed,
            "shuffle": shuffle,
            "checksum": hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest(),
        }
        manifest_target.write_text(json.dumps(manifest_payload, indent=2), encoding="utf-8")

    return lines
