"""Helpers for constructing small evaluation datasets."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List


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


def load_dataset(name_or_path: str, max_samples: int | None = None) -> List[Example]:
    """Load a dataset by preset name or from a JSONL/NDJSON file."""
    if name_or_path in _PRESETS:
        data = list(_PRESETS[name_or_path])
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
