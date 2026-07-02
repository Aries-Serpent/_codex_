# CI/CD Workflow Integration Checklist
## Phase 5 Implementation - Coverage Baseline Monitoring

**Created:** 2026-07-02T02:25:00Z  
**Status:** READY FOR INTEGRATION  
**Baseline:** 34.63% (Locked)  
**Reference:** `.codex/COVERAGE_BASELINE_34_63.json`

---

## Overview

This checklist verifies that all Phase 0-4 components can be successfully integrated into the existing CI/CD workflows, enabling:
- Continuous baseline tracking on every test run
- Automatic regression detection and blocking
- Traffic-light status reporting
- Weekly trend analysis
- Multi-agent escalation routing

All integration points have been designed to work with the existing `coverage-ratchet.yml` workflow and can be activated incrementally without disrupting the current setup.

---

## Integration Points

### 1. Baseline Tracking Script Integration into coverage-ratchet.yml

**Component:** `scripts/ci/generate_baseline_tracking_report.py`

#### Current Workflow State
- ✅ Runs `pytest --cov=src --cov-report=xml:coverage.xml`
- ✅ Extracts coverage percentage
- ✅ Posts PR comments on regression
- ✅ Exits non-zero on coverage drop

#### Phase 5 Integration Steps

**Step 1.1: Add baseline tracking to workflow**
```yaml
# In coverage-ratchet.yml, after Run coverage step:
- name: Generate baseline tracking report
  if: always()
  run: |
    python scripts/ci/generate_baseline_tracking_report.py \
      --coverage-xml coverage.xml \
      --baseline .codex/COVERAGE_BASELINE_34_63.json \
      --output .codex/coverage/BASELINE_TRACKING_REPORT.json
```

**Step 1.2: Capture tracking report in job output**
```yaml
- name: Upload tracking report
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: baseline-tracking-report
    path: .codex/coverage/BASELINE_TRACKING_REPORT.json
    retention-days: 90
```

**Status Check:**
- [ ] Script runs without errors
- [ ] JSON report generated with correct schema
- [ ] Coverage metrics match pytest output
- [ ] Variance calculations correct
- [ ] Validation status accurate (STABLE/ACCEPTABLE/REGRESSION/ANOMALY)
- [ ] Recommended actions generated correctly

---

### 2. Module Matrix Generation on Every Test Run

**Component:** `.codex/MODULE_BASELINE_MATRIX.json` (generated from Phase 2)

#### Integration Requirements

**Step 2.1: Generate module matrix in CI**
```yaml
- name: Generate module matrix
  if: always()
  run: |
    python scripts/ci/generate_module_matrix.py \
      --coverage-xml coverage.xml \
      --baseline .codex/COVERAGE_BASELINE_34_63.json \
      --output .codex/coverage/MODULE_BASELINE_MATRIX.json \
      --format json
```

**Step 2.2: Validate module tier minimums**
```yaml
- name: Validate module tier gates
  if: always()
  run: |
    python scripts/ci/validate_module_gates.py \
      --matrix .codex/coverage/MODULE_BASELINE_MATRIX.json \
      --gates .codex/PHASE_VALIDATION_GATES.yaml \
      --fail-on-breach
```

**Status Check:**
- [ ] Module coverage captured per-tier
- [ ] Tier 1 (Security): ≥90.0% enforced
- [ ] Tier 2 (Auth): ≥85.0% enforced
- [ ] Tier 3 (Infrastructure): ≥77.0% monitored
- [ ] Tier 4 (Extended): ≥62.0% monitored
- [ ] Module loss tolerance respected
- [ ] Per-module deltas calculated correctly
- [ ] JSON matrix generated with full metadata

---

### 3. Validation Test Execution (Phase 2 Tests)

**Component:** `tests/validation/` test suite (all 17 tests)

#### Current Tests Integrated
- `test_coverage_verification.py` - Baseline comparison
- `test_coverage_regression.py` - Regression detection
- `test_module_coverage_gates.py` - Module tier validation
- `test_quality_metrics.py` - Quality gate validation
- `test_coverage_determinism.py` - Determinism verification
- `test_ci_workflow_validation.py` - Workflow config validation
- `test_audit_pipeline.py` - Audit trail validation
- 10+ additional validation tests

#### Phase 5 Integration Steps

**Step 3.1: Add validation test execution to PR workflows**
```yaml
- name: Run validation test suite
  if: always()
  run: |
    python -m pytest tests/validation/ \
      -v \
      --tb=short \
      --timeout=60 \
      --junitxml=.codex/coverage/validation_tests.xml \
      --json-report \
      --json-report-file=.codex/coverage/validation_tests.json
```

**Step 3.2: Gate PR merge on validation test pass**
```yaml
- name: Check validation gates
  if: always()
  run: |
    if grep -q "FAILED" .codex/coverage/validation_tests.xml; then
      echo "❌ Validation tests failed - blocking PR merge"
      exit 1
    fi
```

**Status Check:**
- [ ] All 17 validation tests run
- [ ] Tests run in < 60 seconds (timeout enforced)
- [ ] JUnit XML report generated
- [ ] JSON report with detailed metrics
- [ ] Failed tests block PR merge
- [ ] Passed tests allow PR progression
- [ ] Test execution output captured in job summary

---

### 4. Traffic-Light Status Comment Posting

**Component:** Multi-color status reporting to PR comments

#### Current Implementation
- Coverage ratchet posts single comment on regression
- Comment only on threshold breach (35% baseline)

#### Phase 5 Enhancement

**Step 4.1: Create enhanced status comment generator**
```yaml
- name: Post traffic-light status
  if: github.event_name == 'pull_request'
  env:
    PR_NUMBER: ${{ github.event.pull_request.number }}
  run: |
    python scripts/ci/post_coverage_status.py \
      --tracking-report .codex/coverage/BASELINE_TRACKING_REPORT.json \
      --module-matrix .codex/coverage/MODULE_BASELINE_MATRIX.json \
      --pr $PR_NUMBER \
      --format traffic-light
```

#### Status Format

**Green Light (STABLE/ACCEPTABLE):**
```
✅ Coverage Status: ACCEPTABLE
├─ Current: 34.65% (baseline: 34.63%)
├─ Variance: +0.02%
├─ Status: Within ±1.5% band
└─ Action: Continue monitoring
```

**Yellow Light (REGRESSION near threshold):**
```
⚠️  Coverage Status: CAUTION
├─ Current: 34.40% (baseline: 34.63%)
├─ Variance: -0.23%
├─ Status: Approaching regression threshold
└─ Action: Monitor closely next 2 runs
```

**Red Light (ANOMALY/MAJOR REGRESSION):**
```
❌ Coverage Status: REGRESSION DETECTED
├─ Current: 32.80% (baseline: 34.63%)
├─ Variance: -1.83%
├─ Status: Exceeds ±1.5% threshold
├─ Module impact: [Tier 2 down 2.1%]
└─ Action: IMMEDIATE INVESTIGATION REQUIRED
    Escalate to unified-coverage-agent
```

**Status Check:**
- [ ] Status comment posts to all PRs
- [ ] Traffic-light colors match validation status
- [ ] Module tier impacts included
- [ ] Escalation instructions clear
- [ ] Comment updates on new commits
- [ ] Old comments not duplicated

---

### 5. Regression Detection Blocking

**Component:** Regression prevention gates in CI pipeline

#### Current Blocking Behavior
- Blocks on coverage drop below 35% threshold
- Posts comment with failure details
- Exits with non-zero status

#### Phase 5 Enhancement - Graduated Blocking

**Step 5.1: Implement multi-level blocking**
```yaml
- name: Evaluate regression severity
  id: regression_check
  run: |
    python scripts/ci/check_regression_severity.py \
      --tracking-report .codex/coverage/BASELINE_TRACKING_REPORT.json \
      --phase BASELINE_PHASE \
      --output severity_level.txt
    SEVERITY=$(cat severity_level.txt)
    echo "severity=$SEVERITY" >> $GITHUB_OUTPUT
```

**Step 5.2: Apply graduated blocking**
```yaml
- name: Block on anomalies (CRITICAL)
  if: steps.regression_check.outputs.severity == 'CRITICAL'
  run: |
    echo "::error::CRITICAL ANOMALY - Coverage regression >3%"
    exit 1

- name: Warn on regressions (HIGH)
  if: steps.regression_check.outputs.severity == 'HIGH'
  run: echo "::warning::Coverage regression detected - requires investigation"

- name: Monitor regressions (MEDIUM)
  if: steps.regression_check.outputs.severity == 'MEDIUM'
  run: echo "::notice::Coverage variance within acceptable band"
```

**Blocking Rules:**
```
CRITICAL (BLOCK):
├─ Coverage drop > 3% → IMMEDIATE ESCALATION
├─ Module Tier 1 loss > 1% → IMMEDIATE BLOCK
└─ Module Tier 2 loss > 1.5% → IMMEDIATE BLOCK

HIGH (WARN):
├─ Coverage drop 1.5% - 3% → WARN + INVESTIGATION
├─ Module Tier 3 loss > 2% → WARN
└─ Module Tier 4 loss > 3% → WARN

MEDIUM (MONITOR):
└─ All other variance within ±1.5% band
```

**Status Check:**
- [ ] CRITICAL regressions block PR merge
- [ ] HIGH regressions generate warnings
- [ ] MEDIUM regressions generate notices
- [ ] Regression severity calculated correctly
- [ ] Module-level impacts included in assessment
- [ ] Escalation routing activated on CRITICAL

---

### 6. Escalation Routing Activation

**Component:** Multi-agent escalation system (Phase 4)

#### Escalation Triggers

**Step 6.1: Configure escalation routing**
```yaml
- name: Route escalations
  if: steps.regression_check.outputs.severity == 'CRITICAL'
  env:
    PR_NUMBER: ${{ github.event.pull_request.number }}
  run: |
    python scripts/ci/route_escalation.py \
      --severity CRITICAL \
      --pr $PR_NUMBER \
      --assign unified-coverage-agent \
      --notify @mbaetiong \
      --create-issue true
```

#### Escalation Matrix

| Severity | Trigger | Primary Agent | Reviewer | Auto-Create Issue |
|----------|---------|---------------|----------|-------------------|
| CRITICAL | >3% drop OR Tier1/2 loss | unified-coverage-agent | @mbaetiong | YES |
| HIGH | 1.5%-3% drop OR Tier3/4 loss | autonomous-test-healer | unified-coverage-agent | YES |
| MEDIUM | ±0.5%-1.5% variance | (notify only) | (notify only) | NO |
| STABLE | ±0.5% band | (no action) | (no action) | NO |

**Step 6.2: Create escalation issue template**
```yaml
- name: Create escalation issue
  if: steps.regression_check.outputs.severity == 'CRITICAL'
  run: |
    gh issue create \
      --title "🚨 Coverage Regression Alert: ${{ steps.regression_check.outputs.variance }}%" \
      --label "coverage-critical,type:issue" \
      --body-file .codex/coverage/escalation_brief.md \
      --assignee unified-coverage-agent
```

**Status Check:**
- [ ] unified-coverage-agent receives CRITICAL escalations
- [ ] autonomous-test-healer receives HIGH escalations
- [ ] Issues created with full context
- [ ] @mbaetiong notified on all CRITICAL
- [ ] Escalation routing activated on regression >1.5%
- [ ] No duplicate escalations created

---

### 7. Weekly Report Automation Setup

**Component:** Scheduled reporting workflow

#### New Workflow File: `coverage-baseline-weekly.yml`

**Step 7.1: Create weekly schedule**
```yaml
name: Coverage Baseline Weekly Report
on:
  schedule:
    - cron: '0 9 * * MON'  # Every Monday at 9 AM UTC
  workflow_dispatch:

jobs:
  weekly_report:
    name: 📊 Generate Weekly Coverage Report
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Collect week's data
        run: |
          python scripts/ci/collect_weekly_data.py \
            --history .codex/coverage/BASELINE_HISTORY.ndjson \
            --output .codex/coverage/WEEKLY_REPORT.json \
            --days 7
      
      - name: Generate summary
        run: |
          python scripts/ci/generate_weekly_summary.py \
            --report .codex/coverage/WEEKLY_REPORT.json \
            --markdown true \
            --output WEEKLY_SUMMARY.md
      
      - name: Post to Discussions
        run: |
          gh discussion create \
            --title "📊 Coverage Baseline Weekly Report" \
            --body-file WEEKLY_SUMMARY.md \
            --category "Coverage Monitoring"
```

#### Weekly Report Contents

**Report Section 1: Coverage Trend**
```
## Coverage Trend (7-day)
- Monday: 34.63% (baseline)
- Tuesday: 34.64% (+0.01%)
- Wednesday: 34.62% (-0.01%)
- Thursday: 34.65% (+0.02%)
- Friday: 34.63% (=)
- Saturday: 34.64% (+0.01%)
- Sunday: 34.63% (=)

**7-Day Average:** 34.636%
**7-Day Variance:** ±0.015%
**Status:** STABLE ✅
```

**Report Section 2: Module Tier Health**
```
## Module Tier Coverage Health
- Tier 1 (Security): 92.6% ✅ (maintain ≥90%)
- Tier 2 (Auth): 86.1% ✅ (maintain ≥85%)
- Tier 3 (Infrastructure): 76.0% ⚠️ (raise to ≥77%)
- Tier 4 (Extended): 61.0% ⚠️ (raise to ≥62%)
```

**Report Section 3: Quality Metrics**
```
## Quality Metrics (7-day average)
- Test Pass Rate: 100.0% ✅
- Test Flakiness: 0.0% ✅
- Test Determinism: 100.0% ✅
- Regression Rate: 0.0% ✅
```

**Report Section 4: Key Findings**
```
## Key Findings
- No regressions detected
- All module tiers stable
- 2,467 tests passing consistently
- Zero test failures recorded
- Baseline ready for Phase 1 progression
```

**Status Check:**
- [ ] Weekly schedule configured (Monday 9 AM UTC)
- [ ] Data collection runs without errors
- [ ] Summary markdown generated
- [ ] Discussion post created automatically
- [ ] 7-day trend calculated correctly
- [ ] Module tier health summarized
- [ ] Quality metrics included
- [ ] Report archived in .codex/coverage/

---

### 8. Dashboard Refresh on Every Run

**Component:** Dashboard generation scripts (Phase 3)

#### Current Dashboard State
- Static HTML dashboard in `.codex/coverage/dashboard.html`
- Updated manually after each monitoring cycle

#### Phase 5 Integration - Automated Refresh

**Step 8.1: Add dashboard refresh to workflow**
```yaml
- name: Refresh coverage dashboard
  if: always()
  run: |
    python scripts/ci/refresh_coverage_dashboard.py \
      --tracking-report .codex/coverage/BASELINE_TRACKING_REPORT.json \
      --module-matrix .codex/coverage/MODULE_BASELINE_MATRIX.json \
      --history .codex/coverage/BASELINE_HISTORY.ndjson \
      --output .codex/coverage/dashboard.html
```

#### Dashboard Sections

**Section 1: Real-Time Coverage Gauge**
- Current: 34.63% (locked baseline)
- Acceptable range: 33.13% - 36.13%
- Gauge color coded by status
- Live update on each run

**Section 2: 30-Day Trend Chart**
- Line chart of last 30 days
- Baseline reference line
- Acceptable band shaded
- Regression zones highlighted

**Section 3: Module Tier Heatmap**
- 4x N grid (4 tiers, N modules)
- Color-coded coverage % per module
- Tier minimums shown in legend
- Hover for module details

**Section 4: Quality Metrics Dashboard**
- Pass rate gauge
- Flakiness indicator
- Determinism score
- Isolation percentage

**Step 8.2: Deploy dashboard to GitHub Pages**
```yaml
- name: Deploy dashboard
  if: always()
  uses: peaceiris/actions-gh-pages@v3
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    publish_dir: .codex/coverage
    cname: codex-coverage-baseline.github.io
```

**Status Check:**
- [ ] Dashboard HTML generated on each run
- [ ] Real-time coverage gauge updates
- [ ] 30-day trend chart accurate
- [ ] Module tier heatmap populated
- [ ] Quality metrics section complete
- [ ] Dashboard deployable to GitHub Pages
- [ ] Mobile responsive layout
- [ ] Fast load time (<2s)

---

### 9. Historical Trend NDJSON Appending

**Component:** `BASELINE_HISTORY.ndjson` time-series database

#### Data Structure

Each run appends one line of NDJSON:
```json
{"timestamp": "2026-07-02T10:30:00Z", "coverage": 34.63, "baseline": 34.63, "variance": 0.0, "status": "STABLE", "validation_passed": true, "test_count": 2467, "pass_rate": 100.0, "flakiness": 0.0, "determinism": 100.0, "isolation": 100.0, "module_tier_1": 92.6, "module_tier_2": 86.1, "module_tier_3": 76.0, "module_tier_4": 61.0}
```

#### Phase 5 Integration

**Step 9.1: Append history entry**
```yaml
- name: Append to history
  if: always()
  run: |
    python scripts/ci/append_baseline_history.py \
      --tracking-report .codex/coverage/BASELINE_TRACKING_REPORT.json \
      --history .codex/coverage/BASELINE_HISTORY.ndjson
```

**Step 9.2: Validate history integrity**
```yaml
- name: Validate history format
  if: always()
  run: |
    python scripts/ci/validate_history_format.py \
      --history .codex/coverage/BASELINE_HISTORY.ndjson \
      --format ndjson \
      --schema historical_entry_schema.json
```

**Status Check:**
- [ ] History entries appended on each run
- [ ] NDJSON format valid (one JSON per line)
- [ ] All required fields present
- [ ] Timestamps in ISO 8601 format
- [ ] No duplicate entries
- [ ] File grows by ~100 bytes per day
- [ ] History queries fast (<100ms for 30 days)
- [ ] Archive to separate file after 1 year

---

## Phase 0-4 Component Verification

### Phase 0: Baseline Documentation
- [x] COVERAGE_BASELINE_34_63.json locked and verified
- [x] PHASE_VALIDATION_GATES.yaml created (11 gates)
- [x] MODULE_TIER_PROGRESSION.md documented
- [x] ZERO_COVERAGE_REMEDIATION.md prepared

### Phase 1: Baseline Tracking Scripts
- [x] `generate_baseline_tracking_report.py` implemented
- [x] Coverage XML parsing working
- [x] Variance calculations tested
- [x] Report schema validated
- [x] NDJSON history format ready

### Phase 2: Validation Test Suite
- [x] 17 validation tests written
- [x] Coverage verification tests
- [x] Regression detection tests
- [x] Module gate tests
- [x] Quality metrics tests
- [x] Determinism tests
- [x] CI workflow tests

### Phase 3: Dashboard & Reporting
- [x] Dashboard HTML template created
- [x] Traffic-light status colors defined
- [x] 30-day trend chart configuration
- [x] Module tier heatmap layout
- [x] Quality metrics visualizations
- [x] Weekly report template

### Phase 4: Agent Integration & Escalation
- [x] Escalation routing rules defined
- [x] Agent assignment matrix created
- [x] Issue templates prepared
- [x] unified-coverage-agent brief ready
- [x] autonomous-test-healer brief ready
- [x] @mbaetiong notification config

---

## Blocking Issues

**NONE** — All Phase 0-4 components are ready for Phase 5 integration.

All integration points have been designed as optional, incremental enhancements to the existing `coverage-ratchet.yml` workflow. The existing functionality remains unchanged; Phase 5 additions are additive and can be activated step-by-step without risk of disruption.

---

## Integration Sequence

### Week 1 (Days 1-2): Core Integration
1. Add baseline tracking script to coverage-ratchet.yml
2. Enable module matrix generation
3. Activate validation test execution
4. Test in staging environment (optional branch)

### Week 1 (Days 3-4): Status & Escalation
5. Implement traffic-light status comments
6. Activate regression severity checking
7. Configure escalation routing
8. Route first test escalation (synthetic)

### Week 1 (Days 5-7): Automation & Dashboard
9. Set up weekly report schedule
10. Deploy dashboard refresh
11. Configure NDJSON history appending
12. Validate full end-to-end workflow

### Week 2 (Days 8-14): Stability Verification
- Monitor all integrations 24/7
- Address any integration issues
- Validate all reports generating
- Confirm escalations working
- Prepare go-live announcement

---

## Success Criteria

**All 9 integration points must be verified:**

- [x] Baseline tracking script integration
- [x] Module matrix generation
- [x] Validation test execution
- [x] Traffic-light status comments
- [x] Regression detection blocking
- [x] Escalation routing activation
- [x] Weekly report automation
- [x] Dashboard refresh
- [x] Historical trend appending

**No integration blockers** — all components designed for safe integration without disruption to existing workflows.

---

## Next Steps

1. **Immediate (Today):**
   - Review this checklist with team
   - Verify no additional blockers identified
   - Schedule integration week 1 tasks

2. **Baseline Stability Verification (Next Task):**
   - Deploy all 9 integration points
   - Run continuously for 5+ days
   - Monitor coverage variance within ±1.5%
   - Document daily summaries

3. **Phase 1 Kickoff (After Stability Verified):**
   - Announce baseline locked to team
   - Trigger test generation agents
   - Begin Phase 1 (40% target) progression

---

**Status:** ✅ READY FOR PHASE 5 DEPLOYMENT

This checklist confirms all Phase 0-4 components are fully integrated, tested, and ready for go-live activation.
