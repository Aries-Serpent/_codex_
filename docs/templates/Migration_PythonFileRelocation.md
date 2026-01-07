# [Template]: Python File Relocation with Backward Compatibility
**Version:** v1.0.0  
**Last Updated:** 2025-10-25  
**Role Workflow:** Developers draft → Maintainers execute → Reviewers certify

> [PLACEHOLDER: MIGRATION_INTENT_SUMMARY]

Use this template when relocating Python files or packages while maintaining import stability and release automation. It pairs execution phases with validation artifacts so you can adapt the workflow to your service with minimal rework.

## Executive Summary
- Target module(s): [PLACEHOLDER: MODULE_LIST]
- Motivation and outcomes: [PLACEHOLDER: MOTIVATION_AND_IMPACT]
- Success metrics: [PLACEHOLDER: SUCCESS_METRICS]
- Stakeholders and notification plan: [PLACEHOLDER: STAKEHOLDER_MATRIX]
- Review cadence: [PLACEHOLDER: REVIEW_SCHEDULE]

## Prerequisites
- Document current import graph with `python -m modulefinder [PLACEHOLDER: ENTRY_POINT]` and capture output.
- Confirm runtime hooks (e.g., [`sitecustomize.py`](../../sitecustomize.py)) do not hard-code the old paths.
- Validate tests around the target modules exist; if missing, add smoke coverage in `../../tests/` before proceeding.
- Align logging updates with observability owners to ensure dashboards continue tracking key signals.
- Secure maintainer sign-off for the planned rollout window.

## Phase 1 — Validate Source Layout
1. Inventory files moving from `[PLACEHOLDER: OLD_PACKAGE_PATH]` to `[PLACEHOLDER: NEW_PACKAGE_PATH]`.
2. Record git history with `git log --stat -- [PLACEHOLDER: OLD_PACKAGE_PATH]` for future auditing.
3. Capture baseline metrics (lint, tests, size) before making changes.

## Phase 2 — Scaffold Compatibility Shims
1. Create aliases using `sys.modules` or import forwarding files.
2. Update [`sitecustomize.py`](../../sitecustomize.py) to register runtime aliases if dynamic imports are involved.
3. Provide fallback entry points so third-party integrations remain functional.

## Phase 3 — Update Dependency Graph
1. Adjust imports in code and templates to point at `[PLACEHOLDER: NEW_PACKAGE_PATH]`.
2. Update configuration references (e.g., [`pyproject.toml`](../../pyproject.toml), DAGs, or env vars).
3. Run targeted pytest suites (`pytest [PLACEHOLDER: TEST_SELECTOR]`) to validate dependency updates.

## Phase 4 — Migrate Regression Coverage
1. Move fixtures within [`tests/`](../../tests/) to mirror the new module layout.
2. Add regression tests for aliases to confirm backward compatibility.
3. Ensure coverage remains ≥85% by adding tests where gaps exist.

## Phase 5 — Execute Rollout
1. Merge compatibility shims and new modules behind feature flags if necessary.
2. Coordinate releases with stakeholders documented above.
3. Monitor dashboards and logs during rollout for anomalies.

## Phase 6 — Close-Out & Knowledge Transfer
1. Remove temporary flags or shims once downstream consumers migrate.
2. Archive decisions in the service README and link to this template instance.
3. Update [`docs/CHANGELOG.md`](../CHANGELOG.md) with lessons learned and future follow-ups.

## Success Criteria
- All imports resolved without deprecation warnings.
- CI and manual smoke tests green with coverage ≥85% for touched modules.
- Observability dashboards confirm no error regression post-relocation.
- Stakeholders acknowledge completion and update runbooks accordingly.

## Rollback Procedure
1. Revert the relocation commit(s) with `git revert [PLACEHOLDER: COMMIT_RANGE]`.
2. Restore original configuration files (ensure `sitecustomize.py` and alias files match pre-migration state).
3. Redeploy the previous release artifact and run smoke tests to confirm stability.
4. Document the rollback in the service change log with cause and follow-up actions.

## Customization Guide
| Placeholder | Description | Example |
| --- | --- | --- |
| `[PLACEHOLDER: MIGRATION_INTENT_SUMMARY]` | One-sentence description of the move. | "Relocate shared tokenizer helpers to `codex.text` to unblock GPU builds." |
| `[PLACEHOLDER: MODULE_LIST]` | Enumerate files or directories moving. | "`src/codex/foo.py`, `src/codex/bar/`" |
| `[PLACEHOLDER: OLD_PACKAGE_PATH]` | Current import path. | "`codex.legacy.foo`" |
| `[PLACEHOLDER: NEW_PACKAGE_PATH]` | Target import path. | "`codex.core.foo`" |
| `[PLACEHOLDER: TEST_SELECTOR]` | Command for validating affected tests. | "`pytest tests/foo -k relocation`" |

## References
- [`sitecustomize.py`](../../sitecustomize.py) for runtime aliases.
- [`conftest.py`](../../conftest.py) for pytest fixtures impacted by module moves.
- [`docs/templates/README.md`](./README.md) for workflow overview.
