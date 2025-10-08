# Reproducibility & Integrity

## Seeds & Determinism
- Set all RNG seeds early; prefer deterministic kernels when available.
- Use canonical data ordering and avoid nondeterministic transforms.

## Tracking (Offline-first)
- Default to local MLflow file store (`file:///.../mlruns`).
- If using remote tools, prefer explicit offline modes during local runs.

## NDJSON Metrics
- Emit and summarize metrics via the package CLI:
  ```bash
  python -m codex_ml ndjson-summary --input artifacts/
  ```

References:
- MLflow `file:///` examples for local tracking URIs.
- JSON Lines (NDJSON): one JSON value per line, UTF-8.
