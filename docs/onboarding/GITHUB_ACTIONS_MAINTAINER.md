# GitHub Actions maintainer

## Where to start

Read the [workflow and governance map](../WORKFLOW_MAP.md) and the
[GitHub API reference](../ci/GITHUB_API_COPILOT_AGENT_REFERENCE.md).

## Where the code lives

- `.github/workflows/`: active workflow definitions
- `scripts/ci/`: validation, orchestration, telemetry, and remediation helpers
- `.codex/`: WEC, policy, CI-pattern, and operational references
- `docs/ci/` and `docs/workflows/`: human-facing runbooks and design notes

## What this role cares about

Least-privilege permissions, pinned actions, branch-scoped concurrency, timeouts,
offline-safe gates, WEC integrity, and actionable failure output.

## Key technologies

GitHub Actions, YAML, Python CI helpers, CodeQL, Ruff, mypy, pytest, nox, pre-commit,
dependency scanning, and GitHub MCP/API tooling.

## Typical workflow

1. Identify the workflow category and its supporting script in the workflow map.
2. Read repository workflow instructions and governance policy.
3. Make the smallest workflow or script change.
4. Validate YAML and run the focused script tests.
5. Preserve the PR Workflow Execution Checklist and inspect resulting checks.

## Common gotchas

- Similar workflow names may serve different triggers; inspect each `on:` block.
- Historical workflow reports can be stale; active definitions are under
  `.github/workflows/`.
- Never place secrets in workflow text or logs.
- A workflow can be syntactically valid while violating permissions, concurrency,
  timeout, or WEC policy.

