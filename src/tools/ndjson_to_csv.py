#!/usr/bin/env python3
"""Convert newline-delimited JSON metrics logs into CSV format."""

from __future__ import annotations

import argparse
import csv
import json
from collections.abc import Iterable, Iterator, Sequence
from pathlib import Path
from typing import Any

Record = dict[str, Any]


def iter_records(path: Path) -> Iterator[Record]:
    """Yield parsed JSON objects from ``path`` line-by-line."""

    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            yield payload


def merge_fieldnames(records: Iterable[Record]) -> list[str]:
    fields: set[str] = set()
    for record in records:
        fields.update(str(key) for key in record.keys())
    return sorted(fields)


def convert_records(records: Sequence[Record]) -> tuple[list[str], list[Record]]:
    fieldnames = merge_fieldnames(records)
    normalised: list[Record] = []
    for record in records:
        row = {name: record.get(name, "") for name in fieldnames}
        normalised.append(row)
    return fieldnames, normalised


def write_csv(fieldnames: Sequence[str], rows: Sequence[Record], dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def convert_file(ndjson_path: Path, csv_path: Path) -> tuple[int, list[str]]:
    records = list(iter_records(ndjson_path))
    if not records:
        write_csv([], [], csv_path)
        return 0, []
    fieldnames, rows = convert_records(records)
    write_csv(fieldnames, rows, csv_path)
    return len(rows), fieldnames


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Convert NDJSON metrics logs to CSV")
    parser.add_argument("ndjson", help="Path to NDJSON metrics log")
    parser.add_argument("csv", help="Output CSV path")
    parser.add_argument("--quiet", action="store_true", help="Suppress summary output")
    args = parser.parse_args(list(argv) if argv is not None else None)

    count, fields = convert_file(Path(args.ndjson), Path(args.csv))
    if not args.quiet:
        if count:
            print(f"Wrote {count} records with fields: {', '.join(fields)}")
        else:
            print("No records to convert")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    raise SystemExit(main())
