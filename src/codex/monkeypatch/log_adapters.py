"""
Adapter for codebases lacking log_event/log_message.
If project already defines them, the existing definitions will use pooled
sqlite via patch injection (see sqlite_patch). Otherwise, these provide a
minimal baseline.
"""
import os, sqlite3, time

_DB_PATH = os.getenv("CODEX_SQLITE_DB", "codex_data.sqlite3")

def _ensure_table():
    conn = sqlite3.connect(_DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS app_log(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts REAL NOT NULL,
            level TEXT,
            message TEXT,
            meta TEXT
        );
    """)
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL","0") not in ("1","true","TRUE","yes","YES"):
        conn.close()

def log_event(level: str, message: str, meta: str = None):
    _ensure_table()
    conn = sqlite3.connect(_DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO app_log(ts, level, message, meta) VALUES(?,?,?,?)",
                (time.time(), level, message, meta))
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL","0") not in ("1","true","TRUE","yes","YES"):
        conn.close()

def log_message(message: str, level: str = "INFO", meta: str = None):
    return log_event(level=level, message=message, meta=meta)
