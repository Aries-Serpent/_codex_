# PR #4450 — What's Next

**Branch:** `0D_base_` → `main`  
**Session:** S1003 · 2026-05-13T21:30Z  
**Objective:** Reduce CodeQL Security + Quality alerts < 25 (path to 0)  
**Merge-readiness:** 96/100 (pre-S1003 push) — re-score pending CI

---

## ✅ Completed This Session (S1003)

| # | Task | Status |
|---|------|--------|
| 1 | `py/unused-local-variable` (41) — RUF059 sweep + 4 manual fixes in tests/ | ✅ Done |
| 2 | `py/import-and-import-from` (1) — consolidated `logging_utils` import | ✅ Done |
| 3 | `py/ineffectual-statement` (2) — added `...` to Protocol methods in `embeddings.py` | ✅ Done |
| 4 | `py/uninitialized-local-variable` (1) — reordered import before inner function in `test_peft_utils.py` | ✅ Done |
| 5 | `actions/missing-workflow-permissions` (21 workflows) — added `permissions:` blocks | ✅ Done |
| 6 | `actions/unpinned-tag` (24 refs) — pinned to full commit SHAs | ✅ Done |
| 7 | `labeler.yml` YAML syntax fix (malformed step entry) | ✅ Done |
| 8 | CHANGELOG + AGENT_ACCOUNTABILITY_REPORT updated | ✅ Done |
| 9 | Replied to all `<comment_new>` PR comments | ✅ Done |

## 📊 Alert Count Trajectory

| Date | Inventory | Session | Δ |
|------|-----------|---------|---|
| 2026-05-12 | 127 | Initial inventory | — |
| 2026-05-13 (S995-S1002) | ~120 | CodeQL unused-global fixes, RUF059 in src/ | -7 |
| 2026-05-13 (S1003) | ~54 | Bulk Python quality + GitHub Actions permissions/pinning | -66 |
| **Target** | **< 25** | Remaining: actions/unpinned-tag residuals + Python alerts post-inventory | — |

## �� Next Session Priorities (path to 0)

### Priority 1 — Verify CI Green & Get Updated Alert Count
```
@copilot CTEP Mode: ON
1. Wait for CodeQL workflow to complete on latest push
2. Run: python scripts/ci/check_codeql_alerts.py --count
3. Confirm alert count < 25
```

### Priority 2 — Remaining `actions/unpinned-tag` (est. ~9 left)
- `consolidated-pr-status.yml`: `actions/github-script@v9` — needs SHA lookup
- Scan all `.github/workflows/` for any remaining unpinned `@vN` tags
```bash
grep -rn "uses:.*@v[0-9]" .github/workflows/ | grep -v "#.*[a-f0-9]\{40\}"
```

### Priority 3 — Remaining Python CodeQL
- `py/unused-global-variable` (~4 in mlflow_guard.py, stores/__init__.py) — verify if still open post-S1003
- `py/undefined-export` (~8 in retrieval/__init__.py) — verify if still open (may already be fixed)
- `py/unused-import` (~8 in cognitive_brain tests) — check if stale

### Priority 4 — `actions/untrusted-checkout/medium` (2 alerts)
- `forward-sync-autogen.yml` + `app-package-download.yml` — redesign to avoid checking out untrusted code

### Priority 5 — `actions/syntax-error` (1 alert)
- `.github/actions/doc-test-scribe-action/action.yml:201` — fix syntax

### Success Criteria
- [ ] CodeQL open alerts < 25 (confirmed by CI scan)
- [ ] All Python quality alerts resolved
- [ ] All GitHub Actions permissions alerts resolved
- [ ] Merge PR #4450 into main

---
_Living doc — last updated S1003 · 2026-05-13T21:35Z_
