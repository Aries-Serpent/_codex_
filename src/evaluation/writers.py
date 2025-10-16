from __future__ import annotations

import csv
import json
from collections.abc import Iterable, Mapping, MutableMapping, Sequence
from pathlib import Path


def write_ndjson(
    records: Iterable[Mapping],
    path: str | Path,
    *,
    schema_version: str = "v1",
    metadata: Mapping[str, object] | None = None,
) -> None:
    """Write one JSON object per line (NDJSON) with schema metadata."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8", newline="\n") as f:
        meta_payload: MutableMapping[str, object] = {"schema_version": schema_version}
        if metadata:
            meta_payload.update(dict(metadata))
        f.write(json.dumps({"__meta__": meta_payload}, ensure_ascii=False))
        f.write("\n")
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False))
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
