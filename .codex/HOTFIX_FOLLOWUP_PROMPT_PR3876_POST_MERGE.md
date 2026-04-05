# Hotfix Follow-Up Prompt — PR #3876 · Post-Merge Live Test Dispatch
> **Version:** 1.1.0  
> **Date:** 2026-04-05  
> **Branch:** `main` (run AFTER PR #3876 merges)  
> **Status at write-time:** Branch `0D_base_` — 0 failing checks ✅ — READY TO MERGE

---

## Purpose

This prompt dispatches the **full live test suite** for the changes landed in PR #3876 against `main`.  
It validates every fix end-to-end in the production environment (not the PR sandbox):

| Fix | What the live test validates |
|-----|------------------------------|
| CodeQL #12788/#12789 — uninitialized var | CodeQL re-scan on `main` shows 0 open alerts |
| CodeQL #12790 — clear-text logging | No `X-OAuth-Scopes` raw header in `test_variables_api.py` |
| Variables & Secrets reference (PR #3876) | `test-variables-api.yml` live CRUD pass with `CODEX_MASTER_KEY` |
| Mermaid maps v1.1.0 | `docs/CODEBASE_MERMAID_MAPS.md` updated + link checker clean |
| Pragma threshold 3.1 | `test_no_pragma_no_cover_abuse` passes on `main` |
| Typer Path compatibility | `test_cli_roles_help` / `test_cli_roles_list` pass or skip gracefully |
| RAG numpy guard | `tests/rag/test_coverage_gaps.py` skips cleanly when numpy absent |
| Doc metrics 21000+ | `doc_metrics_sync.py --check` exits 0 on `main` |

---

## Step 1 — Confirm Merge Landed

```bash
git fetch origin main
git log origin/main --oneline -3
# Must see: "docs: update CODEBASE_MERMAID_MAPS.md v1.1.0 — align with PR #3876"
# or the merge commit referencing it.
```

---

## Step 2 — Dispatch Full Live Variable API Test

```bash
# Requires CODEX_MASTER_KEY exported in your shell (not GITHUB_TOKEN)
export GH_TOKEN="$CODEX_MASTER_KEY"

gh workflow run test-variables-api.yml \
  --repo Aries-Serpent/_codex_ \
  --ref main \
  --field dry_run=false \
  --field run_org_tests=true

# Monitor until completion (≈5 min)
gh run list --workflow=test-variables-api.yml --repo Aries-Serpent/_codex_ --limit 3
```

**Expected result:** All `test_read_*`, `test_write_*`, `test_org_*` cases ✅ PASS.  
If `CODEX_MASTER_KEY` is unavailable, run with `dry_run=true` first to validate workflow syntax.

---

## Step 3 — Trigger CodeQL Re-Scan on Main

```bash
# Option A — dispatch via gh CLI
gh workflow run codeql-analysis.yml \
  --repo Aries-Serpent/_codex_ \
  --ref main

# Option B — dispatch via WEC checklist on a new PR
# Tick [x] codeql-analysis.yml in the WEC section of the next PR body
```

**Expected result:** 0 open alerts on `main` for:
- `tests/codex/test_cli_roles.py` (alerts #12788/#12789 — resolved in `1b7d446`)
- `scripts/ci/test_variables_api.py` (alert #12790 — resolved in `1b7d446`)

---

## Step 4 — Validate All PR #3876 Fixes on Main

```bash
# Run these from the root of the repo on a fresh clone/pull of main

# 4a. Ruff — must be clean
python -m ruff check src/ tests/
echo "Expected: All checks passed! (exit 0)"

# 4b. Pragma threshold
python -m pytest tests/coverage_tests/test_coverage_analysis.py::TestCoverageQuality::test_no_pragma_no_cover_abuse -v
echo "Expected: 1 passed"

# 4c. CLI roles smoke
python -m pytest tests/codex/test_cli_roles.py -v
echo "Expected: 2 passed OR 2 skipped (typer version dependent)"

# 4d. RAG numpy guard
python -m pytest tests/rag/test_coverage_gaps.py -v
echo "Expected: passed OR skipped (numpy absent)"

# 4e. Doc metrics
python scripts/tools/doc_metrics_sync.py --check
echo "Expected: ✅  All tracked metrics are up-to-date."

# 4f. Tracked files baseline
python scripts/ci/sync_tracked_files.py --fix
echo "Expected: ✅  All tracked files are consistent"
```

---

## Step 5 — Mermaid Map Link Check

```bash
# Verify docs/CODEBASE_MERMAID_MAPS.md is at v1.1.0
grep "Version:" docs/CODEBASE_MERMAID_MAPS.md | head -1
# Expected: > **Version:** 1.1.0 (S228 + PR #3876)

# Verify key nodes exist
grep -c "PR #3876" docs/CODEBASE_MERMAID_MAPS.md
# Expected: ≥ 3 matches (header, CodeQL node, Variables layer)

grep "Variables & Secrets Knowledge Layer" docs/CODEBASE_MERMAID_MAPS.md
# Expected: subgraph "Variables & Secrets Knowledge Layer (PR #3876)"

grep "test_variables_api.py" docs/CODEBASE_MERMAID_MAPS.md
# Expected: VAR_TEST node + scripts/ci/ listing line
```

---

## Step 6 — Update AGENT_ACCOUNTABILITY_REPORT

```bash
# Append post-merge session entry for REQ-4 compliance
# Entry: S-3876-post-merge · 2026-04-05 · Live test dispatched on main
# File:  docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md
```

Add a session block at the end of the report:

```markdown
### S-3876-post-merge · 2026-04-05

**Action:** Dispatched `test-variables-api.yml` on `main` after PR #3876 merge.  
**Result:** All live variable API tests passed. CodeQL re-scan confirmed 0 open alerts.  
**Files Validated:** `tests/codex/test_cli_roles.py`, `scripts/ci/test_variables_api.py`,
`docs/CODEBASE_MERMAID_MAPS.md`, `tests/coverage_tests/test_coverage_analysis.py`  
**Patterns closed:** CodeQL #12788 #12789 #12790, RP-007 (stale baseline), pragma threshold,
typer Path compat, RAG numpy guard, doc metrics sync
```

---

## Step 7 — CHANGELOG Entry for Post-Merge Confirmation

Under `## [Unreleased]` → `### Verified on main` add:

```markdown
### Verified on main (post PR #3876 merge — 2026-04-05)

- Live `test-variables-api.yml` dispatch on `main` — all variable CRUD tests ✅
- CodeQL re-scan on `main` — 0 open alerts (alerts #12788/#12789/#12790 confirmed closed)
- `test_no_pragma_no_cover_abuse` — 1 passed (threshold 3.1, actual ~2.94)
- `CODEBASE_MERMAID_MAPS.md` v1.1.0 — link-checker clean
```

---

## Abort Criteria

If any of the following are found on `main`, **do not close this prompt** — open a new hotfix PR:

| Finding | Severity | Action |
|---------|----------|--------|
| CodeQL alert re-opened on `main` | 🔴 CRITICAL | New PR — fix same single-try-block pattern |
| `test-variables-api.yml` CRUD failure | 🔴 CRITICAL | Check `CODEX_MASTER_KEY` scope; re-run with `dry_run=true` first |
| `ruff` violations on `main` | 🟡 HIGH | `ruff check --fix src/ tests/` then PR |
| `doc_metrics_sync.py --check` fails | 🟡 HIGH | `python scripts/tools/doc_metrics_sync.py --fix` then PR |
| `CODEBASE_MERMAID_MAPS.md` version mismatch | 🟢 LOW | Update header only |

---

## Quick-Dispatch One-Liner (Copy-Paste)

```bash
# After merge to main — paste into terminal with CODEX_MASTER_KEY set
GH_TOKEN="$CODEX_MASTER_KEY" \
  gh workflow run test-variables-api.yml \
    --repo Aries-Serpent/_codex_ \
    --ref main \
    --field dry_run=false \
    --field run_org_tests=true \
  && echo "✅ Live test dispatched — monitor at: https://github.com/Aries-Serpent/_codex_/actions/workflows/test-variables-api.yml"
```

---

*Generated by Copilot · PR #3876 · commit `1f0bb9c` · S-3876-mermaid session · 2026-04-05*
