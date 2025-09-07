"""Helpers for constructing small evaluation datasets."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List

try:  # pragma: no cover - optional dependency
    from datasets import load_dataset  # type: ignore

    _HAS_DATASETS = True
except Exception:  # pragma: no cover - handled gracefully
    load_dataset = None  # type: ignore
    _HAS_DATASETS = False


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
    hf_split: str = "train",
    hf_text_field: str = "text",
) -> List[Example]:
    """Load a dataset by preset name, HuggingFace hub name, or JSONL/NDJSON file."""
    if name_or_path in _PRESETS:
        data = list(_PRESETS[name_or_path])
    elif name_or_path.startswith("hf://"):
        if not _HAS_DATASETS:
            raise ValueError("huggingface 'datasets' package is required for hf:// URIs")
        spec = name_or_path[len("hf://") :]
        if "/" in spec:
            ds_name, config = spec.split("/", 1)
        else:
            ds_name, config = spec, None
        hf_ds = load_dataset(ds_name, config, split=hf_split)
        if hf_text_field not in hf_ds.column_names:
            raise ValueError(
                f"Column '{hf_text_field}' not found in dataset columns {hf_ds.column_names}"
            )
        data = [Example(text, text) for text in hf_ds[hf_text_field]]
    else:
        path = Path(name_or_path)
        if path.suffix.lower() in {".ndjson", ".jsonl"}:
            data = [
                Example(**json.loads(line))
                for line in path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
        else:
            raise ValueError(f"Unsupported dataset format: {path.suffix}")
    if max_samples is not None:
        data = data[:max_samples]
    return data


__all__ = ["Example", "load_dataset"]
