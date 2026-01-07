# Guide: Offline Workflow and Reproducibility
> Generated: 2025-10-20 06:15:16 UTC | Author: mbaetiong

This guide defines a deterministic, offline-first workflow for running audits, tests, and training.

## Principles
- Determinism: fixed seeds, pinned dependencies, reproducible artifacts.
- Offline Safety: no network I/O; disable online telemetry; verify dataset and model integrity via checksums.
- Minimal Writes: write to `audit_artifacts/` and `reports/` only during audits.

## Environment
- Set `WANDB_MODE=offline` to prevent network calls from tracking backends.
- Set `PYTHONHASHSEED` to a fixed value (e.g., `0`).
- Ensure torch and numpy seeds are set consistently where applicable.
- Pin package versions in Dockerfiles and `pyproject.toml`; avoid `:latest` tags.

## Checksums and Integrity
- Prefer `sha256` digests for datasets and checkpoints.
- Validate manifests before use; store canonical JSON with normalized formatting.

## Commands
- Fast audit: `make space-audit-fast`
- Full audit: `python scripts/space_traversal/audit_runner.py run`
- Status update: `python scripts/space_traversal/status_update_report.py [--base baseline/capabilities_scored.json]`
- Diff: `python scripts/space_traversal/audit_runner.py diff --old A --new B`

## Expected Artifacts
- `audit_artifacts/`: `context_index.json`, `facets.json`, `capabilities_raw.json`, `capabilities_scored.json`, `gaps.json`
- `reports/`: `capability_matrix_<ts>.md`, `codex_status_update_<ts>.md`
- `audit_run_manifest.json`

## Safeguard Keywords
- `sha256`, `checksum`, `rng`, `seed`, `offline`, `WANDB_MODE`
