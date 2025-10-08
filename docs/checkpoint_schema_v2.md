# Checkpoint Schema v2

**Intent**: deterministic, reproducible checkpoint metadata.

- Canonical JSON for hashing/signing (see RFC 8785 / JCS).
- I-JSON constraints (no NaN/Inf; Unicode preserved; IEEE-754 numbers).
- Minimal meta fields: run_id, step, epoch, created_utc, digest.

See also:
- `codex_ml.checkpointing.schema_v2` (implementation)
- `codex_ml.cli.manifest` (hash/validate)
