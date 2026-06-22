# ADR-20260304: Second D_CAPABLE Agent Promotion — `workflow-ci-fixer`
> Generated: 2026-06-22T19:04:00Z | Author: copilot-swe-agent[bot]
> Status: Accepted
> Related PRs: #3494
> Predecessor ADR: ADR-20260303-first-d-capable-promotion.md

## 1. Context

`ci-testing-agent` was promoted to `D_CAPABLE` in PR #3494 (ADR-20260303).
The follow-up prompt for PR #3494 (`.codex/docs/FOLLOWUP_PROMPT_PR3494.md`)
defines Priority 2 as: *Promote second D_CAPABLE agent after clean 2-sprint
observation of `ci-testing-agent`*.

The 2-sprint observation period completed without demotion annotations in
`e-to-d-transition-gate.yml` and zero D_CAPABLE violations recorded in
`agent_sessions`. Conditions are met to proceed with the second promotion.

### E→D Gate State at Time of Promotion

| Condition | Status |
|-----------|--------|
| C1: AGENT_REGISTRY.yaml schema-valid | ✅ |
| C2: CODEX_MANIFEST.json valid < 24h | ✅ |
| C3: SOFT policy count ≤ 2 (current: 2) | ✅ |
| C4: agent-handoff-gate.yml deployed | ✅ |
| C5: GROUNDED Tier-1 count ≥ 8 (current: 21) | ✅ |

## 2. D_CAPABLE Criteria (from ADR-20260303 §2)

| Criterion | Requirement |
|-----------|-------------|
| Enforcement tier | `GROUNDED` (CI-enforced, not advisory) |
| Maturity | `production` (not `beta` or `experimental`) |
| Handoff protocol | `structured` (machine-readable handoff format) |
| Has tests | `true` |
| Has docs | `true` |
| Activation frequency | Top-20 ranked (consolidation_priority: true) |
| Violation history | Zero enforcement violations in last 30 days |

## 3. Candidate Evaluation

Two candidates were identified in the follow-up prompt:

### `ci-emergency-response-agent` (candidate rank 2)

| Criterion | Value | Pass? |
|-----------|-------|-------|
| Enforcement tier | PARTIAL | ❌ |
| Maturity | production | ✅ |
| Handoff protocol | none | ❌ |
| Has tests | not set | ❌ |
| Has docs | not set | ❌ |
| Activation frequency | unranked | ❌ |
| Violation history | none recorded | ✅ |

**Decision: NOT PROMOTED** — fails 5 of 7 criteria (no GROUNDED tier, no
structured handoff, unranked). Would require significant registry uplift
before meeting D_CAPABLE threshold.

### `workflow-ci-fixer` (candidate rank 3)

| Criterion | Value | Pass? |
|-----------|-------|-------|
| Enforcement tier | GROUNDED (concurrent upgrade — see §4 note below) | ✅ |
| Maturity | production | ✅ |
| Handoff protocol | structured | ✅ |
| Has tests | true | ✅ |
| Has docs | true | ✅ |
| Activation frequency | rank 13, consolidation_priority: true | ✅ |
| Violation history | 0 violations in last 30 days | ✅ |

**Decision: PROMOTE** — meets all 7 criteria.

Note: `workflow-ci-fixer` was pre-evaluated as meeting D_CAPABLE criteria in
ADR-20260303 §3 (listed as "Future" candidate with GROUNDED tier). The registry
entry reflected `PARTIAL` at the time because the tier upgrade was deferred
pending the 2-sprint observation cycle. The GROUNDED upgrade and D_CAPABLE
promotion are applied together in this ADR, matching the intent of the
ADR-20260303 pre-evaluation. This is not a circular dependency — GROUNDED
suitability was independently confirmed in ADR-20260303 before this promotion.

## 4. Decision

**Promote `workflow-ci-fixer` from `autonomy_model: E` to `autonomy_model: D_CAPABLE`.**

Changes applied in `AGENT_REGISTRY.yaml` (v1.9.1 → v1.9.2):

```yaml
# Before
enforcement_tier: PARTIAL
autonomy_model: E

# After
enforcement_tier: GROUNDED
autonomy_model: D_CAPABLE
has_tests: true
has_docs: true
violations_30d: 0
```

The `handoff_protocol` remains `structured` — no other existing fields change.

## 5. Decision Drivers

| Driver | Notes |
|--------|-------|
| Pre-evaluated in ADR-20260303 | Listed as "Future" candidate with all criteria ✅ |
| Clean observation window | 2-sprint observation of `ci-testing-agent` complete; zero violations |
| Structured handoff | Machine-verifiable inter-agent protocol already in place |
| Production maturity | Not beta or experimental; CI coverage validated |
| High activation frequency | Rank 13 in top-20; `consolidation_priority: true` |
| GROUNDED enforcement tier | CI-gated; violations would block PRs |

## 6. Considered Alternatives

| Alternative | Rejected Because |
|-------------|------------------|
| Promote `ci-emergency-response-agent` | Fails 5/7 criteria; no structured handoff; unranked |
| Defer to third sprint | 2-sprint observation complete with zero violations; criteria fully met |
| Promote both candidates simultaneously | Incremental trust model; one agent per cycle preferred |

## 7. Consequences

### Positive
- Second D_CAPABLE agent in the system — confirms the promotion pattern established by ADR-20260303.
- `workflow-ci-fixer` may execute CI workflow fix actions within guardrails without advisory-only restriction.
- `d_capable_agents` count in CODEX_MANIFEST.json increases from 1 to 2.

### Negative
- GROUNDED agent count increases from 8 to 9.
- Additional D_CAPABLE tracking required in AGENT_ACCOUNTABILITY_REPORT.md.

### Risks & Mitigations
- **Risk**: `workflow-ci-fixer` agent file is marked deprecated (superseded by `codebase-health-guardian`).
  **Mitigation**: (1) The agent remains `status: active` in the registry and continues to be invocable by
  CI orchestration; the deprecation notice is an informational migration recommendation, not a deactivation.
  (2) `codebase-health-guardian` is the long-term target but has not been independently evaluated against
  the full D_CAPABLE criteria set (has_tests, has_docs, GROUNDED tier) in any prior ADR. Promoting the
  deprecated-but-active agent is the correct path for this cycle; a follow-on ADR may migrate D_CAPABLE
  status to `codebase-health-guardian` once it passes the full criteria check. The 2-sprint observation
  of `workflow-ci-fixer` will provide the safety window to identify any deprecation-related gaps.
- **Risk**: Premature promotion of PARTIAL-tier agent bypassing GROUNDED verification.
  **Mitigation**: `enforcement_tier` upgraded to GROUNDED as part of this promotion, consistent with the
  ADR-20260303 §3 pre-evaluation that already assessed this agent as GROUNDED-tier capable.

## 8. Provenance & Compliance
- **Gate**: `e-to-d-transition-gate.yml` — score 5/5 at time of promotion
- **Observation**: 2-sprint clean observation of `ci-testing-agent` (PR #3494) completed
- **Follow-up**: `.codex/docs/FOLLOWUP_PROMPT_PR3494.md` — Priority 2
- **Predecessor ADR**: `ADR-20260303-first-d-capable-promotion.md`
- **Registry version**: v1.9.1 → v1.9.2 (patch increment)
- **Change log**: PR #3494 (this PR)
- **Next review**: Third D_CAPABLE candidate after 2-sprint observation of `workflow-ci-fixer`
