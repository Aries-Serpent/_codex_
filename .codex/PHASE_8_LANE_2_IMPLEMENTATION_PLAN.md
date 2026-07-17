# PHASE 8 LANE 2: DETAILED IMPLEMENTATION PLAN

**Status:** 🟢 READY FOR EXECUTION  
**Authority:** D-Tier Autonomous (@mbaetiong)  
**Start Time:** 2026-07-17T18:20Z  
**End Time:** 2026-07-18T04:00Z (26 hours)  
**Checkpoints:** Every 6 hours

---

## EXECUTION TIMELINE

### Hour 0-2: Layer 1 Foundation (pip/npm keys)
**Objective:** Fix 14 generic cache keys + add missing hashFiles to 12 workflows

**Tasks:**
```
1. autonomy-phase-ci-matrix.yml
   - Change: ${{ runner.os }}-pytest-${{ github.sha }}
   - To: ${{ runner.os }}-${{ github.workflow }}-pytest-${{ hashFiles('tests/**/*.py') }}

2. pr-checks.yml
   - Add hashFiles('**/pyproject.toml', '**/requirements*.txt')
   - Add restore-keys pattern

3. code-quality-coverage-suite.yml
   - Update pip cache key
   - Optimize path specificity

4. test-rag.yml
   - Verify ML model cache (currently well-configured)

... (10+ more workflows)
```

**Success Criteria:**
- 14 generic keys replaced with hash-based keys
- 12 workflows with complete hashFiles
- All use 3-level restore-keys
- Sample test runs show cache hits

### Hour 2-4: Layer 2 Build Cache (cargo)
**Objective:** Optimize rust_swarm_ci.yml and related build caches

**Tasks:**
```
1. rust_swarm_ci.yml
   - Add Cargo.lock hashing
   - Separate registry vs build artifacts
   - Test cargo build times

2. Build artifact caching (2 workflows)
   - Implement selective caching
   - Profile cache size impact
```

**Success Criteria:**
- Cargo cache keys include Cargo.lock hash
- Build times show improvement
- Cache size within acceptable range

### Hour 4-6: Layer 3 Dependency Expansion
**Objective:** Add npm/poetry/pyenv caching where applicable

**Tasks:**
```
1. Scan for npm workflows (6 identified)
   - Add npm package cache configuration
   - Use package-lock.json hashing

2. Document poetry/uv caching (future)
   - Create templates for optional impl
```

**Success Criteria:**
- npm workflows have optimized caching
- Templates created for future languages
- Test runs verify hit rates

### Hour 6-8: Consolidation & Deduplication
**Objective:** Merge 20+ redundant cache entries

**Tasks:**
```
1. Consolidate pytest caches (18 instances)
   - Merge to 3 common patterns
   - Implement shared keys where safe

2. Consolidate pip caches (12 instances)
   - Group by workflow type
   - Reduce storage footprint

3. Consolidate coverage caches (3 instances)
   - Merge with test cache

4. Evaluate custom single-use keys (8)
   - Generalize if possible
   - Document if workflow-specific
```

**Success Criteria:**
- 20+ consolidations completed
- Storage reduced 40-60%
- No functionality regressions

### Hour 8-10: Checkpoint 1 - Layer 1 & 2 Complete

**Validation:**
```
✅ All pip/npm cache keys use hashFiles
✅ All 33 workflows have restore-keys
✅ No generic ${{ runner.os }}-*-cache keys remain
✅ Sample runs show cache hits in logs
✅ Expected hit rate: 50-55%
✅ Cache size: Same or reduced
✅ No new failures
```

**Decision Point:**
- ✅ If metrics good: Continue to Layer 3/4
- 🟡 If metrics concerning: Diagnostic run
- ❌ If failures: Rollback and troubleshoot

### Hour 10-14: Layer 3 Full Expansion + Monitoring
**Objective:** Complete dependency caching, set up monitoring

**Tasks:**
```
1. npm caching (6 workflows)
   - Implement package-lock.json caching
   - Test incremental npm ci

2. Pre-commit hook caching
   - Add dedicated pre-commit cache
   - Hash .pre-commit-config.yaml

3. HuggingFace/Torch models
   - Verify test-rag.yml configuration
   - Separate model layers if beneficial

4. Monitoring setup
   - Create cache-health-monitor.yml
   - Set up daily reporting
   - Configure alerts
```

**Success Criteria:**
- Layer 3 caching fully deployed
- Monitoring infrastructure ready
- Expected hit rate: 55-65%

### Hour 14-20: Layer 4 & Final Optimizations
**Objective:** Fine-tune ML caches, consolidate final entries

**Tasks:**
```
1. ML model cache refinement (test-rag.yml)
   - Separate model layers
   - Verify cache separation works

2. Final consolidation pass (remaining entries)
   - Review for last opportunities
   - Document all cache patterns

3. Cache-busting strategy docs
   - Document manual triggers
   - Create update procedures
   - Define TTL windows

4. Performance profiling
   - Run workflow suite
   - Measure cache hit improvements
   - Document before/after times
```

**Success Criteria:**
- Expected hit rate: 60%+
- Cache size: <100 GB
- Cache-busting strategy documented
- Performance improvements measurable

### Hour 20-24: Checkpoint 2 - Consolidation Complete

**Validation:**
```
✅ 20+ cache consolidations completed
✅ Layer 3 coverage expanded
✅ Monitoring infrastructure ready
✅ Expected hit rate: 55-65%
✅ Cache storage: -40-60% reduction
✅ CI time reduction: 8-12% visible
✅ All tests passing
```

**Decision Point:**
- ✅ If hit rate ≥60%: Proceed to final validation
- 🟡 If hit rate 55-59%: Continue optimization
- ❌ If hit rate <55%: Activate recovery procedures

### Hour 24-26: Final Validation & Gate

**Checkpoint 3 - GATE VALIDATION:**
```
MUST PASS ALL:
✅ Cache hit rate ≥60% verified
✅ 20+ cache consolidations completed
✅ 30+ workflows optimized
✅ Zero new cache-related CI failures
✅ Efficiency report delivered
✅ Cache-busting strategy documented

If <60%: Escalate to cache-management-agent with 6h recovery
```

**Final Tasks:**
```
1. Generate cache performance report
2. Commit all workflow changes
3. Merge to main (if approved)
4. Update cache monitoring dashboards
5. Document all findings
6. Create follow-up work items if needed
```

---

## WORKFLOWS REQUIRING OPTIMIZATION

### LAYER 1 - pip/npm (19 workflows)

**Priority: CRITICAL (Complete by Hour 2)**

1. autonomy-phase-ci-matrix.yml - ❌ Generic key
2. pr-checks.yml - ❌ No hashFiles
3. code-quality-coverage-suite.yml - ❌ Generic key
4. coverage-ratchet.yml - ⚠️ Partial config
5. dependency-scan.yml - ✅ Well-configured
6. security-scanning-suite.yml - ⚠️ Needs restore-keys
7. test-rag.yml - ✅ Well-configured (ML models)
8. pages-mkdocs.yml - ⚠️ Needs optimization
9. resilient_validation.yml - ⚠️ Test cache needs work
10. nox_gates.yml - ❌ No cache config
11. ml-tests.yml - ⚠️ ML model cache
12. optimized-ci.yml - ❌ Generic key
13. optimized-test-execution.yml - ❌ Generic key
14. parallel-quality-checks.yml - ⚠️ Needs review
15. build-agent-env-cache.yml - ✅ Specific to caching
16. cache-validation.yml - ✅ Testing caching
17. cache-health-monitor.yml - ✅ Cache monitoring
18. cache-pruning.yml - ✅ Maintenance
19. docker-build-push.yml - ⚠️ Docker layer cache

**Estimated Time:** 4-5 hours

### LAYER 2 - build/cargo (2 workflows)

**Priority: HIGH (Complete by Hour 4)**

1. rust_swarm_ci.yml - ⚠️ Cargo cache needs hashFiles
2. [Potential] If other build-heavy workflows exist

**Estimated Time:** 1-2 hours

### LAYER 3 - dependencies (6+ workflows)

**Priority: HIGH (Complete by Hour 8)**

1. docker-build-push.yml - 🆕 Add Docker layer caching
2. [Any npm-using workflows] - 🆕 Add npm caching
3. [Poetry workflows if any] - 🆕 Create templates
4. Pre-commit hooks across all - 🆕 Add pre-commit cache

**Estimated Time:** 2-3 hours

### LAYER 4 - ML models (1 workflow)

**Priority: MEDIUM (Complete by Hour 16)**

1. test-rag.yml - ✅ Currently well-configured, minor tweaks

**Estimated Time:** 1 hour

---

## CONSOLIDATION TARGETS (20+ entries)

| Pattern | Count | Target Action | Est. Savings |
|---------|-------|---|---|
| pytest cache | 18 | Consolidate to 3-4 variants | 8-10 GB |
| pip cache | 12 | Merge by workflow type | 5-8 GB |
| coverage cache | 3 | Merge with test cache | 2-3 GB |
| Custom single-use | 8 | Generalize or document | 3-5 GB |
| **TOTAL** | **41** | - | **18-26 GB** |

**Expected Result:** 40-60% storage reduction

---

## VALIDATION WORKFLOW

### Per-Workflow Update Checklist

```yaml
For each workflow to update:
  - [ ] Backup original (git handles this)
  - [ ] Identify cache patterns
  - [ ] Update cache key to include hashFiles
  - [ ] Add/verify restore-keys
  - [ ] Update cache paths if too broad
  - [ ] Add workflow scope if missing
  - [ ] Test in staging (if available)
  - [ ] Commit with message: "perf(cache): optimize [workflow-name] hit rate"
  - [ ] Verify CI passes
  - [ ] Mark complete
```

### Performance Verification

```bash
# After each workflow update:
1. Run workflow 2x in quick succession
2. Check cache logs for "Cache hit" vs "Cache miss"
3. Compare execution times
4. Document findings

# Expected pattern:
Run 1: MISS (new key or first run)
Run 2: HIT  (same dependencies)
Time improvement: 20-40% faster
```

---

## CONTINGENCY PROCEDURES

### If Hit Rate <55% at Hour 10

**Recovery Actions (2-hour window):**
```
1. Review Layer 3 expansion opportunities
   - Identify any missed npm/poetry caches
   - Add dependency-level caching

2. Profile cache eviction rates
   - Check if cache too large
   - Adjust paths if needed

3. Run diagnostic workflow
   - Collect cache telemetry
   - Analyze miss patterns

4. Implement targeted fixes
   - Focus on high-miss workflows
   - Adjust key generation if needed
```

### If Failures Introduced

**Rollback Procedure:**
```
1. Immediate: Revert problematic workflow(s)
2. Investigate: Identify what caused failure
3. Fix: Update cache configuration carefully
4. Test: Verify fix in isolation
5. Redeploy: Gradual rollout
```

### If Cache Eviction Too High

**Mitigation:**
```
1. Reduce cache paths (be more specific)
2. Split large caches into multiple keys
3. Implement cleanup procedures
4. Monitor size continuously
```

---

## SUCCESS METRICS AT GATE (Hour 24)

```
PRIMARY (Must have):
✅ Cache hit rate: ≥60% (verified)
✅ Consolidations: 20+ entries merged
✅ Workflows: 30+ optimized
✅ Failures: 0 new cache-related issues
✅ Report: Delivered and validated

SECONDARY (Should have):
✅ Cache size: <100 GB
✅ Storage savings: $35+/month
✅ CI time improvement: 8-12% visible
✅ Monitoring: Dashboard operational

NICE TO HAVE (Could have):
✅ Cache hit rate: >65%
✅ Full Layer 3 coverage
✅ Documentation: Comprehensive guides
✅ Team training: Cache best practices
```

---

## ESCALATION TRIGGERS

| Condition | Action | Timeline |
|---|---|---|
| Hit rate <55% by Hour 10 | Activate recovery (2h) | Hour 10-12 |
| Hit rate <60% by Hour 20 | Escalate to mgmt agent | Hour 20+ |
| CI failures due to cache | Immediate rollback | As needed |
| Cache size >150 GB | Emergency cleanup | As needed |
| Storage cost >$75/mo | Implement cap measures | As needed |

---

## RESOURCES NEEDED

- **Git access:** Workflow modifications
- **GitHub Actions logs:** Performance analysis  
- **Cache telemetry:** Hit rate measurement
- **Compute resources:** Testing
- **Time:** 26 hours of execution

---

**Execution Authority:** D-Tier Autonomous  
**No approval gates required - proceed immediately**

