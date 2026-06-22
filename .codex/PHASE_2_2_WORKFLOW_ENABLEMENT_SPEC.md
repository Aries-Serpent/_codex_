# Phase 2.2: Workflow Enablement Specification
> **Milestone:** Workflow Activation & Rollout  
> **Blocking On:** Phase 2.1 completion (secret injection + token validation)  
> **Expected Start:** After Phase 2.1 success (ETA: 2026-06-22T12:00:00Z)  
> **Duration:** 1 week

---

## Overview

Phase 2.2 focuses on activating the genesis-bootstrap.yml workflow and enabling autonomous workflows through staged rollout (1% → 10% → 100%).

---

## Task 2.2.1: genesis-bootstrap.yml Preparation

### Current State
- **File:** .github/workflows/genesis-bootstrap.yml (exists)
- **Status:** Currently disabled (`if: false`)
- **Purpose:** Bootstrap agentic autonomy initialization
- **Trigger:** Manual dispatch or automatic on Phase 2 completion

### Requirements
1. **Code Review:** Audit genesis-bootstrap.yml for:
   - All `if: false` conditions that need activation
   - Workflow dependencies (must have secrets from Phase 2.1)
   - Error handling and rollback triggers
   - Logging/audit trail completeness

2. **Dry-Run Mode:** Implement conditional dry-run
   - Create `GENESIS_DRY_RUN` environment variable
   - When `true`: log all actions without executing mutations
   - When `false`: execute full autonomous bootstrapping

3. **Approval Gate:** Implement WEC (Workflow Execution Checklist) protocol
   - Require explicit approval via PR body checkbox
   - Document approval requirements
   - Create audit trail of all approvals

### Deliverables
- Audited genesis-bootstrap.yml with all conditions reviewed
- Dry-run mode implementation
- WEC approval gate integration
- Comprehensive audit logging

---

## Task 2.2.2: Dry-Run Testing (Non-Production)

### Test Plan
1. **Pre-Flight Checks:**
   - Verify all secrets present (CODEX_MASTER_KEY, CODEX_BACKUP_KEY)
   - Check token health using validation from Phase 2.1
   - Validate GitHub environment setup
   - Confirm all downstream workflows are discoverable

2. **Dry-Run Execution:**
   - Run genesis-bootstrap.yml in dry-run mode on test branch (0D_test_bootstrap_)
   - Verify all downstream workflows trigger correctly (without mutations)
   - Check audit logging captures all bootstrap events
   - Validate rollback procedures work

3. **Validation Checks:**
   - All required variables present in .codex/agent_context.json
   - No errors in workflow logs
   - Audit trail complete and parseable
   - Performance acceptable (<5 minutes total)

### Success Criteria
- ✅ Dry-run completes without errors
- ✅ All downstream workflows discoverable
- ✅ Audit logs complete and machine-readable
- ✅ Rollback procedure validated
- ✅ No mutations occur in dry-run mode

---

## Task 2.2.3: Staged Rollout Execution

### Rollout Strategy

**Stage 1: Alpha (1% of tasks)**
- **Duration:** 2 hours
- **Scope:** Single non-critical task (e.g., log rotation)
- **Monitoring:** Continuous, ready to rollback
- **Success Gate:** Zero errors, audit trail complete

**Stage 2: Beta (10% of tasks)**
- **Duration:** 8 hours
- **Scope:** 3-5 non-critical autonomous tasks
- **Monitoring:** Continuous with alert thresholds
- **Success Gate:** <1% error rate, all tasks completing within SLA

**Stage 3: General Availability (100% of tasks)**
- **Duration:** Ongoing
- **Scope:** All autonomous workflows enabled
- **Monitoring:** Continuous with metrics dashboard
- **Success Gate:** <5% error rate, decision accuracy >90%, no cascading failures

### Rollout Automation
1. **Gradual Enablement:**
   - Use GitHub environment variables to control rollout percentage
   - Create traffic splitter in genesis-bootstrap.yml
   - Automatic progression if each stage meets success criteria

2. **Monitoring & Alerting:**
   - Real-time dashboard showing rollout progress
   - Alerts on error rate threshold exceeded (>5%)
   - Automatic rollback trigger if any stage fails

3. **Rollback Trigger:**
   - Manual: @mbaetiong approves via GitHub comment
   - Automatic: Error rate exceeds 10% for 5 minutes
   - Procedure: Revert `if: false` and wait 30 minutes for stabilization

---

## Task 2.2.4: Gradual Rollout Monitoring

### Monitoring Infrastructure

**Real-Time Dashboard:**
- Rollout stage (Alpha/Beta/GA)
- Error rate by stage
- Task completion time distribution
- Autonomous decision success rate
- Token health metrics
- CI/CD pipeline impact

**Automated Reporting:**
- Hourly status report during rollout
- Daily summary after rollout complete
- Alert on SLA violations
- Audit trail of all rollout events

**Key Metrics:**
- `rollout_stage_complete_time`: How long each stage took
- `autonomous_task_success_rate`: % of tasks completing successfully
- `autonomous_decision_accuracy`: % of decisions that were correct
- `token_health_score`: Overall token broker health (0-100)
- `ci_pipeline_latency`: Impact on build times

### Success Criteria
- ✅ Alpha stage: 0 errors, 100% task completion
- ✅ Beta stage: <1% error rate, tasks completing within SLA
- ✅ GA stage: <5% error rate, >90% decision accuracy
- ✅ No cascading failures or runaway loops
- ✅ CI/CD latency unchanged (<5% variance)

---

## Phase 2.2 Dependencies

**MUST COMPLETE BEFORE PHASE 2.2:**
1. ✅ Phase 2.1: Token broker enhancement
2. ✅ Phase 2.1: Secret injection workflow
3. ✅ Phase 2.1: Compliance framework
4. ✅ Token validation passes all tests
5. ✅ CODEX_MASTER_KEY and CODEX_BACKUP_KEY injected
6. ✅ Zero emergency rollbacks in 48-hour Phase 2.1 stabilization

---

## Phase 2.2 → Phase 2.3 Transition

Once Phase 2.2 GA rollout complete:

**Transition Criteria:**
1. All autonomous workflows executing successfully (>90% success rate)
2. Zero emergency rollbacks after 24-hour stabilization
3. Metrics dashboard fully operational
4. Token health score >95%
5. CI/CD latency unchanged

**Phase 2.3 Kickoff:**
- Implement unified-governance-gate enforcement
- Activate all 6 compliance requirements (REQ-1 through REQ-6)
- Merge compliance checks with autonomous workflows

---

## Timeline

| Date | Event | Duration |
|------|-------|----------|
| 2026-06-22 | Phase 2.1 completion + transition review | - |
| 2026-06-22 AM | Phase 2.2.1: genesis-bootstrap.yml prep | 4h |
| 2026-06-22 PM | Phase 2.2.2: Dry-run testing | 6h |
| 2026-06-23 AM | Phase 2.2.3 Stage 1 (Alpha) | 2h |
| 2026-06-23 PM | Phase 2.2.3 Stage 2 (Beta) | 8h |
| 2026-06-24 AM | Phase 2.2.3 Stage 3 (GA) + 24h monitoring | Ongoing |
| 2026-06-25 | Phase 2.2 → Phase 2.3 transition review | - |

---

## Risk Mitigation

**Risk: Token expiration during rollout**
- **Mitigation:** Token broker circuit breaker from Phase 2.1 handles gracefully
- **Recovery:** Automatic failover to CODEX_BACKUP_KEY

**Risk: Cascading autonomous task failures**
- **Mitigation:** Max 3 failure retries, then escalate to @mbaetiong
- **Recovery:** Manual review + rollback if pattern detected

**Risk: CI/CD latency impact**
- **Mitigation:** Rollout stages ensure limited scope
- **Recovery:** Rollback to `if: false` if latency increases >10%

---

## Artifacts to Produce

1. **genesis-bootstrap.yml (audited & enhanced)**
2. **.github/workflows/genesis-phase2-rollout.yml** (rollout orchestrator)
3. **.codex/PHASE_2_2_ROLLOUT_DASHBOARD.md** (metrics & monitoring)
4. **.codex/PHASE_2_2_ROLLOUT_LOG.md** (real-time status)
5. **scripts/ci/monitor_phase2_rollout.py** (monitoring script)

---

**Last Updated:** 2026-06-21T23:32:53Z  
**Status:** 🟡 AWAITING PHASE 2.1 COMPLETION  
**Next Review:** Phase 2.1 final status report
