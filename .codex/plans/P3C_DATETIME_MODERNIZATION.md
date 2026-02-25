# Planset: P3c — datetime.now(UTC) Modernization Pass

**Status**: 🟢 ENHANCEMENT — Can run anytime
**Priority**: P3 — Enhancement
**Created**: 2026-02-20
**Agent**: `datetime-modernizer`

---

## Problem

Multiple files use `datetime.utcnow()` (timezone-naive, deprecated in Python 3.12) instead of `datetime.now(UTC)` or `datetime.now(timezone.utc)`. This causes `TypeError: can't subtract offset-naive and offset-aware datetimes` when mixed with timezone-aware datetimes in tests or production code.

**Known failures**:
- `tests/cognitive_brain/quantum/test_memory.py::TestIntegration::test_statistics_comprehensive` — assessor uses `datetime.utcnow()` internally, test uses `datetime.now(UTC)`

---

## Affected Files (initial scan)

```bash
grep -rn "datetime.utcnow()\|datetime.utcfromtimestamp" src/ tests/ --include="*.py" \
  | grep -v "# noqa" | grep -v ".pyc"
```

**Expected finds** (partial list based on codebase):
- `src/cognitive_brain/` — multiple files
- `src/codex_ml/` — tracking, logging modules
- `tests/` — fixture files

---

## Modernization Rules

| Old pattern | New pattern | Notes |
|-------------|-------------|-------|
| `datetime.utcnow()` | `datetime.now(timezone.utc)` | Or `datetime.now(UTC)` with `from datetime import UTC` (Py3.11+) |
| `datetime.utcfromtimestamp(ts)` | `datetime.fromtimestamp(ts, tz=timezone.utc)` | |
| `datetime(year, month, day)` (naive) | `datetime(year, month, day, tzinfo=timezone.utc)` | Only if compared with aware datetimes |

---

## Implementation Steps

### Option A: Use `datetime-modernizer` agent (Recommended)

```
@copilot Use the datetime-modernizer agent to:
1. Scan all Python files for datetime.utcnow() usage
2. Replace with datetime.now(timezone.utc)
3. Add `from datetime import timezone` imports where needed
4. Run pytest on changed files to verify no regressions
5. Run ruff check on all changed files
```

### Option B: Manual via sed + verification

```bash
# Step 1: Find all occurrences
grep -rn "datetime\.utcnow()" src/ tests/ --include="*.py" > /tmp/utcnow_findings.txt

# Step 2: Replace (safe — always produces aware datetime)
find src/ tests/ -name "*.py" -exec \
  sed -i 's/datetime\.utcnow()/datetime.now(timezone.utc)/g' {} \;

# Step 3: Add missing imports
# For each file that now uses timezone.utc, ensure:
# from datetime import datetime, timezone
python scripts/ci/auto_fix_common_issues.py --pattern 1  # fix F401 unused imports

# Step 4: Run tests
pytest tests/ -q --tb=short -x

# Step 5: Ruff
ruff check src/ tests/ --fix
```

---

## Impact Assessment

| Category | Files | Risk |
|----------|-------|------|
| Cognitive brain analytics | `src/cognitive_brain/analytics/` | Low — internal use |
| Logging/tracking | `src/codex_ml/tracking/`, `src/codex/logging/` | Low — timestamp only |
| Tests | `tests/cognitive_brain/` | Low — assertion context |
| Serialization | `src/codex_ml/utils/checkpointing.py` | Medium — verify JSON output |

**Total estimated changes**: ~50–100 lines across ~20–30 files.

---

## Immediate Fix (remove `test_statistics_comprehensive` xfail)

After the modernization pass, remove from `tests/conftest.py::_PREEXISTING_FAILURES`:
```python
# Remove this entry:
"tests/cognitive_brain/quantum/test_memory.py::TestIntegration::test_statistics_comprehensive"
```

---

## Success Criterion

- Zero `datetime.utcnow()` calls in `src/` and `tests/`
- `test_statistics_comprehensive` passes without xfail
- `python -W error::DeprecationWarning -m pytest tests/` passes (no deprecation warnings from datetime)
- All ruff checks pass

---

## Estimated Effort

2–3 hours for full codebase pass. Use `datetime-modernizer` agent to automate.
