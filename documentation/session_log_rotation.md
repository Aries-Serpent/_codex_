# Session Log Rotation

The SQLite database at `.codex/session_logs.db` stores session metadata. Without maintenance it can grow indefinitely.

An index on `(session_id, ts)` is created automatically.  This index
substantially improves query performance and makes retention pruning much
faster on large log sets.

## Retention policy
- Keep only the last 30 days of entries.
- Remove older records and NDJSON files regularly to satisfy enterprise retention policies.

Use `tools/purge_session_logs.py` to remove stale NDJSON files and prune
`session_events` rows in the SQLite database:

```bash
python tools/purge_session_logs.py        # purge items older than 30 days
python tools/purge_session_logs.py --days 60   # custom retention window
python tools/purge_session_logs.py --dry-run  # show actions without deleting
```

## Archive then prune
1. **Create a backup** before deleting old rows:
   ```bash
   mkdir -p .codex/archives
   sqlite3 .codex/session_logs.db ".backup '.codex/archives/session_logs_$(date +%Y-%m-%d).db'"
   ```
2. **Delete old rows and vacuum** the database to reclaim space:
   ```bash
   sqlite3 .codex/session_logs.db "DELETE FROM session_events WHERE ts < strftime('%s','now','-30 day'); VACUUM;"
   ```

## Full reset
If the database becomes corrupted or exceptionally large, remove it and let tooling recreate a fresh database:
```bash
rm .codex/session_logs.db
```

Archive backups in a secure location according to your organization's policies.
