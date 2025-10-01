"""CLI utilities for aggregating rotated NDJSON metric shards."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Iterable, List, Mapping


def _rotation_index(path: Path) -> int:
    try:
        return int(path.name.rsplit(".", maxsplit=1)[-1])
    except ValueError:
        return 0


def _iter_shards(directory: Path) -> Iterable[Path]:
    base = directory / "metrics.ndjson"
    rotated = sorted(directory.glob("metrics.ndjson.*"), key=_rotation_index, reverse=True)
    for path in rotated:
        if path.is_file():
            yield path
    if base.is_file():
        yield base


def _load_rows(directory: Path) -> List[Mapping[str, object]]:
    rows: List[Mapping[str, object]] = []
    for path in _iter_shards(directory):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def _canonical_field_order(rows: List[Mapping[str, object]]) -> List[str]:
    if not rows:
        return []
    preferred = [
        "timestamp",
        "run_id",
        "step",
        "split",
        "metric",
        "value",
        "dataset",
        "tags",
    ]
    available = {key for row in rows for key in row.keys()}
    ordered = [key for key in preferred if key in available]
    extras = sorted(available - set(ordered))
    return ordered + extras


def summarize(directory: Path, fmt: str, destination: Path | None = None) -> Path:
    rows = _load_rows(directory)
    if not rows:
        raise SystemExit(f"no metrics.ndjson shards found under {directory}")
    fieldnames = _canonical_field_order(rows)
    if not destination:
        destination = directory / f"metrics.summary.{fmt}"
    destination.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "csv":
        with destination.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow({key: _serialise_cell(row.get(key, "")) for key in fieldnames})
        return destination
    if fmt == "parquet":
        try:
            import pandas as pd  # type: ignore[import]
        except Exception as exc:  # pragma: no cover - optional dependency
            raise SystemExit("pandas is required for parquet export") from exc
        df = pd.DataFrame(rows)
        df.to_parquet(destination, index=False)
        return destination
    raise SystemExit(f"unsupported output format: {fmt}")


def _serialise_cell(value: object) -> object:
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True)
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Summarize rotated NDJSON metrics")
    parser.add_argument("--input", type=Path, required=True, help="Directory with metrics")
    parser.add_argument(
        "--output",
        choices=("csv", "parquet"),
        default="csv",
        help="Output format",
    )
    parser.add_argument(
        "--destination",
        type=Path,
        default=None,
        help="Optional destination path (defaults to metrics.summary.<format>)",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    args_list = list(argv if argv is not None else sys.argv[1:])
    if args_list and args_list[0] == "summarize":
        args_list = args_list[1:]
    elif args_list and args_list[0] not in {"summarize"}:
        raise SystemExit(f"unknown command: {args_list[0]}")
    parser = build_parser()
    args = parser.parse_args(args_list)
    summarize(args.input, args.output, args.destination)


if __name__ == "__main__":  # pragma: no cover - manual invocation
    main()
