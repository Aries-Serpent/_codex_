---
name: Cache Manager Integration Agent
description: Integrate and coordinate cache management operations across repository systems
deprecated: true
superseded_by: cache-management-agent.md
runner_compatibility:
  default: ubuntu-latest        # 2-core — cache management operations coordination across repo systems
  large:   ubuntu-latest-large  # 4-core — enhanced parallelism
---

> ⚠️ **DEPRECATED** — Integration capabilities have been folded into
> **[Cache Management Agent](cache-management-agent.md)** as a sub-capability.
> Use `cache-management-agent` for all new invocations. Tracked under
> Phase-5 agent consolidation matrix (`agents/AGENT_CONSOLIDATION_MATRIX.md`).

# Cache Manager Workflow Integration Agent

**Agent Name**: cache-manager-integration  
**Category**: CI/CD & Performance  
**Status**: ✅ Active  
**Created**: 2026-02-12 (PS-14 Implementation)  
**Version**: 1.0.0

---

## Purpose

Integrates and optimizes CacheManager (`src/codex/ci/cache_manager.py`) across GitHub Actions workflows, ensuring consistent cache key generation, health monitoring, and cross-workflow coordination.

---

## Scope

### Primary Responsibilities

1. **Workflow Integration**
   - Implement CacheManager in documented workflows (5/42 target)
   - Generate standardized cache keys
   - Configure multi-level restore keys

2. **Cache Health Monitoring**
   - Track cache size, age, hit rates
   - Identify unused or stale caches
   - Generate health reports and recommendations

3. **Performance Optimization**
   - Measure cache hit rate improvements
   - Identify redundant downloads
   - Optimize cache coordination across jobs

4. **Documentation & Patterns**
   - Maintain integration patterns in `.codex/CACHE_MANAGER_WORKFLOW_INTEGRATION.md`
   - Update workflows with CacheManager usage
   - Track adoption rate (0/42 → target 5/42 → 100%)

---

## Target Workflows (Phase 2)

| Workflow | Priority | Cache Type | Status |
|----------|----------|------------|--------|
| pr-checks.yml | High | UV, PIP | 📋 Documented |
| test-rag.yml | High | HuggingFace, Transformers | 📋 Documented |
| code-quality-coverage-suite.yml | High | PIP, MYPY, PYTEST, PRE_COMMIT | 📋 Documented |
| pages-mkdocs.yml | Medium | PIP | 📋 Documented |
| rust_swarm_ci.yml | Medium | CARGO | 📋 Documented |

**Adoption Rate**: 0/42 (0%) → Target: 5/42 (12%) → Goal: 42/42 (100%)

---

## Integration Pattern

### Before (Manual Cache Keys)
```yaml
- name: Cache dependencies
  uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: pip-${{ runner.os }}-${{ hashFiles('requirements*.txt') }}
    restore-keys: |
      pip-${{ runner.os }}-
```

### After (CacheManager Integration)
```yaml
- name: Generate cache configuration
  id: cache-config
  run: |
    python -c "
    from codex.ci.cache_manager import CacheManager, CacheType
    manager = CacheManager()
    config = manager.create_cache_config(
      cache_type=CacheType.PIP,
      workflow_name='pr-checks',
      extra_identifiers={'job': 'test'}
    )
    print(f'key={config.key_components[0]}')
    print(f'restore-keys={chr(10).join(config.restore_keys)}')
    print(f'path={chr(10).join(config.paths)}')
    " >> $GITHUB_OUTPUT

- name: Cache dependencies
  uses: actions/cache@v4
  with:
    path: ${{ steps.cache-config.outputs.path }}
    key: ${{ steps.cache-config.outputs.key }}
    restore-keys: ${{ steps.cache-config.outputs.restore-keys }}
```

---

## Tools & Integration Points

### Data Sources

1. **CacheManager Module**
   - File: `src/codex/ci/cache_manager.py`
   - Classes: `CacheManager`, `CacheType`, `CacheConfig`, `CacheHealth`
   - Tests: `tests/ci/test_cache_manager.py`

2. **Integration Documentation**
   - File: `.codex/CACHE_MANAGER_WORKFLOW_INTEGRATION.md`
   - Content: Patterns, examples, success criteria

3. **GitHub Actions Workflows**
   - Directory: `.github/workflows/`
   - Count: 64 total, 42 active (target 5 for Phase 2)

### GitHub Tools Available

- `view` - Read workflow files and CacheManager code
- `edit` - Update workflows with CacheManager integration
- `grep` - Find workflows using actions/cache
- `glob` - Locate workflow files by pattern
- `bash` - Test CacheManager functionality

---

## Activation Commands

```markdown
@copilot Use the Cache Manager Integration Agent to implement CacheManager in pr-checks.yml

@copilot Use the Cache Manager Integration Agent to validate cache health across all workflows

@copilot Use the Cache Manager Integration Agent to measure cache hit rate improvements after integration

@copilot Use the Cache Manager Integration Agent to generate adoption progress report
```

---

## Typical Workflows

### Workflow 1: Single Workflow Integration

**Steps**:
1. Read target workflow file (e.g., `.github/workflows/pr-checks.yml`)
2. Identify existing `actions/cache` usage
3. Generate CacheManager integration code
4. Update workflow with new pattern
5. Test locally (if possible) or document testing plan
6. Commit changes with descriptive message

**Success Criteria**:
- Workflow updated with CacheManager
- Cache keys generated consistently
- Restore keys configured (multi-level fallback)
- No workflow syntax errors

### Workflow 2: Cache Health Report

**Steps**:
1. Use `gh cache list` to enumerate all caches
2. Parse cache metadata (size, age, last accessed)
3. Run `CacheManager().validate_cache_health()`
4. Generate health report with recommendations
5. Update `.codex/cache_health_report.md`

**Output Example**:
```markdown
## Cache Health Report - 2026-02-12

**Overall Health**: 🟢 GOOD

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Total Size | 4.2 GB | <8 GB | ✓ OK |
| Total Caches | 127 | - | Info |
| Oldest Cache | 12 days | <30 days | ✓ OK |
| Unused Caches | 3 | <10 | ✓ OK |

**Recommendations**:
1. Clean up 3 unused caches (save 180 MB)
2. pr-checks cache hit rate: 67% (target: 80%)
```

### Workflow 3: Adoption Progress Tracking

**Steps**:
1. Count workflows using CacheManager (grep for `CacheManager`)
2. Count total active workflows
3. Calculate adoption rate (integrated / total)
4. Compare vs. target (5/42 = 12%)
5. Identify next workflows to integrate

**Output Example**:
```markdown
## CacheManager Adoption Progress - 2026-02-12

**Adoption Rate**: 2/42 (4.8%) → Target: 5/42 (12%)

**Integrated Workflows**:
- ✅ pr-checks.yml (UV, PIP cache)
- ✅ test-rag.yml (HuggingFace cache)

**Next Targets** (Priority Order):
1. code-quality-coverage-suite.yml (High Priority)
2. pages-mkdocs.yml (Medium Priority)
3. rust_swarm_ci.yml (Medium Priority)

**Timeline**: 6-8 hours to reach 12% adoption
```

---

## Success Criteria

### Integration Effectiveness

- **Adoption Rate**: 5/42 (12%) by end of Phase 2
- **Cache Hit Rate**: +15% improvement on integrated workflows
- **Key Consistency**: 100% of integrated workflows use standardized keys
- **Error Rate**: <1% workflow failures due to CacheManager

### Performance Impact

- **Build Time**: -10% average reduction (via improved cache hits)
- **Download Traffic**: -20% reduction (fewer redundant downloads)
- **Cache Size**: Stable or decreasing (better efficiency)

---

## Escalation Protocol

### Level 1: Integration Issue

**Trigger**: CacheManager integration causes workflow failure

**Action**:
1. Revert workflow to previous version
2. Analyze error logs
3. Fix CacheManager code or integration pattern
4. Re-test before re-deploying

### Level 2: Performance Degradation

**Trigger**: Cache hit rate decreases after integration

**Action**:
1. Compare cache keys (before vs. after)
2. Check for key instability (hash changes)
3. Adjust CacheManager key generation
4. Monitor for 24h before escalating

### Level 3: Critical Failure

**Trigger**: Multiple workflows fail simultaneously

**Action**:
1. Disable CacheManager in all workflows (rollback)
2. Escalate to @mbaetiong
3. Root cause analysis (emergency session)
4. Comprehensive testing before re-enabling

---

## Configuration

```yaml
cache_manager_config:
  phase2_target_workflows: 5
  phase3_target_workflows: 42
  cache_hit_rate_target: 0.80  # 80%
  cache_health_thresholds:
    size_gb: 8.0
    age_days: 30
  monitoring_interval: weekly
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-12 | Initial agent specification (PS-14) |

---

**Agent Status**: ✅ ACTIVE  
**Documentation**: COMPLETE  
**Integration**: PHASE 1 (Documentation) COMPLETE  
**Next Phase**: Phase 2 (Implementation, 5 workflows)
