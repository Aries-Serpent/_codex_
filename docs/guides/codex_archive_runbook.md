# Codex Archive Runbook

This runbook documents the repeatable workflow for moving inactive code and documentation
into the Codex tombstone archive while preserving evidence and making restoration
straightforward.

## 1. Environment preparation

1. Ensure dependencies are installed: `typer`, `sqlalchemy` (for Postgres/MariaDB backends),
   and an optional `zstandard` wheel for optimal compression.
2. Configure the target database via the environment:

   ```bash
   export CODEX_ARCHIVE_BACKEND=sqlite
   export CODEX_ARCHIVE_URL=sqlite:///./.codex/archive.sqlite
   # or: export CODEX_ARCHIVE_BACKEND=postgres
   #     export CODEX_ARCHIVE_URL=postgresql://app_user:${POSTGRES_PASSWORD}@host:5432/codex
   ```
3. Verify evidence directory permissions: `.codex/evidence/` must be writable.

## 2. Initialise or migrate the schema

The CLI mirrors the portable SQL in `schemas/codex_archive.sql`. Initialise the database once
per backend:

```bash
python -m codex.cli archive init
```

To inspect the SQL before applying:

```bash
python -m codex.cli archive schema --dialect postgres > /tmp/archive-postgres.sql
```

## 3. Archive content

1. Identify the candidate file(s) and collect metadata (reason, owning team, related PR).
2. Archive each file individually to maintain deterministic ordering:

   ```bash
   python -m codex.cli archive store _codex_ src/legacy/zendesk_v1.py \
       --by "marc" \
       --reason pruned \
       --commit HEAD \
       --tag legacy --tag zendesk \
       --metadata ticket=OPS-1234
   ```

   The command returns a JSON blob with the tombstone ID, hashes, and byte counts. Replace
   the original file with a tombstone stub that references the archive ID and SHA-256.

3. Commit the tombstone stubs and raise a PR referencing:
   * Archive ID(s)
   * Reason for archival
   * Evidence log digest (line hash from `.codex/evidence/archive_ops.jsonl`)

## 4. Evidence handling

Each CLI invocation appends a JSONL record to `.codex/evidence/archive_ops.jsonl`. During PR
review attach the relevant lines and include their SHA-256 digest in the description to
maintain tamper-evident provenance.

## 5. Restore procedure

Restoring is symmetric and deterministic:

```bash
python -m codex.cli archive restore <TOMBSTONE_ID> restored/path.py --by "marc"
```

The command verifies dual-control approvals and writes the restored bytes locally. Inspect
and reintroduce via a pull request; do **not** push directly to production branches.

## 6. Prune and purge governance

* Use `archive prune-request` to log an initial request for deletion.
* Final purge requires two distinct approvers:

  ```bash
  python -m codex.cli archive purge <TOMBSTONE_ID> \
      --by "primary-approver" \
      --second "secondary-approver" \
      --reason "Contains PII" \
      --apply
  ```

  With `--apply` the blob bytes are nulled after both approvals, while metadata remains
  intact. Without `--apply` the command records approvals but retains the compressed bytes.

* Purges are blocked automatically when `legal_hold` is set.

## 7. Operational checks

* Periodically reconcile the archive with production repositories:

  ```sql
  SELECT repo, path, archived_at, tombstone_id
  FROM item
  ORDER BY archived_at DESC
  LIMIT 100;
  ```

* Audit deduplicated artifacts:

  ```sql
  SELECT content_sha256, COUNT(*) AS reuse_count
  FROM artifact a
  JOIN item i ON i.artifact_id = a.id
  GROUP BY content_sha256
  HAVING COUNT(*) > 1;
  ```

* Export JSON metadata for downstream tooling:

  ```bash
  sqlite3 .codex/archive.sqlite "SELECT json_group_array(metadata) FROM item" > artifacts.json
  ```

## 8. Incident response

1. If restore fails due to `blob_bytes` being null, confirm a purge occurred and escalate to
the dual approvers.
2. If tampering is suspected, compare evidence logs against digests recorded in PRs. The
   JSONL log is append-only and should never be rewritten.

## 9. Determinism checklist

* Run archives with a clean working tree.
* Provide explicit `--commit` SHAs for reproducibility when archiving outside Git.
* For batch operations, sort file paths lexicographically before invoking `archive store`.
