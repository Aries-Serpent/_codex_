# PR #4434 — S990 Continuation Prompt

> **Generated:** 2026-05-13T05:50Z | **Session:** S987-S989 | **Branch:** `copilot/verify-codeql-alerts-and-sweep`

## Context

Sessions S987-S989 completed:
- ✅ 20 CodeQL quick-win fixes (6 `py/ineffectual-statement` + 14 unused-global/import)
- ✅ `scripts/ci/_gh_api.py` — shared rate-limit + TTL disk cache layer
- ✅ `scripts/ci/fetch_security_snapshot.py` — unified security data fetcher
- ✅ `codeql-alert-fetcher.yml` — multi-stage pipeline (collect/autofix/prompt) with `actions/cache`
- ✅ `wec_enforcer.py` — `_WORKFLOW_DEFAULT_INPUTS` for explicit pipeline dispatch
- ✅ PR template WEC checkbox + self-healing trigger registered
- ✅ `docs/reference/SECURITY_API_REFERENCE.md` + `CODEQL_FETCHER_WORKFLOW_GUIDE.md` (7 Mermaid diagrams)
- ✅ Pattern 25/30 satisfied, living docs updated

## Priority Tasks for S990

### P1 — Validate the pipeline end-to-end
1. Trigger `codeql-alert-fetcher.yml` via UI or check `- [x] codeql-alert-fetcher.yml` in the PR WEC section.
2. Verify artifact uploads and contains `AGENT_SECURITY_CONTEXT.md`.
3. Verify `@copilot` prompt was posted to PR #4434.
4. Check Security tab for Copilot Autofix suggestions; review and commit any AI-generated fixes.

### P2 — Continue CodeQL alert reduction (next 20)
Using `codeql/alerts_fixable.md` from the latest artifact:
1. Fix next batch of `py/unused-import` and `py/unused-global-variable` alerts.
2. Fix any remaining `py/ineffectual-statement`.
3. Target `py/clear-text-logging-sensitive-data` or `py/path-injection` if present.

### P3 — Dependabot remaining alerts
1. Open `dependabot/alerts_critical.json` from the latest snapshot.
2. Update `requirements/*.txt` or `pyproject.toml` for each critical/high package.
3. Verify patched versions with `gh-advisory-database` tool before pinning.

### P4 — `fetch_security_snapshot.py` validation
```bash
GH_TOKEN=$CODEX_MASTER_KEY python scripts/ci/fetch_security_snapshot.py \
  --types autofix --out-dir /tmp/test_snap --autofix-max 3 \
  --autofix-severities critical,error
```

### P5 — WEC `_WEC_ITEMS` discrepancy
Add `template_lint.yml` to `session_wrapup_autofix.py` after `audit-qa-suite.yml` (before `codeql-alert-fetcher.yml`) to match the PR template.

## Session Start Checklist
```
[ ] git log --oneline -5                                    # verify Pattern 25
[ ] tail -1 .codex/aftermath/pda_iterations.jsonl           # check PDA date (Pattern 30)
[ ] python scripts/ci/sync_tracked_files.py --check
[ ] python scripts/ci/auto_fix_common_issues.py --check-only
[ ] python scripts/ci/verify_living_files.py --pr-number 4434 --strict
```

## Key New Files
- `scripts/ci/_gh_api.py` — HTTP helper; `CODEX_API_CACHE_DISABLED=1` to bypass cache
- `scripts/ci/fetch_security_snapshot.py` — `--types dependabot,secrets,policy,analyses,autofix,context,all`
- `docs/reference/CODEQL_FETCHER_WORKFLOW_GUIDE.md` — full pipeline docs with Mermaid diagrams
- `docs/reference/SECURITY_API_REFERENCE.md` — GitHub Security API catalog
