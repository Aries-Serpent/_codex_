from __future__ import annotations

import csv
import datetime as dt
import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any


def _flatten(data: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    flattened: dict[str, Any] = {}
    for key, value in data.items():
        column = f"{prefix}{key}" if not prefix else f"{prefix}.{key}"
        if isinstance(value, dict):
            flattened.update(_flatten(value, column))
        else:
            flattened[column] = value
    return flattened


def append_event_ndjson(out_file: Path, event: dict[str, Any]) -> None:
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with out_file.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def _iter_ndjson_files(in_path: Path) -> Iterable[Path]:
    if in_path.is_file():
        yield in_path
    elif in_path.is_dir():
        for path in sorted(in_path.rglob("*.ndjson")):
            if path.is_file():
                yield path


def ndjson_to_csv(in_path: Path, out_csv: Path) -> None:
    """Convert NDJSON records (from a file or directory tree) into a single CSV."""
    rows: list[dict[str, Any]] = []
    headers: list[str] = []
    header_set = set()

    for file_path in _iter_ndjson_files(in_path):
        for line in file_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            flat = _flatten(record)
            rows.append(flat)
            for column in flat:
                if column not in header_set:
                    header_set.add(column)
                    headers.append(column)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def cli_ndjson_to_csv() -> None:
    import sys

    if len(sys.argv) < 3:
        print("Usage: ndjson-to-csv <IN_FILE_OR_DIR> <OUT_CSV>", file=sys.stderr)
        sys.exit(2)

    in_path = Path(sys.argv[1])
    out_csv = Path(sys.argv[2])
    ndjson_to_csv(in_path, out_csv)
    print(f"Wrote CSV: {out_csv}")


def make_run_metrics_path(base_dir: Path = Path(".codex/metrics")) -> Path:
    timestamp = dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    return base_dir / f"run-{timestamp}.ndjson"
