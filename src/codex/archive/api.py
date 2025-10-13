from __future__ import annotations

import hashlib
import sqlite3
import uuid
from pathlib import Path
from threading import Lock
from typing import Any
from urllib.parse import unquote, urlparse

try:  # pragma: no cover - optional dependency
    from sqlalchemy import (
        Column,
        Integer,
        LargeBinary,
        MetaData,
        String,
        Table,
        Text,
        create_engine,
        select,
    )
    from sqlalchemy.engine import Engine
    from sqlalchemy.engine.url import make_url

    SQLALCHEMY_AVAILABLE = True
except Exception:  # pragma: no cover - runtime fallback
    SQLALCHEMY_AVAILABLE = False
    Engine = Any  # type: ignore[assignment]

from .util import append_evidence, get_archive_table, get_archive_url, utcnow_iso

if SQLALCHEMY_AVAILABLE:
    _METADATA = MetaData()
    _TABLE: Table | None = None
    _ENGINE: Engine | None = None
else:
    _METADATA = None
    _TABLE = None
    _ENGINE = None

_SQLITE_CONN: sqlite3.Connection | None = None
_SQLITE_LOCK = Lock()
_SQLITE_SCHEMA_INIT = False


def _quote_identifier(name: str) -> str:
    escaped = name.replace('"', '""')
    return f'"{escaped}"'


def _parse_sqlite_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme != "sqlite":
        raise RuntimeError(
            "SQLAlchemy is required for non-SQLite archive backends; "
            "install sqlalchemy or adjust CODEX_ARCHIVE_URL."
        )
    path = parsed.path or ""
    if parsed.netloc:
        path = f"{parsed.netloc}{path}"
    path = unquote(path)
    if path in {"", "/"}:
        return ":memory:"
    if path.startswith("//"):
        path = path[1:]
    if path.startswith("/"):
        path = path[1:] if not path.startswith("//") else path
    if path.startswith("./"):
        path = path[2:]
    return path or ":memory:"


def _ensure_sqlite_connection() -> sqlite3.Connection:
    global _SQLITE_CONN
    if _SQLITE_CONN is not None:
        return _SQLITE_CONN
    url = get_archive_url()
    db_path = _parse_sqlite_url(url)
    if db_path != ":memory:":
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    _SQLITE_CONN = conn
    return conn


def _ensure_sqlite_schema(conn: sqlite3.Connection) -> None:
    global _SQLITE_SCHEMA_INIT
    if _SQLITE_SCHEMA_INIT:
        return
    table = _quote_identifier(get_archive_table())
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {table} (
            tombstone TEXT PRIMARY KEY,
            repo TEXT NOT NULL,
            path TEXT NOT NULL,
            archived_by TEXT NOT NULL,
            reason TEXT NOT NULL,
            commit_sha TEXT NOT NULL,
            mime TEXT,
            lang TEXT,
            sha256 TEXT NOT NULL,
            size_bytes INTEGER NOT NULL,
            stored_at TEXT NOT NULL,
            bytes BLOB NOT NULL
        )
        """
    )
    _SQLITE_SCHEMA_INIT = True


def _ensure_sqlite_dirs(url: str) -> dict[str, Any]:
    connect_args: dict[str, Any] = {}
    if not SQLALCHEMY_AVAILABLE:
        return connect_args
    parsed = make_url(url)
    if parsed.drivername.startswith("sqlite"):
        database = parsed.database or ""
        if database not in ("", ":memory:"):
            db_path = Path(database)
            if not db_path.is_absolute():
                db_path = Path(database)
            if db_path.suffix:
                db_path.parent.mkdir(parents=True, exist_ok=True)
            else:
                db_path.mkdir(parents=True, exist_ok=True)
        connect_args["check_same_thread"] = False
    return connect_args


def _get_table() -> Table:
    if not SQLALCHEMY_AVAILABLE:
        raise RuntimeError("SQLAlchemy backend not available")
    global _TABLE
    if _TABLE is None:
        name = get_archive_table()
        _TABLE = Table(
            name,
            _METADATA,
            Column("tombstone", String(64), primary_key=True),
            Column("repo", String(255), nullable=False),
            Column("path", Text, nullable=False),
            Column("archived_by", String(255), nullable=False),
            Column("reason", String(255), nullable=False),
            Column("commit_sha", String(64), nullable=False),
            Column("mime", String(127)),
            Column("lang", String(64)),
            Column("sha256", String(64), nullable=False),
            Column("size_bytes", Integer, nullable=False),
            Column("stored_at", String(64), nullable=False),
            Column("bytes", LargeBinary, nullable=False),
        )
    return _TABLE


def _get_engine() -> Engine:
    if not SQLALCHEMY_AVAILABLE:
        raise RuntimeError("SQLAlchemy backend not available")
    global _ENGINE
    if _ENGINE is None:
        url = get_archive_url()
        connect_args = _ensure_sqlite_dirs(url)
        _ENGINE = create_engine(url, future=True, connect_args=connect_args)
        table = _get_table()
        _METADATA.create_all(_ENGINE, tables=[table])
    return _ENGINE


def _store_sqlalchemy(record: dict[str, Any]) -> None:
    engine = _get_engine()
    table = _get_table()
    with engine.begin() as conn:
        conn.execute(table.insert().values(record))


def _restore_sqlalchemy(tombstone: str) -> dict[str, Any]:
    engine = _get_engine()
    table = _get_table()
    with engine.connect() as conn:
        row = conn.execute(select(table).where(table.c.tombstone == tombstone)).mappings().first()
    if not row:
        raise KeyError(f"tombstone not found: {tombstone}")
    data_bytes = row["bytes"]
    if isinstance(data_bytes, memoryview):  # sqlite returns memoryview
        data_bytes = data_bytes.tobytes()
    return dict(row, bytes=data_bytes)


# ruff: noqa: S608
def _store_sqlite(record: dict[str, Any]) -> None:
    conn = _ensure_sqlite_connection()
    with _SQLITE_LOCK:
        _ensure_sqlite_schema(conn)
        table = _quote_identifier(get_archive_table())
        sql = (
            f"INSERT INTO {table} ("
            "tombstone, repo, path, archived_by, reason, commit_sha, mime, lang, "
            "sha256, size_bytes, stored_at, bytes"
            ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        )
        conn.execute(
            sql,
            (
                record["tombstone"],
                record["repo"],
                record["path"],
                record["archived_by"],
                record["reason"],
                record["commit_sha"],
                record.get("mime"),
                record.get("lang"),
                record["sha256"],
                record["size_bytes"],
                record["stored_at"],
                record["bytes"],
            ),
        )
        conn.commit()


# ruff: noqa: S608
def _restore_sqlite(tombstone: str) -> dict[str, Any]:
    conn = _ensure_sqlite_connection()
    with _SQLITE_LOCK:
        _ensure_sqlite_schema(conn)
        table = _quote_identifier(get_archive_table())
        sql = (
            "SELECT tombstone, repo, path, archived_by, reason, commit_sha, mime, "
            "lang, sha256, size_bytes, stored_at, bytes FROM "
            f"{table} WHERE tombstone = ?"
        )
        cur = conn.execute(sql, (tombstone,))
        row = cur.fetchone()
    if row is None:
        raise KeyError(f"tombstone not found: {tombstone}")
    return dict(row)


def store(
    *,
    repo: str,
    path: str,
    by: str,
    reason: str,
    commit_sha: str,
    bytes_in: bytes,
    mime: str | None = None,
    lang: str | None = None,
) -> dict[str, Any]:
    tombstone = str(uuid.uuid4())
    sha256 = hashlib.sha256(bytes_in).hexdigest()
    stored_at = utcnow_iso()
    record = {
        "tombstone": tombstone,
        "repo": repo,
        "path": path,
        "archived_by": by,
        "reason": reason,
        "commit_sha": commit_sha,
        "mime": mime,
        "lang": lang,
        "sha256": sha256,
        "size_bytes": len(bytes_in),
        "stored_at": stored_at,
        "bytes": bytes_in,
    }
    if SQLALCHEMY_AVAILABLE:
        _store_sqlalchemy(record)
    else:
        _store_sqlite(record)
    append_evidence(
        {
            "event": "archive.store",
            "repo": repo,
            "path": path,
            "tombstone": tombstone,
            "sha256": sha256,
            "reason": reason,
            "by": by,
            "commit": commit_sha,
            "mime": mime,
            "lang": lang,
            "size": len(bytes_in),
            "stored_at": stored_at,
        }
    )
    return {
        "tombstone": tombstone,
        "sha256": sha256,
        "stored_at": stored_at,
        "path": path,
        "repo": repo,
    }


def restore(tombstone: str) -> dict[str, Any]:
    row = _restore_sqlalchemy(tombstone) if SQLALCHEMY_AVAILABLE else _restore_sqlite(tombstone)
    data_bytes = row["bytes"]
    if isinstance(data_bytes, memoryview):
        data_bytes = data_bytes.tobytes()
    return {
        "tombstone": row["tombstone"],
        "path": row["path"],
        "repo": row["repo"],
        "bytes": data_bytes,
        "sha256": row["sha256"],
        "mime": row.get("mime"),
        "lang": row.get("lang"),
        "stored_at": row["stored_at"],
    }
