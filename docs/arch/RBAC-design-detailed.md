# RBAC Design & Implementation - Detailed
**Last Updated:** 2026-07-11
**Version:** v0.2.0

**Status:** Production Ready
**Version:** 1.0.0
**Last Updated: 2026-07-08
**Author:** Phase 12 WS3 Documentation Team

---

## Table of Contents

1. [Design Principles](#design-principles)
2. [Role Hierarchy](#role-hierarchy)
3. [Permission Matrix](#permission-matrix)
4. [Resource Types](#resource-types)
5. [Access Control Patterns](#access-control-patterns)
6. [Enforcement Engine](#enforcement-engine)
7. [Scope Management](#scope-management)
8. [Best Practices](#best-practices)

---

## Design Principles

### Zero Unauthorized Actions

Every permission check that fails raises `PermissionDeniedError`. There is no silent success or default allow behavior. All access control decisions are explicit and audited.

```python
# BAD: Silent failure
if check_permission(user, action, resource):
 execute(action)
# If check fails, nothing happens (dangerous!)

# GOOD: Explicit enforcement
try:
 enforcer.enforce_action(user, action, resource)
 execute(action)
except PermissionDeniedError as e:
 log_security_event(e)
 return 403_FORBIDDEN
```

### Delegation to Authz Layer

The RBAC module (`src/codex/governance/rbac.py`) delegates all enforcement to the lower-level authz primitives in `src/codex/authz/`:

- `PermissionValidator` - Validates (role, action, resource) tuples
- `RoleManager` - Manages role definitions and assignments
- `AuditLogger` - Records all access control decisions

This separation ensures RBAC adds Codex domain knowledge on top of battle-tested authz primitives.

### Immutable Permission Matrix

The rolepermission mapping is defined as a single source-of-truth Python dictionary:

```python
_ROLE_PERMISSION_MATRIX: dict[CodexRole, dict[ResourceType, set[Action]]] = {
 CodexRole.SYSTEM_ADMIN: {
 ResourceType.AGENTS: {Action.CREATE, Action.READ, ...},
 ...
 },
 ...
}
```

This dictionary is:
- **Immutable at runtime:** No modification of permissions during execution
- **Auditable:** Full Git history of permission changes
- **Testable:** Programmatically verified for consistency

### Forward Compatibility

All Codex code uses `from __future__ import annotations` for Python 3.12+ compatibility and to support forward references without circular imports.

---

## Role Hierarchy

### Visual Hierarchy

```
 system_admin
 (God mode)
 |
 agent_operator (Broad control)
 / | \
 ci_operator [shared] security_reviewer
 \ | /
 doc_maintainer
 |
 agent_reader (Narrow read)
 |
 guest (Minimal)
```

### Role Details

#### System Admin
```
Purpose: Full control and governance
Permission: All actions on all resources
Audit Trail: Every action logged and reviewable
Use Cases:
 - Emergency access
 - Role assignments
 - Governance decisions
 - Compliance audits
 
Typical Users:
 - Platform administrators (1-2 people)
 - Governance leads
 - On-call incident commanders
```

#### Agent Operator
```
Purpose: Deploy and manage agents
Permission: Create, read, update, execute agents/workflows
Audit Trail: Deployment audited, code changes tracked
Use Cases:
 - Deploy new agent versions
 - Configure agent parameters
 - Update agent workflows
 - Execute agents in production
 
Typical Users:
 - ML/Data engineering teams
 - Agent platform team
 - Workflow managers
```

#### CI Operator
```
Purpose: Manage CI/CD pipelines
Permission: Execute workflows, approve CI gates
Audit Trail: Workflow runs tracked, approvals logged
Use Cases:
 - Trigger CI workflows
 - Approve build gates
 - Manage release pipelines
 
Typical Users:
 - DevOps engineers
 - Release managers
 - CI/CD automation
```

#### Security Reviewer
```
Purpose: Review security-sensitive changes
Permission: Approve code/secret/workflow changes
Audit Trail: Every approval logged with reason
Use Cases:
 - Security code reviews
 - Secret rotation approvals
 - Workflow security validation
 
Typical Users:
 - Security engineers
 - Compliance officers
 - Security architects
```

#### Doc Maintainer
```
Purpose: Create and manage documentation
Permission: Full control over docs, read-only elsewhere
Audit Trail: All documentation changes tracked
Use Cases:
 - Update documentation
 - Create runbooks
 - Maintain API docs
 
Typical Users:
 - Technical writers
 - Documentation team
 - Knowledge managers
```

#### Agent Reader
```
Purpose: Read-only agent access
Permission: Read agents, workflows, code, docs, reports
Audit Trail: All reads logged (queryable later)
Use Cases:
 - Monitor agent deployments
 - Audit agent usage
 - Analyze agent logs
 
Typical Users:
 - Auditors
 - Compliance teams
 - Read-only analysts
```

#### Guest
```
Purpose: Minimal external access
Permission: Read public docs and reports only
Audit Trail: All guest access tracked
Use Cases:
 - Public documentation access
 - Performance report viewing
 - General information access
 
Typical Users:
 - External stakeholders
 - Public API users
 - Unauthenticated access
```

---

## Permission Matrix

### Complete Matrix (Rows = Roles, Columns = Resources × Actions)

```
 AGENTS WORKFLOWS SECRETS DOCS
Role C R U D E A C R U D E A C R U D E A C R U D E A

system_admin 
agent_operator × × × × × × × × × × × × × ×
ci_operator × × × × × × × × × × × × × × × × × ×
security_reviewer × × × × × × × × × × × × × × × × × ×
doc_maintainer × × × × × × × × × × × × × × × × × ×
agent_reader × × × × × × × × × × × × × × × × × × × × ×
guest × × × × × × × × × × × × × × × × × × × × × × ×

 CODE REPORTS ROLES AUDIT_LOGS
Role C R U D E A C R U D E A C R U D E A C R U D E A

system_admin × × × × × × × × ×
agent_operator × × × × × × × × × × × × × × × × × ×
ci_operator × × × × × × × × × × × × × × × × × × ×
security_reviewer × × × × × × × × × × × × × × × × × × ×
doc_maintainer × × × × × × × × × × × × × × × × × × × × ×
agent_reader × × × × × × × × × × × × × × × × × × × × ×
guest × × × × × × × × × × × × × × × × × × × × × × ×

Legend: C=Create, R=Read, U=Update, D=Delete, E=Execute, A=Approve, ×=Denied
```

### Key Characteristics

**Principle of Least Privilege:**
- Each role has minimal permissions needed for its function
- Dangerous actions (DELETE, APPROVE) restricted to senior roles
- No role has all permissions except system_admin

**Separation of Duties:**
- Agent Operator (deployment) ≠ Security Reviewer (approval)
- CI Operator (execution) ≠ Code reviewer
- Prevents any single person from deploying unapproved changes

**Read-Heavy Base:**
- Most roles can read agent/workflow definitions
- Execution and modification restricted to operators
- Auditors get full read access

---

## Resource Types

### agents
```
Purpose: Agent definitions, instances, and configurations
Actions: CREATE (define), READ (query), UPDATE (reconfigure), 
 DELETE (deprecate), EXECUTE (run), APPROVE (production)
Scope: Agent metadata, parameters, deployment status
Examples:
 - AgentDefinition (name, version, description)
 - AgentInstance (deployed agent, current state)
 - AgentConfig (parameters, environment)
```

### workflows
```
Purpose: CI/CD workflows, approval workflows, automation
Actions: CREATE (define), READ (view), UPDATE (modify), 
 DELETE (remove), EXECUTE (run), APPROVE (gate)
Scope: Workflow definitions, execution history
Examples:
 - CI workflow (build, test, deploy)
 - Approval workflow (request decision)
 - Automation workflow (scheduled task)
```

### secrets
```
Purpose: Credentials, keys, sensitive configuration
Actions: CREATE (new secret), READ (retrieve), UPDATE (rotate), 
 DELETE (revoke), APPROVE (rotation)
Scope: Secret metadata only (never values in logs)
Examples:
 - API keys
 - Database credentials
 - SSL certificates
 - Encryption keys
```

### docs
```
Purpose: Documentation, runbooks, knowledge base
Actions: CREATE (new doc), READ (view), UPDATE (edit), DELETE (remove)
Scope: All documentation types
Examples:
 - Architecture documentation
 - Security runbooks
 - API documentation
 - Operational guides
```

### code
```
Purpose: Source code, infrastructure as code, configurations
Actions: CREATE (new file), READ (view), UPDATE (modify), DELETE (remove), 
 APPROVE (security review)
Scope: Code repository contents
Examples:
 - Python source code
 - Terraform configurations
 - Docker files
 - Configuration files
```

### reports
```
Purpose: Generated reports, analytics, dashboards
Actions: CREATE (generate), READ (view), UPDATE (refresh), DELETE (archive)
Scope: Report data only
Examples:
 - Deployment reports
 - Security audit reports
 - Performance metrics
 - Compliance dashboards
```

### roles
```
Purpose: Role definitions, assignments, permissions
Actions: CREATE (new role), READ (view roles), UPDATE (modify), 
 DELETE (remove), ASSIGN (assign to user)
Scope: Role metadata only
Examples:
 - Role definitions
 - Role assignments
 - Permission updates
 - Role deprecation
```

### audit_logs
```
Purpose: Audit trail, compliance records, activity logs
Actions: READ (query logs), no write access
Scope: Read-only access to all audit events
Examples:
 - Permission checks
 - Action executions
 - Approval decisions
 - Security events
```

---

## Access Control Patterns

### Pattern 1: Simple Permission Check

```python
from codex.governance.rbac import RBACEnforcer, CodexRole, Action, ResourceType

enforcer = RBACEnforcer()

# Check if user has permission
has_permission = enforcer.has_permission(
 user_id="alice",
 role=CodexRole.AGENT_OPERATOR,
 action=Action.EXECUTE,
 resource=ResourceType.AGENTS
)

if has_permission:
 print("Alice can execute agents")
else:
 print("Alice cannot execute agents")
```

### Pattern 2: Enforce with Exception Handling

```python
from codex.governance.rbac import PermissionDeniedError

try:
 enforcer.enforce_action(
 user_id="bob",
 role=CodexRole.CI_OPERATOR,
 action=Action.APPROVE,
 resource=ResourceType.WORKFLOWS,
 resource_id="deploy_prod_workflow"
 )
 # Permission granted, proceed with action
 execute_workflow("deploy_prod_workflow")
 
except PermissionDeniedError as e:
 logger.warning(
 f"Permission denied: user={e.user_id}, "
 f"action={e.action}, resource={e.resource}"
 )
 return 403_FORBIDDEN
```

### Pattern 3: Audit Action with Context

```python
enforcer.audit_action(
 user_id="charlie",
 role=CodexRole.AGENT_OPERATOR,
 action=Action.CREATE,
 resource=ResourceType.AGENTS,
 resource_id="new_agent_v2.1",
 context={
 "agent_name": "DataProcessor",
 "version": "2.1.0",
 "description": "Q3 campaign model",
 "environment": "production"
 }
)
```

### Pattern 4: Role-Based Conditional Logic

```python
from codex.governance.rbac import CodexRole

def get_visible_agents(user_roles: List[CodexRole]) -> List[Agent]:
 """Return agents visible to user based on role."""
 
 if CodexRole.SYSTEM_ADMIN in user_roles:
 # Admins see all agents
 return get_all_agents()
 
 elif CodexRole.AGENT_OPERATOR in user_roles:
 # Operators see all agents they can manage
 return get_operators_agents()
 
 elif CodexRole.AGENT_READER in user_roles:
 # Readers see published agents only
 return get_published_agents()
 
 else:
 # Guests see public agents only
 return get_public_agents()
```

### Pattern 5: Multi-Role Authorization

```python
def can_deploy_to_production(user_roles: List[CodexRole]) -> bool:
 """Check if user has multi-role permission for prod deployment."""
 
 # Must have AGENT_OPERATOR for deployment
 has_deploy_perm = CodexRole.AGENT_OPERATOR in user_roles
 
 # Must have either CI_OPERATOR or SECURITY_REVIEWER for approval
 has_approval_perm = (
 CodexRole.CI_OPERATOR in user_roles or 
 CodexRole.SECURITY_REVIEWER in user_roles
 )
 
 return has_deploy_perm and has_approval_perm
```

---

## Enforcement Engine

### RBACEnforcer Class

```python
class RBACEnforcer:
 """
 High-level RBAC enforcement for Codex operations.
 
 Design:
 -------
 - Wraps authz layer primitives (PermissionValidator, RoleManager, AuditLogger)
 - Adds Codex domain knowledge (roles, resources, actions)
 - Enforces zero-tolerance for unauthorized actions
 - Full audit trail of all decisions
 """
 
 def __init__(self, audit_logger: AuditLogger | None = None):
 """Initialize with optional audit logger."""
 self.validator = PermissionValidator()
 self.role_manager = RoleManager()
 self.audit_logger = audit_logger or AuditLogger()
 
 def has_permission(
 self, 
 user_id: str,
 role: CodexRole,
 action: Action,
 resource: ResourceType
 ) -> bool:
 """Check if user has permission without raising exception."""
 return self.validator.validate(role, action, resource)
 
 def enforce_action(
 self,
 user_id: str,
 role: CodexRole,
 action: Action,
 resource: ResourceType,
 resource_id: str | None = None,
 context: dict | None = None
 ) -> None:
 """Enforce action or raise PermissionDeniedError."""
 if not self.has_permission(user_id, role, action, resource):
 raise PermissionDeniedError(user_id, action, resource)
 
 # Log the action
 self.audit_logger.log_action(
 user_id=user_id,
 role=role.value,
 action=action.value,
 resource=resource.value,
 resource_id=resource_id,
 context=context or {}
 )
 
 def get_user_permissions(
 self,
 user_id: str,
 roles: List[CodexRole]
 ) -> Dict[ResourceType, Set[Action]]:
 """Get all permissions for user's roles."""
 permissions = {}
 for role in roles:
 for resource, actions in _ROLE_PERMISSION_MATRIX[role].items():
 if resource not in permissions:
 permissions[resource] = set()
 permissions[resource].update(actions)
 return permissions
```

### Permission Validation

```python
def validate_permission(
 role: CodexRole,
 action: Action,
 resource: ResourceType
) -> bool:
 """Check if role can perform action on resource."""
 
 # Get role's permissions from matrix
 role_perms = _ROLE_PERMISSION_MATRIX.get(role, {})
 
 # Get resource's allowed actions
 resource_actions = role_perms.get(resource, set())
 
 # Check if action is allowed
 return action in resource_actions
```

### Audit Logging

```python
class AuditLogger:
 """Log all RBAC decisions for compliance."""
 
 def log_action(
 self,
 user_id: str,
 role: str,
 action: str,
 resource: str,
 resource_id: str | None = None,
 context: dict | None = None,
 result: str = "allowed"
 ) -> None:
 """Log RBAC decision."""
 
 event = {
 "timestamp": time.time(),
 "user_id": user_id,
 "role": role,
 "action": action,
 "resource": resource,
 "resource_id": resource_id,
 "context": context or {},
 "result": result
 }
 
 # Log to audit trail (database, file, centralized logging)
 self.storage.insert_audit_event(event)
```

---

## Scope Management

### Scope Types

```python
class TokenScope(str, Enum):
 """Fine-grained permissions within a token."""
 
 # Agent scopes
 API_AGENTS_READ = "api:agents:read"
 API_AGENTS_WRITE = "api:agents:write"
 API_AGENTS_EXEC = "api:agents:exec"
 
 # Workflow scopes
 API_WORKFLOWS_READ = "api:workflows:read"
 API_WORKFLOWS_EXEC = "api:workflows:exec"
 API_WORKFLOWS_APPROVE = "api:workflows:approve"
 
 # Secret scopes
 API_SECRETS_READ = "api:secrets:read"
 API_SECRETS_ROTATE = "api:secrets:rotate"
 
 # Governance scopes
 GOVERNANCE_APPROVE = "governance:approve"
 GOVERNANCE_AUDIT = "governance:audit"
```

### Scope-Based Access Control

```python
def check_token_scope(token: str, required_scope: TokenScope) -> bool:
 """Check if token has required scope."""
 
 # Decode and validate token
 payload = jwt.decode(token, SECRET_KEY, algorithms=["RS256"])
 
 # Get scopes from token
 token_scopes: List[str] = payload.get("scopes", [])
 
 # Check if required scope is present
 return required_scope.value in token_scopes
```

### Scope Assignment During Token Issue

```python
def issue_token(
 user_id: str,
 roles: List[CodexRole],
 resource: ResourceType | None = None
) -> str:
 """Issue JWT token with appropriate scopes."""
 
 scopes = []
 
 # Add scopes based on roles
 if CodexRole.AGENT_OPERATOR in roles:
 scopes.extend([
 TokenScope.API_AGENTS_READ.value,
 TokenScope.API_AGENTS_WRITE.value,
 TokenScope.API_AGENTS_EXEC.value,
 TokenScope.API_WORKFLOWS_EXEC.value
 ])
 
 if CodexRole.SECURITY_REVIEWER in roles:
 scopes.extend([
 TokenScope.API_WORKFLOWS_APPROVE.value,
 TokenScope.GOVERNANCE_APPROVE.value
 ])
 
 # Create JWT with scopes
 payload = {
 "user_id": user_id,
 "roles": [r.value for r in roles],
 "scopes": scopes,
 "exp": time.time() + 900
 }
 
 return jwt.encode(payload, SECRET_KEY, algorithm="RS256")
```

---

## Best Practices

### 1. Always Use Enforcer

 **GOOD:**
```python
enforcer.enforce_action(user_id, role, Action.DELETE, ResourceType.AGENTS)
```

 **BAD:**
```python
# Don't check permissions manually
if user_role == "admin":
 delete_agent(agent_id)
```

### 2. Include Context in Logs

 **GOOD:**
```python
enforcer.audit_action(
 user_id="alice",
 role=CodexRole.AGENT_OPERATOR,
 action=Action.CREATE,
 resource=ResourceType.AGENTS,
 context={"agent_name": "DataProcessor", "version": "2.1.0"}
)
```

 **BAD:**
```python
logger.info(f"User {user_id} created agent") # No context
```

### 3. Fail Safely

 **GOOD:**
```python
try:
 enforcer.enforce_action(...)
 execute_privileged_action()
except PermissionDeniedError as e:
 logger.error(f"Unauthorized: {e}")
 return 403_FORBIDDEN
```

 **BAD:**
```python
enforcer.enforce_action(...) # No error handling
execute_privileged_action() # Could proceed without permission
```

### 4. Document Role Requirements

 **GOOD:**
```python
def deploy_agent(agent_id: str) -> None:
 """
 Deploy agent to production.
 
 Requires:
 - CodexRole.AGENT_OPERATOR (execute permission on agents)
 - CodexRole.SECURITY_REVIEWER or system_admin (approval)
 - Successful approval workflow
 """
 enforcer.enforce_action(...)
```

 **BAD:**
```python
def deploy_agent(agent_id: str) -> None:
 """Deploy agent.""" # No role requirements documented
 enforcer.enforce_action(...)
```

### 5. Use Least Privilege for API Tokens

 **GOOD:**
```python
# Service account for reading agent logs
scopes = [TokenScope.API_AGENTS_READ.value]
token = issue_token("service_logger", scopes)
```

 **BAD:**
```python
# Service account with admin token
token = issue_admin_token() # Overly privileged
```

### 6. Regular Permission Audits

```python
# Quarterly audit of all role assignments
def audit_role_assignments():
 """Audit all user role assignments."""
 users = get_all_users()
 for user in users:
 roles = user.get_roles()
 permissions = enforcer.get_user_permissions(user.id, roles)
 # Compare against expected permissions
 # Flag any unexpected assignments
```

---

## References

- [Governance API Reference](../api/governance-api-reference.md)
- [Approval Policies](../arch/approval-policies-detailed.md)
- [Authentication & Authorization](../ops/security-runbooks.md)
- [Audit Logging](../ops/security-runbooks.md#audit-logging)

---

**Last Updated: 2026-07-08
**Version:** 1.0.0
**Status:** Production Ready
