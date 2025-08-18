# Mapping Table
| Task | candidate_assets[] | Rationale |
|---|---|---|
| Add `query_logs.py` | (new) `src/codex/logging/query_logs.py` | No prior logging module; standard src layout; localized change |
| SQL on `session_events` | `data/*.db` if present; else `$CODEX_DB_PATH` | Probe SQLite DB path; adapt to schema via PRAGMA |
| README CLI docs | `README.md` | Append a “Logging / Query CLI” section |
