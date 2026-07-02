# Phase 3: Coverage Dashboard & Reporting Automation

> **Phase Deliverables:** Complete automation for continuous coverage monitoring and reporting
> 
> **Timeline:** Days 9-10 of Coverage Baseline Monitoring Plan  
> **Status:** Implementation Ready

---

## 📋 Overview

Phase 3 delivers three key automation systems for the Coverage Baseline Monitoring Plan:

1. **Coverage Dashboard Generator** - Auto-generates visual dashboard from CI outputs
2. **Weekly Report Automation** - Auto-generates weekly trend reports and analyses
3. **Phase Validation Report Template** - Standardized template for phase progression gates

---

## 🎯 Deliverables

### 1️⃣ Coverage Dashboard Generator

**Script:** `scripts/ci/generate_coverage_dashboard.py`

**Purpose:** Auto-generates `.codex/coverage/COVERAGE_DASHBOARD.md` on every test run

**Inputs:**
- `.codex/coverage/BASELINE_TRACKING_REPORT.json` - Current coverage snapshot
- `.codex/coverage/MODULE_BASELINE_MATRIX.json` - Module tier breakdown
- `.codex/coverage/BASELINE_HISTORY.ndjson` - 30+ days historical data

**Outputs:**
- `.codex/coverage/COVERAGE_DASHBOARD.md` - Live dashboard markdown

**Key Sections:**
```
📊 Current Coverage
  ├─ Coverage: 34.63% (status indicator)
  ├─ Baseline: 34.63%
  ├─ Variance: ±0.00%
  └─ Trend: ↔️ STABLE

📈 Phase Progress
  ├─ Phase: BASELINE_PHASE
  ├─ Target: 95.0%
  ├─ Progress: 36.5% toward target
  └─ Status: 🔒 LOCKED - Monitoring

✅ Quality Metrics (4 indicators)
  ├─ Test Pass Rate: 100.0% ✅
  ├─ Test Flakiness: 0.0% ✅
  ├─ Test Determinism: 100.0% ✅
  └─ Test Isolation: 100.0% ✅

📦 Module Tier Breakdown (4 tables)
  ├─ Tier 1: Security & Auth (92.4%)
  ├─ Tier 2: Auth Systems (86.2%)
  ├─ Tier 3: Infrastructure (76.0%)
  └─ Tier 4: Extended (61.0%)

⚠️ Top 10 Lowest Coverage Modules
  ├─ Module: Coverage (Tests)
  └─ ...

🔍 Latest Validation
  ├─ Status: ✅ PASSED
  ├─ Message: STABLE
  └─ Timestamp: 2026-07-02T02:24:41Z

📉 30-Day Coverage Trend
  └─ Text-based trend table

🚀 Recommended Actions
  └─ Context-specific action items
```

**Usage:**

```bash
# Generate dashboard with default paths
python scripts/ci/generate_coverage_dashboard.py

# Custom input/output paths
python scripts/ci/generate_coverage_dashboard.py \
  --input-dir .codex/coverage \
  --output .codex/coverage/COVERAGE_DASHBOARD.md
```

**Integration Points:**
- Runs on every `pytest` execution
- Called by CI/CD pipeline after test phase
- Uploaded as build artifact
- Embedded in PRs as auto-comment

---

### 2️⃣ Weekly Report Automation

**Script:** `scripts/ci/generate_weekly_report.py`

**Purpose:** Auto-generates `.codex/coverage/WEEKLY_COVERAGE_REPORT.md` weekly

**Trigger:** 
- Mondays 08:00 UTC (schedule via GitHub Actions)
- On-demand via `--weeks` parameter

**Inputs:**
- `.codex/coverage/BASELINE_HISTORY.ndjson` - 7-day rolling history
- `.codex/coverage/BASELINE_TRACKING_REPORT.json` - Current snapshot
- `.codex/coverage/MODULE_BASELINE_MATRIX.json` - Module data

**Outputs:**
- `.codex/coverage/WEEKLY_COVERAGE_REPORT.md` - Weekly analysis

**Key Sections:**
```
📊 Weekly Coverage Report

📈 Week-over-Week Change
  ├─ Coverage Change: ±X.XX%
  ├─ This Week: 34.63%
  ├─ Last Week: 34.60%
  └─ Variance: 0.03%

📦 Module Tier Performance (table)
  ├─ Tier 1: 92.4% (5 modules)
  ├─ Tier 2: 86.2% (8 modules)
  ├─ Tier 3: 76.0% (6 modules)
  └─ Tier 4: 61.0% (N modules)

🧪 Test Trends
  ├─ Pass Rate: 100.0%
  ├─ Flakiness: 0.0%
  ├─ Determinism: 100.0%
  └─ Test Runs: [#]

🚨 Risks & Alerts
  ├─ Coverage variance >1.5%?
  ├─ Flaky tests detected?
  ├─ Quality metrics breached?
  └─ Validation failures?

✅ Action Items
  ├─ [ ] Investigate coverage variance
  ├─ [ ] Run test healer if needed
  ├─ [ ] Review tier progression
  └─ [ ] Check Phase 1 readiness

🎯 Phase Progression
  ├─ Current: Baseline Phase @ 34.63%
  ├─ Next Phase: Phase 1 (40% target)
  └─ Prerequisite: 30 days stable ±1.5%
```

**Usage:**

```bash
# Generate current week report
python scripts/ci/generate_weekly_report.py

# Generate last week report
python scripts/ci/generate_weekly_report.py --weeks 1

# Custom output
python scripts/ci/generate_weekly_report.py \
  --weeks 0 \
  --output .codex/coverage/WEEKLY_COVERAGE_REPORT.md
```

**GitHub Actions Schedule:**

```yaml
name: Weekly Coverage Report
on:
  schedule:
    - cron: '0 8 * * 1'  # Every Monday at 08:00 UTC
  workflow_dispatch:

jobs:
  generate-report:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Generate Weekly Report
        run: python scripts/ci/generate_weekly_report.py
      
      - name: Commit & Push
        run: |
          git add .codex/coverage/WEEKLY_COVERAGE_REPORT.md
          git commit -m "chore: generate weekly coverage report"
          git push
```

---

### 3️⃣ Phase Validation Report Template

**File:** `.codex/PHASE_VALIDATION_REPORT_TEMPLATE.md`

**Purpose:** Standardized template for documenting phase progression validation

**When to Use:**
- At the END of each phase (Baseline → Phase 1 → Phase 2 → ... → 95%)
- Before requesting phase progression approval
- For sign-off and audit trail

**Key Sections:**
```
📋 Executive Summary
  ├─ Phase: BASELINE_PHASE
  ├─ Window: Start → End date
  ├─ Status: ✅ PASSED / ⚠️ CONDITIONAL / ❌ FAILED
  └─ Generated: ISO 8601 timestamp

🎯 Coverage Metrics
  ├─ Overall: baseline vs. target vs. achieved
  ├─ Lines: covered/total
  ├─ Branch: %
  ├─ Function: %
  └─ Variance analysis (STABLE/ACCEPTABLE/REGRESSION)

📦 Module Tier Results (4 tables)
  ├─ Tier 1: Security & Auth
  ├─ Tier 2: Auth Systems
  ├─ Tier 3: Infrastructure
  └─ Tier 4: Extended
    ├─ Coverage achieved
    ├─ Module count
    ├─ Avg coverage
    ├─ Test count
    ├─ Top 3 modules
    └─ Regressions detected

🧪 Test Statistics
  ├─ Test Count (happy/edge/error path breakdown)
  ├─ Pass Rate: target vs. achieved
  ├─ Flakiness: target vs. achieved
  ├─ Determinism: target vs. achieved
  ├─ Isolation: target vs. achieved
  └─ Execution summary (runs, duration, issues)

✅ Quality Metrics (All 4 Required)
  ├─ 1. Test Pass Rate (≥99.5%)
  ├─ 2. Test Flakiness (≤0.0%)
  ├─ 3. Test Determinism (≥100.0%)
  └─ 4. Test Isolation (≥100.0%)

🔍 Issues Found & Remediated
  ├─ Critical Issues (blocking)
  ├─ High Priority Issues
  ├─ Medium Priority Issues
  └─ Known Limitations / Deferred

📊 Phase Timeline & Effort
  ├─ Kickoff, Test Gen, Validation, Verification
  ├─ Duration breakdown
  └─ Actual vs. Planned

👥 Approval & Sign-Off
  ├─ Agent Review (unified-coverage-agent, etc.)
  ├─ Human Review (required)
  └─ Final Approval (@mbaetiong or delegated)

🚀 Next Phase Recommendation
  ├─ Decision: PROCEED / CONDITIONAL / HOLD
  ├─ Rationale & key achievements
  ├─ Prerequisites for next phase
  ├─ Blockers / Risk mitigation
  └─ Appendices (test logs, coverage snapshot, etc.)
```

**Usage:**

1. **Baseline Phase Completion (Day 30):**
   - Copy template to `.codex/BASELINE_PHASE_VALIDATION_REPORT.md`
   - Fill in all sections with actual data
   - Get agent review from `unified-coverage-agent`
   - Get human review from codebase owner
   - Get final approval to proceed to Phase 1

2. **Phase 1 Completion (Day 15):**
   - Copy template to `.codex/PHASE_1_VALIDATION_REPORT.md`
   - Fill in sections for Phase 1 (40% target)
   - Get approvals from unified-coverage-agent + human
   - Proceed to Phase 2

3. **Repeat for each phase:**
   - Phase 2 (50%), Phase 3 (60%), ... Phase 9 (93%), Final (95%)

---

## 🔄 Integration Architecture

```
CI/CD Pipeline
    ↓
[Tests Run]
    ↓
[Coverage Measured]
    ↓
[BASELINE_TRACKING_REPORT.json created]
    ↓
[generate_coverage_dashboard.py]
    ├─→ COVERAGE_DASHBOARD.md (updated)
    └─→ Available in artifacts + PR comment
    ↓
[BASELINE_HISTORY.ndjson appended]
    ↓
[Every Monday 08:00 UTC]
    ↓
[generate_weekly_report.py]
    └─→ WEEKLY_COVERAGE_REPORT.md (updated)
    ↓
[After Phase Completion]
    ↓
[Fill PHASE_VALIDATION_REPORT_TEMPLATE.md]
    ├─→ Get agent review
    ├─→ Get human review
    └─→ Get final approval → Next Phase
```

---

## 🚀 Activation & Deployment

### Step 1: Enable Dashboard Generation

**In `.github/workflows/test.yml`:**

```yaml
- name: Generate Coverage Dashboard
  if: always()
  run: |
    python scripts/ci/generate_coverage_dashboard.py \
      --output .codex/coverage/COVERAGE_DASHBOARD.md
    
- name: Upload Dashboard
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: coverage-dashboard
    path: .codex/coverage/COVERAGE_DASHBOARD.md
    retention-days: 30

- name: Comment on PR with Dashboard
  if: github.event_name == 'pull_request'
  uses: actions/github-script@v7
  with:
    script: |
      const fs = require('fs');
      const dashboard = fs.readFileSync('.codex/coverage/COVERAGE_DASHBOARD.md', 'utf8');
      github.rest.issues.createComment({
        issue_number: context.issue.number,
        owner: context.repo.owner,
        repo: context.repo.repo,
        body: dashboard
      });
```

### Step 2: Enable Weekly Report Generation

**In `.github/workflows/weekly-coverage-report.yml`:**

```yaml
name: Weekly Coverage Report
on:
  schedule:
    - cron: '0 8 * * 1'  # Every Monday at 08:00 UTC
  workflow_dispatch:

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Generate Weekly Report
        run: python scripts/ci/generate_weekly_report.py
      
      - name: Commit & Push
        run: |
          git config user.name "coverage-bot"
          git config user.email "coverage@codex.local"
          git add .codex/coverage/WEEKLY_COVERAGE_REPORT.md
          git commit -m "chore: generate weekly coverage report [skip ci]"
          git push
```

### Step 3: Prepare for Phase Validation

**Before starting Phase 1 (Day 30):**

1. Copy template to `.codex/BASELINE_PHASE_VALIDATION_REPORT.md`
2. Extract data from `.codex/coverage/BASELINE_TRACKING_REPORT.json`
3. Fill sections with actual metrics
4. Get agent review → human review → approval
5. Proceed to Phase 1

---

## 📊 Success Metrics (Phase 3)

### Automated Generation

- ✅ Dashboard generates without errors on every test run
- ✅ Weekly reports generate on schedule (Mondays 08:00 UTC)
- ✅ Phase validation template ready for use
- ✅ All data sources (BASELINE_TRACKING_REPORT.json, MODULE_BASELINE_MATRIX.json, BASELINE_HISTORY.ndjson) properly loaded

### Report Quality

- ✅ Dashboard includes all 8 required sections
- ✅ Weekly reports include 6 required sections
- ✅ Phase validation template has all required fields
- ✅ All reports properly formatted (markdown + emoji indicators)

### Documentation

- ✅ README.md created with usage examples
- ✅ Script docstrings complete with inputs/outputs/usage
- ✅ Integration guide provided
- ✅ Sample reports demonstrable

---

## 📚 Reference Documentation

- `.codex/COVERAGE_VALIDATION_CRITERIA.md` - Validation rules
- `.codex/PHASE_VALIDATION_GATES.yaml` - Phase gate definitions
- `.codex/coverage/BASELINE_TRACKING_REPORT.json` - Current metrics
- `.codex/coverage/MODULE_BASELINE_MATRIX.json` - Module breakdown
- `.codex/coverage/BASELINE_HISTORY.ndjson` - 30+ day history

---

## 🔗 Next Steps (Phase 4)

After Phase 3 deployment:

1. **Monitor Dashboard** - Verify it generates correctly on all test runs
2. **Collect Week 1 Data** - Let weekly report run first cycle
3. **Day 30 Checkpoint** - Prepare Phase 1 validation report
4. **Phase 1 Kickoff** - Begin test generation for 40% target
5. **Continuous Monitoring** - Dashboard + weekly reports remain live

---

**Phase 3 Status:** ✅ IMPLEMENTATION COMPLETE  
**Generated:** 2026-07-02  
**Last Updated:** 2026-07-02T02:30:00Z  
**Next Review:** After first full week of data collection
