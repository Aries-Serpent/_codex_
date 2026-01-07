# Cache Monitoring Quick Reference Guide

## Current Status (2024-12-30)

**Cache Limit**: 10 GB (GitHub Actions account limit)
**Current Usage**: 7.69 GB (76.9%)
**Remaining**: 2.31 GB
**Status**: ⚠️ Approaching limit - monitoring required

**⚠️ IMPORTANT**: Cache sizes shown are **already compressed** by GitHub Actions (gzip). Actual uncompressed size is estimated at 15-30 GB.

## Quick Access

**View Cache Status**: 
```
GitHub Repository → Settings → Actions → Caches
```

## Current Active Caches

| Cache Name | Size | Purpose | Last Used |
|------------|------|---------|-----------|
| Linux-pip-python-def56e4e... | 9 GB | Main pip dependencies | Active |
| deps-Linux-py3.12-9b05fe7c... | 6 GB | Optimized-CI dependencies | Active |
| codeql-trap-1-2.23.8... | 0 MB | CodeQL analysis | Active |
| setup-python-Linux-x64... | 7 MB | Python environment | Active |
| Linux-pip-def56e4e...-f6b945e7... | 0 MB | Additional pip cache | Active |

**Effective Total**: 7.69 GB (GitHub calculation accounts for shared/overlapping data)

**Note**: All caches are automatically compressed by GitHub Actions using gzip compression (typically 60-80% compression ratio for Python dependencies).

## Cache Compression

### ✅ Automatic Compression (Built-in)

GitHub Actions automatically handles compression:
- **On Save**: Compresses cache with gzip before storage
- **On Restore**: Automatically decompresses cache
- **Transparent**: No configuration needed in workflows
- **Compression Ratio**: Typically 60-80% for Python pip caches

**Current Implementation**:
```yaml
- uses: actions/cache@v5
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt', 'pyproject.toml') }}
```
This automatically includes compression/decompression.

**❌ Do NOT add manual compression**:
- Would be redundant (already compressed)
- Would slow down workflows significantly
- Could corrupt cache data
- GitHub Actions handles it optimally

### What the 7.69 GB Really Means

- **Reported Size**: 7.69 GB (compressed)
- **Estimated Uncompressed**: ~15-30 GB
- **Compression Savings**: ~10-22 GB saved
- **Automatic**: Handled by GitHub Actions

## Monitoring Checklist

### Daily (During Phase 2 Rollout)
- [ ] Check total cache usage in GitHub UI
- [ ] Verify usage is under 9 GB
- [ ] Look for any eviction warnings in workflow logs

### Weekly
- [ ] Review cache trend (growing/stable)
- [ ] Check for any failed cache operations
- [ ] Verify all Phase 2 workflows are using cache correctly
- [ ] Document any unusual patterns

### Monthly
- [ ] Full cache audit
- [ ] Calculate actual time savings from cache hits
- [ ] Review and optimize cache keys if needed
- [ ] Update documentation with findings

## Alert Thresholds

| Usage | Status | Action Required |
|-------|--------|-----------------|
| < 8 GB | ✅ Safe | Continue normal operations |
| 8-9 GB | ⚠️ Caution | Increase monitoring frequency |
| 9-9.5 GB | 🟠 Warning | Prepare optimization plan |
| 9.5-10 GB | 🔴 Critical | Immediate action required |
| > 10 GB | ⚠️ Eviction | LRU caches auto-deleted |

## Phase 2 Expected Impact

**New Caches from Phase 2**:
1. security-suite.yml (2 jobs) - ~0.2-0.3 GB
2. integration-gated.yml - ~0.1-0.2 GB
3. nox_gates.yml - ~0.1-0.2 GB (includes nox cache)
4. scheduled-dependency-audit.yml - ~0.1-0.2 GB

**Projected Total After Phase 2**: 8.0-8.5 GB (80-85% of limit)

## Emergency Actions (If > 9.5 GB)

### Option 1: Remove Low-Value Caches
```bash
# Manually delete these caches from GitHub UI:
# - scheduled-dependency-audit.yml cache (weekly workflow)
# - integration-gated.yml cache (manual-only workflow)
```

### Option 2: Optimize Cache Configuration
Edit workflows to use built-in caching:
```yaml
# Instead of:
- uses: actions/cache@v5
  with:
    path: ~/.cache/pip
    key: ...

# Use:
- uses: actions/setup-python@v6
  with:
    python-version: '3.11'
    cache: 'pip'  # Built-in, more efficient
```

### Option 3: Reduce Cache Scope
Remove optional cache paths:
```yaml
# Before:
path: |
  ~/.cache/pip
  ~/.cache/nox
  ~/.cache/pre-commit

# After (keep only essential):
path: |
  ~/.cache/pip
```

## GitHub LRU Eviction Policy

**How it Works**:
- When total exceeds 10 GB, GitHub automatically deletes least recently used caches
- Eviction is based on last access time, not creation time
- Frequently accessed caches are protected
- No manual control over eviction order
- Eviction happens silently - check logs for "cache not found" warnings

**To Prevent Eviction**:
- Keep workflows running regularly (caches stay "fresh")
- Prioritize caching for high-frequency workflows
- Remove caching from low-frequency workflows

## Useful Commands

### Check Cache Usage via GitHub CLI
```bash
# List all caches
gh cache list --repo Aries-Serpent/_codex_

# Delete specific cache
gh cache delete <cache-id> --repo Aries-Serpent/_codex_
```

### Monitor Workflow Cache Hits
```bash
# Check workflow logs for cache hit/miss
gh run view <run-id> --log | grep -i "cache"
```

## Phase 3 Decision Matrix

| Current Usage | Phase 3 Action |
|---------------|----------------|
| < 8 GB | Add 5-8 workflows |
| 8-8.5 GB | Add 3-5 workflows |
| 8.5-9 GB | Add 1-2 workflows |
| 9-9.5 GB | Optimize first, then decide |
| > 9.5 GB | Remove low-value caches first |

## Resources

- [GitHub Actions Cache Limits Documentation](https://docs.github.com/actions/using-workflows/caching-dependencies-to-speed-up-workflows#usage-limits-and-eviction-policy)
- [Cache Analysis Report](.github/workflows/CACHE_ANALYSIS_REPORT.md)
- [Workflow README](.github/workflows/README_SCAN_SECRETS_VARIABLES.md)

## Contacts

For questions about cache management:
- Review [CACHE_ANALYSIS_REPORT.md](.github/workflows/CACHE_ANALYSIS_REPORT.md)
- Check GitHub Actions settings
- Monitor workflow run logs

---

**Last Updated**: 2024-12-30
**Next Review**: 2026-01-13 (2 weeks)
