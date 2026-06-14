# RBAC Specification

**Version**: 1.0.0  
**Effective Date**: 2026-06-14  
**Classification**: Internal — Security Sensitive  
**Owner**: Security & Access Management Team  
**Last Updated**: 2026-06-14

---

## Table of Contents

1. [Overview](#overview)
2. [Role Hierarchy](#role-hierarchy)
3. [Permission Matrix](#permission-matrix)
4. [Service Account Management](#service-account-management)
5. [Privilege Escalation Controls](#privilege-escalation-controls)
6. [Access Management Procedures](#access-management-procedures)
7. [Audit & Compliance](#audit--compliance)

---

## Overview

### Purpose

This document defines the Role-Based Access Control (RBAC) system for the _codex_ platform, ensuring users and service accounts have minimal required permissions (least-privilege principle).

### Principles

1. **Least Privilege**: Every user/account has only required permissions
2. **Separation of Duties**: Critical functions require multiple approvals
3. **Time-Limiting**: Privileged access automatically expires
4. **Accountability**: All access logged and audited
5. **Defense in Depth**: Multiple layers of authorization checks

### Scope

- Repository access (GitHub)
- Production deployments
- CI/CD infrastructure
- Data and secrets access
- Administrative functions

---

## Role Hierarchy

### Role Definitions

```
┌──────────────────────────────────────────────────┐
│              RBAC Role Hierarchy                 │
├──────────────────────────────────────────────────┤
│                                                  │
│  Level 0 (Unrestricted)                         │
│  ├─ Owner                                        │
│  │  • Full repository control                    │
│  │  • All permissions                            │
│  │  • Cannot be revoked                          │
│  │  • Audit everything                           │
│  │                                               │
│  Level 1 (Privileged)                           │
│  ├─ Admin (system)                              │
│  │  • Deployment                                 │
│  │  • Secrets management                         │  # pragma: allowlist secret
│  │  • Security policies                          │
│  │  • 4-hour time limit (auto-expiry)            │
│  │  • Requires MFA + approval                    │
│  │                                               │
│  Level 2 (Elevated)                             │
│  ├─ Editor (write access)                       │
│  │  • Pull requests                              │
│  │  • Code commits                               │
│  │  • Branch protection bypass                   │
│  │  • Standard MFA required                      │
│  │                                               │
│  ├─ Reviewer (review access)                    │
│  │  • Code review                                │
│  │  • PR approval                                │
│  │  • Compliance sign-off                        │
│  │  • Standard MFA required                      │
│  │                                               │
│  ├─ Operator (operations)                       │
│  │  • Deploy to prod                             │
│  │  • View logs/metrics                          │
│  │  • Alert management                           │
│  │  • Standard MFA required                      │
│  │                                               │
│  Level 3 (Standard)                             │
│  ├─ Viewer (read-only)                          │
│  │  • View documentation                         │
│  │  • Read public files                          │
│  │  • View metrics/logs (non-sensitive)          │
│  │  • No secrets access                          │  # pragma: allowlist secret
│  │                                               │
│  Level 4 (Service Accounts)                     │
│  ├─ Service Account (scoped)                    │
│  │  • Specific actions only                      │
│  │  • No human access                            │
│  │  • Time-limited tokens                        │  # pragma: allowlist secret
│  │  • Automatic rotation                         │
│  │                                               │
└──────────────────────────────────────────────────┘
```

### Role Characteristics

| Role | Tier | Time Limit | MFA | Approval | Audit |
|------|------|-----------|-----|----------|-------|
| Owner | 0 | None | Required | N/A | 100% |
| Admin | 1 | 4 hours | Required | 2/2 | 100% |
| Editor | 2 | None | Required | None | 100% |
| Reviewer | 2 | None | Required | None | 100% |
| Operator | 2 | None | Required | None | 100% |
| Viewer | 3 | None | Optional | None | Spot |
| Service Acct | 4 | 30-180 days | N/A | N/A | 100% |

---

## Permission Matrix

### Core Permissions

| Permission | Description | Owner | Admin | Editor | Reviewer | Operator | Viewer | Service |
|---|---|---|---|---|---|---|---|---|
| `repo:read` | Read repository | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅* |
| `repo:write` | Write to repository | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| `repo:admin` | Repository administration | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `branch:protect:write` | Modify branch protection | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `branch:protect:bypass` | Bypass protection | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |

### Deployment Permissions

| Permission | Description | Owner | Admin | Editor | Operator |
|---|---|---|---|---|---|
| `deploy:read` | View deployments | ✅ | ✅ | ❌ | ✅ |
| `deploy:write` | Deploy (staging) | ✅ | ✅ | ✅ | ✅ |
| `deploy:prod` | Deploy to production | ✅ | ✅* | ❌ | ✅* |
| `deploy:rollback` | Rollback deployment | ✅ | ✅* | ❌ | ✅* |
| `deploy:approve` | Approve deployment | ✅ | ❌ | ❌ | ❌ |

*Requires secondary approval

### Secrets Management

| Permission | Description | Owner | Admin | Others |
|---|---|---|---|---|
| `secret:read` | Read secrets | ✅ | ✅ | ❌ | <!-- pragma: allowlist secret -->
| `secret:write` | Create/update secrets | ✅ | ✅ | ❌ | <!-- pragma: allowlist secret -->
| `secret:rotate` | Rotate secrets | ✅ | ✅ | ❌ | <!-- pragma: allowlist secret -->
| `secret:delete` | Delete secrets | ✅ | ❌ | ❌ | <!-- pragma: allowlist secret -->

### Security & Compliance

| Permission | Description | Owner | Admin |
|---|---|---|---|
| `security:audit` | View audit logs | ✅ | ✅ |
| `security:config` | Update security policies | ✅ | ❌ |
| `security:incident` | Create incidents | ✅ | ✅ |
| `security:keys:manage` | Manage encryption keys | ✅ | ❌ |

---

## Service Account Management

### Predefined Service Accounts

#### 1. `codex-ci-deploy`

**Purpose**: CI/CD deployment automation  
**Permissions**:
- `repo:read` (all branches)
- `deploy:write` (staging + production)
- `logs:read` (CI/CD logs only)

**Token Expiry**: 90 days  
**Rotation**: Quarterly  
**Scope**: GitHub Actions workflows only

**Usage**:
```yaml
# .github/workflows/deploy.yml
- name: Deploy Application
  env:
    GITHUB_TOKEN: ${{ secrets.CODEX_CI_DEPLOY_TOKEN }}
  run: ./scripts/deploy.sh
```

#### 2. `codex-security-scan`

**Purpose**: Security scanning and compliance  
**Permissions**:
- `repo:read` (all branches)
- `code:scan:read` (CodeQL)
- `security:audit` (log access)

**Token Expiry**: 90 days  
**Rotation**: Quarterly  
**Scope**: Security scanning workflows only

#### 3. `codex-monitoring`

**Purpose**: Observability and alerting  
**Permissions**:
- `logs:read` (application logs)
- `metrics:read` (Prometheus/Grafana)
- `alerts:read|write` (alert management)

**Token Expiry**: 180 days  
**Rotation**: Semi-annually  
**Scope**: Monitoring systems only

#### 4. `codex-backup`

**Purpose**: Data archival and backup  
**Permissions**:
- `data:read` (database snapshots)
- `storage:write` (backup storage)
- `logs:read` (backup logs)

**Token Expiry**: 180 days  
**Rotation**: Semi-annually  
**Scope**: Backup infrastructure only

#### 5. `codex-api-internal`

**Purpose**: Internal service-to-service calls  
**Permissions**:
- `api:call` (internal APIs only)
- Restricted to internal IP ranges
- Cannot access external systems

**Token Expiry**: 30 days  
**Rotation**: Monthly  
**Scope**: Internal service communication

### Service Account Creation

**Process**:
1. Submit request via GitHub Issue: `service-account-request`
2. Security review: Purpose, permissions, expiry
3. Approval: 2/2 review required
4. Creation: Automated via GitHub Actions
5. Distribution: Encrypted to requesting team
6. Rotation: Scheduled automatically

**Request Template**:
```yaml
Service Account Name: codex-new-service
Purpose: [Specific functionality required]
Permissions: [Required permissions]
Token Lifetime: [30/90/180 days]
Justification: [Business need]
Owner: [Team lead name]
```

---

## Privilege Escalation Controls

### Escalation Requirements

#### Admin Role Escalation

**Trigger**: Request admin access for critical operation

**Approval Process**:
```
User Request
    ↓
    [Create GitHub Issue: "admin-access-request"]
    ↓
Require: 2/2 Approval (different teams)
    ├─ Security Team: Security implications review
    └─ Operations Team: Business justification review
    ↓
[If approved] Generate temporary admin token (4 hours)  # pragma: allowlist secret
    ↓
    [User performs privileged action]
    ↓
    [Token auto-expires after 4 hours]  # pragma: allowlist secret
    ↓
    [Action logged with full audit trail]
```

**Auto-Expiry**: 4 hours (non-extendable)

**Audit Trail**:
- Who requested escalation
- Why (business justification)
- When escalation was granted
- What actions performed
- When token expired

#### Emergency Escalation

**For critical incidents only (P0/P1)**:
```
Emergency Detection
    ↓
    [Create GitHub Issue: "SECURITY: Emergency escalation"]
    ↓
    Notify: Security Lead + On-call Engineer
    ↓
    [Grant 1-hour emergency admin access]
    ↓
    [Automatic escalation to all approvers]
    ↓
    [Post-incident review required]
```

### Privilege Escalation Prevention

#### 1. Rate Limiting

- Max 3 escalation requests per user per week
- Max 10 concurrent admin sessions
- Max 5 emergency escalations per day (org-wide)

#### 2. Anomaly Detection

Monitor and alert on:
- Escalation outside normal work hours
- Escalation from unusual location (VPN)
- Escalation for account with no prior usage
- Multiple escalations from same user (potential compromise)

#### 3. Secondary Authentication

All escalations require:
- MFA (2-factor minimum)
- GitHub approval (interactive UI, not bot)
- Reason documentation

#### 4. Access Control

Escalated users cannot:
- Escalate further (cannot request super-admin)
- Create new service accounts
- Modify security policies
- Delete audit logs

### Automatic Privilege Removal

Permissions automatically removed when:
- User employment ends (immediate)
- User transfers teams (re-request with new team)
- 90 days of no usage (notification + 7-day cure)
- Policy violation detected (immediate)
- User requests removal (immediate)

---

## Access Management Procedures

### Onboarding (New Team Member)

**Timeline**: 1 business day before start date

```
1. Create GitHub account + MFA setup
   └─ New employee completes
   
2. Request initial access via form
   └─ Manager approves
   
3. Grant Viewer role (read-only)
   └─ Automatic grant for all new members
   
4. Role escalation (if needed)
   └─ Team lead requests specific role
   └─ Security reviews and approves
   └─ Role assigned
   
5. Team setup (team-specific access)
   └─ Add to GitHub team
   └─ Add to deployment group
   └─ Configure team permissions
   
6. First-day setup
   └─ SSH key registration
   └─ Local environment setup
   └─ Secrets management training  # pragma: allowlist secret
```

### Offboarding (Departing Team Member)

**Timeline**: On final day

```
1. Disable GitHub account access
   └─ Immediate (no grace period)
   
2. Revoke all API tokens  # pragma: allowlist secret
   └─ Immediate
   
3. Disable SSH keys
   └─ Immediate
   
4. Clear local secrets/credentials  # pragma: allowlist secret
   └─ Assisted by IT
   
5. Archive access history
   └─ 90-day retention for legal
   
6. Notify security team
   └─ Send offboarding summary
   
7. Remove from all deployment groups
   └─ Immediate
   
8. Audit verification
   └─ Confirm access fully removed
```

### Role Change Request

**Process**:
1. Manager submits role change request (GitHub Issue)
2. Current role permissions audited
3. New role permissions reviewed
4. Security approves (new role is least-privilege)
5. Old role permissions revoked
6. New role permissions granted
7. Change logged in audit trail

---

## Audit & Compliance

### Access Audit Trail

**All access events logged**:
- Authentication (success/failure)
- Authorization (grant/deny)
- Permission usage (what was accessed)
- Administrative changes (role updates)
- Secret access (who read what secret)
- Privilege escalation (requests + approvals)

**Retention**:
- Security events: 1 year
- Audit trails: 7 years
- Compliance records: Indefinite

### Quarterly Access Review

**Process**:
1. Generate access report for all users/service accounts
2. Review: Is each access still needed?
3. Owner/Team Lead approval required
4. Any unused access revoked immediately
5. Report filed for compliance

**Audit Questions**:
- [ ] Does user still need this access?
- [ ] Is role appropriate for current duties?
- [ ] Have permissions been used in past 90 days?
- [ ] Any suspicious access patterns?

### Compliance Reports

**Monthly**: Access change summary
- New users added
- Roles changed
- Service accounts rotated
- Escalations granted

**Quarterly**: Comprehensive access audit
- All users and their permissions
- All service accounts status
- Privilege escalation summary
- Policy violations

**Annually**: Full compliance certification
- Access control policy adherence
- Least-privilege verification
- Audit trail integrity
- Incident impact review

### Policy Violations

**Detection**:
- Automated monitoring for permission anomalies
- Quarterly manual review
- User/manager reporting

**Response**:
1. Immediate notification to user + manager
2. Investigation into cause
3. Access review and correction
4. Training if needed
5. Document in compliance record

---

## Related Documents

- **Secret Rotation Policy**: `docs/production/SECRET_ROTATION_POLICY.md`
- **Incident Response**: `docs/operations/INCIDENT_RESPONSE_PLAYBOOKS.md`
- **Security Policy**: `SECURITY.md`
- **Production Readiness**: `docs/production/PRODUCTION_READINESS_CHECKLIST.md`

---

**Approved By**: Security & Access Management Team  
**Effective Date**: 2026-06-14  
**Review Frequency**: Semi-annually  
**Next Review**: 2026-12-14

---

*This specification is mandatory for all access control in the _codex_ platform.*
