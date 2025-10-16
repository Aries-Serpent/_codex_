-- Release tracking tables (MariaDB)
CREATE TABLE IF NOT EXISTS release_meta (
  id          CHAR(36) PRIMARY KEY,
  release_id  VARCHAR(191) NOT NULL,
  version     VARCHAR(191) NOT NULL,
  created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  actor       VARCHAR(256) NOT NULL,
  metadata    JSON NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS release_component (
  id            CHAR(36) PRIMARY KEY,
  release_id    CHAR(36) NOT NULL,
  item_id       CHAR(36) NULL,
  tombstone     VARCHAR(191) NOT NULL,
  dest_path     VARCHAR(2048) NOT NULL,
  mode          VARCHAR(8) NOT NULL DEFAULT '0644',
  template_vars JSON NOT NULL,
  FOREIGN KEY (release_id) REFERENCES release_meta(id) ON DELETE CASCADE
) ENGINE=InnoDB;
