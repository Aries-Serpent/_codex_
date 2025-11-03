-- Migration: Add standardization fields to archive tables
-- SQLite: 002_add_standardization.sql
-- Date: 2025-11-02
-- Description: Adds standardization metadata and attestation support

-- Add standardization_metadata column to item table
ALTER TABLE item ADD COLUMN standardization_metadata TEXT DEFAULT NULL;

-- Create attestation table for storing signatures
CREATE TABLE IF NOT EXISTS attestation (
  id TEXT PRIMARY KEY,
  item_id TEXT NOT NULL UNIQUE,
  signature TEXT NOT NULL,
  certificate_chain TEXT,  -- JSON array of PEM certificates
  issuer TEXT,
  signed_at TEXT NOT NULL,
  created_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY(item_id) REFERENCES item(id) ON DELETE CASCADE
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_attestation_item ON attestation(item_id);
CREATE INDEX IF NOT EXISTS idx_attestation_signed_at ON attestation(signed_at);
CREATE INDEX IF NOT EXISTS idx_attestation_issuer ON attestation(issuer);

-- Add index on standardization_metadata for future queries
CREATE INDEX IF NOT EXISTS idx_item_standardization ON item(standardization_metadata);
