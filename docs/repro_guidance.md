# Reproducibility & Integrity

**Last Updated:** 2026-06-22

## Seeds & Determinism
- Set all RNG seeds early; prefer deterministic kernels when available.
- Use canonical data ordering and avoid nondeterministic transforms.

## Tracking (Offline-first)
- Default to local MLflow file store. Accept file: URIs; normalize absolute paths to ``file:///.../mlruns``.
