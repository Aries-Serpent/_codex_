# Coverage Threshold Roadmap

**Created**: 2026-01-20  
**Owner**: @mbaetiong  
**Status**: Active  
**Single Source of Truth**: `pyproject.toml` → `[tool.coverage.report]` → `fail_under`

---

## Overview

This document provides the roadmap for incrementally raising test coverage thresholds from 0% to 100%. The approach uses gradual increases to ensure sustainable progress without blocking development.

---

## Current State

**As of Phase 21 (2026-01-20)**:
- **Coverage Threshold**: 0% (permissive during CI/CD migration)
- **Actual Coverage**: ~17.27% (180/1,042 modules tested)
- **Configuration**: pyproject.toml is now single source of truth
- **Removed Conflicts**: Eliminated conflicting settings in .coveragerc and pytest.ini

---

## Single Source of Truth

### Configuration Hierarchy ✅

**Primary**: `pyproject.toml`
```toml
[tool.coverage.report]
fail_under = 0  # <-- THIS IS THE AUTHORITATIVE THRESHOLD
```

**Defers to Primary**: `.coveragerc`
```ini
[report]
# fail_under removed - use pyproject.toml
```

**Defers to Primary**: `pytest.ini`
```ini
[pytest]
addopts = 
    # --cov-fail-under removed - use pyproject.toml
```

---

## Incremental Raise Schedule

### Phase 23: Raise to 30% Coverage
**Target Date**: 2026-02-15  
**Duration**: 3-4 weeks from Phase 21 completion  
**Status**: 🔄 NOT STARTED

#### Prerequisites
- [ ] Phase 21 CI/CD hardening complete
- [ ] Phase 22 Objective 1 (secrets audit) complete
- [ ] Current coverage validated at ~17-20%
- [ ] Test infrastructure stable (no xdist crashes)

#### Tasks
1. **Write Tests for High-Priority Modules** (Week 1-2)
   - Target: 61 high-priority modules from test_priority_matrix.json
   - Focus: CLI modules, training logic, data loaders
   - Add ~250-300 new tests

2. **Measure Progress** (Week 2)
   - Run coverage analysis
   - Validate coverage ≥30%
   - Identify gaps

3. **Raise Threshold** (Week 3)
   - Update `pyproject.toml`: `fail_under = 30`
   - Commit change
   - Monitor CI for 3 successful runs

4. **Documentation** (Week 3)
   - Update this roadmap with actual date
   - Document modules covered
   - Update QA walkthrough files

#### Success Criteria
- [ ] Coverage ≥30% measured via pytest-cov
- [ ] CI passes with fail_under=30
- [ ] No flaky tests introduced
- [ ] Documentation updated

---

### Phase 24: Raise to 50% Coverage
**Target Date**: 2026-03-01  
**Duration**: 2 weeks from Phase 23 completion  
**Status**: 🔄 NOT STARTED

#### Prerequisites
- [ ] Phase 23 complete (30% threshold active)
- [ ] No major test failures in Phase 23
- [ ] Coverage infrastructure proven stable

#### Tasks
1. **Add Integration Tests** (Week 1)
   - Focus: Cross-module interactions
   - Add ~200 integration tests
   - Target medium-priority modules

2. **Raise Threshold** (Week 2)
   - Update `pyproject.toml`: `fail_under = 50`
   - Validate with 3 CI runs
   - Update documentation

#### Success Criteria
- [ ] Coverage ≥50%
- [ ] CI stable with new threshold
- [ ] Integration test suite established

---

### Phase 25: Raise to 70% Coverage
**Target Date**: 2026-03-15  
**Duration**: 2 weeks from Phase 24 completion  
**Status**: 🔄 NOT STARTED

#### Prerequisites
- [ ] Phase 24 complete (50% threshold active)
- [ ] Coverage at or above 50%
- [ ] Test maintenance workload sustainable

#### Tasks
1. **Add End-to-End Tests** (Week 1)
   - Focus: Critical workflows
   - Add ~150 E2E tests
   - Cover remaining medium/low priority modules

2. **Raise Threshold** (Week 2)
   - Update `pyproject.toml`: `fail_under = 70`
   - Validate with 5 CI runs
   - Celebrate milestone 🎉

#### Success Criteria
- [ ] Coverage ≥70% (matches original pyproject.toml target!)
- [ ] CI passing consistently
- [ ] E2E test suite operational

---

### Phase 26+: Aspire to 100% Coverage
**Target Date**: 2026-04-01 (aspirational)  
**Duration**: Ongoing  
**Status**: 🔄 NOT STARTED

#### Prerequisites
- [ ] Phase 25 complete (70% threshold active)
- [ ] Team consensus on 100% goal
- [ ] Realistic assessment of diminishing returns

#### Approach
- **Incremental Raises**: 70% → 80% → 90% → 95% → 100%
- **Each Step**: 1-2 weeks
- **Focus**: Edge cases, error handling, documentation examples
- **Reality Check**: 100% may not be achievable/valuable for all code

#### Success Criteria (Phase by Phase)
- [ ] 80% coverage (85% including partial)
- [ ] 90% coverage (focus on core modules)
- [ ] 95% coverage (near-complete)
- [ ] 100% coverage (aspirational - exclude if: generated code, platform-specific, deprecated)

---

## Testing Strategy by Phase

### Phase 23 (→30%): Unit Tests
**Focus**: Individual functions and classes
- CLI command handlers
- Training algorithms
- Data loading/preprocessing
- Configuration management

**Approach**:
- Use pytest + hypothesis for property testing
- Mock external dependencies
- Test happy path + error handling

---

### Phase 24 (→50%): Integration Tests
**Focus**: Module interactions
- Pipeline workflows
- Database operations
- API integrations
- Service-to-service calls

**Approach**:
- Use test fixtures for common setups
- Create test databases/mock services
- Validate cross-module contracts

---

### Phase 25 (→70%): End-to-End Tests
**Focus**: Complete user workflows
- CLI workflows (train → evaluate → deploy)
- API workflows (auth → request → response)
- RAG pipelines (index → query → retrieve)

**Approach**:
- Use real or near-real test data
- Validate complete execution paths
- Measure performance/latency

---

### Phase 26+ (→100%): Edge Cases & Robustness
**Focus**: Rare scenarios and failure modes
- Error recovery
- Boundary conditions
- Concurrent access
- Platform-specific behavior

**Approach**:
- Chaos engineering principles
- Fuzzing for input validation
- Stress testing for scalability

---

## Monitoring & Metrics

### Coverage Dashboard (Planned for Phase 23)
**Tool**: GitHub Actions workflow + artifact storage  
**Metrics**:
- Overall coverage percentage (trend over time)
- Per-module coverage (heatmap)
- Coverage delta per PR (require +0.5% or maintain)
- Untested lines (prioritized by module criticality)

### Quality Gates
**PR Requirements**:
- Coverage must meet current threshold
- No decrease in coverage vs. base branch
- New code must have ≥80% coverage (eventually)

**CI Enforcement**:
- pytest-cov --cov-fail-under enforces threshold
- Coverage reports uploaded to Codecov
- PR comments show coverage impact

---

## Risk Management

### Risk 1: Threshold Too Aggressive
**Symptom**: Frequent CI failures due to coverage dips  
**Mitigation**:
- Pause threshold raises if CI failure rate >10%
- Review and adjust schedule
- Focus on test quality over quantity

### Risk 2: Test Quality Degradation
**Symptom**: High coverage but tests don't catch bugs  
**Mitigation**:
- Code review for test meaningfulness
- Require assertions (not just imports)
- Use mutation testing (mutmut) to validate test effectiveness

### Risk 3: Developer Productivity Impact
**Symptom**: PRs delayed waiting for tests  
**Mitigation**:
- Provide test templates and examples
- Allow temporary threshold waivers (with issue tracking)
- Balance velocity vs. quality

### Risk 4: Diminishing Returns at High Coverage
**Symptom**: 95%+ coverage requires disproportionate effort  
**Mitigation**:
- Exclude generated code, deprecated modules
- Accept 95% as "effective 100%"
- Focus effort on critical paths

---

## Rollback Procedure

If a threshold raise causes sustained issues:

1. **Immediate**: Lower threshold by 10% (emergency fix)
   ```bash
   # Edit pyproject.toml
   fail_under = 40  # if 50% was causing issues
   ```

2. **Within 24 hours**: Create issue documenting rollback reason

3. **Within 1 week**: Address root cause (flaky tests, xdist issues, etc.)

4. **Re-attempt**: After stabilization period (1-2 weeks)

---

## Success Metrics

### Phase 23 Success
- ✅ Coverage ≥30%
- ✅ CI green for 7 consecutive days
- ✅ No test flakiness reported
- ✅ Developer satisfaction survey >80% positive

### Phase 24 Success
- ✅ Coverage ≥50%
- ✅ Integration test suite (200+ tests)
- ✅ CI green for 14 consecutive days
- ✅ PR cycle time <2 days (tests don't block)

### Phase 25 Success
- ✅ Coverage ≥70%
- ✅ E2E test suite (150+ tests)
- ✅ CI green for 30 consecutive days
- ✅ Zero coverage-related rollbacks

### Phase 26+ Success
- ✅ Coverage ≥100% (or documented exclusions)
- ✅ Mutation testing score >80%
- ✅ Zero critical bugs escaping to production
- ✅ Test suite maintainable (<10% annual growth)

---

## References

- Current Coverage Analysis: `.codex/qa_walkthrough/coverage_analysis.json`
- Test Priority Matrix: `.codex/qa_walkthrough/test_priority_matrix.json`
- Configuration: `pyproject.toml` (single source of truth)
- Phase 21 Status: `.codex/cognitive_brain/PHASE_21_STATUS_CICD_HARDENING.md`

---

## Change Log

| Date | Change | Coverage | Author |
|------|--------|----------|--------|
| 2026-01-20 | Created roadmap with incremental schedule | 0% → 17.27% (actual) | @copilot |
| 2026-01-20 | Established pyproject.toml as single source of truth | 0% (threshold) | @copilot |
| TBD | Phase 23: Raise to 30% | 30% | TBD |
| TBD | Phase 24: Raise to 50% | 50% | TBD |
| TBD | Phase 25: Raise to 70% | 70% | TBD |
| TBD | Phase 26+: Aspire to 100% | 100% | TBD |

---

**Next Review**: After Phase 23 completion  
**Owner**: @mbaetiong  
**Status**: Active ✅
