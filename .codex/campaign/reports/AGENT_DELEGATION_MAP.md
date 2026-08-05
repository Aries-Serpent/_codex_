# Agent Delegation Map

**Campaign:** Multi-Lane Campaign Framework Execution  
**Repository:** `Aries-Serpent/_codex_`  
**Generated:** `2026-08-05T05:12:00Z`

---

## Mapping Rationale

The campaign framework defines 13 distinct agent roles. The repository already has 164 registered agents in `.github/agents/AGENT_REGISTRY.yaml`. Where an exact role does not exist, the mapping reuses the closest specialist and documents the gap. No new agents are created unless explicitly required by a downstream gate.

---

## Delegation Matrix

| Campaign role | Lane | Mapped agent(s) | Objective | Inputs | Allowed scope | Forbidden scope | Dependencies | Outputs | Validation | Rollback | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `determinism-baseline-agent` | A | `orchestrator-agent` (existing) + `src/orchestration/adapters/input_lock.py` | Generate deterministic input-lock and seed manifest for HEAD | Repo files, `pyproject.toml`, `uv.lock`, workflow dir, agent registry | `.codex/campaign/`, `src/orchestration/adapters/`, `tests/orchestration/` | No edits to production code or secrets | None | `input-lock.json`, `Lane_A_PASS_GATE.md` | `tests/orchestration/test_determinism_baseline.py` passes | Delete generated manifests and reset seed | Queued |
| `security-factory-orchestrator` | B | `unified-security-scanner` + `security-audit-agent` + `codeql-alert-resolution-agent` | Orchestrate S1–S7 pipeline and normalize findings | Security factory modules, CI scan outputs, SARIF/JSON | `src/security/factory/`, `.codex/security-analysis/`, scan configs | No suppression of active critical findings without evidence | Lane A PASS | Security stage matrix, `Lane_B_PASS_GATE.md` | All stages have I/O contracts; critical findings documented | Revert any config changes; re-run from input-lock | Queued |
| `incident-detection-agent` | C | `ci-failure-resolution-agent` + `test-failure-analyzer-agent` | Detect incidents and classify severity with evidence bundle | CI logs, test failures, decision traces | `src/orchestration/healing/incident_detection.py`, logs | No production mutation | Lane A PASS | `incident_report.json`, evidence bundle | Classification matches `.codex/SELF_HEALING_POLICY_TIERS.md` | Archive incident record; notify downstream lanes | Queued |
| `tier-routing-agent` | C | `policy_tier_engine.py` + `ci-failure-resolution-agent` | Route incidents to Tier 0–3 paths | Incident classification, policy tier rules | `src/orchestration/healing/policy_tier_engine.py` | No bypass of Tier 2/3 approval | Incident detection output | Tier decision record | Routing decision is deterministic and logged | Update decision trace with corrected tier | Queued |
| `self-healing-execution-agent` | C | `autonomous-test-healer-agent` + `ci-testing-agent` | Execute allowlisted Tier 0–1 remediations | Tier routing decision, incident evidence | Allowlisted files (tests, docs, non-critical configs) | No code/security/policy changes | Tier 0/1 routing | Fix commits, validation reports | Validation passes before and after fix | `git revert` of fix commit | Queued |
| `proposal-escalation-agent` | C | `ci-failure-resolution-agent` (proposal mode) | Generate Tier 2 proposals with impact and rollback analysis | Tier 2 routing decision, affected modules | Proposal documents only | No autonomous merge or production impact | Tier 2 routing | Tier 2 proposal markdown/JSON | 8-gate contract review | Withdraw proposal; update decision trace | Queued |
| `stakeholder-gate-agent` | C | `approval_router.py` + `@mbaetiong` review | Enforce Tier 3 human approval | Tier 3 proposal, evidence packet | Approval workflow and notifications | No execution until approval | Tier 3 routing | Approval decision record | Two stakeholder signatures per policy | Reject proposal; halt execution | Queued |
| `quantum-compliance-tuning-agent` | D | `quantum-compliance-tuning-agent` (existing) | Map decision domains and evaluate shadow-mode recommendations | `docs/api/reference/QUANTUM_COMPLIANCE_TUNING_AGENT_INTEGRATION_GUIDE.md`, shadow outputs | `src/orchestration/hybrid/decision_domains.py`, quantum subsystem | No production mutation | Lane B PASS | Decision-domain mapping report | Matches Phase 4.5 integration guide | Disable shadow mode; fallback to classical | Queued |
| `shadow-benchmark-agent` | D | `agent-orchestrator` (existing) + `src/orchestration/hybrid/shadow_mode.py` | Compare shadow execution against golden metrics | Baseline decisions, shadow recommendations, golden metrics | `src/orchestration/hybrid/shadow_mode.py`, metrics files | No mutation of classical path | Lane B PASS + quantum domain mapping | `Lane_D_PASS_GATE.md`, benchmark JSON | KPI comparisons reproducible within threshold | Stop shadow promotion; retain classical fallback | Queued |
| `agent-iq-scoring-gate` | E | `agent-iq-scoring-gate` (existing) | Score agent decisions on correctness, safety, reliability, latency, cost, explainability, policy adherence | Agent outputs, decision traces, validation results | Scoring config, agent registry metadata | No modification of agent behavior | Lane D PASS | `Agent IQ report` | Score meets configured minimum | Disallow promotion until score threshold met | Queued |
| `canary-promotion-agent` | E | Inferred from `canary_promotion.py` + `cohort_routing.py` + `sla_monitor.py` | Manage cohort selection, canary routing, and promotion decisions | Cohort classification, canary metrics, SLA thresholds | `src/orchestration/hybrid/canary_promotion.py`, `cohort_routing.py`, `sla_monitor.py` | No full rollout without gate PASS | Lane D PASS + agent IQ PASS | Canary promotion record | Cohort bounded; rollback tested | Roll back traffic allocation; revert to classical | Queued |
| `transfer-aware-scheduler` | K | `orchestrator-agent` + `branch-divergence-resolution-agent` + `LaneSchedulerV1` | Resolve cross-lane dependencies and schedule by latency/priority/risk | Dependency graph, lane manifests, gate states | `src/orchestration/scheduling/lane_scheduler_v1.py` | No bypass of upstream gates | All upstream gate outputs | `Lane_K_SCHEDULE.md`, scheduling decision trace | Deterministic ordering; downstream blocked on gate fail | Recompute schedule from last good checkpoint | Queued |
| `campaign-audit-agent` | All | `session-analysis-agent` + `documentation-quality-agent` (acting as audit maintainers) | Maintain evidence, manifests, decisions, checkpoints, and final reports | All lane outputs, decision traces, gate reports | `.codex/campaign/reports/`, `.codex/decision_traces/` | No production code changes | All lanes | Final campaign report, audit trail | All required artifacts present and validated | Roll back to previous checkpoint | Queued |

---

## Agent Gap Register

| Missing exact role | Lane | Closest existing agent | Proposed resolution |
|---|---|---|---|
| `determinism-baseline-agent` | A | `orchestrator-agent` | Reuse orchestrator-agent; invoke existing `input_lock.py` / `seed_control.py` |
| `security-factory-orchestrator` | B | `unified-security-scanner`, `security-audit-agent` | Reuse scanner/audit agents; no new agent needed |
| `incident-detection-agent` | C | `ci-failure-resolution-agent` | Reuse CI failure agent; invoke `incident_detection.py` |
| `tier-routing-agent` | C | `policy_tier_engine.py` | Use existing engine; document routing rules |
| `self-healing-execution-agent` | C | `autonomous-test-healer-agent` | Reuse test healer for Tier 0–1 fixes |
| `proposal-escalation-agent` | C | `ci-failure-resolution-agent` | Use in proposal-only mode (Tier 2) |
| `stakeholder-gate-agent` | C | `approval_router.py` + `@mbaetiong` | Existing approval router enforces human gate |
| `shadow-benchmark-agent` | D | `agent-orchestrator` | Reuse orchestrator-agent to drive `shadow_mode.py` |
| `canary-promotion-agent` | E | (no exact agent) | Use existing `canary_promotion.py` module; create agent promptset only if required by gate |
| `transfer-aware-scheduler` | K | `orchestrator-agent` + `branch-divergence-resolution-agent` | Use existing `LaneSchedulerV1` |
| `campaign-audit-agent` | All | `session-analysis-agent` | Reuse session analysis agent for evidence maintenance |

---

## Delegation Rules

1. **Reuse first.** All 13 roles are mapped to existing agents/modules before any new agent is created.
2. **No shadow execution.** No agent may mutate production state outside its allowed scope.
3. **Gate respect.** A lane agent cannot start until all upstream dependencies are `PASS`.
4. **Evidence required.** Every agent must emit at least one machine-readable artifact and one decision-trace entry.
5. **Tier discipline.** Tier 0/1 auto-execute; Tier 2 generates proposals; Tier 3 requires `@mbaetiong` approval.

---

## Evidence

- Agent registry inspected: `.github/agents/AGENT_REGISTRY.yaml`
- Lane implementation modules confirmed present under `src/orchestration/` and `src/security/factory/`
- Governance docs `.codex/MULTI_LANE_GOVERNANCE.md` and `.codex/SELF_HEALING_POLICY_TIERS.md` define tier rules and escalation chains
