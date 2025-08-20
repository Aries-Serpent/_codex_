# PINNED_SHAS.md

Immutable pins for GitHub Actions used in the Codex CI workflow. Replace `<FULL_SHA>` placeholders in the workflow with these exact commit SHAs to ensure deterministic, secure builds.

| Action | Purpose | Commit SHA |
|---|---|---|
| `actions/checkout` | Clone repository | `08eba0b27e820071cde6df949e0beb9ba4906955` |
| `actions/setup-python` | Install Python | `a26af69be951a213d495a4c3e4e4022e16d87065` |
| `actions/cache` | Dependency caching | `0400d5f644dc74513175e3cd8d07132dd4860809` |
| `pre-commit/action` | Run pre-commit hooks | `2c7b3805fd2a0fd8c1884dcaebf91fc102a13ecd` |

## How to Resolve the Latest Stable SHAs

Using the GitHub REST API:

```bash
curl -fsSL https://api.github.com/repos/actions/checkout/git/refs/tags/v4 | jq -r '.object.sha'
curl -fsSL https://api.github.com/repos/actions/setup-python/git/refs/tags/v5 | jq -r '.object.sha'
curl -fsSL https://api.github.com/repos/actions/cache/git/refs/tags/v4 | jq -r '.object.sha'
curl -fsSL https://api.github.com/repos/pre-commit/action/git/refs/tags/v3.0.1 | jq -r '.object.sha'
```

Review and update these pins quarterly or when security advisories are published.
