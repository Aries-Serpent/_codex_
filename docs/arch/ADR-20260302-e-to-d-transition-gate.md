# ADR-20260302: E→D Transition Finite State Machine Gate
> Generated: 2026-06-22T07:00:00Z | Author: copilot-swe-agent[bot]
> Status: Accepted
> Related PRs: #3447

## 1. Context

The agentic system defines two autonomy models:

- **E_ONLY** (advisory): Agents propose actions for human review.
- **D_CAPABLE** (autonomous): Agents may execute actions within guardrails.

Premature promotion to D_CAPABLE without verifying that the enforcement
infrastructure is in place could allow unvalidated autonomous actions.
The Soft→GROUNDED plan requires a formal gate that blocks E→D transitions
until all prerequisite conditions are satisfied.

## 2. Problem Statement

Design a CI-enforced gate that prevents any agent from being assigned
`autonomy_model: D_CAPABLE` in AGENT_REGISTRY.yaml until a set of
infrastructure conditions are met.

## 3. Decision

Implement a 5-condition Finite State Machine (FSM) gate in
`.github/workflows/e-to-d-transition-gate.yml`:

| Condition | Check | Threshold |
|-----------|-------|-----------|
| C1 | AGENT_REGISTRY.yaml passes JSON Schema validation | Schema valid |
| C2 | ≥ 2 Tier-1 GROUNDED CI gates active | ≥ 2 |
| C3 | ≤ 2 agents remain at `enforcement_tier: SOFT` | ≤ 2 |
| C4 | CODEX_MANIFEST.json integrity hash matches | SHA-256 match |
| C5 | ≥ 8 agents at `enforcement_tier: GROUNDED` | ≥ 8 |

The gate evaluates all 5 conditions and reports a score (0–5).
Transition is only permitted when score = 5/5.

Current state:
- Score: 5/5 ✅ (all conditions satisfied)
- `d_capable_agents`: 0 (no agents promoted yet)
- `transition_active`: false (gate is ready but no D_CAPABLE assignments made)

The workflow runs as a Tier-2 canary (`core.warning()`) during the
observation period, to be promoted to Tier-1 (`core.setFailed()`) after
confirming zero false positives over 2 sprints.

## 4. Decision Drivers

| Driver | Notes |
|--------|-------|
| Safety-first autonomy | No D_CAPABLE without verified infrastructure |
| Incremental trust | 5 conditions build progressively on each other |
| Auditability | Gate score logged in workflow annotations |
| Reversibility | Demoting an agent back to E_ONLY is a single YAML edit |

## 5. Considered Alternatives

| Alternative | Rejected Because |
|-------------|------------------|
| Manual admin approval only | No CI enforcement; prone to human error |
| Single boolean flag | Too coarse; cannot verify infrastructure readiness |
| 3-condition gate (C1, C2, C4 only) | Skips enforcement tier distribution checks (C3, C5) |
| Runtime gate (check at agent execution time) | Too late; should prevent invalid config from merging |
| Branch protection rule | Cannot evaluate custom YAML schema conditions |

## 6. Consequences

### Positive
- Impossible to merge a D_CAPABLE agent without 5/5 infrastructure conditions met.
- Gate score provides clear, actionable feedback (e.g., "3/5 — C3 and C5 not met").
- Progressive trust model: conditions can be tightened over time.
- Compatible with future conditions (C6, C7, etc.) for higher autonomy levels.

### Negative
- Adds CI execution time (~30 seconds per PR touching the registry).
- Requires maintaining threshold values as the agent population grows.
- Tier-2 canary mode means violations are warnings only until promoted.

### Risks & Mitigations
- **Risk**: Threshold values become stale as agent count grows.
  **Mitigation**: Thresholds are defined as constants in the workflow script;
  review during quarterly governance audits.
- **Risk**: False positive blocks after Tier-1 promotion.
  **Mitigation**: 2-sprint observation period before promotion; rollback to
  Tier-2 documented in the workflow header.
- **Risk**: Gate bypassed by editing workflow file directly.
  **Mitigation**: `.github/CODEOWNERS` requires `@Aries-Serpent/owners` review
  for all governance workflow changes.

## 7. Provenance & Compliance
- **Workflow**: `.github/workflows/e-to-d-transition-gate.yml` (Tier-2 canary)
- **Conditions**: C1–C5 defined in `orchestrator_routing.py` and gate script
- **Current score**: 5/5 ✅
- **Promotion path**: Tier-1 after 2-sprint observation (TASK 4 in follow-up)
- **Change log**: PR #3447 merged to main
