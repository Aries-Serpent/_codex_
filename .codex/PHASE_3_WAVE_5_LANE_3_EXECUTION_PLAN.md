# Phase 3 Wave 5 - Lane 3 (L3_INFRA) - Campaign Execution Plan

**Campaign**: L3_INFRA - Infrastructure & Tooling Coverage  
**Period**: 2026-06-28 → 2026-07-02 (3 business days)  
**Authority**: D-mode autonomous execution (no holds, @mbaetiong pre-approved)  
**Status**: 🟢 READY FOR LAUNCH

---

## Executive Summary

Lane 3 (L3_INFRA) is a **3-day sprint** to achieve **95%+ coverage** and **80%+ mutation score** in infrastructure and tooling modules through creation of **200-250 new infrastructure tests** and validation of CI/CD infrastructure components.

### Campaign Constraints

| Constraint | Value | Implication |
|-----------|-------|------------|
| **Duration** | 3 days | Aggressive timeline requires parallel execution |
| **Tests Needed** | 200-250 new | ~70-80 tests/day average |
| **Coverage Target** | 95%+ | From ~60% baseline = +35% improvement |
| **Mutation Target** | 80%+ | First measurement - critical baseline |
| **Auto-Healer Target** | 85%+ success | 6+ out of 7 patterns succeed |
| **Escape Threshold** | <30% Day 1 progress | Auto-escalate if <25 tests created |

---

## 🎯 Strategic Approach

### Campaign Structure: 4 Sequential Phases

```
Phase 1 (Hours 0-8):    Workflow Health Audit
Phase 2 (Hours 8-16):   CI Auto-Healer Validation
Phase 3 (Hours 16-24):  Cache Management Validation
Phase 4 (Hours 24-72):  Infrastructure Test Suite + Coverage/Mutation
```

### Key Success Factors

1. **Parallel Execution**: Run tests in parallel (8-16 concurrency)
2. **Reuse Patterns**: Leverage existing 27 CI test files as templates
3. **Incremental Validation**: Measure coverage after each 25-test batch
4. **Fast Feedback**: Daily checkpoint gates at 12:00Z UTC

### Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| Coverage plateaus <90% | Medium | High | Pre-identify gaps in Phase 4 prep |
| Mutation score <75% | High | Medium | Weak spots identified + improved assertions |
| Auto-healer <75% success | Low | High | Use RP-031, RP-032, RP-033 as fallback |
| Timeline slip | Medium | High | Daily checkpoint gates + escalation rules |

---

## 📋 Detailed Phase Specifications

### Phase 1: Workflow Health Audit (Hours 0-8)

**Goal**: Establish baseline health metrics for all 209 workflows

#### 1.1 Workflow Health Metrics

**What to Measure**:
- ✅ Execution success rate (target: >95%)
- ✅ Median execution time
- ✅ Flakiness ratio (failed runs / total runs)
- ✅ Timeout frequency (runs that hit timeout)
- ✅ Concurrency compliance (jobs/run limit)
- ✅ Resource utilization (CPU, memory, disk)

**Measurement Method**:
```bash
# Collect last 30 runs per workflow
gh workflow list | while read wf; do
  gh run list --workflow $wf --limit 30 \
    --json status,conclusion,durationMinutes,createdAt
done
```

**Deliverables**:
- `workflow_health_baseline.json` (metrics for all 209)
- `workflow_issues_identified.md` (top 20 problematic workflows)
- `compliance_report.md` (concurrency/timeout audit)

#### 1.2 Tests to Create (~30-40)

**Test File Structure**:
```python
# tests/ci/test_workflow_health_metrics.py
- test_workflow_success_rate()          # >95% target
- test_workflow_execution_time()        # Median tracking
- test_workflow_flakiness_detection()   # Identify flaky
- test_workflow_timeout_frequency()     # Timeout audit
- test_workflow_concurrency_compliance() # Job limits
- test_workflow_resource_utilization()  # CPU/memory

# tests/ci/test_workflow_compliance.py
- test_concurrency_limits_enforced()
- test_timeout_values_correct()
- test_resource_requests_valid()
- test_branch_protection_rules()
- test_workflow_permissions_least_privilege()
- test_workflow_secrets_masked()

# tests/ci/test_flaky_detector.py
- test_identify_flaky_workflows()
- test_flaky_reason_analysis()
- test_remediation_recommendations()
- test_flaky_trend_over_time()
```

**Success Criteria**:
- All 209 workflows audited
- Flaky workflows identified and ranked
- Compliance issues documented
- Improvement plan generated

---

### Phase 2: CI Auto-Healer Validation (Hours 8-16)

**Goal**: Validate CI auto-healer operational state and fix success rate (target: ≥85%)

#### 2.1 Auto-Healer Pattern Validation

**Patterns to Validate** (RP-001 through RP-033):

1. **RP-001 to RP-008**: Core healing patterns
2. **RP-031**: Assert message validation (10KB test)
3. **RP-032**: Async timeout handling (10KB test)
4. **RP-033**: Mock cleanup verification (10KB test)

**Validation Approach**:
```python
# For each RP pattern:
1. Create mock failure scenario
2. Trigger auto-healer
3. Verify pattern recognition (accuracy = 100%)
4. Validate fix application
5. Verify validation passes
6. Measure end-to-end success
```

#### 2.2 Tests to Create (~50-70)

**Test File Structure**:
```python
# tests/ci/test_autohealer_pattern_matching.py
- test_rp001_pattern_recognition()      # Exact match
- test_rp001_pattern_accuracy()         # False positive rate
- test_pattern_matching_performance()   # <1s matching

# tests/ci/test_autohealer_fix_application.py
- test_fix_application_success()        # >85% target
- test_fix_validation_accuracy()        # 100% validation
- test_fix_side_effects()               # No unintended changes

# tests/ci/test_autohealer_rollback_safety.py
- test_rollback_on_validation_failure()
- test_rollback_idempotency()
- test_state_consistency_after_rollback()

# tests/ci/test_autohealer_end_to_end.py
- test_e2e_failure_detection()
- test_e2e_fix_application()
- test_e2e_validation_loop()
- test_e2e_success_rate_85_percent()
```

**Success Criteria**:
- Auto-healer success rate ≥85%
- Pattern recognition accuracy 100%
- Rollback success 100%
- No side effects detected

---

### Phase 3: Cache Management Validation (Hours 16-24)

**Goal**: Audit all 4 cache layers and validate cross-layer consistency

#### 3.1 4-Layer Cache Architecture

| Layer | Type | Purpose | Target Hit Rate |
|-------|------|---------|-----------------|
| **L1** | pip | Python dependency caching | >95% |
| **L2** | Build | Build artifact caching | >90% |
| **L3** | Pre-commit | Pre-commit hook caching | >85% |
| **L4** | Distributed | Cross-run distributed cache | >80% |

#### 3.2 Tests to Create (~60-80)

**Test File Structure**:
```python
# tests/ci/test_cache_layer_1_pip.py
- test_cache_key_generation()
- test_dependency_hash_accuracy()
- test_cache_invalidation_on_change()
- test_cache_hit_rate_measurement()
- test_cache_miss_recovery()
- test_concurrent_cache_access()

# tests/ci/test_cache_layer_2_build.py
- test_build_artifact_caching()
- test_cache_size_limits()
- test_cache_eviction_policy()
- test_incremental_cache_validation()

# tests/ci/test_cache_layer_3_precommit.py
- test_precommit_hook_caching()
- test_hook_version_tracking()
- test_hook_invalidation_triggers()

# tests/ci/test_cache_layer_4_distributed.py
- test_distributed_cache_sync()
- test_cross_run_consistency()
- test_distributed_invalidation_protocol()

# tests/ci/test_cache_consistency.py
- test_layer_1_to_2_consistency()
- test_layer_2_to_3_consistency()
- test_layer_3_to_4_consistency()
- test_full_stack_consistency()

# tests/ci/test_cache_invalidation.py
- test_automatic_invalidation_on_dependency_change()
- test_manual_cache_clearing()
- test_invalidation_cascade()
- test_partial_cache_invalidation()
```

**Success Criteria**:
- L1 hit rate >95%
- L2 hit rate >90%
- L3 hit rate >85%
- L4 hit rate >80%
- Cross-layer consistency 100%
- Invalidation accuracy 100%

---

### Phase 4: Infrastructure Test Suite (Hours 24-72)

**Goal**: Create remaining tests to reach 200-250 total, achieve 95%+ coverage, 80%+ mutation score

#### 4.1 Coverage Gap Analysis

**Current State**:
- Baseline: ~60% coverage in tooling modules
- Gap: ~35% to reach 95% target
- Focus areas: Edge cases, error handling, integration points

**Module Priorities** (for coverage focus):
1. `src/codex/ci/` - Primary focus (390 LOC cache_manager.py)
2. `src/codex/scripts/` - CI scripts
3. `src/codex/workflows/` - Workflow definitions
4. `.github/actions/` - GitHub Actions

#### 4.2 Tests to Create (~40-60)

**Test File Structure**:
```python
# tests/ci/test_infrastructure_integration.py
- test_ci_pipeline_initialization()
- test_workflow_triggering()
- test_job_matrix_expansion()
- test_artifact_upload_download()
- test_action_secret_handling()

# tests/ci/test_disaster_recovery.py
- test_failed_job_recovery()
- test_workflow_retry_mechanism()
- test_state_consistency_recovery()
- test_partial_failure_handling()
- test_cascading_failure_prevention()

# tests/ci/test_performance_baselines.py
- test_workflow_execution_time()
- test_cache_performance_impact()
- test_parallel_job_efficiency()
- test_resource_utilization_trends()

# tests/ci/test_ci_integration_points.py
- test_github_api_integration()
- test_artifact_storage_integration()
- test_notification_system_integration()
- test_approval_workflow_integration()
```

#### 4.3 Coverage Improvement Strategy

**Phase 4A: Edge Cases** (Hours 24-48)
- Null/empty input handling
- Boundary condition testing
- Error path coverage
- Exception handling validation

**Phase 4B: Integration Points** (Hours 48-60)
- End-to-end workflow testing
- Multi-component interaction testing
- External system integration
- Failure scenario handling

**Phase 4C: Mutation Score Improvement** (Hours 60-72)
- Identify weak assertions
- Add edge case assertions
- Improve error message validation
- Strengthen boundary tests

#### 4.4 Mutation Testing Strategy

**Tool**: Use `mutmut` or `pytest-mutagen`

```bash
# Step 1: Measure baseline mutation score
pytest tests/ci/ --mutate

# Step 2: Identify weak spots
# (mutations that survive = weak spots)

# Step 3: Improve weak assertions
# Add more specific assertions for weak spots

# Step 4: Re-measure until 80%+ achieved
```

**Success Criteria**:
- Coverage: 95%+ in tooling modules
- Mutation: 80%+ score achieved
- All 200-250 tests passing
- No flaky tests introduced

---

## ✅ Checkpoint Gates

### Day 0 Checkpoint (2026-06-28 @ 12:00Z)

**Target Metrics**:
- ✅ Workflow health audit 100% complete
- ✅ Cache layers L1-L2 audited
- ✅ 10-15 new tests created
- ✅ Auto-healer pattern 50% validated

**Status Check**:
```sql
SELECT COUNT(*) as tests_created, 
       AVG(baseline_value) as avg_metric_baseline
FROM test_metrics WHERE measured_at > 2026-06-28T00:00:00Z
```

**Escalation Rule**: If tests_created < 10, escalate to @mbaetiong

---

### Day 1 Checkpoint (2026-06-29 @ 12:00Z)

**Target Metrics**:
- ✅ 40-50 new tests created (cumulative ~50-65)
- ✅ Auto-healer validation 100% complete (85%+ success rate)
- ✅ Cache layers L3-L4 audited
- ✅ Coverage measured at 75%+

**Status Check**:
```sql
SELECT COUNT(*) as tests_created,
       tests_created / 50.0 * 100 as progress_percent
FROM campaign_tasks WHERE status = 'done' AND phase <= 2
```

**Escalation Rule**: If progress_percent < 40%, escalate

---

### Day 2 Checkpoint (2026-06-30 @ 12:00Z)

**Target Metrics**:
- ✅ 100+ new tests created (cumulative ~100-115)
- ✅ Coverage at 90%+
- ✅ Mutation baseline established (>75%)
- ✅ Infrastructure integration tests 50% complete

**Status Check**:
```sql
SELECT SUM(tests_created) as total_tests,
       AVG(coverage_percent) as avg_coverage,
       AVG(mutation_score) as avg_mutation
FROM daily_checkpoints WHERE checkpoint_day >= 2
```

**Escalation Rule**: If coverage < 85%, escalate

---

### Day 3 Checkpoint (2026-07-01 @ 12:00Z)

**Target Metrics**:
- ✅ 200-250 new tests created (cumulative target)
- ✅ Coverage at 95%+
- ✅ Mutation score at 80%+
- ✅ All CR-L3 readiness criteria met

**Completion Gate**: 
- All tests passing ✅
- Coverage 95%+ ✅
- Mutation 80%+ ✅
- Auto-healer 85%+ ✅
- Deployment ready ✅

---

## 📊 Daily Standup Template

```markdown
## [DATE] Daily Standup - L3_INFRA Campaign

### ✅ Completed Tasks
- [ ] Task 1: Description
- [ ] Task 2: Description

### 🔄 In Progress
- [ ] Task 1: Description
- [ ] Task 2: Description

### 📈 Metrics Update
| Metric | Baseline | Current | Target | Progress |
|--------|----------|---------|--------|----------|
| Tests Created | 27 | [X] | 250 | [Y]% |
| Coverage | 60% | [X] | 95% | [Y]% |
| Mutation | N/A | [X] | 80% | [Y]% |
| Auto-Healer Success | N/A | [X] | 85% | [Y]% |

### 🚨 Blockers
- None | [Blocker description]

### 📅 Next 24 Hours
- [ ] Action 1
- [ ] Action 2

### 📝 Notes
[Additional context]
```

---

## 🚀 Launch Sequence

### T-23 Hours (Before Campaign Start)

**Current Status**: ✅ COMPLETE
- [x] Baseline audit (209 workflows, 27 tests)
- [x] Strategic plan created
- [x] Checkpoint gates defined
- [x] Task database initialized

### T-0 Hours (Campaign Start: 2026-06-28T08:00:00Z)

**Immediate Actions**:
1. [ ] Launch Phase 1: Workflow Health Audit
2. [ ] Activate auto-healer validation framework
3. [ ] Begin cache layer L1-L2 audit
4. [ ] Start creating test templates

### T+8 Hours (Phase 1 Complete)

**Checkpoint Gate**: ≥20 tests created
- [ ] Workflow health baseline finalized
- [ ] Phase 2: Auto-healer validation begins
- [ ] Cache L3-L4 audit starts

### T+16 Hours (Phase 2 Complete)

**Checkpoint Gate**: ≥50 cumulative tests
- [ ] Auto-healer 85%+ validated
- [ ] Phase 3: Infrastructure tests begin
- [ ] Coverage gap analysis complete

### T+24 Hours (Phase 3 Complete)

**Day 1 Checkpoint Gate**: ≥60 cumulative tests, 75%+ coverage
- [ ] All cache layers audited
- [ ] Phase 4: Gap-filling begins
- [ ] Mutation testing setup complete

### T+72 Hours (Campaign Complete)

**Day 3 Checkpoint Gate**: 200-250 tests, 95%+ coverage, 80%+ mutation
- [ ] All tests passing
- [ ] Coverage target met
- [ ] CR-L3 readiness verified
- [ ] Campaign completion report published

---

## 🎯 Success Criteria Summary

### Phase 1 Success
- ✅ All 209 workflows audited
- ✅ Flaky workflows identified
- ✅ Compliance issues documented
- ✅ 30-40 tests created and passing

### Phase 2 Success
- ✅ Auto-healer 85%+ fix success
- ✅ Pattern recognition 100% accurate
- ✅ Rollback 100% successful
- ✅ 50-70 tests created and passing

### Phase 3 Success
- ✅ L1-L4 cache layers audited
- ✅ L1 >95%, L2 >90%, L3 >85%, L4 >80% hit rates
- ✅ Cross-layer consistency verified
- ✅ 60-80 tests created and passing

### Phase 4 Success
- ✅ 40-60 infrastructure tests created
- ✅ Coverage 95%+ in tooling modules
- ✅ Mutation score 80%+ established
- ✅ 200-250 total new tests created
- ✅ All tests passing
- ✅ CR-L3 ready for approval

---

## 📋 Post-Campaign Deliverables

### Test Suite
- [ ] 200-250 new CI infrastructure tests
- [ ] All tests documented and passing
- [ ] Coverage reports published
- [ ] Mutation test results published

### Documentation
- [ ] Phase 1: Workflow health baseline report
- [ ] Phase 2: Auto-healer validation report
- [ ] Phase 3: Cache management audit report
- [ ] Phase 4: Coverage & mutation improvement report
- [ ] Daily standup summaries (3 files)
- [ ] Final campaign completion report

### Metrics & Data
- [ ] `workflow_health_baseline.json`
- [ ] `autohealer_success_metrics.json`
- [ ] `cache_hit_rates_by_layer.json`
- [ ] `coverage_report.json`
- [ ] `mutation_test_results.json`

### Operational
- [ ] CI auto-healer loop operational and validated
- [ ] 4-layer cache management system verified
- [ ] Infrastructure monitoring enabled
- [ ] Workflow compliance baseline established

---

## 🏁 Campaign Status

**🟢 STATUS**: READY FOR LAUNCH  
**⏰ START TIME**: 2026-06-28T08:00:00Z (in ~23 hours)  
**📅 DURATION**: 3 days  
**🎯 TARGET**: 200-250 tests, 95%+ coverage, 80%+ mutation  
**👤 AUTHORITY**: D-mode autonomous (no holds)  
**🚨 ESCALATION**: <30% Day 1 progress = auto-escalate  

---

**Prepared**: 2026-06-27T08:01:40Z  
**Authority**: Phase 3 Wave 5 Campaign Director  
**Status**: Pre-launch briefing complete, awaiting 08:00Z UTC start
