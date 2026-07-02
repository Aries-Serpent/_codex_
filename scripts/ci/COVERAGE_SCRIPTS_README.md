# Coverage Reporting Scripts

Automation scripts for continuous coverage monitoring and reporting.

## Scripts

### `generate_coverage_dashboard.py`

Auto-generates `.codex/coverage/COVERAGE_DASHBOARD.md` from CI coverage metrics.

**Purpose:** Provides real-time dashboard view of coverage status, quality metrics, and module tier breakdown.

**Usage:**

```bash
# Standard usage (reads from .codex/coverage/, writes to .codex/coverage/COVERAGE_DASHBOARD.md)
python scripts/ci/generate_coverage_dashboard.py

# Custom paths
python scripts/ci/generate_coverage_dashboard.py \
  --input-dir .codex/coverage \
  --output .codex/coverage/COVERAGE_DASHBOARD.md

# With help
python scripts/ci/generate_coverage_dashboard.py --help
```

**Inputs:**
- `.codex/coverage/BASELINE_TRACKING_REPORT.json` - Current coverage snapshot
- `.codex/coverage/MODULE_BASELINE_MATRIX.json` - Module tier breakdown
- `.codex/coverage/BASELINE_HISTORY.ndjson` - 30+ days historical data

**Output:**
- `.codex/coverage/COVERAGE_DASHBOARD.md` - Live dashboard (auto-generated)

**Output Format:**

```markdown
# 📊 Coverage Dashboard

## 🎯 Current Coverage
Coverage: 34.63% 🟢 STABLE ↔️ STABLE

## 📈 Phase Progress
Phase: BASELINE_PHASE (🔒 LOCKED)
Progress: 36.5% toward 95% target

## ✅ Quality Metrics
- Test Pass Rate: 100.0% ✅
- Test Flakiness: 0.0% ✅
- Test Determinism: 100.0% ✅
- Test Isolation: 100.0% ✅

## 📦 Module Tier Breakdown
[4 tables: one per tier with coverage % and test count]

## ⚠️ Top 10 Lowest Coverage Modules
[Modules with lowest coverage %]

## 🔍 Latest Validation
Status: ✅ PASSED

## 📉 30-Day Coverage Trend
[Text-based trend table with dates and coverage %]

## 🚀 Recommended Actions
[Context-specific action items]
```

**Integration:**
- Call on every test run (after coverage measurement)
- Upload to build artifacts
- Post as PR comment (optional)
- Commit to repo (optional)

---

### `generate_weekly_report.py`

Auto-generates `.codex/coverage/WEEKLY_COVERAGE_REPORT.md` with weekly trend analysis.

**Purpose:** Provides weekly summary of coverage trends, test quality, and phase progression readiness.

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

# With help
python scripts/ci/generate_weekly_report.py --help
```

**Inputs:**
- `.codex/coverage/BASELINE_HISTORY.ndjson` - 7-day rolling history
- `.codex/coverage/BASELINE_TRACKING_REPORT.json` - Current snapshot
- `.codex/coverage/MODULE_BASELINE_MATRIX.json` - Module tier data

**Output:**
- `.codex/coverage/WEEKLY_COVERAGE_REPORT.md` - Weekly report (auto-generated)

**Output Format:**

```markdown
# 📊 Weekly Coverage Report

Period: 2026-06-29 to 2026-07-06 (UTC)

## 📈 Week-over-Week Change
Coverage Change: ±X.XX% ↗️/↘️/↔️
This Week: 34.63%
Last Week: 34.60%

## 📦 Module Tier Performance
[Table: Tier | Coverage | Modules]

## 🧪 Test Trends
This Week:
  Pass Rate: 100.0%
  Flakiness: 0.0%
  Determinism: 100.0%
  Test Runs: 1

## 🚨 Risks & Alerts
- ✅ No risks detected - all metrics within range
- ⚠️ [Any specific alerts]

## ✅ Action Items
- [ ] Coverage stable - continue baseline monitoring
- [ ] Review tier-level progression for Phase 1 readiness

## 🎯 Phase Progression
Current: Baseline Phase @ 34.63%
Next Phase: Phase 1 (40% target)
Prerequisite: 30 days stable ±1.5%
```

**Trigger Options:**

1. **Manual:** Run anytime to generate report for any week
2. **Scheduled:** GitHub Actions cron on Mondays 08:00 UTC
3. **On-Demand:** Workflow dispatch in GitHub UI

**GitHub Actions Example:**

```yaml
name: Weekly Coverage Report
on:
  schedule:
    - cron: '0 8 * * 1'  # Monday 08:00 UTC
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
      
      - name: Commit & Push Report
        run: |
          git config user.name "coverage-bot"
          git config user.email "coverage@codex.local"
          git add .codex/coverage/WEEKLY_COVERAGE_REPORT.md
          git commit -m "chore: generate weekly coverage report"
          git push
```

---

## Template: Phase Validation Report

**File:** `.codex/PHASE_VALIDATION_REPORT_TEMPLATE.md`

**Purpose:** Standardized template for documenting phase progression validation and approval.

**When to Use:**
- At END of each phase (Baseline, Phase 1, Phase 2, ..., Final)
- Before requesting phase progression approval
- For audit trail and sign-off

**Usage:**

1. Copy template to new file:
   ```bash
   cp .codex/PHASE_VALIDATION_REPORT_TEMPLATE.md \
      .codex/BASELINE_PHASE_VALIDATION_REPORT.md
   ```

2. Fill sections with actual data:
   - Coverage metrics
   - Module tier results
   - Test statistics
   - Quality metrics
   - Issues found & remediated
   - Approval sign-offs

3. Get reviews:
   - Agent review (unified-coverage-agent)
   - Human review (codebase owner)
   - Final approval (@mbaetiong or delegated)

4. Commit as record of validation

**Template Structure:**

```markdown
# Phase Validation Report

## 📋 Executive Summary
Phase: [PHASE_NAME]
Validation Window: [dates]
Status: ✅ PASSED / ⚠️ CONDITIONAL / ❌ FAILED

## 🎯 Coverage Metrics
[Tables: baseline vs. achieved]

## 📦 Module Tier Results
[4 tables: one per tier]

## 🧪 Test Statistics
[Test counts, pass rate, quality metrics]

## ✅ Quality Metrics (All 4 Required)
1. Test Pass Rate
2. Test Flakiness
3. Test Determinism
4. Test Isolation

## 🔍 Issues Found & Remediated
[Critical, High, Medium priority issues]

## 👥 Approval & Sign-Off
[Agent review, Human review, Final approval]

## 🚀 Next Phase Recommendation
[PROCEED / CONDITIONAL / HOLD]
```

---

## Data Sources & Format

### BASELINE_TRACKING_REPORT.json

**Format:**
```json
{
  "timestamp": "2026-07-02T02:24:41Z",
  "baseline_snapshot": {
    "locked_date": "2026-07-02T02:22:00Z",
    "phase": "BASELINE_PHASE",
    "baseline_coverage": 34.63,
    "acceptable_range": {
      "min": 33.13,
      "max": 36.13
    }
  },
  "current_metrics": {
    "line_coverage_percent": 34.63,
    "branch_coverage_percent": 18.2,
    "function_coverage_percent": 24.3,
    "lines_covered": 34631,
    "lines_total": 100355
  },
  "validation": {
    "passed": true,
    "status": "STABLE",
    "variance_pct": 0.0,
    "message": "STABLE: Coverage within ±0.5% band"
  },
  "quality_metrics": {
    "test_pass_rate": 100.0,
    "test_flakiness": 0.0,
    "test_determinism": 100.0,
    "test_isolation": 100.0
  }
}
```

### MODULE_BASELINE_MATRIX.json

**Format:**
```json
{
  "metadata": {
    "generated_date": "2026-07-02T02:22:00Z",
    "baseline_phase": "BASELINE_PHASE",
    "baseline_coverage": 34.63,
    "total_modules_tracked": 175
  },
  "tier_1_security_authentication": {
    "tier_name": "Security & Authentication Core",
    "status": "COMPREHENSIVE",
    "target_coverage": 92.6,
    "total_tests": 287,
    "modules": [
      {
        "module": "security_core",
        "coverage_percent": 92.8,
        "tests": 35,
        "status": "STABLE"
      }
    ]
  }
}
```

### BASELINE_HISTORY.ndjson

**Format:** One JSON object per line (newline-delimited)
```json
{"timestamp": "2026-07-02T02:24:41Z", "coverage": 34.63, "baseline": 34.63, "variance": 0.0, "status": "STABLE"}
{"timestamp": "2026-07-01T23:12:35Z", "coverage": 34.62, "baseline": 34.63, "variance": -0.01, "status": "STABLE"}
```

---

## Requirements

- Python 3.8+
- No external dependencies (uses standard library only)
- Read access to `.codex/coverage/` directory
- Write access to `.codex/coverage/` directory for output

---

## Error Handling

All scripts handle missing input files gracefully:

- Missing `BASELINE_HISTORY.ndjson`: Reports "no historical data"
- Missing module data: Skips tier sections
- Empty history: Dashboard still generates with current metrics

Examples:

```bash
# Missing file - clear error message
$ python scripts/ci/generate_coverage_dashboard.py
❌ Error generating dashboard: [Errno 2] No such file or directory: '.codex/coverage/BASELINE_TRACKING_REPORT.json'

# Partial data - graceful degradation
$ python scripts/ci/generate_weekly_report.py
⚠️ No previous week data available for comparison.
✅ Weekly report generated: .codex/coverage/WEEKLY_COVERAGE_REPORT.md
```

---

## Testing

### Test Dashboard Generation

```bash
cd /home/runner/work/_codex_/_codex_

# Generate dashboard
python scripts/ci/generate_coverage_dashboard.py

# Verify output
ls -la .codex/coverage/COVERAGE_DASHBOARD.md
head -50 .codex/coverage/COVERAGE_DASHBOARD.md
```

### Test Weekly Report Generation

```bash
cd /home/runner/work/_codex_/_codex_

# Generate current week
python scripts/ci/generate_weekly_report.py

# Verify output
ls -la .codex/coverage/WEEKLY_COVERAGE_REPORT.md
head -50 .codex/coverage/WEEKLY_COVERAGE_REPORT.md
```

### Verify Template

```bash
# Template should exist and be readable
ls -la .codex/PHASE_VALIDATION_REPORT_TEMPLATE.md

# Spot check key sections
grep -c "^##" .codex/PHASE_VALIDATION_REPORT_TEMPLATE.md  # Should have many sections
```

---

## CI/CD Integration

### Integration with Test Workflow

Add to `.github/workflows/test.yml` (after coverage measurement):

```yaml
- name: Generate Coverage Dashboard
  if: always()
  run: python scripts/ci/generate_coverage_dashboard.py

- name: Upload Coverage Dashboard
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: coverage-dashboard
    path: .codex/coverage/COVERAGE_DASHBOARD.md
    retention-days: 30
```

### Integration with PR Comments

Add to `.github/workflows/pr-comment.yml`:

```yaml
- name: Comment Coverage Dashboard
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

---

## Troubleshooting

### Dashboard Not Generating

1. Check input files exist:
   ```bash
   ls .codex/coverage/BASELINE_TRACKING_REPORT.json
   ls .codex/coverage/MODULE_BASELINE_MATRIX.json
   ```

2. Verify Python is available:
   ```bash
   python --version  # Should be 3.8+
   ```

3. Run with verbose output:
   ```bash
   python -u scripts/ci/generate_coverage_dashboard.py
   ```

### Weekly Report Showing "No Data"

1. Check history file exists and has entries:
   ```bash
   wc -l .codex/coverage/BASELINE_HISTORY.ndjson  # Should have entries
   head .codex/coverage/BASELINE_HISTORY.ndjson
   ```

2. Verify data is in JSON format:
   ```bash
   python -m json.tool < .codex/coverage/BASELINE_HISTORY.ndjson | head
   ```

3. Check timestamps are ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)

---

## Reference

- `.codex/PHASE_3_IMPLEMENTATION_GUIDE.md` - Full Phase 3 guide
- `.codex/COVERAGE_VALIDATION_CRITERIA.md` - Validation rules
- `.codex/PHASE_VALIDATION_GATES.yaml` - Phase gate definitions
- `.codex/coverage/README.md` - Coverage directory guide

---

**Generated:** 2026-07-02  
**Last Updated:** 2026-07-02T02:30:00Z  
**Script Version:** 1.0
