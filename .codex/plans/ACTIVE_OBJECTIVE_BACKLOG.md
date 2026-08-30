# Active Objective Backlog

> Active execution source for remaining repo work. Historical plans remain in the archive and are not treated as the live task state.
>
> Canonical active planset: `.codex/plans/LEAN_WORKFLOW_OS_PLANSET.md`

## Objective 1 — Documentation and planset alignment
- Status: In progress
- Owner: `documentation-consolidator` + `reference-updater-agent`
- Goal: Align the repo’s documentation layer with the codebase as it exists today, while preserving historical evidence and clearly separating archive status from active execution.
- Acceptance criteria:
  - One canonical active planset exists and is referenced consistently
  - Historical plan files are labeled as archival/superseded, not active execution guidance
  - Registry and inventory files describe the repo’s current state without implying stale plan activity is still live
- Validation gate:
  - Confirm all active links to plan docs point to `.codex/plans/LEAN_WORKFLOW_OS_PLANSET.md`
  - Confirm historical plans remain clearly marked as archive-only references

## Objective 2 — Archive policy canonicalization
- Status: In progress
- Owner: `repository-organization-agent` + `repository-hygiene-agent`
- Goal: Standardize the repo’s archive policy around one canonical home and keep compatibility aliases explicitly marked as legacy-only.
- Acceptance criteria:
  - Active archive references point to `.codex/archive/root-consolidation/deprecated-reports/misc/repo-owner-review`
  - Legacy root-level `misc/repo-owner-review` references are compatibility-only and not authoritative
  - Bundle and archive docs share a single canonical location
- Validation gate:
  - Search active config/docs/workflows for stale root-level archive assumptions
  - Verify canonical archive root is the only active contract presented in docs and automation

## Objective 3 — Safe bundle transfer and rehomed bundle validation
- Status: Active and validated
- Owner: `ci-testing-agent` + `workflow-compliance-guardian`
- Goal: Keep the file-backed bundle flow as the only approved transfer path and ensure it remains valid after archive rehoming.
- Acceptance criteria:
  - Only file-backed, checksum-validated bundle transfer remains the active pattern
  - Raw `git diff | ...` handoff remains absent from active logic and docs
  - `.codex/sandbox-bundles/sandbox-transfer/` remains the active canonical transfer root
- Validation gate:
  - `pytest -q tests/test_git_patch_bundle.py`
  - bundle verification and apply smoke test against the canonical path

## Objective 4 — Stale reference cleanup in active config and automation
- Status: In progress
- Owner: `reference-updater-agent`
- Goal: Remove active automation/config references that still assume the legacy root-level archive layout.
- Acceptance criteria:
  - Active workflow/config/docs references point to the canonical archive root or clearly label compatibility-only paths
  - Repo automation no longer default-drafts or archives into the stale root path
- Validation gate:
  - Targeted grep across active workflow/config/doc files for stale `misc/repo-owner-review` assumptions
  - YAML parse check for updated workflow and config files

## Objective 5 — Ongoing documentation governance
- Status: Active
- Owner: `documentation-consolidator` + `link-validator-agent`
- Goal: Keep documentation, registry files, and active plan references synchronized with the implementation state of the codebase.
- Acceptance criteria:
  - Active docs reflect the current repo state and no longer imply unsupported historical claims are live
  - Links and relative references remain valid after archive and plan reclassification
- Validation gate:
  - Link pass over plan/docs references
  - Diff review for stale narrative patterns in active docs
