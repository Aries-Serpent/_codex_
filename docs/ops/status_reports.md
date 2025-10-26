# Local Status Reports

Generate a self-contained `STATUS_REPORT.md` that summarizes repository gates and (optionally) evaluates assistant candidates from a JSON summary.

## Quick Start
```bash
python tools/status_report.py \
  --summary samples/assistant_message_summary.sample.json \
  --selected 3 \
  --out STATUS_REPORT.md
```

## What it includes
- Fence integrity result
- Manifest schema validation result
- Evaluator score run (if `--summary` provided)
- Selection Guard result (if `--summary` and `--selected` provided)
- Timestamps and exit codes for reproducibility

## Notes
- This is **local-only** (no CI, no network).
- If `jsonschema` is not installed, schema checks are skipped with an info note.

## See also
- `docs/templates/status_update.md`
- `docs/ops/local_gates.md`
