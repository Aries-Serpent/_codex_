# Phase 3 Campaign Orchestrator — Comprehensive Protocol

**Status:** 🟢 **TIER 1 ACTIVE** | Campaign ID: `PHASE_3_2026-07-02T19:02:08Z`

---

## I. Executive Summary

The Phase 3 Campaign Orchestrator coordinates a 3-tier, multi-agent verification pipeline:

- **Tier 1** (NOW): Real-time monitoring of 10 core workflows with autonomous failure healing
- **Tier 2** (Standby): 28 extended workflows activated upon Tier 1 success
- **Tier 3** (Standby): Security closure (CodeQL + Semgrep) upon Tier 2 success

**Current Status (19:04:16Z):**
- ✅ 3/10 Tier 1 workflows active (in_progress)
- ✅ 0 failures detected
- ✅ All running workflows green
- 🟡 Awaiting 7 additional workflows to trigger

---

## II. Agent Dispatch System

### Routing Table (10 Failure Patterns → Specialized Agents)

| Priority | Failure Pattern | Route Agent | Window | Category |
|----------|-----------------|-------------|--------|----------|
| **P0** | `AttributeError` / `ImportError` | `ci-testing-agent` | 120s | Test Collection |
| **P0** | `xfail(strict=False)` commits | `codebase-health-guardian` | 120s | Policy |
| **P0** | CodeQL alerts (new) | `security-alert-verification-agent` | 180s | Security |
| **P1** | `ruff` F401/I001 violations | `codebase-health-guardian` | 120s | Linting |
| **P1** | Workflow YAML syntax errors | `workflow-compliance-guardian` | 120s | Infrastructure |
| **P1** | `HFModelUnavailableError` / pin drift | `ci-testing-agent` | 120s | Dependencies |
| **P2** | Coverage drop > 2% | `coverage-roadmap-agent` | 180s | Quality |
| **P2** | Circular imports (CodeQL) | `ci-testing-agent` | 180s | Architecture |
| **P3** | Coverage regression | `coverage-roadmap-agent` | 240s | Quality |
| **P3** | Dependency conflicts | `dependency-conflict-agent` | 240s | Dependencies |

**Dispatch Logic:**
```
IF workflow.conclusion == "failure":
  → Extract failure logs
  → Pattern match against 10-pattern routing table
  → Delegate to specialized agent
  → SET heal_window_start = now()
  → AWAIT agent completion (max heal_window_sec)
  → IF agent_completion_time < heal_window_sec:
    → Grade output on 0-100 rubric
    → Record result in failure log
ELSE:
  → Continue monitoring
```

---

## III. Grading Rubric (Agent Performance Assessment)

Each agent output is graded on **0-100 points**:

| Criterion | Points | Definition |
|-----------|--------|-----------|
| **Failure Reduction** | 40 | Each original failure fixed = 40/N points |
| **No Regressions** | 25 | Full score if no new failures; -25 if regression |
| **Policy Compliance** | 20 | No xfail, no bare except, skipif documented; -5 per violation |
| **Documentation** | 10 | Tracking log updated with Attempt entry + commit SHA |
| **Lint Clean** | 5 | ruff + import smoke pass on all changed files |

**Score Thresholds:**
- **≥ 90**: ✅ Auto-approve for merge
- **70–89**: 🔄 Human review recommended
- **< 70**: ❌ Send back to agent with specific feedback

---

## IV. Real-Time Monitoring Loop

**Poll Interval:** 30 seconds  
**Health Check:** Every 5 minutes (update campaign tracker)  
**Max Duration:** 15 minutes (900 seconds)

```
t=0:
  Tier 1 Monitoring Starts
  Poll workflow status every 30 seconds
  Log results to .codex/PHASE_3_WORKFLOW_MONITOR.log

t=5min:
  Update .codex/PHASE_3_CAMPAIGN.md with progress
  Check Gate 1 criteria
  
t=10min:
  Evaluate Tier 1 completion status
  Prepare Tier 2 activation if needed
  
t=15min:
  GATE 1 TIMEOUT CHECK
  IF all workflows not complete:
    → Escalate to human (@mbaetiong)
  ELSE IF Gate 1 criteria met:
    → ACTIVATE TIER 2
    → Begin Tier 2 workflow dispatch
```

---

## V. Gate Criteria & Activation

### Gate 1: Tier 1 Success (Current)

**PASS Criteria:**
```
✅ All 10 Tier 1 workflows completed
✅ All conclusions = success OR skipped
✅ 0 unhealed critical failures (P0-P1)
✅ No regressions in any healed workflow
```

**FAIL Criteria:**
```
❌ Any workflow conclusion = failure after 2min heal window
❌ Heal timeout > 15 minutes
❌ Any P0 failure remains unhealed
```

**Status:** 🔵 IN PROGRESS

---

### Gate 2: Tier 2 Success (Upon Gate 1 Pass)

**Activation:**
```
IF Gate 1 passes:
  → Trigger workflow-analytics-agent for Tier 2 baselining
  → Spawn parallel monitoring for 28 workflows
  → LOG: "TIER 2 ACTIVATED at [timestamp]"
  → Wait for 28 workflows to complete
```

**Status:** ⚪ STANDBY

---

### Gate 3: Security Closure (Upon Gate 2 Pass)

**Activation:**
```
IF Gate 2 passes:
  → Call parallel_validation (CodeQL + Code Review)
  → Delegate to unified-security-scanner (Semgrep)
  → Await security closure findings
  → Generate final compliance report
  → IF all security issues resolved or documented:
    → CAMPAIGN SUCCESS
  ELSE:
    → Route to security-alert-verification-agent
```

**Status:** ⚪ STANDBY

---

## VI. Failure Escalation Chain

```
Auto-Fixable Failure (P0-P1)
  ↓ (Route to specialist agent)
  ├─ Fix + log in .codex/PHASE_3_FAILURE_LOG.json
  ├─ Grade on 0-100 rubric
  └─ If score ≥70: Continue; <70: Retry or escalate

Manual Review Required (P2-P3)
  ↓ (Route to specialist agent)
  ├─ Analyze + propose fix
  ├─ Human approval gate
  └─ Log decision in tracking file

Unresolvable Failure (No pattern match)
  ↓ (Escalate to human)
  └─ @mbaetiong with full context:
     - Workflow name & run ID
     - Complete failure log
     - All attempted fixes
     - Recommendation
```

---

## VII. Campaign Artifacts

### Real-Time Tracking
- **`.codex/PHASE_3_CAMPAIGN.md`** — Live progress table (updated every 5min)
- **`.codex/PHASE_3_WORKFLOW_MONITOR.log`** — Continuous polling log (every 30sec)

### Final Deliverables
- **`.codex/PHASE_3_FAILURE_LOG.json`** — All failures + fixes + grades
- **`.codex/PHASE_3_FINAL_REPORT.md`** — Tier 1-3 completion summary + security closure
- **`.codex/PHASE_3_AGENT_DISPATCH_LOG.json`** — Full agent delegation audit trail

### Format Examples

#### PHASE_3_FAILURE_LOG.json
```json
{
  "campaign_id": "PHASE_3_2026-07-02T19:02:08Z",
  "timestamp": "2026-07-02T19:XX:XXZ",
  "failures": [
    {
      "id": "failure_001",
      "workflow": "Validation Pipeline",
      "run_id": 28614560814,
      "pattern": "AttributeError",
      "detected_at": "2026-07-02T19:05:00Z",
      "agent_routed": "ci-testing-agent",
      "routed_at": "2026-07-02T19:05:05Z",
      "healed_at": "2026-07-02T19:06:00Z",
      "grade": 92,
      "status": "resolved"
    }
  ]
}
```

---

## VIII. Authority & Token Management

**Activation Authority:**
- ✅ `wec:auto-approve` label on PR #5194
- ✅ `CODEX_MASTER_KEY` environment variable set
- ✅ Autonomous GO-CONTINUE mode enabled

**API Operations:**
- GitHub Actions API for workflow status
- Elevated token access via `CODEX_MASTER_KEY`
- Auto-approval of pending workflow runs

---

## IX. Anti-Patterns (Never Do)

- ❌ Route ALL failures to `ci-testing-agent` without triage (causes agent fatigue)
- ❌ Grade before all failures are verified fixed
- ❌ Skip documentation step to save time (compliance violation)
- ❌ Allow any agent to mark tests `xfail(strict=False)` without root-cause doc
- ❌ Escalate without providing full context to human reviewer
- ❌ Skip Tier 1 completion before triggering Tier 2/3

---

## X. Success Criteria

**Campaign Complete When:**
1. ✅ Gate 1 passed (all Tier 1 workflows green)
2. ✅ Gate 2 passed (all Tier 2 workflows green)
3. ✅ Gate 3 passed (security closure complete)
4. ✅ All deliverables generated
5. ✅ Final report posted to PR

**Expected Timeline:**
- Campaign Start: 2026-07-02T19:02:08Z
- Target Completion: 2026-07-02T20:30:00Z (88-minute window)

---

**Last Updated:** 2026-07-02T19:04:16Z  
**Next Update:** 2026-07-02T19:09:16Z (5-minute cycle)
