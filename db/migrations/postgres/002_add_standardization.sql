-- Migration: Add standardization fields to archive tables
-- PostgreSQL: 002_add_standardization.sql
-- Date: 2025-11-02

-- Add standardization_metadata column to item table
ALTER TABLE item ADD COLUMN standardization_metadata JSONB DEFAULT NULL;

-- Create attestation table for storing signatures
CREATE TABLE IF NOT EXISTS attestation (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  item_id UUID NOT NULL UNIQUE REFERENCES item(id) ON DELETE CASCADE,
  signature TEXT NOT NULL,
  certificate_chain JSONB,  -- JSON array of PEM certificates
  issuer TEXT,
  signed_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_attestation_item ON attestation(item_id);
CREATE INDEX IF NOT EXISTS idx_attestation_signed_at ON attestation(signed_at);
CREATE INDEX IF NOT EXISTS idx_attestation_issuer ON attestation(issuer);

-- Add GIN index on JSONB for efficient queries
CREATE INDEX IF NOT EXISTS idx_item_standardization_metadata ON item USING GIN(standardization_metadata);
