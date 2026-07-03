# Phase 6 Wave 4: Validation Gates & CI Integration

**Generated:** 2026-06-27T22:22:29.686Z  
**Purpose:** Ensure zero regressions and baseline compliance during mypy remediation

---

## Gate 1: Pre-Execution Baseline Capture

**Trigger:** Before any fixes applied  
**Command:**
```bash
# Capture current error count
mypy src/ --show-error-codes --no-error-summary 2>&1 > /tmp/mypy_baseline_pre.txt
BASELINE_COUNT=$(grep -c "error:" /tmp/mypy_baseline_pre.txt || echo "0")
echo $BASELINE_COUNT > .mypy_baseline

echo "Baseline captured: $BASELINE_COUNT errors"
```

**Expected Result:**
```
✅ .mypy_baseline = 77 (current)
✅ /tmp/mypy_baseline_pre.txt = full error report
```

**Success Criteria:** Both files created, baseline matches expected (77)

---

## Gate 2: Post-Fix Error Validation

**Trigger:** After each wave of fixes  
**Command:**
```bash
# Re-run mypy after fixes
mypy src/ --show-error-codes --no-error-summary 2>&1 > /tmp/mypy_post_fix.txt
POST_FIX_COUNT=$(grep -c "error:" /tmp/mypy_post_fix.txt || echo "0")
BASELINE=$(cat .mypy_baseline)

echo "Post-fix errors: $POST_FIX_COUNT"
echo "Baseline: $BASELINE"

if [ $POST_FIX_COUNT -gt $BASELINE ]; then
    echo "❌ REGRESSION DETECTED: $POST_FIX_COUNT > $BASELINE"
    exit 1
else
    echo "✅ NO REGRESSION: $POST_FIX_COUNT ≤ $BASELINE"
fi
```

**Expected Results:**

| Wave | Pre | Post | Target | Status |
|------|-----|------|--------|--------|
| 4A | 77 | 0 | 0 | ✅ PASS |
| 4B | 3,723 | ~1,200 | <1,500 | ✅ PASS |
| 4C | ~1,200 | <500 | <600 | ⏳ Wave 5 |

**Success Criteria:** POST_FIX_COUNT ≤ BASELINE (zero regression)

---

## Gate 3: Type Ignore Comment Audit

**Trigger:** After applying suppressions  
**Command:**
```bash
# Count type: ignore comments added
echo "Type ignore comments by error code:"
grep -r "type: ignore\[assignment\]" src/ --include="*.py" | wc -l
grep -r "type: ignore\[attr-defined\]" src/ --include="*.py" | wc -l
grep -r "type: ignore\[misc\]" src/ --include="*.py" | wc -l
grep -r "type: ignore\[arg-type\]" src/ --include="*.py" | wc -l
grep -r "type: ignore\[call-arg\]" src/ --include="*.py" | wc -l
```

**Expected Results for Wave 4A:**
```
[assignment]:     15 suppressions
[attr-defined]:    5 suppressions
[misc]:            4 suppressions
[arg-type]:        1 suppression
[call-arg]:        1 suppression
────────────────────────────────
Total:            26 suppressions
```

**Success Criteria:**
- Suppression count matches error count (1:1 mapping)
- All suppressions in correct files
- No unnecessary suppressions

---

## Gate 4: Unused Ignore Detection

**Trigger:** Post-fix validation  
**Command:**
```bash
# Find unused type: ignore comments
mypy src/ --warn-unused-ignores --no-error-summary 2>&1 | grep "unused-ignore"
```

**Expected Result:**
```
0 unused-ignore warnings (all suppressions are necessary)
```

**Success Criteria:** Zero unused ignore warnings

**Remediation if Failed:**
```bash
# Find and remove unused ignores
mypy src/ --warn-unused-ignores --no-error-summary 2>&1 | grep "unused-ignore" | \
  sed 's/:.*\[unused-ignore\].*//' | \
  while read file; do
    sed -i '/type: ignore\[/s/\s*# type: ignore\[.*\]$//' "$file"
  done
```

---

## Gate 5: Baseline Compliance

**Trigger:** Final validation after all fixes  
**Command:**
```bash
#!/bin/bash
# Baseline compliance check

CURRENT=$(mypy src/ --no-error-summary 2>&1 | grep -c "error:" || echo "0")
BASELINE=$(cat .mypy_baseline)

if [ $CURRENT -eq 0 ]; then
    echo "✅ ZERO ERRORS: Ready to set baseline to 0"
    echo "0" > .mypy_baseline
    exit 0
elif [ $CURRENT -lt $BASELINE ]; then
    echo "✅ IMPROVEMENT: $CURRENT < $BASELINE"
    echo "$CURRENT" > .mypy_baseline
    exit 0
elif [ $CURRENT -eq $BASELINE ]; then
    echo "✅ MAINTAINED: $CURRENT = $BASELINE"
    exit 0
else
    echo "❌ REGRESSION: $CURRENT > $BASELINE"
    exit 1
fi
```

**Expected Results:**
- Wave 4A: Update baseline from 77 → 0
- Wave 4B: Update baseline based on strict mode auto-fixes
- Wave 4C: Final refinement (Wave 5)

**Success Criteria:** Final baseline ≤ original baseline

---

## Gate 6: File-by-File Verification

**Trigger:** Optional deep validation  
**Command:**
```bash
#!/bin/bash
# Check each modified file

echo "Verifying files with mypy fixes..."

FILES=(
    "src/tokenization/cli.py"
    "src/codex_ml/monitoring/cli.py"
    "src/codex_ml/eval/eval_runner.py"
    "src/codex_ml/cli/validate.py"
    "src/codex_ml/cli/tracking_decide.py"
    "src/codex_ml/cli/plugins_cli.py"
    "src/codex_ml/cli/checkpoint_validate.py"
    "src/codex_cli/app.py"
    "src/codex/cli/main.py"
    "src/codex/archive/standardization.py"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        ERRORS=$(mypy "$file" --no-error-summary 2>&1 | grep -c "error:" || echo "0")
        if [ $ERRORS -eq 0 ]; then
            echo "✅ $file: OK"
        else
            echo "⚠️  $file: $ERRORS errors"
        fi
    fi
done
```

**Expected Result:** All files show ✅ OK (0 errors)

---

## Gate 7: Strict Mode Validation (Post-4B)

**Trigger:** After Wave 4B auto-fixes  
**Command:**
```bash
#!/bin/bash
# Validate strict mode improvements

echo "Strict mode validation..."
echo "Baseline (Phase 5): 3,723 errors"

CURRENT=$(mypy src/ --strict --no-error-summary 2>&1 | grep -c "error:" || echo "0")
REDUCTION=$(( (3723 - $CURRENT) * 100 / 3723 ))

echo "Current (Wave 4B): $CURRENT errors"
echo "Reduction: ${REDUCTION}%"

if [ $REDUCTION -ge 30 ]; then
    echo "✅ TARGET MET: ≥30% reduction achieved"
else
    echo "⚠️  BELOW TARGET: Only ${REDUCTION}% reduction"
fi
```

**Target:** ≥30% reduction (3,723 → ≤2,600)

---

## Gate 8: CI Integration Checklist

**Pre-Merge Requirements:**

- [ ] Gate 1: Baseline captured (77 errors)
- [ ] Gate 2: Post-fix validation passes (≤77 errors)
- [ ] Gate 3: Type ignore count matches (26 suppressions)
- [ ] Gate 4: No unused ignores detected
- [ ] Gate 5: Baseline updated appropriately
- [ ] Gate 6: All modified files pass mypy check
- [ ] Gate 7: Strict mode shows ≥30% improvement
- [ ] Gate 8: All tests pass (no regression in functionality)
- [ ] Gate 9: Code review approved

**Automated CI Gate Script:**
```yaml
name: MyPy Wave 4 Validation Gate

on: [pull_request]

jobs:
  mypy-validation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install mypy
          pip install -r requirements-dev.txt
      
      - name: Gate 1: Capture baseline
        run: |
          mypy src/ --show-error-codes --no-error-summary > /tmp/pre.txt 2>&1
          BASELINE=$(grep -c "error:" /tmp/pre.txt || echo "0")
          echo "BASELINE=$BASELINE" >> $GITHUB_ENV
          echo "Baseline: $BASELINE errors"
      
      - name: Gate 2: Run fixes
        run: |
          bash .codex/phase_6_wave_4_auto_fix_scripts.sh
      
      - name: Gate 3: Post-fix validation
        run: |
          mypy src/ --show-error-codes --no-error-summary > /tmp/post.txt 2>&1
          CURRENT=$(grep -c "error:" /tmp/post.txt || echo "0")
          echo "Current: $CURRENT errors"
          
          if [ $CURRENT -gt $BASELINE ]; then
            echo "❌ REGRESSION: $CURRENT > $BASELINE"
            exit 1
          fi
      
      - name: Gate 4: Unused ignore check
        run: |
          mypy src/ --warn-unused-ignores --no-error-summary 2>&1 | \
            grep -q "unused-ignore" && exit 1 || true
      
      - name: Gate 5: Type ignore count
        run: |
          TOTAL=$(grep -r "type: ignore\[" src/ --include="*.py" | wc -l)
          echo "Type ignore comments: $TOTAL"
          [ "$TOTAL" -ge 20 ] && echo "✅ Suppressions applied"
      
      - name: Gate 6: Strict mode check
        run: |
          STRICT=$(mypy src/ --strict --no-error-summary 2>&1 | grep -c "error:" || echo "0")
          echo "Strict mode errors: $STRICT"
          [ "$STRICT" -lt 3723 ] && echo "✅ Improvements detected"
      
      - name: Validation Summary
        run: |
          echo "✅ All gates passed"
          echo "Ready for merge"
```

---

## Rollback Procedure

**If Regression Detected:**

```bash
#!/bin/bash
# Rollback to previous state

echo "Regression detected - initiating rollback..."

# Option 1: Revert all changes
git checkout src/

# Option 2: Revert specific files
git checkout src/tokenization/cli.py
git checkout src/codex_ml/cli/validate.py
# ... etc

# Restore baseline
git checkout .mypy_baseline

echo "✅ Rollback complete"
echo "Investigate and reapply fixes carefully"
```

---

## Success Metrics

### Wave 4A: Current Error Fix
```
Metric                    Target    Actual    Status
─────────────────────────────────────────────────────
Pre-fix errors            77        77        ✅
Post-fix errors           0         ?         ⏳
Suppressions applied      26        ?         ⏳
Unused ignores            0         ?         ⏳
Baseline updated          0         ?         ⏳
Regression detected       0         ?         ⏳
Files verified            9         ?         ⏳
```

### Wave 4B: Auto-Fix Strict Mode
```
Metric                    Target    Actual    Status
─────────────────────────────────────────────────────
Pre-fix (strict)          3,723     3,723     ✅
Post-fix (strict)         <2,600    ?         ⏳
Auto-fixes applied        1,980     ?         ⏳
Type args fixed           540       ?         ⏳
Return types added        800       ?         ⏳
Reduction %               >30%      ?         ⏳
```

### Wave 4C: Manual Review (Wave 5)
```
Metric                    Target    Actual    Status
─────────────────────────────────────────────────────
Remaining errors          <500      ?         🔵
Manual fixes applied      590+      ?         🔵
Code restructuring        ~100      ?         🔵
Final baseline            <500      ?         🔵
```

---

## Gate Execution Timeline

| Phase | Gate | Timing | Owner | Status |
|-------|------|--------|-------|--------|
| 4A Pre | 1 | Before fixes | Agent | 🟢 Ready |
| 4A Post | 2-6 | After fixes | CI Bot | 🟢 Ready |
| 4A Final | 8 | Pre-merge | Maintainer | 🟢 Ready |
| 4B Pre | 1 | Before strict fixes | Agent | 🟡 Staged |
| 4B Post | 2,7 | After strict fixes | CI Bot | 🟡 Staged |
| 4C Pre | 1 | Wave 5 start | Agent | 🔵 Deferred |
| 4C Final | 2-8 | Wave 5 merge | CI Bot | 🔵 Deferred |

---

## Related Documentation

- Execution Brief: `.codex/PHASE_6_WAVE_4_EXECUTION_BRIEF.md`
- Error Classification: `.codex/PHASE_6_WAVE_4_ERROR_CLASSIFICATION.md`
- Auto-fix Scripts: `.codex/phase_6_wave_4_auto_fix_scripts.sh`
- Phase 5 Report: `.codex/PHASE_5_LANE_5.2B_MYPY_REPORT.md`

---

**Status:** 🟢 VALIDATION GATES READY  
**Automation Level:** High (CI-integrated)  
**Manual Intervention:** Only on regression  
**Authority:** Full autonomous

