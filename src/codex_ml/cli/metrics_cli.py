"""Metrics NDJSON ingestion and summary utilities."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any, Iterable


Row = dict[str, Any]


def _iter_ndjson(path: Path) -> Iterable[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            stripped = line.strip()
            if not stripped:
                continue
            yield json.loads(stripped)


def _flatten_records(records: Iterable[dict[str, Any]], run_id: str | None) -> Iterable[Row]:
    """Convert metrics records into tidy {run_id, epoch, key, value} rows."""

    for record in records:
        epoch = record.get("epoch")
        for key, value in record.items():
            if key == "epoch":
                continue
            if isinstance(value, (int, float, str)):
                rendered = value
            else:
                rendered = json.dumps(value, ensure_ascii=False)
            yield {
                "run_id": run_id,
                "epoch": epoch,
                "key": key,
                "value": rendered,
            }


def _write_csv(rows: Iterable[Row], out_csv: Path) -> int:
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with out_csv.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["run_id", "epoch", "key", "value"])
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
            written += 1
    return written


def _try_write_parquet(in_csv: Path, out_parquet: Path) -> bool:
    try:
        import pandas as pd  # type: ignore

        df = pd.read_csv(in_csv)
        df.to_parquet(out_parquet)
        return True
    except Exception:
        return False


def _validate_with_jsonschema(data_path: Path, schema_path: Path) -> None:
    try:
        import jsonschema  # type: ignore
    except Exception as exc:  # pragma: no cover - import guards
        print(
            f"[metrics-cli] jsonschema not installed; skipping validation ({exc!r})",
            file=sys.stderr,
        )
        return

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = jsonschema.Draft7Validator(schema)
    for idx, record in enumerate(_iter_ndjson(data_path), start=1):
        try:
            validator.validate(record)
        except jsonschema.exceptions.ValidationError as exc:  # type: ignore[attr-defined]
            raise ValueError(f"schema validation failed at record {idx}: {exc.message}") from exc


def cmd_ingest(args: argparse.Namespace) -> int:
    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        print(f"[metrics-cli] input not found: {input_path}", file=sys.stderr)
        return 2

    run_id = args.run_id or input_path.stem
    schema_path = Path(args.schema).expanduser().resolve() if args.schema else None
    if schema_path is not None:
        try:
            _validate_with_jsonschema(input_path, schema_path)
        except ValueError as exc:
            print(f"[metrics-cli] {exc}", file=sys.stderr)
            return 3

    rows = _flatten_records(_iter_ndjson(input_path), run_id=run_id)
    out_csv = Path(args.out_csv).expanduser().resolve()
    written = _write_csv(rows, out_csv)

    parquet_path: Path | None = None
    if args.out_parquet:
        candidate = Path(args.out_parquet).expanduser().resolve()
        if _try_write_parquet(out_csv, candidate):
            parquet_path = candidate

    print(
        json.dumps(
            {
                "ok": True,
                "rows": written,
                "csv": out_csv.as_posix(),
                "parquet": parquet_path.as_posix() if parquet_path else None,
            }
        )
    )
    return 0


def _summarize(path: Path) -> dict[str, Any]:
    last_by_key: dict[str, Any] = {}
    min_by_key: dict[str, float] = {}
    max_by_key: dict[str, float] = {}
    epochs: set[int] = set()

    for record in _iter_ndjson(path):
        if "epoch" in record:
            try:
                epochs.add(int(record["epoch"]))
            except Exception:
                pass
        for key, value in record.items():
            if key == "epoch":
                continue
            last_by_key[key] = value
            if isinstance(value, (int, float)):
                min_by_key[key] = value if key not in min_by_key else min(min_by_key[key], value)
                max_by_key[key] = value if key not in max_by_key else max(max_by_key[key], value)

    return {
        "epochs": sorted(epochs),
        "last": last_by_key,
        "min": min_by_key,
        "max": max_by_key,
    }


def cmd_summary(args: argparse.Namespace) -> int:
    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        print(f"[metrics-cli] input not found: {input_path}", file=sys.stderr)
        return 2

    summary = _summarize(input_path)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="codex metrics", description="Metrics NDJSON utilities")
    sub = parser.add_subparsers(dest="subcommand", required=True)

    ingest = sub.add_parser("ingest", help="Ingest NDJSON into tidy CSV rows (optional Parquet)")
    ingest.add_argument("--input", required=True, help="Path to NDJSON (one JSON per line)")
    ingest.add_argument("--out-csv", required=True, help="Output CSV file path")
    ingest.add_argument(
        "--out-parquet",
        help="Optional Parquet file path (requires pandas with pyarrow or fastparquet)",
    )
    ingest.add_argument("--run-id", help="Run identifier (defaults to input stem)")
    ingest.add_argument("--schema", help="Optional JSON Schema file for validation")
    ingest.set_defaults(func=cmd_ingest)

    summary = sub.add_parser("summary", help="Print quick statistics from NDJSON")
    summary.add_argument("--input", required=True, help="Path to NDJSON metrics file")
    summary.set_defaults(func=cmd_summary)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
