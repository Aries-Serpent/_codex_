# PR #4344 — What's Next

> **Last updated:** 2026-05-07T23:14Z — Session 46
> **Status:** 🟡 In progress — additional bot findings remediated, CI rescue checks re-validated

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

## Session 46 Snapshot

- Reviewed newly posted blocking comments and bot review threads.
- Investigated additional failing/blocked runs via MCP:
  - `25526331831` (`Comment review gate`) — failed job log retrieval returned `403`.
  - `25525385592` (`Fast Validation`) — failed job log retrieval returned `403`.
- Applied additional code-quality/security-thread remediations:
  - `tests/hhg_logistics/serve/test_app.py` — removed unreachable defensive `try/except` in torch context test.
  - `tests/mcp/test_utilities.py` — removed redundant no-op `pass` in `capture_log_output`.
  - `src/codex/utils/subprocess.py` — converted overload bodies from `...` to `pass` and hardened type-only `CompletedProcess` annotations via `TYPE_CHECKING` import.
  - `scripts/ci/auto_fix_common_issues.py` — fixed `E741` ambiguous variable naming in exception classifier path.
- Validation status:
  - `python3 -m ruff check` ✅
  - `python3 -m pytest -x` ❌ currently stops at `tests/logging/test_registry_logger.py::test_registry_ndjson_logger_includes_system_metrics`
  - `python -m ruff check src/ tests/ --fix` ✅
  - `python scripts/ci/mypy_baseline.py --require-baseline` ✅ (`126 == baseline 126`)
  - `python scripts/ci/auto_fix_common_issues.py --check-only` ✅

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
