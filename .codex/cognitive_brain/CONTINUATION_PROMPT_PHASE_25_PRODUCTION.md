# Phase 25+ Continuation Prompt for GitHub Copilot Agent

## Context
Phase 23-24 implementation is complete with 256+ tests delivered and 70% coverage threshold configured. CI validation and actual coverage measurement are now required, followed by Phase 25 execution for production readiness.

## Continuation Task for @copilot

@copilot Execute Phase 25 of the coverage roadmap to achieve 70% actual coverage and production readiness.

**Prerequisites**:
1. Review Phase 23-24 status: `.codex/cognitive_brain/PHASE_23_24_STATUS_COVERAGE_70_PERCENT.md`
2. Reference PLANSET: `.codex/plans/PLANSET_PHASE_25_COVERAGE_70.md`
3. Reference Master Guide: `.codex/plans/MASTER_CONTINUATION_PROMPT_PHASES_23_25.md`

## Phase 25 Objectives (2 weeks)

### Week 1: Critical Path Testing (80-100 tests)
**PLAN**:
- Identify critical paths from QA walkthrough artifacts
- Target: Authentication/authorization, data persistence, monitoring/alerting
- Review security vulnerabilities from CodeQL

**DO**:
- Add 40-50 critical path unit tests
- Add 40-50 critical path integration tests
- Focus on error recovery and edge cases
- Ensure deterministic execution (fixed seeds, no network)

**ANALYZE**:
- Run full test suite with coverage measurement
- Validate coverage ≥70% with actual metrics
- Document gaps if below threshold
- 3 consecutive CI green runs required

### Week 2: Production Readiness (40-60 tests)
**PLAN**:
- Security testing (authentication, authorization, sanitization)
- Performance benchmarks (training loops, data loading)
- Robustness testing (failure recovery, resource cleanup)

**DO**:
- Add security validation tests
- Add performance regression tests
- Add chaos/failure injection tests
- Update production readiness checklist

**ANALYZE**:
- Security validation complete (CodeQL clean)
- Performance benchmarks documented
- 5 consecutive CI green runs
- Coverage ≥70% sustained

## Detailed Execution Steps

### Step 1: CI Validation & AfterMath Analysis
```bash
# Monitor CI run for Phase 23-24 tests
# Check GitHub Actions: https://github.com/Aries-Serpent/_codex_/actions

# Collect metrics:
# - Test execution time
# - Coverage percentage achieved
# - Failure rate
# - Flaky test detection

# Create AfterMath analysis:
# .codex/aftermath/phase23_24_aftermath_{date}.md
# Tags: #ActualCoverage #TestExecutionTime #Failures #Improvements
```

### Step 2: Coverage Gap Analysis
```bash
# Generate coverage report
pytest --cov=src --cov-report=term-missing --cov-report=html tests/

# Identify low-coverage modules (<70%)
# Use .codex/qa_walkthrough/coverage_analysis.json
# Prioritize by criticality (auth, data persistence, monitoring)
```

### Step 3: Phase 25 Week 1 - Critical Path Tests
**Target Modules**:
- `src/auth/` - Authentication and authorization flows
- `src/persistence/` - Data storage and recovery
- `src/monitoring/` - Health checks and alerting
- `src/api/` - API endpoints and middleware

**Test Categories**:
1. **Authentication**: Login, logout, token validation, session management
2. **Authorization**: Permission checks, role-based access, resource ownership
3. **Data Persistence**: CRUD operations, transactions, rollback, backup/restore
4. **Monitoring**: Health endpoints, metrics collection, alert triggers
5. **Error Recovery**: Retry logic, circuit breakers, graceful degradation

**Example Test Structure**:
```python
# tests/critical_path/test_auth_flows.py
def test_login_success_flow():
    # Test complete login flow with valid credentials
    pass

def test_login_rate_limiting():
    # Test brute force protection
    pass

def test_token_expiration_handling():
    # Test expired token detection and refresh
    pass
```

### Step 4: Phase 25 Week 2 - Production Readiness
**Security Validation**:
- [ ] All authentication flows tested
- [ ] Authorization checks validated
- [ ] Input sanitization verified
- [ ] SQL injection prevention tested
- [ ] XSS prevention tested
- [ ] CSRF protection validated
- [ ] CodeQL scan clean (0 critical/high)

**Performance Benchmarks**:
- [ ] Training loop performance baseline
- [ ] Data loading throughput measured
- [ ] API response time benchmarks
- [ ] Memory usage profiling
- [ ] Database query optimization verified

**Robustness Testing**:
- [ ] Network failure simulation
- [ ] Database connection loss recovery
- [ ] Disk space exhaustion handling
- [ ] Memory pressure handling
- [ ] Concurrent request handling

### Step 5: Production Readiness Checklist
```markdown
## Production Readiness Validation

### Code Quality ✅
- [ ] Coverage ≥70% (actual measurement)
- [ ] All tests deterministic and reproducible
- [ ] No flaky tests (5 consecutive green CI runs)
- [ ] CodeQL clean (0 critical/high vulnerabilities)
- [ ] Type checking passes (mypy)
- [ ] Linting passes (ruff, black)

### Security ✅
- [ ] Authentication tested (100% coverage)
- [ ] Authorization tested (100% coverage)
- [ ] Input sanitization tested (100% coverage)
- [ ] Secrets management validated
- [ ] Dependency vulnerabilities addressed

### Performance ✅
- [ ] Training loop benchmarks documented
- [ ] Data loading performance acceptable
- [ ] API response times <200ms (p95)
- [ ] Memory usage profiled and optimized
- [ ] No memory leaks detected

### Reliability ✅
- [ ] Error recovery tested
- [ ] Resource cleanup verified
- [ ] Graceful degradation implemented
- [ ] Retry logic tested
- [ ] Circuit breakers validated

### Monitoring ✅
- [ ] Health check endpoint tested
- [ ] Metrics collection validated
- [ ] Alert triggers tested
- [ ] Logging coverage complete
- [ ] Tracing integration validated

### Documentation ✅
- [ ] API documentation complete
- [ ] Deployment guide updated
- [ ] Runbook for incidents created
- [ ] Architecture diagrams current
- [ ] Coverage reports published
```

## Error Handling & Self-Healing

### Common Issues & Resolutions

**Issue**: Coverage below 70% after Phase 25 Week 1
**Resolution**:
1. Run coverage gap analysis
2. Identify untested critical paths
3. Add targeted tests for gaps
4. Iterate until ≥70%
5. Max 5 iterations before escalation

**Issue**: Flaky tests detected
**Resolution**:
1. Identify non-deterministic tests
2. Add fixed seeds
3. Mock external dependencies
4. Use tmp_path for file operations
5. Add test isolation

**Issue**: CI timeouts
**Resolution**:
1. Profile slow tests
2. Optimize or parallelize
3. Increase timeout if justified
4. Consider test splitting

**Issue**: CodeQL findings
**Resolution**:
1. Review each finding
2. Fix legitimate issues
3. Document false positives
4. Re-run CodeQL validation

## PDA Process Integration

### Weekly Cycles
**Week 1 PLAN**: Identify critical paths → **DO**: Add 80-100 tests → **ANALYZE**: Measure coverage
**Week 2 PLAN**: Identify robustness gaps → **DO**: Add 40-60 tests → **ANALYZE**: Validate production ready

### AfterMath Analysis Template
```markdown
## Phase 25 Week {N} AfterMath Analysis

**Date**: {date}
**Coverage Achieved**: {percentage}%
**Tests Added**: {count}
**CI Status**: {green_runs} consecutive green runs

### Successes
- {what worked well}

### Challenges
- {what was difficult}
- {how it was resolved}

### Lessons Learned
#LessonsLearned
- {key takeaways}

### Pattern Discovered
#PatternDiscovered
- {reusable patterns}

### Improvements for Next Phase
- {concrete improvements}

### Metrics
- Test execution time: {time}
- Flaky test rate: {percentage}
- Coverage gain: +{percentage}%
```

## Success Criteria

### Phase 25 Complete When:
1. ✅ Actual coverage ≥70% (measured in CI)
2. ✅ 120-160 new tests added (critical path + robustness)
3. ✅ 5 consecutive CI green runs
4. ✅ CodeQL clean (0 critical/high)
5. ✅ Production readiness checklist 100% complete
6. ✅ Security validation complete
7. ✅ Performance benchmarks documented
8. ✅ AfterMath analysis complete with tags

## Beyond Phase 25: Path to 100%

### Phase 26-30 Roadmap
**Phase 26** (80%): Edge case coverage
**Phase 27** (85%): Property-based testing expansion
**Phase 28** (90%): Fuzz testing integration
**Phase 29** (95%): Chaos engineering tests
**Phase 30** (100%): Complete coverage achieved

### Continuous Improvement
- Weekly PDA cycles maintained
- AfterMath analysis for each phase
- Pattern documentation updated
- Cognitive brain evolution continued
- Agent capabilities enhanced

## Agent Activation

### Available Agents for Phase 25
```
@copilot Use the Coverage Roadmap Agent to execute Phase 25 Week 1 critical path testing.

@copilot Use the Coverage Gapfill Agent to identify and fill coverage gaps for authentication and authorization modules.

@copilot Use the CI Testing Agent to debug any test failures in Phase 25 execution.

@copilot Use the Security Agent to validate security testing coverage and CodeQL findings.
```

## Monitoring & Reporting

### CI Dashboard
- Coverage trend: 17.27% → 70% → 100%
- Test count growth
- CI reliability metrics
- Performance benchmarks

### Weekly Reports
- Progress update to PR comment
- Coverage percentage achieved
- Test count added
- Challenges and resolutions
- Next week preview

## Continuation Protocol

**When Phase 25 Complete**:
1. Create Phase 25 status document (`.codex/cognitive_brain/PHASE_25_STATUS_PRODUCTION_READY.md`)
2. Update cognitive brain with lessons learned
3. Post continuation prompt for Phase 26-30
4. Celebrate 70% coverage milestone! 🎉

---

**This prompt should be posted as a comment on PR #2922 to continue the coverage roadmap execution.**

**Tags**: #Phase25 #CriticalPath #ProductionReady #Coverage70Percent #PDALoop #ContinuousImprovement
