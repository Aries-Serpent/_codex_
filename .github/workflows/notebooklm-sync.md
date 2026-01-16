# NotebookLM Live Sync

**Workflow File**: `notebooklm-sync.yml`

## Purpose

[Automated workflow - purpose to be documented]

## Triggers

[No triggers configured]

## Permissions Required

- **contents**: `read`
- **id-token**: `write`

## Environment Variables

- **OUTPUT_FILE**: codex-architecture-sync.xml
- **REPOMIX_VERSION**: 0.1.11

## Jobs

### consolidate-and-sync

**Runner**: `ubuntu-latest`

**Steps**: 15

**Key Steps**:
1. Checkout Repository
2. Setup Node.js
3. Cache Repomix Installation
4. Install Repomix
5. Generate Repository Consolidation
... and 10 more steps


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
