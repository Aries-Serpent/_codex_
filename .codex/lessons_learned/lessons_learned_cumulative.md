
## Session: S163
**Date**: 2026-03-19T22:39:00Z
**Context**: Autonomous branch-divergence resolution, integration branch model hardening — PR helper bot, auto-merge, REQ-11 guard, session-chain workflow

### Lessons Learned

- **Bot-skip-ci auto-merge prevents spurious REQ-10 blocks**: Five scheduled workflows commit [skip ci] metadata to main every 2–24h; implementing all_skip_ci_bot_commits() + Merges API auto-merge in branch_rebase_check.py eliminates the REQ-10 divergence cycle without human intervention
- **PIPESTATUS masking in piped commands silently drops exit codes**: cmd | tee always exits 0; must use explicit if [ "${PIPESTATUS[0]}" -ne 0 ] block so fallback logic actually fires in iterative-self-healing-ci.yml
- **REQ-11 integration-branch guard requires both hard-block and redirect for sub-PR violations**: Blocking a direct Copilot session on `0D_base_` (when NOT the promotion PR) requires: (1) `core.setFailed` in cognitive-preflight, (2) `needs:` chain blocking `activate-delegation`, AND (3) rich redirect comment with Option A/B and `copilot-session-chain.yml` dispatch command. **Exception:** When `head=0D_base_` and `base=main` (the promotion PR), REQ-11 passes — direct sessions on `0D_base_` are the **ideal formation** for that PR.
- **workflow_run triggers only resolve from default branch**: copilot-review-responder.yml and copilot-agent-session-done.yml only fire once cherry-picked to main; any workflow using workflow_run must be on main to work
- **Unused import bindings in test conftest can fail lint despite side-effect intent**: Using importlib.import_module() instead of a bare import statement preserves shard-isolation side-effects without creating a lint-visible unused binding

### Key Decisions

- **Add copilot-session-chain.yml as GROUNDED agent**: Session-chain workflow auto-creates sub-PRs targeting 0D_base_; grounding it prevents bypass and ensures correct continuation flow
- **Store upsert_dashboard_alert as surgical patch (SECTION/PAYLOAD only)**: Full-body rebuild would overwrite the Merge Readiness score block owned by pr_comment_consolidator.py; surgical patch preserves all existing sections
- **integration-branch-direct-session pattern in iterative-self-healing-ci fires only for non-promotion PRs**: Fixing a direct session on `0D_base_` (when `base≠main`) requires creating a new sub-PR branch — a structural action that cannot be done with `auto_fix_common_issues.py`. When `head=0D_base_` and `base=main` (promotion PR), this pattern does NOT fire — direct sessions are correct in that context.

### Future Research Topics

- **MCP create_or_update_file capability evaluation** (medium complexity): Would allow the cognitive brain CLI to write files to the repo without separate git operations
- **Playwright content blocker bypass for github.com in cognitive_app** (low complexity): Browser integration fails when content blocker intercepts GitHub API calls

---

## Session: S237
**Date**: 2026-03-30T18:10:00Z
**Context**: Sessions S233–S237 · PR #3814 · RAG coverage scope fix · comment dedup consolidation · PR dashboard 90→100 · codebase-wide coverage intelligence system

### Lessons Learned

- **Coverage scope dilution: `--cov=src` vs `--cov=src/codex/rag` + `--cov-config`**: When `test-rag.yml` uses `--cov=src`, coverage.xml `line-rate` is computed across ALL 50k+ lines of `src/` but only RAG tests run → ~5% aggregate. Fix: use `--cov=src/codex/rag` **and** `--cov-config=tests/rag/.coveragerc` (dedicated config prevents global `.coveragerc source=src` from being merged). Pattern `COV_001` now in `ci_failure_patterns.yaml`.

- **`detect-secrets` baseline version must match pre-commit hook pin**: `detect-secrets v1.5.0` (system) writes `version: "1.5.0"` baselines; pre-commit pin at `v1.4.0` may fail to parse them. Fix: check `.pre-commit-config.yaml rev:` and downgrade `.secrets.baseline` `"version"` field to match. Pattern `COV_002`.

- **SHA tag inside comment body, not as upsert key**: Embed `<!-- ci-review-scanned:{sha_short} -->` inside the comment body so agents can detect stale checklists per-commit. Keep `<!-- ci-rescue:{pr_number} -->` as the PR-scoped upsert key. No comment proliferation.

- **Paginated `listComments` for PRs with >100 comments**: A single `per_page: 100` call misses comments on busy PRs. Fix: `while (!existing) { ...; if (batch.length < 100) break; page++; }` — now in `comment-review-gate.yml`.

- **YAML multiline `BODY="..."` trips actionlint (Pattern 20)**: Replace with `printf '%s\n' line1 line2 ... > ${RUNNER_TEMP}/file_${GITHUB_RUN_ID}.txt; BODY=$(cat file.txt)`.

- **PR dashboard 90→100: always decompose score by component**: The 10-point gap was entirely the `Test/quality gate (10%)`. Decomposing the dashboard score breakdown immediately identifies the single root cause rather than searching broadly.

### Key Decisions

- **Omit `benchmarks/`, `analytics/`, and external `providers/` from RAG coverage**: These require binary services (ollama, llama.cpp, gpt4all, metrics DB) unavailable in CI. Omitting gives a coverage metric for testable code; untestable modules need manual review.

- **`setup-python@v5` → `@v6` when already editing a workflow**: Node.js 20 deprecation deadline is 2026-06-02 (informational). Since we were already modifying `comment-review-gate.yml`, upgrading in the same commit avoids a separate PR and resolves Pattern 21 proactively.

- **`COV_001`/`COV_002` in `ci_failure_patterns.yaml`, not just accountability report**: The patterns file is machine-readable and consumed by `ci_rescue.py`. Adding coverage patterns enables automated detection guidance in future triage runs.

### Future Research Topics

- **Coverage map → cognitive brain STM injection** (medium): Wire `generate_coverage_map.py` output into `inject_coverage_context.py` so agents get per-module risk scores at session start without manual lookup.
- **PR coverage delta comment via `--pr-delta` mode** (low): `generate_coverage_map.py --pr-delta` is implemented; just needs a CI step in `validate.yml` to call it and post the delta as a PR comment.
- **`COV_001` auto-fix in `ci_rescue.py`** (low): The fix is deterministic; could be added as a `ci_rescue.py` handler for RAG coverage failures.

---
