---
applyTo: "**/*.yml,**/*.yaml"
---

- Multi-line shell commands in workflow `run:` fields must use the pipe `|` operator when containing shell braces or complex syntax to avoid YAML parsing errors.
- GitHub Actions steps should use the runtime `GITHUB_STEP_SUMMARY` environment variable, not a `github.step_summary` context value, when passing the step summary path into scripts.
- Reusable workflows invoked via `jobs.<id>.uses` must declare `on.workflow_call`.
- Disabled/orphan stub workflows must use `on: workflow_dispatch:` + `permissions: {}` + a minimal noop job to satisfy both actionlint and CodeQL security scans.
