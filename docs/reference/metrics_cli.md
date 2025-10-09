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

## Options (summary)
- `--input PATH` (required): NDJSON input file.
