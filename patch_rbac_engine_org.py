import re

with open('scripts/governance/rbac_engine.py', 'r') as f:
    content = f.read()

# 1. assign_role
content = re.sub(
    r'def assign_role\(self, principal_id: str, role: CodexRole\) -> None:',
    r'def assign_role(self, principal_id: str, role: CodexRole, org_id: str = "default") -> None:',
    content
)
content = content.replace("self._role_assignments[principal_id] = set()", "self._role_assignments[principal_id] = {}")
content = re.sub(
    r'self._role_assignments\[principal_id\]\.add\(role\)',
    r'if org_id not in self._role_assignments[principal_id]:\n                self._role_assignments[principal_id][org_id] = set()\n            self._role_assignments[principal_id][org_id].add(role)',
    content
)

# 2. revoke_role
content = re.sub(
    r'def revoke_role\(self, principal_id: str, role: CodexRole\) -> None:',
    r'def revoke_role(self, principal_id: str, role: CodexRole, org_id: str = "default") -> None:',
    content
)
content = re.sub(
    r'self._role_assignments\[principal_id\]\.discard\(role\)',
    r'if org_id in self._role_assignments[principal_id]:\n                    self._role_assignments[principal_id][org_id].discard(role)',
    content
)

# 3. get_roles
content = re.sub(
    r'def get_roles\(self, principal_id: str\) -> list\[CodexRole\]:',
    r'def get_roles(self, principal_id: str, org_id: str = "default") -> list[CodexRole]:',
    content
)
content = re.sub(
    r'return list\(self._role_assignments\.get\(principal_id, set\(\)\)\)',
    r'return list(self._role_assignments.get(principal_id, {}).get(org_id, set()))',
    content
)

# 4. has_role
content = re.sub(
    r'def has_role\(self, principal_id: str, role: CodexRole\) -> bool:',
    r'def has_role(self, principal_id: str, role: CodexRole, org_id: str = "default") -> bool:',
    content
)
content = re.sub(
    r'return role in self\.get_roles\(principal_id\)',
    r'return role in self.get_roles(principal_id, org_id)',
    content
)

# 5. check_permission
content = re.sub(
    r'def check_permission\(\n        self,\n        principal_id: str,\n        action: Action,\n        resource: ResourceType,\n        resource_id: str = "\*",\n        ooda_context: Optional\[OODAContext\] = None,\n    \) -> bool:',
    r'def check_permission(\n        self,\n        principal_id: str,\n        action: Action,\n        resource: ResourceType,\n        resource_id: str = "*",\n        ooda_context: Optional[OODAContext] = None,\n        org_id: str = "default",\n    ) -> bool:',
    content
)

content = re.sub(
    r'cache_key = f"\{principal_id\}:\{action.value\}:\{resource.value\}:\{resource_id\}"',
    r'cache_key = f"{org_id}:{principal_id}:{action.value}:{resource.value}:{resource_id}"',
    content
)

content = re.sub(
    r'if self._check_role_permissions\(principal_id, action, resource\):',
    r'if self._check_role_permissions(principal_id, action, resource, org_id):',
    content
)

content = re.sub(
    r'def _check_role_permissions\(\n        self, principal_id: str, action: Action, resource: ResourceType\n    \) -> bool:',
    r'def _check_role_permissions(\n        self, principal_id: str, action: Action, resource: ResourceType, org_id: str = "default"\n    ) -> bool:',
    content
)
content = re.sub(
    r'roles = self\.get_roles\(principal_id\)',
    r'roles = self.get_roles(principal_id, org_id)',
    content
)

content = re.sub(
    r'def create_delegation\(\n        self,\n        delegator_id: str,\n        delegatee_id: str,\n        role: CodexRole,\n        duration_seconds: float,\n        reason: str,\n    \) -> str:',
    r'def create_delegation(\n        self,\n        delegator_id: str,\n        delegatee_id: str,\n        role: CodexRole,\n        duration_seconds: float,\n        reason: str,\n        org_id: str = "default",\n    ) -> str:',
    content
)

content = re.sub(
    r'delegation = Delegation\(\n                delegation_id=delegation_id,\n                delegator_id=delegator_id,\n                delegatee_id=delegatee_id,\n                role=role,\n                expires_at=time\.time\(\) \+ duration_seconds,\n                reason=reason,\n            \)',
    r'delegation = Delegation(\n                delegation_id=delegation_id,\n                delegator_id=delegator_id,\n                delegatee_id=delegatee_id,\n                role=role,\n                expires_at=time.time() + duration_seconds,\n                reason=reason,\n            )\n            delegation.org_id = org_id',
    content
)

content = re.sub(
    r'@dataclass\nclass Delegation:\n    """Temporary role delegation\."""\n\n    delegation_id: str\n    delegator_id: str\n    delegatee_id: str\n    role: CodexRole\n    expires_at: float\n    reason: str',
    r'@dataclass\nclass Delegation:\n    """Temporary role delegation."""\n\n    delegation_id: str\n    delegator_id: str\n    delegatee_id: str\n    role: CodexRole\n    expires_at: float\n    reason: str\n    org_id: str = "default"',
    content
)

content = re.sub(
    r'if d\.delegatee_id == principal_id and d\.expires_at > now:',
    r'if d.delegatee_id == principal_id and d.expires_at > now:', # handled below
    content
)

content = re.sub(
    r'def _get_active_delegations\(self, principal_id: str\) -> list\[Delegation\]:',
    r'def _get_active_delegations(self, principal_id: str, org_id: str = "default") -> list[Delegation]:',
    content
)

content = re.sub(
    r'return \[\n                d\n                for d in self\._delegations\.values\(\)\n                if d\.delegatee_id == principal_id and d\.expires_at > now\n            \]',
    r'return [\n                d\n                for d in self._delegations.values()\n                if d.delegatee_id == principal_id and d.expires_at > now and d.org_id == org_id\n            ]',
    content
)

content = re.sub(
    r'delegations = self\._get_active_delegations\(principal_id\)',
    r'delegations = self._get_active_delegations(principal_id, org_id)',
    content
)

content = re.sub(
    r'def _log_audit\(\n        self,\n        principal_id: str,\n        action: Action,\n        resource: ResourceType,\n        resource_id: str,\n        decision: str,\n        reason: str,\n        ooda_context: Optional\[OODAContext\],\n    \) -> None:',
    r'def _log_audit(\n        self,\n        principal_id: str,\n        action: Action,\n        resource: ResourceType,\n        resource_id: str,\n        decision: str,\n        reason: str,\n        ooda_context: Optional[OODAContext],\n        org_id: str = "default",\n    ) -> None:',
    content
)

content = re.sub(
    r'        self\._log_audit\(principal_id, action, resource, resource_id, "ALLOW", "ACL match", ooda_context\)',
    r'        self._log_audit(principal_id, action, resource, resource_id, "ALLOW", "ACL match", ooda_context, org_id)',
    content
)

content = re.sub(
    r'        self\._log_audit\(\n            principal_id, action, resource, resource_id, "ALLOW", "OODA adaptive rule", ooda_context\n        \)',
    r'        self._log_audit(\n            principal_id, action, resource, resource_id, "ALLOW", "OODA adaptive rule", ooda_context, org_id\n        )',
    content
)

content = re.sub(
    r'        self\._log_audit\(\n            principal_id, action, resource, resource_id, "ALLOW", "Role permission", ooda_context\n        \)',
    r'        self._log_audit(\n            principal_id, action, resource, resource_id, "ALLOW", "Role permission", ooda_context, org_id\n        )',
    content
)

content = re.sub(
    r'        self\._log_audit\(\n            principal_id, action, resource, resource_id, "DENY", "No permission found", ooda_context\n        \)',
    r'        self._log_audit(\n            principal_id, action, resource, resource_id, "DENY", "No permission found", ooda_context, org_id\n        )',
    content
)

content = re.sub(
    r'@dataclass\nclass AuditEvent:\n    """Immutable audit log event\."""\n\n    timestamp: float\n    principal_id: str\n    action: Action\n    resource: ResourceType\n    resource_id: str\n    decision: str\n    reason: str\n    context: dict\[str, Any\]\n    session_id: Optional\[str\]',
    r'@dataclass\nclass AuditEvent:\n    """Immutable audit log event."""\n\n    timestamp: float\n    principal_id: str\n    action: Action\n    resource: ResourceType\n    resource_id: str\n    decision: str\n    reason: str\n    context: dict[str, Any]\n    session_id: Optional[str]\n    org_id: str = "default"',
    content
)

content = re.sub(
    r'event = AuditEvent\(\n                timestamp=time\.time\(\),\n                principal_id=principal_id,\n                action=action,\n                resource=resource,\n                resource_id=resource_id,\n                decision=decision,\n                reason=reason,\n                context=ctx_dict,\n                session_id=None,\n            \)',
    r'event = AuditEvent(\n                timestamp=time.time(),\n                principal_id=principal_id,\n                action=action,\n                resource=resource,\n                resource_id=resource_id,\n                decision=decision,\n                reason=reason,\n                context=ctx_dict,\n                session_id=None,\n                org_id=org_id,\n            )',
    content
)

with open('scripts/governance/rbac_engine.py', 'w') as f:
    f.write(content)

print("Org Support Patched successfully")
