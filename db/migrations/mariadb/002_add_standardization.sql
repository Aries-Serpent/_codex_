-- Migration: Add standardization fields to archive tables
-- MariaDB: 002_add_standardization.sql
-- Date: 2025-11-02

-- Add standardization_metadata column to item table
ALTER TABLE item ADD COLUMN standardization_metadata JSON DEFAULT NULL;

-- Create attestation table for storing signatures
CREATE TABLE IF NOT EXISTS attestation (
  id CHAR(36) PRIMARY KEY,
  item_id CHAR(36) NOT NULL UNIQUE,
  signature LONGTEXT NOT NULL,
  certificate_chain JSON,
  issuer VARCHAR(255),
  signed_at DATETIME NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(item_id) REFERENCES item(id) ON DELETE CASCADE,
  KEY idx_attestation_item (item_id),
  KEY idx_attestation_signed_at (signed_at),
  KEY idx_attestation_issuer (issuer)
);

-- Add index on standardization_metadata
ALTER TABLE item ADD KEY idx_item_standardization (standardization_metadata(100));
