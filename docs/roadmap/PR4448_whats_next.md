# PR #4450 — What's Next

**Branch:** `0D_base_` → `main`  
**Session:** S1003 · 2026-05-13T21:50Z  
**Objective:** Reduce CodeQL Security + Quality alerts < 25 (path to 0)  
**Merge-readiness:** ~96/100 pre-sprint; new CodeQL scan pending after push

---

## ✅ Completed This Session (S1003)

| # | Task | Status |
|---|------|--------|
| 1 | `py/unused-local-variable` (41) — RUF059 sweep + 4 manual fixes in tests/ | ✅ Done |
| 2 | `py/import-and-import-from` (1) — consolidated `logging_utils` import | ✅ Done |
| 3 | `py/ineffectual-statement` (2) — added `...` to Protocol methods in `embeddings.py` | ✅ Done |
| 4 | `py/uninitialized-local-variable` (1) — reordered import before inner fn in `test_peft_utils.py` | ✅ Done |
| 5 | `actions/missing-workflow-permissions` (21 workflows) — added permissions blocks | ✅ Done |
| 6 | `actions/unpinned-tag` (24 refs) — pinned all _resolvable_ actions to full commit SHAs | ✅ Done |
| 7 | `labeler.yml` YAML syntax fix | ✅ Done |
| 8 | Hotfix: reverted bad SHA for `actions/create-github-app-token@v3` (4 files) | ✅ Done |
| 9 | CHANGELOG + AGENT_ACCOUNTABILITY_REPORT updated | ✅ Done |
| 10 | Living docs refreshed | ✅ Done |

## 📊 Alert Count Trajectory

| Date | Est. Open | Session | Key Fixes |
|------|:---------:|---------|-----------|
| 2026-05-12 | 127 | Initial inventory | — |
| 2026-05-13 S995–S1002 | ~120 | Unused-global fixes, src/ RUF059 sweep | -7 |
| 2026-05-13 S1003 | **~54** | Bulk Python quality + GitHub Actions permissions/pinning | **-66** |

> ⚠️ `actions/create-github-app-token@v3` reverted to tag in 4 files — still 1 unpinned tag remaining

## 🔲 Next Session Priorities (path to 0)

### Priority 1 — Verify New CodeQL Count
After the CodeQL scan on commit `0d78bc5` / hotfix completes:
```bash
# Check current open alerts via API or artifact
python scripts/ci/check_codeql_alerts.py --count
```
Expected: < 25 open alerts ✅ (goal met) or identify remaining batch

### Priority 2 — `actions/create-github-app-token@v3` (4 files)
Need the correct full-commit SHA for v3.1.1:
```bash
# Lookup via GitHub API (requires CODEX_MASTER_KEY):
curl -H "Authorization: Bearer $GH_TOKEN" \
  https://api.github.com/repos/actions/create-github-app-token/git/ref/tags/v3.1.1
```
Files to update: `auto-approve-workflows.yml`, `self-approve-pending-runs.yml`, `agent-auth-delegation.yml`, `process-variable-intents.yml`

### Priority 3 — Remaining Python CodeQL (if still open)
- `py/unused-global-variable` (~4) — `mlflow_guard.py` lines 8–12, `stores/__init__.py:9`
- `py/undefined-export` (~8) — `src/codex/retrieval/__init__.py` (may be stale — already fixed)
- `py/unused-import` (~8) — `tests/cognitive_brain/` files (may be stale)
- `py/import-and-import-from` (2 remaining) — `test_sentencepiece_contract.py:71`, `test_data_utils.py:267`

### Priority 4 — GitHub Actions (residual)
- `actions/untrusted-checkout/medium` (2) — `forward-sync-autogen.yml` + `app-package-download.yml`
- `actions/syntax-error` (1) — `.github/actions/doc-test-scribe-action/action.yml:201`
- `consolidated-pr-status.yml`: `actions/github-script@v9` — needs SHA lookup

### Priority 5 — Merge to main
Once CodeQL confirms < 25 alerts:
```
@copilot CTEP Mode: ON
Merge PR #4450 (0D_base_ → main) — all gates green, score ≥ 96/100
```

---
_Living doc — last updated S1003-b · 2026-05-13T21:50Z_
