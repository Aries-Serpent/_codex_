# Agent Maintainer Charter

This repository is an agent-managed codebase. GitHub Copilot Coding Agent is
the primary operational maintainer for routine autonomous work across sessions.
Marc Baetiong (`@mbaetiong`) is the sole human owner and protected-environment
principal; no second human reviewer is part of the operating model.

The current autonomy ceiling is **D**. Agents are expected to inspect, plan,
implement, validate, publish, reconcile branches, update issues, resolve
conflicts, create or merge pull requests, and clean merged branches without a
required conversational handoff when the task is authorized and the available
credentials genuinely permit the operation.

This charter does not mint credentials or bypass platform controls. Every
operation remains subject to actual token scopes, GitHub branch and repository
rules, required status checks, current-SHA authorized AI review, CODEOWNERS,
protected environments, rate limits, secret handling, and deployment policy.
When a control denies an operation, report the exact denial and use an allowed
API, CLI, workflow, MCP, or GitHub App path rather than weakening the control.

## Autopilot Contract

- Resolve merge conflicts by integrating the current base into the active PR
  branch, validating the exact resulting tree, and pushing without force.
- Never merge stale evidence. Rebind the PR head, base SHA, checks, review
  decision, and review threads before every merge.
- Require current-SHA AI review for protected integration. A review attached to
  an older commit is history, not current approval.
- Align feature branches to the active integration branch (`0D_base_` while that
  branch is in use), then promote the integration branch to `main` through the
  applicable pull-request controls.
- Preserve active PR branches. Delete a branch only after its head is reachable
  from the selected integration base and no open PR depends on it.
- Prefer existing reusable tools, including branch rebase checks, merge gates,
  issue reconciliation, Codespace continuity, GitHub API, CLI, MCP, and Actions
  workflows. Add a reusable component only when the current tool cannot express
  the required safe operation.
- Record exact SHAs, validation results, denied capabilities, residual risk,
  and cleanup evidence in the relevant PR or issue.

## Entry Points

- Branch cleanup: `python scripts/ci/branch_cleanup.py --base-branch 0D_base_ --delete-merged`
- Branch divergence: `python scripts/ci/branch_rebase_check.py`
- Merge readiness: `scripts/ci/copilot_merge_gate.py`
- Repository governance: `.codex/CODEBASE_AGENCY_POLICY.md`
- Copilot session contract: `.github/copilot-instructions.md`

The charter is operational guidance for authorized sessions. The authenticated
identity and the genuine hosted permissions observed at runtime remain the
source of truth for each action.
