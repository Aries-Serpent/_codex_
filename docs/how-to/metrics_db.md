# Metrics DB Sinks (SQLite & DuckDB)

Use the metrics CLI to ingest NDJSON metrics into CSV, SQLite, or DuckDB targets.

## SQLite

```bash
python -m codex_ml.cli metrics ingest \
  --input runs.ndjson --out-csv runs.csv \
  --to-sqlite runs.sqlite --table metrics \
  --chunk-size 5000 --create-index
```

- Loads via a single transaction with chunked `executemany()` batches.
- `--chunk-size` tunes batch size (default: `5000`).
- `--create-index` builds `(run_id, key, epoch)` after load.
- Table names are validated (regex `^[A-Za-z_][A-Za-z0-9_]*$`); override with `--allow-unsafe-table-name`.

## DuckDB

```bash
python -m codex_ml.cli metrics ingest \
  --input runs.ndjson --out-csv runs.csv \
  --to-duckdb runs.duckdb --table metrics --mode replace
```

| Mode    | Behavior                                                                |
|---------|-------------------------------------------------------------------------|
| replace | `CREATE OR REPLACE TABLE t AS SELECT * FROM read_csv_auto(...)`         |
| append  | `CREATE TABLE IF NOT EXISTS t ...; INSERT INTO t SELECT * FROM ...`     |
| fail    | `CREATE TABLE t AS SELECT * FROM ...` (errors if `t` already exists)    |

DuckDB types are inferred via `read_csv_auto`. For strict control, load into staging tables before casting.

## Exit Codes

| Code | Meaning                 |
|------|-------------------------|
| 0    | Success                 |
| 2    | Input not found         |
| 3    | Schema validation failed|
