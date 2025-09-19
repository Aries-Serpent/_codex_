"""Dataset registry with entry-point discovery for ``codex_ml``."""

from __future__ import annotations

import hashlib
import json
import random
from importlib import metadata
from pathlib import Path
from typing import Any, Callable, Dict


class _DatasetRegistry:
    """Registry that supports explicit and entry-point registrations."""

    _ENTRY_POINT_GROUP = "codex_ml.data_loaders"

    def __init__(self) -> None:
        self._items: Dict[str, Any] = {}
        self._entry_points_loaded = False
        self._failed_entry_points: Dict[str, Exception] = {}

    def register(
        self, name: str, obj: Any | None = None, *, override: bool = False
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        key = self._normalise(name)

        def decorator(target: Callable[..., Any]) -> Callable[..., Any]:
            if not override and key in self._items:
                raise ValueError(f"dataset '{name}' already registered")
            self._items[key] = target
            return target

        if obj is not None:
            return decorator(obj)
        return decorator

    def get(self, name: str) -> Any:
        key = self._normalise(name)
        if key not in self._items:
            self._ensure_entry_points_loaded()

        if key in self._items:
            return self._items[key]

        if key in self._failed_entry_points:
            exc = self._failed_entry_points[key]
            raise RuntimeError(f"dataset '{name}' failed to load from entry point") from exc

        raise KeyError(f"dataset '{name}' is not registered")

    def list(self) -> list[str]:
        self._ensure_entry_points_loaded()
        return sorted(self._items.keys())

    def _ensure_entry_points_loaded(self) -> None:
        if self._entry_points_loaded:
            return

        try:
            entry_points = metadata.entry_points(group=self._ENTRY_POINT_GROUP)
        except Exception:  # pragma: no cover - metadata backend failure
            entry_points = ()

        for entry_point in entry_points:
            key = self._normalise(entry_point.name)
            if key in self._items:
                continue
            try:
                value = entry_point.load()
            except Exception as exc:  # pragma: no cover - plugin failure
                self._failed_entry_points[key] = exc
                continue
            self._items[key] = value

        self._entry_points_loaded = True

    def _normalise(self, name: str) -> str:
        return name.lower()


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
    write_manifest: bool | None = None,
    manifest_path: str | Path | None = None,
) -> list[str]:
    """Load a line-based dataset with deterministic shuffling and manifest logging."""

    dataset_path = Path(path)
    if not dataset_path.exists():
        raise FileNotFoundError(f"dataset not found: {dataset_path}")

    source_bytes = dataset_path.read_bytes()
    source_checksum = hashlib.sha256(source_bytes).hexdigest()

    lines = source_bytes.decode("utf-8").splitlines()
    if shuffle:
        rng = random.Random(seed)
        rng.shuffle(lines)

    should_write_manifest = write_manifest
    if should_write_manifest is None:
        should_write_manifest = manifest_path is not None

    if should_write_manifest:
        manifest_target: Path
        if manifest_path is not None:
            manifest_target = Path(manifest_path)
        elif dataset_path.suffix:
            manifest_target = dataset_path.with_suffix(f"{dataset_path.suffix}.manifest.json")
        else:
            manifest_target = dataset_path.with_name(dataset_path.name + ".manifest.json")
        manifest_target.parent.mkdir(parents=True, exist_ok=True)
        shuffled_checksum = hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()

        manifest_payload = {
            "schema": MANIFEST_SCHEMA,
            "source": str(dataset_path.resolve()),
            "num_records": len(lines),
            "seed": seed,
            "shuffle": shuffle,
            "source_checksum": source_checksum,
            "shuffled_checksum": shuffled_checksum,
            "checksum": shuffled_checksum,
        }
        manifest_target.write_text(json.dumps(manifest_payload, indent=2), encoding="utf-8")

    return lines
