"""Compatibility shim for legacy `codex.archive.dal` imports."""

from __future__ import annotations

import contextlib
import sqlite3
from pathlib import Path

from aries_serpent_core.archive.dal import (
    ArchiveDAL as _CoreArchiveDAL,
    ArtifactRow,
    BaseDAL,
    ItemRow,
    MariaDbDAL,
    PostgresDAL,
    SqliteDAL,
    _cursor_row_to_dict,
    _decode_json_field,
    _maybe_bytes,
)


class ArchiveDAL(_CoreArchiveDAL):
    """Compatibility wrapper that works as both a factory and a lightweight instance."""

    def __init__(self, *args, connection_string=None, timeout=None, **kwargs):
        self.connection_string = connection_string
        self.timeout = timeout
        self._delegate = self._build_delegate(connection_string, timeout)
        self._closed = False

    @staticmethod
    def _build_delegate(connection_string=None, timeout=None):
        target = connection_string or "sqlite:///:memory:"
        if target in ("", None):
            target = "sqlite:///:memory:"
        if target.lower() == "dummy":
            target = "sqlite:///:memory:"
        if target.startswith("sqlite://"):
            parsed = target[len("sqlite://") :]
            if parsed in ("", ":memory:") or parsed.startswith("/:memory:"):
                path = ":memory:"
            elif parsed.startswith("/"):
                path = parsed
            else:
                path = parsed
            conn = sqlite3.connect(path, timeout=float(timeout) if timeout is not None else 5.0)
            return SqliteDAL(conn, Path("."))
        conn = sqlite3.connect(":memory:", timeout=float(timeout) if timeout is not None else 5.0)
        return SqliteDAL(conn, Path("."))

    @staticmethod
    def from_env():
        return _CoreArchiveDAL.from_env()

    def transaction(self):
        return self._delegate.txn()

    def execute(self, sql, *args, **kwargs):
        return self._delegate.conn.execute(sql, *args, **kwargs)

    def close(self):
        if getattr(self, "_closed", False):
            return
        conn = getattr(self._delegate, "conn", None)
        if conn is not None:
            with contextlib.suppress(Exception):
                conn.close()
        self._closed = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False

    def __del__(self):
        with contextlib.suppress(Exception):
            self.close()

    def __getattr__(self, name):
        return getattr(self._delegate, name)


__all__ = [
    "ArchiveDAL",
    "ArtifactRow",
    "BaseDAL",
    "ItemRow",
    "MariaDbDAL",
    "PostgresDAL",
    "SqliteDAL",
    "_cursor_row_to_dict",
    "_decode_json_field",
    "_maybe_bytes",
]
