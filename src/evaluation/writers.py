from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable, List, Mapping, Sequence


def write_ndjson(records: Iterable[Mapping], path: str | Path) -> None:
    """Write one JSON object per line (NDJSON)."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8", newline="\n") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False))
            f.write("\n")


def write_csv(records: Sequence[Mapping], path: str | Path) -> None:
    """Write rows to CSV using DictWriter; header is union of keys."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    keys: List[str] = []
    for r in records:
        for k in r.keys():
            if k not in keys:
                keys.append(k)
    with p.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in records:
            w.writerow({k: r.get(k) for k in keys})
