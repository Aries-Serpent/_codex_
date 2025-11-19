# Artifact decoding and validation

This document describes the lightweight decoding helpers added for the audit artifacts.

## Quickstart

```bash
python scripts/space_traversal/decode_validate_and_extract.py \
  --input tests/fixtures/pasted.txt \
  --output audit_artifacts/decoded_snapshot.json \
  --extract audit_artifacts/gaps_extracted.json \
  --stable-output \
  --generate-baseline
```

The workflow performs three steps:

1. Decode the bundled Base64 + gzip payload.
2. Validate the decoded JSON using `scripts/space_traversal/schemas/validate_report_schema.json`.
3. Extract gap records and emit a deterministic baseline summary.

## Development dependencies

Schema validation uses `jsonschema` when available. Install development dependencies with:

```bash
pip install -r requirements-dev.txt
```

If `jsonschema` is unavailable, the validator falls back to simple structural checks.
