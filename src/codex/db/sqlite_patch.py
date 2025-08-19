import os, sqlite3, threading, contextlib, atexit
from typing import Dict, Tuple

_ORIG_CONNECT = sqlite3.connect
_POOL_ENABLED_ENV = "CODEX_SQLITE_POOL"      # "1" enables pooling
_SESSION_ENV     = "CODEX_SESSION_ID"        # optional logical session id

# Key: (db_path, pid, tid, session_id)
_CONN_POOL: Dict[Tuple[str,int,int,str], sqlite3.Connection] = {}
_POOL_LOCK = threading.RLock()

def _key(database: str) -> Tuple[str,int,int,str]:
    import os, threading
    pid = os.getpid()
    tid = threading.get_ident()
    sid = os.getenv(_SESSION_ENV, "")
    return (database, pid, tid, sid)

def _apply_pragmas(conn: sqlite3.Connection) -> None:
    try:
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("PRAGMA synchronous=NORMAL;")
        cur.execute("PRAGMA temp_store=MEMORY;")
        cur.execute("PRAGMA mmap_size=30000000000;")  # best-effort; ignored if unsupported
        cur.close()
    except Exception:
        pass

def pooled_connect(database, *args, **kwargs):
    # Fallback if pooling off
    if os.getenv(_POOL_ENABLED_ENV, "0") not in ("1","true","TRUE","yes","YES"):
        return _ORIG_CONNECT(database, *args, **kwargs)

    # Ensure multi-thread use is allowed on same connection
    kwargs = dict(kwargs)
    kwargs.setdefault("check_same_thread", False)

    k = _key(str(database))
    with _POOL_LOCK:
        conn = _CONN_POOL.get(k)
        if conn is None:
            conn = _ORIG_CONNECT(database, *args, **kwargs)
            _apply_pragmas(conn)
            _CONN_POOL[k] = conn
        return conn

def enable_pooling():
    sqlite3.connect = pooled_connect

def disable_pooling():
    sqlite3.connect = _ORIG_CONNECT

def auto_enable_from_env():
    if os.getenv(_POOL_ENABLED_ENV, "0") in ("1","true","TRUE","yes","YES"):
        enable_pooling()

@atexit.register
def _close_all():
    with _POOL_LOCK:
        for k, conn in list(_CONN_POOL.items()):
            try: conn.close()
            except Exception: pass
        _CONN_POOL.clear()
