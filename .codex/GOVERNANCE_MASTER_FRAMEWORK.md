# Governance & Policy Master Framework

> **Consolidated Master Document** for Codex Governance  
> **Created**: 2026-07-08  
> **Consolidation Campaign**: Phase 12 WS3  
> **Status**: ✅ Active Master Document

**Consolidated from** 5 source files:
- docs/admin/GOVERNANCE.md
- .codex/GOVERNANCE_POLICY_FRAMEWORK.md
- .codex/LANE_9_GOVERNANCE_REPORT.md
- .codex/BATCH_2_GOVERNANCE_FRAMEWORK.md
- .codex/GOVERNANCE_PATTERNS_REFERENCE.md

---

## Table of Contents

1. [Governance Overview](#governance-overview)
2. [Decision Framework](#decision-framework)
3. [Policy Matrix](#policy-matrix)
4. [Domain Ownership](#domain-ownership)
5. [RBAC System](#rbac-system)
6. [AI Agency Policy](#ai-agency-policy)
7. [Compliance Verification](#compliance-verification)
8. [Governance Patterns](#governance-patterns)

---

## Governance Overview

### Governance Tiers

```
┌─────────────────────────────────┐
│ Level 4: Repository Governance  │ ← MASTER POLICIES
│ (Strategic decisions)           │
├─────────────────────────────────┤
│ Level 3: Domain Governance      │ ← DOMAIN RULES
│ (D1-D4 policies)                │
├─────────────────────────────────┤
│ Level 2: Feature Governance     │ ← FEATURE GATES
│ (Agent/workflow rules)          │
├─────────────────────────────────┤
│ Level 1: Operational Rules      │ ← DAY-TO-DAY
│ (Error handling, retries)       │
└─────────────────────────────────┘
```

### Governance Scope

| Scope | Audience | Authority | Enforcement |
|-------|----------|-----------|-------------|
| **Repository** | All contributors | Repository owner | GitHub settings, policies |
| **Domain (D1-D4)** | Domain team | Domain owner | import-linter, agents |
| **Feature** | Feature team | Feature lead | Feature flags, gates |
| **Operational** | All systems | Ops team | Monitoring, alerts |

---

## Decision Framework

### Decision Types

**Type 1: Strategic Decisions** (Repository-level)
- Architecture changes (major refactors)
- New agent ecosystems
- Major policy changes
- Technology upgrades

**Decision Process**:
1. RFC (Request for Comments) in GitHub Discussions
2. 7-day review period
3. Team consensus required
4. Implementation by assigned owner
5. Post-implementation audit

**Type 2: Domain Decisions** (Domain-level)
- New features within domain
- API changes
- Policy clarifications
- Tool selection

**Decision Process**:
1. Domain owner proposes
2. 3-day review by team
3. Document in domain spec
4. Implement and monitor

**Type 3: Operational Decisions** (Day-to-day)
- Bug fixes
- Performance tuning
- Documentation updates
- Tool configuration

**Decision Process**:
1. Developer decides
2. PR review & approval
3. Merge to main
4. Verify via tests/checks

### Decision Recording

```yaml
# decisions/ADR-0001-agent-consolidation.md
---
status: accepted
date: 2026-07-08
authors: [mbaetiong]
---

# ADR-0001: Consolidate Documentation Agents

## Context
Multiple documentation agents created independently.

## Decision
Consolidate into unified-doc-agent v1.0.

## Consequences
- Reduced cognitive load (100+ agents → 50+)
- Unified tool access
- Consistent behavior
- Deprecated agents archived
```

---

## Policy Matrix

### Core Policies

| Policy | Owner | Scope | Reference |
|--------|-------|-------|-----------|
| **AI Agency Policy** | Repo Lead | Repository | `.codex/CODEBASE_AGENCY_POLICY.md` |
| **RBAC Policy** | Security Lead | Repository | `patch_rbac_engine.py` |
| **Domain Policy** | Domain Owner | Domain (D1-D4) | `.codex/DOMAIN_OWNERSHIP.md` |
| **Compliance Policy** | Compliance Lead | Repository | `docs/production/POLICY_COMPLIANCE_CHECKLIST.md` |
| **Secret Policy** | Security Lead | Repository | `docs/production/SECRETS_SCOPE_POLICY.md` |
| **Retention Policy** | Data Lead | Repository | `.codex/RETENTION_POLICY.md` |

### Policy Precedence

```
1. Legal/Regulatory Requirements (immutable)
2. AI Agency Policy (repository-wide)
3. Domain Policies (domain-specific)
4. Feature Policies (feature-specific)
5. Operational Guidelines (day-to-day)
```

### Policy Application

```yaml
# Example: Secret Rotation Policy
policy_name: SECRET_ROTATION_POLICY
scope: Repository-wide
applies_to: All secrets, tokens, credentials

rules:
  - rule_id: SR-1
    requirement: "Rotate secrets quarterly"
    enforcement: "GitHub Actions scheduled job"
    owner: "Security Team"
    
  - rule_id: SR-2
    requirement: "Audit secret access monthly"
    enforcement: "CloudTrail logs, GitHub audit"
    owner: "Compliance Lead"
    
  - rule_id: SR-3
    requirement: "Immediate rotation on compromise"
    enforcement: "Emergency procedure"
    owner: "On-call security"
```

---

## Domain Ownership

### Domain Structure

**Domain 1 (D1): Architecture & Layer Boundaries**
```yaml
owner: code-analysis-agent
scope:
  - src/codex/
  - src/codex_ml/
  - training/
  - src/services/
  - cli/, apps/

responsibilities:
  - Enforce layer boundaries
  - Approve architecture changes
  - Maintain import linter config
  - Document layer decisions

reference:
  - docs/architecture/ARCHITECTURE_LAYERS.md
  - .importlinter
  - import-linter.yml

enforcement:
  - CI/CD checks (import-linter)
  - Code review (domain owner approval)
  - Automated scanning
```

**Domain 2 (D2): Security & Compliance**
```yaml
owner: security-review-agent
scope:
  - docs/security/
  - Authentication & authorization
  - Encryption & key management
  - Vulnerability scanning
  - Compliance monitoring

responsibilities:
  - Security audits
  - Vulnerability management
  - Policy enforcement
  - Incident response

enforcement:
  - GitHub Advanced Security
  - CodeQL scanning
  - Dependabot updates
  - Secret scanning
```

**Domain 3 (D3): Testing & Quality**
```yaml
owner: ci-testing-agent
scope:
  - Test infrastructure
  - Quality gates
  - Coverage thresholds
  - CI/CD pipeline

responsibilities:
  - Maintain test suite
  - Set coverage targets
  - Manage CI workflows
  - Quality metrics

enforcement:
  - pytest coverage gates
  - CI workflow checks
  - Performance baselines
```

**Domain 4 (D4): Agent & Orchestration**
```yaml
owner: orchestrator-agent
scope:
  - Agent ecosystem
  - Agent registry
  - Skill marketplace
  - Multi-agent coordination

responsibilities:
  - Agent lifecycle management
  - Skill discovery & training
  - Registry maintenance
  - Orchestration logic

enforcement:
  - Agent registry validation
  - Deployment gates
  - IQ scoring system
```

---

## RBAC System

### Role Hierarchy

```
┌─────────────────────┐
│  Repository Owner   │ ← Full access to everything
│  (1 person)         │
├─────────────────────┤
│  Core Maintainers   │ ← Merge PRs, manage releases
│  (3-5 people)       │
├─────────────────────┤
│  Domain Owners      │ ← Approve domain changes
│  (4 people)         │
├─────────────────────┤
│  Contributors       │ ← Create PRs, issues
│  (Open)             │
├─────────────────────┤
│  Bots / Agents      │ ← Automated operations
│  (10+ agents)       │
└─────────────────────┘
```

### Permission Mapping

```yaml
repository_owner:
  - merge_pr: true
  - force_push: true
  - manage_secrets: true
  - manage_workflows: true
  - delete_branches: true
  - approve_codeql: true

core_maintainer:
  - merge_pr: true
  - manage_secrets: false
  - manage_workflows: true
  - delete_branches: false
  - approve_codeql: true

domain_owner:
  - merge_pr: true (domain only)
  - manage_secrets: false
  - manage_workflows: false
  - approve_domain_changes: true
  - approve_codeql: false

contributor:
  - create_pr: true
  - create_issue: true
  - merge_pr: false
  - manage_secrets: false
  - manage_workflows: false

bot_agent:
  - create_pr: true
  - auto_merge: true (specific branches)
  - manage_workflows: false
  - access_secrets: true (scoped)
```

### RBAC Enforcement

```python
# patch_rbac_engine.py
from rbac import enforce_permission

@enforce_permission("merge_pr")
def merge_pull_request(pr_number):
    """Merge PR - only for authorized users."""
    # Implementation
    pass

@enforce_permission("manage_secrets")
def rotate_secret(secret_name):
    """Rotate secret - only for authorized users."""
    # Implementation
    pass

@enforce_permission("approve_codeql")
def approve_codeql_alert(alert_id):
    """Approve CodeQL alert - only for authorized users."""
    # Implementation
    pass
```

---

## AI Agency Policy

### Policy Statement

**Purpose**: Ensure AI agents operate within defined boundaries and with appropriate oversight.

**Authority**: Repository owner  
**Scope**: All agents, all operations  
**Effective Date**: 2026-01-23  
**Review Cycle**: Quarterly

### Core Principles

1. **Transparency**: All agent actions logged and auditable
2. **Accountability**: Clear ownership for each agent
3. **Oversight**: Human review gates for critical operations
4. **Limits**: Bounded autonomy based on trust level
5. **Escalation**: Automatic escalation for exceptions

### Agent Autonomy Levels

```
Level E (Full Autonomy):
  - Agent: orchestrator, skills-master
  - Scope: Agent ecosystem management
  - Oversight: Post-action audit
  - Example: Route tasks to specialized agents

Level D (High Autonomy):
  - Agent: ci-auto-healer, unified-coverage-agent
  - Scope: CI/CD fixes, test coverage
  - Oversight: Human review if changes large (>50 lines)
  - Example: Auto-fix failing CI tests

Level C (Managed Autonomy):
  - Agent: codeql-alert-resolution, security-audit
  - Scope: Security/compliance actions
  - Oversight: 100% human review before merge
  - Example: Propose security fixes

Level B (Supervised):
  - Agent: code-review, research
  - Scope: Analysis and reporting
  - Oversight: Human interpretation required
  - Example: Code review recommendations

Level A (Advisory):
  - Agent: documentation-quality, link-validator
  - Scope: Suggestions and reports
  - Oversight: 0% - purely advisory
  - Example: Documentation quality checks
```

### Compliance Gates

```yaml
gate_1_discovery:
  check: Agent registered in AGENT_REGISTRY.yaml
  enforcement: Pre-deployment validation
  
gate_2_capability_audit:
  check: Tool access matches intended scope
  enforcement: Tool whitelist enforcement
  
gate_3_autonomy_classification:
  check: Agent assigned autonomy level (A-E)
  enforcement: Capability gates based on level
  
gate_4_iq_scoring:
  check: Agent passes IQ minimum (65/100)
  enforcement: Deployment blocked if below threshold
  
gate_5_human_oversight:
  check: Oversight mechanism configured
  enforcement: Logging, alerting, human review
```

---

## Compliance Verification

### Audit Checklist

- [ ] AI Agency Policy compliance
- [ ] RBAC rules enforced
- [ ] Domain boundaries respected
- [ ] Secret rotation current
- [ ] Dependency vulnerabilities patched
- [ ] Code coverage above threshold
- [ ] Security scanning enabled
- [ ] Audit logs retained
- [ ] Incident response plan current
- [ ] Compliance documentation updated

### Compliance Reports

```bash
# Run compliance audit
python scripts/compliance/audit.py

# Output:
# ✅ AI Agency Policy: 100% compliant
# ✅ RBAC: 100% enforced
# ✅ Domain boundaries: 0 violations
# ⚠️  Secret rotation: Due in 3 days
# ✅ Coverage: 87% (target: 80%)
# ✅ Security scanning: Enabled
```

### Non-Compliance Resolution

1. **Issue Identification**: Compliance scan finds violation
2. **Alert**: Notification to responsible team
3. **Investigation**: Determine root cause
4. **Remediation**: Create fix plan
5. **Implementation**: Execute fix
6. **Verification**: Re-run compliance scan
7. **Documentation**: Record resolution

---

## Governance Patterns

### Pattern 1: Feature Flag Governance

```yaml
feature_flags:
  new_agent_framework:
    owner: orchestrator-agent
    status: beta
    rollout: 5%
    criteria:
      - Success rate > 95%
      - Latency < 100ms
      - IQ score > 80
    escalation:
      - If success rate < 95%: rollback
      - If latency > 100ms: optimize
      - If IQ < 80: retrain

gradient_rollout:
  5% → 25% → 50% → 100%
  (each step requires verification)
```

### Pattern 2: Change Governance

```yaml
change_type: Major API Change
approval_required:
  - domain_owner: true
  - security_review: true
  - code_review: true
  - test_coverage: "> 80%"

documentation:
  - Migration guide required
  - Changelog entry required
  - Breaking changes documented

rollout:
  - Beta period: 1 week
  - Deprecation period: 2 weeks
  - Hard cutover after deprecation
```

### Pattern 3: Exception Handling

```yaml
exception_type: Deploy to production outside change window
normal_process:
  - Request must be submitted 48h in advance
  - Approved by core maintainer
  - Execute during change window (Monday 2-4pm UTC)

exception_process:
  - Requires repository owner approval
  - Requires security review
  - Requires incident response team on-call
  - Document exception reasoning
  - Post-incident review required
```

---

## Governance Calendar

### Recurring Activities

**Weekly**:
- Governance review meeting
- RBAC access review
- Security incident triage

**Monthly**:
- Compliance audit
- Domain policy review
- Agent IQ review
- Change log review

**Quarterly**:
- AI Agency Policy review
- RBAC audit
- Governance process improvement
- Compliance training

**Annually**:
- Governance framework review
- Security audit
- Compliance certification
- Policy updates

---

**This document is the authoritative governance and policy framework for Codex.**

*Last Updated: 2026-07-08*  
*Consolidation Status: ✅ Complete (5 files merged)*
