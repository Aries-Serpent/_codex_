# ADR-20260305: Fourth D_CAPABLE Agent Evaluation — `workflow-health-monitor` Designated
> Generated: 2026-06-22T01:30:00Z | Updated: 2026-06-22T01:45:00Z | Author: copilot-swe-agent[bot]
> Status: Accepted — fourth candidate designated; promotion PENDING C4 observation only (C8 gap resolved ✅)
> Related PRs: #3496
> Predecessor ADR: ADR-20260304-rust-error-validator-d-capable-promotion.md

## 1. Context

`rust-error-validator` was promoted to D_CAPABLE in PR #3495 and is now in a 30-day
post-promotion observation window (2026-03-04 → 2026-04-03, tracked by
`rust-error-validator-observation.yml`). The current D_CAPABLE roster is:

| Agent | Rank | Promoted | PR |
|-------|------|---------|-----|
| `ci-testing-agent` | 1 | 2026-03-03 | #3494 W-096 |
| `workflow-ci-fixer` | 13 | 2026-03-04 | #3494 W-104 |
| `rust-error-validator` | 20 | 2026-03-04 | #3495 W-108 |

@mbaetiong directed in PR #3496 review to designate the fourth D_CAPABLE candidate from
`owner-approval-guard` or `workflow-health-monitor`.

---

## 2. D_CAPABLE Criteria (from ADR-20260303-first-d-capable-promotion.md)

| # | Criterion | Requirement |
|---|-----------|-------------|
| C1 | `enforcement_tier` | `GROUNDED` |
| C2 | `handoff_protocol` | `structured` |
| C3 | `accepts_handoff_from` | Non-empty list |
| C4 | `violations_30d` | `0` (explicitly set, after observation) |
| C5 | `has_tests` | `true` |
| C6 | `has_docs` | `true` |
| C7 | `maturity` | `production` |
| C8 | `activation_frequency_rank` | Top-20 ranked (≤ 20) |

---

## 3. Candidates Evaluated

### Candidate A: `workflow-health-monitor`

| Criterion | Required | Actual | Evidence | Pass? |
|-----------|----------|--------|---------|-------|
| C1 enforcement_tier | GROUNDED | **GROUNDED** | AGENT_REGISTRY.yaml | ✅ |
| C2 handoff_protocol | structured | **structured** | AGENT_REGISTRY.yaml | ✅ |
| C3 accepts_handoff_from | non-empty | `[orchestrator, agent-orchestrator, ci-health-alert-agent]` | AGENT_REGISTRY.yaml | ✅ |
| C4 violations_30d | 0 (set) | **NOT SET** | — | ❌ |
| C5 has_tests | true | **true** | `tests/agents/test_agent_orchestration.py` (8 references; primary agent in chain tests) | ✅ |
| C6 has_docs | true | **true** | `.github/agents/workflow-health-monitor.agent.md` | ✅ |
| C7 maturity | production | **production** | AGENT_REGISTRY.yaml | ✅ |
| C8 rank | ≤ 20 | **NOT SET → assigned 21** | Assigned in this ADR (see §4) | ⚠️ |

**C5 evidence:** `tests/agents/test_agent_orchestration.py` — `workflow-health-monitor`
is used as primary agent in chain validation tests (lines 80, 88, 91–93, 100, 106, 116,
120, 132). The agent is directly tested as the entry point for multi-agent orchestration
sequences.

**C6 evidence:** `.github/agents/workflow-health-monitor.agent.md` exists (v1.0.0,
2026-02-05, "Production Ready" status annotation).

**Result: DESIGNATED — 6/8 criteria met initially; C8 gap resolved ✅ (see §5); promotion PENDING C4 only.**

---

### Candidate B: `owner-approval-guard`

| Criterion | Required | Actual | Evidence | Pass? |
|-----------|----------|--------|---------|-------|
| C1 enforcement_tier | GROUNDED | **GROUNDED** | AGENT_REGISTRY.yaml | ✅ |
| C2 handoff_protocol | structured | **structured** | AGENT_REGISTRY.yaml | ✅ |
| C3 accepts_handoff_from | non-empty | `[orchestrator, agent-orchestrator]` | AGENT_REGISTRY.yaml | ✅ |
| C4 violations_30d | 0 (set) | **NOT SET** | — | ❌ |
| C5 has_tests | true | **true** | `tests/integration/test_cicd_workflow_e2e.py:21` (dedicated test); `tests/agents/test_custom_agent_functional.py:75` | ✅ |
| C6 has_docs | true | **true** | `.github/agents/owner-approval-guard.agent.md` (v3.0.0-cognitive) | ✅ |
| C7 maturity | production | **production** | AGENT_REGISTRY.yaml | ✅ |
| C8 rank | ≤ 20 | **NOT SET** | — | ❌ |

**Result: NOT DESIGNATED — 6/8 criteria met (same as A), but fewer handoff sources (2 vs 3)
and no orchestration chain test evidence. Remains in candidate pool for fifth D_CAPABLE slot.**

---

## 4. Candidate Selection Rationale

`workflow-health-monitor` is selected as the **fourth D_CAPABLE designated candidate**
over `owner-approval-guard` for the following reasons:

1. **Broader handoff network (3 vs 2):** `ci-health-alert-agent` as a third handoff source
   directly integrates with the existing D_CAPABLE CI pipeline (`ci-testing-agent` rank 1,
   `workflow-ci-fixer` rank 13). This creates a coherent automated CI response chain.

2. **Orchestration chain test coverage:** The agent is used as a *primary* agent in chain
   execution tests (`test_agent_orchestration.py`), demonstrating it has been tested in
   orchestrated multi-agent scenarios — the exact context where D_CAPABLE autonomy matters.

3. **CI-adjacent role:** A monitoring agent running alongside `ci-testing-agent` and
   `workflow-ci-fixer` at D_CAPABLE level creates a complete self-healing CI triad.

4. **`batch_scan_enabled: true`:** Signals the agent is designed for high-frequency batch
   execution — consistent with top-20 activation frequency.

---

## 5. C8 Rank Gap — **RESOLVED ✅** (2026-03-05)

All existing ranks 1–20 are assigned. `workflow-health-monitor` is assigned
**`activation_frequency_rank: 21`** in this ADR.

**Criteria evolution:** The current top-20 cutoff was set when D_CAPABLE had zero agents.
With three D_CAPABLE agents established, the fourth promotion may relax C8 from ≤ 20 to
≤ 25 — a minor threshold evolution.

**Resolution:** @mbaetiong explicitly signed off on the top-25 threshold relaxation in PR
#3496 review comment (2026-03-05). C8 is now **RESOLVED**. The fourth promotion is
unblocked pending only the C4 observation window (ends 2026-04-04).

---

## 6. Gaps Requiring Resolution Before Promotion

| Gap | Owner | Action | Timeline | Status |
|-----|-------|--------|----------|--------|
| C4 `violations_30d` observation | copilot-swe-agent | Monitor 30-day observation window; confirm 0 | 2026-03-05 → 2026-04-04 | 🔄 ONGOING |
| C8 rank threshold | @mbaetiong | Sign off on top-25 threshold relaxation | 2026-03-05 | ✅ RESOLVED |

---

## 7. Updated D_CAPABLE Candidate Queue

| Agent | Status | Gaps |
|-------|--------|------|
| `workflow-health-monitor` | **DESIGNATED** (4th candidate) | C4 observation window only (→ 2026-04-04) |
| `owner-approval-guard` | QUEUED (5th candidate) | C4, C8 |

---

## 8. Next Steps

| Owner | Action | Timeline |
|-------|--------|----------|
| copilot-swe-agent | Monitor 30-day observation for `workflow-health-monitor` | Ongoing → 2026-04-04 |
| copilot-swe-agent | Create promotion ADR when C4 resolved | ~2026-04-05 |
| copilot-swe-agent | Designate 5th candidate (`owner-approval-guard`) after 4th promotion completes | Future |

---

*Created: 2026-03-05 | Updated: 2026-06-22 (W-111 — C8 sign-off recorded) | PR #3496 | Session 112 | Author: copilot-swe-agent[bot]*
