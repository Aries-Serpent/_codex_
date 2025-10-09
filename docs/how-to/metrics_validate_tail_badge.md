# Metrics: Validate, Tail & Badge

This guide shows how to:

- **Validate** NDJSON metrics with a JSON Schema (Draft-07)
- **Tail** the last N records (optionally follow)
- **Update a README** badge with the latest metric value

## Validate

```bash
python -m codex_ml.cli metrics validate \
  --input artifacts/train.ndjson \
  --schema schemas/metrics.ndjson.schema.json
```

Draft-07 is used for compatibility and stability. Install `jsonschema` if validation is desired.

## Tail
```bash
python -m codex_ml.cli metrics tail --input artifacts/train.ndjson --n 20 --follow
```

## Badge
Insert the following markers in your `README.md`:
```md
<!-- codex:metric-badge:start -->
<!-- codex:metric-badge:end -->
```
Then run:
```bash
python -m codex_ml.cli metrics badge \
  --input artifacts/train.ndjson \
  --readme README.md \
  --metric val_loss \
  --label val_loss \
  --precision 4
```

> The badge is static Markdown; no network access occurs while updating it.
