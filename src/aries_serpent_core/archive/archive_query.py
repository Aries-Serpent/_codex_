"""Archive Query Module

This module provides query operations for retrieving and displaying archive items
and their associated data, including restore payloads and item histories.

Classes:
    ArchiveQuery: Archive data retrieval and query operations

Author: Codex Team
"""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover - typing only
    from .archive_database import ArchiveDatabase

Params = dict[str, Any]


class ArchiveQuery:
    """Provides query operations for retrieving archive items and metadata."""

    def __init__(self, database: ArchiveDatabase) -> None:
        """Initialize query handler with database connection.

        Args:
            database: ArchiveDatabase instance for transaction management
        """
        self.database = database

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
        with self.database._transaction() as execute:
            rows = execute(sql, params, fetchall=True)
        result: list[dict[str, Any]] = []
        for row in rows or []:
            row_dict = dict(row)
            result.append(row_dict)
        return result

    def show_item(self, tombstone_id: str) -> dict[str, Any]:
        """Return a full view of a single item."""
        with self.database._transaction() as execute:
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

    def get_restore_payload(self, tombstone_id: str) -> dict[str, Any]:
        """Return the item and artifact payload for a restore operation."""
        with self.database._transaction() as execute:
            item = self._get_item_by_tombstone(execute, tombstone_id)
            if item is None:
                raise LookupError(f"Unknown tombstone id: {tombstone_id}")
            artifact = self._get_artifact_by_id(execute, item["artifact_id"])
        item_dict = dict(item)
        if isinstance(item_dict.get("metadata"), str):
            item_dict["metadata"] = json.loads(item_dict["metadata"])
        return {"item": item_dict, "artifact": dict(artifact)}

    def _get_artifact_by_id(self, execute: Callable[..., Any], artifact_id: str) -> dict[str, Any]:
        """Retrieve artifact by artifact ID."""
        artifact = execute(
            "SELECT * FROM artifact WHERE id = :id", {"id": artifact_id}, fetchone=True
        )
        if artifact is None:
            raise LookupError(f"Unknown artifact id: {artifact_id}")
        return artifact

    def _get_item_by_tombstone(
        self, execute: Callable[..., Any], tombstone_id: str
    ) -> dict[str, Any] | None:
        """Retrieve item by tombstone ID."""
        return execute(
            "SELECT * FROM item WHERE tombstone_id = :tomb",
            {"tomb": tombstone_id},
            fetchone=True,
        )
