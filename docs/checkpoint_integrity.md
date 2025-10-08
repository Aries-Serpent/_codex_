# Checkpoint Integrity (Atomic Writes & Digests)

Codex checkpoints are persisted with **atomic write semantics** to avoid torn files:

1. Data is written to a temporary file within the destination directory.
2. The file contents are `fsync`'d to ensure durability.
3. We perform an atomic `os.replace` onto the final path.
4. The containing directory is `fsync`'d so directory entries are flushed as well.

Each checkpoint artifact also receives a matching `.sha256` sidecar and a manifest entry for traceability. This means operators can verify integrity via `sha256sum <file>` and compare against the recorded digest.

Why this matters:

- Atomic rename on POSIX filesystems guarantees readers never observe partial files.
- Adding directory `fsync` closes the durability gap across power loss or abrupt termination.
- SHA256 sidecars plus a rolling `manifest.json` help with audits, reproducibility, and sync workflows.

Metric and event logs continue to stream to **NDJSON** for easy ingestion into tail-friendly tools.
