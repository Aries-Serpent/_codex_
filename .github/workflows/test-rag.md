# RAG Module Tests

**Workflow File**: `test-rag.yml`

## Purpose

[Automated workflow - purpose to be documented]

## Triggers

[No triggers configured]

## Permissions Required

[Default permissions]

## Environment Variables

[None specified at workflow level]

## Jobs

### test-rag

**Runner**: `ubuntu-latest`

**Steps**: 12

**Key Steps**:
1. Checkout code
2. Set up Python ${{ matrix.python-version }}
3. Cache sentence-transformers models
4. Free disk space
5. Install dependencies
... and 7 more steps


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
