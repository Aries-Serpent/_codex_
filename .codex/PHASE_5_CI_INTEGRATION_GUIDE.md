# Phase 5 CI Integration Guide: Adding Patterns to CI/CD Pipeline

**Document Date:** 2026-07-09  
**Phase:** Phase 5 Week 2  
**Audience:** DevOps, CI/CD Engineers, Platform Teams  
**Authority:** Phase 5 Execution Mandate (@mbaetiong)

---

## Overview

This guide provides step-by-step instructions for integrating CI Auto-Fixer patterns (36-38) into GitHub Actions CI/CD pipelines.

### What This Guide Covers

- ✅ Adding patterns to GitHub Actions workflows
- ✅ Configuring pattern execution modes
- ✅ Collecting and monitoring metrics
- ✅ Setting up alerts and notifications
- ✅ Troubleshooting common issues

### Pattern Summary

| Pattern | Name | Risk | Priority | Mode |
|---------|------|------|----------|------|
| 37 | Async Timeouts | Low | ⭐ High | Auto-fix |
| 36 | Assert Messages | Low-Med | Medium | Dry-run → Auto-fix |
| 38 | Mock Cleanup | Low-Med | Medium | Dry-run → Auto-fix |

---

## Integration Architecture

### Execution Flow

```
GitHub Actions Workflow
    ↓
[Pattern Selector]
    ↓
auto_fix_common_issues.py
    ├─ Pattern 37 (--pattern 37)
    ├─ Pattern 36 (--pattern 36)
    └─ Pattern 38 (--pattern 38)
    ↓
[JSON Report]
    ↓
Metrics Collection
    ↓
Alert System
```

### Input/Output

**Input:**
- Repository root (auto-detected)
- Pattern number(s) to run
- Mode: `--check-only`, `--dry-run`, or auto-fix
- Optional: JSON output path

**Output:**
- List of detected issues
- List of applied fixes
- JSON metrics report
- Exit code (0 = success, 1 = issues found)

---

## Step 1: Add Pattern to GitHub Actions Workflow

### Basic Integration

**File:** `.github/workflows/validate.yml` (or your validation workflow)

```yaml
name: Validate

on:
  pull_request:
    branches:
      - main
      - develop

jobs:
  ci-patterns:
    name: CI Auto-Fixer - Pattern 37
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for pattern analysis
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"
          cache: "pip"
      
      - name: Run Pattern 37 (Async Timeouts)
        run: |
          python scripts/ci/auto_fix_common_issues.py \
            --pattern 37 \
            --check-only
        continue-on-error: true
```

### Configuration Options

#### Mode 1: Check-Only (Validation)

```yaml
run: |
  python scripts/ci/auto_fix_common_issues.py \
    --pattern 37 \
    --check-only
```

**Use When:**
- First deployment of a pattern
- Baseline validation needed
- Want to measure impact before enabling fixes

**Expected Output:**
```
Pattern 37: Async Timeouts
  ⚠️  Would add X decorator(s)
  ✗ Found X issues
```

#### Mode 2: Dry-Run (Preview)

```yaml
run: |
  python scripts/ci/auto_fix_common_issues.py \
    --pattern 37 \
    --dry-run
```

**Use When:**
- Testing fix logic before auto-enabling
- Want to review what would change
- Staging environment validation

**Expected Output:**
```
Pattern 37: Async Timeouts
  ✅ Would add X decorator(s)
  ✗ Found X issues (would fix)
```

#### Mode 3: Auto-Fix (Production)

```yaml
run: |
  python scripts/ci/auto_fix_common_issues.py \
    --pattern 37
```

**Use When:**
- Pattern validated and proven reliable
- Want automatic fixes in CI
- Has low false positive rate (<1%)

**Expected Output:**
```
Pattern 37: Async Timeouts
  ✅ Added X decorator(s)
  ✓ Found X issues, X auto-fixed
```

### Multi-Pattern Integration

Run multiple patterns in sequence:

```yaml
- name: Run CI Auto-Fixer (All Patterns)
  run: |
    python scripts/ci/auto_fix_common_issues.py \
      --check-only  # Validation mode
  continue-on-error: true

- name: Run Specific Patterns
  run: |
    # Pattern 37 first (highest priority)
    python scripts/ci/auto_fix_common_issues.py --pattern 37 --check-only
    
    # Pattern 36 second
    python scripts/ci/auto_fix_common_issues.py --pattern 36 --dry-run
    
    # Pattern 38 third
    python scripts/ci/auto_fix_common_issues.py --pattern 38 --check-only
  continue-on-error: true
```

---

## Step 2: Collect Metrics and Reports

### JSON Report Generation

```yaml
- name: Generate Pattern Metrics
  run: |
    python scripts/ci/auto_fix_common_issues.py \
      --json-output .codex/patterns-report.json
```

### JSON Output Format

```json
{
  "execution_date": "2026-07-09T12:34:56Z",
  "patterns_run": [36, 37, 38],
  "pattern_results": {
    "36": {
      "name": "Assert Messages",
      "issues_found": 49137,
      "auto_fixable": 45000,
      "fixes_applied": 0,
      "false_positive_rate": 0.015,
      "execution_time_ms": 85
    },
    "37": {
      "name": "Async Timeouts",
      "issues_found": 72,
      "auto_fixable": 65,
      "fixes_applied": 65,
      "false_positive_rate": 0.0,
      "execution_time_ms": 45
    },
    "38": {
      "name": "Mock Cleanup",
      "issues_found": 293,
      "auto_fixable": 190,
      "fixes_applied": 190,
      "false_positive_rate": 0.018,
      "execution_time_ms": 92
    }
  },
  "total_execution_time_ms": 222,
  "repository": "aries-serpent/_codex_"
}
```

### Archive Metrics

```yaml
- name: Archive Pattern Metrics
  uses: actions/upload-artifact@v3
  if: always()
  with:
    name: ci-pattern-metrics
    path: .codex/patterns-report.json
    retention-days: 30
```

---

## Step 3: Monitor Pattern Performance

### Real-Time Logging

```yaml
- name: Display Pattern Results
  if: always()
  run: |
    if [ -f .codex/patterns-report.json ]; then
      echo "=== Pattern Execution Results ==="
      python -m json.tool .codex/patterns-report.json
    fi
```

### Performance Thresholds

Monitor these metrics:

| Metric | Threshold | Alert |
|--------|-----------|-------|
| Execution Time | >500ms | Warn |
| Execution Time | >1000ms | Fail |
| False Positive Rate | >2% | Warn |
| False Positive Rate | >5% | Fail |
| Pattern Crashes | >0 | Fail |

### Health Check Script

```python
#!/usr/bin/env python3
"""Check pattern execution health."""

import json
import sys

with open('.codex/patterns-report.json') as f:
    report = json.load(f)

health_ok = True

for pattern_id, result in report['pattern_results'].items():
    fp_rate = result.get('false_positive_rate', 0)
    exec_time = result.get('execution_time_ms', 0)
    
    if fp_rate > 0.05:
        print(f"❌ Pattern {pattern_id}: High false positive rate: {fp_rate}")
        health_ok = False
    
    if exec_time > 1000:
        print(f"⚠️ Pattern {pattern_id}: Slow execution: {exec_time}ms")

if not health_ok:
    sys.exit(1)
```

---

## Step 4: Set Up Alerts and Notifications

### Alert Configuration

```yaml
- name: Check Pattern Health
  if: always()
  run: |
    python .github/scripts/check_pattern_health.py \
      .codex/patterns-report.json
```

### Slack Notification (Optional)

```yaml
- name: Notify Slack on Pattern Issues
  if: failure()
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK }}
    payload: |
      {
        "text": "❌ CI Pattern execution failed",
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "*CI Pattern Failure*\nRun: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
            }
          }
        ]
      }
```

### GitHub Issue Creation

```yaml
- name: Create Issue if Patterns Fail
  if: failure()
  uses: actions/github-script@v7
  with:
    script: |
      github.rest.issues.create({
        owner: context.repo.owner,
        repo: context.repo.repo,
        title: `CI Pattern Execution Failed (Run #${context.runId})`,
        body: `Pattern execution failed. See logs at: ${context.payload.repository.html_url}/actions/runs/${context.runId}`,
        labels: ['ci', 'patterns', 'urgent']
      })
```

---

## Step 5: Implement Pattern-Specific Workflows

### Pattern 37 (Async Timeouts) - Recommended First

```yaml
name: Pattern 37 - Async Timeouts

on:
  pull_request:
    paths:
      - 'tests/**/*.py'
      - '.github/workflows/pattern37*.yml'

jobs:
  async-timeout-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      
      - name: Check Async Timeouts
        run: |
          python scripts/ci/auto_fix_common_issues.py \
            --pattern 37 \
            --check-only \
            --json-output .codex/p37-report.json
      
      - name: Fail if Issues Found
        run: |
          if grep -q '"issues_found": 0' .codex/p37-report.json; then
            echo "✅ No async timeout issues"
          else
            echo "⚠️  Async timeouts issues detected"
            exit 1
          fi
```

### Pattern 36 (Assert Messages) - Graduated Deployment

```yaml
name: Pattern 36 - Assert Messages (Staged)

on:
  schedule:
    - cron: '0 2 * * 1'  # Weekly, Monday 2 AM

jobs:
  assert-messages-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      
      # Week 1-2: Check-only (baseline)
      - name: Baseline Check
        run: |
          python scripts/ci/auto_fix_common_issues.py \
            --pattern 36 \
            --check-only \
            --json-output .codex/p36-baseline.json
      
      # Week 3-4: Dry-run (show what would change)
      - name: Dry-run (Week 3-4)
        if: github.run_number > 2
        run: |
          python scripts/ci/auto_fix_common_issues.py \
            --pattern 36 \
            --dry-run
      
      # Week 5+: Full auto-fix
      - name: Auto-fix (Week 5+)
        if: github.run_number > 4
        run: |
          python scripts/ci/auto_fix_common_issues.py \
            --pattern 36
```

### Pattern 38 (Mock Cleanup) - Conservative Rollout

```yaml
name: Pattern 38 - Mock Cleanup (Detection Only)

on:
  pull_request:
    paths:
      - 'tests/**/*.py'

jobs:
  mock-cleanup-detect:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      
      - name: Detect Missing Cleanup
        run: |
          python scripts/ci/auto_fix_common_issues.py \
            --pattern 38 \
            --check-only \
            --json-output .codex/p38-report.json
      
      - name: Comment Results
        uses: actions/github-script@v7
        if: always()
        with:
          script: |
            const fs = require('fs');
            const report = JSON.parse(fs.readFileSync('.codex/p38-report.json'));
            const issues = report.pattern_results['38'].issues_found;
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `🔍 Mock Cleanup Analysis:\n- Issues detected: ${issues}\n- Recommendation: Manual review recommended`
            });
```

---

## Step 6: Performance Optimization

### Parallel Pattern Execution

```yaml
name: Run Patterns in Parallel

jobs:
  patterns:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        pattern: [36, 37, 38]
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      
      - name: Run Pattern ${{ matrix.pattern }}
        run: |
          python scripts/ci/auto_fix_common_issues.py \
            --pattern ${{ matrix.pattern }} \
            --check-only \
            --json-output .codex/p${{ matrix.pattern }}-report.json
      
      - name: Upload Report
        uses: actions/upload-artifact@v3
        with:
          name: pattern-p${{ matrix.pattern }}
          path: .codex/p${{ matrix.pattern }}-report.json
```

### Caching Strategy

```yaml
- name: Cache Pattern Execution
  uses: actions/cache@v3
  with:
    path: .codex/pattern-cache
    key: pattern-cache-${{ github.run_id }}
    restore-keys: |
      pattern-cache-
```

---

## Step 7: Troubleshooting

### Pattern Not Executing

**Issue:** Pattern shows "0 issues found" but expected more

**Solution:**
```bash
# Verify pattern is registered
python -c "
import sys
sys.path.insert(0, 'scripts/ci')
from auto_fix_common_issues import CommonIssueFixer
fixer = CommonIssueFixer(Path('.'))
# Check if tests/ directory exists
print('tests/ exists:', Path('tests').exists())
# Run with verbose output
"
```

### High False Positive Rate

**Issue:** False positive rate > 2%

**Solution:**
1. Review JSON report for patterns
2. Check specific files flagged as issues
3. Adjust pattern regex if needed
4. Update PATTERN_REGISTRY with tuning parameters

### Performance Degradation

**Issue:** Pattern execution time > 1 second

**Solution:**
```bash
# Profile pattern execution
python -m cProfile -s cumtime scripts/ci/auto_fix_common_issues.py \
  --pattern 37 \
  --dry-run > profile.txt

# Review slowest functions
head -20 profile.txt
```

### Cascade Detection

**Issue:** "Cascade detected" messages appearing

**Solution:**
```bash
# Disable cascade detection for specific pattern
export CODEX_SKIP_PATTERN_NUMS="36"
python scripts/ci/auto_fix_common_issues.py --pattern 37
```

---

## Reference: Complete Integration Example

### Full Workflow File

```yaml
name: Validate with CI Patterns

on:
  pull_request:
  push:
    branches: [main, develop]

jobs:
  patterns:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
          cache: "pip"
      
      # Priority: Pattern 37 (Async)
      - name: "Pattern 37: Async Timeouts"
        run: |
          python scripts/ci/auto_fix_common_issues.py \
            --pattern 37 \
            --json-output .codex/p37.json
        continue-on-error: true
      
      # Pattern 36 (Assertions)
      - name: "Pattern 36: Assert Messages"
        run: |
          python scripts/ci/auto_fix_common_issues.py \
            --pattern 36 \
            --dry-run \
            --json-output .codex/p36.json
        continue-on-error: true
      
      # Pattern 38 (Mocks)
      - name: "Pattern 38: Mock Cleanup"
        run: |
          python scripts/ci/auto_fix_common_issues.py \
            --pattern 38 \
            --check-only \
            --json-output .codex/p38.json
        continue-on-error: true
      
      # Collect metrics
      - name: Collect All Metrics
        if: always()
        run: |
          python scripts/ci/auto_fix_common_issues.py \
            --json-output .codex/all-patterns.json
      
      # Upload results
      - uses: actions/upload-artifact@v3
        if: always()
        with:
          name: pattern-reports
          path: .codex/*.json
```

---

## Support and Escalation

### For Questions

- **Pattern Implementation:** Review `.codex/PHASE_5_CI_PATTERNS.md`
- **Validation Results:** See `.codex/PHASE_5_CI_PATTERNS_VALIDATION_REPORT.md`
- **Deployment:** Reference `.codex/PHASE_5_CI_DEPLOYMENT_CHECKLIST.md`

### For Issues

1. Check troubleshooting section (above)
2. Review GitHub Actions logs
3. File issue with pattern metrics attached
4. Escalate to @mbaetiong if needed

### For Optimization

- Collect execution metrics weekly
- Review JSON reports for performance trends
- Propose pattern tuning in bi-weekly sync

---

**Integration Guide Version:** 1.0  
**Last Updated:** 2026-07-09  
**Authority:** Phase 5 Execution Mandate (@mbaetiong)
