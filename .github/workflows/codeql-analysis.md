# CodeQL Security Gate

**Workflow File**: `codeql-ga-gate.yml`

## Purpose

The active repository gate for CodeQL analysis and enforcement. This workflow is the source of truth for push/PR security blocking and keeps the broader `security-scanning-suite.yml` job from duplicating automatic CodeQL uploads.

## Triggers

- `push` on `main`, `develop`, and `release/**`
- `pull_request` on `main`, `develop`, and `release/**`
- `workflow_dispatch` with `dry_run` and `severity_threshold` inputs

## Permissions Required

- `contents: read`
- `security-events: write`
- `pull-requests: write`
- `checks: write`
- `statuses: write`

## Environment Variables

- `PYTHON_VERSION: 3.12`
- `CODEQL_SEVERITY_THRESHOLD` from the workflow dispatch input or default `high`

## Jobs

### codeql-analysis

**Runner**: `ubuntu-latest`

**Key Steps**:
1. Checkout repository
2. Initialize CodeQL with `.github/codeql/codeql-config.yml`
3. Autobuild
4. Perform CodeQL analysis and upload SARIF
5. Parse SARIF results and enforce severity-based gate logic
6. Comment on PRs and record audit trail artifacts

## SARIF Contract

- Valid SARIF is required for the gate to count alerts.
- The workflow validates generated SARIF before counting severities.
- Empty or malformed SARIF falls back to a minimal valid SARIF payload so the gate remains deterministic.

## Maintenance

**Status**: Active  
**Maintainer**: Security/DevOps

## Related Documentation

- [Workflow file](codeql-ga-gate.yml)
- [CodeQL config](../codeql/codeql-config.yml)
- [GitHub Actions documentation](https://docs.github.com/en/actions)
