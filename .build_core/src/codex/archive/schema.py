"""Database schema definitions for the Codex archive."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(frozen=True)
class SchemaBundle:
    """Container for DDL statements grouped by backend."""

    name: str
    statements: tuple[str, ...]


POSTGRES_BUNDLE = SchemaBundle(
    name="postgres",
    statements=(
        """
        CREATE TABLE IF NOT EXISTS artifact (
          id               UUID PRIMARY KEY,
          content_sha256   CHAR(64) NOT NULL UNIQUE,
          size_bytes       BIGINT NOT NULL,
          compression      TEXT NOT NULL DEFAULT 'zstd',
          mime_type        TEXT NOT NULL,
          storage_driver   TEXT NOT NULL DEFAULT 'db',
          blob_bytes       BYTEA,
          object_url       TEXT,
          created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """.strip(),
        """
        CREATE TABLE IF NOT EXISTS item (
          id               UUID PRIMARY KEY,
          repo             TEXT NOT NULL,
          path             TEXT NOT NULL,
          commit_sha       CHAR(40) NOT NULL,
          language         TEXT,
          kind             TEXT CHECK (kind IN ('code','doc','asset')) NOT NULL,
          reason           TEXT CHECK (reason IN ('dead','pruned','legacy','replaced')) NOT NULL,
          artifact_id      UUID NOT NULL REFERENCES artifact(id),
          metadata         JSONB NOT NULL DEFAULT '{}'::jsonb,
          archived_by      TEXT NOT NULL,
          archived_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
          tombstone_id     UUID NOT NULL UNIQUE,
          legal_hold       BOOLEAN NOT NULL DEFAULT FALSE,
          delete_after     TIMESTAMPTZ,
          restored_at      TIMESTAMPTZ
        )
        """.strip(),
        """
        CREATE INDEX IF NOT EXISTS idx_item_repo_path ON item(repo, path)
        """.strip(),
        """
        CREATE INDEX IF NOT EXISTS idx_item_archived_at ON item(archived_at)
        """.strip(),
        """
        CREATE INDEX IF NOT EXISTS idx_item_metadata_gin ON item USING GIN (metadata)
        """.strip(),
        """
        CREATE TABLE IF NOT EXISTS event (
          id               UUID PRIMARY KEY,
          item_id          UUID NOT NULL REFERENCES item(id),
          action           TEXT CHECK (
                             action IN ('ARCHIVE','RESTORE','PRUNE_REQUEST','DELETE_APPROVED')
                           ) NOT NULL,
          actor            TEXT NOT NULL,
          context          JSONB NOT NULL DEFAULT '{}'::jsonb,
          created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """.strip(),
        """
        CREATE INDEX IF NOT EXISTS idx_event_item_time ON event(item_id, created_at)
        """.strip(),
        """
        CREATE TABLE IF NOT EXISTS tag (
          item_id          UUID NOT NULL REFERENCES item(id),
          tag              TEXT NOT NULL,
          PRIMARY KEY (item_id, tag)
        )
        """.strip(),
        """
        CREATE TABLE IF NOT EXISTS referent (
          item_id          UUID NOT NULL REFERENCES item(id),
          ref_type         TEXT NOT NULL,
          ref_value        TEXT NOT NULL,
          PRIMARY KEY (item_id, ref_type, ref_value)
        )
        """.strip(),
    ),
)


MARIADB_BUNDLE = SchemaBundle(
    name="mariadb",
    statements=(
        """
        CREATE TABLE IF NOT EXISTS artifact (
          id             CHAR(36) PRIMARY KEY,
          content_sha256 CHAR(64) NOT NULL UNIQUE,
          size_bytes     BIGINT NOT NULL,
          compression    VARCHAR(16) NOT NULL DEFAULT 'zstd',
          mime_type      VARCHAR(255) NOT NULL,
          storage_driver VARCHAR(16) NOT NULL DEFAULT 'db',
          blob_bytes     LONGBLOB,
          object_url     TEXT,
          created_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB
        """.strip(),
        """
        CREATE TABLE IF NOT EXISTS item (
          id             CHAR(36) PRIMARY KEY,
          repo           VARCHAR(512) NOT NULL,
          path           VARCHAR(2048) NOT NULL,
          commit_sha     CHAR(40) NOT NULL,
          language       VARCHAR(64),
          kind           ENUM('code','doc','asset') NOT NULL,
          reason         ENUM('dead','pruned','legacy','replaced') NOT NULL,
          artifact_id    CHAR(36) NOT NULL,
          metadata       JSON NOT NULL,
          archived_by    VARCHAR(256) NOT NULL,
          archived_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
          tombstone_id   CHAR(36) NOT NULL UNIQUE,
          legal_hold     BOOLEAN NOT NULL DEFAULT FALSE,
          delete_after   TIMESTAMP NULL,
          restored_at    TIMESTAMP NULL,
          FOREIGN KEY (artifact_id) REFERENCES artifact(id)
        ) ENGINE=InnoDB
        """.strip(),
        """
        CREATE INDEX IF NOT EXISTS idx_item_repo_path ON item(repo(191), path(191))
        """.strip(),
        """
        CREATE INDEX IF NOT EXISTS idx_item_archived_at ON item(archived_at)
        """.strip(),
        """
        CREATE TABLE IF NOT EXISTS event (
          id          CHAR(36) PRIMARY KEY,
          item_id     CHAR(36) NOT NULL,
          action      ENUM('ARCHIVE','RESTORE','PRUNE_REQUEST','DELETE_APPROVED') NOT NULL,
          actor       VARCHAR(256) NOT NULL,
          context     JSON NOT NULL,
          created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (item_id) REFERENCES item(id)
        ) ENGINE=InnoDB
        """.strip(),
        """
        CREATE INDEX IF NOT EXISTS idx_event_item_time ON event(item_id, created_at)
        """.strip(),
        """
        CREATE TABLE IF NOT EXISTS tag (
          item_id  CHAR(36) NOT NULL,
          tag      VARCHAR(128) NOT NULL,
          PRIMARY KEY (item_id, tag),
          FOREIGN KEY (item_id) REFERENCES item(id)
        ) ENGINE=InnoDB
        """.strip(),
        """
        CREATE TABLE IF NOT EXISTS referent (
          item_id   CHAR(36) NOT NULL,
          ref_type  VARCHAR(32) NOT NULL,
          ref_value VARCHAR(512) NOT NULL,
          PRIMARY KEY (item_id, ref_type, ref_value),
          FOREIGN KEY (item_id) REFERENCES item(id)
        ) ENGINE=InnoDB
        """.strip(),
    ),
)


SQLITE_BUNDLE = SchemaBundle(
    name="sqlite",
    statements=(
        "PRAGMA journal_mode=WAL",
        """
        CREATE TABLE IF NOT EXISTS artifact (
          id             TEXT PRIMARY KEY,
          content_sha256 TEXT NOT NULL UNIQUE,
          size_bytes     INTEGER NOT NULL,
          compression    TEXT NOT NULL DEFAULT 'zstd',
          mime_type      TEXT NOT NULL,
          storage_driver TEXT NOT NULL DEFAULT 'db',
          blob_bytes     BLOB,
          object_url     TEXT,
          created_at     TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """.strip(),
        """
        CREATE TABLE IF NOT EXISTS item (
          id             TEXT PRIMARY KEY,
          repo           TEXT NOT NULL,
          path           TEXT NOT NULL,
          commit_sha     TEXT NOT NULL,
          language       TEXT,
          kind           TEXT NOT NULL CHECK (kind IN ('code','doc','asset')),
          reason         TEXT NOT NULL CHECK (reason IN ('dead','pruned','legacy','replaced')),
          artifact_id    TEXT NOT NULL REFERENCES artifact(id),
          metadata       TEXT NOT NULL DEFAULT '{}',
          archived_by    TEXT NOT NULL,
          archived_at    TEXT NOT NULL DEFAULT (datetime('now')),
          tombstone_id   TEXT NOT NULL UNIQUE,
          legal_hold     INTEGER NOT NULL DEFAULT 0,
          delete_after   TEXT,
          restored_at    TEXT
        )
        """.strip(),
        """
        CREATE INDEX IF NOT EXISTS idx_item_repo_path ON item(repo, path)
        """.strip(),
        """
        CREATE INDEX IF NOT EXISTS idx_item_archived_at ON item(archived_at)
        """.strip(),
        """
        CREATE TABLE IF NOT EXISTS event (
          id         TEXT PRIMARY KEY,
          item_id    TEXT NOT NULL REFERENCES item(id),
          action     TEXT NOT NULL,
          actor      TEXT NOT NULL,
          context    TEXT NOT NULL DEFAULT '{}',
          created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """.strip(),
        """
        CREATE INDEX IF NOT EXISTS idx_event_item_time ON event(item_id, created_at)
        """.strip(),
        """
        CREATE TABLE IF NOT EXISTS tag (
          item_id TEXT NOT NULL,
          tag     TEXT NOT NULL,
          PRIMARY KEY (item_id, tag)
        )
        """.strip(),
        """
        CREATE TABLE IF NOT EXISTS referent (
          item_id   TEXT NOT NULL,
          ref_type  TEXT NOT NULL,
          ref_value TEXT NOT NULL,
          PRIMARY KEY (item_id, ref_type, ref_value)
        )
        """.strip(),
    ),
)


BUNDLES = {bundle.name: bundle for bundle in (POSTGRES_BUNDLE, MARIADB_BUNDLE, SQLITE_BUNDLE)}


def get_bundle(name: str) -> SchemaBundle:
    """Return the schema bundle for *name* (case insensitive)."""

    key = name.lower()
    if key not in BUNDLES:
        raise KeyError(f"Unsupported archive backend: {name}")
    return BUNDLES[key]


def statements_for(name: str) -> Iterable[str]:
    """Yield DDL statements for *name*."""

    bundle = get_bundle(name)
    return bundle.statements
