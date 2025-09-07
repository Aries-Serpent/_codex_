"""Helpers for constructing small evaluation datasets."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List

try:  # pragma: no cover - optional dependency
    from datasets import DatasetDict
    from datasets import load_dataset as hf_load_dataset
    from datasets import load_from_disk

    HAS_DATASETS = True
except Exception:  # pragma: no cover
    DatasetDict = hf_load_dataset = load_from_disk = None  # type: ignore
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
    split: str | None = None,
) -> List[Example]:
    """Load a dataset by preset name, Hugging Face dataset, or JSONL/NDJSON file.

    ``split`` applies when loading from Hugging Face or a directory created via
    ``DatasetDict.save_to_disk``. If ``split`` is ``None`` and a ``DatasetDict`` is
    found on disk, the ``"train"`` split is used when available; otherwise the first
    available split is selected.
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
                if split:
                    if split not in ds:
                        raise ValueError(
                            f"Split '{split}' not found; available splits: {list(ds.keys())}"
                        )
                    ds = ds[split]
                else:
                    ds = ds.get("train") or next(iter(ds.values()))
            data = [
                Example(
                    str(row.get("input", row.get("text", ""))),
                    str(row.get("target", row.get("text", ""))),
                )
                for row in ds
            ]
        elif HAS_DATASETS:
            ds = hf_load_dataset(name_or_path, split=split or "train")
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
