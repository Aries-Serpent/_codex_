# Run Artifact Retention

**Last Updated:** 2026-06-22

- Keep the latest failed run and the last 20 successful runs or 90 iterations, whichever is longer.
- Older artifacts may be pruned.
- Optional WORM archiving: set `CODEX_ENABLE_WORM=1` and `CODEX_WORM_BUCKET` to ship immutable copies to object storage.
