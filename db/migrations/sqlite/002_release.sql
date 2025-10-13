-- Release tracking tables (optional; offline-friendly)
CREATE TABLE IF NOT EXISTS release_meta (
  id            TEXT PRIMARY KEY,
  release_id    TEXT NOT NULL,
  version       TEXT NOT NULL,
  created_at    TEXT NOT NULL,
  actor         TEXT NOT NULL,
  metadata      TEXT NOT NULL DEFAULT '{}'
);
CREATE TABLE IF NOT EXISTS release_component (
  id            TEXT PRIMARY KEY,
  release_id    TEXT NOT NULL,
  item_id       TEXT,             -- optional, if resolvable
  tombstone     TEXT NOT NULL,
  dest_path     TEXT NOT NULL,
  mode          TEXT NOT NULL DEFAULT '0644',
  template_vars TEXT NOT NULL DEFAULT '{}'
);
