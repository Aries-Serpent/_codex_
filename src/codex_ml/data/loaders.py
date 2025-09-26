"""
Dataset loaders for JSONL and CSV with deterministic checksum.

Enhancements (Extended tests support):
- Empty file returns 0 records, no error.
- UTF-8 BOM automatically handled (utf-8-sig).
- Malformed JSONL lines skipped (count in metadata['skipped_malformed']).
- CSV quoted fields preserved (csv.DictReader handles).
- Additional metadata fields: skipped_malformed, empty_file (bool).

Backward compatible (original signatures unchanged).
"""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Sequence, Tuple

__all__ = [
    "load_jsonl",
    "load_csv",
    "compute_file_checksum",
    "Sample",
    "iter_jsonl",
    "iter_txt",
    "stream_paths",
    "collect_stats",
]


@dataclass(frozen=True)
class Sample:
    """Simple container for prompt/completion pairs."""

    prompt: str
    completion: str


def compute_file_checksum(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def load_jsonl(path: str | Path) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"JSONL file not found: {p}")
    records: List[Dict[str, Any]] = []
    skipped = 0
    with p.open("r", encoding="utf-8-sig") as f:  # utf-8-sig handles BOM
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                skipped += 1
                continue
            if not isinstance(obj, dict):
                obj = {"value": obj}
            records.append(obj)
    checksum = compute_file_checksum(p)
    meta = {
        "path": str(p),
        "format": "jsonl",
        "num_records": len(records),
        "checksum": checksum,
        "size_bytes": p.stat().st_size,
        "skipped_malformed": skipped,
        "empty_file": p.stat().st_size == 0,
    }
    return records, meta


def load_csv(path: str | Path) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"CSV file not found: {p}")
    records: List[Dict[str, Any]] = []
    with p.open("r", encoding="utf-8-sig", newline="") as f:  # utf-8-sig covers BOM
        reader = csv.DictReader(f)
        for row in reader:
            records.append(dict(row))
    checksum = compute_file_checksum(p)
    meta = {
        "path": str(p),
        "format": "csv",
        "num_records": len(records),
        "checksum": checksum,
        "size_bytes": p.stat().st_size,
        "empty_file": len(records) == 0,
    }
    return records, meta


def _validate_sample(obj: Dict[str, Any]) -> Sample:
    if not isinstance(obj, dict):
        raise ValueError("Expected JSON object with prompt/completion fields")

    if "prompt" not in obj or "completion" not in obj:
        raise ValueError("Missing prompt/completion fields")

    prompt = obj["prompt"]
    completion = obj["completion"]

    if not isinstance(prompt, str) or not isinstance(completion, str):
        raise ValueError("Prompt and completion must be strings")

    return Sample(prompt=prompt, completion=completion)


def iter_jsonl(path: str | Path) -> Iterator[Sample]:
    """Iterate over a JSONL file yielding :class:`Sample` objects."""

    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"JSONL file not found: {p}")

    with p.open("r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            yield _validate_sample(obj)


def iter_txt(path: str | Path, delimiter: str = "\t") -> Iterator[Sample]:
    """Iterate over a TSV (prompt\tcompletion) file."""

    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"TXT file not found: {p}")

    with p.open("r", encoding="utf-8-sig") as f:
        for raw in f:
            line = raw.rstrip("\n")
            if not line:
                continue
            parts = line.split(delimiter, maxsplit=1)
            if len(parts) != 2:
                raise ValueError("Expected delimiter separating prompt and completion")
            prompt, completion = parts
            yield Sample(prompt=prompt, completion=completion)


def _should_generate_manifest(cfg: Any) -> bool:
    dataset_cfg = getattr(cfg, "dataset", None)
    if dataset_cfg is None:
        return False
    return bool(getattr(dataset_cfg, "generate_manifest", False))


def _write_manifest(path: Path, fmt: str, count: int) -> None:
    manifest_data = {
        "path": str(path),
        "format": fmt,
        "num_records": count,
        "checksum": compute_file_checksum(path),
        "size_bytes": path.stat().st_size,
    }
    manifest_path = Path(f"{path}.manifest.json")
    manifest_path.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")


def stream_paths(
    paths: Sequence[str | Path],
    fmt: str,
    *,
    max_samples: int | None = None,
    cfg: Any | None = None,
) -> Iterator[Sample]:
    """Stream samples from one or more dataset paths."""

    generated = 0
    generate_manifest = _should_generate_manifest(cfg)

    for path in paths:
        p = Path(path)
        if fmt == "jsonl":
            iterator = list(iter_jsonl(p)) if generate_manifest else iter_jsonl(p)
        elif fmt == "txt":
            iterator = list(iter_txt(p)) if generate_manifest else iter_txt(p)
        else:
            raise ValueError(f"Unsupported dataset format: {fmt}")

        if generate_manifest:
            samples = iterator
            _write_manifest(p, fmt, len(samples))
            iterable: Iterable[Sample] = samples
        else:
            iterable = iterator

        for sample in iterable:
            yield sample
            generated += 1
            if max_samples is not None and generated >= max_samples:
                return


def collect_stats(samples: Iterable[Sample]) -> Dict[str, float]:
    total = 0
    total_prompt_len = 0
    total_completion_len = 0
    total_prompt_tokens = 0
    total_completion_tokens = 0

    for sample in samples:
        total += 1
        prompt = sample.prompt
        completion = sample.completion
        total_prompt_len += len(prompt)
        total_completion_len += len(completion)
        total_prompt_tokens += len(prompt.split())
        total_completion_tokens += len(completion.split())

    if total == 0:
        return {
            "samples": 0,
            "avg_prompt_len": 0.0,
            "avg_completion_len": 0.0,
            "avg_prompt_tokens": 0.0,
            "avg_completion_tokens": 0.0,
        }

    return {
        "samples": total,
        "avg_prompt_len": total_prompt_len / total,
        "avg_completion_len": total_completion_len / total,
        "avg_prompt_tokens": total_prompt_tokens / total,
        "avg_completion_tokens": total_completion_tokens / total,
    }
