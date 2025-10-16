-- MariaDB initial schema for Codex Archive (InnoDB)
CREATE TABLE IF NOT EXISTS artifact (
  id             CHAR(36) PRIMARY KEY,
  content_sha256 CHAR(64) NOT NULL UNIQUE,
  size_bytes     BIGINT NOT NULL,
  compression    VARCHAR(16) NOT NULL DEFAULT 'zlib',
  mime_type      VARCHAR(255) NOT NULL,
  storage_driver VARCHAR(16) NOT NULL DEFAULT 'db',
  blob_bytes     LONGBLOB,
  object_url     TEXT,
  created_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS item (
  id             CHAR(36) PRIMARY KEY,
  repo           VARCHAR(512) NOT NULL,
  path           VARCHAR(2048) NOT NULL,
  commit_sha     CHAR(40) NOT NULL,
  language       VARCHAR(64),
  kind           ENUM('code','doc','asset') NOT NULL DEFAULT 'code',
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
CREATE INDEX idx_item_repo_path ON item(repo(191), path(191));
CREATE INDEX idx_item_archived_at ON item(archived_at);

CREATE TABLE IF NOT EXISTS event (
  id          CHAR(36) PRIMARY KEY,
  item_id     CHAR(36) NOT NULL,
  action      ENUM('ARCHIVE','RESTORE','PRUNE_REQUEST','DELETE_APPROVED') NOT NULL,
  actor       VARCHAR(256) NOT NULL,
  context     JSON NOT NULL,
  created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (item_id) REFERENCES item(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS tag (
  item_id  CHAR(36) NOT NULL,
  tag      VARCHAR(128) NOT NULL,
  PRIMARY KEY (item_id, tag),
  FOREIGN KEY (item_id) REFERENCES item(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS referent (
  item_id   CHAR(36) NOT NULL,
  ref_type  VARCHAR(32) NOT NULL,
  ref_value VARCHAR(512) NOT NULL,
  PRIMARY KEY (item_id, ref_type, ref_value),
  FOREIGN KEY (item_id) REFERENCES item(id)
) ENGINE=InnoDB;
