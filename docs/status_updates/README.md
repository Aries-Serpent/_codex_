# Status Updates
**Last Updated:** 2026-10-02
**Version:** v0.3.0

> **Active state:** This folder contains active, evidence-backed repo status for the current branch. Historical backlog narratives, archive snapshots, and older remediation notes remain archive-only evidence unless explicitly labeled historical.

Use this folder to track active, evidence-backed repo status for the current branch. Historical backlog items remain in archive evidence, not in the active operational record, unless explicitly labeled historical.

## Current state
- Active security state: closed/advisory-only with admin-only follow-up where required.
- Current validation scope: repo-managed files only; exclude vendored environment directories such as `.venv_ci/`.
- Remaining active work: docs freshness, validation-scope cleanup, and cost-optimization backlog execution.

## Template
- **Start from**: `docs/status_updates/TEMPLATE_status_update.md`
- **Save instances as**: `docs/status_updates/<slug>-<YYYY-MM-DD>.md`
- **Store large attachments under**: `docs/status_updates/artifacts/<YYYY-MM-DD>-<slug>/`

## Quickstart

1. Copy the template:
   ```bash
   cp docs/status_updates/TEMPLATE_status_update.md \
      docs/status_updates/<slug>-$(date -u +%F).md
   ```

2. Fill all `<placeholder>` fields with current branch data.

3. Record evidence in the `## 4) Evidence` section with:
   - command run
   - exit code
   - artifact link or path
   - UTC timestamp

4. Calculate readiness score using the formula:
   ```text
   R = α·E + β·T + γ·D
   ```
   Where α+β+γ=1 and E,T,D ∈ [0,1]

5. Attach artifacts (metrics NDJSON, logs, reports) to:
   ```text
   docs/status_updates/artifacts/$(date -u +%F)-<slug>/
   ```

## Best Practices
- Anchor each update to the current branch/PR/commit and current validation evidence
- Keep historical backlog items clearly labeled as archive evidence when retained for record
- Attach NDJSON metrics, logs, and generated reports as artifacts for auditability
- Keep "Gaps & Remediations" short, specific, and assigned to owners
- Update changelog section to reference the previous active status update file
- Scope validation to repo-managed files and exclude vendored environment folders such as `.venv_ci/`
