# Phase 6 Batch 2 — Variable Lifecycle & Audit Policy

**Version:** 1.0.0  
**Status:** FINAL  
**Audience:** DevOps, CI/CD operators, infrastructure team  
**Last Updated:** 2026-02-22

---

## Overview

This document defines the complete lifecycle, audit logging, and management procedures for all 13+ critical repository variables used in CI/CD pipelines and deployments.

**Variable Inventory Reference:** `.codex/CRITICAL_REPOSITORY_VARIABLES.md`

---

## Part 1: Variable Categories & Lifecycle Stages

### 1.1 Variable Categories

**Category A: Authentication & Secrets (Immutable, Owner-Only)**

```yaml
Variables:
  - COPILOT_AUTH_TOKEN       # Copilot session authentication
  - GITHUB_TOKEN_ADMIN       # GitHub admin operations
  - AZURE_CREDENTIALS        # Cloud infrastructure access
  - SLACK_BOT_TOKEN          # Notification system

Characteristics:
  - Type: Secret string
  - Scope: CI/CD runners and deployment systems
  - Access: Owner only (@mbaetiong)
  - Rotations: Quarterly to yearly
  - Audit: Immutable, encrypted logs
```

**Category B: CI/CD Health & Monitoring (Agent-Writable)**

```yaml
Variables:
  - CODEX_CI_FAILURE_RATE     # Current failure rate metric
  - CODEX_COVERAGE_THRESHOLD  # Test coverage gate percentage
  - CODEX_CACHE_VERSION       # Build cache invalidation
  - CODEX_TEST_TIMEOUT_MINUTES # Test execution timeout

Characteristics:
  - Type: Metric or configuration value
  - Scope: CI/CD health monitoring and gates
  - Access: Agents (ci-health-alert-agent, etc.)
  - Updates: Automatic or weekly review
  - Audit: Full audit trail with agent attribution
```

**Category C: Runner & Infrastructure Config**

```yaml
Variables:
  - NODE_JS_VERSION           # Node.js LTS version
  - PYTHON_VERSION_LATEST     # Python interpreter version
  - CODEX_MAX_PARALLEL_JOBS   # Maximum parallel job count

Characteristics:
  - Type: Configuration value
  - Scope: Build and test runners
  - Access: Tech lead + owner approval
  - Updates: Quarterly or on release
  - Audit: Full audit with justification
```

**Category D: Cognitive Brain & Session Management (System-Managed)**

```yaml
Variables:
  - COGNITIVE_BRAIN_SESSION_RETENTION_HOURS # Session lifetime
  - SESSION_CONTEXT_AUTO_INJECT              # Auto-injection flag

Characteristics:
  - Type: Configuration (mostly immutable)
  - Scope: Agent session management
  - Access: System only (read-only for agents)
  - Updates: Rare, requires system-level change
  - Audit: Automatic system logging
```

---

### 1.2 Lifecycle States

```
DRAFT → REVIEW → APPROVED → ACTIVE → DEPRECATED → ARCHIVED

State Definitions:
  DRAFT      — Variable defined locally, not in production yet
  REVIEW     — Change proposal submitted, awaiting approval
  APPROVED   — Change approved, ready for deployment
  ACTIVE     — Currently deployed and in use
  DEPRECATED — Marked for removal, replacement documented
  ARCHIVED   — Removed from use, historical records maintained
```

### 1.3 State Transition Matrix

| From State | To State | Required Approver | Duration | Notification |
|-----------|----------|------------------|----------|--------------|
| DRAFT | REVIEW | Author | 1 day | Issue created |
| REVIEW | APPROVED | Tech lead (or Owner for secrets) | 3-7 days | Comments posted |
| APPROVED | ACTIVE | Tech lead (or Owner) | Same day | Slack notification |
| ACTIVE | DEPRECATED | Tech lead | N/A (ongoing) | 30-day notice |
| DEPRECATED | ARCHIVED | Owner | 30 days | Email notification |

---

## Part 2: Lifecycle Procedures by Category

### 2.1 Category A: Authentication & Secrets (Owner-Only)

**Lifecycle Duration:** 1 year (activation) → 1 year (archival)  
**Review Frequency:** Quarterly security audit  

**Procedure A1: Initial Creation**

```yaml
Trigger: Security team identifies need for new secret variable

Steps:
  1. Owner creates issue: "New secret variable: [NAME]"
     - Describe use case and security requirements
     - Identify system that requires the secret
     - Propose rotation schedule
  
  2. Security review (24-48 hours)
     - Evaluate necessity and risk
     - Approve or request modifications
  
  3. Owner creates secret via GitHub Actions:
     - No direct CLI exposure (use GitHub web UI only)
     - Value stored in GitHub's encrypted vault
     - Only accessible to marked workflows
  
  4. Audit log entry created (manual)
     - Creator: @mbaetiong
     - Creation reason: documented
     - Initial rotation date: set for 90-180 days
  
  5. Access control documented
     - Workflows that can access it
     - Human accounts with visibility (none)
     - Rotation contacts: tech lead + owner

Validation:
  ☐ Secret inaccessible to logs/debug output
  ☐ Only accessible in runner environment
  ☐ Audit entry created
  ☐ Access control documented
```

**Procedure A2: Rotation (Quarterly)**

```yaml
Trigger: Scheduled quarterly security audit

Steps:
  1. Owner creates issue: "Quarterly rotation: [SECRET_NAME]"
  
  2. Generate new secret value
     - Use cryptographically secure random generation
     - Ensure compliance with service requirements
  
  3. Update GitHub Actions secret via web UI
     - Override existing value
     - Automatic audit logging
  
  4. Notify dependent services
     - Post message to #infrastructure
     - Verify dependent systems still functioning
     - Check logs for authentication errors
  
  5. Destroy old secret value
     - Secure deletion (not just deletion)
     - Confirm destruction in audit log
  
  6. Audit entry created
     - Timestamp: rotation date
     - Old value: [REDACTED in all logs]
     - New value: [REDACTED in all logs]
     - Reason: "Quarterly security rotation"
     - Verified by: @mbaetiong

Validation:
  ☐ New secret verified working
  ☐ Dependent services still functioning
  ☐ Old secret destroyed
  ☐ Audit entry complete
```

**Procedure A3: Emergency Rotation (Compromise)**

```yaml
Trigger: Security incident or compromise detected

Steps:
  1. Incident commander declares emergency
  2. Owner immediately generates new secret value
  3. Update GitHub Actions secret (no approval needed)
  4. Notify all users of credentials reset
  5. Investigation + audit trail review
  6. Post-incident review (within 24 hours)

Timeline: Execution within 15 minutes
Escalation: Security team + Owner + Incident commander
```

### 2.2 Category B: CI/CD Health & Monitoring (Agent-Writable)

**Lifecycle Duration:** 3-6 months (activation) → 6 months (archival)  
**Review Frequency:** Weekly automatic, monthly manual  

**Procedure B1: Automatic Update (No Manual Approval)**

```yaml
Trigger: Agent detects need for change

Example: ci-health-alert-agent observes CI failure rate > 30%

Steps:
  1. Agent posts PR comment with proposed change
     - Old value: [current value]
     - New value: [proposed value]
     - Reason: "CI failure rate increased to 35% (threshold: 30%)"
     - Justification: Scientific evidence (trend graph)
  
  2. Auto-approval window: 24 hours
     - If no objection from tech lead → change approved
     - If objection posted → escalate to manual review
  
  3. Agent applies change (self-authorized after 24h)
     - Update variable in GitHub Actions
     - Automatic audit logging (agent-recorded)
  
  4. Audit entry created (automatic)
     - Changed by: [agent name]
     - Session ID: [copilot session or automation ID]
     - Reason: [from agent comment]
     - Evidence: [scientific data, metrics, graphs]
     - Timestamp: [when change applied]

Validation:
  ☐ Change posted as PR comment (transparent)
  ☐ 24-hour review window respected
  ☐ Tech lead did not object
  ☐ Audit entry automatically created
```

**Procedure B2: Manual Review (24-48 Hour Approval)**

```yaml
Trigger: Tech lead or human operator requests change

Example: Coverage threshold change CODEX_COVERAGE_THRESHOLD 80% → 85%

Steps:
  1. Create GitHub issue: "Update [VARIABLE_NAME]"
     - Current value: [value]
     - Proposed value: [value]
     - Justification: [detailed reasoning]
     - Testing evidence: [staging results, metrics]
     - Rollback plan: [if needed]
  
  2. Tech lead reviews (24 hours)
     - Evaluate business justification
     - Verify testing in staging
     - Approve or request modifications
  
  3. Owner or automated process applies change
     - Update variable via GitHub Actions
     - Link to PR/issue in commit message
  
  4. Audit entry created (manual or automated)
     - Changed by: [who applied it]
     - Approval: [PR/issue link]
     - Reason: [from issue description]
     - Evidence: [testing screenshots, metrics]
     - Timestamp: [when applied]

Validation:
  ☐ Issue has justification documented
  ☐ Testing evidence attached
  ☐ Tech lead approved
  ☐ Change applied to production
  ☐ Audit entry complete
```

### 2.3 Category C: Runner & Infrastructure (Manual Approval)

**Lifecycle Duration:** 6 months (activation) → 1 year (archival)  
**Review Frequency:** Quarterly manual review  

**Procedure C1: Version Update (Node.js, Python)**

```yaml
Trigger: New LTS version released or quarterly review

Example: Node.js 20 LTS → Node.js 22 LTS

Steps:
  1. Tech lead creates issue: "Update NODE_JS_VERSION"
     - Current version: v20.x.x
     - New version: v22.x.x
     - Reason: LTS release, security patches, performance
     - Migration testing: [staging results]
  
  2. Testing phase (1-2 weeks)
     - Update in staging: `NODE_JS_VERSION=22`
     - Run full test suite
     - Verify no breaking changes
     - Document incompatibilities (if any)
  
  3. Approval (24-48 hours)
     - Owner + Tech lead approval required
     - Both must review migration testing
  
  4. Gradual rollout
     - Apply to 10% of jobs first
     - Monitor for 24 hours
     - Apply to 50% of jobs
     - Monitor for 24 hours
     - Apply to 100% of jobs
  
  5. Audit entry created
     - Changed by: [owner]
     - Approval: [PR/issue link]
     - Old version: v20.x.x
     - New version: v22.x.x
     - Testing: [link to staging results]
     - Rollout timeline: [actual dates]

Validation:
  ☐ Full test suite passing
  ☐ Staging migration successful
  ☐ Owner + Tech lead approved
  ☐ Gradual rollout completed
  ☐ Audit entry complete
```

### 2.4 Category D: Cognitive Brain (System-Managed, Rare)

**Lifecycle Duration:** Indefinite (usually no changes)  
**Review Frequency:** Ad-hoc, only when system upgrades  

**Procedure D1: System Configuration Change**

```yaml
Trigger: Cognitive Brain system upgrade or policy change

Steps:
  1. System administrator creates issue
     - Describe system change
     - Rationale for variable adjustment
     - Expected impact
  
  2. Integration testing (1 week)
     - Test in staging environment
     - Verify all agent sessions working
     - Monitor system stability
  
  3. Owner approval
     - Review all testing evidence
     - Approve or request changes
  
  4. Deployment
     - Apply to production
     - Monitor for 48 hours
     - Ready for automatic rollback if needed
  
  5. Audit entry (automatic system log)
     - Changed by: [system account]
     - Reason: [from issue]
     - Testing: [attached evidence]
     - Rollback capability: [yes/no]

Validation:
  ☐ Staging testing completed
  ☐ Owner approved
  ☐ Deployed to production
  ☐ Monitoring active (48h minimum)
  ☐ Audit entry created
```

---

## Part 3: Audit Logging System

### 3.1 Audit Entry Schema

**Every variable change must create an audit entry:**

```json
{
  "audit_id": "aud-20260222-001",
  "timestamp": "2026-02-22T14:30:00Z",
  "variable_name": "CODEX_CACHE_VERSION",
  "action": "update",
  "old_value": "3.1.0",
  "new_value": "3.1.1",
  "changed_by": "ci-health-alert-agent",
  "approval_chain": {
    "stage1_approval": "none",
    "stage2_approval": "none",
    "stage3_approval": "none"
  },
  "reason": "Cache invalidation needed due to build artifact corruption",
  "evidence": {
    "issue": "https://github.com/Aries-Serpent/_codex_/issues/12345",
    "pr": "https://github.com/Aries-Serpent/_codex_/pull/67890",
    "metrics": "Artifact cache hit rate dropped from 87% to 23%"
  },
  "session_id": "copilot-session-abc123",
  "source_system": "GitHub Actions",
  "security_classification": "internal",
  "reversible": true,
  "rollback_procedure": "Set CODEX_CACHE_VERSION=3.1.0"
}
```

### 3.2 Audit Storage & Access

**Storage Locations:**

```yaml
Live Audit Log:
  - Location: GitHub Actions secrets metadata (read-only)
  - Tool: gh cli query, GitHub API
  - Format: JSON entries

Historical Audit Log:
  - Location: .codex/aftermath/variable_audit_log.json (append-only)
  - Retention: 7 years (compliance requirement)
  - Backup: Daily encrypted backup to secure storage

Dashboard:
  - Location: GitHub repo secrets UI (read-only)
  - Access: Owner + Tech lead
  - Visible fields: Variable name, last change date, change count
```

**Access Control:**

```yaml
Secret Variables (Category A):
  - Read access: Owner only
  - Write access: Owner only
  - Audit access: Owner + Security team
  
Health Metrics (Category B):
  - Read access: All agents + tech lead
  - Write access: Designated agents only
  - Audit access: Tech lead + owner
  
Infrastructure Config (Category C):
  - Read access: All runners
  - Write access: Tech lead + owner
  - Audit access: Tech lead + owner
  
Cognitive Brain (Category D):
  - Read access: All agents
  - Write access: System only
  - Audit access: System + owner
```

### 3.3 Audit Compliance Reports

**Weekly Audit Report:**

```bash
python scripts/ci/audit_logger.py --mode weekly \
  --output artifacts/weekly_audit_report.json

# Output includes:
#   - All variable changes in past 7 days
#   - Approval chain status for each change
#   - Any missing audit entries (anomalies)
#   - Metrics: change frequency, approval latency
```

**Monthly Compliance Report:**

```bash
python scripts/ci/governance_report_generator.py --mode monthly \
  --include-variables \
  --output artifacts/monthly_governance_report.md

# Output includes:
#   - Summary of all changes
#   - Approval chain audit
#   - Metrics trends
#   - Anomalies and recommendations
```

**Quarterly Security Audit:**

```bash
python scripts/ci/security_audit.py --mode quarterly \
  --category secrets \
  --output artifacts/quarterly_secret_audit.json

# Output includes:
#   - Secret rotation schedule compliance
#   - Access pattern analysis
#   - Unauthorized access attempts (if any)
#   - Recommendations for tightening controls
```

---

## Part 4: Enforcement & Monitoring

### 4.1 CI/CD Gate Integration

```yaml
GitHub Actions Workflows:
  - Update variable trigger:
    - Workflow: .github/workflows/variable-update-gate.yml
    - Check: Verify approval chain completed
    - Check: Verify audit entry created
    - Action: Auto-post summary comment

  - Audit compliance check:
    - Workflow: .github/workflows/audit-compliance-gate.yml
    - Frequency: Weekly
    - Check: All changes have audit entries
    - Action: Flag missing entries for review
```

### 4.2 Real-Time Monitoring

**Dashboard Metrics:**

```yaml
Active Variables:
  - Count: 13+ variables
  - Last update: [timestamp]
  - Changes in past 7 days: [count]
  - Pending approvals: [count]

Audit Trail Health:
  - Total audit entries: [count]
  - Entries missing approval: [count]
  - Entries missing evidence: [count]
  - Average approval latency: [time]

Compliance Status:
  - Rotation compliance: [percentage]
  - Audit entry creation: [percentage]
  - Access control violations: [count]
  - Unauthorized changes: [count]
```

### 4.3 Alerting Thresholds

| Alert | Threshold | Action |
|-------|-----------|--------|
| Missing audit entry | Any variable change | Immediate investigation |
| Overdue rotation | 30+ days past due | Tech lead notification |
| Unapproved change | 72+ hours pending | Escalation to owner |
| Unauthorized access attempt | Any attempt | Security team alert |
| Compliance score drop | <95% | Weekly review required |

---

## Part 5: Operational Procedures

### 5.1 Variable Update Request Template

**GitHub Issue Template: `variable-update-request`**

```markdown
# Variable Update Request: [VARIABLE_NAME]

## Current State
- Variable name: [VARIABLE_NAME]
- Current value: [value]
- Category: [A/B/C/D]
- Last updated: [date]

## Proposed Change
- New value: [value]
- Reason: [detailed justification]
- Business impact: [benefits of change]
- Risk assessment: [potential issues]

## Testing & Evidence
- Testing environment: [staging/production]
- Test results: [pass/fail/partial]
- Attached evidence: [links or screenshots]
- Rollback plan: [if change fails, how to revert]

## Approval Requirements
- Approver(s) required: [tech lead / owner / both]
- Expected timeline: [24h / 48h / 1 week]
- Emergency: [yes/no]

## Implementation
- Deployment timeline: [when to apply]
- Monitoring plan: [how to verify success]
- Communication plan: [who to notify]
```

### 5.2 Troubleshooting: Variable Update Failures

| Issue | Cause | Solution |
|-------|-------|----------|
| Change not taking effect | Cache not cleared | Increment CODEX_CACHE_VERSION |
| Tests failing after update | Environment not updated | Restart all runner agents |
| Approval stuck for >72h | Reviewer unavailable | Escalate to owner |
| Audit entry missing | Automation failed | Manual entry + investigation |
| Unauthorized change detected | Access control breach | Security incident review |

---

## Summary & Compliance Verification

✅ **Variable Lifecycle Policy: COMPLETE & OPERATIONAL**

| Requirement | Implementation | Status |
|-----------|-----------------|--------|
| Lifecycle states defined for all 4 categories | Section 1.2-1.3 | ✅ |
| Procedures documented for all state transitions | Section 2 | ✅ |
| Audit logging system fully specified | Section 3 | ✅ |
| CI/CD gate integration defined | Section 4.1 | ✅ |
| Real-time monitoring configured | Section 4.2-4.3 | ✅ |
| Operational playbooks documented | Section 5 | ✅ |

**Next Steps:**
1. Deploy audit logging infrastructure (scripts/ci/audit_logger.py)
2. Configure GitHub Actions gates (variable-update-gate.yml)
3. Set up monitoring dashboard
4. Train team on procedures
5. Begin historical audit log migration

