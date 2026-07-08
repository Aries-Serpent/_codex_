"""Archive Operations Module

This module provides operations for recording archive-related events and actions,
including archiving, restoring, pruning, and deletion approvals.

Classes:
    ArchiveOperations: Core archive operation recording

Author: Codex Team
"""

from __future__ import annotations

import uuid
from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, Any

from .util import json_dumps_sorted, utcnow  # noqa: E402

if TYPE_CHECKING:  # pragma: no cover - typing only
    from .archive_database import ArchiveDatabase

Params = dict[str, Any]


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


class ArchiveOperations:
    """Records archive operations and maintains event audit trail."""

    def __init__(self, database: ArchiveDatabase) -> None:
        """Initialize operations handler with database connection.

        Args:
            database: ArchiveDatabase instance for transaction management
        """
        self.database = database

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

        with self.database._transaction() as execute:
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

    def record_restore(self, tombstone_id: str, *, actor: str) -> None:
        """Persist restore metadata after a successful restore."""
        with self.database._transaction() as execute:
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
        with self.database._transaction() as execute:
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

        with self.database._transaction() as execute:
            item = self._get_item_by_tombstone(execute, tombstone_id)
            if item is None:
                raise LookupError(f"Unknown tombstone id: {tombstone_id}")
            if int(item.get("legal_hold", 0)):
                raise PermissionError("Item is under legal hold and cannot be purged")
            artifact_id = item["artifact_id"]
            blob_scrubbed = False
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
            for actor, tag in (
                (primary_actor, "primary"),
                (secondary_actor, "secondary"),
            ):
                context_payload = {"role": tag, "reason": reason}
                if apply:
                    context_payload.update(
                        {
                            "apply_requested": True,  # type: ignore[dict-item]
                            "blob_scrubbed": blob_scrubbed,  # type: ignore[dict-item]
                        }
                    )
                    if reference_count > 1:
                        context_payload["shared_references"] = max(reference_count - 1, 0)  # type: ignore[assignment]
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

    def _get_artifact_by_sha(self, execute: Callable[..., Any], sha: str) -> dict[str, Any] | None:
        """Retrieve artifact by content SHA."""
        return execute(
            "SELECT * FROM artifact WHERE content_sha256 = :sha",
            {"sha": sha},
            fetchone=True,
        )

    def _get_item_by_tombstone(
        self, execute: Callable[..., Any], tombstone_id: str
    ) -> dict[str, Any] | None:
        """Retrieve item by tombstone ID."""
        return execute(
            "SELECT * FROM item WHERE tombstone_id = :tomb",
            {"tomb": tombstone_id},
            fetchone=True,
        )
