# NDJSON Summary CLI

Summarise rotated `metrics.ndjson` shards into CSV or JSONL reports.

```bash
python -m codex_ml.cli.ndjson_summary --input artifacts/metrics.ndjson --output-format csv
```

The command delegates to `codex_utils.cli.ndjson_summary` but routes through
Codex ML's structured logging to capture CLI start/finish events.

Key tips:
- Inputs may be a directory containing `metrics.ndjson` + rotated shards or a
  single NDJSON file.
- Use `--output` to write the aggregated results to a file; omit it to print to
  stdout.
