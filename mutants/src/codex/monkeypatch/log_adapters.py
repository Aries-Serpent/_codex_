"""
Adapter for codebases lacking log_event/log_message.
If project already defines them, the existing definitions will use pooled
sqlite via patch injection (see sqlite_patch). Otherwise, these provide a
minimal baseline.
"""

from __future__ import annotations

import os
import sqlite3
import time
from pathlib import Path
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


def x__resolve_path__mutmut_orig(db_path: Path | None) -> Path:
    """Return ``db_path`` or fall back to ``CODEX_LOG_DB_PATH`` env var."""
    if db_path is not None:
        return Path(db_path)
    return Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))


def x__resolve_path__mutmut_1(db_path: Path | None) -> Path:
    """Return ``db_path`` or fall back to ``CODEX_LOG_DB_PATH`` env var."""
    if db_path is None:
        return Path(db_path)
    return Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))


def x__resolve_path__mutmut_2(db_path: Path | None) -> Path:
    """Return ``db_path`` or fall back to ``CODEX_LOG_DB_PATH`` env var."""
    if db_path is not None:
        return Path(None)
    return Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))


def x__resolve_path__mutmut_3(db_path: Path | None) -> Path:
    """Return ``db_path`` or fall back to ``CODEX_LOG_DB_PATH`` env var."""
    if db_path is not None:
        return Path(db_path)
    return Path(None)


def x__resolve_path__mutmut_4(db_path: Path | None) -> Path:
    """Return ``db_path`` or fall back to ``CODEX_LOG_DB_PATH`` env var."""
    if db_path is not None:
        return Path(db_path)
    return Path(os.getenv(None, ".codex/session_logs.db"))


def x__resolve_path__mutmut_5(db_path: Path | None) -> Path:
    """Return ``db_path`` or fall back to ``CODEX_LOG_DB_PATH`` env var."""
    if db_path is not None:
        return Path(db_path)
    return Path(os.getenv("CODEX_LOG_DB_PATH", None))


def x__resolve_path__mutmut_6(db_path: Path | None) -> Path:
    """Return ``db_path`` or fall back to ``CODEX_LOG_DB_PATH`` env var."""
    if db_path is not None:
        return Path(db_path)
    return Path(os.getenv(".codex/session_logs.db"))


def x__resolve_path__mutmut_7(db_path: Path | None) -> Path:
    """Return ``db_path`` or fall back to ``CODEX_LOG_DB_PATH`` env var."""
    if db_path is not None:
        return Path(db_path)
    return Path(os.getenv("CODEX_LOG_DB_PATH", ))


def x__resolve_path__mutmut_8(db_path: Path | None) -> Path:
    """Return ``db_path`` or fall back to ``CODEX_LOG_DB_PATH`` env var."""
    if db_path is not None:
        return Path(db_path)
    return Path(os.getenv("XXCODEX_LOG_DB_PATHXX", ".codex/session_logs.db"))


def x__resolve_path__mutmut_9(db_path: Path | None) -> Path:
    """Return ``db_path`` or fall back to ``CODEX_LOG_DB_PATH`` env var."""
    if db_path is not None:
        return Path(db_path)
    return Path(os.getenv("codex_log_db_path", ".codex/session_logs.db"))


def x__resolve_path__mutmut_10(db_path: Path | None) -> Path:
    """Return ``db_path`` or fall back to ``CODEX_LOG_DB_PATH`` env var."""
    if db_path is not None:
        return Path(db_path)
    return Path(os.getenv("CODEX_LOG_DB_PATH", "XX.codex/session_logs.dbXX"))


def x__resolve_path__mutmut_11(db_path: Path | None) -> Path:
    """Return ``db_path`` or fall back to ``CODEX_LOG_DB_PATH`` env var."""
    if db_path is not None:
        return Path(db_path)
    return Path(os.getenv("CODEX_LOG_DB_PATH", ".CODEX/SESSION_LOGS.DB"))

x__resolve_path__mutmut_mutants : ClassVar[MutantDict] = {
'x__resolve_path__mutmut_1': x__resolve_path__mutmut_1, 
    'x__resolve_path__mutmut_2': x__resolve_path__mutmut_2, 
    'x__resolve_path__mutmut_3': x__resolve_path__mutmut_3, 
    'x__resolve_path__mutmut_4': x__resolve_path__mutmut_4, 
    'x__resolve_path__mutmut_5': x__resolve_path__mutmut_5, 
    'x__resolve_path__mutmut_6': x__resolve_path__mutmut_6, 
    'x__resolve_path__mutmut_7': x__resolve_path__mutmut_7, 
    'x__resolve_path__mutmut_8': x__resolve_path__mutmut_8, 
    'x__resolve_path__mutmut_9': x__resolve_path__mutmut_9, 
    'x__resolve_path__mutmut_10': x__resolve_path__mutmut_10, 
    'x__resolve_path__mutmut_11': x__resolve_path__mutmut_11
}

def _resolve_path(*args, **kwargs):
    result = _mutmut_trampoline(x__resolve_path__mutmut_orig, x__resolve_path__mutmut_mutants, args, kwargs)
    return result 

_resolve_path.__signature__ = _mutmut_signature(x__resolve_path__mutmut_orig)
x__resolve_path__mutmut_orig.__name__ = 'x__resolve_path'


def x__ensure_table__mutmut_orig(db_path: Path) -> None:
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS app_log(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts REAL NOT NULL,
            level TEXT,
            message TEXT,
            meta TEXT
        );
        """
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", "0") not in ("1", "true", "TRUE", "yes", "YES"):
        conn.close()


def x__ensure_table__mutmut_1(db_path: Path) -> None:
    conn = None
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS app_log(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts REAL NOT NULL,
            level TEXT,
            message TEXT,
            meta TEXT
        );
        """
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", "0") not in ("1", "true", "TRUE", "yes", "YES"):
        conn.close()


def x__ensure_table__mutmut_2(db_path: Path) -> None:
    conn = sqlite3.connect(None)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS app_log(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts REAL NOT NULL,
            level TEXT,
            message TEXT,
            meta TEXT
        );
        """
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", "0") not in ("1", "true", "TRUE", "yes", "YES"):
        conn.close()


def x__ensure_table__mutmut_3(db_path: Path) -> None:
    conn = sqlite3.connect(str(None))
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS app_log(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts REAL NOT NULL,
            level TEXT,
            message TEXT,
            meta TEXT
        );
        """
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", "0") not in ("1", "true", "TRUE", "yes", "YES"):
        conn.close()


def x__ensure_table__mutmut_4(db_path: Path) -> None:
    conn = sqlite3.connect(str(db_path))
    cur = None
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS app_log(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts REAL NOT NULL,
            level TEXT,
            message TEXT,
            meta TEXT
        );
        """
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", "0") not in ("1", "true", "TRUE", "yes", "YES"):
        conn.close()


def x__ensure_table__mutmut_5(db_path: Path) -> None:
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute(
        None
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", "0") not in ("1", "true", "TRUE", "yes", "YES"):
        conn.close()


def x__ensure_table__mutmut_6(db_path: Path) -> None:
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS app_log(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts REAL NOT NULL,
            level TEXT,
            message TEXT,
            meta TEXT
        );
        """
    )
    conn.commit()
    cur.close()
    if os.getenv(None, "0") not in ("1", "true", "TRUE", "yes", "YES"):
        conn.close()


def x__ensure_table__mutmut_7(db_path: Path) -> None:
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS app_log(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts REAL NOT NULL,
            level TEXT,
            message TEXT,
            meta TEXT
        );
        """
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", None) not in ("1", "true", "TRUE", "yes", "YES"):
        conn.close()


def x__ensure_table__mutmut_8(db_path: Path) -> None:
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS app_log(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts REAL NOT NULL,
            level TEXT,
            message TEXT,
            meta TEXT
        );
        """
    )
    conn.commit()
    cur.close()
    if os.getenv("0") not in ("1", "true", "TRUE", "yes", "YES"):
        conn.close()


def x__ensure_table__mutmut_9(db_path: Path) -> None:
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS app_log(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts REAL NOT NULL,
            level TEXT,
            message TEXT,
            meta TEXT
        );
        """
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", ) not in ("1", "true", "TRUE", "yes", "YES"):
        conn.close()


def x__ensure_table__mutmut_10(db_path: Path) -> None:
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS app_log(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts REAL NOT NULL,
            level TEXT,
            message TEXT,
            meta TEXT
        );
        """
    )
    conn.commit()
    cur.close()
    if os.getenv("XXCODEX_SQLITE_POOLXX", "0") not in ("1", "true", "TRUE", "yes", "YES"):
        conn.close()


def x__ensure_table__mutmut_11(db_path: Path) -> None:
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS app_log(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts REAL NOT NULL,
            level TEXT,
            message TEXT,
            meta TEXT
        );
        """
    )
    conn.commit()
    cur.close()
    if os.getenv("codex_sqlite_pool", "0") not in ("1", "true", "TRUE", "yes", "YES"):
        conn.close()


def x__ensure_table__mutmut_12(db_path: Path) -> None:
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS app_log(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts REAL NOT NULL,
            level TEXT,
            message TEXT,
            meta TEXT
        );
        """
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", "XX0XX") not in ("1", "true", "TRUE", "yes", "YES"):
        conn.close()


def x__ensure_table__mutmut_13(db_path: Path) -> None:
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS app_log(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts REAL NOT NULL,
            level TEXT,
            message TEXT,
            meta TEXT
        );
        """
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", "0") in ("1", "true", "TRUE", "yes", "YES"):
        conn.close()


def x__ensure_table__mutmut_14(db_path: Path) -> None:
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS app_log(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts REAL NOT NULL,
            level TEXT,
            message TEXT,
            meta TEXT
        );
        """
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", "0") not in ("XX1XX", "true", "TRUE", "yes", "YES"):
        conn.close()


def x__ensure_table__mutmut_15(db_path: Path) -> None:
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS app_log(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts REAL NOT NULL,
            level TEXT,
            message TEXT,
            meta TEXT
        );
        """
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", "0") not in ("1", "XXtrueXX", "TRUE", "yes", "YES"):
        conn.close()


def x__ensure_table__mutmut_16(db_path: Path) -> None:
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS app_log(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts REAL NOT NULL,
            level TEXT,
            message TEXT,
            meta TEXT
        );
        """
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", "0") not in ("1", "TRUE", "TRUE", "yes", "YES"):
        conn.close()


def x__ensure_table__mutmut_17(db_path: Path) -> None:
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS app_log(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts REAL NOT NULL,
            level TEXT,
            message TEXT,
            meta TEXT
        );
        """
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", "0") not in ("1", "true", "XXTRUEXX", "yes", "YES"):
        conn.close()


def x__ensure_table__mutmut_18(db_path: Path) -> None:
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS app_log(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts REAL NOT NULL,
            level TEXT,
            message TEXT,
            meta TEXT
        );
        """
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", "0") not in ("1", "true", "true", "yes", "YES"):
        conn.close()


def x__ensure_table__mutmut_19(db_path: Path) -> None:
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS app_log(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts REAL NOT NULL,
            level TEXT,
            message TEXT,
            meta TEXT
        );
        """
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", "0") not in ("1", "true", "TRUE", "XXyesXX", "YES"):
        conn.close()


def x__ensure_table__mutmut_20(db_path: Path) -> None:
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS app_log(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts REAL NOT NULL,
            level TEXT,
            message TEXT,
            meta TEXT
        );
        """
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", "0") not in ("1", "true", "TRUE", "YES", "YES"):
        conn.close()


def x__ensure_table__mutmut_21(db_path: Path) -> None:
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS app_log(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts REAL NOT NULL,
            level TEXT,
            message TEXT,
            meta TEXT
        );
        """
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", "0") not in ("1", "true", "TRUE", "yes", "XXYESXX"):
        conn.close()


def x__ensure_table__mutmut_22(db_path: Path) -> None:
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS app_log(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts REAL NOT NULL,
            level TEXT,
            message TEXT,
            meta TEXT
        );
        """
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", "0") not in ("1", "true", "TRUE", "yes", "yes"):
        conn.close()

x__ensure_table__mutmut_mutants : ClassVar[MutantDict] = {
'x__ensure_table__mutmut_1': x__ensure_table__mutmut_1, 
    'x__ensure_table__mutmut_2': x__ensure_table__mutmut_2, 
    'x__ensure_table__mutmut_3': x__ensure_table__mutmut_3, 
    'x__ensure_table__mutmut_4': x__ensure_table__mutmut_4, 
    'x__ensure_table__mutmut_5': x__ensure_table__mutmut_5, 
    'x__ensure_table__mutmut_6': x__ensure_table__mutmut_6, 
    'x__ensure_table__mutmut_7': x__ensure_table__mutmut_7, 
    'x__ensure_table__mutmut_8': x__ensure_table__mutmut_8, 
    'x__ensure_table__mutmut_9': x__ensure_table__mutmut_9, 
    'x__ensure_table__mutmut_10': x__ensure_table__mutmut_10, 
    'x__ensure_table__mutmut_11': x__ensure_table__mutmut_11, 
    'x__ensure_table__mutmut_12': x__ensure_table__mutmut_12, 
    'x__ensure_table__mutmut_13': x__ensure_table__mutmut_13, 
    'x__ensure_table__mutmut_14': x__ensure_table__mutmut_14, 
    'x__ensure_table__mutmut_15': x__ensure_table__mutmut_15, 
    'x__ensure_table__mutmut_16': x__ensure_table__mutmut_16, 
    'x__ensure_table__mutmut_17': x__ensure_table__mutmut_17, 
    'x__ensure_table__mutmut_18': x__ensure_table__mutmut_18, 
    'x__ensure_table__mutmut_19': x__ensure_table__mutmut_19, 
    'x__ensure_table__mutmut_20': x__ensure_table__mutmut_20, 
    'x__ensure_table__mutmut_21': x__ensure_table__mutmut_21, 
    'x__ensure_table__mutmut_22': x__ensure_table__mutmut_22
}

def _ensure_table(*args, **kwargs):
    result = _mutmut_trampoline(x__ensure_table__mutmut_orig, x__ensure_table__mutmut_mutants, args, kwargs)
    return result 

_ensure_table.__signature__ = _mutmut_signature(x__ensure_table__mutmut_orig)
x__ensure_table__mutmut_orig.__name__ = 'x__ensure_table'


def x_log_event__mutmut_orig(
    level: str,
    message: str,
    meta: str | None = None,
    db_path: Path | None = None,
) -> Path:
    db = _resolve_path(db_path)
    _ensure_table(db)
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO app_log (ts, level, message, meta) VALUES (?, ?, ?, ?)",
        (time.time(), level, message, meta),
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", "0") not in ("1", "true", "TRUE", "yes", "YES"):
        conn.close()
    return db


def x_log_event__mutmut_1(
    level: str,
    message: str,
    meta: str | None = None,
    db_path: Path | None = None,
) -> Path:
    db = None
    _ensure_table(db)
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO app_log (ts, level, message, meta) VALUES (?, ?, ?, ?)",
        (time.time(), level, message, meta),
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", "0") not in ("1", "true", "TRUE", "yes", "YES"):
        conn.close()
    return db


def x_log_event__mutmut_2(
    level: str,
    message: str,
    meta: str | None = None,
    db_path: Path | None = None,
) -> Path:
    db = _resolve_path(None)
    _ensure_table(db)
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO app_log (ts, level, message, meta) VALUES (?, ?, ?, ?)",
        (time.time(), level, message, meta),
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", "0") not in ("1", "true", "TRUE", "yes", "YES"):
        conn.close()
    return db


def x_log_event__mutmut_3(
    level: str,
    message: str,
    meta: str | None = None,
    db_path: Path | None = None,
) -> Path:
    db = _resolve_path(db_path)
    _ensure_table(None)
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO app_log (ts, level, message, meta) VALUES (?, ?, ?, ?)",
        (time.time(), level, message, meta),
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", "0") not in ("1", "true", "TRUE", "yes", "YES"):
        conn.close()
    return db


def x_log_event__mutmut_4(
    level: str,
    message: str,
    meta: str | None = None,
    db_path: Path | None = None,
) -> Path:
    db = _resolve_path(db_path)
    _ensure_table(db)
    conn = None
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO app_log (ts, level, message, meta) VALUES (?, ?, ?, ?)",
        (time.time(), level, message, meta),
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", "0") not in ("1", "true", "TRUE", "yes", "YES"):
        conn.close()
    return db


def x_log_event__mutmut_5(
    level: str,
    message: str,
    meta: str | None = None,
    db_path: Path | None = None,
) -> Path:
    db = _resolve_path(db_path)
    _ensure_table(db)
    conn = sqlite3.connect(None)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO app_log (ts, level, message, meta) VALUES (?, ?, ?, ?)",
        (time.time(), level, message, meta),
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", "0") not in ("1", "true", "TRUE", "yes", "YES"):
        conn.close()
    return db


def x_log_event__mutmut_6(
    level: str,
    message: str,
    meta: str | None = None,
    db_path: Path | None = None,
) -> Path:
    db = _resolve_path(db_path)
    _ensure_table(db)
    conn = sqlite3.connect(str(None))
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO app_log (ts, level, message, meta) VALUES (?, ?, ?, ?)",
        (time.time(), level, message, meta),
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", "0") not in ("1", "true", "TRUE", "yes", "YES"):
        conn.close()
    return db


def x_log_event__mutmut_7(
    level: str,
    message: str,
    meta: str | None = None,
    db_path: Path | None = None,
) -> Path:
    db = _resolve_path(db_path)
    _ensure_table(db)
    conn = sqlite3.connect(str(db))
    cur = None
    cur.execute(
        "INSERT INTO app_log (ts, level, message, meta) VALUES (?, ?, ?, ?)",
        (time.time(), level, message, meta),
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", "0") not in ("1", "true", "TRUE", "yes", "YES"):
        conn.close()
    return db


def x_log_event__mutmut_8(
    level: str,
    message: str,
    meta: str | None = None,
    db_path: Path | None = None,
) -> Path:
    db = _resolve_path(db_path)
    _ensure_table(db)
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    cur.execute(
        None,
        (time.time(), level, message, meta),
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", "0") not in ("1", "true", "TRUE", "yes", "YES"):
        conn.close()
    return db


def x_log_event__mutmut_9(
    level: str,
    message: str,
    meta: str | None = None,
    db_path: Path | None = None,
) -> Path:
    db = _resolve_path(db_path)
    _ensure_table(db)
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO app_log (ts, level, message, meta) VALUES (?, ?, ?, ?)",
        None,
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", "0") not in ("1", "true", "TRUE", "yes", "YES"):
        conn.close()
    return db


def x_log_event__mutmut_10(
    level: str,
    message: str,
    meta: str | None = None,
    db_path: Path | None = None,
) -> Path:
    db = _resolve_path(db_path)
    _ensure_table(db)
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    cur.execute(
        (time.time(), level, message, meta),
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", "0") not in ("1", "true", "TRUE", "yes", "YES"):
        conn.close()
    return db


def x_log_event__mutmut_11(
    level: str,
    message: str,
    meta: str | None = None,
    db_path: Path | None = None,
) -> Path:
    db = _resolve_path(db_path)
    _ensure_table(db)
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO app_log (ts, level, message, meta) VALUES (?, ?, ?, ?)",
        )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", "0") not in ("1", "true", "TRUE", "yes", "YES"):
        conn.close()
    return db


def x_log_event__mutmut_12(
    level: str,
    message: str,
    meta: str | None = None,
    db_path: Path | None = None,
) -> Path:
    db = _resolve_path(db_path)
    _ensure_table(db)
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    cur.execute(
        "XXINSERT INTO app_log (ts, level, message, meta) VALUES (?, ?, ?, ?)XX",
        (time.time(), level, message, meta),
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", "0") not in ("1", "true", "TRUE", "yes", "YES"):
        conn.close()
    return db


def x_log_event__mutmut_13(
    level: str,
    message: str,
    meta: str | None = None,
    db_path: Path | None = None,
) -> Path:
    db = _resolve_path(db_path)
    _ensure_table(db)
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    cur.execute(
        "insert into app_log (ts, level, message, meta) values (?, ?, ?, ?)",
        (time.time(), level, message, meta),
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", "0") not in ("1", "true", "TRUE", "yes", "YES"):
        conn.close()
    return db


def x_log_event__mutmut_14(
    level: str,
    message: str,
    meta: str | None = None,
    db_path: Path | None = None,
) -> Path:
    db = _resolve_path(db_path)
    _ensure_table(db)
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO APP_LOG (TS, LEVEL, MESSAGE, META) VALUES (?, ?, ?, ?)",
        (time.time(), level, message, meta),
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", "0") not in ("1", "true", "TRUE", "yes", "YES"):
        conn.close()
    return db


def x_log_event__mutmut_15(
    level: str,
    message: str,
    meta: str | None = None,
    db_path: Path | None = None,
) -> Path:
    db = _resolve_path(db_path)
    _ensure_table(db)
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO app_log (ts, level, message, meta) VALUES (?, ?, ?, ?)",
        (time.time(), level, message, meta),
    )
    conn.commit()
    cur.close()
    if os.getenv(None, "0") not in ("1", "true", "TRUE", "yes", "YES"):
        conn.close()
    return db


def x_log_event__mutmut_16(
    level: str,
    message: str,
    meta: str | None = None,
    db_path: Path | None = None,
) -> Path:
    db = _resolve_path(db_path)
    _ensure_table(db)
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO app_log (ts, level, message, meta) VALUES (?, ?, ?, ?)",
        (time.time(), level, message, meta),
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", None) not in ("1", "true", "TRUE", "yes", "YES"):
        conn.close()
    return db


def x_log_event__mutmut_17(
    level: str,
    message: str,
    meta: str | None = None,
    db_path: Path | None = None,
) -> Path:
    db = _resolve_path(db_path)
    _ensure_table(db)
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO app_log (ts, level, message, meta) VALUES (?, ?, ?, ?)",
        (time.time(), level, message, meta),
    )
    conn.commit()
    cur.close()
    if os.getenv("0") not in ("1", "true", "TRUE", "yes", "YES"):
        conn.close()
    return db


def x_log_event__mutmut_18(
    level: str,
    message: str,
    meta: str | None = None,
    db_path: Path | None = None,
) -> Path:
    db = _resolve_path(db_path)
    _ensure_table(db)
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO app_log (ts, level, message, meta) VALUES (?, ?, ?, ?)",
        (time.time(), level, message, meta),
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", ) not in ("1", "true", "TRUE", "yes", "YES"):
        conn.close()
    return db


def x_log_event__mutmut_19(
    level: str,
    message: str,
    meta: str | None = None,
    db_path: Path | None = None,
) -> Path:
    db = _resolve_path(db_path)
    _ensure_table(db)
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO app_log (ts, level, message, meta) VALUES (?, ?, ?, ?)",
        (time.time(), level, message, meta),
    )
    conn.commit()
    cur.close()
    if os.getenv("XXCODEX_SQLITE_POOLXX", "0") not in ("1", "true", "TRUE", "yes", "YES"):
        conn.close()
    return db


def x_log_event__mutmut_20(
    level: str,
    message: str,
    meta: str | None = None,
    db_path: Path | None = None,
) -> Path:
    db = _resolve_path(db_path)
    _ensure_table(db)
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO app_log (ts, level, message, meta) VALUES (?, ?, ?, ?)",
        (time.time(), level, message, meta),
    )
    conn.commit()
    cur.close()
    if os.getenv("codex_sqlite_pool", "0") not in ("1", "true", "TRUE", "yes", "YES"):
        conn.close()
    return db


def x_log_event__mutmut_21(
    level: str,
    message: str,
    meta: str | None = None,
    db_path: Path | None = None,
) -> Path:
    db = _resolve_path(db_path)
    _ensure_table(db)
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO app_log (ts, level, message, meta) VALUES (?, ?, ?, ?)",
        (time.time(), level, message, meta),
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", "XX0XX") not in ("1", "true", "TRUE", "yes", "YES"):
        conn.close()
    return db


def x_log_event__mutmut_22(
    level: str,
    message: str,
    meta: str | None = None,
    db_path: Path | None = None,
) -> Path:
    db = _resolve_path(db_path)
    _ensure_table(db)
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO app_log (ts, level, message, meta) VALUES (?, ?, ?, ?)",
        (time.time(), level, message, meta),
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", "0") in ("1", "true", "TRUE", "yes", "YES"):
        conn.close()
    return db


def x_log_event__mutmut_23(
    level: str,
    message: str,
    meta: str | None = None,
    db_path: Path | None = None,
) -> Path:
    db = _resolve_path(db_path)
    _ensure_table(db)
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO app_log (ts, level, message, meta) VALUES (?, ?, ?, ?)",
        (time.time(), level, message, meta),
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", "0") not in ("XX1XX", "true", "TRUE", "yes", "YES"):
        conn.close()
    return db


def x_log_event__mutmut_24(
    level: str,
    message: str,
    meta: str | None = None,
    db_path: Path | None = None,
) -> Path:
    db = _resolve_path(db_path)
    _ensure_table(db)
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO app_log (ts, level, message, meta) VALUES (?, ?, ?, ?)",
        (time.time(), level, message, meta),
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", "0") not in ("1", "XXtrueXX", "TRUE", "yes", "YES"):
        conn.close()
    return db


def x_log_event__mutmut_25(
    level: str,
    message: str,
    meta: str | None = None,
    db_path: Path | None = None,
) -> Path:
    db = _resolve_path(db_path)
    _ensure_table(db)
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO app_log (ts, level, message, meta) VALUES (?, ?, ?, ?)",
        (time.time(), level, message, meta),
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", "0") not in ("1", "TRUE", "TRUE", "yes", "YES"):
        conn.close()
    return db


def x_log_event__mutmut_26(
    level: str,
    message: str,
    meta: str | None = None,
    db_path: Path | None = None,
) -> Path:
    db = _resolve_path(db_path)
    _ensure_table(db)
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO app_log (ts, level, message, meta) VALUES (?, ?, ?, ?)",
        (time.time(), level, message, meta),
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", "0") not in ("1", "true", "XXTRUEXX", "yes", "YES"):
        conn.close()
    return db


def x_log_event__mutmut_27(
    level: str,
    message: str,
    meta: str | None = None,
    db_path: Path | None = None,
) -> Path:
    db = _resolve_path(db_path)
    _ensure_table(db)
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO app_log (ts, level, message, meta) VALUES (?, ?, ?, ?)",
        (time.time(), level, message, meta),
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", "0") not in ("1", "true", "true", "yes", "YES"):
        conn.close()
    return db


def x_log_event__mutmut_28(
    level: str,
    message: str,
    meta: str | None = None,
    db_path: Path | None = None,
) -> Path:
    db = _resolve_path(db_path)
    _ensure_table(db)
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO app_log (ts, level, message, meta) VALUES (?, ?, ?, ?)",
        (time.time(), level, message, meta),
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", "0") not in ("1", "true", "TRUE", "XXyesXX", "YES"):
        conn.close()
    return db


def x_log_event__mutmut_29(
    level: str,
    message: str,
    meta: str | None = None,
    db_path: Path | None = None,
) -> Path:
    db = _resolve_path(db_path)
    _ensure_table(db)
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO app_log (ts, level, message, meta) VALUES (?, ?, ?, ?)",
        (time.time(), level, message, meta),
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", "0") not in ("1", "true", "TRUE", "YES", "YES"):
        conn.close()
    return db


def x_log_event__mutmut_30(
    level: str,
    message: str,
    meta: str | None = None,
    db_path: Path | None = None,
) -> Path:
    db = _resolve_path(db_path)
    _ensure_table(db)
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO app_log (ts, level, message, meta) VALUES (?, ?, ?, ?)",
        (time.time(), level, message, meta),
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", "0") not in ("1", "true", "TRUE", "yes", "XXYESXX"):
        conn.close()
    return db


def x_log_event__mutmut_31(
    level: str,
    message: str,
    meta: str | None = None,
    db_path: Path | None = None,
) -> Path:
    db = _resolve_path(db_path)
    _ensure_table(db)
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO app_log (ts, level, message, meta) VALUES (?, ?, ?, ?)",
        (time.time(), level, message, meta),
    )
    conn.commit()
    cur.close()
    if os.getenv("CODEX_SQLITE_POOL", "0") not in ("1", "true", "TRUE", "yes", "yes"):
        conn.close()
    return db

x_log_event__mutmut_mutants : ClassVar[MutantDict] = {
'x_log_event__mutmut_1': x_log_event__mutmut_1, 
    'x_log_event__mutmut_2': x_log_event__mutmut_2, 
    'x_log_event__mutmut_3': x_log_event__mutmut_3, 
    'x_log_event__mutmut_4': x_log_event__mutmut_4, 
    'x_log_event__mutmut_5': x_log_event__mutmut_5, 
    'x_log_event__mutmut_6': x_log_event__mutmut_6, 
    'x_log_event__mutmut_7': x_log_event__mutmut_7, 
    'x_log_event__mutmut_8': x_log_event__mutmut_8, 
    'x_log_event__mutmut_9': x_log_event__mutmut_9, 
    'x_log_event__mutmut_10': x_log_event__mutmut_10, 
    'x_log_event__mutmut_11': x_log_event__mutmut_11, 
    'x_log_event__mutmut_12': x_log_event__mutmut_12, 
    'x_log_event__mutmut_13': x_log_event__mutmut_13, 
    'x_log_event__mutmut_14': x_log_event__mutmut_14, 
    'x_log_event__mutmut_15': x_log_event__mutmut_15, 
    'x_log_event__mutmut_16': x_log_event__mutmut_16, 
    'x_log_event__mutmut_17': x_log_event__mutmut_17, 
    'x_log_event__mutmut_18': x_log_event__mutmut_18, 
    'x_log_event__mutmut_19': x_log_event__mutmut_19, 
    'x_log_event__mutmut_20': x_log_event__mutmut_20, 
    'x_log_event__mutmut_21': x_log_event__mutmut_21, 
    'x_log_event__mutmut_22': x_log_event__mutmut_22, 
    'x_log_event__mutmut_23': x_log_event__mutmut_23, 
    'x_log_event__mutmut_24': x_log_event__mutmut_24, 
    'x_log_event__mutmut_25': x_log_event__mutmut_25, 
    'x_log_event__mutmut_26': x_log_event__mutmut_26, 
    'x_log_event__mutmut_27': x_log_event__mutmut_27, 
    'x_log_event__mutmut_28': x_log_event__mutmut_28, 
    'x_log_event__mutmut_29': x_log_event__mutmut_29, 
    'x_log_event__mutmut_30': x_log_event__mutmut_30, 
    'x_log_event__mutmut_31': x_log_event__mutmut_31
}

def log_event(*args, **kwargs):
    result = _mutmut_trampoline(x_log_event__mutmut_orig, x_log_event__mutmut_mutants, args, kwargs)
    return result 

log_event.__signature__ = _mutmut_signature(x_log_event__mutmut_orig)
x_log_event__mutmut_orig.__name__ = 'x_log_event'


def x_log_message__mutmut_orig(
    message: str,
    level: str = "INFO",
    meta: str | None = None,
    db_path: Path | None = None,
) -> Path:
    db = _resolve_path(db_path)
    log_event(level=level, message=message, meta=meta, db_path=db)
    return db


def x_log_message__mutmut_1(
    message: str,
    level: str = "XXINFOXX",
    meta: str | None = None,
    db_path: Path | None = None,
) -> Path:
    db = _resolve_path(db_path)
    log_event(level=level, message=message, meta=meta, db_path=db)
    return db


def x_log_message__mutmut_2(
    message: str,
    level: str = "info",
    meta: str | None = None,
    db_path: Path | None = None,
) -> Path:
    db = _resolve_path(db_path)
    log_event(level=level, message=message, meta=meta, db_path=db)
    return db


def x_log_message__mutmut_3(
    message: str,
    level: str = "INFO",
    meta: str | None = None,
    db_path: Path | None = None,
) -> Path:
    db = None
    log_event(level=level, message=message, meta=meta, db_path=db)
    return db


def x_log_message__mutmut_4(
    message: str,
    level: str = "INFO",
    meta: str | None = None,
    db_path: Path | None = None,
) -> Path:
    db = _resolve_path(None)
    log_event(level=level, message=message, meta=meta, db_path=db)
    return db


def x_log_message__mutmut_5(
    message: str,
    level: str = "INFO",
    meta: str | None = None,
    db_path: Path | None = None,
) -> Path:
    db = _resolve_path(db_path)
    log_event(level=None, message=message, meta=meta, db_path=db)
    return db


def x_log_message__mutmut_6(
    message: str,
    level: str = "INFO",
    meta: str | None = None,
    db_path: Path | None = None,
) -> Path:
    db = _resolve_path(db_path)
    log_event(level=level, message=None, meta=meta, db_path=db)
    return db


def x_log_message__mutmut_7(
    message: str,
    level: str = "INFO",
    meta: str | None = None,
    db_path: Path | None = None,
) -> Path:
    db = _resolve_path(db_path)
    log_event(level=level, message=message, meta=None, db_path=db)
    return db


def x_log_message__mutmut_8(
    message: str,
    level: str = "INFO",
    meta: str | None = None,
    db_path: Path | None = None,
) -> Path:
    db = _resolve_path(db_path)
    log_event(level=level, message=message, meta=meta, db_path=None)
    return db


def x_log_message__mutmut_9(
    message: str,
    level: str = "INFO",
    meta: str | None = None,
    db_path: Path | None = None,
) -> Path:
    db = _resolve_path(db_path)
    log_event(message=message, meta=meta, db_path=db)
    return db


def x_log_message__mutmut_10(
    message: str,
    level: str = "INFO",
    meta: str | None = None,
    db_path: Path | None = None,
) -> Path:
    db = _resolve_path(db_path)
    log_event(level=level, meta=meta, db_path=db)
    return db


def x_log_message__mutmut_11(
    message: str,
    level: str = "INFO",
    meta: str | None = None,
    db_path: Path | None = None,
) -> Path:
    db = _resolve_path(db_path)
    log_event(level=level, message=message, db_path=db)
    return db


def x_log_message__mutmut_12(
    message: str,
    level: str = "INFO",
    meta: str | None = None,
    db_path: Path | None = None,
) -> Path:
    db = _resolve_path(db_path)
    log_event(level=level, message=message, meta=meta, )
    return db

x_log_message__mutmut_mutants : ClassVar[MutantDict] = {
'x_log_message__mutmut_1': x_log_message__mutmut_1, 
    'x_log_message__mutmut_2': x_log_message__mutmut_2, 
    'x_log_message__mutmut_3': x_log_message__mutmut_3, 
    'x_log_message__mutmut_4': x_log_message__mutmut_4, 
    'x_log_message__mutmut_5': x_log_message__mutmut_5, 
    'x_log_message__mutmut_6': x_log_message__mutmut_6, 
    'x_log_message__mutmut_7': x_log_message__mutmut_7, 
    'x_log_message__mutmut_8': x_log_message__mutmut_8, 
    'x_log_message__mutmut_9': x_log_message__mutmut_9, 
    'x_log_message__mutmut_10': x_log_message__mutmut_10, 
    'x_log_message__mutmut_11': x_log_message__mutmut_11, 
    'x_log_message__mutmut_12': x_log_message__mutmut_12
}

def log_message(*args, **kwargs):
    result = _mutmut_trampoline(x_log_message__mutmut_orig, x_log_message__mutmut_mutants, args, kwargs)
    return result 

log_message.__signature__ = _mutmut_signature(x_log_message__mutmut_orig)
x_log_message__mutmut_orig.__name__ = 'x_log_message'
