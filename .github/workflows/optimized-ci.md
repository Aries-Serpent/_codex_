# CI — Optimized with Caching

**Workflow File**: `optimized-ci.yml`

## Purpose

Caches Python dependencies for the repository's optimized CI setup.

## Triggers

Manual dispatch and pushes to `main` when source, package, dependency, cache-action,
or workflow files change.

## Permissions Required

- **contents**: `read`

## Environment Variables

- **CODEX_FORCE_CPU**: 1
- **UV_CACHE_DIR**: `~/.cache/uv`
- **PIP_CACHE_DIR**: `~/.cache/pip`

## Jobs

### cache-dependencies

**Runner**: `ubuntu-latest`

**Steps**: 3

**Key Steps**:
1. Checkout with the repository-pinned `actions/checkout` revision
2. Set up Python through `.github/actions/setup-python-cached`
3. Generate a best-effort cache health report


## Secrets Used

[No secrets explicitly referenced]

## Maintenance

**Last Generated**: 2026-01-16  
**Status**: Active  
**Maintainer**: DevOps Team

## Related Documentation

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)

---

*This documentation was automatically generated. For detailed configuration, refer to the workflow file.*
