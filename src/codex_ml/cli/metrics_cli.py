"""Metrics NDJSON ingestion and summary utilities."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sqlite3
import sys
from pathlib import Path
from typing import Any, Iterable


Row = dict[str, Any]


# =============================================================================
# Identifier safety
# =============================================================================
_SAFE_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _validate_table(name: str, allow_unsafe: bool = False) -> str:
    """Return validated SQL identifier for table names."""

    if allow_unsafe or _SAFE_IDENT.fullmatch(name or ""):
        return name
    raise SystemExit(f"[metrics-cli] invalid table name: {name!r}")


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


def _csv_to_sqlite(
    csv_path: Path,
    sqlite_db: Path,
    table: str,
    *,
    chunk_size: int = 5000,
    create_index: bool = False,
    allow_unsafe_table_name: bool = False,
) -> None:
    """Bulk load CSV into SQLite using chunked executemany and optional index."""

    sqlite_db.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(sqlite_db)
    try:
        cur = con.cursor()
        table_safe = _validate_table(table or "metrics", allow_unsafe_table_name)
        cur.execute(
            f"CREATE TABLE IF NOT EXISTS {table_safe} "
            "(run_id TEXT, epoch INTEGER, key TEXT, value TEXT)"
        )
        con.execute("BEGIN IMMEDIATE")
        import csv as _csv

        with csv_path.open("r", encoding="utf-8", newline="") as fh:
            reader = _csv.DictReader(fh)
            buf: list[tuple[Any, Any, Any, Any]] = []
            batch = max(1, int(chunk_size))
            for row in reader:
                buf.append(
                    (
                        row.get("run_id"),
                        int(row["epoch"]) if row.get("epoch") not in (None, "") else None,
                        row.get("key"),
                        row.get("value"),
                    )
                )
                if len(buf) >= batch:
                    cur.executemany(
                        f"INSERT INTO {table_safe} (run_id, epoch, key, value) VALUES (?, ?, ?, ?)",
                        buf,
                    )
                    buf.clear()
            if buf:
                cur.executemany(
                    f"INSERT INTO {table_safe} (run_id, epoch, key, value) VALUES (?, ?, ?, ?)",
                    buf,
                )
        if create_index:
            cur.execute(
                f"CREATE INDEX IF NOT EXISTS idx_{table_safe}_rke ON {table_safe}(run_id, key, epoch)"
            )
        con.commit()
    finally:
        con.close()


def _csv_to_duckdb(
    csv_path: Path,
    duck_db: Path,
    table: str,
    *,
    mode: str = "replace",
    allow_unsafe_table_name: bool = False,
) -> bool:
    """Bulk load CSV into DuckDB with selectable write mode."""

    try:
        import duckdb  # type: ignore
    except Exception:
        return False

    duck_db.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(duck_db.as_posix())
    try:
        table_safe = _validate_table(table or "metrics", allow_unsafe_table_name)
        csvp = csv_path.as_posix()
        mode_normalized = (mode or "replace").lower()
        if mode_normalized == "replace":
            con.execute(
                f"CREATE OR REPLACE TABLE {table_safe} AS SELECT * FROM read_csv_auto('{csvp}')"
            )
        elif mode_normalized == "append":
            con.execute(
                f"CREATE TABLE IF NOT EXISTS {table_safe} AS SELECT * FROM read_csv_auto('{csvp}') WHERE 1=0"
            )
            con.execute(f"INSERT INTO {table_safe} SELECT * FROM read_csv_auto('{csvp}')")
        elif mode_normalized == "fail":
            con.execute(f"CREATE TABLE {table_safe} AS SELECT * FROM read_csv_auto('{csvp}')")
        else:
            raise SystemExit(f"[metrics-cli] unsupported --mode: {mode!r}")
        return True
    finally:
        con.close()


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

    sink_info: dict[str, Any] = {}
    if args.to_sqlite:
        db = Path(args.to_sqlite).expanduser().resolve()
        table = args.table or "metrics"
        _csv_to_sqlite(
            out_csv,
            db,
            table,
            chunk_size=int(getattr(args, "chunk_size", 5000)),
            create_index=bool(getattr(args, "create_index", False)),
            allow_unsafe_table_name=bool(getattr(args, "allow_unsafe_table_name", False)),
        )
        sink_info["sqlite"] = {"db": db.as_posix(), "table": table}

    if args.to_duckdb:
        db = Path(args.to_duckdb).expanduser().resolve()
        table = args.table or "metrics"
        enabled = _csv_to_duckdb(
            out_csv,
            db,
            table,
            mode=str(getattr(args, "mode", "replace")),
            allow_unsafe_table_name=bool(getattr(args, "allow_unsafe_table_name", False)),
        )
        sink_info["duckdb"] = {
            "db": db.as_posix(),
            "table": table,
            "enabled": enabled,
        }

    print(
        json.dumps(
            {
                "ok": True,
                "rows": written,
                "csv": out_csv.as_posix(),
                "parquet": parquet_path.as_posix() if parquet_path else None,
                **sink_info,
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

    ingest = sub.add_parser(
        "ingest", help="Ingest NDJSON into tidy CSV rows (optional Parquet/DBs)"
    )
    ingest.add_argument("--input", required=True, help="Path to NDJSON (one JSON per line)")
    ingest.add_argument("--out-csv", required=True, help="Output CSV file path")
    ingest.add_argument(
        "--out-parquet",
        help="Optional Parquet file path (requires pandas with pyarrow or fastparquet)",
    )
    ingest.add_argument("--run-id", help="Run identifier (defaults to input stem)")
    ingest.add_argument("--schema", help="Optional JSON Schema file for validation")
    ingest.add_argument("--to-sqlite", help="Optional SQLite database file to upsert table")
    ingest.add_argument("--to-duckdb", help="Optional DuckDB database file to upsert table")
    ingest.add_argument("--table", help="Target table name (default: metrics)")
    ingest.add_argument(
        "--mode",
        choices=["replace", "append", "fail"],
        default="replace",
        help="DuckDB table-write mode (default: replace)",
    )
    ingest.add_argument(
        "--chunk-size",
        type=int,
        default=5000,
        help="SQLite INSERT chunk size for executemany() (default: 5000)",
    )
    ingest.add_argument(
        "--create-index",
        action="store_true",
        help="Create index on (run_id, key, epoch) after load (off by default)",
    )
    ingest.add_argument(
        "--allow-unsafe-table-name",
        action="store_true",
        help="Bypass conservative identifier validation (use with caution)",
    )
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
