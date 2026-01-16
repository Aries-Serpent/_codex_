# Zendesk Knowledge Sync

**Workflow File**: `zendesk-knowledge-sync.yml`

## Purpose

[Automated workflow - purpose to be documented]

## Triggers

[No triggers configured]

## Permissions Required

- **contents**: `write`
- **pull-requests**: `write`

## Environment Variables

[None specified at workflow level]

## Jobs

### sync-knowledge

**Runner**: `ubuntu-latest`

**Steps**: 10

**Key Steps**:
1. Checkout code
2. Set up Python
3. Install dependencies
4. Run Zendesk Knowledge Sync
5. Check for updates
... and 5 more steps


## Secrets Used

[Secrets referenced in workflow - see workflow file for details]

## Maintenance

**Last Generated**: 2026-01-16  
**Status**: Active  
**Maintainer**: DevOps Team

## Related Documentation

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)

---

*This documentation was automatically generated. For detailed configuration, refer to the workflow file.*
