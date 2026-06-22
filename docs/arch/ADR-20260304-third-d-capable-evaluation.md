# ADR-20260304-third-d-capable-evaluation

**Last Updated:** 2026-06-22

## Context

**Date:** 2026-03-04
**PR:** #3495
**Session:** COGNITIVE_BRAIN_SESSION_NUMBER 112
**Status:** SUPERSEDED — third promotion **COMPLETE** (see ADR-20260304-rust-error-validator-d-capable-promotion.md)

This ADR records the evaluation of candidates for the **third D_CAPABLE agent** promotion,
following the clean 2-sprint observation window for `workflow-ci-fixer` (second D_CAPABLE,
promoted PR #3494 W-104).

Current D_CAPABLE roster:
| Agent | Rank | Promoted |
|-------|------|---------|
| `ci-testing-agent` | 1 | PR #3494 W-096 |
| `workflow-ci-fixer` | 13 | PR #3494 W-104 |

---

## Criteria (from ADR-20260303-first-d-capable-promotion)

All criteria must be met:

| # | Criterion | Requirement |
|---|-----------|-------------|
| C1 | `enforcement_tier` | `GROUNDED` |
| C2 | `handoff_protocol` | `structured` |
| C3 | `accepts_handoff_from` | Non-empty list |
| C4 | `violations_30d` | `0` (explicitly set) |
| C5 | `has_tests` | `true` |
| C6 | `has_docs` | `true` |
| C7 | `maturity` | `production` |
| C8 | `activation_frequency_rank` | Top-20 |

---

## Candidates Evaluated

### Primary Candidate: `ci-emergency-response-agent`

**Result: REJECTED** — fails 3 of 8 criteria.

| Criterion | Required | Actual | Pass? |
|-----------|----------|--------|-------|
| C1 enforcement_tier | GROUNDED | **PARTIAL** | ❌ |
| C2 handoff_protocol | structured | **none** | ❌ |
| C3 accepts_handoff_from | non-empty | **[]** | ❌ |
| C4 violations_30d | 0 | NOT SET | ❌ |
| C5 has_tests | true | NOT SET | — |
| C6 has_docs | NOT SET | NOT SET | — |
| C7 maturity | production | production | ✅ |
| C8 rank | ≤ 20 | NOT SET | — |

**Rationale for rejection:** `ci-emergency-response-agent` has `handoff_protocol: none` and
`enforcement_tier: PARTIAL`. These are foundational D_CAPABLE requirements — an agent
operating at D_CAPABLE autonomy must be in GROUNDED tier (safety gate) and must support
structured handoffs (auditability gate). Promoting a PARTIAL-tier agent with no handoff
protocol would undermine the safety model established in PR #3494.

---

### Next-Best Candidate: `rust-error-validator`

**Result: DEFERRED** — fails 2 of 8 criteria.

| Criterion | Required | Actual | Pass? |
|-----------|----------|--------|-------|
| C1 enforcement_tier | GROUNDED | GROUNDED | ✅ |
| C2 handoff_protocol | structured | structured | ✅ |
| C3 accepts_handoff_from | non-empty | `[orchestrator, agent-orchestrator]` | ✅ |
| C4 violations_30d | 0 | **NOT SET** | ❌ |
| C5 has_tests | true | true | ✅ |
| C6 has_docs | true | true | ✅ |
| C7 maturity | production | **beta** | ❌ |
| C8 rank | ≤ 20 | 20 | ✅ |

**Gaps requiring resolution:**
1. **C7 maturity `beta` → `production`**: Requires owner sign-off that the agent has
   demonstrated stable behavior in production workloads with no critical failures.
2. **C4 `violations_30d` unset**: The field must be explicitly set to `0` after observing
   the agent for a 30-day window with no GROUNDED-tier violations.

**Recommendation:** `rust-error-validator` is the **designated third D_CAPABLE candidate**
once both gaps are resolved. No other GROUNDED-tier agent with structured handoff currently
exists in the registry.

---

### Remaining GROUNDED Agents (No Viable Rank)

| Agent | Rank | Fails | Notes |
|-------|------|-------|-------|
| `owner-approval-guard` | NOT SET | C4 unset, C5 unset, C8 unset | Production maturity; good handoff |
| `workflow-health-monitor` | NOT SET | C4 unset, C5 unset, C8 unset | Production maturity; good handoff |
| `workflow-compliance-guardian` | NOT SET | C4 unset, C5 `false`, C8 unset | Production maturity; no tests |
| `test-pattern-guardian` | NOT SET | C4 unset, C5 `false`, C8 unset | Production maturity; no tests |

None of these are viable at this time due to missing `activation_frequency_rank` (C8)
and/or missing `violations_30d` tracking (C4).

---

## Decision

**Third D_CAPABLE promotion is DEFERRED.**

`rust-error-validator` is designated as the next candidate. Promotion proceeds when:

1. `rust-error-validator` `maturity` field updated to `production` (requires @mbaetiong sign-off)
2. `rust-error-validator` `violations_30d: 0` explicitly set after 30-day observation window
3. A new ADR is created documenting the evaluation at that time
4. `AGENT_REGISTRY.yaml` updated (v1.9.3) with the promotion
5. `CODEX_MANIFEST.json` regenerated

---

## Alternatives Considered

**Relax C7 (maturity) to allow `beta`:** Rejected. The maturity field is a signal of
production-readiness and stability. Promoting a beta agent to D_CAPABLE autonomy before
it is production-stable creates operational risk. The existing two D_CAPABLE agents are
both `maturity: production`.

**Add `violations_30d: 0` to `rust-error-validator` now:** Not done in this PR. The field
should only be set after a genuine 30-day observation window, not pre-emptively. Setting
it without observation would undermine the integrity of the safety gate.

---

## Next Steps

| Owner | Action | Timeline |
|-------|--------|----------|
| @mbaetiong | Validate `rust-error-validator` operational stability | Next 2 sprints |
| @mbaetiong | Update `maturity: production` when stability confirmed | Sprint +1 |
| copilot-swe-agent | Monitor `violations_30d` for `rust-error-validator` | Ongoing |
| copilot-swe-agent | Create promotion ADR when both gaps resolved | Sprint +2 |

---

*Created: 2026-03-04 | PR #3495 | Session 112 | Author: copilot-swe-agent[bot]*
