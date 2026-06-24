# Phase 6 Batch 2 — Deployment Approval Workflow & Governance Gates

**Version:** 1.0.0  
**Status:** FINAL  
**Audience:** DevOps, deployment engineers, owners, tech leads  
**Last Updated:** 2026-02-22

---

## Overview

This document defines the deployment approval workflow, governance gates, and SLAs for staging and production deployments in the Aries-Serpent/_codex_ repository.

**Related Docs:**
- 📋 Full governance framework: `.codex/BATCH_2_GOVERNANCE_FRAMEWORK.md` (Part 3)
- 🔄 Variable lifecycle policy: `docs/production/VARIABLE_LIFECYCLE_POLICY.md`

---

## Part 1: Deployment Types & Approval Chains

### Deployment Type 1: Staging Deployment (Automatic / Low Touch)

**Trigger:** Merge to `0D_base_` branch (automatic on merge)

**Timeline:**
- Deploy initiation: Immediate on merge (~2 minutes)
- Health checks: 5-15 minutes
- Total deployment: 15-30 minutes

**Prerequisites:**
```yaml
Merge Status:
  ✅ All PR gates passed (code review, security, tests, policy)
  ✅ Integration tests passing on 0D_base_

Deployment Health Checks:
  ✅ Staging environment online
  ✅ Required services running
  ✅ Database migrations compatible
  ✅ No active deployments in progress
```

**Approval Process:**

```yaml
Automatic Deployment:
  1. PR merged to 0D_base_
  2. GitHub Actions trigger: deployment-staging.yml
  3. Stage 1: Pre-deployment checks
     - Verify all CI gates passed
     - Verify no merge conflicts
     - Verify staging environment ready

  4. Stage 2: Deployment
     - Deploy code to staging environment
     - Run database migrations
     - Restart services

  5. Stage 3: Post-deployment validation
     - Run smoke tests on staging
     - Health check API endpoints
     - Verify metrics collection

  6. Notification: Slack #deployments channel
     - Deploy started
     - Deploy completed (success/failure)
     - Link to deployment logs

  7. Fallback: Auto-rollback on failure
     - If health checks fail: Auto-rollback to previous version
     - Alert: Post failure notification
     - Incident: Create GitHub issue for investigation
```

**Approval Override (Manual):**

```yaml
If automatic deployment disabled or failed:
  - Tech lead or owner: GitHub Actions dispatch
  - Manual trigger: Allows forcing deployment
  - Requires confirmation: Explicit "Deploy to Staging" in message
  - Notification: Team alerted of manual deployment
```

**Rollback Procedure:**

```yaml
Automatic Rollback (triggered if health checks fail):
  1. Deployment fails health check
  2. Automatic rollback initiated
  3. Previous version restored
  4. Incident created: "Staging deployment failed - auto-rolled back"
  5. Team alerted: #infrastructure-alerts

Manual Rollback (if needed):
  - Tech lead triggers: GitHub Actions rollback-staging.yml
  - Confirmation: Must provide reason
  - Execution: Immediate
  - Notification: Team alerted
  - Documentation: Incident report created
```

---

### Deployment Type 2: Production Deployment (Manual / High Control)

**Trigger:** Merge to `main` branch (promotion PR from 0D_base_)

**Timeline:**
- Approval phase: 2-4 hours (minimum 24h testing on staging first)
- Deploy initiation: On manual approval
- Health checks: 10-20 minutes
- Total deployment: 30-60 minutes
- Post-deployment monitoring: 1 hour minimum

**Prerequisites:**

```yaml
Merge Status:
  ✅ All PR gates passed
  ✅ Promotion PR merged (0D_base_ → main)

Staging Validation (mandatory):
  ✅ Deployed to staging ≥24 hours ago
  ✅ All integration tests passing for ≥24h
  ✅ No critical bugs reported
  ✅ Performance acceptable (no degradation)
  ✅ Smoke tests passing consistently

Production Readiness:
  ✅ CHANGELOG.md updated with release notes
  ✅ Runbook available (link in deployment request)
  ✅ Rollback plan documented
  ✅ Deployment window confirmed
  ✅ On-call engineer available
  ✅ Communication plan ready (if customer-facing)
```

**Approval Process:**

```yaml
Step 1: Pre-Deployment Checklist (Tech Lead, 30 min)
  Prepare deployment request issue:
    - Title: "Production Deployment: v[VERSION]"
    - Template includes checklist (see 2.1)
    - Attach evidence: staging validation, metrics
    - Assign to: Owner @mbaetiong + Tech lead
    - Label: "deployment-request", "production"

Step 2: Tech Lead Review (24-48 hours)
  Requirements:
    ☐ Review CHANGELOG for release notes
    ☐ Verify staging validation period (≥24h)
    ☐ Inspect git diff (main...0D_base_)
    ☐ Check metrics for regressions
    ☐ Review runbook and rollback plan
    ☐ Confirm deployment window appropriate

  Actions:
    ✅ Comment: "Staging validation complete, ready for approval"
    or
    ❌ Comment: "Need to address [specific concern]"

Step 3: Owner Approval (4-8 hours after tech lead)
  Requirements:
    ☐ Owner reviews tech lead validation
    ☐ Owner personally inspects key changes
    ☐ Owner confirms deployment window
    ☐ Owner verifies runbook completeness

  Actions:
    ✅ Comment: "@tech-lead and I have approved this deployment"
    ✅ React: 👍 emoji for approval marker
    or
    ❌ Comment: "Hold deployment pending [reason]"

Step 4: Manual Deployment Trigger (Owner Only)
  - Tech lead and owner must both approve
  - Owner dispatches: .github/workflows/deploy-production.yml
  - Requires explicit parameter: --approve "Release Notes"
  - Executes immediately

Step 5: Deployment Execution
  - Stage 1: Final pre-flight checks
  - Stage 2: Blue-green deployment (if applicable)
  - Stage 3: Health check & monitoring
  - Stage 4: Complete switchover (if blue-green)
  - Stage 5: Post-deployment validation
```

**Notification & Escalation:**

```yaml
Timeline of notifications:
  T-30 min: #production channel message
    "Deploying [version] in 30 minutes
     Release notes: [link]
     Runbook: [link]"

  T-0: #production message
    "Deployment starting now
     Build: [link]
     Logs: [link]
     Monitoring: [dashboard]"

  T+5 min: Status update
    "Deployment: Stage 2 - Migrating traffic"

  T+10 min: Status update
    "Deployment: Stage 4 - Health checks passing"

  T+15 min: Success notification
    "✅ Production deployment complete!
     Version: [version]
     Metrics dashboard: [link]"
    or
    "❌ Production deployment failed - auto-rolled back
     Error: [details]
     Incident created: [link]"

  T+1 hour: Post-deployment summary
    "Monitoring complete - deployment stable
     Key metrics: [summary]
     No incidents reported"
```

**Rollback Procedure (Critical):**

```yaml
Automatic Rollback (if health checks fail):
  1. Post-deployment health check detects issue
  2. Alert: Critical health check failure
  3. Auto-rollback initiated within 1 minute
  4. Previous stable version restored
  5. Incident created: Critical - auto-rolled back
  6. Team alerted: #production-incidents

Manual Rollback (if needed during deployment):
  - Owner can trigger immediate rollback
  - No approval needed (emergency protocol)
  - Used if: Issue detected within 1 hour post-deploy
  - Execution: Immediate
  - Notification: All teams alerted
  - Incident report: Created immediately
  - Root cause analysis: Scheduled within 2 hours

Post-Rollback:
  1. Investigation begins immediately
  2. Root cause identified within 24 hours
  3. Fix prepared (if applicable)
  4. Retesting in staging
  5. Redeploy (once fixed)
```

---

### Deployment Type 3: Hotfix Deployment (Expedited / Emergency)

**Trigger:** Critical production issue; labeled "hotfix" and targets `main`

**Timeline:**
- Approval: 15-30 minutes (owner only, fast-track)
- Testing: Minimal (validated in staging only)
- Deploy: Immediate
- Monitoring: 1-2 hours intensive

**Prerequisites:**

```yaml
Issue Severity:
  - CRITICAL or P1 only
  - Production impact: service down, data loss risk, or security breach

Hotfix Validation:
  ✅ Issue reproduced in production (proof)
  ✅ Fix verified in staging environment
  ✅ Minimal risk assessment completed
  ✅ Rollback plan (quick revert possible)
```

**Approval Process:**

```yaml
Step 1: Issue Triage (5 minutes)
  - Incident commander: Verify CRITICAL/P1 severity
  - Decision: Hotfix vs. wait for regular deployment
  - If hotfix approved → Step 2

Step 2: Hotfix Code Preparation (10-30 minutes)
  - Engineer creates fix (minimal, scoped change)
  - Self-review for obvious issues
  - Push to branch (do NOT merge yet)

Step 3: Staging Validation (10-20 minutes)
  - Deploy to staging environment
  - Run smoke tests
  - Verify fix works
  - Owner personally validates fix

Step 4: Owner Approval (5 minutes)
  - Owner approves: "Hotfix ready for production"
  - No additional reviews required (emergency exception)
  - Fast-track merge to main

Step 5: Production Deployment (Immediate)
  - Owner dispatches: deploy-production.yml with hotfix flag
  - Deployment executes immediately
  - No waiting time
```

**Hotfix Commit Message Format:**

```
[HOTFIX] [Severity] - [Title]

Description: [what is fixed]
Symptom: [production impact]
Root Cause: [why it happened]
Fix: [code change summary]
Verified: [how it was tested in staging]
Risk: [low/medium - why minimal risk]

Example:
  [HOTFIX] P1 - Database connection leak

  Symptom: Database connections exhausted, API timeouts
  Root Cause: Connection not returned to pool on error
  Fix: Add finally block to ensure connection.close()
  Verified: Staging traffic test - connection count stable
  Risk: Low - single line change, proven in staging
```

**Post-Deployment Hotfix Review:**

```yaml
After successful hotfix deployment:
  1. Incident commander: Monitor for 2 hours
  2. Metrics dashboard: Watch for regressions
  3. Error tracking: Monitor error rates
  4. Team notification: "Hotfix deployed successfully"

Within 24 hours:
  1. Post-mortem issue created
  2. Root cause analysis documented
  3. Permanent fix planned (if needed)
  4. Prevention measures identified

Within 5 days:
  1. Post-mortem meeting held
  2. Action items assigned
  3. Lessons learned documented
  4. Prevention measures implemented (if applicable)
```

---

### Deployment Type 4: Security Patch Deployment (Escalated / Urgent)

**Trigger:** Security vulnerability patched; labeled "security-patch" and targets `main`

**Timeline:**
- Security review: 4-8 hours
- Testing: Full test suite (mandatory)
- Staging validation: 12-24 hours (recommended)
- Approval: 4-8 hours (3-way review)
- Deploy: Scheduled during peak monitoring hours

**Prerequisites:**

```yaml
Security Review Complete:
  ✅ Threat model documented
  ✅ Fix verified against threat model
  ✅ No new vulnerabilities introduced
  ✅ Security scanning: 0 issues

Testing Complete:
  ✅ Full test suite passing
  ✅ Security-specific tests added (if applicable)
  ✅ No regressions (coverage maintained)
  ✅ Staging validation: 12-24 hours stable
```

**Approval Process:**

```yaml
Step 1: Security Team Review (4-8 hours)
  - Security lead: Threat model review
  - Security lead: Fix verification
  - CodeQL + security scanning: 0 issues
  - Approval: "Security review complete"

Step 2: Code Review (4-8 hours)
  - Code owner: Code quality review
  - Coverage check: ≥80% maintained
  - Approval: "Code review complete"

Step 3: Owner Review & Approval (4-8 hours)
  - Owner: Final business impact assessment
  - Owner: Release timing decision
  - Owner: Stakeholder communication
  - Approval: "Ready for production deployment"

Step 4: Staged Deployment
  - All 3 approvals required before merge
  - Owner schedules deployment during peak monitoring
  - Deployment to production (standard process)

Step 5: Post-Deployment (24-48 hours)
  - Enhanced monitoring enabled
  - Security team on alert
  - Customer notifications (if applicable)
  - Issue closure: Pending 48-hour stability verification
```

**Security Patch Communication:**

```yaml
Internal Communication:
  - Security team: Full disclosure
  - Tech lead: Briefing on fix
  - Owner: High-level summary
  - Ops team: Deployment runbook

External Communication (if applicable):
  - Prepared vulnerability disclosure statement
  - Security advisory ready (if public vulnerability)
  - Customer notification scheduled
  - Release notes prepared

Post-Deployment:
  - Security advisory published (if applicable)
  - Vulnerability status updated
  - Customers notified of patch availability
```

---

## Part 2: Pre-Deployment Checklist & Planning

### 2.1 Production Deployment Checklist

**GitHub Issue Template: `production-deployment-request`**

```markdown
# Production Deployment: v[VERSION]

## Pre-Deployment Validation

### Code & Testing
  ☐ Promotion PR merged (0D_base_ → main)
  ☐ All PR gates passed
  ☐ CHANGELOG.md updated with release notes
  ☐ Version number incremented (if semantic versioning used)
  ☐ Git tag created and pushed

### Staging Validation (minimum 24 hours)
  ☐ Deployed to staging ≥24 hours ago
  ☐ Integration tests: All passing
  ☐ Smoke tests: All passing (3+ runs)
  ☐ Performance tests: No degradation detected
  ☐ Security scan: 0 issues (CodeQL, SAST)
  ☐ Dependency audit: 0 critical issues
  ☐ No critical bugs reported (24h observation)

### Production Readiness
  ☐ Runbook prepared and tested (link below)
  ☐ Rollback plan documented (link below)
  ☐ On-call engineer: Confirmed available
  ☐ Communication plan: Prepared (internal + external if applicable)
  ☐ Monitoring dashboard: Prepared and validated
  ☐ Alerts: Configured and tested
  ☐ Deployment window: Confirmed (business hours preferred)

### Risk Assessment
  - Risk level: [LOW / MEDIUM / HIGH]
  - Rationale: [explain risk assessment]
  - Mitigation plan: [what we'll do if issues occur]

### Documentation
  - Runbook: [link to deployment runbook]
  - Rollback plan: [link to rollback documentation]
  - CHANGELOG: [link to CHANGELOG.md]
  - Metrics dashboard: [link to monitoring dashboard]

## Approvals

**Tech Lead Review:**
  - [ ] Reviewed staging validation (24h minimum)
  - [ ] Inspected code changes
  - [ ] Confirmed risk is acceptable
  - [ ] Runbook and rollback plan validated

  _Tech Lead Signature: ___________  Date: _______

**Owner Approval:**
  - [ ] Reviewed tech lead validation
  - [ ] Personally inspected critical changes
  - [ ] Confirmed deployment window
  - [ ] Authorized for production deployment

  _Owner Signature: ___________  Date: _______

## Deployment Execution

Once both approvals obtained, owner dispatches deployment via:
```
gh workflow run deploy-production.yml -f approve="[Release Notes]"
```

Deployment starts immediately. Monitor logs at: [link]

---
