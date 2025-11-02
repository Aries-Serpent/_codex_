"""JSON Lines dataset loader with deterministic caching and splitting."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Iterator, List, Mapping, Tuple

from codex_ml.utils.repro import record_dataset_checksums
from codex_ml.data.splits import assign_split

CacheKey = Tuple[str, Tuple[float, float, float], int, bool]
DEFAULT_CACHE_DIR = Path("artifacts/data_cache")


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _iter_jsonl(path: Path) -> Iterator[Mapping[str, Any]]:
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(payload, Mapping):
                yield payload


def _normalise_record(
    payload: Mapping[str, Any], fields: Tuple[str, str, str]
) -> Dict[str, str] | None:
    text_field, input_field, target_field = fields
    if text_field in payload:
        text = str(payload[text_field])
        source = str(payload.get(input_field, text))
        target = str(payload.get(target_field, text))
    elif input_field in payload and target_field in payload:
        source = str(payload[input_field])
        target = str(payload[target_field])
        text = source
    else:
        return None
    return {"text": text, "input": source, "target": target}


def _cache_key(file_sha: str, ratios: Tuple[float, float, float], seed: int, shuffle: bool) -> str:
    payload = json.dumps(
        {"sha": file_sha, "ratios": ratios, "seed": seed, "shuffle": shuffle},
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def load_jsonl_dataset(
    path: str | Path,
    *,
    text_field: str = "text",
    input_field: str = "input",
    target_field: str = "target",
    split: Tuple[float, float, float] = (0.8, 0.1, 0.1),
    seed: int = 1234,
    shuffle: bool = True,
    cache_dir: str | Path | None = DEFAULT_CACHE_DIR,
) -> Dict[str, List[Dict[str, str]]]:
    """Load ``path`` and return deterministic train/val/test splits."""

    dataset_path = Path(path)
    dataset: Dict[str, List[Dict[str, str]]] = {"train": [], "val": [], "test": []}
    for index, payload in enumerate(_iter_jsonl(dataset_path)):
        normalised = _normalise_record(payload, (text_field, input_field, target_field))
        if normalised is None:
            continue
        example_id = str(payload.get("id") or payload.get("uuid") or payload.get("guid"))
        if not example_id or example_id == "None":
            canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False)
            example_id = hashlib.sha1(canonical.encode("utf-8")).hexdigest()
        normalised["id"] = example_id
        normalised["split"] = assign_split(example_id)
        dataset.setdefault(normalised["split"], []).append(normalised)
        if shuffle:
            # Maintain historical behaviour by preserving deterministic order when requested
            dataset[normalised["split"]][-1]["index"] = index

    if shuffle:
        for split_name in dataset:
            dataset[split_name].sort(key=lambda row: row.pop("index", 0))

    if cache_dir is not None:
        cache_path = Path(cache_dir)
        cache_path.mkdir(parents=True, exist_ok=True)
        file_sha = _file_sha256(dataset_path)
        key = _cache_key(file_sha, split, seed, shuffle)
        target = cache_path / f"{key}.json"
        if not target.exists():
            target.write_text(json.dumps(dataset, indent=2), encoding="utf-8")
        manifest_path = cache_path / f"{key}.manifest.json"
        record_dataset_checksums([dataset_path], manifest_path)
    return dataset


__all__ = ["load_jsonl_dataset"]
