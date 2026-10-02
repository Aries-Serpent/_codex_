# Phase 14 WS4: Agent Grading Rubric & Output Validation Framework

**Authority:** @mbaetiong D-tier autonomous  
**Effective Date:** 2026-07-24T20:10Z  
**Version:** 1.0 (Phase 14 Grading)

---

## 📋 AGENT GRADING RUBRIC (0-100 Scale)

### Overview

All agents working on Phase 14 WS1-3 are graded on a **0-100 scale** with the following criteria:

| Criterion | Points | Definition | Measurement |
|-----------|--------|------------|-------------|
| **Failure Reduction** | 40 | Each original failure fixed = 40/N points | Count: fixed/total original failures |
| **No Regressions** | 25 | Full score if no new failures; -25 if regression | Binary: new failures > 0 = auto-fail |
| **Policy Compliance** | 20 | No xfail, no bare except, skipif documented; -5 per violation | Audit: ruff linting, test analysis |
| **Documentation** | 10 | Tracking log updated with Attempt entry + commit SHA | Check: `.codex/PHASE_14_ATTEMPT_LOG.md` |
| **Lint Clean** | 5 | ruff + import smoke pass on all changed files | Command: `ruff check .` on diff files |

**Total: 100 points**

### Score Interpretation

| Score Range | Status | Action | Authority |
|-------------|--------|--------|-----------|
| **90-100** | ✅ EXCELLENT | Auto-approve for merge | agent-orchestrator (automated) |
| **80-89** | ✅ GOOD | Approve with minor review | Human reviewer (WS lead) |
| **70-79** | ⚠️ ACCEPTABLE | Human review required | Human reviewer (WS lead) |
| **60-69** | ❌ NEEDS IMPROVEMENT | Send back to agent with feedback | agent-orchestrator → agent + feedback |
| **<60** | ❌ FAILED | Escalate to @mbaetiong | @mbaetiong decision |

---

## 🎯 DETAILED GRADING CRITERIA

### 1. Failure Reduction (40 Points)

**Definition:** Each original failure fixed by the agent = 40/N points (where N = total failures identified).

**Scoring:**
- If N=1 failure and fixed: 40/1 = 40 points ✅
- If N=4 failures and 3 fixed: 40/4 × 3 = 30 points ⚠️
- If N=4 failures and all fixed: 40/4 × 4 = 40 points ✅

**Measurement:**
```
Failures at session start: [list from GitHub issue or PR]
Failures at session end: [run test suite after agent completes]
Fixed: [start count] - [end count]
Score: 40 × (fixed / start_count)
```

**Examples:**
- Started with 10 ImportError failures; ended with 0 → 40/10 × 10 = 40 points
- Started with 5 AttributeError failures; ended with 1 → 40/5 × 4 = 32 points
- Started with 2 failures; ended with 2 (no progress) → 40/2 × 0 = 0 points

---

### 2. No Regressions (25 Points)

**Definition:** Full 25 points if no new failures introduced. Automatic failure (0 points) if any regression.

**Measurement:**
```
New failures in changed files = [end test run] - [start test run] - [fixed by agent]
IF new_failures > 0:
  REGRESSION_DETECTED = TRUE
  score = 0 (auto-fail this criterion)
ELSE:
  score = 25
```

**Examples:**
- Fixed 10 ImportErrors, introduced 0 new errors → 25 points ✅
- Fixed 5 AttributeErrors, introduced 2 new test failures → 0 points ❌
- No changes to existing tests, all pass → 25 points ✅

**Prevention Strategy:**
- Agent must run full test suite before claiming completion
- Manual review must verify no new failures in CI
- If regression, agent goes back to fix with feedback

---

### 3. Policy Compliance (20 Points)

**Definition:** No `xfail(strict=False)`, no bare `except` clauses, `skipif` documented. -5 points per violation.

**Audit Checklist:**
```yaml
violations:
  xfail_strict_false: "grep for 'xfail(strict=False)' in changed files"
    penalty: -5 per occurrence
    example: "@pytest.mark.xfail(strict=False)  # ❌ NOT ALLOWED"
    
  bare_except: "grep for 'except:' without exception type"
    penalty: -5 per occurrence
    example: "try:\n    ...\nexcept:  # ❌ NOT ALLOWED\n    pass"
    
  undocumented_skipif: "grep for 'skipif' without docstring"
    penalty: -5 per occurrence
    example: "@pytest.mark.skipif(sys.platform=='win32')  # ❌ NEEDS DOCSTRING"
    
  missing_tracking_log: "No entry in .codex/PHASE_14_ATTEMPT_LOG.md"
    penalty: -5
```

**Scoring:**
- Base: 20 points
- Violations found: -5 each
- Minimum: 0 points

**Examples:**
- No violations → 20 points ✅
- 1 xfail(strict=False) found → 20 - 5 = 15 points ⚠️
- 2 bare except + 1 undocumented skipif → 20 - 15 = 5 points ❌

---

### 4. Documentation (10 Points)

**Definition:** Tracking log updated with Attempt entry + commit SHA.

**Requirements:**
1. Entry created in `.codex/PHASE_14_ATTEMPT_LOG.md`
2. Format: `## Attempt #N (Agent: name) — [Timestamp]`
3. Includes commit SHA(s)
4. Includes summary of work done
5. Includes result (Success/Partial/Failed)

**Tracking Log Template:**
```markdown
## Attempt #3 (Agent: ci-testing-agent) — 2026-07-31T14:30:00Z

**Commit:** `890f016a` (WS3: Create comprehensive feature rollout strategy)

**Work Performed:**
- Fixed 5 ImportError failures in test_model.py
- Added missing __init__.py files to 3 test packages
- Resolved P19 shadow import conflict in src/codex/ml/

**Result:** SUCCESS (All 5 failures resolved; 0 regressions)

**Score:** 95/100
- Failure Reduction: 40/40 (5/5 fixed)
- No Regressions: 25/25 (0 new failures)
- Policy Compliance: 20/20 (no violations)
- Documentation: 10/10 (this entry)
- Lint Clean: 5/5 (ruff passed)
```

**Scoring:**
- Complete, accurate tracking entry → 10 points ✅
- Incomplete entry (missing commit SHA or summary) → 5 points ⚠️
- No tracking entry → 0 points ❌

---

### 5. Lint Clean (5 Points)

**Definition:** `ruff check .` and `python -m py_compile` pass on all changed files.

**Verification:**
```bash
# Get list of changed files
git diff --name-only origin/main

# Run ruff on changed files
ruff check <changed_files>

# Run import smoke test
for f in <changed_files>; do python -m py_compile "$f"; done

# Result: 0 errors = 5 points, any errors = 0 points
```

**Scoring:**
- All checks pass → 5 points ✅
- ruff errors (F-codes, I-codes, etc.) → 0 points ❌
- Import errors in changed files → 0 points ❌

**Examples:**
- `ruff check` passes on all 8 changed files → 5 points ✅
- `ruff check` finds F401 (unused import) in 1 file → 0 points ❌

---

## 🔄 GRADING WORKFLOW

### Step 1: Identify Scope

```
Input: Agent completion claim or PR/issue
├─ Extract: original failures, changed files, commit SHAs
├─ Document in: grading_session.md
└─ Proceed to Step 2
```

### Step 2: Run Failure Reduction Analysis

```
1. Checkout original code (git checkout origin/main)
2. Run test suite; capture failure count
3. Checkout agent's branch
4. Run test suite; capture failure count
5. Calculate: fixed = start_count - end_count
6. Score: 40 × (fixed / start_count)
```

### Step 3: Regression Check

```
1. Compare test results: before → after
2. IF new_failures > 0:
   SCORE = 0 (auto-fail)
   FLAG for manual investigation
3. ELSE:
   SCORE = 25
```

### Step 4: Policy Compliance Audit

```
bash
1. for file in <changed_files>:
     grep "xfail(strict=False)" → count violations
     grep "except:" → count violations  
     grep "skipif" → verify docstring exists
2. Tally violations
3. Score: 20 - (5 × violation_count)
```

### Step 5: Documentation Check

```
1. Find entry in .codex/PHASE_14_ATTEMPT_LOG.md
2. Verify: timestamp, agent name, commit SHA(s), summary, result
3. IF complete: SCORE = 10
4. IF incomplete: SCORE = 5
5. IF missing: SCORE = 0
```

### Step 6: Lint Check

```
bash
ruff check <changed_files>
python -m py_compile <changed_files>
IF any errors:
  SCORE = 0
ELSE:
  SCORE = 5
```

### Step 7: Calculate Total & Recommend

```
Total Score = Failure_Reduction + Regressions + Policy + Docs + Lint
             = F + R + P + D + L

IF Score >= 90:
  Recommendation: AUTO-APPROVE
  Action: Merge without human review
  
ELSE IF Score >= 70:
  Recommendation: HUMAN REVIEW
  Action: Assign to WS lead for approval
  
ELSE IF Score >= 60:
  Recommendation: SEND BACK FOR IMPROVEMENTS
  Action: Provide feedback to agent; re-attempt
  
ELSE:
  Recommendation: ESCALATE
  Action: Notify @mbaetiong; escalate to agent lead
```

---

## 📊 GRADING REPORT TEMPLATE

```markdown
# Agent Grading Report

**Session:** PHASE_14_WS1_FEATURE_ROLLOUT_001
**Agent:** orchestrator-agent
**Date:** 2026-07-31T14:30:00Z
**Grader:** agent-orchestrator (automated)

## Original Scope
- Failures to fix: 5 ImportError in test_model.py
- Changed files: 8 (5 .py, 3 __init__.py)
- Commit SHAs: 890f016a, 8a1b2c3d

## Grading Results

### Criterion 1: Failure Reduction (40 points)
- Original failure count: 5
- Final failure count: 0
- Fixed by agent: 5
- Score: 40/40 ✅ (100% fixed)

### Criterion 2: No Regressions (25 points)
- New failures detected: 0
- Regressions: NONE
- Score: 25/25 ✅ (No regressions)

### Criterion 3: Policy Compliance (20 points)
- xfail(strict=False) violations: 0
- Bare except violations: 0
- Undocumented skipif violations: 0
- Violations total: 0
- Score: 20/20 ✅ (Full compliance)

### Criterion 4: Documentation (10 points)
- Tracking log entry: ✅ FOUND
- Timestamp: 2026-07-31T14:30:00Z
- Commit SHAs: 890f016a, 8a1b2c3d
- Summary: Present and complete
- Score: 10/10 ✅ (Complete documentation)

### Criterion 5: Lint Clean (5 points)
- ruff check result: PASSED
- py_compile result: PASSED
- Score: 5/5 ✅ (No lint errors)

## Total Score: 95/100

### Summary
**Status:** ✅ EXCELLENT (90-100 range)
**Recommendation:** AUTO-APPROVE FOR MERGE
**Action:** No further review needed; merge PR to main

### Notes
- All failures successfully fixed
- No regressions introduced
- Policy compliance maintained
- Clean lint check
- Ready for production deployment
```

---

## 🚨 FAILURE SCENARIOS & MITIGATION

### Scenario A: Agent Claims 40/40 but Actually 30/40

**Detection:**
- Grading step 2 shows 2 failures still present
- Claimed fixed ≠ actually fixed

**Response:**
- Score reduced: 40 × (3/5) = 24 points
- Regressions not the issue (0 new failures introduced)
- Policy/documentation may still be OK
- Total score could be ~80 (marginal, human review required)

**Mitigation:**
- Provide feedback: "3 of 5 failures still present; re-run test suite to verify"
- Agent re-attempts with specific failure IDs
- Grade improved on retry

---

### Scenario B: Agent Introduces 2 New Failures While Fixing 4

**Detection:**
- Original 4 failures fixed ✅
- BUT 2 new failures introduced ❌
- Regression detected

**Response:**
- Regressions score: 0/25 (auto-fail)
- Failure reduction: 40/4 × 3 = 30 points (only 3 old failures net fixed)
- Total score: ~50 (likely <70, send back)

**Mitigation:**
- Flag regressions immediately (within 1 hour of detection)
- Provide specific test IDs of new failures
- Ask agent to investigate root cause
- Require regression fix before approval

---

### Scenario C: Agent Uses xfail(strict=False) in Fix

**Detection:**
- Policy audit finds 2 instances of xfail(strict=False)
- Policy compliance score: 20 - 10 = 10 points

**Response:**
- Total score could drop from 95 to 85 (still acceptable, but flagged)
- Provide feedback: "Remove xfail(strict=False); fix the underlying issue instead"
- Ask agent to re-attempt without xfail

**Mitigation:**
- Document reason in attempt log (e.g., "Known flaky test; will fix in Phase 15")
- If documented, -5 penalty only (not -10)
- If not documented, full -10 penalty

---

## ✅ SUCCESS CRITERIA (Grading Framework)

- ✅ All agents graded consistently on 0-100 scale
- ✅ Scores ≥90 auto-approve (no human bottleneck)
- ✅ Scores 70-89 reviewed by WS leads (<4 hour turnaround)
- ✅ Scores <70 re-attempted with feedback (<24 hour turnaround)
- ✅ 0 grades escalated to @mbaetiong (agents meet quality bar)
- ✅ Attempt log updated for all work (100% documentation)

---

**Grading Rubric Version:** 1.0  
**Effective Date:** 2026-07-24T20:10Z  
**Next Review:** 2026-07-31T20:10Z (after first grading session)  
**Status:** ✅ ACTIVE
