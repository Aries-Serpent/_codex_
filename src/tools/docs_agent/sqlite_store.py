from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA_SQL = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS documents(
  id TEXT PRIMARY KEY, title TEXT, summary TEXT, status TEXT, source_path TEXT, tags_json TEXT
);
CREATE TABLE IF NOT EXISTS sections(
  id TEXT PRIMARY KEY, document_id TEXT, heading TEXT, level INTEGER, tags_json TEXT
);
CREATE TABLE IF NOT EXISTS blocks(
  id TEXT PRIMARY KEY, section_id TEXT, block_type TEXT, text TEXT, tags_json TEXT
);
CREATE TABLE IF NOT EXISTS actions(
  id TEXT PRIMARY KEY, document_id TEXT, title TEXT, description TEXT, status TEXT,
  priority TEXT, related_file TEXT, tags_json TEXT
);
CREATE TABLE IF NOT EXISTS decisions(
  id TEXT PRIMARY KEY, statement TEXT, status TEXT, tags_json TEXT
);
CREATE TABLE IF NOT EXISTS requirements(
  id TEXT PRIMARY KEY, statement TEXT, status TEXT, constraint_type TEXT, tags_json TEXT
);
CREATE TABLE IF NOT EXISTS relationships(
  id TEXT PRIMARY KEY, relationship_type TEXT, source_id TEXT, source_type TEXT,
  target_id TEXT, target_type TEXT
);
CREATE TABLE IF NOT EXISTS "references"(
  id TEXT PRIMARY KEY, ref_type TEXT, label TEXT, target TEXT, document_id TEXT
);
CREATE TABLE IF NOT EXISTS files(
  path TEXT PRIMARY KEY, classification TEXT, covered INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS tags(tag TEXT PRIMARY KEY);
CREATE TABLE IF NOT EXISTS document_tags(document_id TEXT, tag TEXT, PRIMARY KEY(document_id, tag));
CREATE TABLE IF NOT EXISTS action_tags(action_id TEXT, tag TEXT, PRIMARY KEY(action_id, tag));
CREATE VIRTUAL TABLE IF NOT EXISTS docs_fts USING fts5(
  entity_id, entity_type, title, content, tags, related_files, reference_labels
);
"""


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(SCHEMA_SQL)
    return conn
