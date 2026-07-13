# Archived Deployment Workflows

**Archive Date**: 2026-07-13  
**Reason**: Consolidated into 2 master workflows  
**Status**: ARCHIVED (for reference only)

## Archived Workflows

The following 7 workflows have been consolidated into 2 master workflows:

| Legacy Workflow | Consolidated Into | Archive File |
|-----------------|-------------------|--------------|
| release.yml | enhanced-release.yml | release.yml |
| automated-release-creation.yml | enhanced-release.yml | automated-release-creation.yml |
| release-to-pypi.yml | enhanced-release.yml | release-to-pypi.yml |
| pypi-publish.yml | enhanced-release.yml | pypi-publish.yml |
| observable-release.yml | enhanced-release.yml | observable-release.yml |
| pre-release-validation.yml | enhanced-release.yml | pre-release-validation.yml |
| automated-post-deployment-verification.yml | deployment-verification.yml | automated-post-deployment-verification.yml |

## Why Consolidated?

**Before Consolidation**:
- 7 separate workflows with overlapping functionality
- Multiple entry points for release process
- Difficult to maintain version consistency
- Redundant validation gates across workflows

**After Consolidation**:
- 2 master workflows (71% reduction)
- Single point of entry for all releases
- Unified validation gates
- Improved auditability

## How to Reference

These workflows are archived for:
- Historical reference
- Understanding legacy patterns
- Easy rollback if consolidation needs reversal
- Git history preservation

## Rollback Instructions

If needed, to restore a legacy workflow:

```bash
cp .codex/archived-workflows/<workflow>.yml .github/workflows/<workflow>.yml
git add .github/workflows/<workflow>.yml
git commit -m "restore: <workflow> from archive"
```

## Migration Guide

### For Release Operations

**Old Process** (before consolidation):
1. Run pre-release-validation.yml on PR
2. Create release tag
3. release.yml triggered on tag
4. Run release-to-pypi.yml or pypi-publish.yml separately
5. Run observable-release.yml separately

**New Process** (after consolidation):
1. Pre-release validation built into enhanced-release.yml
2. Create release tag (or use workflow_dispatch)
3. Single enhanced-release.yml runs with:
   - Configurable deployment type
   - All validation, build, publish, verify steps
   - Optional dry-run for testing

### For Post-Deployment Verification

**Old Process**:
1. Run automated-post-deployment-verification.yml manually

**New Process**:
1. Run deployment-verification.yml with environment selection
2. Same features, unified interface

## Related Documentation

- `.codex/DEPLOYMENT_CONSOLIDATION_REPORT.md` - Full consolidation details
- `.github/workflows/release.yml` - Enhanced release workflow
- `.github/workflows/deployment-verification.yml` - Enhanced verification workflow

