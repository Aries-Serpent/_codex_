# Agent Brief: Wave 5 - Cache & Performance Optimization

**Target Agent:** cache-management-agent  
**Authority:** @mbaetiong (Autonomous GO CONTINUE)  
**Timeline:** Staged rollout (parallel with Waves 2-3-4)  
**Target:** CI time <30 min, optimized 4-layer cache hierarchy  
**Status:** READY FOR DISPATCH  
**Coordinating Brief:** AGENT_BRIEF_STAGE_5_WAVE2_DELEGATION.md (Stage 5, Phase 6 Wave 1)

---

## Mission

Implement Phase 5 Lane 5.5A audit findings to optimize build and runtime performance across the 4-layer cache hierarchy. Reduce CI pipeline execution time to <30 minutes and improve cache hit rates across Docker builds, GitHub Actions artifacts, application runtime, and persistent data layers.

---

## Executive Summary

Phase 5 Lane 5.5A identified optimization opportunities across all caching layers:

| Layer | Current State | Target | Opportunity | Priority |
|-------|--------------|--------|-------------|----------|
| **1: Build Cache** | Docker multi-stage not optimized | <15 min build | Reorder Dockerfile layers | HIGH |
| **2: Artifact Cache** | Actions cache ~60% hit rate | >85% hit rate | Dependency/coverage cache | HIGH |
| **3: Runtime Cache** | Basic in-memory (no TTL) | In-memory + Redis | Structured caching layer | MEDIUM |
| **4: Persistent Cache** | Database queries N/A for build | Async result cache | Optional for ML pipelines | LOW |

**Overall CI Target:** 34-40 min → <30 min (25% reduction)

---

## 4-Layer Cache Hierarchy Architecture

### Layer 1: Build Cache (Docker)

**Current State:**
- Multi-stage Dockerfile with ~12 stages
- Layer ordering suboptimal (frequent changes early)
- No layer pinning or caching strategy

**Optimization Strategy:**

1. **Reorder Dockerfile layers**
   ```dockerfile
   # Optimal order: stable → frequently changing
   
   # Stage 0: Base system packages (stable, cached)
   FROM python:3.12-slim AS base
   RUN apt-get update && apt-get install -y build-essential ...
   
   # Stage 1: Python dependencies (semi-stable, cached)
   COPY pyproject.toml requirements*.txt ./
   RUN pip install -r requirements-ci.txt
   
   # Stage 2: Application code (frequently changing, cache miss)
   COPY src ./src
   RUN pip install -e .
   
   # Stage 3: Tests (final, always runs)
   COPY tests ./tests
   RUN pytest ...
   ```

2. **Implement Docker buildkit caching**
   - Use `DOCKER_BUILDKIT=1` in CI workflows
   - Enable inline cache output
   - Store cache in GitHub Actions cache

3. **Separate CI and runtime images**
   - Minimal runtime image (exclude test/dev deps)
   - Full CI image with testing tools

**Expected Impact:** Build time 18-25 min → <15 min (35-40% reduction)

### Layer 2: GitHub Actions Artifact Cache

**Current State:**
- Basic actions/cache@v3 with key pattern: `pip-${{ hashFiles('requirements.txt') }}`
- Hit rate: ~60% (many cache misses on dependency changes)
- No coverage/build artifact caching

**Optimization Strategy:**

1. **Granular dependency caching**
   ```yaml
   - name: Cache pip dependencies
     uses: actions/cache@v3
     with:
       path: ~/.cache/pip
       key: pip-${{ runner.os }}-${{ hashFiles('**/requirements*.txt') }}
       restore-keys: |
         pip-${{ runner.os }}-
   
   - name: Cache pre-commit
     uses: actions/cache@v3
     with:
       path: ~/.cache/pre-commit
       key: pre-commit-${{ hashFiles('.pre-commit-config.yaml') }}
   ```

2. **Build artifact caching**
   ```yaml
   - name: Cache build artifacts
     uses: actions/cache@v3
     with:
       path: |
         build/
         dist/
         .tox/
       key: build-${{ github.sha }}
       restore-keys: build-
   ```

3. **Coverage data caching**
   ```yaml
   - name: Cache coverage files
     uses: actions/cache@v3
     with:
       path: .coverage*
       key: coverage-${{ github.ref }}-${{ github.sha }}
   ```

4. **Test result caching**
   - Cache pytest cache directory (.pytest_cache)
   - Cache mypy cache (.mypy_cache)

**Expected Impact:** Artifact cache hit rate 60% → >85% (25 min reduction per miss avoided)

### Layer 3: Application Runtime Cache

**Current State:**
- Basic in-memory caching in some modules
- No TTL or eviction strategy
- No distributed caching (single-instance)

**Optimization Strategy:**

1. **Structured caching layer** (if applicable to runtime)
   ```python
   from codex.caching import CacheManager
   
   cache = CacheManager(
       backend='memory',  # or 'redis'
       ttl=300,  # 5 minutes
       max_size=1000
   )
   
   @cache.memoize
   def expensive_operation(x):
       return compute(x)
   ```

2. **Redis optional integration** (post-Wave 5)
   - For persistent caching across restarts
   - For distributed caching (if multi-instance)
   - Out of scope for Wave 5 MVP

**Expected Impact:** Runtime performance +15-20% (if applicable)

### Layer 4: Persistent Cache (Database)

**Current State:**
- Not applicable for build pipeline
- Optional for ML training pipeline (model caching, embeddings)

**Optimization Strategy (Optional):**
- Cache embedding computations (RAG module)
- Store pre-computed ML metrics
- Async result cache for long-running operations

**Expected Impact:** Optional; ML pipeline speedup if implemented

---

## Optimization Tasks (Staged Rollout)

### Stage 1: Build Cache Optimization (Week 1)

**Task 5A-1: Dockerfile Analysis & Reordering**
- Current: Analyze existing Dockerfile for cache busting
- Action: Reorder layers to maximize cache efficiency
- Estimated effort: 4-6 hours
- Risk: Build behavior must remain identical
- Timeline: By end of Week 1

**Deliverable:**
- Optimized Dockerfile with layer ordering rationale
- Build time benchmark (before/after)
- Commit: `feat(cache): optimize Dockerfile layer ordering for build cache`

### Stage 2: GitHub Actions Cache Configuration (Week 1-2)

**Task 5A-2: Implement Granular Caching**
- Update all workflows to use optimized cache keys
- Add coverage/build artifact caching
- Configure cache retention policies

**Workflows to update:**
- `pr-checks.yml` - main CI workflow
- `code-quality-coverage-suite.yml` - coverage workflow
- `mypy-baseline.yml` - type checking workflow
- `nox_gates.yml` - nox test runner
- `docker-build-push.yml` - container builds

**Estimated effort:** 8-12 hours (1 hour per workflow + testing)

**Timeline:** Week 2

**Deliverable:**
- Updated workflow files with cache configuration
- Cache hit rate metrics before/after
- Commit: `feat(cache): implement granular GitHub Actions caching`

### Stage 3: CI Pipeline Consolidation (Week 2-3)

**Task 5A-3: Reduce Workflow Redundancy**
- Identify duplicate workflow steps across workflows
- Consolidate into composite actions where applicable
- Example: All workflows run pytest → extract to composite

**Expected opportunity:** 5-10% time reduction from consolidation

**Estimated effort:** 6-10 hours

**Timeline:** Week 2-3

**Deliverable:**
- Composite actions for common patterns
- Workflows updated to use composites
- Commit: `feat(cache): consolidate CI workflows with composite actions`

### Stage 4: Performance Monitoring (Week 3+)

**Task 5A-4: Establish Metrics Dashboard**
- Track cache hit rates by layer
- Monitor CI execution time trends
- Alert on performance regressions

**Metrics to track:**
- Docker build time (Layer 1)
- Cache hit rate % (Layer 2)
- Total CI time per workflow
- Cost per workflow run (if available)

**Expected effort:** 4-8 hours (setup + initial reporting)

**Timeline:** Week 3+

**Deliverable:**
- Metrics collection script (.codex/cache_metrics.py)
- Dashboard/reports (.codex/WAVE_5_CACHE_METRICS.json)
- Commit: `feat(cache): implement performance monitoring`

---

## Success Criteria

- ✅ CI pipeline execution time: 34-40 min → <30 min (25%+ reduction)
- ✅ Docker build time: 18-25 min → <15 min (35%+ reduction)
- ✅ Artifact cache hit rate: 60% → >85%
- ✅ All workflows passing (100% success rate)
- ✅ No regressions in test results or build artifacts
- ✅ Cache configuration documented
- ✅ Performance monitoring established
- ✅ Cost optimization verified (if tracked)

---

## Dependencies & Preconditions

**Phase 6 Prerequisites:**
- Stage 4 completion: 79 TIER-1 tests implemented ✅
- All workflows stabilized and passing ✅

**Phase 5 Reference Data:**
- Phase 5 Lane 5.5A audit report (.json or .md)
- Current CI execution time baseline
- Current Docker build time benchmark

**External Dependencies:**
- GitHub Actions cache service (standard, no additional setup)
- Docker buildkit support (most runners support this)
- Python environment for metrics collection

---

## Constraints & Risks

| Risk | Severity | Mitigation |
|------|----------|-----------|
| Cache invalidation too aggressive | MEDIUM | Use conservative cache key patterns; avoid hash-based expiry |
| Build artifact conflicts across PRs | MEDIUM | Use commit SHA in cache key; separate by branch |
| False negatives from cache hits | LOW | Validate cache contents periodically; rebuild if suspect |
| Workflow changes break cache keys | MEDIUM | Document cache key strategy; audit before changes |
| Docker layer reordering breaks build | HIGH | Test rebuilt images thoroughly; maintain parity with existing image |

---

## Dispatch Options

### Option A: Full Optimization (Recommended)
- All 4 stages completed in 3-4 weeks
- Risk: Medium (multiple moving parts)
- Timeline: 3-4 weeks
- Recommended for @mbaetiong's timeline

### Option B: MVP (Conservative)
- Stages 1-2 only (Docker + Actions caching)
- Risk: Low (focused scope)
- Timeline: 1-2 weeks
- Results: 15-20% total time reduction (partial progress)

### Option C: Incremental (Recommended)
- Stage 1: Docker build cache (Week 1) — 35% reduction
- Stage 2: Actions caching (Week 2) — 10% additional reduction
- Stage 3: Consolidation (Week 3) — 5% additional reduction
- Stage 4: Monitoring (Week 3+) — ongoing optimization
- Risk: Low (staged delivery)
- Timeline: 3-4 weeks
- Results: 50%+ time reduction over time

**Recommended Approach:** Option C (Incremental Staged Rollout)

---

## Agent Instructions

### Pre-Dispatch Checklist

- [x] Authority verified: @mbaetiong pre-approved Wave 5
- [x] Current cache configuration analyzed
- [x] Phase 5 Lane 5.5A audit report available
- [x] CI/CD pipelines documented
- [x] Communication channels active (dashboard)

### Dispatch Command

```bash
@copilot-assignment
Agent: cache-management-agent
Brief: AGENT_BRIEF_STAGE_5_WAVE5_CACHE.md
Authority: @mbaetiong (Autonomous GO CONTINUE)
Mode: Staged rollout (Option C recommended)
Timeline: Continuous (parallel with Waves 2-3-4)
Target: CI <30 min, cache hit rate >85%, Docker build <15 min
Coordination: PHASE_6_WAVE2_COORDINATION_DASHBOARD.md

PROCEED WITH CACHE OPTIMIZATION
```

---

## Output Artifacts

**Commits:**
- Format: `feat(cache): Wave 5 — <layer> optimization (<metric> reduction)`
- Example: `feat(cache): Wave 5 — Docker build cache optimization (18-25m → <15m)`

**PRs:**
- 1 PR per stage (4 PRs total) or consolidated as preferred
- Before/after performance benchmarks attached
- Cache metrics and monitoring data included

**Documentation:**
- Cache strategy guide: `.codex/CACHE_STRATEGY_GUIDE.md`
- Per-stage report: `.codex/WAVE_5_STAGE_N_COMPLETION_REPORT.md`
- Metrics dashboard: `.codex/WAVE_5_CACHE_METRICS.json`
- Final report: `.codex/PHASE_6_WAVE_5_FINAL_REPORT.md`

---

**Coordinating Authority:** @mbaetiong  
**Autonomous Mode:** GO CONTINUE (all decision points approved)  
**Parallel Dispatch:** YES (independent of Waves 2-3-4)  
**Escalation Path:** Direct to @mbaetiong or agent-orchestrator
