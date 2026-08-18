# Self-Healing Policy Tiers (T0-T3)

**Date:** 2026-07-13  
**Version:** 1.0  
**Authority:** @mbaetiong (D-tier autonomous)  

---

## Overview

This document defines the 4-tier policy framework for self-healing automation. Each tier controls automation level, approval requirements, incident scope, and evidence collection.

**Core Principle:** Higher tiers require proportionally higher governance gates before execution. T0/T1 auto-execute with audit trails; T2/T3 require explicit approval.

**Authoritative approval contract:** Tier 1 has no approval gate and is auto-executed with a post-hoc audit trail; Tier 3 requires @mbaetiong plus two stakeholder sign-offs before governance changes can proceed.

---

## Tier 0: Metadata & Configuration (Auto-Execute, Zero Approval)

**Automation Level:** 100% autonomous  
**Approval Required:** None  
**Evidence:** Decision trace + input-lock hash  
**Typical MTTR:** <5 minutes  
**Risk Level:** Minimal (no behavior change)  

### Scope

Operations that do NOT change system behavior, only observability or internal state:

1. **Output Logging** — Enable/disable logging levels, change log format
2. **Configuration Overrides** — Update non-policy configuration values
3. **Observability Instrumentation** — Add/update metrics, traces, alerts
4. **Metadata Updates** — Update version numbers, timestamps, artifact references
5. **State Snapshots** — Capture decision traces, manifest generation
6. **Documentation** — Update runbooks, guides, decision rationale

### Examples

```
✅ Enabled debug logging for Lane A
✅ Updated observability metric for security factory wave count
✅ Captured decision-trace JSONL for lane orchestration
✅ Generated lane-manifest.json with current execution state
✅ Updated MTTR baseline after phase completion
```

### Not Tier 0

```
❌ Fix failing test (behavior change → Tier 1)
❌ Patch security vulnerability (code change → Tier 2)
❌ Update incident suppression policy (policy change → Tier 2)
```

### Execution & Audit Trail

```python
# Lane owner autonomous execution
healing_agent.execute_tier_0_action(action_type="enable_logging")

# Automatic decision trace emission
decision_trace.log({
    "tier": "T0",
    "action": "enable_logging",
    "timestamp": ISO8601_UTC_Z,
    "input_lock": input_lock_hash,
    "outcome": "success",
    "evidence": ["decision-trace.jsonl", "lane-manifest.json"]
})
```

### Audit Review

- Weekly aggregation to `AGENT_ACCOUNTABILITY_REPORT.md`
- No blocking review required
- Logged in `.codex/decision_traces/` for drift detection

---

## Tier 1: Low-Risk Operational Changes (Auto-Execute with Audit)

**Automation Level:** 100% autonomous + audit trail  
**Approval Required:** None (post-hoc audit)  
**Evidence:** Decision trace + change summary + affected module list  
**Typical MTTR:** <30 minutes  
**Risk Level:** Low (isolated, low-impact changes)  

### Scope

Operational changes with contained blast radius and minimal risk to system integrity:

1. **Test Fixes** — Fix failing tests with <5 lines changed, no API/behavior changes
2. **Documentation Updates** — README, CONTRIBUTING, guides, examples
3. **Minor Version Bumps** — Non-breaking dependency updates
4. **Observability Configuration** — Dashboard updates, alert thresholds (non-critical)
5. **Low-Risk Workflow Tweaks** — GitHub Actions non-core jobs (e.g., lint, format)
6. **Scaffold Fixes** — Generated code regeneration from templates

### Examples

```
✅ Fix test_determinism_baseline.py (1 line: seed initialization)
✅ Update README with Phase 1 progress
✅ Bump pytest from 7.3.1 → 7.4.0 (patch version)
✅ Update CI workflow artifact upload path
✅ Regenerate TypeScript types from schema
```

### Not Tier 1

```
❌ Fix test that validates security gate behavior (core logic → Tier 2)
❌ Bump torch 2.0 → 2.1 (major version, ML inference change → Tier 2)
❌ Update incident suppression threshold (policy change → Tier 2)
❌ Modify healing approval routing logic (governance change → Tier 2)
```

### Execution & Audit Trail

```python
# Lane owner autonomous execution with audit
healing_agent.execute_tier_1_action(
    action_type="fix_test",
    description="Fix seed initialization in determinism test",
    files_changed=["tests/orchestration/test_determinism_baseline.py"]
)

# Automatic audit trail generation
decision_trace.log({
    "tier": "T1",
    "action": "fix_test",
    "description": "Fix seed initialization in determinism test",
    "timestamp": ISO8601_UTC_Z,
    "input_lock": input_lock_hash,
    "changed_modules": ["tests/orchestration"],
    "affected_subsystems": ["determinism_validation"],
    "outcome": "success",
    "regression_test_results": "ALL_PASS",
    "evidence": ["test_run_log.json", "decision-trace.jsonl"]
})
```

### Audit Review

- Weekly audit by Lane I (Governance)
- Post-change regression tests required (must pass)
- Drift detection threshold: <2 Tier 1 actions per day per lane
- Anomaly trigger: If same action repeated 3+ times → escalate to Tier 2

---

## Tier 2: Code-Level Changes & Security Patches (Proposal Required)

**Automation Level:** Manual execution (lane owner + @mbaetiong)  
**Approval Required:** @mbaetiong within 24h  
**Evidence:** Input-lock hash, output-contract schema, decision-trace, risk assessment  
**Typical MTTR:** 2-8 hours (due to approval gate)  
**Risk Level:** Medium (affects code behavior, security posture, public API)  

### Scope

Changes that modify system behavior, security posture, or public contracts:

1. **Security Vulnerability Fixes** — CVE patches, vulnerability remediation
2. **Dependency Updates** — Major/minor version bumps affecting behavior
3. **New Public API** — Adding new publicly exported functions/classes
4. **Behavior-Changing Refactors** — Logic changes that alter observable behavior
5. **Performance Optimizations** — >10% improvement with risk of regression
6. **Policy Updates** — Severity thresholds, tier classifications, approval chains
7. **Healing Strategy Changes** — New incident type handling, strategy ranking

### Examples

```
✅ Apply security patch for CVE-2026-XXXXX in cryptography library
✅ Refactor decision-trace writer for 15% latency improvement
✅ Add new public API: `healing_agent.execute_with_approval_chain()`
✅ Update incident severity thresholds for self-healing
✅ Implement new healing strategy for "flaky test" incident type
```

### Not Tier 2 (Tier 3 Required)

```
❌ Change tier system from T0-T3 → T0-T5 (governance framework change → Tier 3)
❌ Modify transfer fabric trust boundaries (multi-sandbox security → Tier 3)
❌ Update healing approval chain to require 3 signatures (policy → Tier 3)
❌ Disable quantum-hybrid promotion gates (core capability change → Tier 3)
```

### Approval Workflow

```
1. Lane owner generates change proposal:
   src/orchestration/gates/contract_gate.py --validate-proposal \
     --risk-level medium \
     --affected-subsystems security,healing \
     --regression-tests required

2. 8-gate compliance check:
   ✓ Gate 1: Contract validation
   ✓ Gate 2: Regression tests pass
   ✓ Gate 3: Security audit pass
   ✓ Gate 4: Policy tier compliance
   ✓ Gate 5: Input-lock immutability
   ✓ Gate 6: Output-contract matches expected schema
   ✓ Gate 7: Decision-trace integrity
   ✓ Gate 8: Rollback instruction completeness

3. @mbaetiong reviews within 24h:
   - Risk assessment accuracy
   - Evidence completeness
   - Regression test adequacy
   - Impact on other lanes

4. Approval decision:
   APPROVED  → Execute immediately
   MODIFY   → Lane owner adjusts proposal
   DEFERRED → Schedule for next phase
   REJECTED → Alternative approach required

5. Post-execution audit:
   - Verify all 8 gates still pass
   - Confirm output-contract met
   - Log decision trace with approval chain
```

### Evidence Requirements

Each Tier 2 proposal requires:

1. **Input-Lock Hash** — SHA256 of policy config + solver info + checksums
2. **Output-Contract** — Expected outputs (schema, metrics, success criteria)
3. **Decision-Trace** — Pre-execution trace template
4. **Risk Assessment** — Severity (low/medium/high), blast radius, rollback plan
5. **Regression Tests** — Specific tests to validate fix doesn't break system
6. **Rollback Instructions** — Exact `git revert` + any data migration steps
7. **Approval Justification** — Why this change is necessary at this time

### Execution & Validation

```python
# Lane owner executes upon approval
healing_agent.execute_tier_2_action(
    proposal_id="SEC-2026-001",
    approval_signature=mbaetiong_approval_token,
    description="Apply CVE-2026-XXXXX security patch"
)

# 8-gate compliance validation
gate_result = contract_gate.validate_tier_2_execution(
    input_lock_hash=input_lock,
    output_contract=expected_outputs,
    decision_trace_log=trace_file,
    rollback_instructions=rollback_plan
)

if gate_result.all_gates_pass():
    # Log approval chain
    decision_trace.log({
        "tier": "T2",
        "proposal_id": "SEC-2026-001",
        "approver": "@mbaetiong",
        "approval_timestamp": ISO8601_UTC_Z,
        "execution_timestamp": ISO8601_UTC_Z,
        "evidence": [
            "input-lock.json",
            "output-contract.json",
            "decision-trace.jsonl",
            "risk-assessment.md",
            "rollback-instruction.json"
        ]
    })
else:
    # Automatic rollback on gate failure
    healing_agent.execute_rollback(rollback_instruction)
```

---

## Tier 3: Governance & Policy Changes (Stakeholder Gate)

**Automation Level:** Manual execution (requires stakeholder consensus)  
**Approval Required:** @mbaetiong + 2 nominated stakeholders  
**Evidence:** Full provenance chain, determinism certification, 50+ replay tests  
**Typical MTTR:** 3-7 days (stakeholder review cycle)  
**Risk Level:** High (affects governance model, core capabilities)  

### Scope

Structural changes to governance, policy framework, or core capabilities:

1. **Tier System Changes** — Modify T0-T3 definitions, thresholds, automation rules
2. **Lane Framework Changes** — Add/remove lanes, modify lane boundaries
3. **Healing Policy Framework** — Change approval chain structure, authority hierarchy
4. **Quantum-Hybrid Promotion Gates** — Modify KPI thresholds, shadow mode exit criteria
5. **Transfer Fabric Security** — Modify trust boundaries, policy plane definitions
6. **SLA/Error Budget** — Redefine error budgets, SLO targets, incident severity
7. **Governance Review Cycle** — Change monthly review cadence, drift detection logic

### Examples

```
✅ Extend tier system T0-T3 → T0-T5 (for ultra-high-risk changes)
✅ Modify quantum-hybrid promotion KPI threshold 5% → 8%
✅ Change healing approval chain from 1 signature → 2 signatures
✅ Update transfer fabric trust boundaries for new sandbox
✅ Redefine error budget allocation across lanes A-K
```

### Not Tier 3 (Pre-Tier 3 Negotiation)

```
❌ Change specific incident type handling (Tier 2 proposal)
❌ Bump single dependency version (Tier 2)
❌ Fix single security vulnerability (Tier 2)
```

### Approval Workflow

```
1. Lane I (Governance) initiates stakeholder review:
   - Creates GitHub issue labeled "governance-review"
   - Tags @mbaetiong + 2 nominated stakeholders
   - Attaches full evidence packet

2. Stakeholder review (3-7 days):
   - @mbaetiong reviews impact on lanes A-K
   - Stakeholder 1 reviews impact on security/compliance
   - Stakeholder 2 reviews impact on operations/SRE
   - Each stakeholder signs off or requests modifications

3. Consensus decision:
   APPROVED (3 signatures)  → Schedule for next phase
   MODIFY REQUESTED        → Negotiate proposals
   REJECTED (any veto)     → Alternative approach required

4. Implementation (upon approval):
   - Create implementation ticket in next phase
   - Document rationale in `.codex/GOVERNANCE_CHANGE_YYYY_MM_DD.md`
   - Include 50+ replay verification tests
   - Schedule mandatory training for all lane owners

5. Post-implementation audit:
   - 30-day drift monitoring (acceptable range ±5%)
   - Monthly review for unintended consequences
   - Rollback option remains available for 90 days
```

### Evidence Requirements

Each Tier 3 change requires comprehensive packet:

1. **Full Provenance Chain** — Git history, decision traces, prior proposals
2. **Determinism Certification** — 50+ replay verification tests all passing
3. **Impact Analysis** — Detailed impact on each lane (A-K)
4. **Rollback Plan** — Step-by-step recovery to prior governance state
5. **Training Materials** — Updated documentation for lane owners
6. **Historical Precedent** — Similar changes in other systems, lessons learned
7. **Stakeholder Risk Assessment** — Each stakeholder's risk analysis + concerns

---

## Tier Escalation Rules

### Auto-Escalation Triggers

The following conditions automatically escalate a proposed action to next tier:

```
Tier 0 → Tier 1:
  IF action_affects_regression_tests OR action_affects_public_API
  THEN escalate_to_tier_1

Tier 1 → Tier 2:
  IF same_action_repeated_3_times OR action_affects_security_posture
  THEN escalate_to_tier_2

Tier 2 → Tier 3:
  IF action_affects_governance_framework OR action_affects_tier_system
  THEN escalate_to_tier_3

Tier 3 → BLOCKED:
  IF stakeholder_consensus_not_reached
  THEN block_until_consensus
```

### Manual Escalation

Lane owners may manually escalate action to higher tier if:
- Risk assessment indicates higher tier appropriate
- Uncertainty about tier classification
- Desire additional approval gates
- Preparation for policy precedent

---

## Tier Metrics & Monitoring

### Dashboard Metrics (Real-time)

```
Lane A Tier Distribution (Last 7 Days):
  T0: 145 actions (68%)
  T1: 52 actions  (24%)
  T2: 15 actions  (7%)
  T3: 1 action    (0.5%)

Lane A Tier Velocity:
  T0: 21 actions/day (target: 15-25)
  T1: 7.4 actions/day (target: <10)
  T2: 2.1 actions/day (target: <5)
  T3: 0.14 actions/day (target: <1/week)

Approval Latency (T2):
  Median: 4.2 hours
  p95: 18 hours
  Target: <24 hours
  ✅ PASS

Approval Success Rate (T2):
  Approved: 87%
  Modified: 11%
  Rejected: 2%
  Target: >85% approval rate

Stakeholder Review Time (T3):
  Median: 4.8 days
  Target: 3-7 days
  ✅ PASS
```

### Anomaly Detection

```
IF tier_distribution_outside_range:
  THEN generate_drift_detection_issue

IF approval_latency_p95 > 24_hours:
  THEN escalate_bottleneck

IF same_tier_2_action_repeated_5_times:
  THEN suggest_tier_3_governance_change

IF tier_3_rejections > 30_percent:
  THEN schedule_stakeholder_governance_review
```

---

## Transition Rules Between Tiers

### Within Single Incident

- Start at lowest applicable tier
- Escalate mid-incident if risk assessment changes
- Cannot de-escalate mid-incident (only after resolution)
- All escalations logged in decision-trace with rationale

### Between Incidents

- Tier classification sticky per incident type (first occurrence sets tier)
- Reclassification allowed with stakeholder review (Tier 3 change)
- Lane owner may propose tier up/down with justification (annual review)

---

## Tier Compliance Enforcement

### Automated Enforcement

```python
# On every healing action
@healing_action_executor.enforce_tier_compliance
def execute_healing_action(action):
    tier = classify_action_tier(action)
    
    if tier == "T0":
        execute_immediately(action)
        emit_decision_trace()
    
    elif tier == "T1":
        result = execute_immediately(action)
        emit_decision_trace()
        if not result.success:
            escalate_to_tier_2(action, reason="Execution failure")
    
    elif tier == "T2":
        proposal = generate_proposal(action)
        await mbaetiong_approval(proposal)
        if approved:
            result = execute(action)
            if not result.success and result.error_critical:
                execute_rollback(action)
        else:
            propose_alternative_approach(action)
    
    elif tier == "T3":
        issue = create_stakeholder_review_issue(action)
        await stakeholder_consensus(issue)
        if consensus_reached:
            schedule_implementation(action, next_phase=True)
```

### Manual Review (Monthly)

Lane I (Governance) monthly review:
- Sample 10% of T0 actions → verify minimal blast radius
- Audit 100% of T2 actions → check approval chain
- Review 100% of T3 changes → verify stakeholder documentation
- Generate monthly compliance report

---

## Incident Type → Tier Mapping

| Incident Type | Typical Tier | Justification |
|---|---|---|
| Log level change | T0 | No behavior change |
| Test fix (<5 lines) | T1 | Low risk, isolated |
| Test fix (>5 lines) | T2 | Broader codebase impact |
| Security vulnerability | T2 | Requires approval + audit |
| New test type | T1 | Additive, non-breaking |
| Incident suppression threshold | T2 | Affects policy |
| Healing strategy for new incident type | T2 | Requires security review |
| Modify incident classification rules | T3 | Affects tier system itself |
| Disable quantum-hybrid | T3 | Governance-level capability change |
| Transfer fabric security policy | T3 | Multi-sandbox trust boundaries |

---

## Emergency Bypass (T0-T2 Only)

**Condition:** Critical incident affecting lanes + >2 hour MTTR without normal approval  
**Authorization:** @mbaetiong verbal/text authorization + documented decision-trace  
**Constraints:**  
- T3 changes CANNOT be bypassed (full stakeholder review required)
- Bypass requires post-incident review within 24 hours
- Rollback option must remain available for 48 hours post-execution

**Procedure:**
1. Lane owner calls emergency escalation to @mbaetiong
2. @mbaetiong issues verbal authorization + approval message
3. Lane owner executes with "EMERGENCY_BYPASS" flag in decision-trace
4. Auto-execute with full audit trail + timestamps
5. Schedule post-incident review within 24 hours

---

**Document Status:** ✅ Complete  
**Last Updated:** 2026-07-13T00:26Z  
**Next Review:** Upon Phase 1 gate completion (Week 3)
