-- PostgreSQL initial schema for Codex Archive
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS artifact (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  content_sha256   CHAR(64) NOT NULL UNIQUE,
  size_bytes       BIGINT NOT NULL,
  compression      TEXT NOT NULL DEFAULT 'zlib',
  mime_type        TEXT NOT NULL,
  storage_driver   TEXT NOT NULL DEFAULT 'db',
  blob_bytes       BYTEA,
  object_url       TEXT,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS item (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  repo             TEXT NOT NULL,
  path             TEXT NOT NULL,
  commit_sha       CHAR(40) NOT NULL,
  language         TEXT,
  kind             TEXT CHECK (kind IN ('code','doc','asset')) NOT NULL DEFAULT 'code',
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

CREATE TABLE IF NOT EXISTS event (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  item_id          UUID NOT NULL REFERENCES item(id),
  action           TEXT CHECK (action IN ('ARCHIVE','RESTORE','PRUNE_REQUEST','DELETE_APPROVED')) NOT NULL,
  actor            TEXT NOT NULL,
  context          JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_event_item_time ON event(item_id, created_at);

CREATE TABLE IF NOT EXISTS tag (
  item_id          UUID NOT NULL REFERENCES item(id),
  tag              TEXT NOT NULL,
  PRIMARY KEY (item_id, tag)
);

CREATE TABLE IF NOT EXISTS referent (
  item_id          UUID NOT NULL REFERENCES item(id),
  ref_type         TEXT NOT NULL,
  ref_value        TEXT NOT NULL,
  PRIMARY KEY (item_id, ref_type, ref_value)
);
