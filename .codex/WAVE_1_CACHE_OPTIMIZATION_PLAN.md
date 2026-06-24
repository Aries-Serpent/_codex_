# WAVE 1: Cache Optimization Plan
**Date:** 2026-06-24  
**Phase:** Wave 1 Sub-Agent 4 — Strategic Cache Management  
**Authority:** D-Tier Autonomous (@mbaetiong pre-approved)  
**Target Outcome:** Optimize 4-layer cache hierarchy to 95%+ hit rate

---

## Executive Summary

This plan maps **immediate, short-term, and medium-term optimizations** to improve cache hit rates from 92.6% → 95%+, expand Layer 3 adoption from 28% → 80%, and establish cache monitoring infrastructure.

**Total Estimated Impact:**
- **Hit Rate:** +2-3 percentage points
- **CI Speed:** 20-30% reduction
- **Workflow Coverage:** 14 → 35+ workflows enabled
- **Observability:** 0% → 100% coverage

---

## Phase 10 Optimization Roadmap

### WAVE 1 (Week 1 - IMMEDIATE)

#### Sprint 1A: Enable Cache Monitoring (2 hours)

**Objective:** Re-enable cache health tracking for observability

**Tasks:**
1. **Restore cache-health-monitor.yml** 
   - [ ] Uncomment workflow (currently stub only)
   - [ ] Wire to CacheManager.validate_cache_health()
   - [ ] Add metrics export to `.codex/cache_metrics.json`
   - [ ] Schedule: Daily at 02:00 UTC
   - **Deliverable:** Workflow reports cache health daily

2. **Integrate CacheIntelligence metrics**
   - [ ] Add callback hook in CacheManager
   - [ ] Export to `.codex/cache_intelligence_state.json`
   - [ ] Integrate with AAIS scoring
   - **Deliverable:** Real-time cache metrics available

3. **Create cache metrics dashboard**
   - [ ] Add CI job to post metrics to GitHub
   - [ ] Surface in job summary
   - [ ] Add trend tracking
   - **Deliverable:** Cache health visible in workflow summaries

**Files to Modify:**
- `.github/workflows/cache-health-monitor.yml`
- `src/codex/ci/cache_manager.py` (add metrics export)
- `.github/workflows/pr-checks.yml` (add metrics step)

**Acceptance Criteria:**
- ✅ Cache health metrics exported daily
- ✅ Hit rate trends tracked
- ✅ Zero CI slowdown from monitoring

---

#### Sprint 1B: Enable Pre-commit Caching (1.5 hours)

**Objective:** Cache pre-commit hook environments

**Current State:**
- Pre-commit runs on every PR
- No caching: ~3-5 min overhead
- Cache potential: Save 1-2 min (30-40%)

**Implementation:**

1. **Update pr-checks.yml**
   ```yaml
   - name: Restore pre-commit cache
     uses: actions/cache@v4
     with:
       path: ~/.cache/pre-commit
       key: ${{ runner.os }}-pre-commit-${{ hashFiles('.pre-commit-config.yaml') }}
       restore-keys: |
         ${{ runner.os }}-pre-commit-
   
   - name: Run pre-commit
     run: pre-commit run --all-files
   ```

2. **Update cache_manager.py to include pre-commit**
   - Already has PRE_COMMIT type
   - Verify cache paths: `~/.cache/pre-commit`
   - Add to dependency files tracking

3. **Test & validate**
   - Run pr-checks.yml 2-3 times
   - Verify cache hit in subsequent runs
   - Measure time reduction

**Files to Modify:**
- `.github/workflows/pr-checks.yml`
- Optionally: `.github/actions/setup-python-cached/action.yml`

**Acceptance Criteria:**
- ✅ Pre-commit cache enabled in pr-checks.yml
- ✅ Subsequent runs show cache hit
- ✅ Time savings: 1-2 min measured
- ✅ No false positives from cache invalidation

**Expected Impact:**
- pr-checks.yml: 180s → 150s (16% faster)
- All PRs benefit: ~60 min/day saved across org

---

#### Sprint 1C: Unify Cache Key Strategy (2 hours)

**Objective:** Establish consistent cache key generation across all workflows

**Current Problem:**
- Each workflow uses ad-hoc cache keys
- No standardization on key components
- Risk: False hits/misses from inconsistent naming

**Solution:** Adopt CacheManager key generation everywhere

**Implementation:**

1. **Create cache key generation script**
   - Wrapper around CacheManager
   - Usage: `generate-cache-key --type pip --workflow pr-checks`
   - Output: Consistent key format

2. **Document cache key format**
   ```
   Format: ${os}-${workflow}-${cache-type}-${dependency-hash}
   Example: Linux-pr-checks-pip-a1b2c3d4e5f6
   
   Components:
   - ${os}: runner.os (Linux, Windows, macOS)
   - ${workflow}: github.workflow (pr-checks, etc)
   - ${cache-type}: pip, pre-commit, mypy, etc
   - ${hash}: SHA256(dependency_files) [12 chars]
   
   Restore Keys (fallback chain):
   1. ${os}-${workflow}-${cache-type}-${hash}
   2. ${os}-${workflow}-${cache-type}-
   3. ${os}-
   ```

3. **Update existing workflows**
   - [ ] pr-checks.yml
   - [ ] build-agent-env-cache.yml  
   - [ ] code-quality-coverage-suite.yml
   - [ ] pages-mkdocs.yml
   - [ ] Any others with manual cache keys

4. **Create reusable GitHub Action**
   - Name: `cache/generate-key`
   - Usage: `uses: ./.github/actions/cache/generate-key`
   - Output: cache_key, restore_keys

**Files to Create/Modify:**
- `scripts/ci/generate_cache_keys.py` (already exists, enhance)
- `.github/actions/cache/generate-key/action.yml` (new)
- All workflow files using cache

**Acceptance Criteria:**
- ✅ Unified key format documented
- ✅ All workflows using consistent keys
- ✅ No cache pollution between workflows
- ✅ Restore key hierarchy working

---

### WAVE 2 (Week 2 - SHORT-TERM)

#### Sprint 2A: Expand Cache to Tool State (2.5 hours)

**Objective:** Cache tool state (.mypy_cache, .ruff_cache, .pytest_cache)

**Current Problem:**
- Tools redundantly analyze code every run
- mypy: 3-5 min to analyze full codebase
- ruff: 2-3 min for full check
- Cache potential: 20-30% time savings

**Implementation:**

1. **Update pr-checks.yml**
   ```yaml
   - name: Restore mypy cache
     uses: actions/cache@v4
     with:
       path: .mypy_cache
       key: ${{ runner.os }}-mypy-${{ hashFiles('pyproject.toml', 'src/**/*.py') }}
       restore-keys: |
         ${{ runner.os }}-mypy-
   
   - name: Restore ruff cache
     uses: actions/cache@v4
     with:
       path: .ruff_cache
       key: ${{ runner.os }}-ruff-${{ hashFiles('pyproject.toml', 'src/**/*.py') }}
       restore-keys: |
         ${{ runner.os }}-ruff-
   ```

2. **Add to CacheManager**
   - Update CACHE_PATHS for MYPY, RUFF, PYTEST
   - Verify paths are correct
   - Add to dependency tracking

3. **Test tool caches**
   - First run: Cache miss, full analysis
   - Second run: Cache hit, partial/incremental analysis
   - Measure time reduction

**Files to Modify:**
- `.github/workflows/pr-checks.yml`
- `src/codex/ci/cache_manager.py`

**Acceptance Criteria:**
- ✅ Tool caches stored in GH Actions cache
- ✅ Subsequent runs show time savings
- ✅ Cache invalidation on code changes working
- ✅ Cache size <500 MB per tool

**Expected Impact:**
- mypy: 5 min → 2 min (60% faster)
- ruff: 3 min → 1 min (67% faster)
- Overall pr-checks: 180s → 130s (28% faster)

---

#### Sprint 2B: Expand Cache to 10+ Workflows (3 hours)

**Objective:** Enable caching in 10+ additional workflows

**Current State:**
- 12/42 workflows cached (28%)
- Target: 25/42 (60%) by end of Phase 10

**Workflow Adoption Plan:**

| Workflow | Type | Estimated Time | Priority |
|----------|------|-----------------|----------|
| code-quality-coverage | Python | 20 min | HIGH |
| pages-mkdocs | Python | 20 min | HIGH |
| rust_swarm_ci | Rust | 30 min | HIGH |
| test-rag | Python | 20 min | MEDIUM |
| ml-validation | Python | 30 min | MEDIUM |
| lint | Python | 15 min | MEDIUM |
| security-audit | Python | 20 min | MEDIUM |

**Implementation for Each:**

1. **code-quality-coverage-suite.yml**
   ```yaml
   # Add pip cache
   - name: Restore pip cache
     uses: actions/cache@v4
     with:
       path: ~/.cache/pip
       key: ${{ runner.os }}-coverage-${{ hashFiles('pyproject.toml') }}
       restore-keys: |
         ${{ runner.os }}-coverage-
   
   # Add tool caches
   - name: Restore coverage cache
     uses: actions/cache@v4
     with:
       path: .coverage
       key: ${{ runner.os }}-coverage-${{ github.ref }}
       restore-keys: |
         ${{ runner.os }}-coverage-
   ```

2. **pages-mkdocs.yml**
   ```yaml
   - name: Restore docs cache
     uses: actions/cache@v4
     with:
       path: ~/.cache/pip
       key: ${{ runner.os }}-mkdocs-${{ hashFiles('requirements.txt') }}
       restore-keys: |
         ${{ runner.os }}-mkdocs-
   ```

3. **rust_swarm_ci.yml**
   ```yaml
   - name: Restore cargo cache
     uses: actions/cache@v4
     with:
       path: |
         ~/.cargo/registry
         ~/.cargo/git
         target
       key: ${{ runner.os }}-cargo-${{ hashFiles('Cargo.lock') }}
       restore-keys: |
         ${{ runner.os }}-cargo-
   ```

**Files to Modify:**
- `.github/workflows/code-quality-coverage-suite.yml`
- `.github/workflows/pages-mkdocs.yml`
- `.github/workflows/rust_swarm_ci.yml`
- Others as identified

**Acceptance Criteria:**
- ✅ 10+ workflows updated with caching
- ✅ Cache hits verified in workflow runs
- ✅ Time savings measured for each
- ✅ No false cache invalidations

**Expected Impact:**
- Each workflow: 10-20% speed improvement
- Organization total: ~150-200 min/week saved

---

#### Sprint 2C: Implement Cache Size Management (2 hours)

**Objective:** Manage Layer 2 cache to prevent threshold-based evictions

**Current Problem:**
- Layer 2 at 75% capacity (4.5 GB / 6 GB limit)
- Risk: When threshold crossed, aggressive evictions
- Solution: Implement intelligent size management

**Implementation:**

1. **Update cache-pruning.yml**
   - Increase frequency to bi-weekly
   - Lower threshold from 7 → 5 days
   - Add metrics collection
   - Report on freed space

2. **Create cache size optimizer**
   - Script: `scripts/ci/manage_cache_size.py`
   - Function: Identify low-hit caches for removal
   - Policy: Keep high-hit-rate caches, remove low-utility ones
   - Integration: Run weekly, report findings

3. **Configure size alerts**
   - Threshold: Alert at 80% capacity
   - Action: Trigger immediate pruning
   - Notification: Post to GitHub issue

**Implementation:**
```python
# scripts/ci/manage_cache_size.py

class CacheOptimizer:
    def __init__(self):
        self.hit_rate_threshold = 0.70
        self.age_threshold_days = 14
    
    def should_remove(self, cache):
        """Determine if cache should be removed."""
        return (
            cache.hit_rate < self.hit_rate_threshold and
            cache.age_days > self.age_threshold_days
        )
    
    def get_optimization_plan(self):
        """Generate cache optimization plan."""
        # Analyze current caches
        # Identify candidates for removal
        # Estimate freed space
        # Return recommendation
```

**Files to Modify:**
- `.github/workflows/cache-pruning.yml`
- Create: `scripts/ci/manage_cache_size.py`

**Acceptance Criteria:**
- ✅ Cache size management script implemented
- ✅ Layer 2 stays below 70% capacity
- ✅ Alerts triggered at 80%
- ✅ Weekly optimization report generated

---

### WAVE 3 (Week 3 - MEDIUM-TERM)

#### Sprint 3A: Implement Cache Warming (2 hours)

**Objective:** Pre-populate caches to maximize hit rates

**Strategy:**

1. **Create cache-warmup.yml workflow**
   - Trigger: On schedule (daily at 01:00 UTC) or manual
   - Purpose: Pre-download dependencies, tools
   - Benefit: First CI run of day starts with warm cache

2. **Identify cache "critical path" items**
   - Most-used dependencies (numpy, torch, transformers)
   - Language toolchains (Python 3.11, 3.12)
   - CI tools (ruff, mypy, pytest)

3. **Implementation:**
   ```yaml
   name: Cache Warmup
   on:
     schedule:
       - cron: '0 1 * * *'  # Daily at 01:00 UTC
   
   jobs:
     warmup:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - uses: ./.github/actions/setup-python-cached
         - run: |
             pip install -r requirements.txt -r requirements-dev.txt
             python -m mypy src
             python -m ruff check src
   ```

**Files to Create:**
- `.github/workflows/cache-warmup.yml`
- `.github/actions/cache/warmup/action.yml` (optional)

**Acceptance Criteria:**
- ✅ Cache warmup workflow scheduled
- ✅ All dependencies pre-downloaded
- ✅ First CI run of day sees 95%+ hit rate
- ✅ No performance regression from warming

---

#### Sprint 3B: Add Predictive Prefetching (3 hours)

**Objective:** Intelligently prefetch caches based on workflow type

**Concept:** Analyze workflow type → Prefetch likely-needed items

**Implementation:**

1. **Workflow Classification**
   - PR checks: Standard test environment
   - Code quality: Lint + type check tools
   - ML validation: ML dependencies
   - Docs: Documentation tools

2. **Prefetch Strategy**
   ```python
   PREFETCH_PROFILES = {
       "pr-checks": ["pip", "pre-commit", "mypy", "ruff"],
       "code-quality": ["ruff", "mypy", "pytest"],
       "ml-validation": ["pip", "huggingface", "torch"],
       "docs": ["pip", "mkdocs"],
   }
   ```

3. **Implementation in setup-python-cached**
   - Add `prefetch-profile` input
   - Based on workflow type, download additional cache items
   - Measure improvement

**Files to Modify:**
- `.github/actions/setup-python-cached/action.yml`
- `scripts/ci/cache_manager.py` (add prefetch logic)

**Acceptance Criteria:**
- ✅ Prefetch profiles defined for 5+ workflow types
- ✅ Prefetch reduces cache misses by 5-10%
- ✅ No performance degradation from prefetching
- ✅ Prefetch time < 30 seconds

---

#### Sprint 3C: Layer 4 Foundation (Redis preparation) (2 hours)

**Objective:** Lay groundwork for distributed caching (Phase 11)

**Current State:**
- Layer 4 uses DVC + HuggingFace hub
- No distributed cache backend (Redis/Memcached)
- Appropriate for current single-instance deployment

**Phase 11 Preparation:**

1. **Document Layer 4 strategy**
   - When Redis becomes necessary (scaling)
   - Configuration options
   - Integration points

2. **Create Redis configuration templates**
   - `docker-compose.yml` with Redis service
   - Environment variable setup
   - Connection pooling config

3. **Prepare DistributedCache for Redis**
   - Already has Redis backend implemented
   - Add documentation
   - Add configuration validation

**Files to Create:**
- `docs/cache/LAYER4_STRATEGY.md`
- `docker-compose.cache.yml` (Redis template)

**Acceptance Criteria:**
- ✅ Layer 4 strategy documented
- ✅ Redis configuration templates available
- ✅ No changes needed for current single-instance
- ✅ Ready for Phase 11 distributed deployment

---

## Implementation Timeline

### WEEK 1: IMMEDIATE (Highest Impact)

| Task | Duration | Priority | Owner |
|------|----------|----------|-------|
| Enable cache monitoring | 2 hrs | CRITICAL | Agent |
| Enable pre-commit caching | 1.5 hrs | CRITICAL | Agent |
| Unify cache key strategy | 2 hrs | CRITICAL | Agent |
| **Week 1 Total** | **5.5 hrs** | - | - |

**Expected Impact:**
- Hit rate: 92.6% → 93.5%
- CI speed: 15% improvement
- Observability: Fully enabled

---

### WEEK 2: SHORT-TERM (Adoption & Expansion)

| Task | Duration | Priority | Owner |
|------|----------|----------|-------|
| Tool state caching | 2.5 hrs | HIGH | Agent |
| 10+ workflow adoption | 3 hrs | HIGH | Agent |
| Cache size management | 2 hrs | MEDIUM | Agent |
| **Week 2 Total** | **7.5 hrs** | - | - |

**Expected Impact:**
- Hit rate: 93.5% → 94.5%
- CI speed: 25% improvement
- Workflow coverage: 28% → 60%

---

### WEEK 3: MEDIUM-TERM (Optimization)

| Task | Duration | Priority | Owner |
|------|----------|----------|-------|
| Cache warming | 2 hrs | MEDIUM | Agent |
| Predictive prefetching | 3 hrs | MEDIUM | Agent |
| Layer 4 foundation | 2 hrs | LOW | Agent |
| **Week 3 Total** | **7 hrs** | - | - |

**Expected Impact:**
- Hit rate: 94.5% → 95%+
- CI speed: 30% improvement
- Observability: Advanced metrics

---

## Success Metrics

### Primary Metrics

| Metric | Current | Target | Stretch |
|--------|---------|--------|---------|
| Overall Hit Rate | 92.6% | 95% | 97% |
| L3 Adoption | 28% | 60% | 80% |
| Cache Health Monitoring | Disabled | Enabled | Real-time |
| Average CI Speed | 180s | 140s | 120s |

### Secondary Metrics

- Pre-commit cache hit rate: 0% → 85%+
- Tool state cache hit rate: 0% → 80%+
- Cache size stability: <75% utilization
- Zero cache-related CI failures

### Impact Metrics

- **Org-wide CI time saved per week:** 0 min → 300+ min
- **GitHub Actions cost reduction:** 0% → 15%
- **Developer experience:** Faster feedback loops

---

## Risk Mitigation

### Risk: Cache Key Collision

**Risk:** Inconsistent keys cause false hits

**Mitigation:**
- ✅ Unified key generation script
- ✅ Key format documentation
- ✅ Validation in CI pipeline

---

### Risk: Cache Bloat

**Risk:** Layer 2 exceeds capacity → Aggressive evictions

**Mitigation:**
- ✅ Size monitoring enabled
- ✅ Bi-weekly pruning
- ✅ Alerts at 80% capacity

---

### Risk: Workflow Performance Regression

**Risk:** Cache warming/prefetch adds latency

**Mitigation:**
- ✅ Timeout guards (<30s for warmup)
- ✅ Conditional enabling based on cache miss rates
- ✅ Rollback plan if regression detected

---

## Rollback Strategy

Each sprint has clear rollback:

1. **Cache Monitoring** → Simply disable cache-health-monitor.yml
2. **Pre-commit Cache** → Remove cache step from pr-checks.yml
3. **Tool State Cache** → Remove .mypy_cache/.ruff_cache steps
4. **10+ Workflows** → Remove cache steps from each workflow

No code changes required, pure workflow YAML modifications.

---

## Phase 10 Expected Outcomes

Upon completion of all three waves:

```
BEFORE (Current State):
  Overall Hit Rate:     92.6%
  L3 Adoption:          28% (12/42 workflows)
  Cache Monitoring:     Disabled
  Avg CI Duration:      180s
  CI Costs:             Baseline

AFTER (Phase 10 Complete):
  Overall Hit Rate:     95.2% (+2.6%)
  L3 Adoption:          65% (27/42 workflows)
  Cache Monitoring:     Enabled (daily)
  Avg CI Duration:      140s (-22%)
  CI Costs:             -15% (~$3K/month saved)
  
ADDITIONAL BENEFITS:
  - Developer experience: Faster feedback
  - Cache reliability: Fully observable
  - Operational confidence: Metrics-driven decisions
```

---

## Phase 11+ Roadmap

### Short-term (Phase 11)

- [ ] Redis deployment for distributed caching
- [ ] Database query result caching
- [ ] Advanced cache analytics and predictions
- [ ] Cache-aware resource allocation

### Long-term (Phase 12+)

- [ ] Machine learning-based prefetching
- [ ] Cross-org cache sharing (if multi-tenant)
- [ ] Cache cost optimization engine
- [ ] Autonomous cache tuning

---

## Execution Checklist

- [x] Audit completed (92.6% baseline established)
- [x] Optimization plan created (3 waves, 20 hrs total)
- [x] Success metrics defined
- [x] Risk mitigation planned
- [x] Rollback strategy documented
- [ ] Week 1 execution (immediate tasks)
- [ ] Week 2 execution (short-term tasks)
- [ ] Week 3 execution (medium-term tasks)
- [ ] Validation & measurement
- [ ] Phase 10 completion report

---

## Conclusion

This optimization plan will systematically improve the cache hierarchy from solid (92.6%) to excellent (95%+), expand adoption from 28% to 65% of workflows, and establish comprehensive monitoring infrastructure. The phased approach minimizes disruption while delivering rapid improvements.

**Phase 10 Timeline:** 3 weeks  
**Total Effort:** ~20 hours  
**Estimated ROI:** 300+ min/week CI time saved ($3K+ annual cost reduction)

---

**Plan Created:** 2026-06-24 01:08:59 UTC  
**Agent:** Wave 1 Sub-Agent 4 (Cache Management)  
**Authority:** D-Tier Autonomous (@mbaetiong pre-approved)  
**Ready for Execution:** ✅ YES
