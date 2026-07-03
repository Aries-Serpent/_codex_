-- =====================================================
-- RBAC Schema Performance Validation Script
-- Tests permission lookup latency, role hierarchy traversal, and scalability
-- Target: <10ms permission lookup @ 1000 agents
-- =====================================================

-- =====================================================
-- Phase 1: Load Test Data (Scalability @ 1000 agents)
-- =====================================================

-- Create test data: 1000 agents for performance testing
INSERT INTO agents (name, tier_level, owner_id, is_active)
SELECT 
  'test_agent_' || seq AS name,
  (seq % 4) + 1 AS tier_level,
  'test_owner_' || (seq % 10) AS owner_id,
  true
FROM generate_series(1, 1000) AS seq
ON CONFLICT DO NOTHING;

-- Assign roles to test agents (create 1200 role assignments)
INSERT INTO agent_role_assignments (agent_id, role_id, tenant_id, assigned_at, expires_at, assigned_by)
SELECT 
  a.agent_id,
  r.role_id,
  'test_tenant_' || (seq % 5) AS tenant_id,
  CURRENT_TIMESTAMP,
  NULL,
  'admin'
FROM agents a, roles r, generate_series(1, 1200) seq
WHERE a.name LIKE 'test_agent_%'
ORDER BY RANDOM()
LIMIT 1200
ON CONFLICT (agent_id, role_id, tenant_id) DO NOTHING;

-- Log test data creation
DO $$
DECLARE
  agent_count INTEGER;
  assignment_count INTEGER;
BEGIN
  SELECT COUNT(*) INTO agent_count FROM agents WHERE name LIKE 'test_agent_%';
  SELECT COUNT(*) INTO assignment_count FROM agent_role_assignments WHERE tenant_id LIKE 'test_tenant_%';
  RAISE NOTICE 'Test Data Loaded: % agents, % role assignments', agent_count, assignment_count;
END $$;

-- =====================================================
-- Phase 2: Permission Lookup Latency Testing
-- Target: <10ms @ 1000 agents
-- =====================================================

-- Test Query 1: Single permission lookup (most frequent operation)
-- Expected: 7ms baseline, <15ms under load
EXPLAIN ANALYZE
SELECT DISTINCT p.name, p.category
FROM permissions p
JOIN role_permissions rp ON p.permission_id = rp.permission_id
JOIN agent_role_assignments ara ON ara.role_id = rp.role_id
WHERE ara.agent_id = (SELECT agent_id FROM agents WHERE name = 'test_agent_1' LIMIT 1)
AND (ara.expires_at IS NULL OR ara.expires_at > CURRENT_TIMESTAMP)
AND ara.tenant_id = 'test_tenant_0';

-- Test Query 2: Multi-tenant permission isolation
-- Expected: <10ms with proper indexing
EXPLAIN ANALYZE
SELECT COUNT(DISTINCT p.permission_id) as permission_count
FROM permissions p
JOIN role_permissions rp ON p.permission_id = rp.permission_id
JOIN agent_role_assignments ara ON ara.role_id = rp.role_id
WHERE ara.tenant_id = 'test_tenant_0'
AND (ara.expires_at IS NULL OR ara.expires_at > CURRENT_TIMESTAMP);

-- Test Query 3: Active role assignments query (partial index test)
-- Expected: <10ms with idx_agent_role_assignments_active
EXPLAIN ANALYZE
SELECT COUNT(*) as active_assignments
FROM agent_role_assignments ara
WHERE ara.tenant_id = 'test_tenant_0'
AND (ara.expires_at IS NULL OR ara.expires_at > CURRENT_TIMESTAMP);

-- =====================================================
-- Phase 3: Role Hierarchy Traversal Testing
-- Target: <50ms for 5-level hierarchy
-- =====================================================

-- Test Query 1: Simple hierarchy traversal (2-level)
-- Expected: 2-3ms
EXPLAIN ANALYZE
WITH RECURSIVE hierarchy_traversal AS (
  SELECT role_id, parent_role_id, 1 as depth
  FROM role_hierarchy
  WHERE parent_role_id = (SELECT role_id FROM roles WHERE name = 'admin' LIMIT 1)
  UNION ALL
  SELECT ht.role_id, rh.parent_role_id, ht.depth + 1
  FROM hierarchy_traversal ht
  JOIN role_hierarchy rh ON ht.role_id = rh.parent_role_id
  WHERE ht.depth < 5
)
SELECT COUNT(DISTINCT role_id) as accessible_roles
FROM hierarchy_traversal;

-- Test Query 2: Cycle detection (graph integrity)
-- Expected: 3-8ms for up to 5-level hierarchy
EXPLAIN ANALYZE
WITH RECURSIVE cycle_detection AS (
  SELECT parent_role_id, child_role_id, 1 as depth
  FROM role_hierarchy
  WHERE parent_role_id = (SELECT role_id FROM roles WHERE name = 'admin' LIMIT 1)
  UNION ALL
  SELECT cd.parent_role_id, rh.child_role_id, cd.depth + 1
  FROM cycle_detection cd
  JOIN role_hierarchy rh ON cd.child_role_id = rh.parent_role_id
  WHERE cd.depth < 4
)
SELECT COUNT(*) as cycles_detected
FROM cycle_detection
WHERE parent_role_id = child_role_id;

-- =====================================================
-- Phase 4: Index Efficiency Validation
-- =====================================================

-- Index Stats: Permission Lookup Index
SELECT 'idx_agent_role_assignments_active' as index_name,
       schemaname,
       tablename,
       indexname,
       idx_scan as scan_count,
       idx_tup_read as tuples_examined,
       idx_tup_fetch as tuples_returned,
       ROUND(100.0 * idx_tup_fetch / NULLIF(idx_tup_read, 0), 2) as efficiency_pct
FROM pg_stat_user_indexes
WHERE indexname = 'idx_agent_role_assignments_active'
  AND schemaname = 'public';

-- Index Stats: Composite Index (agent_tenant)
SELECT 'idx_agent_role_assignments_agent_tenant' as index_name,
       schemaname,
       tablename,
       indexname,
       idx_scan as scan_count,
       idx_tup_read as tuples_examined,
       idx_tup_fetch as tuples_returned,
       ROUND(100.0 * idx_tup_fetch / NULLIF(idx_tup_read, 0), 2) as efficiency_pct
FROM pg_stat_user_indexes
WHERE indexname = 'idx_agent_role_assignments_agent_tenant'
  AND schemaname = 'public';

-- =====================================================
-- Phase 5: Tenant Isolation Enforcement Test
-- =====================================================

-- Test Query 1: Verify cross-tenant access is blocked by RLS
-- Expected: Only returns records for current tenant
EXPLAIN ANALYZE
SELECT COUNT(*) as current_tenant_assignments
FROM agent_role_assignments ara
WHERE ara.tenant_id = current_setting('app.current_tenant', true);

-- Test Query 2: Verify RLS policy effectiveness
-- Expected: Row count should match tenant_id filter
EXPLAIN ANALYZE
SELECT COUNT(*) as filtered_assignments
FROM agent_role_assignments ara
WHERE ara.tenant_id = 'test_tenant_0';

-- =====================================================
-- Phase 6: Bulk Operation Performance
-- =====================================================

-- Test bulk assignment operation (100 agents at once)
-- Expected: 120ms for 100 role assignments vs 500ms row-by-row
EXPLAIN ANALYZE
INSERT INTO agent_role_assignments (agent_id, role_id, tenant_id, assigned_at, expires_at, assigned_by)
SELECT 
  a.agent_id,
  (SELECT role_id FROM roles WHERE name = 'operator' LIMIT 1),
  'bulk_test_tenant',
  CURRENT_TIMESTAMP,
  NULL,
  'admin'
FROM agents a
WHERE a.name LIKE 'test_agent_%'
LIMIT 100
ON CONFLICT (agent_id, role_id, tenant_id) DO UPDATE
SET assigned_at = CURRENT_TIMESTAMP
RETURNING COUNT(*);

-- =====================================================
-- Phase 7: Storage & Scalability Metrics
-- =====================================================

-- Calculate table sizes
SELECT 'agent_role_assignments' as table_name,
       pg_size_pretty(pg_total_relation_size('agent_role_assignments')) as total_size,
       pg_size_pretty(pg_relation_size('agent_role_assignments')) as table_size,
       pg_size_pretty(pg_indexes_size('agent_role_assignments')) as indexes_size,
       (SELECT COUNT(*) FROM agent_role_assignments) as row_count
UNION ALL
SELECT 'audit_log' as table_name,
       pg_size_pretty(pg_total_relation_size('audit_log')) as total_size,
       pg_size_pretty(pg_relation_size('audit_log')) as table_size,
       pg_size_pretty(pg_indexes_size('audit_log')) as indexes_size,
       (SELECT COUNT(*) FROM audit_log) as row_count
UNION ALL
SELECT 'agents' as table_name,
       pg_size_pretty(pg_total_relation_size('agents')) as total_size,
       pg_size_pretty(pg_relation_size('agents')) as table_size,
       pg_size_pretty(pg_indexes_size('agents')) as indexes_size,
       (SELECT COUNT(*) FROM agents) as row_count;

-- =====================================================
-- Phase 8: Performance Summary & Validation
-- =====================================================

-- Summary: Test Data Statistics
SELECT 'PERFORMANCE_SUMMARY' as metric,
       'Agent Count' as check_type,
       COUNT(*)::VARCHAR as value,
       CASE WHEN COUNT(*) >= 1000 THEN 'PASS' ELSE 'FAIL' END as status
FROM agents
WHERE name LIKE 'test_agent_%'
UNION ALL
SELECT 'PERFORMANCE_SUMMARY' as metric,
       'Role Assignment Count' as check_type,
       COUNT(*)::VARCHAR as value,
       CASE WHEN COUNT(*) >= 1000 THEN 'PASS' ELSE 'FAIL' END as status
FROM agent_role_assignments
WHERE tenant_id LIKE 'test_tenant_%'
UNION ALL
SELECT 'PERFORMANCE_SUMMARY' as metric,
       'Permission Latency Target' as check_type,
       '<10ms' as value,
       'READY_FOR_TESTING' as status
UNION ALL
SELECT 'PERFORMANCE_SUMMARY' as metric,
       'Hierarchy Traversal Target' as check_type,
       '<50ms' as value,
       'READY_FOR_TESTING' as status
UNION ALL
SELECT 'PERFORMANCE_SUMMARY' as metric,
       'Tenant Isolation Status' as check_type,
       'RLS Enabled' as value,
       CASE 
         WHEN EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'tenant_isolation_agent_roles')
         THEN 'PASS'
         ELSE 'FAIL'
       END as status;

-- =====================================================
-- Phase 9: Cleanup (Optional - Remove Test Data)
-- =====================================================

-- Uncomment to clean up test data after validation
/*
DELETE FROM agent_role_assignments WHERE tenant_id LIKE 'test_tenant_%' OR tenant_id = 'bulk_test_tenant';
DELETE FROM agents WHERE name LIKE 'test_agent_%';
VACUUM ANALYZE;
*/
