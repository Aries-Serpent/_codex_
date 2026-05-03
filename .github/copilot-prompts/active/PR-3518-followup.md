# 🎯 PR Follow-Up Tasks - #3518

**PR**: #3518 - PR #3518  
**Branch**: `dependabot/github_actions/hadolint/hadolint-action-3.3.0`  
**Author**: @dependabot[bot]  
**Date**: 2026-03-09  
**Commit**: `823da599998ea07a2f35a78a17f90434d6888b4b`  
**Status**: 🔄 ACTIVE

---

## 📋 PREVIOUS SESSION SUMMARY

### Completed Work
- [`823da599`] ci(deps): bump hadolint/hadolint-action from 3.1.0 to 3.3.0 (dependabot[bot], 2026-03-09)
- [`258b150a`] chore(vars): sync .codex/agent_context.json from repo variables [skip ci] (github-actions[bot], 2026-03-09)
- [`8bc91d68`] chore(vars): auto-sync variable audit report [skip ci] (github-actions[bot], 2026-03-09)

### Files Modified
No files modified

---

## 🎯 NEXT PHASE OBJECTIVES

### Priority 1: Immediate Tasks 🔴 CRITICAL
- [x] Verify PR was successfully merged to target branch
- [x] Confirm CI checks on target branch are green post-merge
- [ ] Run `python scripts/ci/auto_fix_common_issues.py --check-only` to verify no regressions
- [ ] Update `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` if any gaps found

**Validation**:
```bash
python scripts/ci/auto_fix_common_issues.py --check-only
python -m ruff check src/ tests/ --output-format=concise
python scripts/ci/mypy_baseline.py --require-baseline
```

### Priority 2: Follow-Up Validation 🟡 HIGH
- [ ] Confirm no CodeQL alerts were introduced by this PR (check GitHub Security tab)
- [ ] Verify `CHANGELOG.md` has an entry for this PR under `## [Unreleased]`
- [ ] Check that all review comments were addressed before merge
- [ ] Validate `sync_tracked_files.py --fix` passes cleanly on current main

### Priority 3: Future Enhancements 🟢 MEDIUM
- [ ] Archive this follow-up file once all Priority 1 & 2 tasks are confirmed complete
- [ ] Add any unresolved items as new issues in the repository
- [ ] Update `CODEQL-QUALITY-REMEDIATION.md` if this PR introduced or fixed CodeQL findings

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

**When you see `@copilot continue` in PR #3518:**

1. Load this prompt from `.github/copilot-prompts/active/PR-3518-followup.md`
2. Execute Priority 1 tasks in order, validating each
3. Then execute Priority 2 tasks
4. Review Priority 3 tasks
5. Update this file after each task (add ✅ for completed)
6. Perform mandatory 5-pass self-review
7. Post comprehensive status as PR comment
8. Generate new continuation if work remains

**Self-Review Mandate**: Perform 5 comprehensive passes. Address ALL concerns until 0 issues remain. NEVER defer work without explicit reasoning and resolution plan.

---

**Generated**: 2026-03-09  
**Template Version**: 2.0.0  
**Last Updated**: 2026-03-09 09:31:31
