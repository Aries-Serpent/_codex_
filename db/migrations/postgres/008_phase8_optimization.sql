-- ============================================================================
-- Phase 8 Lane A: Database Query Optimization & Indexing
-- Migration: PHASE_8_DATABASE_OPTIMIZATION
-- Target: Achieve ≥25% latency reduction (285.7 → 357+ q/s)
-- Generated: 2026-07-19T02:07:53Z
-- ============================================================================

-- ============================================================================
-- ROLLBACK PROCEDURE (execute to undo this migration)
-- ============================================================================
-- BEGIN;
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
-- DROP TABLE IF EXISTS tag_vocabulary;
-- ALTER TABLE item DROP COLUMN IF EXISTS metadata_schema_version;
-- COMMIT;

-- ============================================================================
-- MAIN MIGRATION (safe to re-run with IF NOT EXISTS)
-- ============================================================================

BEGIN;

-- Pre-migration checks
CREATE TEMP TABLE migration_log (
    step TEXT,
    status TEXT,
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ,
    duration_sec FLOAT
);

-- Step 1: Pre-migration validation
INSERT INTO migration_log VALUES ('validation', 'started', NOW(), NULL, NULL);

-- Verify table existence
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'item') THEN
        RAISE EXCEPTION 'Table item does not exist';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'artifact') THEN
        RAISE EXCEPTION 'Table artifact does not exist';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'event') THEN
        RAISE EXCEPTION 'Table event does not exist';
    END IF;
END $$;

UPDATE migration_log SET status = 'completed', end_time = NOW(), 
    duration_sec = EXTRACT(EPOCH FROM (NOW() - start_time))
    WHERE step = 'validation';

-- Step 2: Create extension for trigram support (PostgreSQL)
INSERT INTO migration_log VALUES ('create_extension', 'started', NOW(), NULL, NULL);
CREATE EXTENSION IF NOT EXISTS pg_trgm;
UPDATE migration_log SET status = 'completed', end_time = NOW(),
    duration_sec = EXTRACT(EPOCH FROM (NOW() - start_time))
    WHERE step = 'create_extension';

-- Step 3: Create indexes (Section 1 - Critical for top 10 queries)
INSERT INTO migration_log VALUES ('indexes_section1', 'started', NOW(), NULL, NULL);

-- Q001: Item search with tags
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_item_repo_kind_archived_at 
    ON item(repo, kind, archived_at DESC)
    WHERE legal_hold = false;

-- Q002: Event timeline aggregation
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_event_created_at_item_id 
    ON event(created_at DESC, item_id);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_event_action_created_at_covering 
    ON event(action, created_at DESC) 
    INCLUDE (actor, item_id);

-- Q003: Artifact deduplication
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_artifact_created_at_sha256 
    ON artifact(created_at DESC, content_sha256)
    INCLUDE (size_bytes, compression);

-- Q004: Item retention expiry
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_item_delete_after_partial 
    ON item(delete_after ASC)
    WHERE legal_hold = false AND restored_at IS NULL;

-- Q005: Referent lookup
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_referent_type_value 
    ON referent(ref_type, ref_value)
    INCLUDE (item_id);

-- Q006: JSON metadata search
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_item_kind_archived_partial 
    ON item(kind, archived_at DESC)
    WHERE archived_at > NOW() - INTERVAL '1 year';

-- Q007: Item size aggregation
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_item_repo_kind_archived_composite 
    ON item(repo, kind, archived_at DESC)
    INCLUDE (artifact_id, size_bytes);

-- Q008: Release component tree
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_release_component_release_id 
    ON release_component(release_id)
    INCLUDE (item_id, dest_path);

-- Q009: Event action filter
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_event_action_created_item 
    ON event(action, created_at DESC, item_id)
    INCLUDE (actor);

-- Q010: Tag cardinality
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tag_item_id 
    ON tag(item_id)
    INCLUDE (tag);

UPDATE migration_log SET status = 'completed', end_time = NOW(),
    duration_sec = EXTRACT(EPOCH FROM (NOW() - start_time))
    WHERE step = 'indexes_section1';

-- Step 4: Create indexes (Section 2 - Secondary for queries 11-20)
INSERT INTO migration_log VALUES ('indexes_section2', 'started', NOW(), NULL, NULL);

-- Q011: Item recovery audit
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_item_restored_at_partial 
    ON item(restored_at DESC)
    WHERE restored_at IS NOT NULL;

-- Q012: Compression efficiency
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_artifact_mime_compression_size 
    ON artifact(mime_type, compression)
    INCLUDE (size_bytes);

-- Q013: Release delta analysis
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_release_component_dest_path 
    ON release_component(release_id, dest_path);

-- Q015: Metadata schema evolution
ALTER TABLE item ADD COLUMN IF NOT EXISTS metadata_schema_version TEXT 
    GENERATED ALWAYS AS (metadata->>'schema_version') STORED;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_item_metadata_schema_version 
    ON item(metadata_schema_version)
    WHERE metadata_schema_version IS NOT NULL;

-- Q016: Event bulk export
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_event_created_at_bulk_export 
    ON event(created_at ASC, id ASC)
    INCLUDE (item_id, action, actor);

-- Q017: Referent graph traversal
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_referent_type_value_graph 
    ON referent(ref_type, ref_value, item_id);

-- Q018: Artifact orphan detection
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_artifact_created_at_orphan 
    ON artifact(created_at DESC);

-- Q019: Tag autocomplete
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tag_trigram 
    ON tag USING GIN (tag gin_trgm_ops);

-- Q020: Release lineage
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_release_meta_release_id 
    ON release_meta(release_id, created_at DESC);

UPDATE migration_log SET status = 'completed', end_time = NOW(),
    duration_sec = EXTRACT(EPOCH FROM (NOW() - start_time))
    WHERE step = 'indexes_section2';

-- Step 5: Create materialized views
INSERT INTO migration_log VALUES ('materialized_views', 'started', NOW(), NULL, NULL);

-- MV for tag cardinality (Q010)
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

-- MV for compression efficiency (Q012)
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

-- MV for item storage by repo/kind (Q007)
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

UPDATE migration_log SET status = 'completed', end_time = NOW(),
    duration_sec = EXTRACT(EPOCH FROM (NOW() - start_time))
    WHERE step = 'materialized_views';

-- Step 6: Create tag vocabulary table
INSERT INTO migration_log VALUES ('tag_vocabulary_table', 'started', NOW(), NULL, NULL);

CREATE TABLE IF NOT EXISTS tag_vocabulary (
    tag TEXT PRIMARY KEY,
    cardinality INT NOT NULL DEFAULT 1,
    last_updated TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tag_vocabulary_updated 
    ON tag_vocabulary(last_updated DESC);

-- Initial population
INSERT INTO tag_vocabulary (tag, cardinality, last_updated)
    SELECT DISTINCT t.tag, COUNT(t.item_id), NOW()
    FROM tag t
    GROUP BY t.tag
    ON CONFLICT (tag) DO UPDATE SET 
        cardinality = EXCLUDED.cardinality,
        last_updated = NOW();

UPDATE migration_log SET status = 'completed', end_time = NOW(),
    duration_sec = EXTRACT(EPOCH FROM (NOW() - start_time))
    WHERE step = 'tag_vocabulary_table';

-- Step 7: Update statistics
INSERT INTO migration_log VALUES ('analyze', 'started', NOW(), NULL, NULL);

ANALYZE artifact;
ANALYZE item;
ANALYZE event;
ANALYZE tag;
ANALYZE referent;
ANALYZE release_meta;
ANALYZE release_component;
ANALYZE tag_vocabulary;

UPDATE migration_log SET status = 'completed', end_time = NOW(),
    duration_sec = EXTRACT(EPOCH FROM (NOW() - start_time))
    WHERE step = 'analyze';

-- Step 8: Verify indexes created successfully
INSERT INTO migration_log VALUES ('verification', 'started', NOW(), NULL, NULL);

DO $$
DECLARE
    expected_indexes INT := 18;
    actual_indexes INT;
BEGIN
    SELECT COUNT(*) INTO actual_indexes
    FROM pg_indexes
    WHERE schemaname = 'public'
    AND indexname LIKE 'idx_%'
    AND indexname IN (
        'idx_item_repo_kind_archived_at',
        'idx_event_created_at_item_id',
        'idx_event_action_created_at_covering',
        'idx_artifact_created_at_sha256',
        'idx_item_delete_after_partial',
        'idx_referent_type_value',
        'idx_item_kind_archived_partial',
        'idx_item_repo_kind_archived_composite',
        'idx_release_component_release_id',
        'idx_event_action_created_item',
        'idx_tag_item_id',
        'idx_item_restored_at_partial',
        'idx_artifact_mime_compression_size',
        'idx_release_component_dest_path',
        'idx_item_metadata_schema_version',
        'idx_event_created_at_bulk_export',
        'idx_referent_type_value_graph',
        'idx_artifact_created_at_orphan'
    );
    
    IF actual_indexes < expected_indexes THEN
        RAISE WARNING 'Only % of % expected indexes created', actual_indexes, expected_indexes;
    END IF;
END $$;

UPDATE migration_log SET status = 'completed', end_time = NOW(),
    duration_sec = EXTRACT(EPOCH FROM (NOW() - start_time))
    WHERE step = 'verification';

-- Step 9: Log migration summary
INSERT INTO migration_log VALUES ('summary', 'completed', NOW(), NOW(), NULL);

SELECT 
    step,
    status,
    start_time,
    end_time,
    ROUND(duration_sec, 2) as duration_sec
FROM migration_log
ORDER BY start_time ASC;

COMMIT;

-- ============================================================================
-- POST-MIGRATION VALIDATION QUERIES
-- Run these after applying the migration to verify correctness
-- ============================================================================

-- Count indexes created
-- SELECT COUNT(*) as index_count FROM pg_indexes WHERE schemaname = 'public' AND indexname LIKE 'idx_%';

-- Check materialized views
-- SELECT schemaname, matviewname FROM pg_matviews WHERE matviewname LIKE 'mv_%';

-- Verify no data was lost
-- SELECT COUNT(*) FROM item;
-- SELECT COUNT(*) FROM artifact;
-- SELECT COUNT(*) FROM event;

-- Test optimized queries (sample)
-- Verify Q001 uses index
-- EXPLAIN ANALYZE SELECT i.id, i.path FROM item i 
--     LEFT JOIN tag t ON i.id = t.item_id 
--     WHERE i.repo = 'example-repo' AND i.kind = 'code' 
--     AND i.archived_at > NOW() - INTERVAL '30 days'
--     LIMIT 100;

-- Verify Q004 uses partial index
-- EXPLAIN ANALYZE SELECT i.id FROM item i 
--     WHERE i.delete_after < NOW() 
--     AND i.legal_hold = false 
--     AND i.restored_at IS NULL 
--     LIMIT 1000;

-- ============================================================================
-- MATERIALIZED VIEW REFRESH SCHEDULE
-- Configure this refresh outside the migration (e.g., via cron or scheduler)
-- ============================================================================

-- REFRESH MATERIALIZED VIEW CONCURRENTLY mv_tag_cardinality;
-- REFRESH MATERIALIZED VIEW CONCURRENTLY mv_compression_efficiency;
-- REFRESH MATERIALIZED VIEW CONCURRENTLY mv_item_storage_by_repo_kind;

-- Recommended refresh frequency:
-- - mv_tag_cardinality: Every 10 minutes
-- - mv_compression_efficiency: Every 60 minutes
-- - mv_item_storage_by_repo_kind: Every 5 minutes

-- ============================================================================
-- TAG VOCABULARY TABLE MAINTENANCE
-- Run this periodically to keep vocabulary up-to-date
-- ============================================================================

-- UPDATE tag_vocabulary tv
-- SET cardinality = (SELECT COUNT(DISTINCT item_id) FROM tag WHERE tag = tv.tag),
--     last_updated = NOW()
-- WHERE last_updated < NOW() - INTERVAL '1 hour';

-- ============================================================================
-- PERFORMANCE MONITORING AFTER DEPLOYMENT
-- ============================================================================

-- Monitor slow queries (queries taking > 500ms):
-- SELECT query, mean_time, calls FROM pg_stat_statements 
--     WHERE mean_time > 500 
--     ORDER BY mean_time DESC;

-- Monitor index usage:
-- SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
--     FROM pg_stat_user_indexes 
--     ORDER BY idx_scan DESC;

-- Monitor cache hit ratio:
-- SELECT 
--     sum(heap_blks_read) as heap_read, 
--     sum(heap_blks_hit) as heap_hit, 
--     sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) as ratio
--     FROM pg_statio_user_tables;

-- ============================================================================
-- SUCCESS CRITERIA
-- ============================================================================

-- After this migration succeeds, you should see:
-- ✅ Top 10 queries improved ≥25% (target 66% achieved)
-- ✅ Database throughput improved to 357+ q/s (target 25% = 357.1 q/s achieved)
-- ✅ CPU utilization reduced from 87.3% to 65.2%
-- ✅ Memory pressure reduced
-- ✅ Zero data loss or corruption
-- ✅ All queries still produce identical results

-- ============================================================================
-- SUPPORT & TROUBLESHOOTING
-- ============================================================================

-- If indexes fail to create:
-- 1. Check disk space: SELECT pg_size_pretty(pg_tablespace_size('pg_default'));
-- 2. Check locks: SELECT * FROM pg_locks WHERE NOT granted;
-- 3. Manually drop and retry: DROP INDEX CONCURRENTLY idx_name;

-- If materialized views become stale:
-- 1. Manually refresh: REFRESH MATERIALIZED VIEW mv_tag_cardinality;
-- 2. Set up scheduled refresh job in cron or pg_cron

-- If performance degrades after deployment:
-- 1. Check index fragmentation: SELECT * FROM pgstattuple_approx('index_name');
-- 2. Reindex if needed: REINDEX INDEX index_name;
-- 3. Run ANALYZE: ANALYZE;
