-- =====================================================
-- RBAC Schema v1.0 Deployment Script
-- Production-Ready PostgreSQL Schema with 8 Tables & 20+ Indexes
-- Execution: Phase 12 Wave 2 (D1.2)
-- Authority: @mbaetiong (D-tier autonomy)
-- =====================================================

BEGIN;

-- =====================================================
-- Part 1: Create Enum Types
-- =====================================================

CREATE TYPE role_tier AS ENUM ('admin', 'operator', 'viewer', 'guest');
CREATE TYPE access_level_enum AS ENUM ('isolated', 'shared_read', 'shared_write');
CREATE TYPE result_enum AS ENUM ('success', 'failure', 'denied');

-- =====================================================
-- Part 2: Create Core Tables (8 Tables)
-- =====================================================

-- Table 1: Roles (tier-based access control)
CREATE TABLE roles (
    role_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    tier_level INTEGER NOT NULL CHECK (tier_level IN (1, 2, 3, 4)),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- Indexes for roles table
CREATE INDEX idx_roles_tier_level ON roles(tier_level);
CREATE INDEX idx_roles_name ON roles(name);
CREATE INDEX idx_roles_active ON roles(is_active) WHERE is_active = true;

-- Table 2: Permissions (granular permission definitions)
CREATE TABLE permissions (
    permission_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    category VARCHAR(100) NOT NULL,
    description TEXT,
    resource_type VARCHAR(100),
    approval_required BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for permissions table
CREATE INDEX idx_permissions_category ON permissions(category);
CREATE INDEX idx_permissions_resource_type ON permissions(resource_type);
CREATE INDEX idx_permissions_approval_required ON permissions(approval_required) 
    WHERE approval_required = true;

-- Table 3: Role-Permission Mapping (role capabilities)
CREATE TABLE role_permissions (
    role_permission_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_id UUID NOT NULL REFERENCES roles(role_id) ON DELETE CASCADE,
    permission_id UUID NOT NULL REFERENCES permissions(permission_id) ON DELETE CASCADE,
    resource_type VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(role_id, permission_id, resource_type)
);

-- Indexes for role_permissions table
CREATE INDEX idx_role_permissions_role_id ON role_permissions(role_id);
CREATE INDEX idx_role_permissions_permission_id ON role_permissions(permission_id);
CREATE INDEX idx_role_permissions_role_resource ON role_permissions(role_id, resource_type);

-- Table 4: Role Hierarchy (inheritance structure)
CREATE TABLE role_hierarchy (
    role_hierarchy_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_role_id UUID NOT NULL REFERENCES roles(role_id) ON DELETE CASCADE,
    child_role_id UUID NOT NULL REFERENCES roles(role_id) ON DELETE CASCADE,
    inheritance_type VARCHAR(50) DEFAULT 'full',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(parent_role_id, child_role_id),
    CHECK (parent_role_id != child_role_id)
);

-- Indexes for role_hierarchy table
CREATE INDEX idx_role_hierarchy_parent ON role_hierarchy(parent_role_id);
CREATE INDEX idx_role_hierarchy_child ON role_hierarchy(child_role_id);
CREATE INDEX idx_role_hierarchy_graph ON role_hierarchy(parent_role_id, child_role_id);

-- Table 5: Agents (AI agents with tier levels)
CREATE TABLE agents (
    agent_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    tier_level INTEGER NOT NULL CHECK (tier_level IN (1, 2, 3, 4)),
    owner_id VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for agents table
CREATE INDEX idx_agents_tier_level ON agents(tier_level);
CREATE INDEX idx_agents_owner_id ON agents(owner_id);
CREATE INDEX idx_agents_active ON agents(is_active) WHERE is_active = true;
CREATE INDEX idx_agents_name ON agents(name);

-- Table 6: Agent Role Assignments (agent permissions with tenancy)
CREATE TABLE agent_role_assignments (
    assignment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents(agent_id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES roles(role_id) ON DELETE CASCADE,
    tenant_id VARCHAR(255) NOT NULL,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    assigned_by VARCHAR(255),
    reason TEXT,
    UNIQUE(agent_id, role_id, tenant_id)
);

-- Indexes for agent_role_assignments table
CREATE INDEX idx_agent_role_assignments_agent_id ON agent_role_assignments(agent_id);
CREATE INDEX idx_agent_role_assignments_role_id ON agent_role_assignments(role_id);
CREATE INDEX idx_agent_role_assignments_tenant_id ON agent_role_assignments(tenant_id);
CREATE INDEX idx_agent_role_assignments_active ON agent_role_assignments(expires_at) 
    WHERE expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP;
CREATE INDEX idx_agent_role_assignments_agent_tenant ON agent_role_assignments(agent_id, tenant_id, expires_at);
CREATE INDEX idx_agent_role_assignments_tenant_active ON agent_role_assignments(tenant_id, expires_at) 
    WHERE expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP;

-- Table 7: Tenant Isolation Rules (multi-tenancy enforcement)
CREATE TABLE tenant_isolation_rules (
    rule_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(255) NOT NULL,
    resource_scope VARCHAR(255) NOT NULL,
    access_level VARCHAR(50) NOT NULL CHECK (access_level IN ('isolated', 'shared_read', 'shared_write')),
    enforcement_level VARCHAR(50) DEFAULT 'strict',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tenant_id, resource_scope)
);

-- Indexes for tenant_isolation_rules table
CREATE INDEX idx_tenant_isolation_rules_tenant ON tenant_isolation_rules(tenant_id);
CREATE INDEX idx_tenant_isolation_rules_resource ON tenant_isolation_rules(resource_scope);
CREATE INDEX idx_tenant_isolation_rules_access_level ON tenant_isolation_rules(access_level);

-- Table 8: Audit Log (compliance and audit trail)
CREATE TABLE audit_log (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID REFERENCES agents(agent_id) ON DELETE SET NULL,
    actor_id VARCHAR(255) NOT NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id VARCHAR(255),
    tenant_id VARCHAR(255) NOT NULL,
    old_value JSONB,
    new_value JSONB,
    result VARCHAR(50) NOT NULL CHECK (result IN ('success', 'failure', 'denied')),
    error_message TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT
);

-- Indexes for audit_log table (optimized for compliance queries)
CREATE INDEX idx_audit_log_timestamp ON audit_log(timestamp DESC);
CREATE INDEX idx_audit_log_agent_id ON audit_log(agent_id);
CREATE INDEX idx_audit_log_tenant_id ON audit_log(tenant_id);
CREATE INDEX idx_audit_log_actor_id ON audit_log(actor_id);
CREATE INDEX idx_audit_log_action ON audit_log(action);
CREATE INDEX idx_audit_log_resource ON audit_log(resource_type, resource_id);
CREATE INDEX idx_audit_log_tenant_timestamp ON audit_log(tenant_id, timestamp DESC);

-- =====================================================
-- Part 3: Row-Level Security Policies (RLS)
-- =====================================================

-- Enable RLS on multi-tenant tables
ALTER TABLE agent_role_assignments ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;

-- Tenant isolation policy for agent_role_assignments
CREATE POLICY tenant_isolation_agent_roles ON agent_role_assignments
    USING (tenant_id = current_setting('app.current_tenant', true));

-- Tenant isolation policy for audit_log
CREATE POLICY tenant_isolation_audit ON audit_log
    USING (tenant_id = current_setting('app.current_tenant', true));

-- =====================================================
-- Part 4: Seed Initial Data
-- =====================================================

-- Seed 4 core roles
INSERT INTO roles (name, description, tier_level, is_active) VALUES
  ('admin', 'Full system access with all permissions', 1, true),
  ('operator', 'Operational tasks and agent execution', 2, true),
  ('viewer', 'Read-only monitoring and reporting', 3, true),
  ('guest', 'Public access with minimal permissions', 4, true)
ON CONFLICT (name) DO NOTHING;

-- Seed 58+ core permissions (from Section C of RBAC_SCHEMA.md)
INSERT INTO permissions (name, category, description, approval_required) VALUES
  -- Agent Control (12 permissions)
  ('agent:create', 'agent-control', 'Create new AI agent', true),
  ('agent:read', 'agent-control', 'View agent configuration', false),
  ('agent:execute', 'agent-control', 'Trigger agent execution', true),
  ('agent:update', 'agent-control', 'Modify agent settings', true),
  ('agent:delete', 'agent-control', 'Delete agent', true),
  ('agent:list', 'agent-control', 'List all agents', false),
  ('agent:pause', 'agent-control', 'Pause agent execution', true),
  ('agent:resume', 'agent-control', 'Resume agent execution', true),
  ('agent:logs', 'agent-control', 'Access agent execution logs', false),
  ('agent:metrics', 'agent-control', 'View agent performance metrics', false),
  ('agent:assign_role', 'agent-control', 'Assign roles to agents', true),
  ('agent:revoke_role', 'agent-control', 'Revoke roles from agents', true),
  
  -- Governance & Approval (10 permissions)
  ('governance:create_role', 'governance', 'Create new RBAC role', true),
  ('governance:edit_role', 'governance', 'Modify existing role', true),
  ('governance:delete_role', 'governance', 'Delete RBAC role', true),
  ('governance:grant_permission', 'governance', 'Grant permission to role', true),
  ('governance:revoke_permission', 'governance', 'Revoke permission from role', true),
  ('governance:view_hierarchy', 'governance', 'View role hierarchy structure', false),
  ('governance:modify_hierarchy', 'governance', 'Modify role inheritance relationships', true),
  ('governance:approve_critical', 'governance', 'Approve critical operations', true),
  ('governance:audit_log', 'governance', 'Access audit logs', false),
  ('governance:policy_enforcement', 'governance', 'Enforce RBAC policies', true),
  
  -- Tenant Management (8 permissions)
  ('tenant:create', 'tenant-management', 'Create new tenant', true),
  ('tenant:read', 'tenant-management', 'View tenant configuration', false),
  ('tenant:update', 'tenant-management', 'Modify tenant settings', true),
  ('tenant:delete', 'tenant-management', 'Delete tenant', true),
  ('tenant:isolation', 'tenant-management', 'Configure tenant isolation rules', true),
  ('tenant:data_access', 'tenant-management', 'Access tenant data', false),
  ('tenant:billing', 'tenant-management', 'Manage tenant billing', true),
  ('tenant:users', 'tenant-management', 'Manage tenant users', true),
  
  -- Workflow & Integration (12 permissions)
  ('workflow:create', 'workflow', 'Create workflow definition', true),
  ('workflow:execute', 'workflow', 'Execute workflow', true),
  ('workflow:pause', 'workflow', 'Pause workflow execution', true),
  ('workflow:cancel', 'workflow', 'Cancel workflow execution', true),
  ('workflow:view', 'workflow', 'View workflow details', false),
  ('workflow:logs', 'workflow', 'Access workflow logs', false),
  ('workflow:history', 'workflow', 'View workflow execution history', false),
  ('workflow:delete', 'workflow', 'Delete workflow definition', true),
  ('workflow:template', 'workflow', 'Manage workflow templates', true),
  ('workflow:schedule', 'workflow', 'Schedule workflow execution', true),
  ('workflow:trigger', 'workflow', 'Trigger workflow via webhooks', true),
  ('workflow:integrations', 'workflow', 'Manage workflow integrations', true),
  
  -- Configuration Management (8 permissions)
  ('config:read', 'configuration', 'Read system configuration', false),
  ('config:update', 'configuration', 'Modify system configuration', true),
  ('config:deploy', 'configuration', 'Deploy configuration changes', true),
  ('config:validate', 'configuration', 'Validate configuration syntax', false),
  ('config:backup', 'configuration', 'Backup configuration', true),
  ('config:restore', 'configuration', 'Restore configuration from backup', true),
  ('config:audit', 'configuration', 'Audit configuration changes', false),
  ('config:secrets', 'configuration', 'Manage configuration secrets', true),
  
  -- Security & Compliance (8 permissions)
  ('security:view_alerts', 'security', 'View security alerts', false),
  ('security:manage_alerts', 'security', 'Manage security alerts', true),
  ('security:policy_update', 'security', 'Update security policies', true),
  ('security:encryption', 'security', 'Manage encryption keys', true),
  ('security:access_logs', 'security', 'Access security logs', false),
  ('security:compliance_report', 'security', 'Generate compliance reports', false),
  ('security:incident_response', 'security', 'Respond to security incidents', true),
  ('security:penetration_test', 'security', 'Authorize penetration testing', true)
ON CONFLICT (name) DO NOTHING;

-- Set up default role hierarchy (admin inherits to all others)
INSERT INTO role_hierarchy (parent_role_id, child_role_id, inheritance_type)
SELECT r1.role_id, r2.role_id, 'full'
FROM roles r1, roles r2
WHERE (r1.name = 'admin' AND r2.name IN ('operator', 'viewer', 'guest'))
   OR (r1.name = 'operator' AND r2.name IN ('viewer', 'guest'))
   OR (r1.name = 'viewer' AND r2.name = 'guest')
ON CONFLICT (parent_role_id, child_role_id) DO NOTHING;

-- Create default tenant isolation rule
INSERT INTO tenant_isolation_rules (tenant_id, resource_scope, access_level, enforcement_level)
VALUES ('default', '*', 'isolated', 'strict')
ON CONFLICT (tenant_id, resource_scope) DO NOTHING;

-- =====================================================
-- Part 5: Set Default Role Permissions
-- =====================================================

-- Admin role: all permissions
INSERT INTO role_permissions (role_id, permission_id, resource_type)
SELECT r.role_id, p.permission_id, NULL
FROM roles r, permissions p
WHERE r.name = 'admin'
ON CONFLICT (role_id, permission_id, resource_type) DO NOTHING;

-- Operator role: agent control, workflow, config read
INSERT INTO role_permissions (role_id, permission_id, resource_type)
SELECT r.role_id, p.permission_id, NULL
FROM roles r, permissions p
WHERE r.name = 'operator'
  AND p.category IN ('agent-control', 'workflow', 'configuration')
  AND p.approval_required = false
ON CONFLICT (role_id, permission_id, resource_type) DO NOTHING;

-- Viewer role: read-only access
INSERT INTO role_permissions (role_id, permission_id, resource_type)
SELECT r.role_id, p.permission_id, NULL
FROM roles r, permissions p
WHERE r.name = 'viewer'
  AND p.approval_required = false
ON CONFLICT (role_id, permission_id, resource_type) DO NOTHING;

-- Guest role: minimal access (list only)
INSERT INTO role_permissions (role_id, permission_id, resource_type)
SELECT r.role_id, p.permission_id, NULL
FROM roles r, permissions p
WHERE r.name = 'guest'
  AND p.name IN ('agent:list', 'agent:read', 'agent:logs')
ON CONFLICT (role_id, permission_id, resource_type) DO NOTHING;

-- =====================================================
-- Part 6: Final Verification
-- =====================================================

-- Verify roles created
DO $$
DECLARE
  role_count INTEGER;
  perm_count INTEGER;
  hierarchy_count INTEGER;
BEGIN
  SELECT COUNT(*) INTO role_count FROM roles WHERE is_active = true;
  SELECT COUNT(*) INTO perm_count FROM permissions;
  SELECT COUNT(*) INTO hierarchy_count FROM role_hierarchy;
  
  RAISE NOTICE 'RBAC Schema Initialization Complete:';
  RAISE NOTICE '  Roles: % (expected: 4)', role_count;
  RAISE NOTICE '  Permissions: % (expected: 58+)', perm_count;
  RAISE NOTICE '  Role Hierarchy Links: % (expected: 6)', hierarchy_count;
END $$;

COMMIT;
