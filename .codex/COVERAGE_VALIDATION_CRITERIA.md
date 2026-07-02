# Coverage Validation Criteria
## Baseline Stability & Regression Thresholds

**Baseline Locked:** 2026-07-02T02:22:00Z  
**Baseline Coverage:** 34.63%  
**Phase:** BASELINE_PHASE  

---

## 1. Baseline Stability Tolerance

### Overall Coverage Variance Band
- **Baseline:** 34.63%
- **Acceptable Range:** 33.13% - 36.13% (±1.5%)
- **Status Indicators:**
  - 🟢 **STABLE:** ±0.5% variance (34.13% - 35.13%)
  - 🟡 **ACCEPTABLE:** ±1.0-1.5% variance (33.63% - 35.63%, 32.63% - 36.63%)
  - 🔴 **REGRESSION:** >1.5% loss (< 33.13%)
  - 🔴 **ANOMALY:** >3% swing (>37.63% or <31.63%)

### Detection Rules
- **Per-PR Check:** Compare HEAD coverage vs. baseline snapshot
- **Per-Run Tracking:** Log every test run to historical NDJSON
- **Weekly Aggregation:** Average coverage by week, flag anomalies
- **Monthly Review:** Trend analysis with statistical significance

---

## 2. Regression Threshold Definitions

| Category | Threshold | Action | Escalation |
|----------|-----------|--------|-----------|
| **Module-Level Drop** | >5% loss on any module | Flag for review | unified-coverage-agent |
| **Test Count Regression** | <2,467 tests | Block PR merge | ci-failure-resolution-agent |
| **Tier 1 Regression** | <90% (security) | Escalate immediately | @mbaetiong |
| **Tier 2 Regression** | <85% (auth) | Block PR merge | unified-coverage-agent |
| **Tier 3 Regression** | <77% (infra) | Block PR merge | unified-coverage-agent |
| **Tier 4 Regression** | <62% (extended) | Warn + recommend fixes | unified-coverage-agent |
| **Coverage Drop >1.5%** | >1.5% overall | Block PR merge | ci-emergency-response-agent |
| **Coverage Drop >3%** | >3% overall | Escalate + hold merge | @mbaetiong |
| **Test Flakiness Increase** | Any flakiness detected | Trigger healer | autonomous-test-healer-agent |
| **Determinism Decrease** | <100% determinism | Investigate & fix | ci-testing-agent |

---

## 3. Quality Gate Requirements

### Stabilization Metrics (All Required at 100% / 0%)
1. **Test Pass Rate:** 100% (no failures)
2. **Test Flakiness:** 0% (no flaky tests)
3. **Test Determinism:** 100% (reproducible across runs)
4. **Test Isolation:** 100% (no cross-test dependencies)

### Enforcement
- **CI Gate:** Fail PR if any metric breaches
- **Reporting:** Include all 4 metrics in every validation report
- **Recovery:** Automated remediation via autonomous-test-healer-agent

---

## 4. Module-Level Stability Requirements

### Per-Module Minimum Coverage
- **Tier 1 (Security):** ≥90.0% (current: 92.6%)
- **Tier 2 (Auth):** ≥85.0% (current: 86.1%)
- **Tier 3 (Infrastructure):** ≥77.0% (current: 76.0%)
- **Tier 4 (Extended):** ≥62.0% (current: 61.0%)

### Coverage Loss Tolerance Per Module
- **Tier 1:** No loss allowed (maintain ≥90%)
- **Tier 2:** Max 1% loss (maintain ≥84%)
- **Tier 3:** Max 2% loss (maintain ≥75%)
- **Tier 4:** Max 3% loss (maintain ≥59%)

### Module Addition / Removal
- **New modules:** Must start with tests
- **Removed modules:** Document in changelog
- **Refactored modules:** Maintain original coverage baseline or improve

---

## 5. Test Count Requirements

### Minimum Test Count
- **Baseline Requirement:** ≥2,467 tests
- **Tolerance:** No decrease allowed
- **Increase:** Recommended every phase (target: +333 tests/phase)

### Test Distribution (Required Ratios)
- **Happy Path:** ≥65% of tests (≥1,604)
- **Edge Case:** ≥15% of tests (≥370)
- **Error Path:** ≥10% of tests (≥247)

### Validation
- Count tests on every run
- Flag if count decreases
- Report distribution to ensure balanced testing

---

## 6. PR Validation Checklist

Every PR must pass all these checks before merge:

- [ ] **Coverage Check:** 34.63% ±1.5% (33.13% - 36.13%)
- [ ] **Module Tiers:** All 4 tiers meet minimums (Tier 1 ≥90%, Tier 2 ≥85%, Tier 3 ≥77%, Tier 4 ≥62%)
- [ ] **Test Count:** ≥2,467 tests (no regression)
- [ ] **Quality Metrics:** 100% pass rate, 0% flakiness, 100% determinism, 100% isolation
- [ ] **Regression Detection:** No module loses >5% coverage
- [ ] **No Regressions:** Compare vs. baseline snapshot in `.codex/COVERAGE_BASELINE_34_63.json`
- [ ] **Module Changes:** Document any modules with >1% coverage change
- [ ] **Escalation:** If any threshold breached, assign to appropriate agent

---

## 7. CI Automation Gates

### Pre-Merge Gates (Blocking)
```
if (coverage < 33.13% OR coverage > 36.13%):
  BLOCK_MERGE("Coverage regression detected")
  
if (test_count < 2467):
  BLOCK_MERGE("Test count decreased")
  
if (any_tier_below_minimum):
  BLOCK_MERGE("Module tier coverage breached")
  
if (test_flakiness > 0 OR determinism < 100%):
  BLOCK_MERGE("Quality metric failure")
```

### Post-Merge Monitoring
```
if (coverage drops > 1.5% from baseline):
  POST_COMMENT("Coverage regression detected, monitoring")
  
if (coverage drops > 3% from baseline):
  ESCALATE_TO_AGENT(unified-coverage-agent)
  
if (flakiness detected):
  DELEGATE_TO_AGENT(autonomous-test-healer-agent)
```

---

## 8. Reporting & Transparency

### Automated Reports
- **Per-Run Report:** `.codex/coverage/BASELINE_TRACKING_REPORT.json`
- **PR Comment:** Traffic-light dashboard (🟢/🟡/🔴)
- **Weekly Digest:** `.codex/coverage/WEEKLY_COVERAGE_REPORT.md`
- **Historical Trend:** `.codex/coverage/BASELINE_HISTORY.ndjson`

### Report Contents
- Current coverage vs. baseline
- Variance percentage and status
- Module changes >1% coverage
- Quality metric results
- Test statistics
- Next recommended action

---

## 9. Escalation Matrix

| Issue | Severity | Agent | Action |
|-------|----------|-------|--------|
| Coverage drop 1-1.5% | Yellow | unified-coverage-agent | Review + recommend fix |
| Coverage drop 1.5-3% | Orange | ci-emergency-response-agent | Block PR, investigate |
| Coverage drop >3% | Red | @mbaetiong | Escalate immediately |
| Module tier breach | Red | unified-coverage-agent | Block PR, notify owner |
| Test count decrease | Red | ci-testing-agent | Block PR, restore tests |
| Quality metric breach | Red | autonomous-test-healer-agent | Block PR, auto-heal if possible |
| Flaky test detected | Yellow | autonomous-test-healer-agent | Create fix PR |
| Measurement accuracy issue | Red | ci-testing-agent | Re-run with diagnostics |

---

## 10. Success Criteria for Baseline Phase

All of the following must be true for 30+ consecutive days:

- ✅ Coverage stable at 34.63% ±1.5% (33.13% - 36.13%)
- ✅ All 4 quality metrics: 100% / 0% maintained
- ✅ Test count ≥2,467 (no regression)
- ✅ Zero regressions detected
- ✅ All module tiers meet minimums:
  - Tier 1: ≥90%
  - Tier 2: ≥85%
  - Tier 3: ≥77%
  - Tier 4: ≥62%
- ✅ All PR validation gates pass consistently
- ✅ Dashboard updated automatically on every run
- ✅ No false positives in escalation alerts
- ✅ Unified-coverage-agent operational and responsive
- ✅ Zero unplanned coverage dips or spikes

---

## 11. Phase Progression Gate

After 30+ days of baseline stability, Phase 1 (40% target) can begin with:

- ✅ Baseline stability validated
- ✅ Module remediation strategy documented
- ✅ Zero-coverage module prioritization complete (120 modules)
- ✅ Test generation plan ready (2,467 → 2,800+ tests)
- ✅ Phase 1 validation gates defined in `PHASE_VALIDATION_GATES.yaml`
- ✅ Agent delegation tested and working
- ✅ Weekly trend reports show no anomalies

---

## References

- **Baseline Snapshot:** `.codex/COVERAGE_BASELINE_34_63.json`
- **Phase Validation Gates:** `.codex/PHASE_VALIDATION_GATES.yaml` (created during Phase 1)
- **Monitoring System:** `.codex/coverage/BASELINE_TRACKING_REPORT.json`
- **Tier Progression:** `.codex/MODULE_TIER_PROGRESSION.md`
- **Zero-Coverage Remediation:** `.codex/ZERO_COVERAGE_REMEDIATION.md`
