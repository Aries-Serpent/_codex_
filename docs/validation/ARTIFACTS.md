# [Docs]: Phase-A Validator Artifacts (base64+gz) — decode, extract, CI

Overview
- The repository stores Phase-A validator snapshots as gzipped JSON encoded in base64 and committed under `artifacts/*.json.gz.b64`.
- A decoder script and extractor are included to produce validated JSON and human-friendly summaries.

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

1. **Decode** the bundled Base64 + gzip payload.
2. **Validate** the decoded JSON using `scripts/space_traversal/schemas/validate_report_schema.json`.
3. **Extract** gap records and emit a deterministic baseline summary.

## Dev & CI

| Task            | Command / File                                             |
|-----------------|------------------------------------------------------------|
| Install deps    | `python -m pip install -r requirements-dev.txt`            |
| Run sandbox     | `tools/run_in_sandbox.sh`                                  |
| Stable output   | `--stable-output` flag (writes deterministic manifest)     |
| Generate base   | `--generate-baseline` (writes baseline/capabilities.json)  |
| Baseline path   | `--baseline-path <path>` (explicit baseline location)      |

## CLI Flags

- `--stable-output` : deterministic output directory and `stable_manifest.json`
- `--generate-baseline` : write `baseline/capabilities_scored.json`
- `--baseline-path <path>` : explicit baseline path

## Continuous Integration

- The decode-validate workflow decodes artifacts, runs tests, and uploads decoded artifacts and validated outputs.
- Schema validation uses `jsonschema` when available and falls back to basic checks if missing.
