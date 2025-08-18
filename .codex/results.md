# Results Summary

## Implemented

* src/codex/logging/query_logs.py
* scripts/smoke_query_logs.sh
* README.md: appended "Logging: Querying transcripts"
* .codex/mapping.md

## Residual gaps

* SQLite database is not included. Provide a DB at $CODEX_DB_PATH (default: data/codex.db) with a 'session_events' table.

## Pruning

* None

## Next recommended steps

* Add a minimal sample DB for CI-less validation.
* Extend query output to include metadata fields when present.

**DO NOT ACTIVATE ANY GitHub Actions files.**
