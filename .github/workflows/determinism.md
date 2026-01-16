# Determinism & Audit Validation

**Workflow File**: `determinism.yml`

## Purpose

[Automated workflow - purpose to be documented]

## Triggers

[No triggers configured]

## Permissions Required

- **contents**: `read`
- **pull-requests**: `write`

## Environment Variables

- **PYTHONHASHSEED**: 0
- **PYTHONDONTWRITEBYTECODE**: 1
- **RANDOM_SEED**: 42
- **OMP_NUM_THREADS**: 1
- **MKL_NUM_THREADS**: 1
- **NUMEXPR_NUM_THREADS**: 1
- **TF_DETERMINISTIC_OPS**: 1
- **CUBLAS_WORKSPACE_CONFIG**: :4096:8

## Jobs

### determinism-check

**Runner**: `ubuntu-latest`

**Steps**: 9

**Key Steps**:
1. Checkout
2. Free disk space for CI
3. Setup Python
4. Install dependencies
5. Clear Python caches
... and 4 more steps


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
