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
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional, Sequence, Tuple

from codex_ml.safety.filters import (
    SafetyFilters,
    SafetyResult,
)
from codex_ml.safety.filters import (
    sanitize_output as filter_sanitize_output,
)
from codex_ml.safety.filters import (
    sanitize_prompt as filter_sanitize_prompt,
)
from codex_ml.utils.error_log import log_error

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


def _coerce_data_cfg(cfg: Any | None) -> Any | None:
    if cfg is None:
        return None
    data_cfg = getattr(cfg, "data", None)
    return data_cfg if data_cfg is not None else cfg


def _resolve_safety_filters(
    cfg: Any | None,
    provided_filters: SafetyFilters | None,
) -> SafetyFilters | None:
    if provided_filters is not None:
        return provided_filters

    data_cfg = _coerce_data_cfg(cfg)
    if data_cfg is None:
        return None

    enabled = getattr(data_cfg, "safety_filter_enabled", None)
    if enabled is None:
        enabled = getattr(data_cfg, "safety_filter", None)
    if not enabled:
        return None

    policy_path = None
    for attr in ("safety_filter_policy_path", "safety_filter_policy", "policy_path"):
        value = getattr(data_cfg, attr, None)
        if value:
            policy_path = value
            break

    try:
        if policy_path:
            return SafetyFilters.from_policy_file(policy_path)
        return SafetyFilters.from_defaults()
    except Exception:
        # Fall back to defaults if the configured policy cannot be loaded.
        return SafetyFilters.from_defaults()


def _infer_format(path: Path, explicit: Optional[str]) -> str:
    if explicit and explicit.lower() not in {"auto", "default"}:
        return explicit.lower()

    suffix = path.suffix.lower()
    if suffix in {".jsonl", ".json"}:
        return "jsonl"
    if suffix in {".txt", ".tsv"}:
        return "txt"
    # Default to JSONL for backwards compatibility with legacy callers.
    return "jsonl"


def _log_safety_decision(path: Path, prompt: SafetyResult, completion: SafetyResult) -> None:
    try:
        context = json.dumps(
            {
                "path": str(path),
                "prompt_allowed": prompt.allowed,
                "prompt_blocked_rules": list(prompt.blocked_rules),
                "completion_allowed": completion.allowed,
                "completion_blocked_rules": list(completion.blocked_rules),
            },
            ensure_ascii=False,
        )
        log_error("data.safety", "dataset sample sanitized", context)
    except Exception:
        # Logging should not interfere with dataset streaming.
        pass


def _apply_safety(sample: Sample, *, path: Path, filters: SafetyFilters | None) -> Sample:
    if filters is None:
        return sample

    prompt_decision = filter_sanitize_prompt(sample.prompt, filters=filters)
    completion_decision = filter_sanitize_output(sample.completion, filters=filters)

    if (
        prompt_decision.sanitized_text != sample.prompt
        or completion_decision.sanitized_text != sample.completion
    ):
        _log_safety_decision(path, prompt_decision, completion_decision)

    return Sample(
        prompt=prompt_decision.sanitized_text,
        completion=completion_decision.sanitized_text,
    )


def stream_paths(
    paths: Sequence[str | Path],
    fmt: str | None = None,
    *,
    max_samples: int | None = None,
    seed: int | None = None,
    num_workers: int | None = None,
    prefetch: int | None = None,
    delimiter: str = "\t",
    safety_filters: SafetyFilters | None = None,
    cfg: Any | None = None,
) -> Iterator[Sample]:
    """Stream samples from one or more dataset paths.

    The signature intentionally preserves the historical keyword arguments used
    by downstream tooling (``seed``, ``num_workers``, ``prefetch``,
    ``safety_filters``) even if this implementation processes files
    sequentially.  Callers depending on deterministic shuffling and safety
    filtering continue to function without modification.
    """

    del num_workers, prefetch  # preserved for backwards compatibility

    generated = 0
    generate_manifest = _should_generate_manifest(cfg)
    active_filters = _resolve_safety_filters(cfg, safety_filters)

    ordered_paths = [Path(p) for p in paths]
    if seed is not None:
        rng = random.Random(seed)
        rng.shuffle(ordered_paths)

    for path in ordered_paths:
        resolved_fmt = _infer_format(path, fmt)

        if resolved_fmt == "jsonl":
            iterator: Iterable[Sample] = iter_jsonl(path)
        elif resolved_fmt == "txt":
            iterator = iter_txt(path, delimiter=delimiter)
        else:
            raise ValueError(f"Unsupported dataset format: {resolved_fmt}")

        if generate_manifest:
            samples = list(iterator)
            _write_manifest(path, resolved_fmt, len(samples))
            iterable: Iterable[Sample] = samples
        else:
            iterable = iterator

        for sample in iterable:
            sanitized = _apply_safety(sample, path=path, filters=active_filters)
            yield sanitized
            generated += 1
            if max_samples is not None and generated >= max_samples:
                return


def collect_stats(
    samples: Iterable[Sample], *, sample_limit: int | None = None
) -> Dict[str, float]:
    total = 0
    total_prompt_len = 0
    total_completion_len = 0
    total_prompt_tokens = 0
    total_completion_tokens = 0

    for sample in samples:
        if sample_limit is not None and total >= sample_limit:
            break
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
