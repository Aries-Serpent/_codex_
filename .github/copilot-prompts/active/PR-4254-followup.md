# 🎯 PR Follow-Up Tasks - #4254

**PR**: #4254 - PR #4254  
**Branch**: `copilot/consolidate-pytorch-versions`  
**Author**: @mbaetiong  
**Date**: 2026-05-04  
**Commit**: `f026e67319ffc6f56a64b5c0b49096f8830605be`  
**Status**: 🔄 ACTIVE

---

## 📋 PREVIOUS SESSION SUMMARY

### Completed Work
- [`f026e673`] chore(manifest): auto-refresh CODEX_MANIFEST.json [skip ci] (github-actions[bot], 2026-05-04)
- [`a1d3502f`] Initial plan (copilot-swe-agent[bot], 2026-05-04)
- [`533471e4`] fix(ci): auto-sync .secrets.baseline and add pragma to test false-positives [skip ci] (copilot-swe-agent[bot], 2026-05-04)

### Files Modified
- `requirements/lock-ml.txt` — torch version pin updated (2.9.1+cpu → 2.11.0+cpu)
- `tests/unit/utils/test_sensitive_data_utils.py` — pragma deduplication, new phone test, hash uniqueness edge cases

---

## 🎯 NEXT PHASE OBJECTIVES

### Priority 1: Immediate Tasks 🔴 CRITICAL
- [ ] Verify `requirements/lock-ml.txt` torch pin (`2.11.0+cpu`) is reachable from `https://download.pytorch.org/whl/cpu`
- [ ] Confirm all existing tests in `tests/unit/utils/test_sensitive_data_utils.py` pass (including new `test_mask_sensitive_data_phone_unformatted`)
- [ ] Run `python scripts/ci/sync_tracked_files.py --fix` if `.secrets.baseline` is stale after bot commits

**Validation**:
```bash
python -m ruff check src/ tests/ --output-format=concise
python scripts/ci/mypy_baseline.py --require-baseline
python scripts/ci/auto_fix_common_issues.py --check-only
python scripts/ci/sync_tracked_files.py --fix
```

### Priority 2: Follow-Up Validation 🟡 HIGH
- [ ] Ensure `requirements/base.txt` and `requirements/lock.txt` torch pins remain consistent with `lock-ml.txt` across future dependency updates
- [ ] Consider adding Unicode normalization test (precomposed vs. decomposed `é`) to `test_hash_sensitive_value_uniqueness` as a future enhancement (flagged by code reviewer)

### Priority 3: Future Enhancements 🟢 MEDIUM
- [ ] Add Unicode normalization edge-case test (`\u00e9` precomposed vs `e\u0301` decomposed) to verify security-relevant hash distinctness
- [ ] Document intentional CPU-only vs full-CUDA torch pin split in requirements README if multiple deployment targets are maintained

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

**When you see `@copilot continue` in PR #4254:**

1. Load this prompt from `.github/copilot-prompts/active/PR-4254-followup.md`
2. Execute Priority 1 tasks in order, validating each
3. Then execute Priority 2 tasks
4. Review Priority 3 tasks
5. Update this file after each task (add ✅ for completed)
6. Perform mandatory 5-pass self-review
7. Post comprehensive status as PR comment
8. Generate new continuation if work remains

**Self-Review Mandate**: Perform 5 comprehensive passes. Address ALL concerns until 0 issues remain. NEVER defer work without explicit reasoning and resolution plan.

---

**Generated**: 2026-05-04  
**Template Version**: 2.0.0  
**Last Updated**: 2026-05-04 13:45:03
