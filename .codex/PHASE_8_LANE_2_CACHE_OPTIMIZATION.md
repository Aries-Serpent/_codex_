# PHASE 8 LANE 2: 4-Layer Cache Hierarchy Optimization

**Date:** 2026-07-16  
**Phase:** 8 (D-Tier Autonomous Authority)  
**Lane:** 2 — Cache Management  
**Objective:** Optimize 4-layer cache hierarchy to achieve >60% cache hit rate  
**Current State:** ~40% cache hit rate (Phase 7 baseline)  
**Target:** >60% cache hit rate  
**Expected Impact:** 15-20% reduction in CI pipeline time  
**Gate Target:** 2026-07-18T14:00Z  
**Authority:** Cache Management Agent (@mbaetiong pre-approved)

---

## 🎯 Executive Summary

This optimization plan addresses the 4-layer cache hierarchy to improve hit rates from 40% → >60%. The improvements focus on:

1. **Layer 1 (pip cache):** Optimize retention policies and dependency hashing
2. **Layer 2 (npm cache):** Validate node_modules strategy and key scope expansion
3. **Layer 3 (workflow cache):** Expand cache key scope and improve matching
4. **Layer 4 (artifact cache):** Implement retention windows and cleanup policies

**Estimated Impact:**
- Cache hit rate improvement: +20-25 percentage points
- CI pipeline speedup: 15-20% reduction in execution time
- Storage cost reduction: ~25% (fewer cache misses = fewer rebuilds)
- Developer productivity: Reduced wait times for cache-dependent workflows

---

## 📊 Current State Analysis

### Baseline Metrics (Phase 7)
```
Cache Hit Rate:           ~40%
Workflows Using Cache:    59.5% (110 of 185)
Workflows Optimized:      8.1% (15 of 185)
Workflows with Issues:    51.4% (95 of 185)
Cache Size:               ~150 GB (GitHub Actions)
Primary Issue:            Generic cache keys, missing restore-keys
```

### Key Problems Identified
1. **Generic Cache Keys (40+ workflows)**
   - Keys like `${{ runner.os }}-pip-cache` without dependency hashing
   - Results in cache misses on every dependency change

2. **Missing restore-keys (60+ workflows)**
   - No fallback strategy when exact key doesn't match
   - Forces full reinstalls instead of incremental updates

3. **Broad Path Scopes (30+ workflows)**
   - Caching `~/.cache` instead of specific paths like `~/.cache/pip`
   - Causes cache bloat and frequent evictions

4. **Workflow Isolation Issues**
   - Cache keys lack workflow/job identifiers
   - Can cause cross-workflow contamination

5. **Retention Policy Gaps**
   - No systematic cleanup of old caches
   - Cache size grows unbounded

---

## 🔧 4-Layer Optimization Plan

### Layer 1: Pip Cache Optimization

**Current Issues:**
- Generic keys without dependency hashing
- Missing Python version specificity
- No pre-commit caching

**Optimization Strategy:**

#### 1.1 Dependency Hash-Based Keys
```yaml
# ❌ BEFORE: Generic key
key: ${{ runner.os }}-pip-cache

# ✅ AFTER: Hash-based with workflow scope
key: ${{ runner.os }}-${{ github.workflow }}-pip-${{ hashFiles('**/pyproject.toml', '**/requirements*.txt') }}
```

**Implementation:**
- Use `CacheManager.generate_cache_key()` with dependency files
- Include all dependency file patterns: `pyproject.toml`, `requirements*.txt`, `setup.py`
- Include Python version in key for environment specificity

#### 1.2 Multi-Level Restore Keys
```yaml
restore-keys: |
  ${{ runner.os }}-${{ github.workflow }}-pip-
  ${{ runner.os }}-pip-
  ${{ runner.os }}-
```

**Benefit:** 3-level fallback strategy
- Exact match → Highest hit rate
- Workflow-scoped prefix → Avoid cross-workflow contamination
- OS-only fallback → Last resort (slower but better than full miss)

#### 1.3 Pre-commit Cache Integration
```yaml
- name: Cache pre-commit hooks
  uses: actions/cache@v5
  with:
    path: ~/.cache/pre-commit
    key: ${{ runner.os }}-pre-commit-${{ hashFiles('.pre-commit-config.yaml') }}
    restore-keys: |
      ${{ runner.os }}-pre-commit-
```

**Expected Time Savings:** 1-2 minutes per pre-commit run (30-40% reduction)

#### 1.4 Retention Policies
- Max age: 30 days (GitHub default is fine)
- Max size: 5GB per workflow
- Auto-cleanup: Run nightly cache prune

---

### Layer 2: npm/Node Cache Optimization

**Current Issues:**
- `node_modules` caching not standardized
- Missing yarn/pnpm support
- No package manager detection

**Optimization Strategy:**

#### 2.1 Package Manager-Specific Keys
```yaml
# For npm
- uses: actions/setup-node@v4
  with:
    node-version: '18'
    cache: 'npm'

# For yarn
- uses: actions/setup-node@v4
  with:
    node-version: '18'
    cache: 'yarn'

# For pnpm
- uses: actions/setup-node@v4
  with:
    node-version: '18'
    cache: 'pnpm'
```

**Implementation:**
- Leverage `setup-node` built-in cache when possible
- For custom scenarios, use explicit paths:
  ```yaml
  path: |
    node_modules
    ~/.npm
    ~/.yarn/cache
  ```

#### 2.2 Lock File Hashing
```yaml
key: ${{ runner.os }}-${{ github.workflow }}-node-${{ hashFiles('**/package-lock.json', '**/yarn.lock', '**/pnpm-lock.yaml') }}
```

**Benefit:** Automatically invalidates cache on dependency changes

#### 2.3 Multi-Version Support
```yaml
key: ${{ runner.os }}-${{ github.workflow }}-node-${{ matrix.node-version }}-${{ hashFiles('**/package-lock.json') }}
```

**Benefit:** Separate caches per Node.js version (avoid version-incompatible modules)

---

### Layer 3: Workflow Cache Key Expansion

**Current Issues:**
- Keys too similar across workflows
- Cross-workflow contamination
- Job-level specificity missing

**Optimization Strategy:**

#### 3.1 Workflow-Scoped Keys
```yaml
# ✅ Include workflow name for isolation
key: ${{ runner.os }}-${{ github.workflow }}-pip-${{ hashFiles('**/requirements*.txt') }}
```

**Format Spec:**
```
{OS}-{WORKFLOW}-{CACHE_TYPE}-{DEPENDENCY_HASH}

Examples:
- Linux-pr-checks-pip-abc123def456
- Linux-security-scanning-suite-pip-abc123def456
- Windows-build-test-cargo-abc123def456
```

#### 3.2 Job-Level Specificity (Optional)
```yaml
# ✅ Add job matrix variables if applicable
key: ${{ runner.os }}-${{ github.workflow }}-job${{ matrix.python-version }}-pip-${{ hashFiles('**/requirements*.txt') }}
```

**Use When:** Matrix strategies with multiple versions

#### 3.3 Smart Key Generation
```python
# Use CacheManager for consistent key generation
from aries_serpent_core.ci.cache_manager import CacheManager, CacheType

manager = CacheManager()
cache_key = manager.generate_cache_key(
    cache_type=CacheType.PIP,
    workflow_name="pr-checks",
    extra_identifiers={"python": "3.12"}
)
# Output: "Linux-pr-checks-python-3.12-pip-abc123def456"
```

---

### Layer 4: Artifact Cache Retention & Cleanup

**Current Issues:**
- No retention window policy
- Caches accumulate indefinitely
- Storage costs growing

**Optimization Strategy:**

#### 4.1 Retention Window Policy
```yaml
# Implement cache cleanup workflow
name: Cache Cleanup
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 02:00 UTC

jobs:
  cleanup:
    runs-on: ubuntu-latest
    steps:
      - name: Cleanup old caches
        run: |
          # Keep only last 30 days
          # Delete caches older than 30 days
          gh cache delete-all --older-than 30
```

**Retention Rules:**
- Default: 30 days (GitHub Actions standard)
- High-traffic workflows: Keep 5 days (more frequent updates)
- Low-traffic workflows: Keep 60 days (infrequent updates)

#### 4.2 Size Management
```yaml
- name: Report cache size
  run: |
    gh cache list --json sizeInBytes | \
    jq '[.[].sizeInBytes] | add / 1024 / 1024 / 1024' | \
    awk '{print "Total cache size: " $1 " GB"}'
```

**Size Limits:**
- Total per repo: <200 GB (GitHub default, ~$50/month)
- Per workflow: <10 GB
- Alert threshold: >150 GB

#### 4.3 Cleanup Triggers
```yaml
# On workflow completion
- name: Calculate cache efficiency
  if: always()
  run: |
    # Measure cache hit rate
    # Alert if < 60%
    python scripts/ci/measure_cache_hit_rate.py
    if [ $CACHE_HIT_RATE -lt 60 ]; then
      echo "WARNING: Cache hit rate below target (60%)"
      exit 1
    fi
```

---

## 📋 Implementation Roadmap

### Phase 8a: Immediate (2-4 hours)
**Goal:** Implement Layer 1 & 2 optimizations

Tasks:
1. Update `CacheManager` to generate optimized keys
2. Fix pip cache configuration in top 10 workflows:
   - security-scanning-suite.yml
   - test-rag.yml
   - autonomy-phase-ci-matrix.yml
   - resilient_validation.yml
   - scheduled-dependency-audit.yml
3. Validate key generation with unit tests
4. Commit and test

**Expected Result:** 5-10% hit rate improvement

### Phase 8b: Mid-term (4-6 hours)
**Goal:** Implement Layer 3 optimizations

Tasks:
1. Update all cache keys to include workflow scope
2. Add job-level specificity where applicable
3. Update 20+ workflows with new key format
4. Test with multiple workflows running in parallel
5. Verify no cross-workflow contamination

**Expected Result:** Additional 5-10% hit rate improvement

### Phase 8c: Long-term (2-3 hours)
**Goal:** Implement Layer 4 cleanup & monitoring

Tasks:
1. Create cache cleanup workflow
2. Add cache health monitoring
3. Implement size and age thresholds
4. Setup alerts for cache efficiency
5. Document retention policies

**Expected Result:** Stable >60% hit rate with automatic management

---

## 🔍 Validation Metrics

### Success Criteria
✓ Cache hit rate >60% (measured across all layers)  
✓ No cross-workflow cache contamination  
✓ Cache size stabilized <150 GB  
✓ All workflows using optimized keys  
✓ Automated cleanup running successfully  

### Measurement Methods

#### 1. Cache Hit Rate Tracking
```bash
# Query GitHub Actions API
gh cache list --json sizeInBytes,key,createdAt

# Calculate hit rate from workflow logs
grep "Cache hit" .github/workflows/logs/*.txt
```

#### 2. Performance Measurement
```bash
# Compare execution times before/after
# Track dependency install times
# Measure total workflow duration
```

#### 3. Storage Analysis
```bash
# Monitor cache directory sizes
du -sh ~/.cache/*
du -sh ~/.npm
du -sh ~/.cargo
```

---

## 🛠️ Technical Implementation Details

### CacheManager Integration

```python
from aries_serpent_core.ci.cache_manager import CacheManager, CacheType

manager = CacheManager()

# Layer 1: Pip cache
config = manager.create_cache_config(
    cache_type=CacheType.PIP,
    workflow_name="pr-checks",
    extra_identifiers={"python": "3.12"}
)
# Output: CacheConfig with optimized key and restore-keys

# Layer 2: Node cache
config = manager.create_cache_config(
    cache_type=CacheType.YARN,
    workflow_name="test-frontend",
    extra_identifiers={"node": "18"}
)

# Layer 3: Custom cache
config = manager.create_cache_config(
    cache_type=CacheType.CUSTOM,
    workflow_name="build-docker",
    additional_paths=["/tmp/docker-cache"]
)

# Layer 4: Health check
health = manager.validate_cache_health()
print(f"Hit rate: {health.cache_hit_rate}%")
print(f"Size: {health.total_size_gb} GB")
```

### Workflow YAML Template

```yaml
# ✅ OPTIMIZED: 4-Layer Cache Strategy
jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.11', '3.12']
    steps:
      - uses: actions/checkout@v5

      # Layer 1: Pip Cache
      - name: Cache Python dependencies
        uses: actions/cache@v5
        id: cache-pip
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-${{ github.workflow }}-pip-py${{ matrix.python-version }}-${{ hashFiles('**/pyproject.toml', '**/requirements*.txt') }}
          restore-keys: |
            ${{ runner.os }}-${{ github.workflow }}-pip-py${{ matrix.python-version }}-
            ${{ runner.os }}-${{ github.workflow }}-pip-
            ${{ runner.os }}-pip-

      # Layer 2: Node Cache (if applicable)
      - name: Cache Node modules
        uses: actions/cache@v5
        id: cache-npm
        with:
          path: node_modules
          key: ${{ runner.os }}-${{ github.workflow }}-npm-${{ hashFiles('**/package-lock.json') }}
          restore-keys: |
            ${{ runner.os }}-${{ github.workflow }}-npm-
            ${{ runner.os }}-npm-

      # Layer 3: Pre-commit Cache
      - name: Cache pre-commit hooks
        uses: actions/cache@v5
        id: cache-pre-commit
        with:
          path: ~/.cache/pre-commit
          key: ${{ runner.os }}-pre-commit-${{ hashFiles('.pre-commit-config.yaml') }}
          restore-keys: |
            ${{ runner.os }}-pre-commit-

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: pip install -e ".[dev]"
        if: steps.cache-pip.outputs.cache-hit != 'true'

      - name: Run tests
        run: pytest tests/

      # Layer 4: Cache Health Check
      - name: Report cache hit rate
        if: always()
        run: |
          echo "Cache pip hit: ${{ steps.cache-pip.outputs.cache-hit }}"
          echo "Cache npm hit: ${{ steps.cache-npm.outputs.cache-hit }}"
          echo "Cache pre-commit hit: ${{ steps.cache-pre-commit.outputs.cache-hit }}"
```

---

## 📈 Performance Impact Projections

### Time Savings Calculation
```
Assumptions:
- 500 workflow runs per day
- Current 40% hit rate → Target 60% hit rate
- Average dependency install time: 8 minutes

Current scenario (40% hit):
- Misses per day: 500 × 60% = 300 misses
- Time wasted: 300 × 8 min = 2,400 min = 40 hours/day

Optimized scenario (60% hit):
- Misses per day: 500 × 40% = 200 misses
- Time wasted: 200 × 8 min = 1,600 min = 26.7 hours/day

Daily savings: 40 - 26.7 = 13.3 hours/day
Annual savings: 13.3 × 365 = 4,850 hours/year
```

### Storage Cost Savings
```
GitHub Actions storage pricing: $0.50/GB per month (after 1 GB free)

Current scenario (40% hit = more rebuilds):
- Cache size: 150 GB
- Monthly cost: (150 - 1) × $0.50 = $74.50

Optimized scenario (60% hit = fewer rebuilds):
- Cache size: 110 GB
- Monthly cost: (110 - 1) × $0.50 = $54.50

Monthly savings: $74.50 - $54.50 = $20
Annual savings: $20 × 12 = $240
```

---

## ⚠️ Risk Mitigation

### Risk 1: Cross-Workflow Contamination
**Problem:** Workflows using each other's cache  
**Mitigation:** Always include workflow name in key  
**Verification:** Test with parallel workflow runs

### Risk 2: Stale Cache
**Problem:** Cache not invalidated on dependency changes  
**Mitigation:** Hash all dependency files  
**Verification:** Monitor for version mismatch errors

### Risk 3: Cache Eviction
**Problem:** New caches evicting old ones due to size limits  
**Mitigation:** Implement cleanup policy  
**Verification:** Monitor cache size and hit rate

### Risk 4: Key Generation Failures
**Problem:** Hash generation failing silently  
**Mitigation:** Add error handling and logging  
**Verification:** Unit tests for all key generation scenarios

---

## ✅ Acceptance Criteria

- [x] All 4 layers documented with optimization strategies
- [x] Cache hit rate improvement path identified (+20% target)
- [x] CacheManager integration tested
- [x] Workflow templates created and validated
- [ ] Top 10 workflows updated with optimized keys
- [ ] Cache hit rate >60% measured
- [ ] Retention cleanup running successfully
- [ ] Monitoring and alerts implemented
- [ ] Documentation updated
- [ ] Phase 8 gate approved by 2026-07-18T14:00Z

---

## 📞 Escalation & Support

**Questions?** Contact the Cache Management Agent (@mbaetiong)

**Issues:**
- Cache hit rate not improving → Check key generation
- Cross-workflow contamination → Verify workflow name in key
- Cache size growing → Run cleanup workflow
- Performance still poor → Check for missing restore-keys

---

## 📝 Appendix: Cache Key Format Specification

### Format: `{OS}-{WORKFLOW}-{TYPE}-{PYTHON_VERSION}-{HASH}`

```
OS:              Linux | macOS | Windows
WORKFLOW:        github.workflow value (pr-checks, etc.)
TYPE:            pip | npm | cargo | docker | custom
PYTHON_VERSION:  3.11 | 3.12 | (optional)
HASH:            hashFiles() output (12-16 chars)

Examples:
✓ Linux-pr-checks-pip-3.12-abc123def456
✓ macOS-test-frontend-npm-abc123def456
✓ Windows-rust-build-cargo-abc123def456
```

### Restore Keys Strategy

```yaml
restore-keys: |
  # Level 1: Exact match (highest priority)
  ${{ runner.os }}-${{ github.workflow }}-${{ cache_type }}-${{ dep_hash }}
  
  # Level 2: Workflow-scoped fallback
  ${{ runner.os }}-${{ github.workflow }}-${{ cache_type }}-
  
  # Level 3: Cache-type fallback
  ${{ runner.os }}-${{ cache_type }}-
  
  # Level 4: OS-only fallback
  ${{ runner.os }}-
```

---

## 📊 Status Summary

| Component | Status | Target |
|-----------|--------|--------|
| Documentation | ✅ Complete | 2026-07-16 |
| Implementation Plan | ✅ Complete | 2026-07-17 |
| Layer 1 Optimization | 🟡 In Progress | 2026-07-17 |
| Layer 2 Optimization | 🟡 Pending | 2026-07-18 |
| Layer 3 Optimization | 🟡 Pending | 2026-07-18 |
| Layer 4 Cleanup | 🟡 Pending | 2026-07-18 |
| Validation & Testing | ⏳ Pending | 2026-07-18 |
| Phase 8 Gate Decision | ⏳ Pending | 2026-07-18T14:00Z |

---

**Report Version:** 1.0  
**Last Updated:** 2026-07-16T14:56Z  
**Authority:** Cache Management Agent  
**Next Review:** 2026-07-18T12:00Z (2 hours before gate)
