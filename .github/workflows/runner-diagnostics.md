# Runner diagnostics — self-hosted readiness

**Workflow File**: `runner-diagnostics.yml`

## Purpose

[Automated workflow - purpose to be documented]

## Triggers

[No triggers configured]

## Permissions Required

- **contents**: `read`

## Environment Variables

[None specified at workflow level]

## Jobs

### diag

**Runner**: `${{ fromJSON(vars.RUNS_ON || '["self-hosted","linux"]') }}`

**Steps**: 4

**Key Steps**:
1. Print host and env
2. Docker readiness
3. binfmt status (best-effort)
4. Summary


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
