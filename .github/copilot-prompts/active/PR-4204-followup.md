# 🎯 PR Follow-Up Tasks - #4204

**PR**: #4204 - PR #4204  
**Branch**: `copilot/add-validation-for-batch-size`  
**Author**: @mbaetiong  
**Date**: 2026-05-03  
**Commit**: `6c7b69f4a61fbd88ea2021a4b14dce9fe4da07b2`  
**Status**: 🔄 ACTIVE

---

## 📋 PREVIOUS SESSION SUMMARY

### Completed Work
- [`6c7b69f4`] fix(codeql): resolve py/use-of-exit-or-quit, py/unnecessary-pass, py/comparison-of-identical-expressions, py/implicit-string-concatenation-in-list" (copilot-swe-agent[bot], 2026-05-03)
- [`8d2a8068`] fix(ci): universal baseline sweep — sync+auto_fix [skip ci] (github-actions[bot], 2026-05-03)
- [`b1449d81`] chore(d00): update session context digest [skip ci] (github-actions[bot], 2026-05-03)

### Files Modified
No files modified

---

## 🎯 NEXT PHASE OBJECTIVES

### Priority 1: Immediate Tasks 🔴 CRITICAL
- [ ] Fix 24 CodeQL error-level findings — `py/call-to-non-callable` ×4, `py/call/wrong-arguments` ×2, `py/call/wrong-named-argument` ×18
  - Requires CodeQL CLI: `codeql database analyze db-python --format=csv --output=/tmp/errors.csv`
  - Locations documented in `CODEQL-QUALITY-REMEDIATION.md`
- [ ] Fix `py/missing-equals` ×1 — class missing `__eq__` while having `__hash__`
  - Search: `grep -rn "__hash__" src/ --include="*.py" | grep -v "__eq__"`
- [ ] Fix `py/comparison-of-constants` ×1 — literal vs literal comparison always True/False
  - Search: `ruff check src/ --select=F632 --output-format=concise`
- [ ] Fix `py/unreachable-statement` ×33 — statements after unconditional return/raise/continue
  - Search: `ruff check src/ tests/ --select=F401,E501 --output-format=concise`

**Validation**:
```bash
python -m py_compile scripts/ci/batch_scan_integration.py scripts/ci/scan_failing_workflows.py scripts/cognitive/har_ingest.py scripts/cognitive/zendesk_endpoint_manager.py scripts/migrations/001_userstore_to_sqlite.py
python -m ruff check src/ tests/ --output-format=concise
python scripts/ci/mypy_baseline.py --require-baseline
python scripts/ci/auto_fix_common_issues.py --check-only
python scripts/ci/sync_tracked_files.py --fix
```

### Priority 2: Follow-Up Validation 🟡 HIGH
- [ ] Fix `py/unnecessary-lambda` ×5 — replace `lambda x: f(x)` with direct `f` reference
  - Search: `grep -rn "lambda.*:" src/ scripts/ --include="*.py" | grep -v "#"`
- [ ] Fix `py/unused-global-variable` ×118 — module-level variables never read outside the module
  - Run: `ruff check src/ scripts/ --select=F841 --output-format=concise`
- [ ] Fix `py/unused-import` ×36 — dead imports not caught by previous ruff pass
  - Run: `ruff check src/ scripts/ --select=F401 --output-format=concise`
- [ ] Fix `py/unused-local-variable` ×62 — local variables assigned but never used
  - Run: `ruff check src/ tests/ --select=F841 --output-format=concise`
- [ ] Fix `js/unused-local-variable` ×4 — JavaScript variables never read
  - Search: `grep -rn "var \|let \|const " src/ --include="*.js"`
- [ ] Update `CHANGELOG.md` `## [Unreleased]` section with PR #4204 entry
- [ ] Update `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` with session S294 completion

### Priority 3: Future Enhancements 🟢 MEDIUM
- [ ] Run full `pytest tests/ -v` suite and confirm 0 failures
- [ ] Confirm mypy baseline still ≤ 169 after all fixes: `python scripts/ci/mypy_baseline.py --require-baseline`
- [ ] Update `CODEQL-QUALITY-REMEDIATION.md` per-section Progress fields with commit SHAs
- [ ] Move this file to `.github/copilot-prompts/archive/` once all items are checked

---

## ✅ EXECUTION CHECKLIST

- [ ] All Priority 1 tasks completed and validated
- [ ] All Priority 2 tasks completed or documented
- [ ] Priority 3 tasks reviewed and prioritized
- [ ] All validation checks passed
- [ ] Documentation updated
- [ ] Self-review completed (5 passes, 0 concerns)

---

## 🔍 MANDATORY SELF-REVIEW PROTOCOL

**CRITICAL**: Perform 5 comprehensive self-review passes BEFORE concluding.

### Pass 1: Code Quality & Correctness
- [ ] All syntax errors resolved
- [ ] No linting warnings introduced
- [ ] Type hints correct
- [ ] Error handling comprehensive
- [ ] Edge cases covered

### Pass 2: Testing & Validation
- [ ] All tests passing locally
- [ ] New tests added for new functionality
- [ ] Test coverage maintained or improved
- [ ] CI/CD checks passing

### Pass 3: Documentation & Communication
- [ ] Code comments added for complex logic
- [ ] Docstrings updated
- [ ] README reflects changes
- [ ] CHANGELOG updated
- [ ] Commit messages descriptive

### Pass 4: Security & Safety
- [ ] No hardcoded secrets or credentials
- [ ] Input validation added
- [ ] Dependencies reviewed (no vulnerabilities)
- [ ] Security implications documented

### Pass 5: Integration & Dependencies
- [ ] No breaking changes (or properly documented)
- [ ] Backward compatibility maintained
- [ ] Cross-PR dependencies resolved
- [ ] No regressions introduced

**Failure Protocol**: If ANY checkpoint fails, document issue, create resolution plan, execute within current session, re-run until all checks clear. **NEVER defer** without explicit reasoning.

---

## 🤖 COPILOT AGENT INSTRUCTIONS

**When you see `@copilot continue` in PR #4204:**

1. Load this prompt from `.github/copilot-prompts/active/PR-4204-followup.md`
2. Execute Priority 1 tasks in order, validating each
3. Then execute Priority 2 tasks
4. Review Priority 3 tasks
5. Update this file after each task (add ✅ for completed)
6. Perform mandatory 5-pass self-review
7. Post comprehensive status as PR comment
8. Generate new continuation if work remains

**Self-Review Mandate**: Perform 5 comprehensive passes. Address ALL concerns until 0 issues remain. NEVER defer work without explicit reasoning and resolution plan.

---

**Generated**: 2026-05-03  
**Template Version**: 2.0.0  
**Last Updated**: 2026-05-03 17:56:49
