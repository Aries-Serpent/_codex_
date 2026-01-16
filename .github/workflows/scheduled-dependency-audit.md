# Scheduled Dependency Audit & SBOM

**Workflow File**: `scheduled-dependency-audit.yml`

## Purpose

[Automated workflow - purpose to be documented]

## Triggers

[No triggers configured]

## Permissions Required

[Default permissions]

## Environment Variables

- **PYTHON_VERSION**: ${{ (github.event_name == 'workflow_dispatch' && github.event.inputs.python_version) || '3.11' }}
- **ALLOW_MULTIARCH**: ${{ (github.event_name == 'workflow_dispatch' && github.event.inputs.enable_multiarch == 'true') && 'true' || 'false' }}

## Jobs

### baseline-wheels

**Runner**: `ubuntu-latest`

**Steps**: 7

**Key Steps**:
1. actions/checkout@v6
2. Set up Docker Buildx
3. Build wheelhouse (builder stage) for ${{ matrix.platform }}
4. Set up Python
5. Cache Dependencies
... and 2 more steps

### sbom-generation

**Runner**: `ubuntu-latest`

**Steps**: 10

**Key Steps**:
1. actions/checkout@v6
2. Set up Docker Buildx
3. Determine Dockerfile
4. Build image for SBOM
5. Install Syft
... and 5 more steps

### upgrade-compatibility

**Runner**: `ubuntu-latest`

**Steps**: 4

**Key Steps**:
1. actions/checkout@v6
2. Set up Docker Buildx
3. Test build with Python ${{ matrix.python_version }}
4. Report compatibility

### drift-detection

**Runner**: `ubuntu-latest`

**Steps**: 5

**Key Steps**:
1. actions/checkout@v6
2. Download current baseline (amd64)
3. Download previous baseline (if exists)
4. Compare manifests
5. Create drift alert issue

### summary

**Runner**: `ubuntu-latest`

**Steps**: 1

**Key Steps**:
1. Generate summary


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
