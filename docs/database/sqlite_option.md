# SQLite Option A Configuration

Option A stores all conversation logs in a local SQLite database. The database
can be shared across tools and supports a lightweight connection pool for
improved concurrent writes.

## Enable connection pooling

```bash
export CODEX_SQLITE_POOL=1
```
With the environment variable set, the `src.codex.db.sqlite_patch` module
patches `sqlite3.connect` to reuse a connection per thread and applies helpful
`PRAGMA` settings such as `journal_mode=WAL`.

## Selecting the database path

Tools look for `CODEX_LOG_DB_PATH` or `CODEX_DB_PATH` to locate the SQLite file.
If unset, `.codex/session_logs.db` is used.

```bash
export CODEX_LOG_DB_PATH=/tmp/session_logs.db
```
Any command that uses the logging utilities will create the database if it does
not already exist.
