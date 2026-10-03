# Historical .codex root archive

This archive contains `.codex` files that were historical, report-style, or no longer active operational state and were moved out of the active top-level status to prevent the active `.codex/` root from acting as a live operational index.

## Archive label

`ARCHIVED_HISTORICAL_ROOT`

## Queryable artifacts

- `manifest.json` — full structured manifest for all items
- `index.csv` — flat query-ready inventory
- `metadata/` — per-file JSON metadata with archive state, hashes, and source paths
- `checksums/` — sha256 files for integrity verification

## Query examples

```bash
jq '.total_files' .codex/archive/legacy-root/manifest.json
jq '.items[] | {id, archive_label, status, archive_path}' .codex/archive/legacy-root/manifest.json
cut -d, -f1,2,3 .codex/archive/legacy-root/index.csv | head
```

## Policy

- Operational files remain in the active root namespace.
- Historical artifacts are stored here with an explicit archive label and checksum.
- Files in this archive should be treated as read-only reference material unless formally restored.
