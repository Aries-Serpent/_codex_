"""CSV/TSV dataset loader with deterministic splits and caching."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Tuple

from codex_ml.utils.repro import record_dataset_checksums
from codex_ml.data.splits import assign_split

DEFAULT_CACHE_DIR = Path("artifacts/data_cache")


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _cache_key(file_sha: str, ratios: Tuple[float, float, float], seed: int, shuffle: bool) -> str:
    payload = json.dumps(
        {"sha": file_sha, "ratios": ratios, "seed": seed, "shuffle": shuffle},
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def load_csv_dataset(
    path: str | Path,
    *,
    text_column: str = "text",
    input_column: str = "input",
    target_column: str = "target",
    delimiter: str | None = None,
    split: Tuple[float, float, float] = (0.8, 0.1, 0.1),
    seed: int = 1234,
    shuffle: bool = True,
    cache_dir: str | Path | None = DEFAULT_CACHE_DIR,
) -> Dict[str, List[Dict[str, str]]]:
    """Load a CSV/TSV dataset and return train/val/test splits."""

    dataset_path = Path(path)
    if delimiter is None:
        delimiter = "\t" if dataset_path.suffix.lower() == ".tsv" else ","
    dataset: Dict[str, List[Dict[str, str]]] = {"train": [], "val": [], "test": []}
    with dataset_path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh, delimiter=delimiter)
        for index, row in enumerate(reader):
            if not row:
                continue
            text = row.get(text_column) or row.get(input_column)
            target = row.get(target_column)
            if text is None or target is None:
                continue
            payload = {
                "text": str(text),
                "input": str(row.get(input_column, text)),
                "target": str(target),
            }
            example_id = str(
                row.get("id")
                or row.get("uuid")
                or row.get("guid")
                or row.get("example_id")
            )
            if not example_id or example_id == "None":
                canonical = json.dumps(row, sort_keys=True, ensure_ascii=False)
                example_id = hashlib.sha1(canonical.encode("utf-8")).hexdigest()
            payload["id"] = example_id
            payload["split"] = assign_split(example_id)
            dataset[payload["split"]].append({**payload, "_index": index} if shuffle else payload)

    if shuffle:
        for split_name, items in dataset.items():
            items.sort(key=lambda row: row.pop("_index", 0))

    if cache_dir is not None:
        cache_path = Path(cache_dir)
        cache_path.mkdir(parents=True, exist_ok=True)
        key = _cache_key(_file_sha256(dataset_path), split, seed, shuffle)
        target = cache_path / f"{key}.json"
        if not target.exists():
            target.write_text(json.dumps(dataset, indent=2), encoding="utf-8")
        manifest_path = cache_path / f"{key}.manifest.json"
        record_dataset_checksums([dataset_path], manifest_path)
    return dataset


__all__ = ["load_csv_dataset"]
