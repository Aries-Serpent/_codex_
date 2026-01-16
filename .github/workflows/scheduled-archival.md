# Scheduled Archival

**Workflow File**: `scheduled-archival.yml`

## Purpose

[Automated workflow - purpose to be documented]

## Triggers

[No triggers configured]

## Permissions Required

- **contents**: `write`
- **pull-requests**: `write`
- **issues**: `write`

## Environment Variables

[None specified at workflow level]

## Jobs

### identify-candidates

**Runner**: `ubuntu-latest`

**Steps**: 2

**Key Steps**:
1. Checkout repository
2. Find Archival Candidates

### create-proposal

**Runner**: `ubuntu-latest`

**Steps**: 3

**Key Steps**:
1. Checkout repository
2. Create Archival Issue
3. Dry Run Summary

### compress-large-files

**Runner**: `ubuntu-latest`

**Steps**: 2

**Key Steps**:
1. Checkout repository
2. Find and Compress Large Files


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
