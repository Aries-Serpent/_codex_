# Issue #5029 Validation Checklist

**Status:** AWAITING PHASE 1 EXECUTION
**Created:** 2026-06-21T01:35:56Z
**Owner:** @mbaetiong

---

## Phase 1 Validation (Immediate Fixes)

### Progressive-Validation.yml Fixes

#### Smoke Tests
- [ ] Run manual workflow trigger on PR with small changes
- [ ] Verify "Install dependencies with validation" step completes
- [ ] Check that setuptools is pinned `<82` in pip freeze output
- [ ] Verify no "conflict" or "error" messages in install step
- [ ] Test passes with 0 test skips

```bash
# Manual test
gh workflow run progressive-validation.yml \
  --ref test-branch \
  -f test_size=small \
  --wait
```

#### Test Tier Selection
- [ ] Small PR: only smoke tests run
- [ ] Medium PR: smoke + unit tests run
- [ ] Large PR: smoke + unit + integration tests run
- [ ] No test tier executes if files don't exist (validation step prevents)

```bash
# Check test tier output
gh run view <RUN_ID> --log | grep -i "Required test files"
```

#### Error Propagation
- [ ] Pip install failure outputs full error message
- [ ] Test tier failures don't silently succeed
- [ ] Exit codes propagate correctly to downstream steps
- [ ] PR shows "FAILED" when any step fails (no silent success)

#### Success Metrics
- [ ] 0 failures in 5 consecutive PR cycles (varied sizes)
- [ ] Average execution time: < 3 minutes
- [ ] Cache hit rate: > 85%

---

### Auto-Fix-PR-Check.yml Fixes

#### Git Race Condition Prevention
- [ ] Protected branch check runs before commit
- [ ] No direct commits to `main`, `0D_base_`, or `release/*` branches
- [ ] Feature branch receives auto-fix commits successfully

```bash
# Test branch safety
git checkout -b feature/test-auto-fix
# Make changes to test files
git commit -am "test changes"
gh workflow run auto-fix-pr-check.yml --ref feature/test-auto-fix --wait
# Verify commit was pushed
git log origin/feature/test-auto-fix | head -5
```

#### Rebase Fallback Logic
- [ ] Git push fails gracefully (not hung or timeout)
- [ ] Rebase succeeds when main moved forward
- [ ] Up to 3 retries attempted before giving up
- [ ] Conflict scenario detected and reported

```bash
# Simulate race condition
# 1. Start workflow
# 2. While running, push new commit to main
# 3. Verify workflow detects and rebases
gh run view <RUN_ID> --log | grep -E "attempt|rebase|push"
```

#### Push Success Rate
- [ ] 100% push success in 20 consecutive PR cycles
- [ ] No "Updates were rejected" errors
- [ ] No timeouts on push operations
- [ ] MTTR < 1 minute for recovery

#### Success Metrics
- [ ] 0 push failures in 10 PR cycles
- [ ] Average push time: < 30 seconds
- [ ] Rebase success rate (when triggered): 100%

---

### Security-Scanning-Suite.yml Fixes

#### Cache Key Stability
- [ ] Cache key identical for same requirements.txt + workflow.yml
- [ ] Cache key changes when requirements.txt changes
- [ ] No random/dynamic elements in key (no torch=true/false variants)

```bash
# Check cache key stability
gh workflow run security-scanning-suite.yml --ref main --wait
CACHE_KEY_1=$(gh run view <RUN_ID> --log | grep "cache_key=" | head -1)

# Run again without changes
gh workflow run security-scanning-suite.yml --ref main --wait
CACHE_KEY_2=$(gh run view <RUN_ID> --log | grep "cache_key=" | head -1)

# Compare
[ "$CACHE_KEY_1" = "$CACHE_KEY_2" ] && echo "✅ Cache key stable" || echo "❌ Cache key unstable"
```

#### Tool Sequencing
- [ ] CodeQL scan runs first (no deps)
- [ ] Semgrep scan waits for CodeQL completion
- [ ] Dependency scan waits for Semgrep completion
- [ ] No parallel execution of analysis tools

```bash
gh run view <RUN_ID> --log | grep -E "CodeQL|Semgrep|Dependency" | head -20
# Verify order: CodeQL start → CodeQL end → Semgrep start → ...
```

#### Cache Hit Performance
- [ ] Cache hit rate: > 90% (was 65%)
- [ ] OOM errors: < 1% (was 15%)
- [ ] Tool timeout errors: < 1% (was 5%)
- [ ] Average execution time: < 20 minutes (was 45 min)

```bash
# Query cache statistics
gh run list --workflow security-scanning-suite.yml --limit 50 --json conclusion,duration \
  | jq '[.[] | select(.conclusion == "success")] | length as $total | {
    success: ., 
    rate: ($total / length)
  }'
```

#### Success Metrics
- [ ] Cache hit rate > 90% (sustained)
- [ ] 0 OOM failures in 10 runs
- [ ] < 20 minute execution time (consistent)
- [ ] 0 tool timing conflicts

---

## Phase 2 Validation (Copilot Integration)

### Dependency Prediction Engine

#### Prediction Accuracy
- [ ] Trained on 100+ prior PR cycles
- [ ] Accuracy > 75% on test set
- [ ] No false positives on clean PRs
- [ ] Correctly identifies torch/setuptools conflicts

```bash
# Test on PR with setuptools change
# Create test PR changing requirements to setuptools==82
gh pr create --title "test: bump setuptools to 82" --body "test"
# Prediction should flag this as risky
```

#### Integration Test
- [ ] Prediction step executes in < 30 seconds
- [ ] Outputs saved to GitHub outputs
- [ ] Suggested pins match actual conflicts (when they occur)
- [ ] Graceful degradation if API unavailable

#### Success Metrics
- [ ] Prediction accuracy > 75%
- [ ] Execution time < 30 seconds
- [ ] Zero false positives on 20 test PRs

---

### Conflict Resolution Engine

#### Detection Accuracy
- [ ] All merge conflicts detected (100%)
- [ ] Conflicted files listed correctly
- [ ] Conflict count matches actual files
- [ ] No false positives

```bash
# Test with known conflict scenario
# Push PR that will conflict with main when main updates
git push --force  # simulate main moving forward
# Verify all conflicts detected
```

#### Resolution Suggestion Accuracy
- [ ] Suggests resolution for 80%+ of conflicts
- [ ] No data loss in suggested resolutions
- [ ] Suggestions preserve both sides' changes (merge strategy)
- [ ] Manual review flagged for complex conflicts

#### Success Metrics
- [ ] 100% conflict detection
- [ ] 80% resolution suggestion rate
- [ ] 0% data loss cases

---

### Cache Prediction Engine

#### Prediction Accuracy
- [ ] Hit probability > 80% for no-dependency-change PRs
- [ ] Hit probability < 50% for torch/setuptools changes
- [ ] Risky package identification 100% accurate

```bash
# Test predictions across various scenarios
for i in {1..10}; do
  gh workflow run security-scanning-suite.yml --ref test-branch-$i --wait
  gh run view $(gh run list --workflow security-scanning-suite.yml -L 1 --json databaseId -q .[0].databaseId) --log | grep "cache_hit_probability"
done
```

#### Performance Impact
- [ ] Prediction job < 2 minutes
- [ ] No delay in main scanning workflows
- [ ] Graceful degradation if unavailable

#### Success Metrics
- [ ] Prediction accuracy > 80%
- [ ] Overhead < 2 minutes
- [ ] Zero API failures with graceful fallback

---

## Phase 3 Validation (Monitoring & Success Metrics)

### Baseline Metrics Collection
- [ ] `.codex/ISSUE_5029_METRICS.json` created with pre-fix baseline
- [ ] Current state captured: failure rates, execution times, cache performance
- [ ] Metrics point to specific workflow runs for audit trail

```json
{
  "baseline": {
    "timestamp": "2026-06-21T01:35:56Z",
    "progressive_validation": {
      "failure_rate": 0.80,
      "avg_duration_minutes": 8.5,
      "cache_hit_rate": 0.65,
      "sample_size": 25,
      "last_5_runs": ["run_id_1", "run_id_2", ...]
    },
    "auto_fix_pr_check": {
      "failure_rate": 1.0,
      "push_failure_rate": 1.0,
      "avg_duration_minutes": 4.2,
      "sample_size": 1
    },
    "security_scanning": {
      "failure_rate": 0.85,
      "cache_hit_rate": 0.65,
      "oom_error_rate": 0.15,
      "avg_duration_minutes": 45,
      "sample_size": 22
    }
  },
  "target_metrics": {
    "progressive_validation": {
      "failure_rate": 0.0,
      "cache_hit_rate": 0.95,
      "avg_duration_minutes": 3.0
    },
    "auto_fix_pr_check": {
      "failure_rate": 0.0,
      "push_failure_rate": 0.0
    },
    "security_scanning": {
      "failure_rate": 0.03,
      "cache_hit_rate": 0.95,
      "oom_error_rate": 0.0,
      "avg_duration_minutes": 18
    }
  }
}
```

### Monitoring Dashboard
- [ ] Daily metrics collected in `.codex/` (not /tmp)
- [ ] Alert threshold: failure_rate > 0.05
- [ ] SLO tracking: 99.5% uptime
- [ ] Trend analysis: weekly review

```bash
# Create daily monitor job
cat > /tmp/monitor_issue_5029.sh << 'MONITOR'
#!/bin/bash
TIMESTAMP=$(date -u +'%Y-%m-%dT%H:%M:%SZ')

# Query recent runs
PROG_FAIL=$(gh run list --workflow progressive-validation.yml -L 20 --json conclusion | jq 'map(select(.conclusion == "failure")) | length')
AUTO_FAIL=$(gh run list --workflow auto-fix-pr-check.yml -L 20 --json conclusion | jq 'map(select(.conclusion == "failure")) | length')
SEC_FAIL=$(gh run list --workflow security-scanning-suite.yml -L 20 --json conclusion | jq 'map(select(.conclusion == "failure")) | length')

echo "Progressive-validation: $PROG_FAIL failures in last 20 runs"
echo "Auto-fix-pr-check: $AUTO_FAIL failures in last 20 runs"
echo "Security-scanning: $SEC_FAIL failures in last 20 runs"

# Alert if threshold exceeded
[ $PROG_FAIL -gt 1 ] && echo "⚠️ ALERT: progressive-validation failure rate high"
[ $AUTO_FAIL -gt 0 ] && echo "⚠️ ALERT: auto-fix-pr-check failures detected"
[ $SEC_FAIL -gt 0 ] && echo "⚠️ ALERT: security-scanning failures detected"
MONITOR

chmod +x /tmp/monitor_issue_5029.sh
```

### Success Criteria (48-hour period)
- [ ] Progressive-validation: 0% failures
- [ ] Auto-fix-pr-check: 0% failures
- [ ] Security-scanning-suite: < 3% failures (natural flakiness)
- [ ] All fixes validated by @mbaetiong

---

## Rollback Procedures

### Phase 1 Rollback (Immediate)
If any Phase 1 fix causes regressions:

```bash
# 1. Identify failing commit
git log -1 --oneline

# 2. Revert specific workflow file
git revert <commit_sha>
# or
git checkout <main_branch> -- .github/workflows/<workflow>.yml

# 3. Force push to disable (if urgent)
git checkout main
git pull --rebase origin main

# 4. Notify @mbaetiong
gh issue comment -R Aries-Serpent/_codex_ <issue_number> \
  --body "🚨 Phase 1 Rollback: <workflow> reverted due to regression"
```

### Phase 2 Rollback (Copilot Integration)
If Copilot integrations cause issues:

```bash
# 1. Disable Copilot prediction steps
# In workflows, set: if: false for prediction steps

# 2. Keep Phase 1 fixes (they're stable)

# 3. Iterate on Copilot integration
```

### Full Rollback (All Phases)
If everything must be reverted:

```bash
# 1. Revert all Issue #5029 commits
git log --grep="5029" --oneline | head -20
for commit in $(git log --grep="5029" --format="%H" | head -20); do
  git revert $commit --no-edit
done

# 2. Restore original workflows from main
git checkout main -- .github/workflows/

# 3. Push rollback
git push origin HEAD:refs/heads/rollback-5029
```

---

## Sign-Off Checklist

### For @mbaetiong

- [ ] All Phase 1 fixes reviewed and approved
- [ ] Test results showing improvement
- [ ] Metrics baseline established
- [ ] Rollback procedures tested
- [ ] Phase 2 Copilot integration approved
- [ ] Monitoring dashboard set up
- [ ] Final validation complete

### For Lead Agent

- [ ] All Phase 1 PRs merged without conflicts
- [ ] All validation tests passing
- [ ] Metrics collected for 48+ hours
- [ ] Rollback plan confirmed with @mbaetiong
- [ ] Documentation updated
- [ ] Success criteria met

---

## Status Tracking

| Phase | Task | Owner | Status | Due | Notes |
|-------|------|-------|--------|-----|-------|
| 1 | progressive-validation.yml | autonomous-test-healer | 🟠 PENDING | 2026-06-21 13:00Z | - |
| 1 | auto-fix-pr-check.yml | ci-auto-healer | 🟠 PENDING | 2026-06-21 13:00Z | - |
| 1 | security-scanning-suite.yml | unified-security-scanner | 🟠 PENDING | 2026-06-21 13:00Z | - |
| 2 | Dependency Prediction | cognitive-brain-cli | 🟠 PENDING | 2026-06-22 11:00Z | - |
| 2 | Conflict Resolution | cognitive-brain-cli | 🟠 PENDING | 2026-06-22 11:00Z | - |
| 2 | Cache Prediction | cache-management | 🟠 PENDING | 2026-06-22 11:00Z | - |
| 3 | Baseline Metrics | artifact-monitor | 🟠 PENDING | 2026-06-23 08:00Z | - |
| 3 | Validation Checklist | governance-gate | 🟠 PENDING | 2026-06-23 08:00Z | - |

---

**Created:** 2026-06-21T01:35:56Z
**Status:** AWAITING PHASE 1 EXECUTION
**Next Step:** @mbaetiong reviews and approves agent delegation
