"""
Backend Module

This module provides the Archive Data Access Layer (DAL) facade that composes
specialized modules for database operations, archive operations, and queries.

Usage:
    from archive.backend import ArchiveDAL, ArchiveConfig

Classes:
    ArchiveDAL: Main data access layer facade (backward compatible)
    ArchiveConfig: Runtime configuration

Author: Codex Team
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


import os  # noqa: E402
from collections.abc import Iterable, Mapping  # noqa: E402
from dataclasses import dataclass  # noqa: E402
from typing import TYPE_CHECKING, Any  # noqa: E402

from .archive_database import ArchiveDatabase  # noqa: E402
from .archive_operations import ArchiveOperations  # noqa: E402
from .archive_query import ArchiveQuery  # noqa: E402

if TYPE_CHECKING:  # pragma: no cover - typing only
    pass

Params = dict[str, Any]


@dataclass(frozen=True)
class ArchiveConfig:
    """Runtime configuration for the archive backend."""

    url: str
    backend: str

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> ArchiveConfig:
        runtime_env: dict[str, str] = dict(os.environ)
        if env is not None:
            runtime_env.update(env)
        # Read env vars directly — avoids the backend→config→backend cyclic import.
        url = runtime_env.get("CODEX_ARCHIVE_URL", "sqlite:///./.codex/archive.sqlite")
        backend = runtime_env.get("CODEX_ARCHIVE_BACKEND") or infer_backend(url)
        return cls(url=url, backend=backend)

    @classmethod
    def from_settings(
        cls,
        settings: Any,  # ArchiveAppConfig from .config — omitted to break cyclic import
    ) -> ArchiveConfig:
        """Create a runtime backend config from archive settings."""

        return cls(url=settings.backend.url, backend=settings.backend.backend)


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
    """Archive data access layer supporting PostgreSQL, MariaDB, and SQLite.

    This class acts as a facade that composes ArchiveDatabase, ArchiveOperations,
    and ArchiveQuery modules. It maintains backward compatibility with the original API.
    """

    def __init__(self, config: ArchiveConfig | None = None, *, apply_schema: bool = True) -> None:
        self.config = config or ArchiveConfig.from_env()
        self.backend = self.config.backend
        self.url = self.config.url

        # Initialize specialized modules
        self._db = ArchiveDatabase(self.backend, self.url, apply_schema=apply_schema)
        self._operations = ArchiveOperations(self._db)
        self._query = ArchiveQuery(self._db)

    # ------------------------------------------------------------------
    # schema management
    # ------------------------------------------------------------------
    def ensure_schema(self) -> None:
        """Apply the schema bundle for the configured backend."""
        self._db.ensure_schema()

    # ------------------------------------------------------------------
    # public API: delegated to operations module
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
        return self._operations.record_archive(
            repo=repo,
            path=path,
            commit_sha=commit_sha,
            language=language,
            reason=reason,
            kind=kind,
            artifact_payload=artifact_payload,
            archived_by=archived_by,
            metadata=metadata,
            context=context,
            tags=tags,
        )

    def record_restore(self, tombstone_id: str, *, actor: str) -> None:
        """Persist restore metadata after a successful restore."""
        self._operations.record_restore(tombstone_id, actor=actor)

    def record_prune_request(self, tombstone_id: str, *, actor: str, reason: str) -> None:
        """Record a prune request event."""
        self._operations.record_prune_request(tombstone_id, actor=actor, reason=reason)

    def record_delete_approval(
        self,
        tombstone_id: str,
        *,
        primary_actor: str,
        secondary_actor: str,
        reason: str,
        apply: bool = False,
    ) -> bool:
        """Insert dual approvals and optionally scrub blob bytes."""
        return self._operations.record_delete_approval(
            tombstone_id,
            primary_actor=primary_actor,
            secondary_actor=secondary_actor,
            reason=reason,
            apply=apply,
        )

    # ------------------------------------------------------------------
    # public API: delegated to query module
    # ------------------------------------------------------------------
    def list_items(
        self,
        *,
        repo: str | None = None,
        since: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Return archived items with optional filters."""
        return self._query.list_items(repo=repo, since=since, limit=limit)

    def show_item(self, tombstone_id: str) -> dict[str, Any]:
        """Return a full view of a single item."""
        return self._query.show_item(tombstone_id)

    def get_restore_payload(self, tombstone_id: str) -> dict[str, Any]:
        """Return the item and artifact payload for a restore operation."""
        return self._query.get_restore_payload(tombstone_id)
