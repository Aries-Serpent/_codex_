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
    "iter_jsonl",
    "iter_txt",
    "stream_paths",
    "collect_stats",
]


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


@dataclass
class Sample:
    prompt: str
    completion: str


def _ensure_prompt_completion(payload: Dict[str, Any]) -> Sample:
    prompt = payload.get("prompt")
    completion = payload.get("completion")
    if not isinstance(prompt, str) or not isinstance(completion, str):
        raise ValueError("Rows must include string 'prompt' and 'completion' fields")
    return Sample(prompt=prompt, completion=completion)


def iter_jsonl(path: str | Path) -> Iterator[Sample]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"JSONL file not found: {p}")
    with p.open("r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError as exc:  # pragma: no cover
                raise ValueError(f"Invalid JSON on line {lineno}: {exc}") from exc
            if not isinstance(data, dict):
                msg = f"JSONL rows must be objects; got {type(data)!r} on line {lineno}"
                raise ValueError(msg)
            yield _ensure_prompt_completion(data)


def iter_txt(path: str | Path, *, delimiter: str = "\t") -> Iterator[Sample]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"TXT file not found: {p}")
    with p.open("r", encoding="utf-8") as f:
        for lineno, raw in enumerate(f, start=1):
            raw = raw.rstrip("\n")
            if not raw:
                continue
            parts = raw.split(delimiter, maxsplit=1)
            if len(parts) != 2:
                raise ValueError(f"Line {lineno} missing delimiter {delimiter!r}")
            prompt, completion = parts
            yield Sample(prompt=prompt, completion=completion)


def _iter_samples_for_path(path: Path, *, fmt: str, delimiter: str) -> Iterator[Sample]:
    if fmt == "jsonl":
        return iter_jsonl(path)
    if fmt == "txt":
        return iter_txt(path, delimiter=delimiter)
    raise ValueError(f"Unsupported format: {fmt}")


def stream_paths(
    paths: Sequence[str | Path],
    *,
    fmt: str = "jsonl",
    max_samples: int | None = None,
    delimiter: str = "\t",
    cfg: Any | None = None,
    num_workers: int | None = None,
    prefetch: int | None = None,
) -> Iterator[Sample]:
    # num_workers/prefetch retained for compatibility; streaming is synchronous for now
    del num_workers, prefetch

    yielded = 0
    for p in paths:
        path = Path(p)
        samples_iter = _iter_samples_for_path(path, fmt=fmt, delimiter=delimiter)
        if cfg and getattr(getattr(cfg, "dataset", None), "generate_manifest", False):
            samples_cache = list(samples_iter)
            manifest_path = Path(f"{path}.manifest.json")
            manifest = {
                "path": str(path),
                "format": fmt,
                "num_records": len(samples_cache),
                "checksum": compute_file_checksum(path),
            }
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            samples_iter = iter(samples_cache)
        for sample in samples_iter:
            yield sample
            yielded += 1
            if max_samples is not None and yielded >= max_samples:
                return


def collect_stats(
    rows: Iterable[Sample],
    *,
    sample_limit: int | None = None,
) -> Dict[str, Any]:
    total_prompt_chars = 0
    total_completion_chars = 0
    total_prompt_tokens = 0
    total_completion_tokens = 0
    count = 0

    for row in rows:
        if sample_limit is not None and count >= sample_limit:
            break
        prompt = getattr(row, "prompt", None)
        completion = getattr(row, "completion", None)
        if not isinstance(prompt, str) or not isinstance(completion, str):
            continue
        count += 1
        total_prompt_chars += len(prompt)
        total_completion_chars += len(completion)
        total_prompt_tokens += len(prompt.split())
        total_completion_tokens += len(completion.split())

    if count == 0:
        return {
            "samples": 0,
            "avg_prompt_len": 0.0,
            "avg_completion_len": 0.0,
            "avg_prompt_tokens": 0.0,
            "avg_completion_tokens": 0.0,
        }

    return {
        "samples": count,
        "avg_prompt_len": total_prompt_chars / count,
        "avg_completion_len": total_completion_chars / count,
        "avg_prompt_tokens": total_prompt_tokens / count,
        "avg_completion_tokens": total_completion_tokens / count,
    }
