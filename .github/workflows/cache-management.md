# Cache Management

**Workflow File**: `cache-management.yml`

## Purpose

[Automated workflow - purpose to be documented]

## Triggers

[No triggers configured]

## Permissions Required

- **contents**: `read`
- **actions**: `write`

## Environment Variables

[None specified at workflow level]

## Jobs

### cache-report

**Runner**: `ubuntu-latest`

**Steps**: 2

**Key Steps**:
1. Checkout
2. List all caches

### cleanup-ephemeral

**Runner**: `ubuntu-latest`

**Steps**: 1

**Key Steps**:
1. Cleanup old ephemeral caches

### cleanup-common

**Runner**: `ubuntu-latest`

**Steps**: 1

**Key Steps**:
1. Cleanup old common caches


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
