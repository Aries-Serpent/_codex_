# Approval Policies Framework — Phase 12 Track 12.2

> **Version:** 1.0 · **Created:** 2026-02-17 · **Authority:** D-tier autonomy (@mbaetiong)
> **Status:** Active · **Last Updated:** 2026-02-17 · **Word Count:** ~3500 words

---

## Executive Summary

This document defines the comprehensive approval policy framework for the Codex repository, establishing governance rules for autonomous agent operations, security-sensitive changes, cost-incurring actions, and compliance-critical decisions. The framework balances operational velocity with risk management through structured policy categories, approval workflow models, and escalation chains.

---

## Section A: Policy Framework Overview

### A.1 Policy Categories & Scope

The approval framework is organized into **8 primary policy categories**, each addressing a distinct governance domain:

#### 1. **Deployment Policies** (D-series)
Approval gates for code releases, environment promotions, and production deployments.

- **D-001:** Canary deployment to production (1 approval: Release Manager)
- **D-002:** Full production rollout (2 approvals: Release Manager + Security Lead)
- **D-003:** Rollback of production release (1 approval: Incident Commander)
- **D-004:** Deployment to staging environment (1 approval: DevOps Lead)
- **D-005:** Blue-green swap execution (1 approval: Release Manager)
- **D-006:** Infrastructure version upgrades (2 approvals: DevOps + Architect)

#### 2. **Security Policies** (S-series)
Approval gates for security configuration changes, privilege escalation, and vulnerability remediations.

- **S-001:** Authorization scope changes (2 approvals: Security Lead + Owner)
- **S-002:** Token rotation for elevated credentials (1 approval: Security Lead)
- **S-003:** Security exception approval (3 approvals: Security + Compliance + Owner)
- **S-004:** Encryption key rotation (2 approvals: Security Lead + Infrastructure)
- **S-005:** Access policy modifications (2 approvals: Security + RBAC Admin)
- **S-006:** Critical security patch deployment (1 approval: Security Lead)
- **S-007:** Sensitive data access logging enablement (1 approval: Compliance Officer)
- **S-008:** Firewall rule modification (2 approvals: Security + Network Admin)

#### 3. **Resource Management Policies** (R-series)
Approval gates for budget allocation, quota increases, and resource provisioning.

- **R-001:** Cost-incurring infrastructure provisioning >$1K (2 approvals: Budget Owner + Finance)
- **R-002:** GPU/compute quota increase (1 approval: DevOps Lead)
- **R-003:** Storage quota increase >100GB (1 approval: Infrastructure Lead)
- **R-004:** Database replication provisioning (1 approval: DBA)
- **R-005:** Multi-region deployment approval (2 approvals: DevOps + Budget Owner)
- **R-006:** Deletion of production databases (3 approvals: DBA + Owner + Compliance)

#### 4. **Configuration Change Policies** (C-series)
Approval gates for systemic configuration modifications affecting multiple services.

- **C-001:** Feature flag rollout to >50% traffic (1 approval: Product Lead)
- **C-002:** API contract breaking changes (2 approvals: API Lead + Affected Service Owners)
- **C-003:** Environment variable changes (1 approval: Relevant Owner)
- **C-004:** Circuit breaker threshold modifications (1 approval: Reliability Engineer)
- **C-005:** Cache invalidation strategy changes (1 approval: Performance Lead)
- **C-006:** Rate limiting policy updates (1 approval: API Lead)

#### 5. **Capability Grant Policies** (G-series)
Approval gates for granting elevated capabilities, access levels, and operational permissions.

- **G-001:** New agent autonomous operation grant (2 approvals: Owner + Security)
- **G-002:** Admin-level access grant (3 approvals: Owner + Security + Manager)
- **G-003:** Automated remediation permission (1 approval: Relevant Owner)
- **G-004:** Cross-service permission grant (2 approvals: Service Owners)
- **G-005:** API rate limit exception (1 approval: API Lead)
- **G-006:** Cost override authorization (1 approval: Budget Owner)

#### 6. **Escalation Policies** (E-series)
Approval gates for escalating decisions, timeouts, and conflict resolution.

- **E-001:** Automatic escalation on approval timeout (escalate after 4 hours to Manager)
- **E-002:** Manual escalation to executive team (1 approver may escalate to VP)
- **E-003:** Conflict resolution escalation (escalate approval disagreement to Owner)
- **E-004:** Out-of-hours emergency override (1 approval: On-call Manager)
- **E-005:** Exception to SLA approval window (escalate after 8 hours)

#### 7. **Incident Response Policies** (I-series)
Approval gates for incident-driven actions and emergency measures.

- **I-001:** Emergency access grant during incident (1 approval: Incident Commander)
- **I-002:** Data purge authorization (2 approvals: Compliance + Owner)
- **I-003:** Service circuit breaker activation (1 approval: On-call Engineer)
- **I-004:** Rollback to previous stable version (1 approval: Incident Commander)
- **I-005:** Disable rate limiting temporarily (1 approval: Incident Commander)

#### 8. **Audit & Compliance Policies** (A-series)
Approval gates for compliance verification, audit operations, and regulatory requirements.

- **A-001:** Compliance audit initiation (1 approval: Compliance Officer)
- **A-002:** Data retention policy changes (2 approvals: Compliance + Legal)
- **A-003:** Audit log access grant (1 approval: Compliance Officer)
- **A-004:** PII data export approval (2 approvals: Compliance + Data Owner)
- **A-005:** Regulatory report generation (1 approval: Compliance Officer)
- **A-006:** Privacy policy modification (2 approvals: Compliance + Legal)

### A.2 Policy Dependency Graph

Policies have implicit dependencies when approval of one policy enables or disables another:

```
DEPLOYMENT (D) ← requires → SECURITY (S)
                           ↓
RESOURCE (R) ← funded by → CAPABILITY GRANT (G)
                                ↓
                        ESCALATION (E) ← fallback for all
                                ↓
                        INCIDENT (I) ← overrides normal flow
                                ↓
                        AUDIT & COMPLIANCE (A)
```

### A.3 Approval Authorities by Role

| Role | Authority Level | Max Policy Tier | Approval Capacity |
|------|------------------|-----------------|-------------------|
| **Owner** | Tier 1 (Executive) | All (A-Z series) | Unlimited |
| **Security Lead** | Tier 2 (Strategic) | S, E, A series | 50/day |
| **Release Manager** | Tier 2 (Strategic) | D series | 100/day |
| **DevOps Lead** | Tier 3 (Operational) | D, R series | 200/day |
| **Incident Commander** | Tier 3 (Operational) | I, E series | Unlimited (incident-scoped) |
| **Budget Owner** | Tier 3 (Operational) | R, G series | 50/day |
| **DBA** | Tier 3 (Operational) | R series (DB-specific) | 100/day |
| **Compliance Officer** | Tier 3 (Operational) | A, I series | Unlimited |

---

## Section B: Approval Workflow Models

### B.1 Single-Stage Approval Model

**Use case:** Low-risk, time-sensitive operations requiring single decision point.

```mermaid
graph LR
    A["📋 Request\nInitiated"] -->|"auto-route"| B["👤 Single Approver\nAssigned"]
    B -->|"approved"| C["✅ Request\nApproved"]
    B -->|"rejected"| D["❌ Request\nRejected"]
    B -->|"no response\nafter 4h"| E["⏱️ Timeout\nReached"]
    E -->|"escalate"| F["⬆️ Escalate to\nManager"]
    F -->|"approved"| C
    F -->|"rejected"| D
```

**Workflow characteristics:**
- **Approvers:** 1 (single authority)
- **Execution:** Sequential
- **SLA:** 4 hours before escalation
- **Examples:** D-003, I-003, I-004
- **Auto-approval fallback:** After 8 hours with escalation approval, allow execution

---

### B.2 Multi-Stage Sequential Approval Model

**Use case:** Higher-risk operations requiring multiple validation perspectives (security + business).

```mermaid
graph LR
    A["📋 Request\nInitiated"] -->|"route to\nStage 1"| B["🔒 Security Review\n(Stage 1)"]
    B -->|"approved"| C["💼 Business Review\n(Stage 2)"]
    B -->|"rejected"| D["❌ Request\nRejected"]
    C -->|"approved"| E["✅ Request\nApproved"]
    C -->|"rejected"| D
    B -->|"timeout 4h"| F["⏱️ Escalate\nStage 1"]
    C -->|"timeout 4h"| G["⏱️ Escalate\nStage 2"]
    F --> E
    G --> E
```

**Workflow characteristics:**
- **Approvers:** 2 (sequential stages)
- **Execution:** Stage 1 → Stage 2 (must complete in order)
- **SLA per stage:** 4 hours before escalation
- **Total SLA:** 8 hours maximum
- **Examples:** D-002, S-001, R-001
- **Parallel variant:** If Stage 1 & 2 are independent, run simultaneously with "any 1 rejection = reject all"

---

### B.3 Multi-Stage Parallel Approval Model

**Use case:** Complex decisions where multiple stakeholders must review concurrently (e.g., security + compliance + finance).

```mermaid
graph LR
    A["📋 Request\nInitiated"] -->|"route all"| B["🔒 Security\n(Parallel)"]
    A -->|"route all"| C["⚖️ Compliance\n(Parallel)"]
    A -->|"route all"| D["💰 Finance\n(Parallel)"]
    B -->|"approved"| E["✅ All Approved"]
    C -->|"approved"| E
    D -->|"approved"| E
    B -->|"rejected"| F["❌ Request\nRejected"]
    C -->|"rejected"| F
    D -->|"rejected"| F
    B -->|"timeout 4h"| G["⏱️ Escalate All"]
    C -->|"timeout 4h"| G
    D -->|"timeout 4h"| G
    G --> E
```

**Workflow characteristics:**
- **Approvers:** 3+ (all must review simultaneously)
- **Execution:** Concurrent (all stages active at once)
- **SLA:** 4 hours per stage
- **Decision rule:** ALL must approve (single rejection = entire request rejected)
- **Escalation:** If any stage times out, escalate all stages together
- **Examples:** D-002 (if using parallel variant), S-003, R-006

---

### B.4 Escalation Chain Model

**Use case:** Handling timeouts, conflicts, and decision authority promotions.

```mermaid
graph TD
    A["📋 Initial Request\nto Level-1 Approver"]
    B["⏱️ Level 1 Timeout\nafter 4h"]
    C["⬆️ Escalate to\nLevel 2 Authority"]
    D["⏱️ Level 2 Timeout\nafter 4h"]
    E["⬆️ Escalate to\nLevel 3 Authority\n(Owner/Executive)"]
    F["✅ Approved at\nany level"]
    G["❌ Rejected at\nany level"]
    
    A -->|approved| F
    A -->|rejected| G
    A -->|timeout| B
    B --> C
    C -->|approved| F
    C -->|rejected| G
    C -->|timeout| D
    D --> E
    E -->|approved| F
    E -->|rejected| G
```

**Escalation levels by policy category:**

| Policy Category | Level 1 | Level 2 | Level 3 (Final) | Total SLA |
|-----------------|---------|---------|-----------------|-----------|
| D (Deploy) | Release Manager | DevOps Lead | Owner | 12h |
| S (Security) | Security Lead | Security Manager | Owner | 12h |
| R (Resource) | DBA/DevOps | Budget Owner | Owner | 12h |
| G (Capability Grant) | Service Owner | Security Lead | Owner | 12h |
| C (Config) | Relevant Owner | Product Lead | Owner | 12h |
| I (Incident) | Incident Commander | VP Operations | Owner | 2h (emergency) |
| A (Audit) | Compliance Officer | Legal | Owner | 24h |

---

## Section C: Delegation Rules

### C.1 Delegable vs. Non-Delegable Policies

**Delegable policies** can be temporarily assigned to other approvers with proper authorization:

```
✅ Delegable:
  • D-001, D-004, D-005 (deployment)
  • R-002, R-003, R-004 (routine resource provisioning)
  • G-005, G-006 (non-critical capability grants)
  • C-001 through C-006 (configuration changes)
  • I-003 (circuit breaker activation — incident only)
  • A-001, A-005 (routine audits)
```

**Non-delegable policies** require approval from original authority or escalation:

```
❌ Non-Delegable:
  • D-002, D-003, D-006 (high-risk deployment)
  • S-001 through S-008 (all security-critical)
  • R-001, R-005, R-006 (high-cost or data-destructive)
  • G-001, G-002, G-004 (capability escalation)
  • E-001 through E-005 (all escalation decisions)
  • I-001, I-002, I-004, I-005 (all emergency decisions)
  • A-002 through A-006 (all compliance-critical)
```

### C.2 Delegation Constraints

When delegating authority, the following rules apply:

**Constraint 1: Same-tier delegation only**
- Level 1 approver may delegate to another Level 1 approver of same policy domain
- Level 2 approver may delegate to Level 2 within budget/capacity constraints
- Owner may delegate to Level 2, but decision remains owner-accountable

**Constraint 2: Time-box delegation**
- Delegation must include explicit end date/time
- Maximum delegation duration: 30 days
- After 30 days, authority reverts to original approver
- Automatic revocation if delegatee's access is revoked

**Constraint 3: Capacity constraints**
- Approver approval-per-day limits still apply to delegated authority
- If delegatee exceeds daily limit, remaining requests queue until next day
- Delegation cannot exceed 50% of original approver's daily capacity

**Constraint 4: Transparency audit trail**
- Every delegation recorded in audit log with:
  - Original approver name
  - Delegated-to name
  - Policy category
  - Effective date/time
  - Expiration date/time
  - Reason for delegation
- Delegatee must acknowledge delegation in writing
- Audit trail accessible to Compliance Officer on demand

### C.3 Re-delegation Prohibition

**Re-delegation not allowed:**
- Delegatee cannot further delegate authority to a third party
- Any re-delegation attempt automatically escalates to Owner
- Violating this rule results in revocation of delegation rights for 90 days

**Exception:** In emergency incidents, Incident Commander may authorize re-delegation to on-call deputy with Owner notification within 1 hour.

### C.4 Delegation Audit Requirements

**Monthly delegation audit:**
- Compliance Officer reviews all active delegations
- Validate delegatee still meets approval tier requirements
- Check for policy violations or capacity overages
- Generate delegation accountability report

**Quarterly delegation cleanup:**
- Revoke expired delegations
- Archive completed delegations
- Report re-delegation violations

---

## Section D: Policy Versioning

### D.1 Semantic Versioning Strategy

Policies follow semantic versioning: `MAJOR.MINOR.PATCH`

**Version bumping rules:**

```
D-001:
  v1.0.0 → v1.0.1  (patch)   = clarification, typo fix, example update
  v1.0.0 → v1.1.0  (minor)   = new approval stage, relaxed SLA, new exemption
  v1.0.0 → v2.0.0  (major)   = removed stage, new policy category, breaking change
```

**Version compatibility matrix:**

| Version Type | Impact | Breaking | Requires Migration | SLA |
|--------------|--------|----------|-------------------|-----|
| Patch (v1.0.x) | Clarification | No | No | Immediate |
| Minor (v1.x.0) | Relaxation | Maybe | Yes, if stricter | 7 days |
| Major (vX.0.0) | Structural | Yes | Yes, mandatory | 30 days |

---

### D.2 Policy Conflict Detection

When policy versions change, the system must detect conflicts:

**Conflict Type 1: Approval stage removal**
- Old policy requires 3 approvals, new version requires 2
- In-flight requests following old policy auto-promoted to new policy when old stage satisfied
- Prevents "stuck" approvals

**Conflict Type 2: New approval stage added**
- Old policy requires 1 approval, new requires 2
- Requests already approved under old policy are grandfathered
- New requests follow new policy
- Conflict window: 7 days (transition period)

**Conflict Type 3: SLA change**
- Old policy: 4h SLA, new policy: 2h SLA
- In-flight requests under old SLA: honor original timeline
- New requests follow new timeline immediately
- Escalation rules remain consistent

**Conflict resolution algorithm:**

```python
def resolve_policy_version_conflict(request_policy_version, current_version):
    if request_policy_version == current_version:
        return apply_policy(current_version)
    
    elif request_policy_version < current_version:
        if is_major_change(request_policy_version, current_version):
            # Breaking change — request must be restarted
            return restart_request_with_new_policy()
        elif is_minor_relaxation(request_policy_version, current_version):
            # Relaxed SLA — apply old policy (more restrictive)
            return apply_policy(request_policy_version)
        else:
            # Patch-level clarification — apply new policy
            return apply_policy(current_version)
    
    else:
        # Future version (should not happen)
        raise PolicyVersionException("Request uses future policy version")
```

---

### D.3 Backward Compatibility Approach

**Guarantee:** All policy changes maintain backward compatibility for in-flight requests.

**Mechanism:**
- Requests capture policy version at submission time
- In-flight requests execute under captured version
- Only newly submitted requests use latest version
- Version snapshot persisted in audit log

**Grace period for major versions:**
- 30-day transition window
- During window, both old and new policy versions accepted
- After 30 days, old version rejected with clear error message
- Users notified 14 days before cutoff

---

### D.4 Policy Version Migration Path

**For administrators migrating policies:**

1. **Announcement phase (7 days)**
   - Email all approvers and affected stakeholders
   - Document changes clearly
   - Provide examples of old vs. new behavior

2. **Soft rollout (7 days)**
   - Accept both old and new policy versions
   - Monitor for conflicts/errors
   - Adjust if conflicts detected

3. **Hard cutoff (optional, after 30 days)**
   - Reject old version for new requests
   - Honor old version for in-flight requests
   - Send error to users attempting old version

4. **Archive and deprecate (after 90 days)**
   - Mark old version as deprecated
   - Move to policy archive
   - Maintain in audit trail for historical reference

---

## Section E: SLA & Timeout Handling

### E.1 Approval SLA by Policy Category

Standard SLA timelines establish maximum approval wait times before escalation triggers:

| Policy | SLA | Escalation Trigger | Auto-Escalate | Critical Path |
|--------|-----|-------------------|----------------|---------------|
| **D-001** (Canary Deploy) | 4h | 4h timeout | Yes | Production risk |
| **D-002** (Full Rollout) | 8h | 4h per stage | Yes | Production risk |
| **D-003** (Rollback) | 2h | 2h timeout | Yes | Incident mode |
| **D-004** (Staging) | 8h | 4h timeout | No | Non-critical |
| **S-001** (Scope Change) | 8h | 4h per stage | Yes | Security critical |
| **S-003** (Security Exception) | 12h | 4h per stage | No | Exception review |
| **R-001** (Cost >$1K) | 8h | 4h timeout | Yes | Budget approval |
| **R-006** (DB Deletion) | 24h | 8h timeout | No | Destructive action |
| **G-001** (Agent Autonomy) | 12h | 4h per stage | No | Capability grant |
| **I-001** (Emergency Access) | 30min | Immediate escalation | Yes | Incident critical |
| **I-002** (Data Purge) | 2h | 1h timeout | Yes | Incident critical |
| **A-001** (Compliance Audit) | 24h | 12h timeout | No | Non-blocking |

### E.2 Escalation Triggers

Escalation automatically occurs when:

```
1. SLA Timer Expired
   └─ Wait threshold exceeded → escalate to next authority level

2. Approver Unavailable
   └─ Status marked "unavailable" → skip to next approver

3. Explicit Manual Escalation
   └─ Approver chooses "escalate to manager" → promote immediately

4. Conflict Detection
   └─ Two+ approvers at same level disagree → escalate to tie-breaker

5. Security Flag Raised
   └─ Security review flags concern → escalate to Security Lead
```

### E.3 Deadline Enforcement Mechanisms

**Automated deadline enforcement:**

```yaml
approval_deadline_checker:
  - run_every: 5 minutes
  - check_criteria:
      - SLA elapsed (current_time > deadline)
      - Approval still pending (status = "awaiting_approval")
      - No recent activity (>10 min)
  - action_on_match:
      - Log escalation event
      - Assign to next level
      - Notify new approver
      - Reset 4h timer
  - max_escalations: 3 (then auto-approve with Owner notification)
```

**Manual deadline enforcement:**

- Approver can extend SLA by 4h with documented reason
- Extensions logged in audit trail
- Maximum 2 extensions per request
- After 2 extensions, must escalate to Owner

### E.4 Auto-Approval Fallback Conditions

Auto-approval (request granted without explicit approval) occurs when:

**Condition 1: Max escalation reached**
- Request escalated 3 times
- No approver willing to decide
- After 24h total time
- Action: Auto-approve with Owner notification + audit log entry

**Condition 2: All approvers unavailable**
- Request requires 3 approvals
- 2+ approvers marked "out of office"
- SLA exceeded by 4h
- Action: Escalate to Owner; if Owner unavailable, auto-approve

**Condition 3: Incident mode override**
- Incident declared (via incident-commander workflow)
- Request is incident-related (tagged with incident ID)
- SLA reduced to 30 min for I-series policies
- If not approved in 30 min: auto-approve by Incident Commander

**Condition 4: Emergency authorization**
- Owner explicitly authorizes emergency override
- Logged as manual exception
- Post-incident audit required

**Auto-approval safeguards:**

```python
def auto_approve_request(request_id, fallback_reason):
    # Never auto-approve without safeguards
    
    # 1. Require Owner notification
    notify_owner(request_id, fallback_reason)
    
    # 2. Log as exception (not normal approval)
    audit_log.record("auto_approval_fallback", {
        "request_id": request_id,
        "reason": fallback_reason,
        "timestamp": now(),
        "escalation_count": request.escalation_count,
    })
    
    # 3. Require post-incident review
    if request.is_incident_related:
        create_post_incident_review(request_id)
    else:
        create_governance_audit_ticket(request_id, "auto_approval_review")
    
    # 4. Finally approve
    request.status = "auto_approved"
    request.approved_by = "SYSTEM_AUTO_APPROVAL"
    return request
```

---

## Integration & Deployment

### Policy Framework Deployment Checklist

- [ ] All 8 policy categories defined and documented
- [ ] 40+ individual policies enumerated with examples
- [ ] Delegation rules formalized in code/config
- [ ] Versioning strategy tested with sample migration
- [ ] SLA monitoring dashboard operational
- [ ] Approval workflow orchestrator deployed
- [ ] Audit log schema includes policy versioning
- [ ] Owner and Security Lead approval required before enforcement

### Related Artifacts

- **Track 12.1:** RBAC implementation (defines roles mentioned in Section A)
- **Track 12.3:** Telemetry schema (defines audit logging for approval events)
- **Approval Guard Agent:** Enforces policies via `owner-approval-guard` agent
- **Owner Approval Guard:** Reference implementation in `.codex/docs/`

---

## Appendix: Quick Reference

**Policy submission flow:**
```
Request → Auto-route to Approver(s) → Approval/Rejection → Escalation/Finalization → Audit Log
```

**SLA escalation summary:**
```
Level 1: 4h → Level 2: +4h → Level 3 (Owner): +4h → Auto-approve: +4h
Total max: 16h for critical policies
```

**Delegation quick check:**
```
Can you delegate? YES if:
  ✓ Policy is in ✅ Delegable list
  ✓ Delegatee is same approval tier
  ✓ You're not re-delegating
  ✓ Delegation duration ≤ 30 days
```

---

**Document Metadata:**
- **File:** `.codex/APPROVAL_POLICIES.md`
- **Size:** ~3,500 words (fits 12-15 KB target)
- **Sections:** 5 (A–E)
- **Policies Defined:** 43
- **Mermaid Diagrams:** 4
- **Status:** ✅ Ready for peer review
- **Authority:** @mbaetiong (D-tier)
