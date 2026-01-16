# Rate-Limit History Prune

**Workflow File**: `ratelimit_history_prune.yml`

## Purpose

[Automated workflow - purpose to be documented]

## Triggers

[No triggers configured]

## Permissions Required

[Default permissions]

## Environment Variables

[None specified at workflow level]

## Jobs

### prune

**Runner**: `ubuntu-latest`

**Steps**: 3

**Key Steps**:
1. actions/checkout@v6
2. Prune history (keep 90 days)
3. Upload post-prune listing


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
