"""Utilities to persist evaluation artefacts (NDJSON, CSV)."""

from __future__ import annotations

import csv
import json
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path


def write_ndjson(records: Iterable[Mapping[str, object]], path: str | Path) -> None:
    """Write records to ``path`` as newline-delimited JSON."""

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(dict(record), ensure_ascii=False))
            handle.write("\n")


def write_csv(records: Sequence[Mapping[str, object]], path: str | Path) -> None:
    """Write records to CSV, merging keys across all rows for the header."""

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    fieldnames: list[str] = []
    for record in records:
        for key in record:
            if key not in fieldnames:
                fieldnames.append(key)

    with destination.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow({key: record.get(key) for key in fieldnames})
