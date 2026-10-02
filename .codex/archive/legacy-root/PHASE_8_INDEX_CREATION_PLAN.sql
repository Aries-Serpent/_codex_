-- ============================================================================
-- Phase 8 Lane A: Database Query Optimization & Indexing
-- Index Creation Plan for PostgreSQL, MariaDB, and SQLite
-- Generated: 2026-07-19T02:07:53Z
-- Target: ≥25% latency reduction, 285.7 → 357+ q/s throughput
-- ============================================================================

-- PostgreSQL-specific indexes and optimizations
-- Run this migration to optimize Phase 7 slow queries

BEGIN;

-- ============================================================================
-- SECTION 1: CRITICAL INDEXES FOR TOP 10 SLOWEST QUERIES
-- Priority: Implement first; estimated 65% improvement on top 10 queries
-- ============================================================================

-- Q001: Item search with tags
-- Current latency: 847.3ms → Target: 322ms (62% improvement)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_item_repo_kind_archived_at 
    ON item(repo, kind, archived_at DESC)
    WHERE legal_hold = false;

-- Q002: Event timeline aggregation
-- Current latency: 634.2ms → Target: 184ms (71% improvement)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_event_created_at_item_id 
    ON event(created_at DESC, item_id);

-- Covering index for event aggregation (excludes context JSONB)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_event_action_created_at_covering 
    ON event(action, created_at DESC) 
    INCLUDE (actor, item_id);

-- Q003: Artifact deduplication lookup
-- Current latency: 521.8ms → Target: 219.4ms (58% improvement)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_artifact_created_at_sha256 
    ON artifact(created_at DESC, content_sha256)
    INCLUDE (size_bytes, compression);

-- Q004: Item retention expiry check
-- Current latency: 412.1ms → Target: 90.5ms (78% improvement)
-- PARTIAL INDEX: Only for items that can be deleted
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_item_delete_after_partial 
    ON item(delete_after ASC)
    WHERE legal_hold = false AND restored_at IS NULL;

-- Q005: Referent lookup
-- Current latency: 398.5ms → Target: 127.5ms (68% improvement)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_referent_type_value 
    ON referent(ref_type, ref_value)
    INCLUDE (item_id);

-- Q006: JSON metadata search
-- Current latency: 376.2ms → Target: 169.3ms (55% improvement)
-- Already has GIN index on metadata; add partial index for common patterns
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_item_kind_archived_partial 
    ON item(kind, archived_at DESC)
    WHERE archived_at > NOW() - INTERVAL '1 year';

-- Q007: Item size aggregation
-- Current latency: 354.3ms → Target: 99.2ms (72% improvement)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_item_repo_kind_archived_composite 
    ON item(repo, kind, archived_at DESC)
    INCLUDE (artifact_id, size_bytes);

-- Q008: Release component tree
-- Current latency: 287.5ms → Target: 97.8ms (66% improvement)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_release_component_release_id 
    ON release_component(release_id)
    INCLUDE (item_id, dest_path);

-- Q009: Event action filter
-- Current latency: 267.3ms → Target: 69.5ms (74% improvement)
-- Composite index with action in leading position for filter
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_event_action_created_item 
    ON event(action, created_at DESC, item_id)
    INCLUDE (actor);

-- Q010: Tag cardinality analysis
-- Current latency: 245.6ms → Target: 98.2ms (60% improvement)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tag_item_id 
    ON tag(item_id)
    INCLUDE (tag);

-- ============================================================================
-- SECTION 2: SECONDARY INDEXES FOR QUERIES 11-20
-- Priority: Implement after Section 1; estimated 60% improvement on queries 11-20
-- ============================================================================

-- Q011: Item recovery audit
-- Current latency: 198.7ms → Target: 69.5ms (65% improvement)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_item_restored_at_partial 
    ON item(restored_at DESC)
    WHERE restored_at IS NOT NULL;

-- Q012: Compression efficiency
-- Current latency: 156.4ms → Target: 45.4ms (71% improvement)
-- Exclude blob_bytes from index (use covering index for size info)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_artifact_mime_compression_size 
    ON artifact(mime_type, compression)
    INCLUDE (size_bytes);

-- Q013: Release delta analysis
-- Current latency: 134.2ms → Target: 60.4ms (55% improvement)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_release_component_dest_path 
    ON release_component(release_id, dest_path);

-- Q014: Item corruption check (anti-join optimization)
-- Current latency: 123.5ms → Target: 64.2ms (48% improvement)
-- This is better handled with LEFT JOIN + IS NULL; no index needed beyond PK

-- Q015: Metadata schema evolution
-- Current latency: 98.3ms → Target: 47.2ms (52% improvement)
-- Add generated column to extract schema_version for regular indexing
ALTER TABLE item ADD COLUMN IF NOT EXISTS metadata_schema_version TEXT 
    GENERATED ALWAYS AS (metadata->>'schema_version') STORED;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_item_metadata_schema_version 
    ON item(metadata_schema_version)
    WHERE metadata_schema_version IS NOT NULL;

-- Q016: Event bulk export
-- Current latency: 87.6ms → Target: 34.2ms (61% improvement)
-- Covering index to avoid fetching context JSONB
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_event_created_at_bulk_export 
    ON event(created_at ASC, id ASC)
    INCLUDE (item_id, action, actor);

-- Q017: Referent graph traversal
-- Current latency: 76.4ms → Target: 31.4ms (59% improvement)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_referent_type_value_graph 
    ON referent(ref_type, ref_value, item_id);

-- Q018: Artifact orphan detection
-- Current latency: 67.8ms → Target: 29.1ms (57% improvement)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_artifact_created_at_orphan 
    ON artifact(created_at DESC);

-- Q019: Tag autocomplete (STRING PATTERN OPTIMIZATION)
-- Current latency: 54.3ms → Target: 8.7ms (84% improvement)
-- PostgreSQL-specific: trigram extension for LIKE optimization
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tag_trigram 
    ON tag USING GIN (tag gin_trgm_ops);

-- Alternative: Create a separate tag vocabulary table for better performance
CREATE TABLE IF NOT EXISTS tag_vocabulary (
    tag TEXT PRIMARY KEY,
    cardinality INT NOT NULL DEFAULT 1,
    last_updated TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tag_vocabulary_updated 
    ON tag_vocabulary(last_updated DESC);

-- Q020: Release lineage
-- Current latency: 43.2ms → Target: 14.7ms (66% improvement)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_release_meta_release_id 
    ON release_meta(release_id, created_at DESC);

-- ============================================================================
-- SECTION 3: MATERIALIZED VIEW INDEXES (for heavy aggregations)
-- Purpose: Pre-compute expensive aggregations; refresh on schedule
-- ============================================================================

-- Materialized view for tag cardinality (Q010)
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_tag_cardinality AS
    SELECT 
        t.tag,
        COUNT(t.item_id) as cardinality,
        COUNT(DISTINCT i.repo) as repo_count,
        MAX(i.archived_at) as most_recent_archive
    FROM tag t
    JOIN item i ON t.item_id = i.id
    GROUP BY t.tag;

CREATE INDEX IF NOT EXISTS idx_mv_tag_cardinality_card 
    ON mv_tag_cardinality(cardinality DESC);

-- Materialized view for compression efficiency (Q012)
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_compression_efficiency AS
    SELECT 
        mime_type,
        compression,
        COUNT(*) as artifact_count,
        SUM(size_bytes) as original_total_bytes,
        ROUND(100.0 * (1.0 - AVG(CASE 
            WHEN blob_bytes IS NOT NULL THEN octet_length(blob_bytes)::float / size_bytes
            ELSE 1.0 
        END)), 2) as compression_ratio_percent
    FROM artifact
    WHERE blob_bytes IS NOT NULL
    GROUP BY mime_type, compression;

CREATE INDEX IF NOT EXISTS idx_mv_compression_ratio 
    ON mv_compression_efficiency(compression_ratio_percent DESC);

-- Materialized view for item size by repo/kind (Q007)
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_item_storage_by_repo_kind AS
    SELECT 
        i.repo,
        i.kind,
        COUNT(*) as item_count,
        SUM(a.size_bytes) as total_size_bytes,
        ROUND(AVG(a.size_bytes), 2) as avg_size_bytes,
        MIN(i.archived_at) as oldest_archive,
        MAX(i.archived_at) as newest_archive
    FROM item i
    JOIN artifact a ON i.artifact_id = a.id
    WHERE i.archived_at > NOW() - INTERVAL '90 days'
    GROUP BY i.repo, i.kind;

CREATE INDEX IF NOT EXISTS idx_mv_storage_total_size 
    ON mv_item_storage_by_repo_kind(total_size_bytes DESC);

CREATE INDEX IF NOT EXISTS idx_mv_storage_repo_kind 
    ON mv_item_storage_by_repo_kind(repo, kind);

-- ============================================================================
-- SECTION 4: OPTIMIZATION HINTS & STATISTICS
-- ============================================================================

-- Update table statistics for query planner
ANALYZE artifact;
ANALYZE item;
ANALYZE event;
ANALYZE tag;
ANALYZE referent;
ANALYZE release_meta;
ANALYZE release_component;

-- ============================================================================
-- SECTION 5: CONNECTION POOLING & QUERY CACHE CONFIGURATION
-- ============================================================================

-- Set work_mem for GROUP BY operations (adjust based on available RAM)
SET work_mem = '256MB';

-- Enable parallel query execution for large scans
SET max_parallel_workers_per_gather = 4;
SET max_parallel_workers = 8;

-- ============================================================================
-- SECTION 6: MariaDB-specific indexes (MySQL 8.0+ compatible)
-- Run this section if using MariaDB/MySQL instead of PostgreSQL
-- ============================================================================

-- CREATE INDEX idx_item_repo_kind_archived_at ON item(repo, kind, archived_at DESC) WHERE legal_hold = 0;
-- CREATE INDEX idx_event_created_at_item_id ON event(created_at DESC, item_id);
-- CREATE INDEX idx_artifact_created_at_sha256 ON artifact(created_at DESC, content_sha256);
-- CREATE INDEX idx_item_delete_after_partial ON item(delete_after ASC, legal_hold, restored_at);
-- CREATE INDEX idx_referent_type_value ON referent(ref_type, ref_value);
-- CREATE INDEX idx_item_kind_archived_partial ON item(kind, archived_at DESC);
-- CREATE INDEX idx_item_repo_kind_archived_composite ON item(repo, kind, archived_at DESC);
-- CREATE INDEX idx_release_component_release_id ON release_component(release_id);
-- CREATE INDEX idx_event_action_created_item ON event(action, created_at DESC, item_id);
-- CREATE INDEX idx_tag_item_id ON tag(item_id);
-- CREATE INDEX idx_item_restored_at_partial ON item(restored_at DESC) WHERE restored_at IS NOT NULL;
-- CREATE INDEX idx_artifact_mime_compression_size ON artifact(mime_type, compression);
-- CREATE INDEX idx_release_component_dest_path ON release_component(release_id, dest_path);
-- CREATE INDEX idx_event_created_at_bulk_export ON event(created_at ASC, id ASC);
-- CREATE INDEX idx_referent_type_value_graph ON referent(ref_type, ref_value, item_id);
-- CREATE INDEX idx_artifact_created_at_orphan ON artifact(created_at DESC);
-- CREATE INDEX idx_tag_trigram ON tag(tag);  -- Use FULLTEXT for LIKE optimization
-- CREATE INDEX idx_release_meta_release_id ON release_meta(release_id, created_at DESC);

-- ============================================================================
-- SECTION 7: SQLite-specific indexes
-- Run this section if using SQLite (simplified, no INCLUDE clause)
-- ============================================================================

-- CREATE INDEX IF NOT EXISTS idx_item_repo_kind_archived_at ON item(repo, kind, archived_at DESC);
-- CREATE INDEX IF NOT EXISTS idx_event_created_at_item_id ON event(created_at DESC, item_id);
-- CREATE INDEX IF NOT EXISTS idx_artifact_created_at_sha256 ON artifact(created_at DESC, content_sha256);
-- CREATE INDEX IF NOT EXISTS idx_item_delete_after_partial ON item(delete_after ASC);
-- CREATE INDEX IF NOT EXISTS idx_referent_type_value ON referent(ref_type, ref_value);
-- CREATE INDEX IF NOT EXISTS idx_item_kind_archived_partial ON item(kind, archived_at DESC);
-- CREATE INDEX IF NOT EXISTS idx_release_component_release_id ON release_component(release_id);
-- CREATE INDEX IF NOT EXISTS idx_event_action_created_item ON event(action, created_at DESC, item_id);
-- CREATE INDEX IF NOT EXISTS idx_tag_item_id ON tag(item_id);
-- CREATE INDEX IF NOT EXISTS idx_item_restored_at_partial ON item(restored_at DESC);
-- CREATE INDEX IF NOT EXISTS idx_artifact_mime_compression_size ON artifact(mime_type, compression);
-- CREATE INDEX IF NOT EXISTS idx_release_component_dest_path ON release_component(release_id, dest_path);
-- CREATE INDEX IF NOT EXISTS idx_event_created_at_bulk_export ON event(created_at ASC, id ASC);
-- CREATE INDEX IF NOT EXISTS idx_referent_type_value_graph ON referent(ref_type, ref_value, item_id);
-- CREATE INDEX IF NOT EXISTS idx_artifact_created_at_orphan ON artifact(created_at DESC);
-- CREATE INDEX IF NOT EXISTS idx_release_meta_release_id ON release_meta(release_id, created_at DESC);

COMMIT;

-- ============================================================================
-- SECTION 8: VERIFICATION & VALIDATION QUERIES
-- Run these queries to verify index effectiveness
-- ============================================================================

-- Check index creation status
-- SELECT schemaname, tablename, indexname, indexdef FROM pg_indexes ORDER BY tablename, indexname;

-- Estimate index sizes
-- SELECT schemaname, tablename, indexname, pg_size_pretty(pg_relation_size(indexrelid)) as size 
-- FROM pg_indexes JOIN pg_class ON indexname = relname ORDER BY pg_relation_size(indexrelid) DESC;

-- Find unused indexes
-- SELECT schemaname, tablename, indexname FROM pg_stat_user_indexes WHERE idx_scan = 0;

-- ============================================================================
-- SECTION 9: QUERY OPTIMIZATION RECOMMENDATIONS (Non-DDL)
-- ============================================================================

-- 1. DENORMALIZATION STRATEGY
-- For high-volume queries, consider denormalizing frequently accessed columns:
--   - Add tag_count to item table (update on tag insert/delete)
--   - Store recent_action timestamp in item for event filtering
--   - Denormalize item.repo, item.path into event for JOIN elimination

-- 2. BATCH LOADING STRATEGY
-- Replace N+1 queries with batch loading:
--   SELECT * FROM item WHERE id = ANY($1)  -- Instead of multiple single lookups

-- 3. PAGINATION STRATEGY
-- For large result sets, implement cursor-based pagination:
--   SELECT * FROM item WHERE repo = $1 AND id > $last_id ORDER BY id LIMIT 100

-- 4. CACHING STRATEGY
-- Implement Redis/Memcached for high-frequency queries:
--   - Tag autocomplete (ttl: 24 hours)
--   - Release lineage (ttl: 1 hour)
--   - Tag cardinality (ttl: 1 hour)

-- 5. CONNECTION POOLING
-- Use PgBouncer or similar to maintain connection pool:
--   - Pool mode: transaction
--   - max_client_conn: 1000
--   - default_pool_size: 25

-- ============================================================================
-- PERFORMANCE TARGETS (Post-optimization)
-- ============================================================================

-- Expected improvements after applying all optimizations:
-- - Q001: 847.3ms → 322ms (62% improvement)
-- - Q002: 634.2ms → 184ms (71% improvement)
-- - Q003: 521.8ms → 219.4ms (58% improvement)
-- - Q004: 412.1ms → 90.5ms (78% improvement)
-- - Q005: 398.5ms → 127.5ms (68% improvement)
-- - Q006: 376.2ms → 169.3ms (55% improvement)
-- - Q007: 354.3ms → 99.2ms (72% improvement)
-- - Q008: 287.5ms → 97.8ms (66% improvement)
-- - Q009: 267.3ms → 69.5ms (74% improvement)
-- - Q010: 245.6ms → 98.2ms (60% improvement)
--
-- Aggregate improvement (Top 10): 65.8% reduction
-- Estimated database throughput: 285.7 q/s → 357+ q/s (25%+ improvement)

-- ============================================================================
-- ROLLBACK STRATEGY
-- ============================================================================

-- To rollback all optimizations, execute:
-- DROP INDEX CONCURRENTLY IF EXISTS idx_item_repo_kind_archived_at;
-- DROP INDEX CONCURRENTLY IF EXISTS idx_event_created_at_item_id;
-- DROP INDEX CONCURRENTLY IF EXISTS idx_event_action_created_at_covering;
-- DROP INDEX CONCURRENTLY IF EXISTS idx_artifact_created_at_sha256;
-- DROP INDEX CONCURRENTLY IF EXISTS idx_item_delete_after_partial;
-- DROP INDEX CONCURRENTLY IF EXISTS idx_referent_type_value;
-- DROP INDEX CONCURRENTLY IF EXISTS idx_item_kind_archived_partial;
-- DROP INDEX CONCURRENTLY IF EXISTS idx_item_repo_kind_archived_composite;
-- DROP INDEX CONCURRENTLY IF EXISTS idx_release_component_release_id;
-- DROP INDEX CONCURRENTLY IF EXISTS idx_event_action_created_item;
-- DROP INDEX CONCURRENTLY IF EXISTS idx_tag_item_id;
-- DROP INDEX CONCURRENTLY IF EXISTS idx_item_restored_at_partial;
-- DROP INDEX CONCURRENTLY IF EXISTS idx_artifact_mime_compression_size;
-- DROP INDEX CONCURRENTLY IF EXISTS idx_release_component_dest_path;
-- DROP INDEX CONCURRENTLY IF EXISTS idx_item_metadata_schema_version;
-- DROP INDEX CONCURRENTLY IF EXISTS idx_event_created_at_bulk_export;
-- DROP INDEX CONCURRENTLY IF EXISTS idx_referent_type_value_graph;
-- DROP INDEX CONCURRENTLY IF EXISTS idx_artifact_created_at_orphan;
-- DROP INDEX CONCURRENTLY IF EXISTS idx_tag_trigram;
-- DROP INDEX CONCURRENTLY IF EXISTS idx_release_meta_release_id;
-- DROP MATERIALIZED VIEW IF EXISTS mv_tag_cardinality;
-- DROP MATERIALIZED VIEW IF EXISTS mv_compression_efficiency;
-- DROP MATERIALIZED VIEW IF EXISTS mv_item_storage_by_repo_kind;
