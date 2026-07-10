# Phase 12 WS3 Tier 2 Lane 7: CI/CD Optimization Roadmap

**Execution Date**: 2026-07-08
**Authority**: D-tier autonomous
**Campaign**: Performance Optimization for Phase 13 Scaling

---

## 🗺️ Implementation Timeline

### Phase 1: Quick Wins (Week 1) — Expected: 40-50% improvement on affected workflows

#### Week 1, Day 1-2: Foundation Setup (2h)
- [x] Analyze current workflow performance
- [x] Identify bottlenecks
- [x] Create optimization plan
- [ ] Set up performance monitoring dashboard

**Tasks**:
1. **Parallelize Python Matrix Tests** (0.5h)
   - File: `.github/workflows/ml-tests.yml`, `auth-tests.yml`
   - Change: Add `max-parallel: 3` to matrix strategy
   - Expected: Save 8-12 min per workflow
   - Test: Run all 3 Python versions simultaneously
   - Validation: Confirm all versions pass

2. **Implement pip Cache Strategy** (2h)
   - Files: All workflows with `pip install`
   - Pattern:
     ```yaml
     - uses: actions/cache@v5
       with:
         path: ~/.cache/pip
         key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
     ```
   - Expected: Save 5-8 min per workflow
   - Validation: Verify cache hits in logs

3. **Create Dependency Installation Action** (1h)
   - File: `.github/actions/setup-dependencies`
   - Centralize: pytest, bandit, semgrep, etc.
   - Expected: Save 2-3 min per workflow + reduce duplication
   - Validation: Compare before/after artifact counts

4. **Add Conditional Test Execution** (2h)
   - File: `.github/workflows/reusable-test.yml`
   - Use: `dorny/paths-filter@v2`
   - Pattern: Only run tests for changed modules
   - Expected: Save 5-15 min on non-main branches
   - Validation: Test on feature branch

**Estimated Savings**: 600-900 min/week

---

#### Week 1, Day 3-5: Quick Implementation (4h)
5. **Implement Smart Artifact Caching** (2.5h)
   - Files: `auth-tests.yml`, `ml-tests.yml`
   - Changes:
     - Only upload coverage diffs (instead of full reports)
     - Archive old reports separately
     - Implement artifact compression
   - Expected: Save 8-12 min per workflow
   - Validation: Verify artifact retrieval works

6. **Optimize PyTorch Installation** (1h)
   - Options:
     a. Pre-cache PyTorch wheel
     b. Install only on demand
     c. Use CPU-only variant
   - Expected: Save 3-5 min per install
   - Validation: Confirm PyTorch available in tests

7. **Add Workflow Performance Monitoring** (0.5h)
   - Tool: GitHub Actions workflow metrics
   - Track: Execution time, success rate, resource usage
   - Expected: Enable data-driven optimization
   - Validation: Dashboard shows metrics

**Estimated Savings**: 400-600 min/week

**Cumulative Phase 1 Savings**: 1000-1500 min/week (20-35% reduction)

---

### Phase 2: Medium Priority (Week 2-3) — Expected: Additional 25-30% improvement

#### Week 2, Day 1-3: Consolidation (4h)
8. **Consolidate Security Scans** (2h)
   - Current: bandit, detect-secrets, semgrep, CodeQL separate
   - New: Single composite job with aggregated results
   - Files: `auth-tests.yml`, create `security-tests.yml`
   - Expected: Save 10-15 min per workflow
   - Validation: All scans still report correctly

9. **Create Modular Test Suite Markers** (3h)
   - Implementation:
     - Mark existing tests: `@pytest.mark.unit`, `@pytest.mark.slow`
     - Files: All test files in `tests/`
     - Create CI filters: `-m unit`, `-m integration`
   - Expected: Save 15-20 min on fast paths
   - Validation: Test different marker combinations

10. **Implement Workflow Deduplication** (4h)
    - Create: `.github/workflows/reusable-test.yml`
    - Create: `.github/workflows/reusable-security.yml`
    - Create: `.github/workflows/reusable-coverage.yml`
    - Expected: 30+ fewer workflow files, reduced maintenance
    - Validation: All callers work correctly

**Estimated Savings**: 600-800 min/week

#### Week 2, Day 4-5 & Week 3: Advanced Setup (8h)
11. **Upgrade to Latest Actions** (1h)
    - Upgrade: checkout@v4→v5, cache@v3→v5, setup-python@v4→v5
    - Expected: 2-5 min per workflow
    - Validation: Run on feature branch

12. **Add Fail-Fast Strategy** (0.5h)
    - Add: `fail-fast: true` to matrix strategies
    - Expected: Stop early on failures, save debug time
    - Validation: Test on multi-OS matrix

13. **Implement Test Grouping** (2h)
    - Files: `tests/` structure review
    - Pattern: Logical test grouping by module
    - Expected: Enable selective test running
    - Validation: Each group runs independently

14. **Create Optimization Metrics Dashboard** (3h)
    - Tool: GitHub Pages + GitHub API
    - Metrics:
      - Workflow execution time trends
      - Cache hit rates
      - Cost per workflow
      - Test execution patterns
    - Expected: Data-driven decision making
    - Validation: Dashboard updates automatically

**Estimated Savings**: 500-700 min/week + better visibility

**Cumulative Phase 2 Savings**: 1100-1500 min/week (additional 25-35%)

---

### Phase 3: Advanced Optimization (Week 4+) — Expected: Additional 35-40% improvement

#### Week 4, Day 1-3: Distributed Testing (6h)
15. **Implement Test Sharding** (6h)
    - Pattern: Distribute tests across 4-6 runners
    - Implementation:
      ```yaml
      strategy:
        matrix:
          shard: [1, 2, 3, 4]
      run: pytest tests/ --co -q | \
        awk "NR%${{ strategy.job-total }}==${{ strategy.job-index }}" | \
        xargs pytest
      ```
    - Expected: 25-35 min per workflow (from 45-60)
    - Validation: All tests still pass, coverage maintained

16. **Create Custom CI Container** (5h)
    - Dockerfile:
      ```dockerfile
      FROM ubuntu:22.04
      RUN apt-get update && apt-get install -y \
        python3.12 python3.12-venv git curl
      RUN pip install -r requirements.txt
      ```
    - Expected: 10-15 min per workflow
    - Validation: Image builds, tests pass

17. **Implement Artifact Mirror** (5h)
    - Setup: S3 or GitHub artifact cache
    - Scope: Large files (models, wheels, archives)
    - Expected: 8-12 min per workflow
    - Validation: Mirror sync works

**Estimated Savings**: 1000+ min/week

---

## 📅 Detailed Timeline

### Week 1 (Complete by Friday EOD)
```
Mon-Tue:   Quick wins setup
Wed:       Parallel matrix + cache implementation
Thu-Fri:   Artifact optimization + validation
Savings:   20-35% improvement
```

### Week 2-3 (Complete by Friday EOD)
```
Week 2:    Security consolidation + test markers
Week 3:    Workflow deduplication + dashboard
Savings:   Additional 25-35% improvement
```

### Week 4+ (Ongoing optimization)
```
Week 4+:   Distributed testing, containers, mirrors
Savings:   Additional 35-40% improvement
```

---

## 🎯 Success Criteria & Validation

### Phase 1 Validation (Week 1)
- [ ] Cache hit rate: >85% (measurement)
- [ ] Parallel matrix: All 3 versions run simultaneously
- [ ] Artifact upload time: <2 min (was 3-5)
- [ ] pip install time: <3 min (was 8-12)
- [ ] Conditional tests: Skip on non-main branches
- [ ] Performance dashboard: Shows baseline metrics

**Success**: All Phase 1 optimizations deployed and validated

### Phase 2 Validation (Week 3)
- [ ] Security scans consolidated: Single job
- [ ] Test markers: All tests have category
- [ ] Reusable workflows: Used by 10+ callers
- [ ] Code duplication: <20% (from current 40-60%)
- [ ] Workflow maintenance time: 30% reduction
- [ ] Coverage reporting: Still accurate

**Success**: All Phase 2 optimizations deployed and validated

### Phase 3 Validation (Week 4+)
- [ ] Test sharding: 4-6 runners executing in parallel
- [ ] Distributed execution: <35 min average (from 60)
- [ ] Custom container: <30 sec boot overhead
- [ ] Artifact mirror: Reduces transfer time by 60%
- [ ] Cost reduction: 30-40% (via optimizations)

**Success**: All Phase 3 optimizations deployed and validated

---

## 💰 Cost Analysis

### Current Cost Estimate (Baseline)
```
Workflow Runs per Day:     50
Average Duration:          50 minutes
Monthly Run Hours:         37,500 hours
GitHub Actions Cost:       $0.008 per minute × 37,500 = $300/month
```

### Phase 1 Optimization (20-35% reduction)
```
New Average Duration:      33-40 minutes
Monthly Cost:              $195-240 (35-40% savings)
Cost Savings:              $60-105/month
```

### Phase 2-3 Optimization (45-55% total reduction)
```
New Average Duration:      22-27 minutes
Monthly Cost:              $110-135 (55-60% savings)
Cost Savings:              $165-190/month
Annual Savings:            $2,000-2,300
```

---

## 📊 Metrics & Monitoring

### Key Metrics to Track
```
1. Average Workflow Duration (minutes)
   Baseline: 45-60 → Phase 1: 33-40 → Phase 3: 22-27

2. Cache Hit Rate (%)
   Baseline: 65-75% → Target: >85%

3. Test Pass Rate (%)
   Baseline: 98.5% → Target: >99%

4. Artifact Upload Time (seconds)
   Baseline: 180-300 → Phase 1: <120 → Phase 3: <60

5. Dependency Install Time (minutes)
   Baseline: 8-12 → Phase 1: <3 → Phase 3: <1

6. Cost per Workflow (USD)
   Baseline: $0.40 → Phase 3: $0.18
```

### Monitoring Dashboard
- URL: `https://pages.github.com/aries-serpent/codex/performance`
- Update Frequency: Daily
- Data Retention: 90 days

---

## 🚨 Risk Management

### Risk: Cache Invalidation (MEDIUM)
- Mitigation: Version cache keys, implement manual clear
- Contingency: Disable cache temporarily if issues
- Testing: Verify on feature branch first

### Risk: Test Parallelization Issues (MEDIUM)
- Mitigation: Ensure test isolation, separate DBs
- Contingency: Fall back to sequential execution
- Testing: Run full suite on staging first

### Risk: Reusable Workflow Breaking Changes (MEDIUM)
- Mitigation: Version reusable workflows
- Contingency: Keep old version available
- Testing: Test all callers on feature branch

### Risk: Performance Regression (LOW)
- Mitigation: Continuous monitoring, assertions
- Contingency: Revert changes, investigate
- Testing: Compare before/after metrics

---

## 📋 Checklist & Tracking

### Phase 1 Implementation
- [ ] Parallelize Python matrix (ml-tests.yml, auth-tests.yml)
- [ ] Implement pip cache (all workflows)
- [ ] Create dependency action
- [ ] Add conditional test execution
- [ ] Smart artifact caching
- [ ] PyTorch optimization
- [ ] Performance monitoring setup
- [ ] Phase 1 validation complete

### Phase 2 Implementation
- [ ] Consolidate security scans
- [ ] Create test markers (all test files)
- [ ] Implement workflow deduplication
- [ ] Upgrade GitHub Actions
- [ ] Add fail-fast strategy
- [ ] Test grouping
- [ ] Metrics dashboard
- [ ] Phase 2 validation complete

### Phase 3 Implementation
- [ ] Test sharding implementation
- [ ] Custom CI container
- [ ] Artifact mirror setup
- [ ] Cost analysis update
- [ ] Final optimization
- [ ] Phase 3 validation complete

---

## 🔗 Related Artifacts

- `PHASE_12_WS3_TIER2_LANE7_PERFORMANCE_MONITORING.md` - Main report
- `.codex/perf/baselines.json` - Performance baselines
- `.github/actions/setup-dependencies/` - Dependency action
- `.github/workflows/reusable-test.yml` - Reusable test workflow
- Performance Dashboard: `https://pages.github.com/aries-serpent/codex/performance`

---

## ✅ Implementation Complete

**Status**: Ready for implementation
**Next Step**: Begin Phase 1 implementation (Week 1)
**Owner**: Performance Optimization Team
**Approval**: D-tier autonomous (@mbaetiong standing approval)

---

Generated: 2026-07-08
Authority: Phase 12 WS3 Tier 2 Lane 7
