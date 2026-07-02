# Coverage Monitoring Rollback & Recovery Procedures
## Phase 5 - Contingency Planning

**Created:** 2026-07-02T02:25:00Z  
**Status:** CONTINGENCY PROCEDURES DOCUMENTED  
**Activation Condition:** Only if baseline verification fails or agent integration fails

---

## Overview

This document outlines detailed recovery procedures for each failure scenario during baseline stability verification (Days 1-7) and Phase 1 progression (Days 8+).

**Key Principle:** All Phase 0 core components remain stable regardless of failures in later phases. The monitoring system can be rolled back gracefully without disrupting development.

---

## Severity Levels

### CRITICAL (⛔ Block All Progression)
- Baseline regression >3% from 34.63%
- Module Tier 1 (Security) loses >1% coverage
- Data corruption in BASELINE_HISTORY.ndjson
- CI workflow completely broken

**Action:** Immediate escalation to @mbaetiong, pause all phase progression

### HIGH (⚠️ Pause & Investigate)
- Baseline regression 1.5%-3%
- Module Tier 2 (Auth) loses >1.5%
- Module Tier 3/4 loses >2%
- Validation test suite >50% failures

**Action:** Pause progression, investigate root cause, fix, re-verify for 1 day

### MEDIUM (🔶 Monitor & Track)
- Baseline variance ±0.5%-1.5%
- Quality metrics drop >1%
- Single validation test flaky
- Dashboard generation slow (>10s)

**Action:** Monitor closely, document, adjust if pattern emerges

### LOW (ℹ️ Note & Continue)
- Baseline variance ±0.5% or less
- Isolated test failures
- Minor dashboard UI issues
- Non-blocking warnings

**Action:** Document, continue monitoring, address in next iteration

---

## Scenario 1: Coverage Regression >1.5% (CRITICAL)

### Trigger
```
Coverage drops from 34.63% to 32.80% (-1.83%)
OR
Coverage drops from 34.63% to below 33.13% (acceptable minimum)
```

### Immediate Response (First 15 minutes)

**Step 1: Halt Progression**
```bash
# Stop all CI workflows (no new test merges)
gh workflow disable coverage-ratchet
gh workflow disable coverage-baseline-weekly

# Create emergency issue
gh issue create \
  --title "🚨 CRITICAL: Coverage Regression >1.5% — Baseline Verification Paused" \
  --label "coverage-critical,type:incident" \
  --body "Coverage dropped to X% (variance: -X%). All Phase 1 progression HALTED pending investigation."
```

**Step 2: Notify Stakeholders**
```bash
# Notify @mbaetiong immediately
cat > regression_alert.md << 'EOF'
# CRITICAL REGRESSION ALERT

**Coverage:** 32.80% (from 34.63%)  
**Variance:** -1.83% (EXCEEDS THRESHOLD)  
**Status:** 🛑 PAUSED  
**Action Required:** Immediate investigation by @mbaetiong

## Details
- Baseline locked: 34.63%
- Acceptable minimum: 33.13%
- Current: 32.80%
- Variance: -1.83% (exceeds ±1.5% threshold)

## Next Steps
1. Identify root cause (code change or test issue)
2. Determine if regression is real or measurement artifact
3. Decide: Fix vs. Rollback
4. Re-verify baseline for 1 day minimum
EOF

gh issue create \
  --title "URGENT: Coverage regression >1.5% — @mbaetiong approval required" \
  --assignee mbaetiong \
  --label "coverage-critical" \
  --body-file regression_alert.md
```

**Step 3: Capture Failure Diagnostics**
```bash
# Generate detailed diagnostics
python scripts/ci/diagnose_regression.py \
  --history .codex/coverage/BASELINE_HISTORY.ndjson \
  --output regression_diagnostics.json

# Identify which test/code change caused regression
python scripts/ci/identify_regression_cause.py \
  --last-pass <last_passing_commit> \
  --first-fail <first_failing_commit> \
  --output cause_analysis.json
```

**Expected Output:**
```json
{
  "regression_severity": "CRITICAL",
  "coverage_drop_pct": 1.83,
  "first_failing_commit": "abc1234def567",
  "failing_test_files": [
    "tests/validation/test_coverage_verification.py",
    "tests/module/test_security_core.py"
  ],
  "probable_cause": "Recent PR merged code without test coverage",
  "recommendations": [
    "Revert commits abc1234 and def567",
    "Re-add tests for changed code",
    "Re-run baseline verification"
  ]
}
```

### Investigation Phase (15 minutes - 2 hours)

**Step 4: Analyze Root Cause**
```bash
# Option A: Code regression (actual loss of coverage)
if [[ "$CAUSE" == "code_change" ]]; then
  echo "Root cause: Code changed without accompanying tests"
  
  # Identify which files changed
  git diff abc1234~1 abc1234 --name-only > changed_files.txt
  
  # Check if tests were added for changed code
  python scripts/ci/check_test_coverage_for_changes.py \
    --changed-files changed_files.txt \
    --coverage-xml coverage.xml
fi

# Option B: Test issue (flaky test, wrong baseline)
if [[ "$CAUSE" == "test_issue" ]]; then
  echo "Root cause: Test failure or baseline measurement issue"
  
  # Re-run failing tests individually to check flakiness
  python -m pytest tests/validation/test_coverage_verification.py::test_baseline_coverage_pct -v --count=5
fi

# Option C: CI environment issue
if [[ "$CAUSE" == "ci_environment" ]]; then
  echo "Root cause: CI environment (timeouts, memory, dependencies)"
  
  # Check CI logs for errors
  gh run view <run_id> --log | grep -i "error\|warning\|timeout"
fi
```

### Decision Point (At 2 hours)

**Decision A: Real Code Regression (MOST LIKELY)**
→ Proceed to Recovery Path A (Rollback & Re-test)

**Decision B: Test Infrastructure Issue**
→ Proceed to Recovery Path B (Fix Tests & Re-verify)

**Decision C: CI Environment Problem**
→ Proceed to Recovery Path C (Fix Environment & Re-run)

---

## Recovery Path A: Code Regression Rollback

### Step 1: Identify Problematic Commit(s)
```bash
# Get commit hash of failing code
FAIL_COMMIT=$(git log -1 --pretty=%H)
echo "First failing commit: $FAIL_COMMIT"

# Verify what changed
git show $FAIL_COMMIT --stat

# Count how many commits back we need to go
git log --oneline abc1234 | head -20
```

### Step 2: Revert Changes
```bash
# Option 1: Revert single commit
git revert $FAIL_COMMIT --no-edit
git push origin HEAD:coverage-baseline-monitoring

# Option 2: Revert last 5 commits (if multiple suspects)
git revert HEAD~4..HEAD --no-edit
git push origin HEAD:coverage-baseline-monitoring

# Option 3: Force rollback to known good commit
git reset --hard <last_passing_commit>
git push origin HEAD:coverage-baseline-monitoring -f
```

### Step 3: Re-run Baseline Verification
```bash
# Run full test suite
python -m pytest tests/ \
  --cov=src \
  --cov-report=xml:coverage.xml \
  --cov-fail-under=34.13 \
  -v

# Generate tracking report
python scripts/ci/generate_baseline_tracking_report.py \
  --coverage-xml coverage.xml \
  --baseline .codex/COVERAGE_BASELINE_34_63.json \
  --output .codex/coverage/BASELINE_TRACKING_REPORT.json

# Check result
python scripts/ci/check_baseline_restored.py \
  --report .codex/coverage/BASELINE_TRACKING_REPORT.json
```

**Expected Output:** ✅ "Coverage restored to 34.63% ±1.5%"

### Step 4: Verify 1-Day Stability
```bash
# After rollback, verify baseline stable for 1 full day
# before resuming Phase 1 progression

# Day 1 monitoring:
# - Run tests every 2 hours
# - Capture coverage metrics
# - Check for regressions
# - Verify quality metrics

# If stable for 24 hours:
echo "✅ Baseline re-verified. Phase 1 progression can resume."

# Document incident
cat > incident_report.md << 'EOF'
# Incident Report: Coverage Regression

**Date:** 2026-07-03
**Duration:** 2 hours (detected & resolved)
**Root Cause:** [Code without tests / Test flakiness / CI issue]
**Action:** Reverted commits X-Y
**Verification:** 1 day re-test passed
**Lessons Learned:** [...]
EOF
```

### Step 5: Resume Phase 1 (Optional)

**Option 1: Resume with same timeline** (if quick fix)
- Resume test generation immediately
- Adjust timeline only if necessary

**Option 2: Extend timeline** (if significant re-work)
- Delay Phase 1 start by 3 days
- Allow buffer for additional testing

**Option 3: Reduce scope** (if recurring issues)
- Focus Phase 1 on Tier A only (8 modules, 600 tests)
- Defer Tiers B+C to Phase 2
- Reduce Phase 1 target to 37% instead of 40%

---

## Recovery Path B: Test Infrastructure Issue

### Step 1: Identify Flaky Test
```bash
# Run failing test 10 times
python -m pytest tests/validation/test_coverage_verification.py::test_baseline_coverage_pct -v --count=10

# Check for timing dependencies
python -m pytest tests/validation/ -v --timeout=120 --durations=10

# Check for isolation issues
python -m pytest tests/validation/ -v --random-order
```

**Expected Output:**
- **Consistently failing:** Real bug, fix it
- **Intermittently failing:** Timing/environment issue
- **Fails in isolation:** Shared state issue

### Step 2: Fix the Test
```bash
# If timing issue
# Add longer timeout, disable timeout, or restructure test

# If isolation issue
# Remove shared fixtures, reset state between tests

# If external dependency
# Mock the dependency, skip test if unavailable

# Example fix:
git diff -u tests/validation/test_flaky_test.py << 'EOF'
- @pytest.mark.timeout(1)  # Too short
+ @pytest.mark.timeout(10) # Increased tolerance

- def test_something():
+ @pytest.mark.flaky(reruns=3, reruns_delay=1)
+ def test_something():
    ...
EOF

git commit -am "Fix flaky test: increase timeout and add flaky decorator"
```

### Step 3: Re-run Test Suite
```bash
python -m pytest tests/ \
  --cov=src \
  --cov-report=xml:coverage.xml \
  -v

# Verify coverage restored
python scripts/ci/generate_baseline_tracking_report.py \
  --coverage-xml coverage.xml
```

### Step 4: Resume Monitoring
- Coverage should return to baseline
- If still failing: proceed to Recovery Path A (rollback)
- If fixed: resume Phase 1 immediately

---

## Recovery Path C: CI Environment Problem

### Step 1: Diagnose Environment Issue
```bash
# Check CI logs
gh run view <run_id> --log | head -100

# Common issues:
# - Timeout (increase timeout in workflow)
# - Memory (reduce parallel workers)
# - Dependency (update requirements)
# - Python version (verify 3.12.13)
# - Cache stale (clear cache)

# Check system resources
df -h              # Disk space
free -h            # Memory
uptime             # Load average
```

### Step 2: Fix Environment Issue

**For Timeout Issues:**
```yaml
# In coverage-ratchet.yml:
timeout-minutes: 30  # Increase from 20 to 30
pytest_timeout: 120  # seconds per test
```

**For Memory Issues:**
```bash
# Reduce parallel workers
pytest -n 2  # From -n 4 to -n 2
```

**For Dependency Issues:**
```bash
# Update requirements
pip install --upgrade pip
pip install -r requirements-dev.txt --upgrade

# Commit updated lock file
git add requirements.txt uv.lock
git commit -m "Update dependencies for CI stability"
```

**For Cache Issues:**
```yaml
# Clear GitHub Actions cache
# Via web UI: Settings → Actions → Caches → Delete
# Or via CLI:
gh api /repos/{owner}/{repo}/actions/caches --method DELETE
```

### Step 3: Re-run Test Suite
```bash
# Test in clean environment
rm -rf .coverage coverage.xml

python -m pytest tests/ \
  --cov=src \
  --cov-report=xml:coverage.xml \
  -v

# Check coverage restored
python scripts/ci/generate_baseline_tracking_report.py \
  --coverage-xml coverage.xml
```

### Step 4: Resume Monitoring
- If coverage restored: resume Phase 1
- If still failing: escalate to infrastructure team

---

## Scenario 2: Validation Tests Failing (HIGH)

### Trigger
```
>50% of validation tests failing
OR
Critical validation test consistently failing
```

### Immediate Response

**Step 1: Identify Failing Tests**
```bash
python -m pytest tests/validation/ -v \
  --tb=short \
  --json-report-file=validation_failures.json

# Parse failures
python scripts/ci/parse_test_failures.py \
  --json validation_failures.json \
  --output failure_summary.txt
```

**Example Failures:**
```
FAILED test_coverage_verification.py::test_baseline_coverage_pct
  AssertionError: 34.58 not within acceptable band (33.13, 36.13)

FAILED test_module_coverage_gates.py::test_tier_1_minimum
  AssertionError: Tier 1 coverage 89.8% < 90%

FAILED test_quality_metrics.py::test_pass_rate
  AssertionError: Pass rate 98.2% < 99.5%
```

### Step 2: Analyze Test Issues

**Option A: Tests are correct, code changed**
→ Proceed to Recovery Path A (rollback)

**Option B: Tests are flaky**
→ Proceed to Recovery Path B (fix tests)

**Option C: Tests outdated**
→ Update tests to match new behavior

```bash
# Decide which applies
if [[ "$(git diff main --name-only | grep -c 'tests/')" -eq 0 ]]; then
  echo "No test changes - likely code regression (Path A)"
else
  echo "Test changes detected - likely flaky tests (Path B)"
fi
```

### Step 3: Fix Issues
```bash
# Path A: Revert code changes
git revert <failing_commit>

# Path B: Fix test flakiness
# - Add timeouts
# - Fix dependencies
# - Reset shared state
# - Use fixtures properly

# Path C: Update validation tests
# - Adjust thresholds if intentional change
# - Add mocking for new dependencies
# - Document why test changed
```

### Step 4: Verify Resolution
```bash
python -m pytest tests/validation/ -v --count=3
# All tests should pass on first try, not flaky
```

---

## Scenario 3: Module Tier Minimum Breached (HIGH)

### Trigger
```
Tier 1 (Security) drops below 90%
OR
Tier 2 (Auth) drops below 85%
OR
Tier 3 (Infrastructure) drops below 76%
OR
Tier 4 (Extended) drops below 61%
```

### Immediate Response

**Step 1: Identify Affected Module**
```bash
python scripts/ci/identify_module_regression.py \
  --matrix .codex/coverage/MODULE_BASELINE_MATRIX.json \
  --baseline-matrix .codex/COVERAGE_BASELINE_34_63.json
```

**Example Output:**
```
REGRESSION DETECTED: Tier 2 (Auth Systems)
├─ module: user_store
├─ baseline: 87.5%
├─ current: 85.8%
├─ delta: -1.7%
└─ status: BREACHED (minimum: 85%)
```

**Step 2: Find Offending Commit**
```bash
# Get detailed change history for module
git log -p --follow -- src/auth/user_store.py | head -200

# Identify which change reduced coverage
python scripts/ci/find_coverage_loss_commit.py \
  --module user_store \
  --baseline-coverage 87.5 \
  --current-coverage 85.8
```

**Step 3: Decide: Revert or Add Tests**

**Option A: Revert** (code was wrong)
```bash
git revert <commit>
git push origin HEAD:coverage-baseline-monitoring
```

**Option B: Add Tests** (code is right, tests missing)
```bash
# Add tests to restore coverage
python scripts/ci/generate_gap_tests.py \
  --module user_store \
  --target-coverage 87.5 \
  --output tests/module/test_user_store_gap_fill.py

# Verify coverage restored
python -m pytest tests/module/test_user_store_gap_fill.py -v --cov=src/auth/user_store
```

### Step 4: Verify Module Restored
```bash
python scripts/ci/validate_module_gates.py \
  --matrix .codex/coverage/MODULE_BASELINE_MATRIX.json \
  --gates .codex/PHASE_VALIDATION_GATES.yaml
```

**Expected:** All tier minimums met

---

## Scenario 4: Quality Metrics Drop >1% (MEDIUM)

### Trigger
```
Test pass rate: 99.5% → 98.5% (-1.0%)
OR
Test flakiness: 0% → 1.5% (+1.5%)
OR
Test determinism: 100% → 98.5% (-1.5%)
```

### Immediate Response

**Step 1: Identify Problem**
```bash
# Run test suite and capture metrics
python -m pytest tests/ -v \
  --json-report-file=test_metrics.json

# Analyze what changed
python scripts/ci/analyze_quality_drop.py \
  --current tests/metrics.json \
  --baseline baseline_metrics.json \
  --output quality_analysis.json
```

**Example Analysis:**
```json
{
  "pass_rate_drop": -1.0,
  "flaky_tests": [
    "test_coverage_determinism.py::test_determinism_on_windows",
    "test_ci_workflow_validation.py::test_workflow_timeout"
  ],
  "likely_cause": "Newly added tests are flaky",
  "recommended_action": "Fix flaky tests or revert commits"
}
```

**Step 2: Fix Quality Issues**
```bash
# Option A: Revert changes
git revert <last_3_commits>

# Option B: Fix flaky tests
python scripts/ci/stabilize_flaky_tests.py \
  --tests "test_determinism.py" \
  --action "add_timeouts,increase_retries"

# Option C: Skip known-flaky tests temporarily
# Mark with @pytest.mark.flaky for CI to rerun
```

**Step 3: Verify Metrics Restored**
```bash
python -m pytest tests/ -v --count=3
# Run 3 times to ensure determinism
```

---

## Scenario 5: Agent Integration Failure

### Trigger
```
Escalation routing not working
OR
automated status comments not posting
OR
Dashboard generation failing
OR
Weekly reports not being created
```

### Recovery Action

**If Escalation Routing Fails:**
```bash
# Manual escalation
gh issue create \
  --title "🚨 Coverage Regression Detected" \
  --label "coverage-critical" \
  --body "Automated escalation failed. Manual escalation: $(cat escalation_details.md)"

# Notify @mbaetiong directly
# Send Slack message or email with regression details
```

**If Status Comments Fail:**
```bash
# Check workflow logs
gh run view <run_id> --log | grep -A 20 "Post PR comment"

# Fix issue (likely token/permission problem)
# Then re-run workflow manually
gh workflow run coverage-ratchet.yml
```

**If Dashboard Generation Fails:**
```bash
# Fall back to manual HTML generation
python scripts/ci/generate_dashboard_manual.py \
  --history .codex/coverage/BASELINE_HISTORY.ndjson \
  --output .codex/coverage/dashboard_backup.html

# Deploy manually
gh pages deploy .codex/coverage/
```

**If Weekly Reports Fail:**
```bash
# Disable automated reports
gh workflow disable coverage-baseline-weekly

# Manually trigger report generation
python scripts/ci/generate_weekly_summary.py \
  --history .codex/coverage/BASELINE_HISTORY.ndjson \
  --output WEEKLY_SUMMARY.md

# Post manually to Discussions
gh discussion create \
  --title "📊 Weekly Coverage Report" \
  --body-file WEEKLY_SUMMARY.md
```

---

## Decision Tree: What To Do When Baseline Verification Fails

```
Is coverage drop >1.5%?
├─ YES → CRITICAL (Go to Scenario 1)
│  ├─ Is it code change? → Rollback (Path A)
│  ├─ Is it test flakiness? → Fix tests (Path B)
│  └─ Is it CI environment? → Fix environment (Path C)
│
└─ NO (coverage within ±1.5%) → Go to Scenario 2-5
   ├─ Are validation tests failing? → Fix tests (Scenario 2)
   ├─ Are module tiers breached? → Add tests/revert (Scenario 3)
   ├─ Are quality metrics dropping? → Fix flakiness (Scenario 4)
   └─ Is an agent/feature failing? → Manual workaround (Scenario 5)
```

---

## Escalation Paths

### Path 1: Baseline Regression (Coverage drop >1.5%)
1. Halt all CI workflows
2. Create CRITICAL issue
3. Notify @mbaetiong
4. Investigate (15 min - 2 hours)
5. Rollback OR add tests OR fix environment
6. Re-verify baseline (1 day)
7. @mbaetiong approves resumption
8. Resume Phase 1 progression (OR extend timeline)

### Path 2: Quality Metrics Degradation
1. Identify flaky tests
2. Fix or revert changes
3. Re-verify (< 2 hours)
4. Resume (no approval needed)

### Path 3: Agent Integration Failure
1. Switch to manual workaround
2. Document issue
3. Fix when convenient (< 24 hours)
4. Resume automated operation

### Path 4: Phase 1 Progression Blocked
1. Pause test generation
2. Investigate blocking issue
3. Fix root cause
4. Verify baseline stable (1 day)
5. Resume Phase 1
6. **Decision gate:** Extend timeline or reduce scope?

---

## Post-Incident Procedures

### After Every Incident (Regardless of Severity)

**Step 1: Document Incident**
```markdown
# Incident Report — YYYY-MM-DD

**Severity:** [CRITICAL/HIGH/MEDIUM/LOW]
**Duration:** HH:MM
**Root Cause:** [...]
**Resolution:** [...]
**Lessons Learned:** [...]

## Timeline
- HH:MM Incident detected
- HH:MM Root cause identified
- HH:MM Fix applied
- HH:MM Verification complete

## Preventive Measures
- [Measure 1]
- [Measure 2]
- [Measure 3]
```

**Step 2: File Post-Mortem Issue**
```bash
gh issue create \
  --title "Post-Mortem: [Incident Title]" \
  --label "type:post-mortem" \
  --body-file incident_report.md
```

**Step 3: Share Learning**
- Post incident summary to team Slack
- Add preventive measure to validation test suite if applicable
- Update runbooks/documentation

---

## Prevention Measures

### To Prevent Coverage Regressions
1. **Require test coverage for code changes** (enforce in CI)
2. **Flag high-mutation tests** (tests that don't catch bugs)
3. **Monitor test flakiness** (rerun flaky tests before merge)
4. **Track module-level coverage** (catch tier minimums early)

### To Prevent Validation Test Failures
1. **Run tests in isolation** (catch shared state issues)
2. **Use timeouts** (catch timing dependencies)
3. **Mock external dependencies** (make tests deterministic)
4. **Randomize test order** (catch ordering dependencies)

### To Prevent Environment Issues
1. **Use Docker for CI** (consistent environment)
2. **Cache dependencies wisely** (but invalidate when needed)
3. **Monitor CI quota** (ensure enough resources)
4. **Use standard Python version** (3.12.13)

---

## Rollback Success Criteria

### Successful Rollback If:
- ✅ Coverage restored to 34.63% ±1.5%
- ✅ All tests passing (100% pass rate)
- ✅ Quality metrics restored
- ✅ Module tier minimums met
- ✅ Baseline stable for 1 day post-rollback
- ✅ @mbaetiong approves resumption

### Failed Rollback If:
- ❌ Coverage still below 33.13%
- ❌ Tests still failing after rollback
- ❌ Quality metrics still degraded
- ❌ Same issue happens again post-rollback
- ❌ Cascading failures detected

**If rollback fails:** Escalate to full engineering review

---

## Contact & Support

| Situation | Contact | Action |
|-----------|---------|--------|
| Coverage regression >1.5% | @mbaetiong | Immediate investigation |
| Validation test failure | unified-coverage-agent | Fix tests |
| CI environment issue | infrastructure team | Fix environment |
| Module tier breach | unified-coverage-agent | Add tests or revert |
| Phase 1 progression blocked | @mbaetiong | Approve timeline extension |

---

**Status:** ✅ ROLLBACK PROCEDURES DOCUMENTED & READY

All failure scenarios have documented recovery paths with clear decision trees and escalation procedures.
