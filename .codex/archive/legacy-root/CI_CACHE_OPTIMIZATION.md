# CI/CD Cache Optimization Guide

## Overview
This document outlines the cache optimization strategy for GitHub Actions workflows in the _codex_ repository. The goal is to reduce workflow execution time and CI resource utilization by strategically adding caching to workflows that download dependencies.

## Cache Strategy

### Current State
- **Total Workflows:** ~164
- **Workflows with Cache:** 62 (~38%)
- **Workflows without Cache:** 102 (~62%)
- **Cache Strategy:** 4-layer hierarchy managed by `.github/actions/setup-python-cached`

### Cache Hierarchy
1. **Layer 1 - pip download cache** (~/.cache/pip) — Shared across ALL workflows
2. **Layer 2 - PyTorch CPU wheels** (~/.cache/torch-whl) — Keyed on PyTorch version
3. **Layer 3 - installed venv** (.venv_ci) — Keyed on dependencies hash
4. **Layer 4 - npm tool cache** (~/.npm) — Keyed on tool names

## High-Impact Workflows for Optimization

The following workflows would benefit most from cache optimization (runs frequently + installs many dependencies):

### Priority 1 - Critical Path PR Workflows
- `pr-checks.yml` — Already optimized ✅
- `resilient_validation.yml` — Already optimized ✅
- `pre-flight-validation.yml` — Uses basic setup-python cache ⚠️
- `ci-checkpoint-validation.yml` — Uses basic setup-python cache ⚠️

### Priority 2 - Frequently Triggered Build Workflows
- `docker-build-push.yml` — Build pipeline
- `coverage-with-timeout.yml` — Coverage collection
- `nox_gates.yml` — Test matrix
- `code-quality-coverage-suite.yml` — Quality checks

### Priority 3 - Less Frequent But Heavy Workflows
- `copilot-iterative-self-healing.yml` — Self-healing CI
- `app-package-download.yml` — App packaging
- `fast-forward-safe-files.yml` — File operations

## Migration Path

### Step 1: Identify Target Workflows
A workflow is a good candidate for cache optimization if it:
1. Uses Python (pip install, pytest, ruff, mypy, etc.)
2. Installs 5+ dependencies OR total install time > 30 seconds
3. Runs on PR events or scheduled triggers (frequently)
4. Does NOT already use `setup-python-cached` action

### Step 2: Update Workflow
Replace manual Python setup with the cached action:

**Before:**
```yaml
- name: Setup Python
  uses: actions/setup-python@v4
  with:
    python-version: '3.12'
    cache: 'pip'

- name: Install dependencies
  run: pip install pytest ruff mypy
```

**After:**
```yaml
- name: Setup Python (cached)
  uses: ./.github/actions/setup-python-cached
  with:
    python-version: '3.12'
    cache-tier: common
```

### Step 3: Verify
- Run workflow locally/manually
- Monitor cache hit rates in workflow logs
- Verify install times decrease over subsequent runs

## Expected Impact

### Performance Improvements
- **First run (cold cache):** No change (cache must be populated)
- **Subsequent runs (warm cache):** 40-60% reduction in install time
- **Average across PR workflow set:** 20-30% reduction in total CI time

### Resource Savings
- **Bandwidth:** Reduced PyPI downloads (~500MB per workflow run)
- **Runner utilization:** Less CPU/disk I/O during dependency install
- **Cost:** Reduced GitHub Actions minutes per PR

## Implementation Notes

1. **Cache Invalidation:** Automatic when `pyproject.toml` or `requirements*.txt` change
2. **Cache Scope:** Per-branch in PRs, shared on main branch
3. **Cache Version:** Managed by `CODEX_CACHE_VERSION` repository variable
4. **Cleanup:** Stale cache entries auto-expire after 7 days of disuse

## Monitoring

Use GitHub Actions cache management:
```
Settings → Caches → View cache usage and hit rates
```

Target metrics:
- Cache hit rate > 80% for PR workflows
- Average cache size < 500MB per workflow
- Install time < 2 minutes for cached runs
