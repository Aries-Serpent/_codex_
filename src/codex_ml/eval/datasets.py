"""Helpers for constructing small evaluation datasets."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List

try:  # pragma: no cover - optional dependency
    from datasets import DatasetDict, load_from_disk  # isort: skip
    from datasets import load_dataset as hf_load_dataset  # isort: skip
    from datasets import load_dataset_builder as hf_load_dataset_builder  # isort: skip

    HAS_DATASETS = True
except Exception:  # pragma: no cover
    hf_load_dataset = load_from_disk = DatasetDict = hf_load_dataset_builder = None  # type: ignore
    HAS_DATASETS = False


@dataclass
class Example:
    input: str
    target: str


_PRESETS = {
    "toy_copy_task": [
        Example("hello", "hello"),
        Example("world", "world"),
    ],
    "tiny_wikitext": [
        Example("Anarchism is a political philosophy.", "Anarchism is a political philosophy."),
    ],
}


def load_dataset(
    name_or_path: str,
    max_samples: int | None = None,
    *,
    split: str | None = None,
) -> List[Example]:
    """Load a dataset by preset name, Hugging Face dataset, or JSONL/NDJSON file.

    Sources supported:
    - Built-in presets (toy_copy_task, tiny_wikitext)
    - Local JSONL/NDJSON files containing objects with at least input/target keys
    - Local datasets saved via datasets.DatasetDict.save_to_disk
    - Remote datasets via datasets.load_dataset

    Split selection rules:
    - For DatasetDict (local or remote), if split is provided, it is used.
      If split is None, prefer "train" when available; otherwise use the first available split.
    """
    if name_or_path in _PRESETS:
        data = list(_PRESETS[name_or_path])
    else:
        path = Path(name_or_path)
        # Plain JSONL/NDJSON file
        if path.suffix.lower() in {".ndjson", ".jsonl"} and path.is_file():
            data = [
                Example(**json.loads(line))
                for line in path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
        # datasets.DatasetDict saved to disk
        elif path.exists() and path.is_dir() and HAS_DATASETS:
            ds = load_from_disk(str(path))
            # If it's a DatasetDict, select split
            if isinstance(ds, DatasetDict) or hasattr(ds, "keys"):
                if split is None:
                    chosen = "train" if "train" in ds else next(iter(ds.keys()))
                else:
                    chosen = split
                if chosen not in ds:
                    raise ValueError(
                        f"Split '{chosen}' not found in dataset; available: {list(ds.keys())}"
                    )
                ds = ds[chosen]
            # Map rows to Example, with graceful fallbacks
            data = [
                Example(
                    str(row.get("input", row.get("text", ""))),
                    str(row.get("target", row.get("text", ""))),
                )
                for row in ds
            ]
        # Remote dataset via datasets.load_dataset
        elif HAS_DATASETS:
            # Determine split when not explicitly provided
            if split is None:
                try:
                    builder = hf_load_dataset_builder(name_or_path)  # type: ignore[misc]
                    if builder.info.splits:
                        # Prefer 'train' if present, else first available
                        available = list(builder.info.splits)
                        chosen = "train" if "train" in builder.info.splits else available[0]
                        ds = hf_load_dataset(name_or_path, split=chosen)  # type: ignore[misc]
                    else:
                        ds = hf_load_dataset(name_or_path)  # type: ignore[misc]
                except Exception:
                    # Fallback: try default 'train', then without split
                    try:
                        ds = hf_load_dataset(name_or_path, split="train")  # type: ignore[misc]
                    except Exception:
                        ds = hf_load_dataset(name_or_path)  # type: ignore[misc]
            else:
                ds = hf_load_dataset(name_or_path, split=split)  # type: ignore[misc]
            # If the loader returned a DatasetDict, select the desired split
            if isinstance(ds, DatasetDict) or hasattr(ds, "keys"):
                if split is None:
                    chosen = "train" if "train" in ds else next(iter(ds.keys()))
                else:
                    chosen = split
                if chosen not in ds:
                    raise ValueError(
                        f"Split '{chosen}' not found in dataset; available: {list(ds.keys())}"
                    )
                ds = ds[chosen]
            data = [
                Example(
                    str(row.get("input", row.get("text", ""))),
                    str(row.get("target", row.get("text", ""))),
                )
                for row in ds
            ]
        else:
            raise ValueError("Unsupported dataset format or 'datasets' package not available")
    if max_samples is not None:
        data = data[:max_samples]
    return data


__all__ = ["Example", "load_dataset"]
