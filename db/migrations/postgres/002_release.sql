-- Ensure UUID generator is available for gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Release tracking tables (PostgreSQL)
CREATE TABLE IF NOT EXISTS release_meta (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  release_id  TEXT NOT NULL,
  version     TEXT NOT NULL,
  created_at  TIMESTAMPTZ NOT NULL,
  actor       TEXT NOT NULL,
  metadata    JSONB NOT NULL DEFAULT '{}'::jsonb
);
CREATE TABLE IF NOT EXISTS release_component (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  release_id    UUID NOT NULL REFERENCES release_meta(id) ON DELETE CASCADE,
  item_id       UUID, -- optional link to archive.item
  tombstone     TEXT NOT NULL,
  dest_path     TEXT NOT NULL,
  mode          TEXT NOT NULL DEFAULT '0644',
  template_vars JSONB NOT NULL DEFAULT '{}'::jsonb
);
