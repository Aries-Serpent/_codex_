# S174 Archived Workflows

Archived on: 2026-03-21 (S174 consolidation session)

## Files

| File | Original Name | Reason Archived |
|------|-------------|-----------------|
| `self-healing.yml` | Art_Self-Healing CI/CD | Duplicate of `iterative-self-healing-ci.yml`. Triggered on `workflow_run` for a subset of named workflows; the canonical uses `workflow_run: workflows: ["*"]` (all) with exclusion guards. |
| `self_healing_ci.yml` | Self-Healing CI | Duplicate of `iterative-self-healing-ci.yml`. Triggered on `workflow_run` for a subset of named workflows; the canonical uses `workflow_run: workflows: ["*"]` (all) with exclusion guards. |
| `pr3178-pytest-execution.yml` | Pytest Full Suite Execution | PR#3178 was merged long ago. This workflow fires on `0D_base_ → main` PRs but provides no value not covered by existing CI. |

## Recovery

To restore any of these workflows, copy the file back to `.github/workflows/`.

Note: `iterative-self-healing-ci.yml` covers all functionality of the two
self-healing workflows. The references to `Self-Healing CI` and `Art_Self-Healing CI/CD`
have been removed from `iterative-self-healing-ci.yml` and `cognitive_brain_ci_feedback.yml`
exclusion guards.
