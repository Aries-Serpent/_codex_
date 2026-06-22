# PHASE 9.1: D_CAPABLE Decision Framework Specification

**Version:** 1.0.0  
**Generated:** 2026-06-22T11:12:24Z  
**Author:** orchestrator-agent  
**Status:** ✅ ACTIVE

---

## Executive Summary

This framework defines the decision-making model for 9 D_CAPABLE agents operating with autonomous authority within the Aries-Serpent/_codex_ repository. All decisions are logged, scored for confidence, and escalated to human review when confidence drops below predefined thresholds.

**Key Metrics:**
- **9 Authorized Agents:** Expanded from 3-5 to full roster
- **Decision Logging:** 100% coverage with immutable audit trail
- **Confidence Scoring:** Multi-factor algorithm (40/30/20/10 weights)
- **Escalation Triggers:** <60% critical decisions require human approval
- **Target Accuracy:** 90%+ on 100+ test scenarios
- **False Positive Rate:** <2% on high-risk decisions

---

## Part 1: D_CAPABLE Decision Model

### 1.1 Decision Types

All agent decisions fall into one of four categories:

#### TYPE A: Low-Risk, Read-Only Analysis
- **Examples:** Pattern recognition, static validation, audit checks
- **Agents:** ci-health-alert-agent, packaging-validation-agent, rust-error-validator
- **Authority:** Autonomous execution; no escalation required >80% confidence
- **Escalation Threshold:** <65%
- **Confidence Weight:** Historical accuracy (50%), context complexity (30%), coverage (20%)

#### TYPE B: Medium-Risk, Structured Modifications
- **Examples:** Workflow file updates, test assertion generation, configuration validation
- **Agents:** workflow-ci-fixer, test-assertion-updater, energy-conversion-agent
- **Authority:** Autonomous with audit trail; escalate if confidence <75%
- **Escalation Threshold:** <60-65%
- **Confidence Weight:** Historical accuracy (40%), context complexity (30%), pre-deployment tests (20%), manual signals (10%)

#### TYPE C: High-Risk, Code Modifications
- **Examples:** Test file changes, CI logic modifications, session orchestration
- **Agents:** ci-testing-agent, test-pattern-guardian, copilot-session-chain
- **Authority:** Conditional autonomous (confidence >75%); standard escalation <60%
- **Escalation Threshold:** <60% (CRITICAL)
- **Confidence Weight:** Historical accuracy (40%), test coverage (25%), context complexity (20%), manual signals (15%)

#### TYPE D: Reserved - System-Critical
- **Examples:** Security policy changes, deployment authorization, data deletion
- **Agents:** NONE currently authorized
- **Authority:** Requires explicit human pre-approval + post-execution audit
- **Escalation Threshold:** Always human-approved
- **Confidence Weight:** N/A (human-gated)

---

### 1.2 Decision Lifecycle

```
┌─────────────────┐
│  Trigger Event  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ 1. Decision Context Analysis        │
│   - Gather input parameters         │
│   - Validate pre-conditions         │
│   - Assess complexity/uncertainty   │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ 2. Confidence Scoring               │
│   - Historical accuracy baseline    │
│   - Context complexity analysis     │
│   - Test coverage assessment        │
│   - Manual override signals         │
│   → Final confidence score (0-100)  │
└────────┬────────────────────────────┘
         │
         ▼
    ┌────────────────────────────┐
    │ Confidence >= Threshold?   │
    └────────┬────────┬──────────┘
             │        │
        YES  │        │ NO
             │        │
             ▼        ▼
      ┌───────────┐  ┌──────────────────────┐
      │ EXECUTE   │  │ Escalate to Human    │
      │ Decision  │  │ - Log decision ID    │
      │           │  │ - Send notification  │
      │           │  │ - Wait for approval  │
      └─────┬─────┘  └──────────┬───────────┘
            │                    │
            │                    ▼
            │            ┌─────────────────┐
            │            │ Human Review    │
            │            │ - Analyze       │
            │            │ - Override?     │
            │            └────────┬────────┘
            │                     │
            │                     ▼
            │            ┌─────────────────┐
            │            │ Execute or      │
            │            │ Modify Decision │
            │            └────────┬────────┘
            │                     │
            └──────────┬──────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │ 3. Execute Decision  │
            │   - Apply changes    │
            │   - Log outcome      │
            │   - Record result    │
            └──────────┬───────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │ 4. Post-Execution    │
            │   Audit              │
            │   - Verify outcome   │
            │   - Record validation│
            │   - Update metrics   │
            └──────────┬───────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │ Decision Complete    │
            │ (Immutable Log)      │
            └──────────────────────┘
```

---

## Part 2: Confidence Scoring Algorithm

### 2.1 Multi-Factor Scoring (0-100 scale)

Each decision gets a confidence score calculated from 4 factors:

```
Final Confidence = (
    Historical Accuracy × 0.40 +
    Context Complexity × 0.30 +
    Test Coverage × 0.20 +
    Manual Signals × 0.10
)
```

#### Factor 1: Historical Accuracy (Weight: 40%)
- **Source:** Agent's previous decision outcomes (past 90 days)
- **Calculation:** (Successful Decisions / Total Decisions) × 100
- **Range:** 0-100 (requires >10 decisions for baseline)
- **Default:** 75 (conservative baseline for new agents)
- **Examples:**
  - ci-testing-agent: 89/95 = 93.7% → 93.7 points
  - workflow-ci-fixer: 67/78 = 85.9% → 85.9 points
  - test-assertion-updater: 34/42 = 80.9% → 80.9 points

#### Factor 2: Context Complexity Analysis (Weight: 30%)
- **Source:** Real-time analysis of decision context
- **Calculation:** 100 - (Complexity Score × 20)
- **Complexity Factors:**
  - **0 (Simple):** Single-agent decision, no dependencies → 100 points
  - **1 (Low):** Single-agent, 1-2 dependencies → 80 points
  - **2 (Medium):** Multi-agent coordination or complex analysis → 60 points
  - **3 (High):** Cross-system impact, multiple dependencies → 40 points
  - **4 (Critical):** System-wide impact, many unknowns → 20 points
  - **5 (Unknown):** Novel scenario, insufficient data → 0 points
- **Examples:**
  - Updating single workflow job: 100 points (simple)
  - Fixing test assertions in one file: 80 points (low complexity)
  - Coordinating session chains across 3+ services: 40 points (high complexity)

#### Factor 3: Test Coverage (Weight: 20%)
- **Source:** Pre-deployment test results for this decision type
- **Calculation:** (Pass Rate of Relevant Tests) × 100
- **Requirements:**
  - Minimum 10 relevant test cases per agent
  - Tests must cover decision's specific code path
  - Must pass in CI environment
- **Examples:**
  - ci-testing-agent: 98/100 decision path tests pass → 98 points
  - packaging-validation-agent: 45/45 validation tests pass → 100 points
  - test-assertion-updater: 38/40 assertion tests pass → 95 points

#### Factor 4: Manual Override Signals (Weight: 10%)
- **Source:** Human feedback, explicit overrides, annotations
- **Signals:**
  - `--high-confidence`: +15 points (override if human confidence known)
  - `--caution`: -20 points (human concerns about decision)
  - `--block`: -100 points (explicit human block; always escalate)
  - No signal: 0 points (neutral)
- **Usage:** Command-line flags passed to decision logger
- **Examples:**
  - `decision_logger execute --agent ci-testing-agent --high-confidence` → +15
  - `decision_logger execute --agent test-assertion-updater --caution` → -20

### 2.2 Confidence Score Interpretation

| Confidence Range | Label | Action | Escalation |
|------------------|-------|--------|------------|
| 95-100 | ✅ VERY HIGH | Execute immediately | None |
| 85-94 | ✅ HIGH | Execute immediately | None |
| 75-84 | ⚠️ MEDIUM-HIGH | Execute with logging | None (monitor) |
| 60-74 | ⚠️ MEDIUM | Execute with audit trail | Standard escalation |
| 50-59 | ⚠️ MEDIUM-LOW | Escalate to human | **REQUIRED** |
| 0-49 | ❌ LOW | Block execution; escalate | **CRITICAL** |

### 2.3 Escalation Thresholds by Agent Type

| Agent | Risk Level | TYPE | Escalation Threshold | Comment |
|-------|-----------|------|----------------------|---------|
| ci-health-alert-agent | LOW | A | <65% | Read-only; permissive |
| packaging-validation-agent | LOW | A | <65% | Static analysis only |
| rust-error-validator | LOW | A | <70% | Rust-specific domain |
| test-pattern-guardian | LOW | A | <65% | Guidance generation |
| workflow-ci-fixer | LOW | B | <70% | Workflow modifications |
| energy-conversion-agent | MEDIUM | B | <65% | Scientific computation |
| ci-testing-agent | MEDIUM | C | <60% | **CRITICAL** - code mod |
| copilot-session-chain | MEDIUM | C | <60% | **CRITICAL** - sessions |
| test-assertion-updater | MEDIUM | C | <60% | **CRITICAL** - code mod |

---

## Part 3: Risk Categories & Thresholds

### 3.1 Risk Category Definitions

#### Category 1: Observability & Alerts (0.5% risk)
- **Agents:** ci-health-alert-agent
- **Impact:** Alerts, notifications; no state changes
- **Recovery:** Reverse alert; no system impact
- **Policy:** Autonomous execution >70% confidence

#### Category 2: Static Validation (2% risk)
- **Agents:** packaging-validation-agent, rust-error-validator
- **Impact:** Read-only validation; guidance generation
- **Recovery:** Regenerate validation; no data loss
- **Policy:** Autonomous execution >65% confidence

#### Category 3: Workflow & Configuration (5% risk)
- **Agents:** workflow-ci-fixer, test-pattern-guardian
- **Impact:** Configuration changes; reversible via git
- **Recovery:** Revert commit; restore from backup
- **Policy:** Autonomous execution >70% confidence; escalate <70%

#### Category 4: Test & Assertion Modifications (10% risk)
- **Agents:** test-assertion-updater, ci-testing-agent
- **Impact:** Test file changes; potential false negatives
- **Recovery:** Review changes; revert if needed
- **Policy:** Escalate if confidence <60%; mandatory audit trail

#### Category 5: Session & Orchestration (8% risk)
- **Agents:** copilot-session-chain
- **Impact:** Multi-session coordination; state changes
- **Recovery:** Reset session state; restart workflows
- **Policy:** Escalate if confidence <60%; mandatory audit trail

#### Category 6: Domain-Specific Computation (3% risk)
- **Agents:** energy-conversion-agent
- **Impact:** Scientific calculations; no system impact
- **Recovery:** Recalculate; rerun simulations
- **Policy:** Autonomous execution >65% confidence

---

### 3.2 High-Risk False Positives

**Definition:** Decision executed with high confidence (>80%) but produces incorrect outcome.

**Target Rate:** <2% across all 9 agents
**Monitoring:** Daily review via audit trail query
**Escalation:** Any agent exceeding 2% false positive rate → immediate human review

**Example Scenarios:**
- ci-testing-agent: Suggests test fix that masks real bug (false positive)
- test-assertion-updater: Generates assertion that matches new bug, not expected behavior
- workflow-ci-fixer: "Fixes" workflow job that actually had intentional configuration

---

## Part 4: Rollback Procedures

### 4.1 Decision Rollback (within 2 hours)

**Trigger:** False positive detected; human override; high-risk escalation failed

**Steps:**
1. **Identify Decision:** Query audit trail by decision_id
2. **Analyze Impact:** Review what was changed/executed
3. **Revert Changes:** `git revert <commit_hash>` or undo operation
4. **Log Rollback:** `decision_logger rollback --decision-id <id> --reason "..."`
5. **Notify Stakeholders:** Post GitHub comment on associated PR/issue
6. **Update Agent Confidence:** Reduce agent's historical accuracy baseline by 10%

**Example:**
```bash
# Identify problem decision
decision_logger query --decision-id phase-9-1-dec-2026-06-22-042 --full

# Review changes
git show <commit_hash>

# Rollback
git revert <commit_hash>

# Log the rollback
decision_logger rollback \
  --decision-id phase-9-1-dec-2026-06-22-042 \
  --reason "False positive: Test assertion matched bug, not expected behavior" \
  --agent test-assertion-updater
```

### 4.2 Agent Suspension (>24 hours required)

**Trigger:** Agent exceeds 2% false positive rate; confidence baseline drops below 60%

**Steps:**
1. **Immediate Pause:** Set agent autonomy_model to "E" (advisory only)
2. **Human Review:** Analyze last 20-30 decisions for patterns
3. **Root Cause Analysis:** Identify systematic issues
4. **Corrective Action:** Code fix, re-training, or policy update
5. **Confidence Reset:** Recalibrate baseline after fixes
6. **Re-authorization:** Require explicit approval to restore D_CAPABLE status

---

## Part 5: Human Intervention Points

### 5.1 Mandatory Human Review

The following decisions **require** human review before execution:

1. **Confidence <60%:** Any decision below medium-high confidence
2. **High-Risk Categories:** Test modifications, session orchestration
3. **Unknown Scenarios:** Novel decision types not in training data
4. **Manual Blocks:** Explicit `--block` flag in decision context
5. **Escalation Triggers:** Agent-specific thresholds breached

### 5.2 Optional Human Review (Audit)

The following decisions are **logged for audit** but can execute autonomously:

1. **Confidence 60-75%:** Medium range; logged but executed
2. **Novel Agent Combinations:** New handoff paths
3. **Large-Scale Changes:** Affecting >50 files or >10 test files

### 5.3 Human Approval Workflow

**Timeline:** Max 5 minutes to review & approve/reject

```
Decision Request (confidence <60%) sent to human
    ↓
    [Email + GitHub notification]
    ↓
    [Human reviews decision context]
    ↓
    [Approve / Reject / Modify]
    ↓
    Execute with human feedback OR Block decision
    ↓
    Log outcome + human decision
```

---

## Part 6: Audit & Logging Requirements

### 6.1 Decision Log Entry

Every D_CAPABLE decision generates an immutable log entry:

```json
{
  "decision_id": "phase-9-1-dec-2026-06-22-042",
  "timestamp": "2026-06-22T11:15:30.123Z",
  "agent_id": "test-assertion-updater",
  "decision_type": "TYPE_B",
  "risk_category": "test_modifications",
  "input_context": {
    "trigger": "api_change_detected",
    "files_affected": ["tests/unit/test_api.py", "tests/integration/test_endpoints.py"],
    "api_changes": "UserModel.email field added"
  },
  "confidence_score": 78.5,
  "confidence_factors": {
    "historical_accuracy": 80.9,
    "context_complexity": 80,
    "test_coverage": 95,
    "manual_signals": 0
  },
  "escalation_threshold": 60,
  "escalated": false,
  "decision_action": "EXECUTE",
  "execution_details": {
    "changes_made": 12,
    "files_modified": 2,
    "test_commands_run": ["pytest tests/unit/test_api.py -v"]
  },
  "outcome": "SUCCESS",
  "validation_timestamp": "2026-06-22T11:16:15.456Z",
  "human_review_requested": false,
  "human_review_provided": null,
  "created_by": "orchestrator-agent",
  "created_on": "2026-06-22T11:12:24Z"
}
```

### 6.2 Audit Trail Immutability

- **Format:** Append-only SQLite database
- **Index:** Decision_id, timestamp, agent_id, confidence_score
- **Backup:** Daily export to GitHub gist + cloud storage
- **Retention:** 12 months minimum
- **Query Speed:** <30 seconds for any time range

---

## Part 7: Success Metrics

### 7.1 Phase 9.1 Success Criteria

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Decision logging framework deployed | ✅ | Pending | 🔴 |
| Confidence scoring operational | ✅ | Pending | 🔴 |
| 100+ test scenarios passing | 90%+ | Pending | 🔴 |
| False positive rate | <2% | Pending | 🔴 |
| Audit trail queryable | <30s | Pending | 🔴 |
| All 9 agents authorized | ✅ | ✅ | 🟢 |
| Rollback plan tested | ✅ | Pending | 🔴 |

### 7.2 Ongoing Monitoring

**Daily Checks:**
- False positive rate per agent
- Confidence score distribution
- Escalation frequency
- Human review response time

**Weekly Reports:**
- Agent accuracy trends
- Risk category distribution
- Policy violation incidents
- Rollback events

---

## Part 8: Phase 9.1 Timeline

| Task | Duration | Dependencies | Status |
|------|----------|--------------|--------|
| TASK 9.1.1: Identify & authorize agents | 0.5 days | None | ✅ DONE |
| TASK 9.1.2: Build decision logging | 1 day | 9.1.1 | 🔄 IN PROGRESS |
| TASK 9.1.3: Implement confidence scoring | 1 day | 9.1.2 | 🔄 IN PROGRESS |
| TASK 9.1.4: Build audit trail | 0.5 days | 9.1.2 | 🔄 PENDING |
| TASK 9.1.5: Test decision accuracy | 1.5 days | 9.1.3, 9.1.4 | 🔄 PENDING |
| TASK 9.1.6: Deploy authorization | 0.5 days | 9.1.5 | 🔄 PENDING |

**Execution Window:** 2026-06-30 → 2026-07-05 (5 days)  
**GO/NO-GO Decision:** 2026-07-05 17:00 UTC by @mbaetiong

---

## References

- `.codex/PHASE_9_1_CANDIDATE_AGENTS.md` — Authorized agents list
- `scripts/ci/phase_9_1_decision_logger.py` — Logging implementation
- `scripts/ci/phase_9_1_confidence_scorer.py` — Scoring implementation
- `tests/unit/test_phase_9_1_decisions.py` — Test suite (100+ scenarios)
- `.codex/PHASE_9_1_AGENT_AUTHORIZATION_SUMMARY.md` — Final authorization

---

**Framework Version:** 1.0.0  
**Last Updated:** 2026-06-22T11:12:24Z  
**Authority:** @mbaetiong (D-tier approved)  
**Status:** ✅ ACTIVE & OPERATIONAL
