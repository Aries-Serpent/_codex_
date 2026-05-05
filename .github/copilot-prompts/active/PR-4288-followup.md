# 🎯 PR Follow-Up Tasks - #4288

**PR**: #4288 - PR #4288  
**Branch**: `dependabot/pip/opentelemetry-exporter-prometheus-0.62b1`  
**Author**: @dependabot[bot]  
**Date**: 2026-05-05  
**Commit**: `247da068a50dee6ec4bfb36c33e61833f0f2169f`  
**Status**: 🔄 ACTIVE

---

## 📋 PREVIOUS SESSION SUMMARY

### Completed Work
- [`247da068`] deps(deps): bump opentelemetry-exporter-prometheus from 0.58b0 to 0.62b1 (dependabot[bot], 2026-05-05)
- [`1aecb7d0`] Merge pull request #4270 from Aries-Serpent/copilot/s679-sec-update-agent-accountability-report (Statix, 2026-05-05)
- [`4fddb142`] chore: auto-merge 1 automated commit(s) from main [skip ci] (github-actions[bot], 2026-05-05)

### Files Modified
No files modified

---

## 🎯 NEXT PHASE OBJECTIVES

### Priority 1: Immediate Tasks 🔴 CRITICAL
- [ ] No tasks specified

**Validation**:
```bash
python -m ruff check src/ tests/ --output-format=concise
python scripts/ci/mypy_baseline.py --require-baseline
python scripts/ci/auto_fix_common_issues.py --check-only
python scripts/ci/sync_tracked_files.py --fix
```

### Priority 2: Follow-Up Validation 🟡 HIGH
- [ ] No tasks specified

### Priority 3: Future Enhancements 🟢 MEDIUM
- [ ] No tasks specified

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

**When you see `@copilot continue` in PR #4288:**

1. Load this prompt from `.github/copilot-prompts/active/PR-4288-followup.md`
2. Execute Priority 1 tasks in order, validating each
3. Then execute Priority 2 tasks
4. Review Priority 3 tasks
5. Update this file after each task (add ✅ for completed)
6. Perform mandatory 5-pass self-review
7. Post comprehensive status as PR comment
8. Generate new continuation if work remains

**Self-Review Mandate**: Perform 5 comprehensive passes. Address ALL concerns until 0 issues remain. NEVER defer work without explicit reasoning and resolution plan.

---

**Generated**: 2026-05-05  
**Template Version**: 2.0.0  
**Last Updated**: 2026-05-05 19:38:16
