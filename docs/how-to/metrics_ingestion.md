# How-to: Ingest training metrics (NDJSON → CSV/Parquet)

This guide demonstrates converting newline-delimited JSON (**NDJSON**) metrics into tidy tabular files for downstream analysis.

## Prerequisites
- Metrics logging already writes an NDJSON artifact (for example `metrics.ndjson`).
- Python environment with optional `pandas` (for Parquet output).

## Steps
```bash
# Convert NDJSON → CSV (always)
python -m codex_ml.cli metrics ingest --input artifacts/metrics.ndjson --out-csv artifacts/metrics.csv

# Optional: also emit Parquet (requires pandas + pyarrow/fastparquet)
python -m codex_ml.cli metrics ingest --input artifacts/metrics.ndjson \
  --out-csv artifacts/metrics.csv --out-parquet artifacts/metrics.parquet

# Print quick stats (last/min/max by key)
python -m codex_ml.cli metrics summary --input artifacts/metrics.ndjson
```

### Notes
- NDJSON = "one JSON object per line"; the CLI streams the file to keep memory usage low.
- Provide `--schema schema.json` to validate against a JSON Schema (requires `jsonschema`).
- Parquet output is attempted only when `--out-parquet` is supplied *and* `pandas` is installed.
