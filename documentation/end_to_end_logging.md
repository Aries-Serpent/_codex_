# End-to-End Logging

This guide describes the environment variables and the start→message→end logging pattern.

## 1) Environment

* **CODEX_SESSION_ID**: A UUID tying multiple invocations together.
* **CODEX_LOG_DB_PATH**: Path to a SQLite DB (or NDJSON) where events are stored.

### Shell Setup

**Bash/Zsh**

```bash
export CODEX_SESSION_ID="$(uuidgen || python -c 'import uuid;print(uuid.uuid4())')"
export CODEX_LOG_DB_PATH="${PWD}/.codex/session_logs.db"
```

**PowerShell**

```powershell
$env:CODEX_SESSION_ID = [guid]::NewGuid().ToString()
$env:CODEX_LOG_DB_PATH = (Join-Path (Get-Location) ".codex/session_logs.db")
```

## NDJSON as Canonical Source

Session hooks write newline-delimited JSON files under
``.codex/sessions/<SESSION_ID>.ndjson``.  These files are treated as the
authoritative record of events.  A separate importer synchronizes the NDJSON
into the SQLite ``session_events`` table so tools that expect a database view
remain functional.

Run the importer after sessions complete:

```bash
codex-import-ndjson --session "$CODEX_SESSION_ID"
```

To ingest all sessions in the log directory:

```bash
codex-import-ndjson --all
```

The importer tracks a ``session_ingest_watermark`` for each session to avoid
duplicating already processed lines.

## 2) Quick Start

```python
import os, sqlite3, time, pathlib

sid = os.getenv("CODEX_SESSION_ID", "dev-session")
db = pathlib.Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
db.parent.mkdir(parents=True, exist_ok=True)

con = sqlite3.connect(db)
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS logs(ts REAL, session TEXT, kind TEXT, message TEXT)")

def log(kind, msg):
    cur.execute("INSERT INTO logs(ts, session, kind, message) VALUES(strftime('%s','now'), ?, ?, ?)", (sid, kind, msg))

log("start", "session begin")
log("message", "processing step A")
log("message", "processing step B")
log("end", "session end")
con.commit(); con.close()
```

## 3) Viewing Logs

If you have `tools/codex_log_viewer.py`:

```bash
python tools/codex_log_viewer.py --db "$CODEX_LOG_DB_PATH" --session "$CODEX_SESSION_ID"
```

Options:

* `--db` (default: `./.codex/session_logs.db`)
* `--session` (optional filter)
* `--tail` (show latest N rows)

> **Compliance:** DO NOT ACTIVATE ANY GitHub Actions files.

## Example Script

The repository includes [`scripts/codex_end_to_end.py`](../scripts/codex_end_to_end.py),
which records a short conversation with `conversation_logger` and then queries
the transcript using `codex.logging.query_logs`.
