# 🎯 PR Follow-Up Tasks - #4470

**PR**: #4470  
**Branch**: `0D_base_`  
**Author**: @mbaetiong  
**Date**: 2026-05-14  
**Commit**: `38a4967486b28826c5378e8cc6888ab810b2112d`  
**Status**: 🔄 ACTIVE

---

## 📋 PREVIOUS SESSION SUMMARY

### Completed Work
- [`38a49674`] chore(manifest): auto-refresh CODEX_MANIFEST.json [skip ci] (github-actions[bot], 2026-05-14)
- [`96a7406e`] Merge pull request #4469 from Aries-Serpent/copilot/fix-deprecated-utcfromtimestamp (Statix, 2026-05-14)
- [`87866724`] test: align connection pool state with review feedback (copilot-swe-agent[bot], 2026-05-14)

### Files Modified
- `.codex/agent_auth_session.json`
- `.codex/CODEX_MANIFEST.json`
- `.codex/session_context_latest.md`
- `.github/copilot-prompts/active/PR-4468-followup.md`
- `.github/copilot-prompts/active/PR-4469-followup.md`
- `.github/copilot-prompts/active/PR-4470-followup.md`
- `CHANGELOG.md`
- `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md`
- `tests/agents/test_phase2_deep_coverage_batch11.py`
- `tests/api/test_auth_token_lifecycle.py`

---

## 🎯 NEXT PHASE OBJECTIVES

### Priority 1: Immediate Tasks 🔴 CRITICAL
- [ ] Align WEC execution with iterative plan path:
  1. Parse PR WEC block
  2. Validate always-required checks
  3. Validate workflow active/non-active state integrity
  4. Dispatch newly checked workflows
  5. Approve pending `action_required` runs
  6. Post execution-plan summary comment
- [ ] Identify and track merge-required WEC workflows that are currently non-active in Actions.
- [ ] Verify WEC is hardened for Copilot selection-by-checkbox on PR approval flow.
- [ ] Prepare a general tailored operator prompt for repeatable Copilot WEC sessions.

**Current non-active WEC workflows requiring enablement in Actions (live audit):**
- [ ] `nox_gates.yml` (`disabled_manually`)
- [ ] `pr-checks.yml` (`disabled_manually`)
- [ ] `docker-build-push.yml` (`disabled_manually`)
- [ ] `html_visual_regression.yml` (`disabled_manually`)
- [ ] `template_lint.yml` (`disabled_manually`)
- [ ] `codeql-alert-fetcher.yml` (`disabled_manually`)
- [ ] `copilot-iterative-self-healing.yml` (`disabled_manually`)

**Enable command (requires token with `actions:write`, e.g. `CODEX_MASTER_KEY`):**
```bash
GH_TOKEN="$CODEX_MASTER_KEY" gh api --method PUT repos/Aries-Serpent/_codex_/actions/workflows/<workflow_id>/enable
```

**General tailored prompt (WEC iterative execution):**
> "Run WEC execution in strict iterative order: parse current PR checklist, validate always-required checks, validate selected + merge-required workflow active states, stop on non-active workflow findings with explicit list, dispatch newly checked workflows only, approve pending action_required runs, and post/update one gate summary comment with run/skip and remediation actions."

**Validation**:
```bash
python -m ruff check scripts/ci/wec_enforcer.py
python -m ruff check .github/workflows/workflow-execution-gate.yml
python scripts/ci/wec_enforcer.py --validate-body --pr 4470
```

### Priority 2: Follow-Up Validation 🟡 HIGH
- [ ] Confirm WEC summary comment stays single-anchor (upsert behavior).
- [ ] Confirm token chain uses `CODEX_MASTER_KEY || CODEX_BACKUP_KEY || github.token` for checklist parsing and summary posting.
- [ ] Re-audit non-active workflow set after any manual workflow enablement action.

### Priority 3: Future Enhancements 🟢 MEDIUM
- [ ] Add automated daily report artifact for `merge-required but non-active` workflows.
- [ ] Add optional WEC mermaid map in PR summary comments for rapid operator understanding.

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

**When you see `@copilot continue` in PR #4470:**

1. Load this prompt from `.github/copilot-prompts/active/PR-4470-followup.md`
2. Execute Priority 1 tasks in order, validating each
3. Then execute Priority 2 tasks
4. Review Priority 3 tasks
5. Update this file after each task (add ✅ for completed)
6. Perform mandatory 5-pass self-review
7. Post comprehensive status as PR comment
8. Generate new continuation if work remains

**Self-Review Mandate**: Perform 5 comprehensive passes. Address ALL concerns until 0 issues remain. NEVER defer work without explicit reasoning and resolution plan.

---

**Generated**: 2026-05-14  
**Template Version**: 2.0.0  
**Last Updated**: 2026-05-14 21:43:41
