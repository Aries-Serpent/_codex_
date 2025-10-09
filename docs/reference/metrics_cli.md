# Reference: `codex_ml.cli metrics`

## Synopsis
```bash
python -m codex_ml.cli metrics <subcommand> [options]
```

## Subcommands
- `ingest` — read NDJSON and produce a tidy CSV (and optionally Parquet).
- `summary` — print quick statistics from NDJSON metrics.

## Options (ingest)
- `--input PATH` (required): NDJSON input file.
- `--out-csv PATH` (required): CSV output path.
- `--out-parquet PATH` (optional): Parquet output path (requires `pandas`).
- `--run-id STR` (optional): Label written into the `run_id` column.
- `--schema PATH` (optional): JSON Schema to validate each record.
- `--to-sqlite PATH` (optional): Load rows into a SQLite table.
- `--to-duckdb PATH` (optional): Load rows into a DuckDB table.
- `--table STR` (optional): Destination table name (default: `metrics`).
- `--mode {replace,append,fail}` (optional): DuckDB write semantics (default: `replace`).
- `--chunk-size INT` (optional): SQLite `executemany()` batch size (default: `5000`).
- `--create-index` (flag): Build `(run_id, key, epoch)` index in SQLite.
- `--allow-unsafe-table-name` (flag): Bypass conservative identifier validation.

## Options (summary)
- `--input PATH` (required): NDJSON input file.
