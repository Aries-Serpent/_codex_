"""
Datasets Module

This module provides functionality for datasets.

Usage:
    from eval.datasets import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import hashlib  # noqa: E402
import json  # noqa: E402
import warnings  # noqa: E402
from collections.abc import Iterable, Iterator, Sequence  # noqa: E402
from dataclasses import asdict, dataclass  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Any  # noqa: E402

from codex_ml.utils.hf_pinning import ensure_pinned_kwargs  # noqa: E402

try:  # pragma: no cover - optional dependency
    from datasets import (  # type: ignore[attr-defined]
        DatasetDict,
        load_from_disk,
    )
    from datasets import load_dataset as _hf_load_dataset  # type: ignore[attr-defined]

    def hf_load_dataset(*args: Any, **kwargs: Any):
        global _LAST_HF_REVISION
        if args:
            identifier = args[0]
        else:
            identifier = None
            for key in ("path", "name", "dataset_name"):
                if key in kwargs and kwargs[key] is not None:
                    identifier = kwargs[key]
                    break
            if identifier is None:
                raise TypeError("dataset name must be provided")
        revision, extra = ensure_pinned_kwargs(identifier, kwargs)
        if revision is None:
            dataset = _hf_load_dataset(
                *args,
                **extra,
            )  # nosec B615: local path or offline dataset
            _LAST_HF_REVISION = None
            return dataset
        dataset = _hf_load_dataset(
            *args,
            revision=revision,
            **extra,
        )  # nosec B615: revision pinned via ensure_pinned_kwargs
        _LAST_HF_REVISION = revision
        return dataset

    HAS_DATASETS = True
except (ValueError, TypeError):  # pragma: no cover - handled gracefully
    DatasetDict = load_from_disk = None

    def hf_load_dataset(*_args: Any, **_kwargs: Any):
        raise RuntimeError("datasets library is required for hf:// URIs")

    HAS_DATASETS = False


_LAST_HF_REVISION: str | None = None


@dataclass
class Example:
    input: str
    target: str


@dataclass
class DatasetBundle(Sequence[Example]):
    """Container bundling examples with a deterministic hash."""

    examples: list[Example]
    dataset_hash: str
    source: str
    metadata: dict[str, Any] | None = None

    def __iter__(self) -> Iterator[Example]:
        return iter(self.examples)

    def __len__(self) -> int:  # pragma: no cover - trivially exercised elsewhere
        return len(self.examples)

    def __getitem__(self, index: int) -> Example:  # type: ignore[override]
        return self.examples[index]


_PRESETS = {
    "toy_copy_task": [
        Example("hello", "hello"),
        Example("world", "world"),
    ],
    "tiny_wikitext": [
        Example(
            "Anarchism is a political philosophy.",
            "Anarchism is a political philosophy.",
        ),
    ],
}


def _hash_examples(examples: Iterable[Example]) -> str:
    """Hash examples using JSON serialization to avoid collisions."""
    examples_list = list(examples)
    payload = json.dumps(
        [asdict(example) for example in examples_list],
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def load_dataset(
    name_or_path: str,
    max_samples: int | None = None,
    *,
    hf_split: str = "train",
    hf_input_field: str | None = None,
    hf_target_field: str | None = None,
    hf_text_field: str | None = None,
) -> DatasetBundle:
    """Load a dataset by preset name, HuggingFace hub name, or JSONL/NDJSON file."""
    global _LAST_HF_REVISION
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
    revision: str | None = None
    if name_or_path in _PRESETS:
        data = list(_PRESETS[name_or_path])
    elif name_or_path.startswith("hf://"):
        if not HAS_DATASETS:
            raise ValueError(
                "huggingface 'datasets' package is required for hf:// URIs",
            )
        spec = name_or_path[len("hf://") :]
        parts = spec.split("/")
        if len(parts) >= 3:
            ds_name = "/".join(parts[:-1])
            config = parts[-1]
            _LAST_HF_REVISION = None
            hf_ds = hf_load_dataset(ds_name, config, split=hf_split)
        elif len(parts) == 2:
            ds_name, config = parts
            try:
                _LAST_HF_REVISION = None
                hf_ds = hf_load_dataset(ds_name, config, split=hf_split)
            except (ValueError, TypeError):  # fall back to owner/dataset without config
                ds_name = "/".join(parts)
                config = None
                _LAST_HF_REVISION = None
                hf_ds = hf_load_dataset(ds_name, config, split=hf_split)
        else:
            ds_name, config = parts[0], None
            _LAST_HF_REVISION = None
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
            has_text_column = "text" in hf_ds.column_names
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
            if target_field is None and input_field == "text" and has_text_column:
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
        revision = _LAST_HF_REVISION
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
            # Check if ds is a DatasetDict (defensive isinstance check)
            try:
                is_dataset_dict = DatasetDict is not None and isinstance(ds, DatasetDict)
            except TypeError:
                # Fallback: check if it has the DatasetDict API (keys() method and dict-like)
                is_dataset_dict = hasattr(ds, "keys") and hasattr(ds, "__getitem__")

            if is_dataset_dict:
                if hf_split not in ds:
                    raise ValueError(f"Split '{hf_split}' not found in saved dataset")
                ds = ds[hf_split]
            data = [
                Example(
                    str(row.get("input", row.get("text", ""))),
                    str(row.get("target", row.get("text", ""))),
                )
                for row in ds
            ]
        # Remote dataset via datasets.load_dataset
        elif HAS_DATASETS:
            _LAST_HF_REVISION = None
            ds = hf_load_dataset(name_or_path, split=hf_split)
            data = [
                Example(
                    str(row.get("input", row.get("text", ""))),
                    str(row.get("target", row.get("text", ""))),
                )
                for row in ds
            ]
        else:
            raise ValueError(
                "Unsupported dataset format or 'datasets' package not available",
            )
        revision = _LAST_HF_REVISION
    if max_samples is not None:
        data = data[: max(0, int(max_samples))]

    metadata: dict[str, Any] = {
        "source": str(name_or_path),
        "hf_split": hf_split,
        "hf_input_field": hf_input_field,
        "hf_target_field": hf_target_field,
        "max_samples": max_samples,
        "hf_revision": revision,
        "num_examples": len(data),
    }

    return DatasetBundle(
        examples=data,
        dataset_hash=_hash_examples(data),
        source=name_or_path,
        metadata={k: v for k, v in metadata.items() if v is not None},
    )


__all__ = ["DatasetBundle", "Example", "load_dataset"]
