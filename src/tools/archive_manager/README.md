# Hybrid Code Archive Orchestrator (v4)

Artifacts:
1. **`code_archive.jsonl` (+ `.jsonl.gz`)** — append-only interchange (path, language, content)
2. **`metadata.sqlite`** — metadata index (path, language, mime, lines, sha256, parquet_row_id, deleted_at)
3. **`code_blobs.parquet` + deltas** — compressed text blobs for analytics and fast joins
4. **Tombstones** — JSONL streams that record deletes:
   - `tombstones_code.jsonl` (+ `.gz`) → code/docs/tests/configs
   - `tombstones_logs.jsonl` (+ `.gz`) → logs/test logs

## New in v4
- **Gzipped tombstones**: `update --gzip-tombstones` emits/refreshes `.gz` for any tombstones appended in that run.
- **`vacuum`** summarizes and prunes tombstones by date:
  - `--summary` totals, date ranges, unique paths, category breakdown
  - `--before YYYY-MM-DD` prune records older than the date (UTC)
  - `--dry-run` simulate pruning; no writes
  - `--gzip-tombstones` regenerate `.gz` after pruning

## Quickstart

```bash
pip install pyarrow duckdb

# Fresh build (auto workers, include code+docs, exclude logs)
python archive_manager.py build \
  --root ./my_codebase \
  --workers auto \
  --allow-globs "src/**" "docs/**" "configs/**" "tests/**" \
  --deny-globs "logs/**" "log/**" \
  --gzip-jsonl

# Update + deletion tracking w/ tombstones + gz
python archive_manager.py update \
  --root ./my_codebase \
  --workers auto \
  --allow-globs "src/**" "docs/**" "configs/**" "tests/**" \
  --deny-globs "logs/**" "log/**" \
  --track-deletes \
  --tombstones-code ./tombstones_code.jsonl \
  --tombstones-logs ./tombstones_logs.jsonl \
  --gzip-tombstones \
  --gzip-jsonl
```

### Vacuum tombstones

```bash
# Print summary (no pruning)
python archive_manager.py vacuum \
  --tombstones-code ./tombstones_code.jsonl \
  --tombstones-logs ./tombstones_logs.jsonl \
  --summary

# Prune records strictly older than 2025-06-01 (UTC) and regenerate gzip
python archive_manager.py vacuum \
  --tombstones-code ./tombstones_code.jsonl \
  --tombstones-logs ./tombstones_logs.jsonl \
  --before 2025-06-01 \
  --gzip-tombstones
```

## Notes
* JSONL is line-oriented and ideal for append-only logs and streaming; gzip reduces storage/egress.
* `query`/`verify` operate on **active** rows (`deleted_at IS NULL`).
* Delete handling mirrors lakehouse tombstones + `VACUUM` patterns (soft delete then periodic cleanup).
* DuckDB reads Parquet with `read_parquet()` and can `ATTACH` SQLite for cross-store joins.
