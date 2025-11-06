# TOMBSTONE — <original_path>

This tombstone replaces the removed artifact `<original_path>`.

- removed_on: 2025-11-06T00:00:00Z
- removed_by: <actor>
- reason: <obsolete|superseded|reorg|policy>
- adr_ref: docs/arch/ADR-YYYYMMDD-brief-title.md
- commit_sha: <commit-sha>
- replacement: <new/path or "none">
- pointer_bundle: <audit_artifacts/bundles/bundle_<ts>.pointer.json (optional)>

## Guidance

1. The ADR referenced above must exist and explain rationale, alternatives, rollback plan, and migration steps.
2. The tombstone file should remain in-tree where the original file resided (same path).
3. An evidence event must be appended to `.codex/evidence/archive_ops.jsonl` using the archival API or CLI tooling.
4. For bulk removals, follow pointer bundle strategy to capture originals before deleting.
