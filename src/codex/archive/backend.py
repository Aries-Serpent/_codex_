"""Database access layer for the Codex archive."""

from __future__ import annotations

import json
import os
import sqlite3
import uuid
from collections.abc import Callable, Iterable, Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

try:  # pragma: no cover - optional dependency
    import sqlalchemy as sa  # type: ignore
except Exception:  # pragma: no cover
    sa = None

from . import schema
from .config import ArchiveAppConfig as RuntimeArchiveConfig
from .util import ensure_directory, json_dumps_sorted, utcnow

if TYPE_CHECKING:  # pragma: no cover - typing only
    from .config import ArchiveAppConfig as SettingsArchiveConfig

Params = dict[str, Any]


@dataclass(frozen=True)
class ArchiveConfig:
    """Runtime configuration for the archive backend."""

    url: str
    backend: str

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> ArchiveConfig:
        runtime_env = dict(os.environ)
        if env is not None:
            runtime_env.update(env)
        settings = RuntimeArchiveConfig.from_env(runtime_env)
        return cls(url=settings.backend.url, backend=settings.backend.type)

    @classmethod
    def from_settings(
        cls,
        settings: RuntimeArchiveConfig | SettingsArchiveConfig,
    ) -> ArchiveConfig:
        """Create a runtime backend config from archive settings."""

        return cls(url=settings.backend.url, backend=settings.backend.type)


def infer_backend(url: str) -> str:
    lowered = url.lower()
    if lowered.startswith("postgres"):
        return "postgres"
    if lowered.startswith("mariadb") or lowered.startswith("mysql"):
        return "mariadb"
    if lowered.startswith("sqlite"):
        return "sqlite"
    raise ValueError(f"Unable to infer archive backend from URL: {url}")


class ArchiveDAL:
    """Archive data access layer supporting PostgreSQL, MariaDB, and SQLite."""

    def __init__(self, config: ArchiveConfig | None = None, *, apply_schema: bool = True) -> None:
        self.config = config or ArchiveConfig.from_env()
        self.backend = self.config.backend
        self.url = self.config.url
        self._conn: sqlite3.Connection | None = None
        self._engine: Any | None = None
        if self.backend == "sqlite":
            path = self._sqlite_path(self.url)
            ensure_directory(path.parent)
            self._conn = sqlite3.connect(str(path))
            self._conn.row_factory = sqlite3.Row
        else:
            if sa is None:  # pragma: no cover - informative guard
                raise RuntimeError(
                    "sqlalchemy is required for non-sqlite archive backends. "
                    "Install sqlalchemy>=2.0"
                )
            self._engine = sa.create_engine(self.url, future=True)
        if apply_schema:
            self.ensure_schema()

    # ------------------------------------------------------------------
    # schema management
    # ------------------------------------------------------------------
    def ensure_schema(self) -> None:
        """Apply the schema bundle for the configured backend."""

        statements = schema.statements_for(self.backend)
        with self._transaction() as execute:
            for statement in statements:
                execute(statement)

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------
    def record_archive(
        self,
        *,
        repo: str,
        path: str,
        commit_sha: str,
        language: str | None,
        reason: str,
        kind: str,
        artifact_payload: dict[str, Any],
        archived_by: str,
        metadata: dict[str, Any],
        context: dict[str, Any],
        tags: Iterable[str] | None = None,
    ) -> dict[str, Any]:
        """Persist an archive record, returning the stored row."""

        now = utcnow()
        tombstone_id = str(uuid.uuid4())
        meta_copy = dict(metadata)
        legal_hold_raw = meta_copy.pop("legal_hold", 0)
        legal_hold_value = _coerce_bool(legal_hold_raw)
        delete_after_value = meta_copy.pop("delete_after", None)
        if legal_hold_value:
            meta_copy.setdefault("legal_hold", True)
        if delete_after_value is not None:
            meta_copy.setdefault("delete_after", delete_after_value)
        with self._transaction() as execute:
            artifact = self._get_artifact_by_sha(execute, artifact_payload["content_sha256"])
            if artifact is None:
                artifact_id = str(uuid.uuid4())
                artifact = {
                    "id": artifact_id,
                    **artifact_payload,
                    "created_at": now,
                }
                execute(
                    """
                    INSERT INTO artifact (
                        id, content_sha256, size_bytes, compression, mime_type,
                        storage_driver, blob_bytes, object_url, created_at
                    ) VALUES (
                        :id, :content_sha256, :size_bytes, :compression, :mime_type,
                        :storage_driver, :blob_bytes, :object_url, :created_at
                    )
                    """,
                    artifact,
                )
            else:
                artifact_id = artifact["id"]
                needs_refresh = (
                    artifact.get("blob_bytes") is None
                    or artifact.get("storage_driver") != artifact_payload["storage_driver"]
                )
                metadata_changed = any(
                    artifact.get(field) != artifact_payload[field]
                    for field in ("size_bytes", "compression", "mime_type")
                )
                if needs_refresh or metadata_changed:
                    execute(
                        """
                        UPDATE artifact
                        SET size_bytes = :size_bytes,
                            compression = :compression,
                            mime_type = :mime_type,
                            storage_driver = :storage_driver,
                            blob_bytes = :blob_bytes,
                            object_url = :object_url
                        WHERE id = :id
                        """,
                        {"id": artifact_id, **artifact_payload},
                    )

            item_id = str(uuid.uuid4())
            item_payload = {
                "id": item_id,
                "repo": repo,
                "path": path,
                "commit_sha": commit_sha,
                "language": language,
                "kind": kind,
                "reason": reason,
                "artifact_id": artifact_id,
                "metadata": json_dumps_sorted(meta_copy),
                "archived_by": archived_by,
                "archived_at": now,
                "tombstone_id": tombstone_id,
                "legal_hold": legal_hold_value,
                "delete_after": delete_after_value,
                "restored_at": None,
            }
            execute(
                """
                INSERT INTO item (
                    id, repo, path, commit_sha, language, kind, reason, artifact_id,
                    metadata, archived_by, archived_at, tombstone_id, legal_hold,
                    delete_after, restored_at
                ) VALUES (
                    :id, :repo, :path, :commit_sha, :language, :kind, :reason, :artifact_id,
                    :metadata, :archived_by, :archived_at, :tombstone_id, :legal_hold,
                    :delete_after, :restored_at
                )
                """,
                item_payload,
            )

            event_payload = {
                "id": str(uuid.uuid4()),
                "item_id": item_id,
                "action": "ARCHIVE",
                "actor": archived_by,
                "context": json_dumps_sorted(context),
                "created_at": now,
            }
            execute(
                """
                INSERT INTO event (id, item_id, action, actor, context, created_at)
                VALUES (:id, :item_id, :action, :actor, :context, :created_at)
                """,
                event_payload,
            )

            for tag in tags or []:
                params = {"item_id": item_id, "tag": tag}
                existing = execute(
                    "SELECT 1 FROM tag WHERE item_id = :item_id AND tag = :tag",
                    params,
                    fetchone=True,
                )
                if existing is None:
                    execute(
                        "INSERT INTO tag (item_id, tag) VALUES (:item_id, :tag)",
                        params,
                    )

        return {
            "tombstone_id": tombstone_id,
            "artifact_id": artifact_id,
            "item_id": item_id,
        }

    def get_restore_payload(self, tombstone_id: str) -> dict[str, Any]:
        """Return the item and artifact payload for a restore operation."""

        with self._transaction() as execute:
            item = self._get_item_by_tombstone(execute, tombstone_id)
            if item is None:
                raise LookupError(f"Unknown tombstone id: {tombstone_id}")
            artifact = self._get_artifact_by_id(execute, item["artifact_id"])
        item_dict = dict(item)
        if isinstance(item_dict.get("metadata"), str):
            item_dict["metadata"] = json.loads(item_dict["metadata"])
        return {"item": item_dict, "artifact": dict(artifact)}

    def record_restore(self, tombstone_id: str, *, actor: str) -> None:
        """Persist restore metadata after a successful restore."""

        with self._transaction() as execute:
            item = self._get_item_by_tombstone(execute, tombstone_id)
            if item is None:
                raise LookupError(f"Unknown tombstone id: {tombstone_id}")
            now = utcnow()
            execute(
                """
                UPDATE item SET restored_at = :restored_at WHERE id = :id
                """,
                {"restored_at": now, "id": item["id"]},
            )
            event_payload = {
                "id": str(uuid.uuid4()),
                "item_id": item["id"],
                "action": "RESTORE",
                "actor": actor,
                "context": json_dumps_sorted({}),
                "created_at": now,
            }
            execute(
                """
                INSERT INTO event (id, item_id, action, actor, context, created_at)
                VALUES (:id, :item_id, :action, :actor, :context, :created_at)
                """,
                event_payload,
            )

    def record_prune_request(self, tombstone_id: str, *, actor: str, reason: str) -> None:
        """Record a prune request event."""

        with self._transaction() as execute:
            item = self._get_item_by_tombstone(execute, tombstone_id)
            if item is None:
                raise LookupError(f"Unknown tombstone id: {tombstone_id}")
            payload = {
                "id": str(uuid.uuid4()),
                "item_id": item["id"],
                "action": "PRUNE_REQUEST",
                "actor": actor,
                "context": json_dumps_sorted({"reason": reason}),
                "created_at": utcnow(),
            }
            execute(
                """
                INSERT INTO event (id, item_id, action, actor, context, created_at)
                VALUES (:id, :item_id, :action, :actor, :context, :created_at)
                """,
                payload,
            )

    def record_delete_approval(
        self,
        tombstone_id: str,
        *,
        primary_actor: str,
        secondary_actor: str,
        reason: str,
        apply: bool = False,
    ) -> bool:
        """Insert dual approvals and optionally scrub blob bytes.

        Returns ``True`` when the underlying artifact payload was scrubbed.
        ``False`` indicates that the blob bytes were left intact (for example
        because the artifact is still referenced by other tombstones).
        """

        if primary_actor == secondary_actor:
            raise ValueError("Primary and secondary approvers must be distinct")
        with self._transaction() as execute:
            item = self._get_item_by_tombstone(execute, tombstone_id)
            if item is None:
                raise LookupError(f"Unknown tombstone id: {tombstone_id}")
            if int(item.get("legal_hold", 0)):
                raise PermissionError("Item is under legal hold and cannot be purged")
            artifact_id = item["artifact_id"]
            blob_scrubbed = False
            reference_count = 1
            if apply:
                row = execute(
                    """
                    SELECT COUNT(*) AS ref_count
                    FROM item
                    WHERE artifact_id = :artifact_id
                    """,
                    {"artifact_id": artifact_id},
                    fetchone=True,
                )
                raw_count = row.get("ref_count", 0) if row else 0
                reference_count = int(raw_count)
                blob_scrubbed = reference_count <= 1
            now = utcnow()
            for actor, tag in ((primary_actor, "primary"), (secondary_actor, "secondary")):
                context_payload = {"role": tag, "reason": reason}
                if apply:
                    context_payload.update(
                        {
                            "apply_requested": True,
                            "blob_scrubbed": blob_scrubbed,
                        }
                    )
                    if reference_count > 1:
                        context_payload["shared_references"] = max(reference_count - 1, 0)
                payload = {
                    "id": str(uuid.uuid4()),
                    "item_id": item["id"],
                    "action": "DELETE_APPROVED",
                    "actor": actor,
                    "context": json_dumps_sorted(context_payload),
                    "created_at": now,
                }
                execute(
                    """
                    INSERT INTO event (id, item_id, action, actor, context, created_at)
                    VALUES (:id, :item_id, :action, :actor, :context, :created_at)
                    """,
                    payload,
                )
            if blob_scrubbed:
                execute(
                    """
                    UPDATE artifact
                    SET blob_bytes = NULL,
                        storage_driver = 'object',
                        object_url = COALESCE(object_url, 'purged://dual-control')
                    WHERE id = :artifact_id
                    """,
                    {"artifact_id": artifact_id},
                )
            return blob_scrubbed

    def list_items(
        self,
        *,
        repo: str | None = None,
        since: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Return archived items with optional filters."""

        params: Params = {"limit": limit}
        clauses: list[str] = []
        if repo:
            clauses.append("repo = :repo")
            params["repo"] = repo
        if since:
            clauses.append("archived_at >= :since")
            params["since"] = since
        query_lines = [
            "SELECT id, repo, path, commit_sha, reason, archived_by, archived_at, tombstone_id",
            "FROM item",
        ]
        if clauses:
            query_lines.append("WHERE " + " AND ".join(clauses))
        query_lines.extend(
            [
                "ORDER BY archived_at DESC",
                "LIMIT :limit",
            ]
        )
        sql = "\n".join(query_lines)
        with self._transaction() as execute:
            rows = execute(sql, params, fetchall=True)
        result: list[dict[str, Any]] = []
        for row in rows or []:
            row_dict = dict(row)
            result.append(row_dict)
        return result

    def show_item(self, tombstone_id: str) -> dict[str, Any]:
        """Return a full view of a single item."""

        with self._transaction() as execute:
            item = self._get_item_by_tombstone(execute, tombstone_id)
            if item is None:
                raise LookupError(f"Unknown tombstone id: {tombstone_id}")
            events = execute(
                (
                    "SELECT action, actor, context, created_at "
                    "FROM event WHERE item_id = :item_id "
                    "ORDER BY created_at"
                ),
                {"item_id": item["id"]},
                fetchall=True,
            )
        item_dict = dict(item)
        if isinstance(item_dict.get("metadata"), str):
            item_dict["metadata"] = json.loads(item_dict["metadata"])
        events_payload = []
        for row in events or []:
            entry = dict(row)
            context = entry.get("context")
            if isinstance(context, str):
                entry["context"] = json.loads(context)
            events_payload.append(entry)
        item_dict["events"] = events_payload
        return item_dict

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------
    def _sqlite_path(self, url: str) -> Path:
        prefix = "sqlite:///"
        if url.startswith(prefix):
            path = url[len(prefix) :]
        elif url.startswith("sqlite://"):
            path = url[len("sqlite://") :]
        else:
            path = url
        return Path(path).expanduser().resolve()

    @contextmanager
    def _transaction(self) -> Iterator[Callable[[str, Params | None, bool, bool], Any]]:
        if self.backend == "sqlite":
            if self._conn is None:
                raise RuntimeError("SQLite connection is not initialised")
            cursor = self._conn.cursor()
            try:

                def execute_sql(
                    sql: str,
                    params: Params | None = None,
                    fetchone: bool = False,
                    fetchall: bool = False,
                ) -> Any:
                    return self._sqlite_execute(cursor, sql, params, fetchone, fetchall)

                yield execute_sql
                self._conn.commit()
            except Exception:
                self._conn.rollback()
                raise
            finally:
                cursor.close()
        else:
            if self._engine is None:
                raise RuntimeError("SQLAlchemy engine is not initialised")
            with self._engine.begin() as connection:

                def execute_sql(
                    sql: str,
                    params: Params | None = None,
                    fetchone: bool = False,
                    fetchall: bool = False,
                ) -> Any:
                    return self._sqlalchemy_execute(connection, sql, params, fetchone, fetchall)

                yield execute_sql

    def _sqlite_execute(
        self,
        cursor: sqlite3.Cursor,
        sql: str,
        params: Params | None,
        fetchone: bool,
        fetchall: bool,
    ) -> Any:
        parameters = params or {}
        cursor.execute(sql, parameters)
        if fetchone:
            row = cursor.fetchone()
            return dict(row) if row is not None else None
        if fetchall:
            return [dict(row) for row in cursor.fetchall()]
        return None

    def _sqlalchemy_execute(
        self, connection: Any, sql: str, params: Params | None, fetchone: bool, fetchall: bool
    ) -> Any:
        statement = sa.text(sql)
        result = connection.execute(statement, params or {})
        if fetchone:
            row = result.mappings().first()
            return dict(row) if row is not None else None
        if fetchall:
            return [dict(row) for row in result.mappings().all()]
        return None

    def _get_artifact_by_sha(self, execute: Callable[..., Any], sha: str) -> dict[str, Any] | None:
        return execute(
            "SELECT * FROM artifact WHERE content_sha256 = :sha", {"sha": sha}, fetchone=True
        )

    def _get_artifact_by_id(self, execute: Callable[..., Any], artifact_id: str) -> dict[str, Any]:
        artifact = execute(
            "SELECT * FROM artifact WHERE id = :id", {"id": artifact_id}, fetchone=True
        )
        if artifact is None:
            raise LookupError(f"Unknown artifact id: {artifact_id}")
        return artifact

    def _get_item_by_tombstone(
        self, execute: Callable[..., Any], tombstone_id: str
    ) -> dict[str, Any] | None:
        return execute(
            "SELECT * FROM item WHERE tombstone_id = :tomb", {"tomb": tombstone_id}, fetchone=True
        )


def _coerce_bool(value: Any) -> int:
    """Normalise truthy inputs to 0/1 for SQL storage."""

    if isinstance(value, bool):
        return 1 if value else 0
    if isinstance(value, int | float):
        return 1 if value else 0
    if isinstance(value, str):
        lowered = value.strip().lower()
        return 1 if lowered in {"1", "true", "yes", "on"} else 0
    return 0
