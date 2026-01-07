# Phase 3C-Lite: Sustainable Caching Strategy

**Status**: Ready for implementation AFTER emergency cleanup  
**Target**: Add 200-300 MB of critical tool caches only  
**Constraint**: Must stay under 8 GB total (80% capacity)

---

## Overview

Phase 3C-Lite focuses on adding **minimal, high-impact tool caches** to improve CI performance without exceeding capacity limits. Unlike the full Phase 3C plan, this lite version adds only the most critical caches with strict size limits.

---

## Critical Tool Caches to Add

### 1. Ruff Cache (~20-30 MB)

**Impact**: 5-10 second speedup on lint jobs  
**Size**: Small, stable  
**Priority**: HIGH

```yaml
- name: Cache Ruff
  uses: actions/cache@v4
  with:
    path: ~/.cache/ruff
    key: ${{ runner.os }}-ruff-${{ hashFiles('.ruff.toml', 'pyproject.toml') }}
    restore-keys: |
      ${{ runner.os }}-ruff-
```

### 2. MyPy Cache (~50-80 MB)

**Impact**: 15-30 second speedup on type check jobs  
**Size**: Moderate, grows with codebase  
**Priority**: HIGH

```yaml
- name: Cache MyPy
  uses: actions/cache@v4
  with:
    path: .mypy_cache
    key: ${{ runner.os }}-mypy-${{ hashFiles('**/*.py', 'pyproject.toml') }}
    restore-keys: |
      ${{ runner.os }}-mypy-
```

### 3. Pytest Cache (~30-50 MB)

**Impact**: 10-20 second speedup on test discovery  
**Size**: Small to moderate  
**Priority**: MEDIUM

```yaml
- name: Cache Pytest
  uses: actions/cache@v4
  with:
    path: .pytest_cache
    key: ${{ runner.os }}-pytest-${{ hashFiles('tests/**/*.py') }}
    restore-keys: |
      ${{ runner.os }}-pytest-
```

### 4. Pre-commit Hooks Cache (~50-100 MB)

**Impact**: 20-40 second speedup on pre-commit runs  
**Size**: Moderate  
**Priority**: MEDIUM

```yaml
- name: Cache pre-commit
  uses: actions/cache@v4
  with:
    path: ~/.cache/pre-commit
    key: ${{ runner.os }}-pre-commit-${{ hashFiles('.pre-commit-config.yaml') }}
    restore-keys: |
      ${{ runner.os }}-pre-commit-
```

---

## Total Projected Addition

| Cache Type | Size (MB) | Impact (seconds) |
|------------|-----------|------------------|
| Ruff | 20-30 | 5-10 |
| MyPy | 50-80 | 15-30 |
| Pytest | 30-50 | 10-20 |
| Pre-commit | 50-100 | 20-40 |
| **TOTAL** | **150-260 MB** | **50-100 seconds/run** |

---

## Implementation Strategy

### Phase 3C-Lite-1: Add to `optimized-ci.yml`

Add Ruff and MyPy caches to the main CI workflow:

```yaml
# After pip cache restoration
- name: Cache Ruff
  uses: actions/cache@v4
  with:
    path: ~/.cache/ruff
    key: ${{ runner.os }}-ruff-${{ hashFiles('.ruff.toml', 'pyproject.toml') }}
    restore-keys: |
      ${{ runner.os }}-ruff-

- name: Cache MyPy  
  uses: actions/cache@v4
  with:
    path: .mypy_cache
    key: ${{ runner.os }}-mypy-${{ hashFiles('**/*.py', 'pyproject.toml') }}
    restore-keys: |
      ${{ runner.os }}-mypy-
```

### Phase 3C-Lite-2: Add to test workflows

Add Pytest cache to test jobs:

```yaml
# In test matrix jobs, after checkout
- name: Cache Pytest
  uses: actions/cache@v4
  with:
    path: .pytest_cache
    key: ${{ runner.os }}-pytest-shard-${{ matrix.shard }}-${{ hashFiles('tests/**/*.py') }}
    restore-keys: |
      ${{ runner.os }}-pytest-shard-${{ matrix.shard }}-
      ${{ runner.os }}-pytest-
```

### Phase 3C-Lite-3: Add to pre-commit workflow (if exists)

```yaml
- name: Cache pre-commit
  uses: actions/cache@v4
  with:
    path: ~/.cache/pre-commit
    key: ${{ runner.os }}-pre-commit-${{ hashFiles('.pre-commit-config.yaml') }}
    restore-keys: |
      ${{ runner.os }}-pre-commit-
```

---

## Monitoring and Limits

### Hard Limits

- **Total cache size MUST stay < 8 GB** (80% capacity)
- **Individual cache MUST be < 500 MB**
- **Monitor after each addition**

### Monitoring Commands

```bash
# Check total cache size
gh cache list --json sizeInBytes --limit 100 | jq '[.[].sizeInBytes] | add / 1024 / 1024 / 1024'

# Check if under limit
TOTAL_GB=$(gh cache list --json sizeInBytes --limit 100 | jq '[.[].sizeInBytes] | add / 1024 / 1024 / 1024')
if (( $(echo "$TOTAL_GB < 8.0" | bc -l) )); then
  echo "✅ Under limit: ${TOTAL_GB} GB"
else
  echo "⚠️ Over limit: ${TOTAL_GB} GB"
fi
```

---

## Rollback Plan

If cache size exceeds 8 GB after any addition:

1. **Identify newest cache**:
   ```bash
   gh cache list --json key,createdAt,sizeInBytes --limit 10 | jq -r 'sort_by(.createdAt) | reverse | .[0]'
   ```

2. **Delete it**:
   ```bash
   gh cache delete <cache-id> --confirm
   ```

3. **Remove cache step from workflow**

4. **Commit reversion**

---

## Success Criteria

- ✅ Total cache size < 8 GB (80% capacity)
- ✅ All added caches have hit rate > 70%
- ✅ CI runs 50-100 seconds faster
- ✅ No cache evictions for 7 days
- ✅ Documentation updated

---

## NOT Included in Phase 3C-Lite

The following from full Phase 3C are **deferred** until cache capacity improves:

- ❌ Python bytecode compilation cache (too large, ~200-300 MB)
- ❌ Test duration-based sharding (requires additional caching)
- ❌ MCP cache warmup (requires significant space)
- ❌ Playwright browser cache (very large, ~1 GB+)

---

## Next Steps After Phase 3C-Lite

1. Monitor for 1 week
2. Generate performance report
3. If successful and capacity allows, consider:
   - Full Phase 3C implementation
   - Additional workflow caching
   - Cross-workflow cache sharing

---

## Emergency Procedures

If cache limit is exceeded again:

1. Run emergency cleanup workflow
2. Review and remove low-value caches
3. Consider switching more workflows to built-in caching
4. Evaluate cache retention policies (reduce from 7 days to 5 days)

---

**Last Updated**: 2025-12-30  
**Next Review**: After 1-week monitoring period
