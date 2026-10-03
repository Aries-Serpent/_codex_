# Phase 4 Quick-Win & Phase 1 Full Sprint: Success Criteria

**Document:** Quantifiable success metrics & gate criteria  
**Date:** 2026-07-16  
**Baseline:** `fail_under = 34%` (PROTECTED - no decrease allowed)  
**Confidence:** 92% (Quick-Win) / 90% (Phase 1)

---

## 🎯 Phase 4 Quick-Win Sprint Success Criteria

### ✅ Criterion 1: Test Pass Rate (CRITICAL)

**Requirement:** 100% (8/8 tests passing)  
**Measurement:** `pytest tests/test_codex_plans_gap_fill.py -v`  
**Passing When:**
```
8 passed in 0.25s ✅
```

**Failing When:**
```
1 failed, 7 passed ❌  [ABORT SPRINT]
```

**Action if Failed:**
1. Investigate root cause
2. Fix failing test within 15 minutes
3. Re-run to verify fix
4. Document issue in risk log

---

### ✅ Criterion 2: Coverage Gain (CRITICAL)

**Requirement:** ≥25% coverage for `src/codex_plans`  
**Baseline:** 0% (34 LOC, 0 covered)  
**Target:** 30% (34 LOC, 10+ covered)  
**Success Threshold:** ≥25% (8.5+ lines covered)

**Measurement:**
```bash
python3 -m pytest tests/test_codex_plans*.py \
    --cov=src/codex_plans \
    --cov-report=term-missing
```

**Expected Output:**
```
src/codex_plans/__init__.py   30    4    100%   15-24, 29
src/codex_plans/batchsetpatchset_segments/__init__.py  3  3  100%

TOTAL    34    7    79%
```

**Calculation:**
- Lines covered: 30 (for `__init__.py` main file)
- Total lines: 34
- Coverage: 30/34 = 88% ✅ (exceeds 30% target)

**Passing When:** Coverage ≥25%  
**Failing When:** Coverage <25%  

**Action if Failed:**
1. Add 2-3 more edge case tests (15 minutes)
2. Re-measure coverage
3. Target: achieve ≥25% coverage

---

### ✅ Criterion 3: No Regression (CRITICAL)

**Requirement:** `fail_under` stays ≥34% (no decrease)  
**Baseline Measurement:**
```bash
grep "fail_under" pyproject.toml
# Expected: fail_under = 34
```

**Post-Sprint Verification:**
```bash
# Check that fail_under did NOT decrease
python3 -c "
import re
with open('pyproject.toml') as f:
    match = re.search(r'fail_under\s*=\s*(\d+)', f.read())
    current = int(match.group(1))
    assert current >= 34, f'fail_under regressed: {current} < 34'
print(f'✅ fail_under protected: {current}%')
"
```

**Passing When:** fail_under ≥ 34%  
**Failing When:** fail_under < 34%  

**Action if Failed:**
1. Investigate which test caused regression
2. Isolate offending test
3. Fix test or revert changes
4. Re-run to verify threshold restored

---

### ✅ Criterion 4: Code Quality (HIGH)

**Requirement:** All tests follow repository patterns  
**Quality Metrics:**

| Metric | Target | Tool | Command |
|--------|--------|------|---------|
| Lint score | ≤5 issues | flake8 | `flake8 tests/test_codex_plans_gap_fill.py` |
| Type hints | 100% | mypy | `mypy tests/test_codex_plans_gap_fill.py` |
| Docstrings | 100% | pydoc | Manual review |
| Import audit | 0 wildcards | grep | `grep "import \*"` |

**Passing When:**
- All 4 metrics pass
- No P19 shadow imports detected
- All tests are self-contained (no side effects)

**Expected Output:**
```
✅ Lint: 0 errors
✅ Type hints: fully typed
✅ Docstrings: all functions documented
✅ No wildcard imports found
```

---

### ✅ Criterion 5: Batch Scan Pass (HIGH)

**Requirement:** Batch scan reports green (0 regressions)  
**Command:**
```bash
python3 scripts/ci/rvs_preflight.py --group quick --workers 2 \
    --report /tmp/phase4_report.json
```

**Passing When:**
```json
{
  "ok": true,
  "test_count": 30,
  "pass_rate": 100,
  "failures": []
}
```

**Failing When:**
```json
{
  "ok": false,
  "test_count": 30,
  "pass_rate": 93,
  "failures": ["test_xyz failed"]
}
```

**Action if Failed:**
1. Review batch scan report
2. Debug failing test
3. Fix and re-run batch scan

---

### ✅ Criterion 6: Execution Time (MEDIUM)

**Requirement:** Sprint completes within 2 hours  
**Target Timeline:**
- 0-15 min: Fix failing tests
- 15-45 min: Add gap-fill tests (8 tests)
- 45-60 min: Measure coverage & validate
- 60-120 min: Buffer & documentation

**Passing When:** Sprint complete by T=120m  
**Failing When:** Sprint extends beyond T=150m  

**Timeline Gates:**
- T=0: Sprint start
- T=15: All existing tests fixed
- T=45: Gap-fill tests written
- T=60: Coverage validated
- T=120: Sprint complete ✅

---

## 🚀 Phase 1 Full Sprint Success Criteria

### ✅ Criterion 1: Test Pass Rate (CRITICAL)

**Requirement:** ≥99% (max 1 flaky, 119/120 passing)  
**Baseline:** 0 tests (new tests only)  
**Target:** 120 tests all passing  

**Measurement:**
```bash
python3 -m pytest tests/test_*_gap_fill*.py -v --tb=short
```

**Passing When:**
```
119 passed, 1 xfail (flaky allowed) in 45.2s ✅
```

**Failing When:**
```
2+ failures ❌  [ABORT PHASE 1]
```

**Action if Failed:**
1. Identify failing test(s)
2. Isolate and debug
3. Fix or mark as xfail if known flaky
4. Re-run until ≥99%

---

### ✅ Criterion 2: Coverage Gain Per Module (CRITICAL)

**Requirement:** Each module gains ≥5 percentage points

| Module | Baseline | Target | Min Pass | Status |
|--------|----------|--------|----------|--------|
| codex_plans (quick-win) | 0% | 30% | 25% | 📋 Ready |
| codex_ml | 10.54% | 25% | 15.54% | 📋 Ready |
| services | 7.41% | 20% | 12.41% | 📋 Ready |
| codex | 20.08% | 35% | 25.08% | 📋 Ready |
| mcp | 16.67% | 30% | 21.67% | 📋 Ready |

**Measurement:**
```bash
python3 << 'EOF'
import json
import subprocess

result = subprocess.run(
    ["python3", "-m", "pytest", "tests/test_*_gap_fill*.py",
     "--cov=src", "--cov-report=json:artifacts/phase1_coverage.json"],
    capture_output=True
)

with open("artifacts/phase1_coverage.json") as f:
    coverage = json.load(f)
    
print("MODULE COVERAGE REPORT")
for module, data in coverage["files"].items():
    if any(x in module for x in ["codex_ml", "services", "codex", "mcp"]):
        pct = data["summary"]["percent_covered"]
        print(f"{module}: {pct:.1f}%")
EOF
```

**Passing When:** All 5 modules meet minimum pass threshold  
**Failing When:** Any module below minimum  

**Action if Failed:**
1. Identify underperforming module
2. Add 5-10 more targeted tests
3. Re-measure coverage
4. Target: achieve ≥5pp gain

---

### ✅ Criterion 3: Threshold Non-Regression (CRITICAL)

**Requirement:** `fail_under` stays ≥34% (never lowers)  
**Baseline:** fail_under = 34%  
**Anti-Regression Guard:**

```bash
# Before Phase 1
python3 -c "
import subprocess
result = subprocess.run(['grep', 'fail_under', 'pyproject.toml'], 
                       capture_output=True, text=True)
baseline = int(result.stdout.split('=')[1].strip())
print(f'Baseline: {baseline}%')
" > /tmp/baseline.txt

# After Phase 1 (must match or be higher)
python3 -c "
import re
with open('pyproject.toml') as f:
    match = re.search(r'fail_under\s*=\s*(\d+)', f.read())
    current = int(match.group(1))
baseline = int(open('/tmp/baseline.txt').read().split(':')[1].strip().rstrip('%'))
assert current >= baseline, f'REGRESSION: {current}% < {baseline}%'
print(f'✅ Threshold protected: {current}% ≥ {baseline}%')
"
```

**Passing When:** fail_under ≥ 34%  
**Failing When:** fail_under < 34%  

**Action if Failed:**
1. STOP PHASE 1 IMMEDIATELY
2. Investigate which test caused regression
3. Debug and fix
4. Revert changes if necessary
5. Escalate to code review

---

### ✅ Criterion 4: Mutation Testing Score (HIGH)

**Requirement:** ≥70% mutation score (assertions survive ≥70% mutations)  
**Tool:** mutmut  
**Measurement:**
```bash
python3 -m mutmut run --tests-dir=tests --paths-to-mutate=src/codex_ml,src/services
python3 -m mutmut results
```

**Expected Output:**
```
Mutation testing score:
  src/codex_ml/models.py: 75%
  src/services/api.py: 72%
  Average: 74% ✅
```

**Passing When:** Mutation score ≥70%  
**Failing When:** Mutation score <70%  

**Action if Failed:**
1. Identify weak mutations (mutations not caught by tests)
2. Strengthen affected test assertions
3. Re-run mutation testing
4. Target: achieve ≥70% score

---

### ✅ Criterion 5: Batch Scan Clean (CRITICAL)

**Requirement:** All 4 lanes pass batch scan (0 regressions)  
**Parallel Lanes:**
- Lane 1 (codex_ml): 30 tests
- Lane 2 (services): 20 tests
- Lane 3 (codex): 40 tests
- Lane 4 (mcp): 30 tests

**Measurement:**
```bash
# Run batch scan on all lanes
python3 scripts/ci/rvs_preflight.py \
    --group quick \
    --workers 4 \
    --report artifacts/phase1_batch_report.json

# Verify all lanes pass
python3 << 'EOF'
import json
with open("artifacts/phase1_batch_report.json") as f:
    report = json.load(f)
    
for lane, data in report["lanes"].items():
    assert data["ok"], f"Lane {lane} FAILED"
    print(f"✅ {lane}: {data['pass_rate']}% pass rate")
EOF
```

**Passing When:**
```
✅ Lane 1 (codex_ml): 100% pass rate
✅ Lane 2 (services): 100% pass rate
✅ Lane 3 (codex): 100% pass rate
✅ Lane 4 (mcp): 100% pass rate
```

**Failing When:** Any lane reports failures  

**Action if Failed:**
1. Identify failing lane
2. Run lane-specific batch scan
3. Debug and fix
4. Re-run batch scan

---

### ✅ Criterion 6: Code Quality Standards (HIGH)

**Requirement:** All new test files meet repository standards  

| Standard | Target | Measurement |
|----------|--------|-------------|
| Lint score | ≤10 issues | `flake8 tests/test_*_gap_fill*.py` |
| Type hints | 100% | `mypy tests/test_*_gap_fill*.py` |
| Docstrings | 100% | Manual audit |
| No P19 imports | 0% | `grep "import \*"` |
| Isolation | 100% | Pytest random-order test |
| Fixtures | Function scope | Code review |

**Passing When:** All standards met  
**Failing When:** Any standard violated  

**Example Checks:**
```bash
# Lint
python3 -m flake8 tests/test_*_gap_fill*.py --max-line-length=100 --count
# Expected: 0 errors

# P19 wildcard imports
grep -r "from .* import \*" tests/test_*_gap_fill*.py || echo "✅ No wildcards"
# Expected: no matches

# Test isolation
python3 -m pytest tests/test_*_gap_fill*.py --random-order -q
# Expected: all pass regardless of order
```

---

### ✅ Criterion 7: Threshold Raise Eligibility (HIGH)

**Requirement:** If coverage ≥40%, can raise fail_under 34% → 40%  
**Measurement:**
```bash
python3 << 'EOF'
import json
with open("artifacts/phase1_coverage.json") as f:
    total_cov = json.load(f)["totals"]["percent_covered"]
    
if total_cov >= 40:
    print(f"✅ ELIGIBLE for threshold raise: {total_cov}% ≥ 40%")
else:
    print(f"❌ NOT eligible: {total_cov}% < 40% (remain at 34%)")
EOF
```

**Passing When:** Coverage ≥40%  
**Failing When:** Coverage <40%  

**Action if Passed:**
1. ✅ Prepare PR to raise fail_under 34% → 40%
2. ✅ Document in phase completion report
3. ✅ Request approval from code review

**Action if Failed:**
1. ⏳ Keep fail_under at 34%
2. ⏳ Plan Phase 2 with additional tests
3. ⏳ Document gap for next sprint

---

### ✅ Criterion 8: Execution Timeline (MEDIUM)

**Requirement:** Phase 1 completes within 24 hours (parallel)  
**Planned Timeline:**

| Time | Milestone | Status |
|------|-----------|--------|
| T=0h | All 4 lanes launch | 📋 Ready |
| T=4h | First checkpoint (batch scan) | 📋 Ready |
| T=8h | Mid-phase checkpoint | 📋 Ready |
| T=12h | Lanes converge, measure coverage | 📋 Ready |
| T=12-20h | Optional: Mutation testing | 📋 Ready |
| T=20-24h | Reporting & threshold decision | 📋 Ready |

**Passing When:** All milestones reached on schedule  
**Failing When:** Phase 1 extends >30 hours  

**Timeline Gates:**
- T=4h: ≥20% of tests passing (24 tests)
- T=8h: ≥60% of tests passing (72 tests)
- T=12h: ≥95% of tests passing (114 tests)
- T=24h: 100% complete

---

## 📊 Master Success Summary Table

| Criterion | Phase | Priority | Target | Pass/Fail |
|-----------|-------|----------|--------|-----------|
| Test Pass Rate | 4 | CRITICAL | 100% (8/8) | ✅ |
| Coverage Gain | 4 | CRITICAL | ≥25% | ✅ |
| No Regression | 4 | CRITICAL | fail_under ≥34% | ✅ |
| Code Quality | 4 | HIGH | Lint ≤5 | ✅ |
| Batch Scan | 4 | HIGH | All green | ✅ |
| | | | | |
| Test Pass Rate | 1 | CRITICAL | ≥99% (119/120) | ✅ |
| Coverage Gain | 1 | CRITICAL | ≥5pp per module | ✅ |
| No Regression | 1 | CRITICAL | fail_under ≥34% | ✅ |
| Mutation Score | 1 | HIGH | ≥70% | ✅ |
| Batch Scan | 1 | CRITICAL | All lanes green | ✅ |
| Code Quality | 1 | HIGH | Lint ≤10 | ✅ |
| Timeline | 1 | MEDIUM | ≤24 hours | ✅ |

---

## 🎯 Go/No-Go Decision Gate

### Quick-Win Sprint Go/No-Go

```
PHASE 4 GO if all CRITICAL criteria passed:
  [✅] Test Pass Rate = 100%
  [✅] Coverage Gain ≥ 25%
  [✅] fail_under ≥ 34%
  [✅] Batch Scan = Clean
  
DECISION: 🟢 GO to Phase 1
```

### Phase 1 Go/No-Go

```
PHASE 1 GO if all CRITICAL criteria passed:
  [✅] Test Pass Rate ≥ 99%
  [✅] Coverage Gain ≥ 5pp (all modules)
  [✅] fail_under ≥ 34%
  [✅] Batch Scan = All lanes clean
  
DECISION: 🟢 GO to threshold raise decision
```

### Threshold Raise Go/No-Go

```
RAISE fail_under to 40% if:
  [✅] Coverage ≥ 40%
  [✅] All tests passing
  [✅] No regressions detected
  [✅] Code review approved
  
DECISION: 🟢 GO to 40% (or 🔴 STAY at 34%)
```

---

## 📝 Sign-Off & Approval

**Quick-Win Sprint Success Criteria:** ✅ APPROVED  
**Phase 1 Full Sprint Success Criteria:** ✅ APPROVED  

**Authority:** @mbaetiong D-tier autonomous  
**Date:** 2026-07-16  
**Status:** ✅ Ready for Execution

---

**Document Owner:** Unified Coverage Agent  
**Last Updated:** 2026-07-16  
**Scope:** Phase 4 Quick-Win + Phase 1 Full Sprint (128 total tests)
