# Phase 5 CI Patterns Deployment Checklist

**Document Date:** 2026-07-09  
**Phase:** Phase 5 Week 2  
**Scope:** Production Deployment of RP-031, RP-032, RP-033  
**Authority:** Phase 5 Execution Mandate (@mbaetiong)

---

## Pre-Deployment Verification

### Code Quality Gates

- [ ] All patterns implemented and integrated
- [ ] `scripts/ci/auto_fix_common_issues.py` updated with patterns 36-38
- [ ] CLI argument range updated to 1-38
- [ ] All docstrings complete and accurate
- [ ] No breaking changes to existing patterns 1-35
- [ ] Type hints present on all new functions

**Verification Command:**
```bash
python -m mypy scripts/ci/auto_fix_common_issues.py --ignore-missing-imports
```

### Testing Gates

- [ ] Unit tests passing: `pytest tests/ci/test_rp031_assert_messages.py -v`
- [ ] Unit tests passing: `pytest tests/ci/test_rp032_async_timeout.py -v`
- [ ] Unit tests passing: `pytest tests/ci/test_rp033_mock_cleanup.py -v`
- [ ] All 64 tests pass (RP-031: 21, RP-032: 22, RP-033: 21)
- [ ] No test flakiness observed (run 3x to verify)
- [ ] Edge cases covered

**Verification Command:**
```bash
pytest tests/ci/test_rp0{31,32,33}*.py -v --tb=short
```

### Integration Gates

- [ ] Patterns registered in `run_all_patterns()` method
- [ ] Pattern numbers verified (36, 37, 38)
- [ ] Help text updated in module docstring
- [ ] Pattern-to-function mapping verified
- [ ] No duplicate pattern IDs with existing patterns 1-35
- [ ] JSON report generation includes patterns 36-38

**Verification Command:**
```bash
python scripts/ci/auto_fix_common_issues.py --help | grep -A 5 "Pattern\|--pattern"
```

### Validation Gates

- [ ] RP-031: False positive rate confirmed <2%
- [ ] RP-032: False positive rate confirmed 0%
- [ ] RP-033: False positive rate confirmed <2%
- [ ] Performance: All patterns execute within <150ms SLA
- [ ] Cascade detection: No infinite loops or cascading fixes
- [ ] Error handling: All edge cases handled gracefully

**Verification Command:**
```bash
time python scripts/ci/auto_fix_common_issues.py --pattern 36 --dry-run
time python scripts/ci/auto_fix_common_issues.py --pattern 37 --dry-run
time python scripts/ci/auto_fix_common_issues.py --pattern 38 --dry-run
```

---

## Pre-Deployment Checks

### Repository State

- [ ] Working tree clean (`git status` shows nothing)
- [ ] No uncommitted pattern changes
- [ ] Branch is `copilot/post-merge-validation-setup` or production branch
- [ ] Upstream is current (no commits behind)

**Verification Command:**
```bash
git status
git log --oneline -5
```

### Coverage Verification

- [ ] Coverage at 38.86%+ (from Phase 1 baseline)
- [ ] No regressions in existing test suite
- [ ] All patterns 1-35 still passing

**Verification Command:**
```bash
coverage run --parallel-mode -m pytest tests/ -q
coverage report --fail-under=38.86
```

### Dependency Verification

- [ ] Python 3.8+ available
- [ ] All pattern dependencies installed
- [ ] No new external dependencies added
- [ ] pathlib, re, os modules available (standard library)

**Verification Command:**
```bash
python --version
python -c "import re, pathlib, os; print('Dependencies OK')"
```

---

## CI Pipeline Integration

### GitHub Actions Setup

#### Step 1: Add to Workflow File

**Location:** `.github/workflows/validate.yml` or equivalent

```yaml
- name: Run CI Auto-Fixer (Patterns 36-38)
  run: |
    python scripts/ci/auto_fix_common_issues.py \
      --pattern 37 \
      --check-only
  continue-on-error: true
```

**Integration Order:**
1. Run with `--check-only` first (validation only, no writes)
2. Verify 0 issues or acceptable baseline
3. Then enable `--dry-run` for staging
4. Finally enable auto-fix when confident

#### Step 2: Add JSON Report Collection

```yaml
- name: Collect Pattern Metrics
  run: |
    python scripts/ci/auto_fix_common_issues.py \
      --json-output .codex/patterns-report.json
      
- name: Archive Pattern Report
  uses: actions/upload-artifact@v3
  with:
    name: pattern-metrics
    path: .codex/patterns-report.json
```

#### Step 3: Add Alert Thresholds

**Alert Condition:** Pattern execution fails or false positive rate > 5%

```yaml
- name: Check Pattern Metrics
  run: |
    if [ -f .codex/patterns-report.json ]; then
      python -c "
        import json
        with open('.codex/patterns-report.json') as f:
          data = json.load(f)
        false_pos = data.get('false_positive_rate', 0)
        if false_pos > 0.05:
          print(f'WARNING: High false positive rate: {false_pos}')
          exit(1)
      "
    fi
```

### Rollout Strategy

#### Phase 1: Validation Only (Week 1)

```bash
python scripts/ci/auto_fix_common_issues.py \
  --pattern 37 \
  --check-only
```

- Runs pattern without modifications
- Reports issues found
- Allows verification of baseline
- Duration: 1 week

**Success Criteria:** No unexpected issues, false positive rate <5%

#### Phase 2: Dry Run (Week 2)

```bash
python scripts/ci/auto_fix_common_issues.py \
  --pattern 37 \
  --dry-run
```

- Shows what would be changed
- No actual modifications
- Tests fix logic
- Duration: 1 week

**Success Criteria:** All proposed changes are sensible

#### Phase 3: Auto-Fix Enabled (Week 3+)

```bash
python scripts/ci/auto_fix_common_issues.py \
  --pattern 37
```

- Automatically applies fixes
- Commits changes if fixes applied
- Enables full pattern automation
- Duration: Ongoing

**Success Criteria:** CI success rate improves, no regressions

### Monitoring Integration

#### Metric Collection

Create `.codex/PHASE_5_CI_PATTERN_METRICS.md`:

```markdown
# CI Pattern Metrics (Week 1-N)

## RP-032 (Async Timeouts)
- Detections: X
- Auto-fixes: Y
- False positives: 0
- Avg execution: Zms

## RP-031 (Assert Messages)  
- Detections: X
- Auto-fixes: Y
- False positives: <2%
- Avg execution: Zms

## RP-033 (Mock Cleanup)
- Detections: X
- Auto-fixes: Y
- False positives: <2%
- Avg execution: Zms
```

#### Alert Thresholds

| Metric | Threshold | Action |
|--------|-----------|--------|
| False positive rate | >5% | Pause deployment, investigate |
| Execution time | >500ms | Optimize, consider parallel execution |
| Crash/error rate | >1% | Rollback, debug |
| CI job failure | Yes | Rollback, investigate |

---

## Rollback Procedures

### If Pattern Causes Issues

**Step 1: Immediate Halt**
```bash
# Disable pattern in CI workflow
# Set environment variable
export CODEX_SKIP_PATTERN_NUMS="36,37,38"
```

**Step 2: Revert Changes**
```bash
# If auto-fix was enabled, revert recent commits
git revert HEAD~1  # Adjust based on how many commits were made

# Or use git restore if changes not yet committed
git restore <affected_files>
```

**Step 3: Investigation**
```bash
# Check pattern logs
grep -r "Pattern [36-38]" .codex/ *.log

# Review git diff of pattern changes
git diff HEAD~5
```

**Step 4: Root Cause Analysis**

Document in `.codex/PHASE_5_CI_ROLLBACK_<date>.md`:
- What went wrong
- Which pattern failed
- What triggers the failure
- Recommended fix

**Step 5: Re-enable**

After fix:
```bash
# Test locally first
python scripts/ci/auto_fix_common_issues.py --pattern XX --dry-run

# Then update CI workflow and re-deploy
```

### Full Rollback to Previous Release

```bash
# If entire pattern set needs rollback
git revert <commit_id>  # Revert integration commit

# Update CI workflow to remove patterns 36-38
vim .github/workflows/validate.yml

git commit -m "Rollback: Disable patterns 36-38 pending investigation"
git push
```

---

## Post-Deployment Validation

### Immediate Checks (Day 1)

- [ ] CI jobs complete without errors
- [ ] Pattern output appears in logs as expected
- [ ] No unexpected file modifications
- [ ] All existing tests still passing
- [ ] Performance metrics within SLA

**Verification Command:**
```bash
# Check recent workflow runs
gh workflow run validate.yml
gh run view <run_id> --log
```

### Short-term Monitoring (Week 1)

- [ ] Pattern execution stable across multiple runs
- [ ] False positive rate remains low (<2-5%)
- [ ] Fixes are sensible and correct
- [ ] No cascading issues between patterns

**Weekly Review Task:**
1. Collect metrics from JSON reports
2. Review false positive samples
3. Update `.codex/PHASE_5_CI_PATTERN_METRICS.md`
4. Report to @mbaetiong

### Medium-term Monitoring (Ongoing)

- [ ] CI success rate trends up
- [ ] Test flakiness reduced (target: 10%+ improvement)
- [ ] Pattern effectiveness aligns with predictions
- [ ] User feedback collected and addressed

**Monthly Review:** 
- Analyze pattern effectiveness
- Identify optimization opportunities
- Plan for Pattern 39+ additions

---

## Communication Plan

### Pre-Deployment (48 hours before)

Notify:
- Engineering leads
- QA team
- DevOps/CI team

Message:
```
CI Patterns 36-38 deploying in 48 hours:
- RP-032 (Async Timeouts): 0% false positive rate
- RP-031 (Assert Messages): <2% false positive rate  
- RP-033 (Mock Cleanup): <2% false positive rate

Validation report: .codex/PHASE_5_CI_PATTERNS_VALIDATION_REPORT.md
Deployment guide: .codex/PHASE_5_CI_DEPLOYMENT_CHECKLIST.md
```

### Post-Deployment (Day 1)

Status Update:
```
✅ CI Patterns 36-38 successfully deployed

Monitoring active:
- Pattern 37 (Async): Check-only mode, 0 issues
- Pattern 36 (Asserts): Check-only mode, baseline established
- Pattern 38 (Cleanup): Check-only mode, baseline established

Next: Transition to dry-run in 1 week
```

### Weekly Updates

Report to @mbaetiong:
- Metrics collected
- Issues encountered
- Recommended actions

---

## Sign-Off

### Pre-Deployment Approval

- [ ] QA Lead: Approves testing results
- [ ] DevOps: Confirms CI integration ready
- [ ] Engineering Lead: Approves for production
- [ ] Phase 5 Authority (@mbaetiong): Final approval

### Deployment Authorization

**Authorized By:** [Fill in name/date]  
**Date:** [Fill in date]  
**Deployment Status:** ✅ APPROVED FOR PRODUCTION

---

## Appendix: Quick Reference

### Pattern Deployment Commands

```bash
# Pattern 36 - Assert Messages
python scripts/ci/auto_fix_common_issues.py --pattern 36 --check-only
python scripts/ci/auto_fix_common_issues.py --pattern 36 --dry-run

# Pattern 37 - Async Timeouts (highest priority)
python scripts/ci/auto_fix_common_issues.py --pattern 37 --check-only
python scripts/ci/auto_fix_common_issues.py --pattern 37 --dry-run

# Pattern 38 - Mock Cleanup
python scripts/ci/auto_fix_common_issues.py --pattern 38 --check-only
python scripts/ci/auto_fix_common_issues.py --pattern 38 --dry-run

# All patterns
python scripts/ci/auto_fix_common_issues.py --check-only
python scripts/ci/auto_fix_common_issues.py --dry-run
python scripts/ci/auto_fix_common_issues.py  # Full auto-fix
```

### Monitoring Commands

```bash
# Generate metrics report
python scripts/ci/auto_fix_common_issues.py \
  --json-output .codex/metrics.json

# View latest metrics
cat .codex/metrics.json | python -m json.tool
```

### Rollback Commands

```bash
# Disable specific patterns
export CODEX_SKIP_PATTERN_NUMS="36,37,38"

# Revert changes
git revert HEAD~1

# Check status
git log --oneline -5
git diff HEAD~1
```

---

**Checklist Version:** 1.0  
**Last Updated:** 2026-07-09  
**Next Review:** 2026-07-16
