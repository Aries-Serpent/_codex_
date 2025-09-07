"""Helpers for constructing small evaluation datasets."""

from __future__ import annotations

import json
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import List

try:  # pragma: no cover - optional dependency
    from datasets import load_dataset as hf_load_dataset  # type: ignore
    from datasets import load_from_disk

    HAS_DATASETS = True
except Exception:  # pragma: no cover - handled gracefully
    hf_load_dataset = load_from_disk = None  # type: ignore
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
    hf_split: str = "train",
    hf_input_field: str | None = None,
    hf_target_field: str | None = None,
    hf_text_field: str | None = None,
) -> List[Example]:
    """Load a dataset by preset name, HuggingFace hub name, or JSONL/NDJSON file."""
    if hf_text_field is not None:
        if hf_input_field is not None or hf_target_field is not None:
            raise ValueError(
                "'hf_text_field' cannot be combined with 'hf_input_field' or 'hf_target_field'"
            )
        warnings.warn(
            "'hf_text_field' is deprecated; use 'hf_input_field' and 'hf_target_field' instead",
            DeprecationWarning,
            stacklevel=2,
        )
        hf_input_field = hf_text_field
        hf_target_field = hf_text_field
    if name_or_path in _PRESETS:
        data = list(_PRESETS[name_or_path])
    elif name_or_path.startswith("hf://"):
        if not HAS_DATASETS:
            raise ValueError("huggingface 'datasets' package is required for hf:// URIs")
        spec = name_or_path[len("hf://") :]
        parts = spec.split("/")
        if len(parts) >= 3:
            ds_name = "/".join(parts[:-1])
            config = parts[-1]
            hf_ds = hf_load_dataset(ds_name, config, split=hf_split)
        elif len(parts) == 2:
            ds_name, config = parts
            try:
                hf_ds = hf_load_dataset(ds_name, config, split=hf_split)
            except Exception:  # fall back to owner/dataset without config
                ds_name = "/".join(parts)
                config = None
                hf_ds = hf_load_dataset(ds_name, config, split=hf_split)
        else:
            ds_name, config = parts[0], None
            hf_ds = hf_load_dataset(ds_name, config, split=hf_split)
        input_field = hf_input_field
        target_field = hf_target_field
        if input_field is None:
            if "input" in hf_ds.column_names:
                input_field = "input"
            elif "text" in hf_ds.column_names:
                input_field = "text"
            else:
                raise ValueError(
                    f"No suitable input column found in dataset columns {hf_ds.column_names}"
                )
        elif input_field not in hf_ds.column_names:
            raise ValueError(
                f"Column '{input_field}' not found in dataset columns {hf_ds.column_names}"
            )

        if target_field is None:
            for candidate in [
                "target",
                "output",
                "answer",
                "label",
                "text",
            ]:
                if candidate in hf_ds.column_names and candidate != input_field:
                    target_field = candidate
                    break
            if target_field is None and input_field == "text" and "text" in hf_ds.column_names:
                target_field = "text"
            if target_field is None:
                raise ValueError(
                    f"No suitable target column found in dataset columns {hf_ds.column_names}"
                )
        elif target_field not in hf_ds.column_names:
            raise ValueError(
                f"Column '{target_field}' not found in dataset columns {hf_ds.column_names}"
            )

        data = [Example(str(row[input_field]), str(row[target_field])) for row in hf_ds]
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
            data = [
                Example(
                    str(row.get("input", row.get("text", ""))),
                    str(row.get("target", row.get("text", ""))),
                )
                for row in ds
            ]
        elif HAS_DATASETS:
            ds = hf_load_dataset(name_or_path, split="train")
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
