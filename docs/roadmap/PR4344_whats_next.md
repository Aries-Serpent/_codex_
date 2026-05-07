# PR #4344 — What's Next

> **Last updated:** 2026-05-07T22:55Z — Session 45
> **Status:** 🟡 In progress — review-thread fixes applied, CI healing/monitoring active

## Current Objectives

- Complete iterative self-healing loop for `copilot/fix-deprecated-imports`.
- Apply all actionable review-thread comments on PR #4344.
- Keep PR #4344 living docs, accountability, and changelog synchronized each push.

## Session 45 Snapshot

- Investigated `Auto-Fix Common CI Issues` failure run `25525872834` (head `1eb01cc`).
- Confirmed current branch state now reports no auto-fixable issues:
  - `python scripts/ci/auto_fix_common_issues.py --check-only` ✅
  - `python scripts/ci/session_wrapup_autofix.py --pr-number 4344` ✅
- Applied review-thread adjustments:
  - `src/codex/utils/subprocess.py` — return typing now reflects `text=True/False` via overloads.
  - `tests/mcp/test_utilities.py` — cleanup warning now uses module-scoped logger.
  - `.github/copilot-prompts/active/PR-4344-followup.md` — timestamp normalized to ISO-8601 UTC.

## Repository Living-Docs Inventory (gathered this session)

### `whats_next`
- `docs/roadmap/PR4289_whats_next.md`
- `docs/roadmap/PR4317_whats_next.md`
- `docs/roadmap/PR4323_whats_next.md`
- `docs/roadmap/PR4343_whats_next.md`
- `docs/roadmap/PR4344_whats_next.md` (this PR)

### `session_diagram`
- `docs/sessions/PR4289_session_diagram.md`
- `docs/sessions/PR4317_session_diagram.md`
- `docs/sessions/PR4323_session_diagram.md`
- `docs/sessions/PR4343_session_diagram.md`
- `docs/sessions/PR4344_session_diagram.md` (this PR)
