# 🎯 PR Follow-Up Tasks - #4502

**PR**: #4502
**Branch**: `copilot/review-codebase-for-quick-wins`
**Author**: @Copilot
**Date**: 2026-05-19
**Commit**: `0ccea56009673527cba9cd22ab3cedf57a3a3006`
**Status**: 🔄 ACTIVE

---

## 📋 PREVIOUS SESSION SUMMARY

### Completed Work
- [`0ccea560`] chore: fix Pattern 25 accountability drift (auto-fix) (copilot-swe-agent[bot], 2026-05-19)
- [`5ec9eae8`] Initial plan (copilot-swe-agent[bot], 2026-05-19)
- [`283f5d74`] Merge pull request #4501 from Aries-Serpent/copilot/fix-tracing-function-reference (Statix, 2026-05-18)

### Files Modified
- No files modified in the last recorded session

---

## 🎯 NEXT PHASE OBJECTIVES

### Priority 1: Immediate Tasks 🔴 CRITICAL
- [ ] Finish full Session D runtime rerun to terminal pytest summary and bucket failures
- [ ] Land minimal fix for the highest-frequency non-heavy-dependency runtime bucket
- [ ] Re-check CI after `70359ee` and clear remaining blocking gates
- [ ] Re-run the CI rescue validation set and confirm clean status
- [ ] Validate `promote-integration-branch.yml` dispatch to `main` with current `source_sha` (token-scope dependent)
- [ ] Verify WEC-driven automation/checks via report console with SHA correlation
- [ ] Continue worker-stability follow-up after runtime fixes
- [ ] Keep continuation docs, changelog, and accountability synchronized
- [ ] Address outstanding review feedback linked to PR #4502
- [ ] Re-attempt cancellation of stale old-SHA in-progress comment-triggered runs when rate budget permits
- [ ] Keep workflow-misfire prevention active (divergence check, rebase-first, live WEC sourcing)

### Priority 2: Follow-Up Validation 🟡 HIGH
- [ ] Re-run targeted validation after the runtime fix lands
- [ ] Confirm tracked-file/accountability freshness remains green
- [ ] Verify no new workflow pin or comment drift was introduced

### Priority 3: Future Enhancements 🟢 MEDIUM
- [ ] Review remaining follow-up work after CI is green

---

## ▶️ CONTINUATION PROMPTS

**For this PR:**
```text
@copilot continue with next phase tasks for PR #4502:
- monitor approval-dispatched queue outcomes
- keep tracked-file/accountability freshness intact
- reserve final 5 minutes for wrap-up and handoff
```

**For immediate post-merge follow-up (if needed):**
```text
@copilot continue in a new PR for post-merge stabilization:
- verify main-branch CI on the merge SHA
- close residual follow-up tasks from PR #4502
- refresh living docs + accountability in the new PR context
```

---

## ✅ VALIDATION COMMANDS

```bash
python -m ruff check src/ tests/ --output-format=concise
python scripts/ci/mypy_baseline.py --require-baseline
python scripts/ci/auto_fix_common_issues.py --check-only
python scripts/ci/sync_tracked_files.py --fix
```

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

**CRITICAL**: Perform 5 comprehensive self-review passes before concluding.

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

**Failure Protocol**: If any checkpoint fails, document the issue, create a resolution plan, execute it within the current session, and re-run until all checks clear.

---

## 🤖 COPILOT AGENT INSTRUCTIONS

When you see `@copilot continue` in PR #4502:
1. Load this prompt from `.github/copilot-prompts/active/PR-4502-followup.md`
2. Execute Priority 1 tasks in order, validating each change
3. Execute Priority 2 tasks next, then review Priority 3 tasks
4. Update this file after each meaningful step
5. Perform the mandatory 5-pass self-review
6. Post a comprehensive PR status comment
7. Generate a new continuation prompt if work remains

**Generated**: 2026-05-19
**Template Version**: 2.0.0
**Last Updated**: 2026-05-19T05:59:36Z
