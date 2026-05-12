# 🎯 PR Follow-Up Tasks - #4425

**PR**: #4425 - PR #4425  
**Branch**: `copilot/update-coverage-improvement-timeline`  
**Author**: @Copilot  
**Date**: 2026-05-12  
**Commit**: S965 in progress → final TBD  
**Status**: 🔄 ACTIVE — S965 in progress

---

## 📋 PREVIOUS SESSION SUMMARY

### Completed Work (S960–S965)
- [`2deb01d`] ✅ Security: Bandit 63→0 HIGH/MEDIUM (B605 command-injection, B306 insecure-temp, B314 XML, B113 resource-exhaustion, B108 /tmp, B310×55 urlopen, B608×8 SQL)
- [`98fda5a`] ✅ fix(s961): populate followup tasks, fix manifest timestamp, deduplicate archive log, add workflow observability
- [`a142c75`] ✅ fix(s961): use `steps.post_copilot_comment.outcome` for continue-on-error observability
- [`4cf58f0`] ✅ fix(s962): deduplicate archive_ops.jsonl (81→79 lines), rewrite followup.md as living doc, confirm workflow observability
- [`400fc3f`] ✅ fix(s963): populate PR-4425-followup.md with real tasks, resolve merge conflicts, update Pattern 25
- [`a3c6c2b`] ✅ fix(s964): `# pragma: allowlist secret` on commit-SHA constants in `process_workflow_runs.py` (lines 44–56)
- [S965] ✅ fix(s965): Pattern 25 fix; created `scripts/ci/verify_living_files.py`; updated living docs + CHANGELOG + AAAR
- All 4 copilot-pull-request-reviewer threads: **RESOLVED** ✅

### Review Thread Status
- ✅ `.codex/evidence/archive_ops.jsonl` lines 80-81 — RESOLVED (duplicate pair removed)
- ✅ `.github/copilot-prompts/active/PR-4425-followup.md` lines 24-33 — RESOLVED (tasks populated)
- ✅ `.github/workflows/agent-auth-delegation.yml` lines 2021-2031 — RESOLVED (observability step added)
- ✅ `CODEX_MANIFEST.json:3` — RESOLVED (timestamp monotonicity fixed)

### Local Validation (S965)
- `ruff check src/ tests/ --fix` → 0 violations ✅
- `sync_tracked_files --fix` → all consistent ✅
- `verify_living_files.py --strict` → all living files present and non-stale ✅
- `check_deferral_language.py --git-log` → 0 violations ✅
- mypy: 135 errors (known branch state, baseline=125)

---

## 🎯 NEXT PHASE OBJECTIVES

### Priority 1: Immediate Tasks 🔴 CRITICAL
- [ ] Continue CodeQL alert remediation (127 → 100 → 75 → 50 → 25 → 0) — fetch open alerts via GitHub MCP `list_code_scanning_alerts` and apply fixes in batch (API was rate-limited in S965; retry with fresh token)
- [ ] Run `python scripts/ci/verify_living_files.py --strict` before every final commit (script now exists at `scripts/ci/verify_living_files.py`)
- [ ] Confirm Pattern 25: CHANGELOG.md + AGENT_ACCOUNTABILITY_REPORT.md updated in EVERY commit — including session plan / context commits
- [ ] Run `python -m ruff check src/ tests/ --fix` (must show 0 violations before push)
- [ ] Continue Bandit/CodeQL sweep toward 0 open alerts

**Validation** (run all before push):
```bash
python scripts/ci/verify_living_files.py --strict
python -m ruff check src/ tests/ --output-format=concise
python scripts/ci/mypy_baseline.py --require-baseline
python scripts/ci/auto_fix_common_issues.py --check-only
python scripts/ci/sync_tracked_files.py --fix
```

### Priority 2: Follow-Up Validation 🟡 HIGH
- [ ] Expand living-files hardening to cover new PR-number transitions automatically (update `scripts/generate_pr_followup.py` to preserve real content across regenerations)
- [ ] Run `python scripts/ci/mypy_baseline.py --require-baseline` — known 135 vs 125 baseline, document as known branch state

### Priority 3: Future Enhancements 🟢 MEDIUM
- [ ] Reduce mypy error count from 135 → 125 (return to baseline) by fixing type annotation regressions
- [ ] After CodeQL remediation complete: update PR description with final count

---

## ✅ EXECUTION CHECKLIST

- [ ] All Priority 1 tasks completed and validated
- [ ] All Priority 2 tasks completed or documented
- [ ] Priority 3 tasks reviewed and prioritized
- [ ] All validation checks passed
- [ ] Documentation updated
- [ ] Self-review completed (5 passes, 0 concerns)

---

## 🤖 COPILOT AGENT INSTRUCTIONS

**When you see `@copilot continue` in PR #4425:**

1. Load this prompt from `.github/copilot-prompts/active/PR-4425-followup.md`
2. Execute Priority 1 tasks in order, validating each
3. Then execute Priority 2 tasks
4. Update this file after each task (add ✅ for completed)
5. Confirm Pattern 25: CHANGELOG.md + AGENT_ACCOUNTABILITY_REPORT.md in same commit
6. Post comprehensive status as PR comment

**Self-Review Mandate**: Perform 5 comprehensive passes. Address ALL concerns until 0 issues remain.

---

**Generated**: 2026-05-12  
**Template Version**: 2.1.0  
**Last Updated**: 2026-05-12 19:50Z (S966)
