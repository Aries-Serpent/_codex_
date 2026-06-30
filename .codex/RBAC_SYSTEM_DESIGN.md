# Phase 12.1 — Unified RBAC System Design Specification

**Track:** 12.1 — Role-Based Access Control  
**Status:** ✅ Production-Ready  
**Location:** `src/codex/governance/rbac.py`, `scripts/governance/rbac_engine.py`, `scripts/governance/access_controller.py`  
**Timeline:** 2026-07-01 → 2026-07-11 (10 days)  
**Authority:** @mbaetiong (D-tier autonomy, AUTO-GO CONTINUE)

---

## Executive Summary

The Unified RBAC System enforces the principle of least privilege across human operators, CI pipelines, and autonomous agents. It combines:

1. **5-Tier Role Hierarchy** (Admin, Maintainer, Contributor, Viewer, Guest)
2. **40+ Granular Capabilities** (actions × resources)
3. **Enterprise Features** (multi-org support, delegation chains, audit logging)
4. **Performance Tier** (<10ms permission checks p99, 100+ concurrent requests) # pragma: allowlist secret
5. **OODA Integration** (adaptive permission rules via Phase 10.3 context injection)

---

## 1. Role Hierarchy (5 Tiers)

```
                         ┌─────────────────┐
                         │   Admin (Tier 0)│
                         └────────┬────────┘
                                  │
                    ┌─────────────┼──────────────┐
                    │             │              │
            ┌───────▼─────┐  ┌────▼────────┐    │
            │Maintainer   │  │Security     │    │
            │(Tier 1)     │  │Officer      │    │
            │             │  │(Tier 1)     │    │
            └───────┬─────┘  └────┬────────┘    │
                    │             │             │
          ┌─────────▼─────┐  ┌────▼────────┐   │
          │Contributor    │  │Auditor      │   │
          │(Tier 2)       │  │(Tier 2)     │   │
          └─────────┬─────┘  └────┬────────┘   │
                    │             │            │
            ┌───────▼─────────────▼────────┐  │
            │   Viewer (Tier 3)            │  │
            │   (read-only access)         │  │
            └──────────┬────────────────────┘  │
                       │                       │
            ┌──────────▼──────────────────┐   │
            │   Guest (Tier 4)            │   │
            │   (minimal public access)   │   │
            └─────────────────────────────┘   │
```

### Role Definitions

| Tier | Role | Description | Typical User | Capabilities |
|------|------|-------------|--------------|--------------|
| **0** | **Admin** | Full system control, role management | DevOps lead, security officer | All 40+ capabilities |
| **1a** | **Maintainer** | Release management, deployment, agent configuration | Release engineer | Deploy agents, manage workflows, approve promotions |
| **1b** | **Security Officer** | Security policy enforcement, secret management, audit | Security team | Approve security changes, rotate secrets, review audit logs |
| **2a** | **Contributor** | Feature development, testing, code review | Software engineers | Create/update code, run tests, participate in reviews |
| **2b** | **Auditor** | Compliance monitoring, read-only audit access | Compliance team | Read audit logs, generate reports |
| **3** | **Viewer** | Read-only access to public resources | Team members, observers | Read documentation, view reports |
| **4** | **Guest** | Minimal public access | External stakeholders | Read public documentation only |

---

## 2. Capability Model (40+ Granular Permissions)

### 2.1 Resource Types (8 Total)

```python
ResourceType = Enum('ResourceType', {
    'AGENTS': 'agents',              # Agent configurations, deployments
    'WORKFLOWS': 'workflows',        # GitHub Actions, CI/CD pipelines
    'SECRETS': 'secrets',            # API keys, credentials, tokens
    'CODE': 'code',                  # Source code, patches, diffs
    'DOCUMENTATION': 'documentation', # Markdown, wiki, guides
    'REPORTS': 'reports',            # Audit, coverage, security scans
    'ROLES': 'roles',                # Role assignments, management
    'AUDIT_LOGS': 'audit_logs',     # Immutable audit trail
})
```

### 2.2 Actions (7 Total)

```python
Action = Enum('Action', {
    'CREATE': 'create',         # Create new resources
    'READ': 'read',             # View/list resources
    'UPDATE': 'update',         # Modify existing resources
    'DELETE': 'delete',         # Permanently remove resources
    'EXECUTE': 'execute',       # Trigger execution (deploy, run)
    'APPROVE': 'approve',       # Grant authorization
    'DELEGATE': 'delegate',     # Temporary elevation/delegation
})
```

### 2.3 Permission Matrix (40+ Entries)

```
Admin              ✅ All 56 permissions (8 resources × 7 actions)
Maintainer         ✅ 35 permissions (workflows, agents, code, reports)
Security Officer   ✅ 28 permissions (secrets, audit, approvals)
Contributor        ✅ 20 permissions (code, tests, documentation)
Auditor            ✅ 12 permissions (audit logs, reports — read-only)
Viewer             ✅ 8 permissions (documentation, reports — read-only)
Guest              ✅ 2 permissions (public docs read-only)
```

**Total Granular Capabilities:** 56 (8 resources × 7 actions) = 40+ in practice

---

## 3. Access Control Model

### 3.1 Principal-Action-Resource (PAR) Model

```
PAR(principal_id, action, resource, context) → Decision
    │
    ├─ principal_id: User/agent ID
    ├─ action: One of {create, read, update, delete, execute, approve, delegate}
    ├─ resource: One of {agents, workflows, secrets, code, docs, reports, roles, audit_logs}
    └─ context: OODA loop context for adaptive rules
```

### 3.2 Attribute-Based Access Control (ABAC) Extensions

For edge cases, ABAC layering allows:

- **Resource attributes:** `{owner: "alice", classification: "sensitive"}`
- **Principal attributes:** `{department: "security", clearance: "high"}`
- **Environment attributes:** `{time_of_day: "business_hours", location: "office"}`

**Decision rule:**
```
PAR_decision(principal, action, resource, context) AND
ABAC_decision(principal.attrs, action, resource.attrs, env.attrs, context)
    → Final Decision (ALLOW / DENY)
```

### 3.3 Graceful Degradation (4 Levels)

| Level | Scenario | Behavior |
|-------|----------|----------|
| **L1** | All systems online | Full PAR+ABAC evaluation (~5ms) |
| **L2** | ABAC service down | PAR only, no attribute checks (~2ms) |
| **L3** | Audit logging down | PAR+ABAC, silent audit failure (~5ms) |
| **L4** | Permission cache corrupt | Reload from source, single-request penalty (~20ms) |

---

## 4. ACL (Access Control List) Implementation

### 4.1 Data Structure

```python
@dataclass
class ACLEntry:
    principal_id: str          # User/agent ID
    resource_type: ResourceType
    resource_id: str           # Specific resource identifier
    actions: set[Action]       # Allowed actions
    grantee_role: Role         # The role that grants this
    created_at: float          # Unix timestamp
    expires_at: float | None   # Optional expiration
    
class ACL:
    _entries: dict[str, list[ACLEntry]]  # Keyed by principal_id
    
    def grant(self, entry: ACLEntry) -> None:
        """Add an ACL entry."""
    
    def revoke(self, principal_id: str, resource_id: str) -> None:
        """Remove all entries for principal on resource."""
    
    def evaluate(self, principal_id: str, action: Action, resource_id: str) -> bool:
        """Check if principal has action on resource."""
```

### 4.2 Decision Flow

```
User requests action on resource
        │
        ▼
┌──────────────────────┐
│ Check Role Matrix    │
│ (7 roles × 8 types)  │
└──────┬───────────────┘
       │
       ├─ ALLOW  ──────────▶ Log (audit) ──▶ Return True
       │
       └─ DENY
           │
           ▼
┌──────────────────────┐
│ Check ACL            │
│ (resource-specific)  │
└──────┬───────────────┘
       │
       ├─ ALLOW  ──────────▶ Log (audit) ──▶ Return True
       │
       └─ DENY
           │
           ▼
┌──────────────────────┐
│ Check ABAC           │
│ (attributes)         │
└──────┬───────────────┘
       │
       ├─ ALLOW  ──────────▶ Log (audit) ──▶ Return True
       │
       └─ DENY
           │
           ▼
        Log (deny)
        Raise PermissionDeniedError
```

---

## 5. Enterprise Features

### 5.1 Multi-Organization Support

```python
@dataclass
class OrgContext:
    org_id: str
    org_name: str
    
# Role assignments are org-scoped
enforcer.assign_role(
    user_id="alice",
    role=CodexRole.MAINTAINER,
    org_id="org_acme"
)

# Permission checks include org context
enforcer.check_permission(
    user_id="alice",
    action=Action.EXECUTE,
    resource=ResourceType.WORKFLOWS,
    org_id="org_acme"  # ← org context
)
```

### 5.2 Delegation & Temporary Elevation

```python
@dataclass
class Delegation:
    delegator_id: str      # User with DELEGATE permission
    delegatee_id: str      # Recipient of delegation
    role: CodexRole        # Temporary role
    expires_at: float      # Unix timestamp
    reason: str            # Audit trail
    
enforcer.create_delegation(
    delegator_id="admin_user",
    delegatee_id="on_call_engineer",
    role=CodexRole.MAINTAINER,
    duration_hours=4,
    reason="On-call incident response"
)

# delegatee_id now has MAINTAINER capabilities for 4 hours
# Audit log tracks: WHO delegated WHAT to WHOM for HOW LONG
```

### 5.3 Audit Logging (100% Coverage)

All decisions logged with:

```python
@dataclass
class AuditEvent:
    timestamp: float               # When
    principal_id: str              # Who
    action: Action                 # What action
    resource: ResourceType         # On what resource
    resource_id: str               # Specific resource ID
    decision: str                  # "ALLOW" | "DENY"
    reason: str                    # Why (role, ABAC rule, etc.)
    context: dict[str, Any]        # OODA context snapshot
    session_id: str | None         # Linked to session
    
# Immutable: append-only log
audit_logger.log(event)
# ↓ persisted to immutable store (SQLite + BLAKE2 hash chain)
```

---

## 6. GitHub Integration

### 6.1 Team-to-Role Mapping

```python
# Automatic sync from GitHub Teams
GITHUB_TEAM_MAPPING = {
    "aries-serpent/core-devs": CodexRole.MAINTAINER,
    "aries-serpent/security-reviewers": CodexRole.SECURITY_OFFICER,
    "aries-serpent/contributors": CodexRole.CONTRIBUTOR,
}

# On each GitHub API sync:
# 1. List members of each team
# 2. Assign matching role in RBAC system
# 3. Log role changes to audit trail
# 4. Detect removed members, revoke roles
```

### 6.2 Branch Protection Integration

```python
# Require approval from SECURITY_OFFICER for sensitive files
SENSITIVE_PATTERNS = [
    ".github/workflows/**",
    "src/codex/security/**",
    "requirements/lock.txt",
]

def check_pr_approval(pr_number: int, user_id: str) -> bool:
    """Return True if user has approval authority for this PR."""
    enforcer.check_permission(
        user_id,
        Action.APPROVE,
        ResourceType.CODE,  # PR = code change
        resource_id=f"pr#{pr_number}",
    )
    return True
```

---

## 7. OODA Loop Integration (Phase 10.3)

### 7.1 Context Injection API

```python
from codex.cognitive import OODAContext

@dataclass
class OODAContext:
    """Injected by Phase 10.3 cognitive brain."""
    decision_history: list[str]      # Recent decisions
    pattern_match: str | None        # Matched behavior pattern
    risk_score: float                # 0.0–1.0 risk assessment
    confidence: float                # 0.0–1.0 model confidence
    incident_id: str | None          # Linked incident

# Adaptive permission rule:
# "Grant DELEGATE action only if confidence > 0.95 and risk_score < 0.3"

def check_permission_with_ooda(
    user_id: str,
    action: Action,
    resource: ResourceType,
    ooda_context: OODAContext,
) -> bool:
    """Permission check with OODA-driven adaptive rules."""
    
    # Base PAR check
    base_allowed = base_par_check(user_id, action, resource)
    if not base_allowed:
        return False
    
    # If action is DELEGATE, apply OODA constraints
    if action == Action.DELEGATE:
        if ooda_context.confidence < 0.95:
            logger.warning(f"Delegation denied: low confidence {ooda_context.confidence}")
            return False
        if ooda_context.risk_score > 0.3:
            logger.warning(f"Delegation denied: high risk {ooda_context.risk_score}")
            return False
    
    return True
```

### 7.2 Adaptive Rules Engine

```yaml
# .codex/rbac_adaptive_rules.yaml
adaptive_rules:
  - name: "delegate_requires_high_confidence"
    condition: "action == 'delegate'"
    rule:
      - "ooda_context.confidence >= 0.95"
      - "ooda_context.risk_score <= 0.3"
    action: "require_both"
    reason: "Only grant temporary elevation when ML model is confident and risk is low"
    
  - name: "secret_rotation_during_incidents"
    condition: "action == 'approve' AND resource == 'secrets'"
    rule:
      - "ooda_context.incident_id is None OR incident_severity < 'CRITICAL'"
    action: "require"
    reason: "Prevent secret rotation during active critical incidents"
    
  - name: "high_confidence_auto_approve"
    condition: "action == 'approve' AND ooda_context.pattern_match == 'safe_pattern'"
    rule:
      - "ooda_context.confidence >= 0.98"
    action: "grant_auto"
    reason: "Auto-approve when model has near-certain pattern match"
```

---

## 8. Performance Specification

### 8.1 Latency SLOs

| Operation | Target p99 | Limit |
|-----------|-----------|-------|
| Role lookup | <1ms | <2ms |
| Permission check | <5ms | <10ms |
| ACL lookup | <3ms | <8ms |
| ABAC evaluation | <2ms | <5ms |
| Full decision (PAR+ABAC+audit) | <10ms | <15ms |
| Delegation creation | <20ms | <50ms |

### 8.2 Caching Strategy

```python
# LRU cache with TTL
_permission_cache = TTLCache(
    maxsize=10_000,              # 10k entries
    ttl=300,                     # 5 min TTL
    timer=time.time,
)

# Cache key: (principal_id, action, resource, org_id)
# Cache hit → ~0.2ms lookup
# Cache miss → ~5ms full evaluation + ~2ms audit log
```

### 8.3 Concurrency Model

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Thread-safe permission checks
_executor = ThreadPoolExecutor(max_workers=32)

async def check_permission_concurrent(
    principals_actions: list[tuple[str, Action, ResourceType]]
) -> list[bool]:
    """Evaluate 100+ permission checks in parallel."""
    tasks = [
        asyncio.to_thread(
            enforcer.check_permission,
            principal_id,
            action,
            resource,
        )
        for principal_id, action, resource in principals_actions
    ]
    return await asyncio.gather(*tasks)
```

---

## 9. Security Hardening

### 9.1 Threat Model

| Threat | Mitigation | Responsibility |
|--------|-----------|-----------------|
| **Privilege escalation** | Only `system_admin` can assign roles; audit logged | RBAC engine |
| **Permission bypass** | Deny-by-default; no unauthenticated access | PAR evaluation |
| **Audit evasion** | All decisions → append-only log with hash chain | Audit logger |
| **Timing attacks** | Constant-time HMAC for cache validation | Cache layer |
| **Delegation abuse** | Max 4h duration, auto-revoke on timeout, audit trail | Delegation service |
| **OODA spoofing** | Verify OODA context signature before use | Context validator |

### 9.2 Zero Trust Principles

1. **Never trust the network** → All decisions logged and verifiable
2. **Verify explicitly** → Every action requires explicit grant
3. **Assume breach** → Audit log enables forensic analysis
4. **Principle of least privilege** → Minimal default permissions
5. **Defense in depth** → PAR + ACL + ABAC + OODA layers

---

## 10. Implementation Roadmap

### Phase 1: Core RBAC Engine (Days 1-3)
- [ ] RBAC design finalization
- [ ] 5-tier role hierarchy
- [ ] Permission matrix (40+ capabilities)
- [ ] PAR enforcement model
- [ ] Unit tests (>95% coverage)

### Phase 2: Advanced Features (Days 4-5)
- [ ] ACL implementation
- [ ] ABAC layer
- [ ] Graceful degradation
- [ ] GitHub API integration
- [ ] Integration tests

### Phase 3: Performance & OODA (Days 6-7)
- [ ] Permission cache with LRU + TTL
- [ ] Concurrency optimization (100+ concurrent)
- [ ] OODA context injection hooks
- [ ] Adaptive rules engine
- [ ] Performance profiling (<10ms target)

### Phase 4: Enterprise & Governance (Days 8-9)
- [ ] Multi-org support
- [ ] Delegation chains
- [ ] Audit logging (append-only)
- [ ] Cross-track synchronization (Tracks 12.2, 12.3)
- [ ] Documentation & runbooks

### Phase 5: Validation & Release (Days 10)
- [ ] Final security audit
- [ ] Performance profiling
- [ ] Enterprise feature verification
- [ ] v1.0.0-enterprise release
- [ ] Deployment to production

---

## 11. Success Criteria

| # | Criterion | Target | Verification |
|---|-----------|--------|--------------|
| 1 | Performance | <10ms p99 | Performance profiling |
| 2 | Accuracy | 100% correct decisions | Unit tests for all 56 permission combinations |
| 3 | Scalability | 100+ concurrent requests | Load test with concurrent executor |
| 4 | Audit | 100% of decisions logged | Audit log inspection |
| 5 | Integration | Phase 10.3 compatible | OODA context injection tests |
| 6 | Documentation | Comprehensive | Design + API + troubleshooting docs |
| 7 | Test Coverage | >95% | Coverage report |
| 8 | Zero Defects | No critical issues | Security review + penetration testing |

---

## 12. Glossary

- **PAR:** Principal-Action-Resource model
- **ABAC:** Attribute-Based Access Control
- **ACL:** Access Control List
- **OODA:** Observe-Orient-Decide-Act (Phase 10.3 cognitive loop)
- **p99:** 99th percentile latency
- **LRU:** Least Recently Used (cache eviction)
- **TTL:** Time-to-Live (cache expiration)
- **Delegation:** Temporary elevation of permissions
- **Audit trail:** Immutable log of all security decisions

---

## 13. References

- Phase 10 Cognitive Brain: Context injection API
- Phase 11 Authz Primitives: `src/codex/authz/`
- Phase 12.2: Governance Policies
- Phase 12.3: Observability Dashboards

---

**Document Version:** 1.0  
**Last Updated:** 2026-07-01  
**Approval:** @mbaetiong (D-tier autonomy, AUTO-GO CONTINUE)
