"""Bounded, local dataset profiling with measured/reported values kept separate."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from collections import Counter
from pathlib import Path
from typing import Any


def profile_dataset(
    path: str | Path, *, max_bytes: int = 50_000_000, max_records: int = 100_000
) -> dict[str, Any]:
    """Profile a CSV or JSONL file; counts describe only parsed records."""
    dataset_path = Path(path)
    with dataset_path.open("rb") as stream:
        raw = stream.read(max_bytes + 1)
    if len(raw) > max_bytes:
        raise ValueError(f"Dataset exceeds the {max_bytes}-byte profile limit")
    digest = hashlib.sha256(raw).hexdigest()
    suffix = dataset_path.suffix.lower()
    if suffix == ".csv":
        records, columns = _read_csv(raw, max_records)
    elif suffix in {".jsonl", ".ndjson"}:
        records, columns = _read_jsonl(raw, max_records)
    else:
        raise ValueError("Dataset profiling supports only CSV and JSONL/NDJSON files")
    missing_counts: Counter[str] = Counter()
    value_types: dict[str, Counter[str]] = {column: Counter() for column in columns}
    seen_rows: set[str] = set()
    duplicate_count = 0
    for record in records:
        canonical = json.dumps(record, sort_keys=True, ensure_ascii=False, default=str)
        row_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        if row_hash in seen_rows:
            duplicate_count += 1
        seen_rows.add(row_hash)
        for column in columns:
            value = record.get(column)
            if value is None or (isinstance(value, str) and not value.strip()):
                missing_counts[column] += 1
            else:
                value_types[column][_type_name(value)] += 1
    return {
        "dataset_id": f"sha256:{digest}",
        "path": dataset_path.name,
        "format": suffix.lstrip("."),
        "sha256": digest,
        "measurement_status": "profiled_download_or_supplied_file",
        "reported_properties": [],
        "observed": {
            "record_count": len(records),
            "count_scope": "records successfully parsed from this file",
            "sampled": False,
            "types_are_inferred_for_csv": suffix == ".csv",
            "columns": columns,
            "missing_counts": {column: missing_counts.get(column, 0) for column in columns},
            "value_types": {column: dict(value_types[column]) for column in columns},
            "duplicate_record_count": duplicate_count,
        },
        "not_assessed": [
            "outliers",
            "label_quality",
            "population_coverage",
            "bias",
            "leakage",
            "fitness_for_research_question",
        ],
    }


def _read_csv(raw: bytes, max_records: int) -> tuple[list[dict[str, Any]], list[str]]:
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text, newline=""))
    if not reader.fieldnames:
        raise ValueError("CSV dataset must include a header row")
    records: list[dict[str, Any]] = []
    for row in reader:
        if len(records) >= max_records:
            raise ValueError(f"Dataset exceeds the {max_records}-record profile limit")
        records.append(dict(row))
    return records, list(reader.fieldnames)


def _read_jsonl(raw: bytes, max_records: int) -> tuple[list[dict[str, Any]], list[str]]:
    records: list[dict[str, Any]] = []
    columns: set[str] = set()
    for line_number, line in enumerate(raw.decode("utf-8-sig").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSONL record on line {line_number}") from exc
        if not isinstance(item, dict):
            raise ValueError(f"JSONL record on line {line_number} must be an object")
        if len(records) >= max_records:
            raise ValueError(f"Dataset exceeds the {max_records}-record profile limit")
        records.append(item)
        columns.update(item)
    return records, sorted(columns)


def _type_name(value: Any) -> str:
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return "unknown"
        if stripped.casefold() in {"true", "false"}:
            return "boolean"
        try:
            int(stripped)
            return "integer"
        except ValueError:
            try:
                float(stripped)
                return "number"
            except ValueError:
                return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return "unknown"
