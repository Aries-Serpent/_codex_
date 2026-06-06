# Gap 45: Architecture Decision Records (ADRs) — Evidence

**Gap:** 45 — Add Architecture Decision Records (ADRs)
**Status:** ✅ Implemented
**Date:** 2025-01-15
**Branch:** copilot/explore-codebase-and-create-plan

---

## Summary

Created `docs/adr/` with five Architecture Decision Records (including the
pre-existing ADR-0001 for distributed tracing) documenting the major
architectural decisions implemented across this session.

---

## Files Created / Modified

| File | Action | Size |
|------|--------|------|
| `docs/adr/README.md` | Updated | Adds index table with 4 new ADRs + status legend + contribution guide |
| `docs/adr/ADR-001-drift-monitoring-approach.md` | Created | ~5 KB |
| `docs/adr/ADR-002-resilience-pattern.md` | Created | ~5.5 KB |
| `docs/adr/ADR-003-continuous-learning-architecture.md` | Created | ~6 KB |
| `docs/adr/ADR-004-testing-strategy.md` | Created | ~6.8 KB |
| `workbench/evidence/gap45_adrs.md` | Created | This file |

---

## ADR Content Verification

### ADR-001: Use PSI + KL-Divergence for Data Drift, JSD for Model Drift

- **Status:** Accepted
- **Date:** 2025-01-15
- **Covers:** Gaps 17/18 (drift monitoring)
- **Key decisions:**
  - PSI for categorical/binned feature drift (threshold 0.2)
  - KL-divergence for continuous unbinned distributions
  - JSD (symmetric, bounded [0,1]) for model output probability vectors
  - `NoopModCounter` fallback for environments without `prometheus-client`
- **Alternatives documented:** KS test, Wasserstein, MMD, single-metric approach

### ADR-002: Three-Layer Resilience: Circuit Breaker + Retry + Graceful Degradation

- **Status:** Accepted
- **Date:** 2025-01-15
- **Covers:** Gaps 29/30/31 (resilience layer)
- **Key decisions:**
  - CircuitBreaker with CLOSED/OPEN/HALF-OPEN states at service boundary
  - RetryWithBackoff with exponential back-off + full jitter for individual calls
  - GracefulDegradation with typed fallbacks for feature groups
  - Composable: CB wraps service, retry wraps call, degradation wraps feature group
- **Alternatives documented:** timeout-only, bulkhead, retry-only, Hystrix

### ADR-003: Event-Driven Continuous Learning via Drift → Trigger → EvalGate → Promote

- **Status:** Accepted
- **Date:** 2025-01-15
- **Covers:** Gaps 36/38/39 (continuous learning, auto-retrain, feedback loop)
- **Key decisions:**
  - Four-stage pipeline: DriftMonitor → RetrainingTrigger → AutoRetrainPipeline+EvalGate → ModelPromoter
  - OODA feedback overlay: FeedbackLoop feeds production outcomes back into training data
  - `repository_dispatch` GitHub Actions event bridges monitoring to CI
  - EvalGate quality thresholds prevent regressions from reaching production
- **Alternatives documented:** time-based retraining, manual promotion only, online learning

### ADR-004: Multi-Layer Testing: Unit + Integration + Regression + Property + Fuzz + Chaos

- **Status:** Accepted
- **Date:** 2025-01-15
- **Covers:** Gap 45 context — formalises existing multi-layer test strategy
- **Key decisions:**
  - 6 distinct layers in `tests/<layer>/` directories
  - Hypothesis for property/fuzz; pytest for all layers
  - `mutmut` for mutation testing (suite quality)
  - `pytest-cov --cov-fail-under=80` on unit+integration layers
  - `@pytest.mark.flaky(reruns=3)` permitted exclusively for chaos tests
- **Alternatives documented:** flat test dir, BDD-only, integration-only, no chaos tests

---

## Format Compliance

All ADRs use the MADR (Markdown Any Decision Record) format with these required
sections, verified present in each file:

| Section | ADR-001 | ADR-002 | ADR-003 | ADR-004 |
|---------|---------|---------|---------|---------|
| Title (H1) | ✅ | ✅ | ✅ | ✅ |
| Status | ✅ | ✅ | ✅ | ✅ |
| Date | ✅ | ✅ | ✅ | ✅ |
| Context | ✅ | ✅ | ✅ | ✅ |
| Decision | ✅ | ✅ | ✅ | ✅ |
| Consequences | ✅ | ✅ | ✅ | ✅ |
| Alternatives Considered | ✅ | ✅ | ✅ | ✅ |

Word count per ADR (approximate):

| ADR | Words |
|-----|-------|
| ADR-001 | ~620 |
| ADR-002 | ~590 |
| ADR-003 | ~650 |
| ADR-004 | ~680 |

All four ADRs are within the 400–700 word target range.

---

## Done Criteria Checklist

- [x] `docs/adr/` directory exists with README.md and 4 new ADR files
- [x] All ADRs use consistent MADR format with all required sections
- [x] README.md index table lists all 5 ADRs (including pre-existing ADR-0001)
- [x] README.md includes status definitions and contribution guide
- [x] Evidence file at `workbench/evidence/gap45_adrs.md` (this file)
- [x] `workbench/gap_backlog_prioritized.md` gap 45 → `✅ Implemented`
