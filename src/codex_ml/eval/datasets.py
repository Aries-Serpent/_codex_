"""Helpers for constructing small evaluation datasets."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List

try:  # pragma: no cover - optional dependency
    from datasets import DatasetDict, load_from_disk  # isort: skip
    from datasets import load_dataset as hf_load_dataset  # isort: skip

    HAS_DATASETS = True
except Exception:  # pragma: no cover
    hf_load_dataset = load_from_disk = DatasetDict = None  # type: ignore
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
    split: str | None = "train",
) -> List[Example]:
    """Load a dataset by preset name, Hugging Face dataset, or JSONL/NDJSON file.

    When loading from a path saved with ``datasets.DatasetDict.save_to_disk`` or a
    remote dataset via ``datasets.load_dataset``, the ``split`` argument selects
    which split to use. If ``split`` is ``None`` the first available split is
    used. The default is ``"train"``.
    """
    if name_or_path in _PRESETS:
        data = list(_PRESETS[name_or_path])
    else:
        path = Path(name_or_path)
        if path.suffix.lower() in {".ndjson", ".jsonl"} and path.is_file():
            data = [
                Example(**json.loads(line))
                for line in path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
        elif path.exists() and path.is_dir() and HAS_DATASETS:
            ds = load_from_disk(str(path))
            if isinstance(ds, DatasetDict):
                chosen = split or next(iter(ds.keys()))
                if chosen not in ds:
                    raise ValueError(f"Split '{chosen}' not found in dataset")
                ds = ds[chosen]
            data = [
                Example(
                    str(row.get("input", row.get("text", ""))),
                    str(row.get("target", row.get("text", ""))),
                )
                for row in ds
            ]
        elif HAS_DATASETS:
            if split is None:
                ds = hf_load_dataset(name_or_path)
                if isinstance(ds, DatasetDict):
                    ds = ds[next(iter(ds.keys()))]
            else:
                ds = hf_load_dataset(name_or_path, split=split)
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
