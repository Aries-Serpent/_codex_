from __future__ import annotations

import contextlib
import json
import os
import sqlite3
import uuid
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast
from urllib.parse import parse_qsl, urlparse


@dataclass
class ArtifactRow:
    id: str
    content_sha256: str
    size_bytes: int
    compression: str
    mime_type: str
    storage_driver: str
    blob_bytes: bytes | None
    object_url: str | None


@dataclass
class ItemRow:
    id: str
    repo: str
    path: str
    commit_sha: str
    language: str
    kind: str
    reason: str
    artifact_id: str
    metadata: dict[str, Any]
    tombstone_id: str


def _cursor_row_to_dict(cursor: Any, row: Any) -> dict[str, Any]:
    description = getattr(cursor, "description", None) or []
    columns: list[str] = []
    for desc in description:
        name = getattr(desc, "name", None)
        if name is None:
            try:
                name = desc[0]
            except Exception:  # pragma: no cover - defensive
                name = str(desc)
        columns.append(name)
    return dict(zip(columns, row, strict=False))


def _decode_json_field(raw: Any) -> dict[str, Any]:
    if raw is None:
        return {}
    if isinstance(raw, memoryview):  # pragma: no cover - driver specific
        raw = raw.tobytes()
    if isinstance(raw, bytes | bytearray):
        try:
            raw = raw.decode("utf-8")
        except UnicodeDecodeError:  # pragma: no cover - defensive
            return {}
    if isinstance(raw, str):
        with contextlib.suppress(json.JSONDecodeError):
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                return parsed
        return {}
    if isinstance(raw, dict):
        return raw
    return {}


def _maybe_bytes(raw: Any) -> bytes | None:
    if raw is None:
        return None
    if isinstance(raw, memoryview):  # pragma: no cover - driver specific
        return raw.tobytes()
    if isinstance(raw, bytearray):
        return bytes(raw)
    return cast(bytes | None, raw)


class ArchiveDAL:
    """Factory for backend-specific DALs."""

    @staticmethod
    def from_env() -> BaseDAL:
        backend = os.getenv("CODEX_ARCHIVE_BACKEND", "sqlite").strip().lower()
        url = os.getenv("CODEX_ARCHIVE_URL", "sqlite:///./.codex/archive.sqlite")
        if backend == "sqlite":
            return SqliteDAL.from_url(url)
        if backend == "postgres":
            return PostgresDAL.from_url(url)
        if backend == "mariadb":
            return MariaDbDAL.from_url(url)
        raise ValueError(f"Unsupported CODEX_ARCHIVE_BACKEND: {backend}")


class BaseDAL:
    def txn(self) -> contextlib.AbstractContextManager[None]:
        raise NotImplementedError

    def ensure_schema(self) -> None:
        raise NotImplementedError

    def insert_referent(self, *, item_id: str, ref_type: str, ref_value: str) -> None:
        raise NotImplementedError

    @staticmethod
    def validate_identifier(name: str, allowed: Iterable[str]) -> str:
        allowed_set = set(allowed)
        if name not in allowed_set:
            raise ValueError(f"identifier not allowed: {name}")
        return name

    def recent_items(self, limit: int) -> list[dict[str, Any]]:
        raise NotImplementedError

    def summary(self) -> dict[str, int]:
        raise NotImplementedError

    def ensure_artifact(
        self,
        *,
        sha: str,
        size: int,
        mime: str,
        blob: bytes,
        compression: str = "zlib",
        storage_driver: str = "db",
        object_url: str | None = None,
    ) -> dict[str, Any]:
        raise NotImplementedError

    def insert_item(
        self,
        *,
        repo: str,
        path: str,
        commit_sha: str,
        language: str,
        reason: str,
        artifact_id: str,
        tombstone_id: str,
        kind: str = "code",
        metadata: dict[str, Any] | None = None,
        archived_by: str = "codex",
    ) -> dict[str, Any]:
        raise NotImplementedError

    def insert_event(
        self,
        *,
        item_id: str,
        action: str,
        actor: str,
        context: dict[str, Any] | None = None,
    ) -> None:
        raise NotImplementedError

    def fetch_by_tombstone(self, tombstone_id: str) -> tuple[ItemRow, ArtifactRow]:
        raise NotImplementedError

    # -------- Release persistence (optional) --------
    def create_release_meta(
        self,
        *,
        release_id: str,
        version: str,
        created_at: str,
        actor: str,
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        """Insert a row into release_meta and return the persisted row."""

        raise NotImplementedError

    def add_release_component(
        self,
        *,
        release_meta_id: str,
        item_id: str | None,
        tombstone: str,
        dest_path: str,
        mode: str,
        template_vars: dict[str, Any],
    ) -> dict[str, Any]:
        """Insert a row into release_component for this release."""

        raise NotImplementedError

    def get_release_meta_by_release_id(self, *, release_id: str) -> dict[str, Any] | None:
        """Lookup release_meta by its human release_id."""

        raise NotImplementedError


class SqliteDAL(BaseDAL):
    _ALLOWED_TABLES = frozenset(
        {
            "artifact",
            "item",
            "event",
            "tag",
            "referent",
            "release_meta",
            "release_component",
        }
    )

    def __init__(self, conn: sqlite3.Connection, db_root: Path):
        self.conn = conn
        self.db_root = db_root
        self.conn.row_factory = sqlite3.Row

    @staticmethod
    def from_url(url: str) -> SqliteDAL:
        if not url.startswith("sqlite:///"):
            raise ValueError("SQLite URL must start with sqlite:///")
        path = url[len("sqlite:///") :]
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(p.as_posix())
        dal = SqliteDAL(conn, p.parent)
        dal.ensure_schema()
        return dal

    def txn(self) -> contextlib.AbstractContextManager[None]:
        @contextlib.contextmanager
        def _ctx() -> Iterator[None]:
            try:
                yield
                self.conn.commit()
            except Exception:  # pragma: no cover - passthrough
                self.conn.rollback()
                raise

        return _ctx()

    def _load_migration_sql(self) -> str:
        here = Path(__file__).resolve()
        root = here.parents[3]
        preferred = root / "db" / "migrations" / "sqlite" / "001_init_archive.sql"
        if preferred.exists():
            return preferred.read_text(encoding="utf-8")
        mig = root / "db" / "migrations" / "sqlite" / "001_init.sql"
        if mig.exists():
            return mig.read_text(encoding="utf-8")
        return """
        PRAGMA journal_mode=WAL;
        CREATE TABLE IF NOT EXISTS artifact (
          id             TEXT PRIMARY KEY,
          content_sha256 TEXT NOT NULL UNIQUE,
          size_bytes     INTEGER NOT NULL,
          compression    TEXT NOT NULL DEFAULT 'zlib',
          mime_type      TEXT NOT NULL,
          storage_driver TEXT NOT NULL DEFAULT 'db',
          blob_bytes     BLOB,
          object_url     TEXT,
          created_at     TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS item (
          id             TEXT PRIMARY KEY,
          repo           TEXT NOT NULL,
          path           TEXT NOT NULL,
          commit_sha     TEXT NOT NULL,
          language       TEXT,
          kind           TEXT NOT NULL,
          reason         TEXT NOT NULL,
          artifact_id    TEXT NOT NULL REFERENCES artifact(id),
          metadata       TEXT NOT NULL DEFAULT '{}',
          archived_by    TEXT NOT NULL,
          archived_at    TEXT NOT NULL DEFAULT (datetime('now')),
          tombstone_id   TEXT NOT NULL UNIQUE,
          legal_hold     INTEGER NOT NULL DEFAULT 0,
          delete_after   TEXT,
          restored_at    TEXT
        );
        CREATE TABLE IF NOT EXISTS event (
          id         TEXT PRIMARY KEY,
          item_id    TEXT NOT NULL REFERENCES item(id),
          action     TEXT NOT NULL,
          actor      TEXT NOT NULL,
          context    TEXT NOT NULL DEFAULT '{}',
          created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS tag (
          item_id TEXT NOT NULL,
          tag     TEXT NOT NULL,
          PRIMARY KEY (item_id, tag)
        );
        CREATE TABLE IF NOT EXISTS referent (
          item_id   TEXT NOT NULL,
          ref_type  TEXT NOT NULL,
          ref_value TEXT NOT NULL,
          PRIMARY KEY (item_id, ref_type, ref_value)
        );
        """

    def ensure_schema(self) -> None:
        sql = self._load_migration_sql()
        with self.txn():
            self.conn.executescript(sql)
        self._ensure_release_tables()

    def _ensure_release_tables(self) -> None:
        with self.txn():
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS release_meta (
                  id TEXT PRIMARY KEY,
                  release_id TEXT NOT NULL UNIQUE,
                  version TEXT NOT NULL,
                  created_at TEXT NOT NULL,
                  actor TEXT NOT NULL,
                  metadata TEXT NOT NULL DEFAULT '{}'
                )
                """
            )
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS release_component (
                  id TEXT PRIMARY KEY,
                  release_id TEXT NOT NULL,
                  item_id TEXT,
                  tombstone TEXT NOT NULL,
                  dest_path TEXT NOT NULL,
                  mode TEXT NOT NULL DEFAULT '0644',
                  template_vars TEXT NOT NULL DEFAULT '{}',
                  FOREIGN KEY(release_id) REFERENCES release_meta(id)
                )
                """
            )
            self.conn.execute(
                "CREATE INDEX IF NOT EXISTS "
                "idx_release_component_release_id ON release_component(release_id)"
            )

    def insert_referent(self, *, item_id: str, ref_type: str, ref_value: str) -> None:
        with self.txn():
            cur = self.conn.execute(
                "SELECT id FROM item WHERE id = ?",
                (item_id,),
            )
            row = cur.fetchone()
            if row is None:
                raise KeyError(f"Item not found: {item_id}")
            item_id = row["id"]
            self.conn.execute(
                "INSERT OR IGNORE INTO referent (item_id, ref_type, ref_value) VALUES (?,?,?)",
                (item_id, ref_type, ref_value),
            )

    def recent_items(self, limit: int) -> list[dict[str, Any]]:
        cur = self.conn.execute(
            """
            SELECT item.tombstone_id,
                   item.repo,
                   item.path,
                   item.archived_at,
                   artifact.content_sha256
            FROM item
            JOIN artifact ON item.artifact_id = artifact.id
            ORDER BY item.archived_at DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows: list[dict[str, Any]] = []
        for row in cur.fetchall():
            rows.append(
                {
                    "tombstone": row["tombstone_id"],
                    "repo": row["repo"],
                    "path": row["path"],
                    "archived_at": row["archived_at"],
                    "sha256": row["content_sha256"],
                }
            )
        return rows

    def summary(self) -> dict[str, int]:
        cur = self.conn.execute(
            """
            SELECT COUNT(*) AS cnt, COALESCE(SUM(artifact.size_bytes), 0) AS total_bytes
            FROM item
            JOIN artifact ON item.artifact_id = artifact.id
            """
        )
        row = cur.fetchone()
        if row is None:
            return {"count": 0, "total_bytes": 0}
        return {
            "count": int(row["cnt"] or 0),
            "total_bytes": int(row["total_bytes"] or 0),
        }

    def ensure_artifact(
        self,
        *,
        sha: str,
        size: int,
        mime: str,
        blob: bytes,
        compression: str = "zlib",
        storage_driver: str = "db",
        object_url: str | None = None,
    ) -> dict[str, Any]:
        with self.txn():
            cur = self.conn.execute(
                (
                    "SELECT id, content_sha256, size_bytes, compression, mime_type, "
                    "storage_driver, blob_bytes, object_url FROM artifact "
                    "WHERE content_sha256 = ?"
                ),
                (sha,),
            )
            row = cur.fetchone()
            if row:
                return dict(row)
            aid = str(uuid.uuid4())
            self.conn.execute(
                (
                    "INSERT INTO artifact (id, content_sha256, size_bytes, compression, "
                    "mime_type, storage_driver, blob_bytes, object_url) "
                    "VALUES (?,?,?,?,?,?,?,?)"
                ),
                (
                    aid,
                    sha,
                    size,
                    compression,
                    mime,
                    storage_driver,
                    blob if storage_driver == "db" else None,
                    object_url,
                ),
            )
            return {
                "id": aid,
                "content_sha256": sha,
                "size_bytes": size,
                "compression": compression,
                "mime_type": mime,
                "storage_driver": storage_driver,
                "blob_bytes": blob if storage_driver == "db" else None,
                "object_url": object_url,
            }

    def insert_item(
        self,
        *,
        repo: str,
        path: str,
        commit_sha: str,
        language: str,
        reason: str,
        artifact_id: str,
        tombstone_id: str,
        kind: str = "code",
        metadata: dict[str, Any] | None = None,
        archived_by: str = "codex",
    ) -> dict[str, Any]:
        iid = str(uuid.uuid4())
        meta_s = json.dumps(metadata or {}, sort_keys=True)
        with self.txn():
            self.conn.execute(
                (
                    "INSERT INTO item (id, repo, path, commit_sha, language, kind, "
                    "reason, artifact_id, metadata, archived_by, tombstone_id) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?,?)"
                ),
                (
                    iid,
                    repo,
                    path,
                    commit_sha,
                    language,
                    kind,
                    reason,
                    artifact_id,
                    meta_s,
                    archived_by,
                    tombstone_id,
                ),
            )
        return {"id": iid, "tombstone_id": tombstone_id}

    def insert_event(
        self,
        *,
        item_id: str,
        action: str,
        actor: str,
        context: dict[str, Any] | None = None,
    ) -> None:
        eid = str(uuid.uuid4())
        ctx = json.dumps(context or {}, sort_keys=True)
        with self.txn():
            self.conn.execute(
                ("INSERT INTO event (id, item_id, action, actor, context) " "VALUES (?,?,?,?,?)"),
                (
                    eid,
                    item_id,
                    action,
                    actor,
                    ctx,
                ),
            )

    def fetch_by_tombstone(self, tombstone_id: str) -> tuple[ItemRow, ArtifactRow]:
        cur = self.conn.execute(
            "SELECT * FROM item WHERE tombstone_id = ?",
            (tombstone_id,),
        )
        it = cur.fetchone()
        if not it:
            raise KeyError(f"Tombstone not found: {tombstone_id}")
        cur = self.conn.execute(
            "SELECT * FROM artifact WHERE id = ?",
            (it["artifact_id"],),
        )
        ar = cur.fetchone()
        if not ar:
            raise KeyError(f"Artifact missing for item {it['id']}")
        item = ItemRow(
            id=it["id"],
            repo=it["repo"],
            path=it["path"],
            commit_sha=it["commit_sha"],
            language=it["language"] or "",
            kind=it["kind"],
            reason=it["reason"],
            artifact_id=it["artifact_id"],
            metadata=json.loads(it["metadata"] or "{}"),
            tombstone_id=it["tombstone_id"],
        )
        art = ArtifactRow(
            id=ar["id"],
            content_sha256=ar["content_sha256"],
            size_bytes=ar["size_bytes"],
            compression=ar["compression"],
            mime_type=ar["mime_type"],
            storage_driver=ar["storage_driver"],
            blob_bytes=ar["blob_bytes"],
            object_url=ar["object_url"],
        )
        return item, art

    # -------- Release persistence (sqlite) --------
    def create_release_meta(
        self,
        *,
        release_id: str,
        version: str,
        created_at: str,
        actor: str,
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        self._ensure_release_tables()
        rid = str(uuid.uuid4())
        payload = json.dumps(metadata or {}, ensure_ascii=False, sort_keys=True)
        with self.txn():
            self.conn.execute(
                (
                    "INSERT INTO release_meta (id, release_id, version, created_at, actor, "
                    "metadata) VALUES (?,?,?,?,?,?)"
                ),
                (rid, release_id, version, created_at, actor, payload),
            )
        return {"id": rid, "release_id": release_id, "version": version}

    def add_release_component(
        self,
        *,
        release_meta_id: str,
        item_id: str | None,
        tombstone: str,
        dest_path: str,
        mode: str,
        template_vars: dict[str, Any],
    ) -> dict[str, Any]:
        self._ensure_release_tables()
        cid = str(uuid.uuid4())
        payload = json.dumps(template_vars or {}, ensure_ascii=False, sort_keys=True)
        with self.txn():
            self.conn.execute(
                (
                    "INSERT INTO release_component (id, release_id, item_id, tombstone, "
                    "dest_path, mode, template_vars) VALUES (?,?,?,?,?,?,?)"
                ),
                (cid, release_meta_id, item_id, tombstone, dest_path, mode, payload),
            )
        return {"id": cid, "release_id": release_meta_id, "tombstone": tombstone}

    def get_release_meta_by_release_id(self, *, release_id: str) -> dict[str, Any] | None:
        self._ensure_release_tables()
        cur = self.conn.execute(
            "SELECT * FROM release_meta WHERE release_id = ?",
            (release_id,),
        )
        row = cur.fetchone()
        if not row:
            return None
        data = dict(row)
        meta_raw = data.get("metadata")
        if isinstance(meta_raw, str):
            with contextlib.suppress(json.JSONDecodeError):
                data["metadata"] = json.loads(meta_raw)
        return data


class PostgresDAL(BaseDAL):
    _ALLOWED_TABLES = frozenset(
        {
            "artifact",
            "item",
            "event",
            "referent",
            "release_meta",
            "release_component",
        }
    )

    def __init__(self, dsn: str):
        self.dsn = dsn
        try:
            import psycopg
        except Exception as e:  # pragma: no cover - import guard
            raise RuntimeError("psycopg (v3) is required for postgres backend") from e
        self.pg = psycopg
        self.conn = self.pg.connect(self.dsn)
        self.ensure_schema()

    def _sql_ident(self, name: str):
        from psycopg import sql  # type: ignore

        self.validate_identifier(name, self._ALLOWED_TABLES)
        return sql.Identifier(name)

    @staticmethod
    def from_url(url: str) -> PostgresDAL:
        return PostgresDAL(url)

    def txn(self) -> contextlib.AbstractContextManager[None]:
        return cast(contextlib.AbstractContextManager[None], self.conn.transaction())

    def ensure_schema(self) -> None:
        here = Path(__file__).resolve()
        root = here.parents[3]
        migrations_dir = root / "db" / "migrations" / "postgres"
        sql_files = sorted(migrations_dir.glob("*.sql"))
        if not sql_files:
            return
        with self.txn():
            cur = self.conn.cursor()
            try:
                for path in sql_files:
                    script = path.read_text(encoding="utf-8")
                    for stmt in script.split(";"):
                        if stmt.strip():
                            cur.execute(stmt)
            finally:
                cur.close()

    def _ensure_pgcrypto(self) -> None:  # pragma: no cover - runtime guard
        cur = self.conn.cursor()
        try:
            cur.execute("SELECT 1 FROM pg_extension WHERE extname='pgcrypto'")
            if not cur.fetchone():
                raise RuntimeError(
                    "Postgres missing extension 'pgcrypto'. Run: "
                    "CREATE EXTENSION IF NOT EXISTS pgcrypto;"
                )
        finally:
            cur.close()

    def ensure_artifact(self, **_: Any) -> dict[str, Any]:  # pragma: no cover - stub
        raise NotImplementedError("Implement postgres artifact ops or use SQLite backend for dev.")

    def insert_item(self, **_: Any) -> dict[str, Any]:  # pragma: no cover - stub
        raise NotImplementedError("Implement postgres item ops or use SQLite backend for dev.")

    def insert_event(self, **_: Any) -> None:  # pragma: no cover - stub
        raise NotImplementedError("Implement postgres event ops or use SQLite backend for dev.")

    def fetch_by_tombstone(self, tombstone_id: str) -> tuple[ItemRow, ArtifactRow]:
        cur = self.conn.cursor()
        try:
            cur.execute("SELECT * FROM item WHERE tombstone_id = %s", (tombstone_id,))
            row = cur.fetchone()
            if not row:
                raise KeyError(f"Tombstone not found: {tombstone_id}")
            item_data = _cursor_row_to_dict(cur, row)
            cur.execute("SELECT * FROM artifact WHERE id = %s", (item_data["artifact_id"],))
            art_row = cur.fetchone()
            if not art_row:
                raise KeyError(f"Artifact missing for item {item_data['id']}")
            art_data = _cursor_row_to_dict(cur, art_row)
        finally:
            cur.close()

        metadata = _decode_json_field(item_data.get("metadata"))
        item = ItemRow(
            id=str(item_data["id"]),
            repo=str(item_data["repo"]),
            path=str(item_data["path"]),
            commit_sha=str(item_data["commit_sha"]),
            language=str(item_data.get("language") or ""),
            kind=str(item_data["kind"]),
            reason=str(item_data["reason"]),
            artifact_id=str(item_data["artifact_id"]),
            metadata=metadata,
            tombstone_id=str(item_data["tombstone_id"]),
        )

        blob_bytes = _maybe_bytes(art_data.get("blob_bytes"))
        artifact = ArtifactRow(
            id=str(art_data["id"]),
            content_sha256=str(art_data["content_sha256"]),
            size_bytes=int(art_data["size_bytes"]),
            compression=str(art_data["compression"]),
            mime_type=str(art_data["mime_type"]),
            storage_driver=str(art_data["storage_driver"]),
            blob_bytes=blob_bytes,
            object_url=(
                str(art_data["object_url"]) if art_data.get("object_url") is not None else None
            ),
        )
        return item, artifact

    def insert_referent(self, *, item_id: str, ref_type: str, ref_value: str) -> None:
        with self.txn():
            cur = self.conn.cursor()
            try:
                cur.execute(
                    "INSERT INTO referent (item_id, ref_type, ref_value) VALUES (%s,%s,%s) "
                    "ON CONFLICT DO NOTHING",
                    (item_id, ref_type, ref_value),
                )
            finally:
                cur.close()

    def recent_items(self, *_: Any, **__: Any) -> list[dict[str, Any]]:  # pragma: no cover - stub
        raise NotImplementedError(
            "Implement postgres recent listing or use SQLite backend for dev."
        )

    def summary(self) -> dict[str, int]:  # pragma: no cover - stub
        raise NotImplementedError("Implement postgres summary or use SQLite backend for dev.")

    def create_release_meta(
        self,
        *,
        release_id: str,
        version: str,
        created_at: str,
        actor: str,
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        payload = json.dumps(metadata or {}, ensure_ascii=False, sort_keys=True)
        self._ensure_pgcrypto()
        with self.txn():
            cur = self.conn.cursor()
            try:
                sql = (
                    "INSERT INTO release_meta "
                    "(release_id, version, created_at, actor, metadata)\n"
                    "VALUES (%s,%s,%s,%s,%s) RETURNING id"
                )
                cur.execute(sql, (release_id, version, created_at, actor, payload))
                row = cur.fetchone()
            finally:
                cur.close()
        if not row:
            raise RuntimeError("Failed to insert release_meta row")
        rid = str(row[0])
        return {"id": rid, "release_id": release_id, "version": version}

    def add_release_component(
        self,
        *,
        release_meta_id: str,
        item_id: str | None,
        tombstone: str,
        dest_path: str,
        mode: str,
        template_vars: dict[str, Any],
    ) -> dict[str, Any]:
        payload = json.dumps(template_vars or {}, ensure_ascii=False, sort_keys=True)
        self._ensure_pgcrypto()
        with self.txn():
            cur = self.conn.cursor()
            try:
                sql = (
                    "INSERT INTO release_component "
                    "(release_id, item_id, tombstone, dest_path, mode, template_vars)\n"
                    "VALUES (%s,%s,%s,%s,%s,%s) RETURNING id"
                )
                cur.execute(
                    sql,
                    (release_meta_id, item_id, tombstone, dest_path, mode, payload),
                )
                row = cur.fetchone()
            finally:
                cur.close()
        if not row:
            raise RuntimeError("Failed to insert release_component row")
        cid = str(row[0])
        return {"id": cid, "release_id": release_meta_id, "tombstone": tombstone}

    def get_release_meta_by_release_id(self, *, release_id: str) -> dict[str, Any] | None:
        cur = self.conn.cursor()
        try:
            cur.execute("SELECT * FROM release_meta WHERE release_id = %s LIMIT 1", (release_id,))
            row = cur.fetchone()
            if not row:
                return None
            data = _cursor_row_to_dict(cur, row)
        finally:
            cur.close()
        data["id"] = str(data["id"])
        data["release_id"] = str(data["release_id"])
        data["metadata"] = _decode_json_field(data.get("metadata"))
        return data


class MariaDbDAL(BaseDAL):
    def __init__(self, dsn: str):
        self.dsn = dsn
        try:
            import pymysql  # type: ignore
        except Exception as e:  # pragma: no cover - import guard
            raise RuntimeError("pymysql is required for mariadb backend") from e
        self.mysql = pymysql
        self.conn = self.mysql.connect(self._parse_dsn(self.dsn), autocommit=False)
        self.ensure_schema()

    @staticmethod
    def from_url(url: str) -> MariaDbDAL:
        return MariaDbDAL(url)

    def _parse_dsn(self, url: str) -> dict[str, Any]:
        parsed = urlparse(url)
        if not parsed.scheme:
            raise ValueError("MariaDB DSN must include a scheme, e.g. mariadb://user:pass@host/db")

        config: dict[str, Any] = {}

        if parsed.hostname:
            config["host"] = parsed.hostname
        if parsed.port is not None:
            config["port"] = parsed.port
        if parsed.username is not None:
            config["user"] = parsed.username
        if parsed.password is not None:
            config["password"] = parsed.password

        database = parsed.path.lstrip("/")
        if database:
            config["database"] = database

        for key, value in parse_qsl(parsed.query, keep_blank_values=True):
            if key == "port":
                with contextlib.suppress(ValueError):
                    value = int(value)
            config[key] = value

        config.setdefault("host", "localhost")
        config.setdefault("database", "")

        return config

    def txn(self) -> contextlib.AbstractContextManager[None]:
        @contextlib.contextmanager
        def _tx() -> Iterator[None]:
            try:
                yield
                self.conn.commit()
            except Exception:  # pragma: no cover - passthrough
                self.conn.rollback()
                raise

        return _tx()

    def ensure_schema(self) -> None:
        here = Path(__file__).resolve()
        root = here.parents[3]
        migrations_dir = root / "db" / "migrations" / "mariadb"
        sql_files = sorted(migrations_dir.glob("*.sql"))
        if not sql_files:
            return
        with self.txn():
            cur = self.conn.cursor()
            try:
                for path in sql_files:
                    script = path.read_text(encoding="utf-8")
                    for stmt in script.split(";"):
                        if stmt.strip():
                            cur.execute(stmt)
            finally:
                cur.close()

    def ensure_artifact(self, **_: Any) -> dict[str, Any]:  # pragma: no cover - stub
        raise NotImplementedError("Implement mariadb artifact ops or use SQLite backend for dev.")

    def insert_item(self, **_: Any) -> dict[str, Any]:  # pragma: no cover - stub
        raise NotImplementedError("Implement mariadb item ops or use SQLite backend for dev.")

    def insert_event(self, **_: Any) -> None:  # pragma: no cover - stub
        raise NotImplementedError("Implement mariadb event ops or use SQLite backend for dev.")

    def fetch_by_tombstone(self, tombstone_id: str) -> tuple[ItemRow, ArtifactRow]:
        cur = self.conn.cursor()
        try:
            cur.execute("SELECT * FROM item WHERE tombstone_id = %s", (tombstone_id,))
            row = cur.fetchone()
            if not row:
                raise KeyError(f"Tombstone not found: {tombstone_id}")
            item_data = _cursor_row_to_dict(cur, row)
            cur.execute("SELECT * FROM artifact WHERE id = %s", (item_data["artifact_id"],))
            art_row = cur.fetchone()
            if not art_row:
                raise KeyError(f"Artifact missing for item {item_data['id']}")
            art_data = _cursor_row_to_dict(cur, art_row)
        finally:
            cur.close()

        metadata = _decode_json_field(item_data.get("metadata"))
        item = ItemRow(
            id=str(item_data["id"]),
            repo=str(item_data["repo"]),
            path=str(item_data["path"]),
            commit_sha=str(item_data["commit_sha"]),
            language=str(item_data.get("language") or ""),
            kind=str(item_data["kind"]),
            reason=str(item_data["reason"]),
            artifact_id=str(item_data["artifact_id"]),
            metadata=metadata,
            tombstone_id=str(item_data["tombstone_id"]),
        )

        blob_bytes = _maybe_bytes(art_data.get("blob_bytes"))
        artifact = ArtifactRow(
            id=str(art_data["id"]),
            content_sha256=str(art_data["content_sha256"]),
            size_bytes=int(art_data["size_bytes"]),
            compression=str(art_data["compression"]),
            mime_type=str(art_data["mime_type"]),
            storage_driver=str(art_data["storage_driver"]),
            blob_bytes=blob_bytes,
            object_url=(
                str(art_data["object_url"]) if art_data.get("object_url") is not None else None
            ),
        )
        return item, artifact

    def insert_referent(self, *, item_id: str, ref_type: str, ref_value: str) -> None:
        with self.txn():
            cur = self.conn.cursor()
            try:
                cur.execute(
                    "INSERT IGNORE INTO referent (item_id, ref_type, ref_value) VALUES (%s,%s,%s)",
                    (item_id, ref_type, ref_value),
                )
            finally:
                cur.close()

    def recent_items(self, *_: Any, **__: Any) -> list[dict[str, Any]]:  # pragma: no cover - stub
        raise NotImplementedError("Implement mariadb listing or use SQLite backend for dev.")

    def summary(self) -> dict[str, int]:  # pragma: no cover - stub
        raise NotImplementedError("Implement mariadb summary or use SQLite backend for dev.")

    def create_release_meta(
        self,
        *,
        release_id: str,
        version: str,
        created_at: str,
        actor: str,
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        rid = str(uuid.uuid4())
        payload = json.dumps(metadata or {}, ensure_ascii=False, sort_keys=True)
        with self.txn():
            cur = self.conn.cursor()
            try:
                sql = (
                    "INSERT INTO release_meta "
                    "(id, release_id, version, created_at, actor, metadata)\n"
                    "VALUES (%s,%s,%s,%s,%s,%s)"
                )
                cur.execute(sql, (rid, release_id, version, created_at, actor, payload))
            finally:
                cur.close()
        return {"id": rid, "release_id": release_id, "version": version}

    def add_release_component(
        self,
        *,
        release_meta_id: str,
        item_id: str | None,
        tombstone: str,
        dest_path: str,
        mode: str,
        template_vars: dict[str, Any],
    ) -> dict[str, Any]:
        cid = str(uuid.uuid4())
        payload = json.dumps(template_vars or {}, ensure_ascii=False, sort_keys=True)
        with self.txn():
            cur = self.conn.cursor()
            try:
                sql = (
                    "INSERT INTO release_component "
                    "(id, release_id, item_id, tombstone, dest_path, mode, template_vars)\n"
                    "VALUES (%s,%s,%s,%s,%s,%s,%s)"
                )
                cur.execute(
                    sql,
                    (cid, release_meta_id, item_id, tombstone, dest_path, mode, payload),
                )
            finally:
                cur.close()
        return {"id": cid, "release_id": release_meta_id, "tombstone": tombstone}

    def get_release_meta_by_release_id(self, *, release_id: str) -> dict[str, Any] | None:
        cur = self.conn.cursor()
        try:
            cur.execute("SELECT * FROM release_meta WHERE release_id = %s LIMIT 1", (release_id,))
            row = cur.fetchone()
            if not row:
                return None
            data = _cursor_row_to_dict(cur, row)
        finally:
            cur.close()
        data["id"] = str(data["id"])
        data["release_id"] = str(data["release_id"])
        data["metadata"] = _decode_json_field(data.get("metadata"))
        return data
