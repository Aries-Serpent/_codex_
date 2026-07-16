# PHASE 8 LANE 3: WORKFLOW CONSOLIDATION MAPPING

**Generated:** 2026-07-16T14:56:10Z  
**Status:** COMPLETE  
**Total Consolidated:** 39 workflows → 7 unified workflows  

---

## Consolidation Groups Reference Table

| Group ID | Unified Workflow | Original Count | Consolidated | Reduction | Status |
|----------|-----------------|---|---|---|---|
| G1 | unified-health-monitoring.yml | 4 | 1 | 3 (75%) | ✅ |
| G2 | unified-session-management.yml | 5 | 1 | 4 (80%) | ✅ |
| G3 | unified-post-merge-management.yml | 5 | 1 | 4 (80%) | ✅ |
| G4 | unified-documentation.yml | 6 | 1 | 5 (83%) | ✅ |
| G5 | unified-copilot-management.yml | 9 | 1 | 8 (89%) | ✅ |
| G6 | unified-phase-gates.yml | 6 | 1 | 5 (83%) | ✅ |
| G7 | unified-security-scanning.yml | 4 | 1 | 3 (75%) | ✅ |
| **TOTAL** | **7 workflows** | **39** | **7** | **32 (82%)** | ✅ |

---

## Group G1: Health Monitoring

**Unified Workflow:** `unified-health-monitoring.yml`

### Consolidated Files (4 → 1)

| Original Workflow | Purpose | Jobs | Triggers | Status |
|---|---|---|---|---|
| ci-health-monitor.yml | CI pipeline health checks | health-check | schedule, push, pr | ✅ Archived |
| health-dashboard-update.yml | Dashboard metrics updates | dashboard-update | schedule, workflow_dispatch | ✅ Archived |
| repository-health-monitoring.yml | Repository metrics tracking | repo-metrics | schedule, push | ✅ Archived |
| workflow-health-update.yml | Workflow status updates | workflow-status | schedule, workflow_dispatch | ✅ Archived |

### Unified Job Structure

```yaml
unified-health-monitoring.yml:
  jobs:
    - ci-health-check      # Monitors CI pipeline
    - dashboard-update     # Updates dashboard (needs ci-health-check)
    - repository-health    # Monitors repo metrics
    - workflow-health      # Updates workflow status (needs repo-health)
    - summary              # Reports overall status (always)
```

### Migration Path

**Trigger Mapping:**
- `schedule`: `0 */6 * * *` (CI every 6h), `0 0 * * 1` (weekly Mon)
- `push`: main, develop branches
- `pull_request`: opened, synchronize, reopened
- `workflow_dispatch`: operation selection

**Operation Dispatch Options:**
- `ci-health` → Run CI health check only
- `dashboard-update` → Update dashboard
- `repository-health` → Monitor repository
- `workflow-health` → Update workflow status
- `all` → Run all health operations (default)

---

## Group G2: Session Management

**Unified Workflow:** `unified-session-management.yml`

### Consolidated Files (5 → 1)

| Original Workflow | Purpose | Jobs | Triggers | Status |
|---|---|---|---|---|
| session-context-capture.yml | Capture session context | context-capture | schedule, push | ✅ Archived |
| session-incremental-summary-reminder.yml | Generate incremental summaries | incremental-summary | schedule, workflow_dispatch | ✅ Archived |
| session-recovery-continuous-monitoring.yml | Monitor recovery status | recovery-monitor | schedule, push | ✅ Archived |
| session-recovery-handler.yml | Handle recovery operations | recovery-handler | schedule, workflow_dispatch | ✅ Archived |
| session-watchdog.yml | Session watchdog checks | watchdog | schedule, push | ✅ Archived |

### Unified Job Structure

```yaml
unified-session-management.yml:
  jobs:
    - context-capture         # Captures session context
    - incremental-summary     # Generates summaries
    - recovery-monitor        # Monitors recovery
    - recovery-handler        # Handles recovery (needs recovery-monitor)
    - watchdog                # Watchdog checks
    - summary                 # Reports status (always)
```

### Migration Path

**Trigger Mapping:**
- `schedule`: `*/30 * * * *` (every 30 minutes - continuous monitoring)
- `push`: main branch
- `pull_request`: opened, synchronize
- `workflow_dispatch`: operation selection

**Operation Dispatch Options:**
- `capture-context` → Session context capture
- `increment-summary` → Incremental summary generation
- `recovery-monitor` → Recovery status monitoring
- `recovery-handler` → Recovery operations
- `watchdog` → Watchdog checks
- `all` → All session management operations (default)

---

## Group G3: Post-Merge Management

**Unified Workflow:** `unified-post-merge-management.yml`

### Consolidated Files (5 → 1)

| Original Workflow | Purpose | Jobs | Triggers | Status |
|---|---|---|---|---|
| post-accountability-to-discussion.yml | Accountability reporting | accountability | push (main) | ✅ Archived |
| post-ci-status-to-discussion.yml | CI status updates | ci-status | push (main) | ✅ Archived |
| post-merge-validation-optimized.yml | Post-merge validation | merge-validation | push (main) | ✅ Archived |
| post-phase-4-5-to-discussion.yml | Phase 4/5 reporting | phase-reporting | workflow_dispatch | ✅ Archived |
| post-phase-update-to-discussion.yml | Phase update reporting | phase-reporting | workflow_dispatch | ✅ Archived |

### Unified Job Structure

```yaml
unified-post-merge-management.yml:
  jobs:
    - accountability-report   # Accountability reporting
    - ci-status-report        # CI status to discussion
    - merge-validation        # Post-merge validation checks
    - phase-reporting         # Phase updates (needs all above)
    - summary                 # Reports overall status (always)
```

### Migration Path

**Trigger Mapping:**
- `push`: main branch only
- `workflow_dispatch`: operation selection

**Operation Dispatch Options:**
- `accountability` → Accountability report
- `ci-status` → CI status report
- `validation` → Post-merge validation
- `phase-reporting` → Phase updates
- `all` → All post-merge operations (default)

---

## Group G4: Documentation

**Unified Workflow:** `unified-documentation.yml`

### Consolidated Files (6 → 1)

| Original Workflow | Purpose | Jobs | Triggers | Status |
|---|---|---|---|---|
| doc-freshness-check.yml | Documentation freshness | freshness-check | schedule, push, pr | ✅ Archived |
| doc-refresh-gate.yml | Refresh requirements | refresh-gate | schedule, workflow_dispatch | ✅ Archived |
| docs-code-alignment.yml | Code example alignment | code-alignment | push (docs/), pr | ✅ Archived |
| docs-health.yml | Documentation health | health-check | schedule, push | ✅ Archived |
| documentation-link-checker.yml | Link validation | link-checker | schedule, push, pr | ✅ Archived |
| documentation-quality-check.yml | Quality assessment | quality-check | schedule, workflow_dispatch | ✅ Archived |

### Unified Job Structure

```yaml
unified-documentation.yml:
  jobs:
    - freshness-check         # Documentation freshness
    - refresh-gate            # Refresh requirements (needs freshness)
    - code-alignment          # Code example alignment
    - health-check            # Documentation health
    - link-checker            # Link validation
    - quality-check           # Quality assessment (needs all above)
    - summary                 # Reports overall status (always)
```

### Migration Path

**Trigger Mapping:**
- `schedule`: `0 2 * * *` (daily at 2 AM)
- `push`: paths `docs/**`, `**/*.md` on main
- `pull_request`: paths `docs/**`, `**/*.md`
- `workflow_dispatch`: operation selection

**Operation Dispatch Options:**
- `freshness-check` → Documentation freshness
- `refresh-gate` → Refresh requirements
- `code-alignment` → Code example alignment
- `health-check` → Documentation health
- `link-checker` → Link validation
- `quality-check` → Quality assessment
- `all` → All documentation operations (default)

---

## Group G5: Copilot Management

**Unified Workflow:** `unified-copilot-management.yml`

### Consolidated Files (9 → 1)

| Original Workflow | Purpose | Jobs | Triggers | Status |
|---|---|---|---|---|
| copilot-agent-checkin.yml | Agent status check-in | agent-checkin | schedule, push | ✅ Archived |
| copilot-agent-session-done.yml | Session completion | session-done | schedule, workflow_dispatch | ✅ Archived |
| copilot-agent-vars-bootstrap.yml | Variable bootstrap | vars-bootstrap | schedule, workflow_dispatch | ✅ Archived |
| copilot-automation.yml | Copilot automations | automation | schedule, push | ✅ Archived |
| copilot-issue-triage.yml | Issue management | issue-triage | schedule, push | ✅ Archived |
| copilot-iterative-self-healing.yml | Self-healing checks | self-healing | schedule, push | ✅ Archived |
| copilot-pr-session-injector.yml | PR session context | session-injector | pull_request_target | ✅ Archived |
| copilot-review-responder.yml | Review response | review-responder | pull_request | ✅ Archived |
| copilot-session-chain.yml | Session chaining | session-chain | schedule, workflow_dispatch | ✅ Archived |

### Unified Job Structure

```yaml
unified-copilot-management.yml:
  jobs:
    - agent-checkin           # Agent status check-in
    - session-done            # Mark session complete
    - vars-bootstrap          # Bootstrap variables
    - automation              # Copilot automations (needs vars)
    - issue-triage            # Issue triage operations
    - self-healing            # Self-healing checks
    - session-injector        # PR session context
    - review-responder        # Review response handling
    - session-chain           # Chain sessions (needs injector, responder)
    - summary                 # Reports status (always)
```

### Migration Path

**Trigger Mapping:**
- `schedule`: `*/15 * * * *` (every 15 minutes)
- `push`: main branch
- `pull_request_target`: opened, synchronize, reopened
- `workflow_dispatch`: operation selection

**Operation Dispatch Options:**
- `agent-checkin` → Agent check-in
- `session-done` → Mark session done
- `vars-bootstrap` → Bootstrap variables
- `automation` → Automation execution
- `issue-triage` → Issue triage
- `self-healing` → Self-healing checks
- `session-injector` → Session injector
- `review-responder` → Review response
- `session-chain` → Session chaining
- `all` → All Copilot operations (default)

---

## Group G6: Phase Gates

**Unified Workflow:** `unified-phase-gates.yml`

### Consolidated Files (6 → 1)

| Original Workflow | Purpose | Jobs | Triggers | Status |
|---|---|---|---|---|
| phase-8-1-health-monitor.yml | Phase 8.1 health | phase-8-1-health | schedule, push | ✅ Archived |
| phase-8-1-enhanced-health-monitor.yml | Phase 8.1 enhanced | phase-8-1-enhanced | schedule, workflow_dispatch | ✅ Archived |
| phase-8-2-issue-triage.yml | Phase 8.2 triage | phase-8-2-triage | schedule, push | ✅ Archived |
| phase-8-3-perf-monitor.yml | Phase 8.3 performance | phase-8-3-perf | schedule, push | ✅ Archived |
| phase-9-2-cascade.yml | Phase 9.2 cascade | phase-9-2-cascade | schedule, workflow_dispatch | ✅ Archived |
| phase-9-3-router.yml | Phase 9.3 routing | phase-9-3-router | schedule, workflow_dispatch | ✅ Archived |

### Unified Job Structure

```yaml
unified-phase-gates.yml:
  jobs:
    - phase-8-1-health        # Phase 8.1 Health
    - phase-8-2-triage        # Phase 8.2 Triage (needs 8.1)
    - phase-8-3-performance   # Phase 8.3 Performance
    - phase-9-2-cascade       # Phase 9.2 Cascade (needs 8.x)
    - phase-9-3-router        # Phase 9.3 Router (needs 9.2)
    - summary                 # Reports status (always)
```

### Migration Path

**Trigger Mapping:**
- `schedule`: `0 * * * *` (every hour)
- `push`: main branch
- `workflow_dispatch`: operation selection

**Operation Dispatch Options:**
- `phase-8-1-health` → Phase 8.1 health check
- `phase-8-2-triage` → Phase 8.2 issue triage
- `phase-8-3-performance` → Phase 8.3 performance monitor
- `phase-9-2-cascade` → Phase 9.2 cascade operations
- `phase-9-3-router` → Phase 9.3 routing logic
- `all` → All phase gate operations (default)

---

## Group G7: Security Scanning

**Unified Workflow:** `unified-security-scanning.yml`

### Consolidated Files (4 → 1)

| Original Workflow | Purpose | Jobs | Triggers | Status |
|---|---|---|---|---|
| codeql-alert-fetcher.yml | Fetch CodeQL alerts | codeql-fetch | schedule, push, pr | ✅ Archived |
| codeql-analysis.yml | CodeQL analysis | codeql-analysis | schedule, push, pr | ✅ Archived |
| codeql-alert-triage.yml | Alert triage | codeql-triage | schedule, workflow_dispatch | ✅ Archived |
| codeql-fix-verification.yml | Fix verification | codeql-fix-verify | schedule, workflow_dispatch | ✅ Archived |

### Unified Job Structure

```yaml
unified-security-scanning.yml:
  jobs:
    - codeql-fetch            # Fetch CodeQL alerts
    - codeql-analysis         # Run CodeQL analysis
    - codeql-triage           # Triage findings (needs fetch)
    - codeql-fix-verify       # Verify fixes (needs analysis, triage)
    - summary                 # Reports security status (always)
```

### Migration Path

**Trigger Mapping:**
- `schedule`: `0 3 * * *` (daily 3 AM), `0 15 * * 0` (weekly Sunday 3 PM)
- `push`: main, develop
- `pull_request`: opened, synchronize, reopened
- `workflow_dispatch`: operation selection

**Operation Dispatch Options:**
- `codeql-fetch` → Fetch CodeQL alerts
- `codeql-analysis` → Run CodeQL analysis
- `codeql-triage` → Triage findings
- `codeql-fix-verify` → Verify fixes
- `all` → All security operations (default)

---

## Archived Files Reference

All consolidated original workflows are archived in:
```
.github/workflows/_archived/
```

### Archived File Listing

```
_archived/
├── ci-health-monitor.yml.archived
├── health-dashboard-update.yml.archived
├── repository-health-monitoring.yml.archived
├── workflow-health-update.yml.archived
├── session-context-capture.yml.archived
├── session-incremental-summary-reminder.yml.archived
├── session-recovery-continuous-monitoring.yml.archived
├── session-recovery-handler.yml.archived
├── session-watchdog.yml.archived
├── post-accountability-to-discussion.yml.archived
├── post-ci-status-to-discussion.yml.archived
├── post-merge-validation-optimized.yml.archived
├── post-phase-4-5-to-discussion.yml.archived
├── post-phase-update-to-discussion.yml.archived
├── doc-freshness-check.yml.archived
├── doc-refresh-gate.yml.archived
├── docs-code-alignment.yml.archived
├── docs-health.yml.archived
├── documentation-link-checker.yml.archived
├── documentation-quality-check.yml.archived
├── copilot-agent-checkin.yml.archived
├── copilot-agent-session-done.yml.archived
├── copilot-agent-vars-bootstrap.yml.archived
├── copilot-automation.yml.archived
├── copilot-issue-triage.yml.archived
├── copilot-iterative-self-healing.yml.archived
├── copilot-pr-session-injector.yml.archived
├── copilot-review-responder.yml.archived
├── copilot-session-chain.yml.archived
├── phase-8-1-enhanced-health-monitor.yml.archived
├── phase-8-1-health-monitor.yml.archived
├── phase-8-2-issue-triage.yml.archived
├── phase-8-3-perf-monitor.yml.archived
├── phase-9-2-cascade.yml.archived
├── phase-9-3-router.yml.archived
├── codeql-alert-fetcher.yml.archived
├── codeql-alert-triage.yml.archived
├── codeql-analysis.yml.archived
└── codeql-fix-verification.yml.archived

Total: 39 archived files
```

---

## Cross-Reference: Original Workflow → Unified Workflow

| Original Workflow | Group | Unified Workflow |
|---|---|---|
| ci-health-monitor.yml | G1 | unified-health-monitoring.yml |
| health-dashboard-update.yml | G1 | unified-health-monitoring.yml |
| repository-health-monitoring.yml | G1 | unified-health-monitoring.yml |
| workflow-health-update.yml | G1 | unified-health-monitoring.yml |
| session-context-capture.yml | G2 | unified-session-management.yml |
| session-incremental-summary-reminder.yml | G2 | unified-session-management.yml |
| session-recovery-continuous-monitoring.yml | G2 | unified-session-management.yml |
| session-recovery-handler.yml | G2 | unified-session-management.yml |
| session-watchdog.yml | G2 | unified-session-management.yml |
| post-accountability-to-discussion.yml | G3 | unified-post-merge-management.yml |
| post-ci-status-to-discussion.yml | G3 | unified-post-merge-management.yml |
| post-merge-validation-optimized.yml | G3 | unified-post-merge-management.yml |
| post-phase-4-5-to-discussion.yml | G3 | unified-post-merge-management.yml |
| post-phase-update-to-discussion.yml | G3 | unified-post-merge-management.yml |
| doc-freshness-check.yml | G4 | unified-documentation.yml |
| doc-refresh-gate.yml | G4 | unified-documentation.yml |
| docs-code-alignment.yml | G4 | unified-documentation.yml |
| docs-health.yml | G4 | unified-documentation.yml |
| documentation-link-checker.yml | G4 | unified-documentation.yml |
| documentation-quality-check.yml | G4 | unified-documentation.yml |
| copilot-agent-checkin.yml | G5 | unified-copilot-management.yml |
| copilot-agent-session-done.yml | G5 | unified-copilot-management.yml |
| copilot-agent-vars-bootstrap.yml | G5 | unified-copilot-management.yml |
| copilot-automation.yml | G5 | unified-copilot-management.yml |
| copilot-issue-triage.yml | G5 | unified-copilot-management.yml |
| copilot-iterative-self-healing.yml | G5 | unified-copilot-management.yml |
| copilot-pr-session-injector.yml | G5 | unified-copilot-management.yml |
| copilot-review-responder.yml | G5 | unified-copilot-management.yml |
| copilot-session-chain.yml | G5 | unified-copilot-management.yml |
| phase-8-1-enhanced-health-monitor.yml | G6 | unified-phase-gates.yml |
| phase-8-1-health-monitor.yml | G6 | unified-phase-gates.yml |
| phase-8-2-issue-triage.yml | G6 | unified-phase-gates.yml |
| phase-8-3-perf-monitor.yml | G6 | unified-phase-gates.yml |
| phase-9-2-cascade.yml | G6 | unified-phase-gates.yml |
| phase-9-3-router.yml | G6 | unified-phase-gates.yml |
| codeql-alert-fetcher.yml | G7 | unified-security-scanning.yml |
| codeql-alert-triage.yml | G7 | unified-security-scanning.yml |
| codeql-analysis.yml | G7 | unified-security-scanning.yml |
| codeql-fix-verification.yml | G7 | unified-security-scanning.yml |

---

**Total Workflows:** 39 original → 7 unified  
**Net Reduction:** 32 files (82% consolidation within groups)  
**Document Generated:** 2026-07-16T14:56:10Z  

