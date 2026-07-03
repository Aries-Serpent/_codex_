-- =====================================================
-- RBAC Schema Migration Verification Script
-- Tests idempotency, foreign keys, and constraint integrity
-- =====================================================

-- =====================================================
-- Section 1: Post-Migration Verification Queries
-- =====================================================

-- Verify Query 1: All roles exist
SELECT 'VERIFY_1_ROLES' as test,
       COUNT(*) as role_count,
       CASE WHEN COUNT(*) = 4 THEN 'PASS' ELSE 'FAIL' END as status
FROM roles
WHERE is_active = true;

-- Verify Query 2: Permissions count
SELECT 'VERIFY_2_PERMISSIONS' as test,
       COUNT(*) as permission_count,
       CASE WHEN COUNT(*) >= 58 THEN 'PASS' ELSE 'FAIL' END as status
FROM permissions;

-- Verify Query 3: Role hierarchy is acyclic (no cycles)
WITH RECURSIVE hierarchy AS (
  SELECT parent_role_id, child_role_id, 1 as depth
  FROM role_hierarchy
  UNION ALL
  SELECT h.parent_role_id, rh.child_role_id, h.depth + 1
  FROM hierarchy h
  JOIN role_hierarchy rh ON h.child_role_id = rh.parent_role_id
  WHERE h.depth < 10
)
SELECT 'VERIFY_3_HIERARCHY' as test,
       COUNT(*) as cycle_count,
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END as status
FROM hierarchy
WHERE parent_role_id = child_role_id;

-- Verify Query 4: Tenant isolation rules exist
SELECT 'VERIFY_4_TENANT_RULES' as test,
       COUNT(*) as tenant_rule_count,
       CASE WHEN COUNT(*) >= 1 THEN 'PASS' ELSE 'FAIL' END as status
FROM tenant_isolation_rules;

-- Verify Query 5: Foreign key constraints are valid
SELECT 'VERIFY_5_FK_CONSTRAINTS' as test,
       COUNT(*) as constraint_count,
       CASE WHEN COUNT(*) >= 8 THEN 'PASS' ELSE 'FAIL' END as status
FROM information_schema.table_constraints
WHERE constraint_type = 'FOREIGN KEY'
  AND table_schema = 'public';

-- Verify Query 6: All 8 tables exist
SELECT 'VERIFY_6_TABLES' as test,
       COUNT(*) as table_count,
       CASE WHEN COUNT(*) = 8 THEN 'PASS' ELSE 'FAIL' END as status
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN (
    'roles', 'permissions', 'role_permissions', 'role_hierarchy',
    'agents', 'agent_role_assignments', 'tenant_isolation_rules', 'audit_log'
  );

-- Verify Query 7: All 20+ indexes exist
SELECT 'VERIFY_7_INDEXES' as test,
       COUNT(*) as index_count,
       CASE WHEN COUNT(*) >= 20 THEN 'PASS' ELSE 'FAIL' END as status
FROM pg_indexes
WHERE schemaname = 'public'
  AND tablename IN (
    'roles', 'permissions', 'role_permissions', 'role_hierarchy',
    'agents', 'agent_role_assignments', 'tenant_isolation_rules', 'audit_log'
  );

-- Verify Query 8: RLS policies are enabled
SELECT 'VERIFY_8_RLS' as test,
       COUNT(*) as rls_enabled_tables,
       CASE WHEN COUNT(*) = 2 THEN 'PASS' ELSE 'FAIL' END as status
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('agent_role_assignments', 'audit_log')
  AND rowsecurity = true;

-- =====================================================
-- Section 2: Migration Idempotency Check
-- =====================================================

-- This query should run without errors if migration is idempotent
SELECT 'IDEMPOTENT_CHECK' as test,
       'READY' as status
WHERE NOT EXISTS (
  SELECT 1 FROM information_schema.constraint_column_usage
  WHERE table_schema = 'public'
    AND constraint_name LIKE 'uq_%'
    AND COUNT(*) > 1
);

-- =====================================================
-- Section 3: Schema Integrity Check
-- =====================================================

-- Check for NULL constraints on required columns
SELECT 'SCHEMA_INTEGRITY' as test,
       COUNT(*) as nullable_required_cols,
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END as status
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name IN (
    'roles', 'permissions', 'role_permissions', 'role_hierarchy',
    'agents', 'agent_role_assignments', 'tenant_isolation_rules', 'audit_log'
  )
  AND is_nullable = 'YES'
  AND column_name IN ('name', 'role_id', 'permission_id', 'agent_id', 'tenant_id');

-- =====================================================
-- Section 4: Constraint Validation
-- =====================================================

-- Verify UNIQUE constraints
SELECT 'UNIQUE_CONSTRAINTS' as test,
       constraint_name,
       table_name,
       'DEFINED' as status
FROM information_schema.table_constraints
WHERE constraint_type = 'UNIQUE'
  AND table_schema = 'public'
ORDER BY table_name;

-- Verify PRIMARY KEY constraints
SELECT 'PRIMARY_KEY_CONSTRAINTS' as test,
       COUNT(*) as pk_count,
       CASE WHEN COUNT(*) = 8 THEN 'PASS' ELSE 'FAIL' END as status
FROM information_schema.table_constraints
WHERE constraint_type = 'PRIMARY KEY'
  AND table_schema = 'public'
  AND table_name IN (
    'roles', 'permissions', 'role_permissions', 'role_hierarchy',
    'agents', 'agent_role_assignments', 'tenant_isolation_rules', 'audit_log'
  );

-- =====================================================
-- Section 5: Data Consistency Check
-- =====================================================

-- Check for orphaned permissions (permissions not assigned to any role)
SELECT 'ORPHANED_PERMISSIONS' as test,
       COUNT(*) as orphaned_count,
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'WARN' END as status
FROM permissions p
WHERE NOT EXISTS (
  SELECT 1 FROM role_permissions rp WHERE rp.permission_id = p.permission_id
);

-- Check for role hierarchy with inactive parent
SELECT 'HIERARCHY_VALIDATION' as test,
       COUNT(*) as invalid_hierarchy,
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END as status
FROM role_hierarchy rh
WHERE NOT EXISTS (
  SELECT 1 FROM roles r WHERE r.role_id = rh.parent_role_id AND r.is_active = true
)
OR NOT EXISTS (
  SELECT 1 FROM roles r WHERE r.role_id = rh.child_role_id AND r.is_active = true
);

-- =====================================================
-- Section 6: Index Coverage Report
-- =====================================================

-- Report on index performance metrics
SELECT 'INDEX_COVERAGE_REPORT' as test,
       tablename,
       indexname,
       idx_scan as scans_since_creation,
       idx_tup_read as tuples_read,
       idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
  AND tablename IN (
    'roles', 'permissions', 'role_permissions', 'role_hierarchy',
    'agents', 'agent_role_assignments', 'tenant_isolation_rules', 'audit_log'
  )
ORDER BY tablename, indexname;

-- =====================================================
-- Section 7: Migration Checklist Status
-- =====================================================

-- Overall migration status
SELECT 'MIGRATION_STATUS' as check_name,
       'SCHEMA_DEPLOYMENT' as phase,
       CASE 
         WHEN COUNT(*) >= 8 THEN 'COMPLETE'
         ELSE 'INCOMPLETE'
       END as status
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN (
    'roles', 'permissions', 'role_permissions', 'role_hierarchy',
    'agents', 'agent_role_assignments', 'tenant_isolation_rules', 'audit_log'
  );
