# Workflow Templates

This directory contains workflow templates that require human admin approval before activation.

## ⚠️ Repository Policy

Per `.github/copilot-instructions.md`:
> Do NOT create or activate any GitHub Actions workflow files.

These workflows are provided as **templates only** and must be:
1. Reviewed by repository maintainer (@mbaetiong)
2. Explicitly approved for activation
3. Moved to `.github/workflows/` when approved

## Available Templates

### 1. cache-health-monitor.yml.template

**Purpose:** Daily cache health monitoring and cleanup

**Features:**
- Daily cache size/age tracking
- Conflict detection across workflows
- Automatic cleanup (on-demand)
- Health reports with recommendations

**Activation Steps:**
```bash
# After approval
mv .codex/templates/workflows/cache-health-monitor.yml.template \
   .github/workflows/cache-health-monitor.yml
```

### 2. cache-validation.yml.template

**Purpose:** PR-triggered cache configuration validation

**Features:**
- Validates cache key uniqueness
- Checks workflow isolation
- Tests reusable action
- Blocks merge on conflicts

**Activation Steps:**
```bash
# After approval
mv .codex/templates/workflows/cache-validation.yml.template \
   .github/workflows/cache-validation.yml
```

### 3. documentation-quality-check.yml.template

**Purpose:** Documentation quality monitoring

**Features:**
- Link validation with anchors
- Freshness tracking (>90 days stale)
- Structure validation
- Quality scoring
- Health dashboard generation

**Activation Steps:**
```bash
# After approval
mv .codex/templates/workflows/documentation-quality-check.yml.template \
   .github/workflows/documentation-quality-check.yml
```

## Changes from Original PR

The following improvements have been made based on code review:

### All Workflows
- ✅ Moved to template location (complies with repository policy)
- ✅ Fixed script flag names (`--check` instead of `--check-only`)
- ✅ Reduced dependency installation (minimal deps only)
- ✅ Added GH_TOKEN where needed

### cache-health-monitor.yml
- ✅ Use `--no-deps` for minimal installation
- ✅ Add `GH_TOKEN` for cache health step

### cache-validation.yml
- ✅ Install minimal test dependencies only
- ✅ Fix pytest coverage path (module, not file path)
- ✅ Install pyyaml before validation

### documentation-quality-check.yml
- ✅ Use `paths-ignore` instead of `!pattern`
- ✅ Install only pyyaml + requests
- ✅ Fix flag: `--validate-anchors` not `--check-anchors`
- ✅ Fix flags: `--check` not `--check-only`

## Testing Before Activation

Before activating any workflow, test locally:

```bash
# Test cache manager
pytest tests/ci/test_cache_manager.py -v

# Test validation scripts
python scripts/validate_docs_links.py --validate-anchors
python scripts/validate_code_fences.py --check
python scripts/validate_table_spacing.py --check

# Test cache CLI
python -m codex.ci.cache_manager health
python -m codex.ci.cache_manager generate-key --cache-type pip --workflow test
```

## Approval Process

1. **Request Approval:**
   - Comment on PR: "@mbaetiong please review workflow templates for activation"
   - Reference this README and test results

2. **After Approval:**
   - Move templates to `.github/workflows/`
   - Remove `.template` extension
   - Commit with message: "feat(ci): activate [workflow-name] (approved by @mbaetiong)"

3. **Monitor Initial Runs:**
   - Check first 3-5 workflow runs
   - Verify no unexpected failures
   - Adjust if needed

## Support

- **Issues:** GitHub Issues with `[workflows]` tag
- **Questions:** @mbaetiong
- **Documentation:** See individual workflow files for detailed documentation

---

**Last Updated:** 2026-02-11  
**Status:** Templates Ready for Review  
**Approval Required:** Yes
