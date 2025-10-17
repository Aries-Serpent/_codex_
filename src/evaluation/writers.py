from __future__ import annotations

import csv
import json
from collections.abc import Iterable, Mapping, MutableMapping, Sequence
from pathlib import Path


def write_ndjson(
    records: Iterable[Mapping],
    path: str | Path,
    *,
    schema_version: str | None = "v1",
    metadata: Mapping[str, object] | None = None,
) -> None:
    """Write one JSON object per line (NDJSON) with optional schema metadata."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    schema_meta: MutableMapping[str, object] | None = None
    if metadata:
        schema_meta = dict(metadata)

    with p.open("w", encoding="utf-8", newline="\n") as f:
        for rec in records:
            payload = dict(rec)
            if schema_version is not None and "schema_version" not in payload:
                payload["schema_version"] = schema_version
            if schema_meta:
                existing = payload.get("_schema")
                if isinstance(existing, Mapping):
                    merged = dict(existing)
                    merged.update(schema_meta)
                else:
                    merged = dict(schema_meta)
                payload["_schema"] = merged
            f.write(json.dumps(payload, ensure_ascii=False))
            f.write("\n")


def write_csv(records: Sequence[Mapping], path: str | Path) -> None:
    """Write rows to CSV using DictWriter; header is union of keys."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    keys: list[str] = []
    for r in records:
        for k in r:
            if k not in keys:
                keys.append(k)
    with p.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in records:
            w.writerow({k: r.get(k) for k in keys})
