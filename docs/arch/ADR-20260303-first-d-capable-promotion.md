# ADR-20260303: First D_CAPABLE Agent Promotion — `ci-testing-agent`
> Generated: 2026-06-22T02:25:00Z | Author: copilot-swe-agent[bot]
> Status: Accepted
> Related PRs: #3494

## 1. Context

The E→D Transition Readiness Gate (`e-to-d-transition-gate.yml`) has held
a 5/5 score since PR #3447 merged the Soft→GROUNDED infrastructure.
All prerequisite conditions for D_CAPABLE promotion have been met:

| Condition | Status |
|-----------|--------|
| C1: AGENT_REGISTRY.yaml schema-valid | ✅ |
| C2: CODEX_MANIFEST.json valid < 24h | ✅ |
| C3: SOFT policy count ≤ 2 (current: 2) | ✅ |
| C4: agent-handoff-gate.yml deployed | ✅ |
| C5: GROUNDED Tier-1 count ≥ 8 (current: 21) | ✅ |

The follow-up prompt for PR #3492 (`.codex/docs/FOLLOWUP_PROMPT_PR3492.md`)
identifies Priority 2 as: *First D_CAPABLE Promotion*.  This ADR documents
the criteria, candidate selection, and decision for that initial promotion.

## 2. D_CAPABLE Criteria

An agent qualifies for `autonomy_model: D_CAPABLE` when it satisfies **all** of:

| Criterion | Requirement |
|-----------|-------------|
| Enforcement tier | `GROUNDED` (CI-enforced, not advisory) |
| Maturity | `production` (not `beta` or `experimental`) |
| Handoff protocol | `structured` (machine-readable handoff format) |
| Has tests | `true` |
| Has docs | `true` |
| Activation frequency | Top-20 ranked (consolidation_priority: true) |
| Violation history | Zero enforcement violations in last 30 days |

These criteria are intentionally conservative for the inaugural promotion.
Future ADRs may relax maturity or frequency thresholds as the D_CAPABLE
operating model matures.

## 3. Candidate Evaluation

| Agent | Tier | Maturity | Handoff | Tests | Docs | Rank | Decision |
|-------|------|----------|---------|-------|------|------|----------|
| `ci-testing-agent` | GROUNDED | production | structured | ✅ | ✅ | 1 | **PROMOTE** |
| `workflow-ci-fixer` | GROUNDED | production | structured | ✅ | ✅ | 3 | Future |
| `doc-freshness-checker` | GROUNDED | production | structured | ✅ | ✅ | 14 | Future |
| `dependency-vulnerability-scanner` | GROUNDED | production | structured | ✅ | ✅ | 15 | Future |

`ci-testing-agent` is the clear first candidate: it holds activation rank 1
(most frequently invoked agent in the system), is the only agent with
`enforcement_tier: GROUNDED` AND `maturity: production` AND rank ≤ 3.

## 4. Decision

**Promote `ci-testing-agent` from `autonomy_model: E` to `autonomy_model: D_CAPABLE`.**

Change applied in `AGENT_REGISTRY.yaml` (line 157):
```yaml
# Before
autonomy_model: E

# After
autonomy_model: D_CAPABLE
```

The `enforcement_tier` remains `GROUNDED` and `handoff_protocol` remains
`structured` — no other fields change.

## 5. Decision Drivers

| Driver | Notes |
|--------|-------|
| Infrastructure readiness | E→D gate 5/5 ✅ — prerequisites fully met |
| Highest frequency agent | Rank 1 — most exposure, most CI validation coverage |
| GROUNDED enforcement | CI enforces its behaviour; violations block PRs |
| Structured handoff | Machine-verifiable inter-agent protocol |
| Reversibility | Single YAML edit to demote back to `E` if needed |

## 6. Considered Alternatives

| Alternative | Rejected Because |
|-------------|------------------|
| Promote all 8 GROUNDED agents at once | Too aggressive for first promotion; incremental trust preferred |
| Promote a beta-maturity agent | Violates D_CAPABLE criterion #2 (production maturity required) |
| Wait for owner manual approval at runtime | Gate 5/5 already constitutes system-level approval of the criteria |
| Promote `workflow-ci-fixer` (rank 3) instead | Rank 1 is less ambiguous first choice; `ci-testing-agent` has broadest CI coverage |

## 7. Consequences

### Positive
- First D_CAPABLE agent in the system — establishes the promotion pattern.
- `ci-testing-agent` may now execute CI diagnosis and fix actions within guardrails without advisory-only restriction.
- Sets the template for future D_CAPABLE promotions (see Section 2 criteria).
- Gate demotion annotations will flag any future D_CAPABLE agent lacking `structured` handoff.

### Negative
- `d_capable_agents` count in CODEX_MANIFEST.json increases from 0 to 1.
- `transition_active` flag becomes `true` — system enters D_CAPABLE operating mode.
- Any regression in D_CAPABLE behaviour requires tracking in AGENT_ACCOUNTABILITY_REPORT.md.

### Risks & Mitigations
- **Risk**: D_CAPABLE status allows autonomous execution that bypasses advisory review.
  **Mitigation**: `enforcement_tier: GROUNDED` means all actions are CI-gated; the
  `e-to-d-transition-gate.yml` demotion-annotation step catches any future compliance gap.
- **Risk**: Premature promotion before full D_CAPABLE semantics are implemented in orchestrator.
  **Mitigation**: `orchestrator_routing.py` already differentiates E vs D_CAPABLE routing;
  the promotion only changes the registry label, not the agent's code.
- **Risk**: Other agents promoted prematurely by following this precedent.
  **Mitigation**: This ADR documents explicit criteria; future promotions must reference these criteria.

## 8. Provenance & Compliance
- **Gate**: `e-to-d-transition-gate.yml` — score 5/5 at time of promotion
- **Follow-up**: `.codex/docs/FOLLOWUP_PROMPT_PR3492.md` — Priority 2
- **Registry version**: v1.9.0 → v1.9.1 (patch increment for D_CAPABLE field change)
- **Change log**: PR #3494 (this PR)
- **Next review**: Promote second D_CAPABLE agent after 2-sprint observation period
