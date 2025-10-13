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
