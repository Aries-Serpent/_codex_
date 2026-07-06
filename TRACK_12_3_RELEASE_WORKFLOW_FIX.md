# Track 12.3 Release Workflow Failures - Phase 13 Fix Report

## Critical Finding
- **Issue**: Track 12.3 (Release workflow) at **0% success rate** (0/30 passing runs)
- **Threshold**: Requires ≥95% success rate for Gate 5
- **Root Cause**: Reusable workflow trigger misconfiguration

## Root Cause Analysis

### Issue 1: Missing Secret Configuration in sbom.yml (Primary Blocker)
**File**: `.github/workflows/sbom.yml` (lines 2-4)
**Problem**: The `workflow_call` trigger was defined without explicit secrets configuration:
```yaml
on:
  workflow_call:    # ❌ Empty - no secrets/inputs defined
  workflow_dispatch: {}
```

When the Release workflow called this as a reusable workflow (`uses: ./.github/workflows/sbom.yml`), it couldn't pass the required `GH_TOKEN` secret, causing the SBOM job to fail silently during initialization.

### Issue 2: Missing Secrets Passthrough in release.yml (Secondary Blocker)
**File**: `.github/workflows/release.yml` (lines 44-50)
**Problem**: The `generate-sbom` job had incorrect permissions syntax instead of secrets:
```yaml
generate-sbom:
  uses: ./.github/workflows/sbom.yml
  permissions:        # ❌ Wrong - permissions aren't inherited this way
    contents: read
    actions: write
```

Reusable workflows require an explicit `secrets:` section to receive secrets from the caller.

## Applied Fixes

### Fix 1: Add Secret Configuration to sbom.yml
```yaml
on:
  workflow_call:
    secrets:
      GH_TOKEN:
        description: GitHub token for API access
        required: false
  workflow_dispatch: {}
```

**Changes**:
- ✅ Defined `GH_TOKEN` secret in `workflow_call` trigger
- ✅ Set as optional (`required: false`) to handle workflow_dispatch fallback
- ✅ Added description for clarity

### Fix 2: Add Secrets Passthrough in release.yml
```yaml
generate-sbom:
  name: Generate SBOM
  needs: validate
  uses: ./.github/workflows/sbom.yml
  secrets:
    GH_TOKEN: ${{ secrets.CODEX_MASTER_KEY || secrets.CODEX_BACKUP_KEY || secrets.GITHUB_TOKEN }}
```

**Changes**:
- ✅ Removed incorrect `permissions:` section from reusable workflow call
- ✅ Added proper `secrets:` section to pass credentials
- ✅ Maintained credential hierarchy (CODEX_MASTER_KEY > CODEX_BACKUP_KEY > GITHUB_TOKEN)

## Technical Details

### GitHub Actions Reusable Workflow Requirements
When calling a reusable workflow with `uses: path/to/workflow.yml`:

1. **The reusable workflow** must declare inputs/secrets in its `on.workflow_call` trigger
2. **The caller** must pass these via `with:` (for inputs) and `secrets:` (for secrets)
3. **Secrets are NOT inherited** automatically - they must be explicitly passed
4. **Permissions in the call** don't override reusable workflow permissions

### Why This Was Failing
1. SBOM workflow didn't expose `GH_TOKEN` as an acceptible secret
2. Release workflow didn't pass any secrets to the SBOM job
3. SBOM job attempted to use `secrets.CODEX_MASTER_KEY` etc., but received nothing
4. Job silently failed during initialization (before job output was logged)

## Validation Results

✅ **YAML Syntax**: Both files pass YAML validation
✅ **Workflow Call Syntax**: Proper `uses:` + `secrets:` pattern
✅ **Secret Configuration**: Explicit declaration in `workflow_call` trigger
✅ **Backward Compatibility**: Maintained existing trigger types (workflow_dispatch, push, pull_request, release)

## Expected Outcome

After these fixes, the next Release workflow run should:
1. ✅ Properly initialize the `generate-sbom` reusable workflow job
2. ✅ Pass required credentials to SBOM generation
3. ✅ Generate SBOM artifacts (CycloneDX JSON + pip-licenses CSV)
4. ✅ Allow the `release` job to complete successfully

**Target Success Rate**: ≥95% (28.5+ of 30 runs passing)
**Expected Timeline**: Next release tag push or workflow_dispatch trigger

## Files Modified
- `.github/workflows/sbom.yml` (lines 2-4): Added secret declaration
- `.github/workflows/release.yml` (lines 44-50): Added secrets passthrough

## References
- [GitHub Actions: Reusable Workflows](https://docs.github.com/en/actions/using-workflows/reusing-workflows)
- [GitHub Actions: Workflow Syntax - workflow_call](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#onworkflow_call)

---

**Status**: ✅ Fixed and Ready for Testing
**Phase**: Phase 13 (Gate 5 Compliance)
**Escalation**: None required
