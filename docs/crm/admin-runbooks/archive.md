# Codex Archive (Tombstone) — Runbook

**Goal:** Never hard-delete. Move dead/pruned code & docs into a portable SQL archive with append-only evidence. Supports SQLite (default), PostgreSQL, MariaDB.

## Backends
Set env before running:
```bash
# Default (local dev):
export CODEX_ARCHIVE_BACKEND=sqlite
export CODEX_ARCHIVE_URL=sqlite:///./.codex/archive.sqlite

# PostgreSQL (requires psycopg installed)
# export CODEX_ARCHIVE_BACKEND=postgres
# export CODEX_ARCHIVE_URL=postgresql://user:pass@host/dbname  # pragma: allowlist secret

# MariaDB (requires pymysql installed)
# export CODEX_ARCHIVE_BACKEND=mariadb
# export CODEX_ARCHIVE_URL=mysql+pymysql://user:pass@host/dbname  # pragma: allowlist secret
```

## Initialize schema
For SQLite the CLI auto-creates the schema from `db/migrations/sqlite/001_init.sql`.
For Postgres/MariaDB apply the SQL under `db/migrations/{postgres|mariadb}/001_init.sql`.

## Archive a file
```bash
python -m codex.cli archive store _codex_ src/legacy/zendesk_v1.py --reason dead --by "marc" --commit d3e8729 --mime text/x-python --lang python
```
Output includes the **tombstone** (UUID) and **sha256**. Replace the file with a brief stub that points to the tombstone and restoration command.

## Restore a file
```bash
python -m codex.cli archive restore <TOMBSTONE-UUID> --out restored/zendesk_v1.py
```

## Evidence
All actions append JSONL lines to:
```text
.codex/evidence/archive_ops.jsonl
```
Each line contains: ts, action (ARCHIVE/RESTORE), actor, repo, path, tombstone, sha256, size, commit.

## Governance
- Soft-delete only. For permanent deletion, require dual approval (future enhancement).
- Optional legal hold: set it in the DB to block purge workflows.

## Notes
- SQLite is single-writer; use PostgreSQL for multi-user/scale.
- For large artifacts, you can store bytes externally (S3/minio) and set `storage_driver='object'` and `object_url`, but the default CLI uses DB BLOBs.
- Health checks: `make archive-ping` (or `python -m codex.cli archive ping`) verifies the configured backend DSN and a read/write transaction round-trip.
- Typer pattern: prefer `Annotated` signatures for CLI arguments/options to avoid Ruff B008 (e.g., `path: Annotated[Path, typer.Argument(...)]`).
- SQL safety: never interpolate identifiers; validate against an allow-list and use bound parameters. Postgres callers can rely on `psycopg.sql.Identifier` after validation.
