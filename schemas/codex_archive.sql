-- Codex archive portable schema
-- Generated from codex.archive.schema

-- PostgreSQL -----------------------------------------------------------

CREATE TABLE artifact (
  id               UUID PRIMARY KEY,
  content_sha256   CHAR(64) NOT NULL UNIQUE,
  size_bytes       BIGINT NOT NULL,
  compression      TEXT NOT NULL DEFAULT 'zstd',
  mime_type        TEXT NOT NULL,
  storage_driver   TEXT NOT NULL DEFAULT 'db',
  blob_bytes       BYTEA,
  object_url       TEXT,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE item (
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
);

CREATE INDEX IF NOT EXISTS idx_item_repo_path ON item(repo, path);
CREATE INDEX IF NOT EXISTS idx_item_archived_at ON item(archived_at);
CREATE INDEX IF NOT EXISTS idx_item_metadata_gin ON item USING GIN (metadata);

CREATE TABLE event (
  id               UUID PRIMARY KEY,
  item_id          UUID NOT NULL REFERENCES item(id),
  action           TEXT CHECK (
                      action IN ('ARCHIVE','RESTORE','PRUNE_REQUEST','DELETE_APPROVED')
                    ) NOT NULL,
  actor            TEXT NOT NULL,
  context          JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_event_item_time ON event(item_id, created_at);

CREATE TABLE tag (
  item_id          UUID NOT NULL REFERENCES item(id),
  tag              TEXT NOT NULL,
  PRIMARY KEY (item_id, tag)
);

CREATE TABLE referent (
  item_id          UUID NOT NULL REFERENCES item(id),
  ref_type         TEXT NOT NULL,
  ref_value        TEXT NOT NULL,
  PRIMARY KEY (item_id, ref_type, ref_value)
);

-- MariaDB --------------------------------------------------------------

CREATE TABLE artifact (
  id             CHAR(36) PRIMARY KEY,
  content_sha256 CHAR(64) NOT NULL UNIQUE,
  size_bytes     BIGINT NOT NULL,
  compression    VARCHAR(16) NOT NULL DEFAULT 'zstd',
  mime_type      VARCHAR(255) NOT NULL,
  storage_driver VARCHAR(16) NOT NULL DEFAULT 'db',
  blob_bytes     LONGBLOB,
  object_url     TEXT,
  created_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE item (
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
) ENGINE=InnoDB;

CREATE INDEX IF NOT EXISTS idx_item_repo_path ON item(repo(191), path(191));
CREATE INDEX IF NOT EXISTS idx_item_archived_at ON item(archived_at);

CREATE TABLE event (
  id          CHAR(36) PRIMARY KEY,
  item_id     CHAR(36) NOT NULL,
  action      ENUM('ARCHIVE','RESTORE','PRUNE_REQUEST','DELETE_APPROVED') NOT NULL,
  actor       VARCHAR(256) NOT NULL,
  context     JSON NOT NULL,
  created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (item_id) REFERENCES item(id)
) ENGINE=InnoDB;

CREATE INDEX IF NOT EXISTS idx_event_item_time ON event(item_id, created_at);

CREATE TABLE tag (
  item_id  CHAR(36) NOT NULL,
  tag      VARCHAR(128) NOT NULL,
  PRIMARY KEY (item_id, tag),
  FOREIGN KEY (item_id) REFERENCES item(id)
) ENGINE=InnoDB;

CREATE TABLE referent (
  item_id   CHAR(36) NOT NULL,
  ref_type  VARCHAR(32) NOT NULL,
  ref_value VARCHAR(512) NOT NULL,
  PRIMARY KEY (item_id, ref_type, ref_value),
  FOREIGN KEY (item_id) REFERENCES item(id)
) ENGINE=InnoDB;

-- SQLite ----------------------------------------------------------------

PRAGMA journal_mode=WAL;

CREATE TABLE artifact (
  id             TEXT PRIMARY KEY,
  content_sha256 TEXT NOT NULL UNIQUE,
  size_bytes     INTEGER NOT NULL,
  compression    TEXT NOT NULL DEFAULT 'zstd',
  mime_type      TEXT NOT NULL,
  storage_driver TEXT NOT NULL DEFAULT 'db',
  blob_bytes     BLOB,
  object_url     TEXT,
  created_at     TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE item (
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
);

CREATE INDEX IF NOT EXISTS idx_item_repo_path ON item(repo, path);
CREATE INDEX IF NOT EXISTS idx_item_archived_at ON item(archived_at);

CREATE TABLE event (
  id         TEXT PRIMARY KEY,
  item_id    TEXT NOT NULL REFERENCES item(id),
  action     TEXT NOT NULL,
  actor      TEXT NOT NULL,
  context    TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_event_item_time ON event(item_id, created_at);

CREATE TABLE tag (
  item_id TEXT NOT NULL,
  tag     TEXT NOT NULL,
  PRIMARY KEY (item_id, tag)
);

CREATE TABLE referent (
  item_id   TEXT NOT NULL,
  ref_type  TEXT NOT NULL,
  ref_value TEXT NOT NULL,
  PRIMARY KEY (item_id, ref_type, ref_value)
);
