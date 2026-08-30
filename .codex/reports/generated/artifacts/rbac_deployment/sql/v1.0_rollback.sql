-- =====================================================
-- RBAC Schema v1.0 Rollback Script
-- Complete Rollback to Pre-Schema State (24-hour rollback window)
-- WARNING: This destroys all RBAC data. Execute only with manual confirmation.
-- =====================================================

BEGIN;

-- =====================================================
-- Part 1: Disable and Drop RLS Policies
-- =====================================================

-- Drop tenant isolation policies
DROP POLICY IF EXISTS tenant_isolation_agent_roles ON agent_role_assignments;
DROP POLICY IF EXISTS tenant_isolation_audit ON audit_log;

-- Disable RLS on tables
ALTER TABLE agent_role_assignments DISABLE ROW LEVEL SECURITY;
ALTER TABLE audit_log DISABLE ROW LEVEL SECURITY;

-- =====================================================
-- Part 2: Drop All Tables in Reverse Dependency Order
-- =====================================================

-- Drop audit log first (no FK dependencies to other tables)
DROP TABLE IF EXISTS audit_log CASCADE;

-- Drop tenant isolation rules (no FK dependencies)
DROP TABLE IF EXISTS tenant_isolation_rules CASCADE;

-- Drop agent role assignments (references agents and roles)
DROP TABLE IF EXISTS agent_role_assignments CASCADE;

-- Drop agents (no FK dependencies to other tables)
DROP TABLE IF EXISTS agents CASCADE;

-- Drop role hierarchy (references roles)
DROP TABLE IF EXISTS role_hierarchy CASCADE;

-- Drop role permissions (references roles and permissions)
DROP TABLE IF EXISTS role_permissions CASCADE;

-- Drop permissions (no FK dependencies)
DROP TABLE IF EXISTS permissions CASCADE;

-- Drop roles (no FK dependencies)
DROP TABLE IF EXISTS roles CASCADE;

-- =====================================================
-- Part 3: Drop Enum Types
-- =====================================================

DROP TYPE IF EXISTS role_tier CASCADE;
DROP TYPE IF EXISTS access_level_enum CASCADE;
DROP TYPE IF EXISTS result_enum CASCADE;

-- =====================================================
-- Part 4: Rollback Verification
-- =====================================================

-- Verify all tables are dropped
DO $$
DECLARE
  table_count INTEGER;
BEGIN
  SELECT COUNT(*)
  INTO table_count
  FROM information_schema.tables
  WHERE table_schema = 'public'
    AND table_name IN (
      'roles', 'permissions', 'role_permissions', 'role_hierarchy',
      'agents', 'agent_role_assignments', 'tenant_isolation_rules', 'audit_log'
    );
  
  IF table_count = 0 THEN
    RAISE NOTICE 'RBAC Rollback Complete: All tables successfully dropped';
  ELSE
    RAISE WARNING 'RBAC Rollback Incomplete: % tables still exist', table_count;
  END IF;
END $$;

COMMIT;
