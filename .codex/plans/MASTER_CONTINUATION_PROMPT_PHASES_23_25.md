# GitHub Copilot Agent Master Continuation Prompt: Phases 23-25 Execution

**Generated**: 2026-01-20  
**Purpose**: Complete autonomous execution guidance for coverage roadmap Phases 23-25  
**Target**: Achieve 70% production-ready test coverage  
**Owner**: GitHub Copilot Agents  
**Status**: ✅ READY FOR EXECUTION

---

## 🎯 Executive Summary

This document provides the master continuation prompt for GitHub Copilot Agents to autonomously execute Phases 23-25 of the coverage threshold roadmap, achieving the production-ready milestone of 70% test coverage.

---

## 📋 MASTER PROMPTSET

### Phase 23 Activation Prompt

```markdown
@copilot Execute Phase 23 of the coverage roadmap to raise coverage from 17.27% to 30%.

**PLANSET**: `.codex/plans/PLANSET_PHASE_23_COVERAGE_30.md`

**Context**:
- Current coverage: 17.27% (180/1,042 modules tested)
- Target: 30% coverage threshold
- Timeline: 3-4 weeks
- Agent: Coverage Roadmap Agent

**Prerequisites**:
- Phase 21 CI/CD hardening complete ✅
- Phase 22 Objectives 1 & 2 complete ✅
- Secrets audit complete ✅
- Coverage threshold standardized ✅

**Execution Approach**:
1. Follow PDA (Plan → Do → Analyze) process weekly
2. Week 1: Add 120-150 unit tests for high-priority modules
3. Week 2: Add 100-120 integration tests and gap-filling
4. Week 3: Final push and raise threshold to 30%

**Key Deliverables**:
- 250-300 unit tests across CLI, training, data loading modules
- 100-120 integration tests for module interactions
- AfterMath analysis after each week
- pyproject.toml updated to fail_under=30

**Success Criteria**:
- Coverage ≥30% validated by pytest-cov
- CI passing for 3 consecutive runs
- Zero critical test failures
- AfterMath analysis complete

**Error Handling**:
- Comprehensive error scenarios in PLANSET
- Rollback procedure documented
- Self-healing iterations (up to 5 attempts)

**References**:
- Coverage Roadmap: `.codex/plans/COVERAGE_THRESHOLD_ROADMAP.md`
- Test Priority Matrix: `.codex/qa_walkthrough/test_priority_matrix.json`
- Coverage Analysis: `.codex/qa_walkthrough/coverage_analysis.json`

**Report Progress**: Use `report_progress` tool after each week with AfterMath analysis.

**Tag Usage**: #Phase23 #Coverage30 #PDALoop #UnitTests #IntegrationTests
```

---

### Phase 24 Activation Prompt

```markdown
@copilot Execute Phase 24 of the coverage roadmap to raise coverage from 30% to 50%.

**PLANSET**: `.codex/plans/PLANSET_PHASE_24_COVERAGE_50.md`

**Context**:
- Current coverage: 30.X% (Phase 23 complete)
- Target: 50% coverage threshold
- Timeline: 2-3 weeks
- Agent: Coverage Roadmap Agent

**Prerequisites**:
- Phase 23 complete with 30% threshold raised ✅
- Review Phase 23 AfterMath analysis
- Validate CI stability (last 5 runs green)
- Verify baseline at 30%+

**Execution Approach**:
1. Week 1: Add 100-120 integration tests for cross-module interactions
   - CLI → Model pipeline tests
   - Data → Model pipeline tests
   - Configuration integration across all systems
2. Week 2: Add 80-100 workflow/E2E tests + final push
   - Complete user workflow scenarios
   - Multi-step process testing
   - Gap-filling from Week 1

**Key Deliverables**:
- 100-120 integration tests
- 80-100 workflow/E2E tests
- Integration test patterns documented
- pyproject.toml updated to fail_under=50

**Success Criteria**:
- Coverage ≥50% validated
- Integration test suite established
- E2E workflows tested
- CI green for 3 runs
- Test execution time <10 minutes

**Error Handling**:
- Integration test timeout solutions
- External service mocking patterns
- Flaky test retry strategies
- Rollback procedure

**References**:
- Phase 23 AfterMath: `.codex/plans/PHASE_23_AFTERMATH_ANALYSIS.md`
- Integration targets: `.codex/plans/phase24_integration_targets.json`
- Coverage Roadmap: `.codex/plans/COVERAGE_THRESHOLD_ROADMAP.md`

**Report Progress**: Weekly updates with PDA cycle completion.

**Tag Usage**: #Phase24 #Coverage50 #IntegrationTests #WorkflowTests #E2E
```

---

### Phase 25 Activation Prompt

```markdown
@copilot Execute Phase 25 of the coverage roadmap to raise coverage from 50% to 70% - PRODUCTION READY milestone.

**PLANSET**: `.codex/plans/PLANSET_PHASE_25_COVERAGE_70.md`

**Context**:
- Current coverage: 50.X% (Phase 24 complete)
- Target: 70% coverage threshold (PRODUCTION READY)
- Timeline: 2 weeks
- Agent: Coverage Roadmap Agent
- **Significance**: 70% represents production-ready quality threshold

**Prerequisites**:
- Phase 24 complete with 50% threshold raised ✅
- Review Phase 24 AfterMath analysis
- Management approval for production readiness work
- Validate integration test stability

**Execution Approach**:
1. Week 1: Critical path & E2E coverage (80-100 tests)
   - Authentication/authorization flows
   - Data persistence critical paths
   - Production workflow E2E scenarios
   - Security testing
2. Week 2: Edge cases & final push to 70%
   - Boundary condition testing
   - Concurrent access patterns
   - Memory limits and performance
   - Final gap-filling

**Key Deliverables**:
- 80-100 critical path tests
- Comprehensive E2E production workflows
- Edge case and robustness testing
- Security validation complete
- pyproject.toml updated to fail_under=70
- Production readiness certification

**Success Criteria** (PRODUCTION BLOCKING):
- Coverage ≥70% validated
- All critical paths tested
- Zero high-severity bugs
- CI green for 5 consecutive runs
- Performance benchmarks passing
- Security testing complete

**Error Handling**:
- Emergency rollback for production-critical errors
- Performance regression detection
- Security vulnerability handling
- Comprehensive monitoring

**Production Readiness Checklist**:
- [ ] Authentication/authorization fully tested
- [ ] Data persistence verified
- [ ] Error handling comprehensive
- [ ] Performance validated
- [ ] Security testing complete
- [ ] Monitoring integration tested

**References**:
- Phase 24 AfterMath: `.codex/plans/PHASE_24_AFTERMATH_ANALYSIS.md`
- Critical paths: `.codex/plans/phase25_critical_paths.json`
- Coverage Roadmap: `.codex/plans/COVERAGE_THRESHOLD_ROADMAP.md`

**Report Progress**: Weekly with production readiness assessment.

**Celebration**: Upon completion, create tag `coverage-70-production-ready` 🎉

**Tag Usage**: #Phase25 #Coverage70 #ProductionReady #CriticalPaths #E2E #Security
```

---

## 🔄 PDA LOOP INTEGRATION

### Plan Phase Template
```markdown
## Week X Plan Phase

**Date**: YYYY-MM-DD  
**Objective**: [Specific coverage target for the week]

### Target Modules
[List of modules to test this week]

### Test Strategy
[Approach for this week's tests]

### Success Metrics
- Coverage increase: +X%
- Tests added: Y tests
- CI stability: green

### Risks
[Identified risks for the week]
```

### Do Phase Template
```markdown
## Week X Do Phase

**Dates**: YYYY-MM-DD to YYYY-MM-DD  
**Status**: IN PROGRESS / COMPLETE

### Tests Implemented
[List of test files created with counts]

### Challenges Encountered
[Issues faced and resolutions]

### Code Quality
- All tests have docstrings ✅
- Error handling included ✅
- Fixtures reusable ✅
```

### Analyze Phase Template
```markdown
## Week X Analyze Phase (AfterMath Analysis)

**Date**: YYYY-MM-DD  
**Coverage**: X.XX%

### What Worked ✅
[Successful patterns and approaches]

### What Didn't Work ❌
[Challenges and failures]

### Lessons Learned 📚
[Key insights from the week]

### Adjustments for Next Week 🔄
[Changes to strategy]

### Metrics
- Tests added: X
- Coverage gain: +Y%
- CI runs: Z/Z passing

**Tags**: #WeekXComplete #LessonsLearned #PDALoop
```

---

## 🤖 AGENT ACTIVATION PATTERNS

### Coverage Roadmap Agent
```markdown
@copilot Use the Coverage Roadmap Agent to [specific task]

Example tasks:
- "analyze current coverage gaps"
- "generate test plan for module X"
- "validate coverage metrics"
- "update coverage artifacts"
```

### Agent Capabilities
- Coverage baseline tracking
- Test prioritization using test_priority_matrix.json
- Threshold update validation
- Documentation generation
- Risk assessment

---

## 📊 METRICS & MONITORING

### Required Metrics Per Phase
- **Coverage Percentage**: Measured by pytest-cov
- **Test Count**: Unit, integration, E2E breakdown
- **CI Health**: Pass rate, execution time
- **Flaky Test Count**: Tests requiring reruns
- **Coverage Delta**: Week-over-week improvement

### Monitoring Commands
```bash
# Coverage check
python -m pytest tests/ --cov=src --cov-report=term

# Test count
find tests/ -name "test_*.py" -exec grep -c "^def test_" {} + | awk '{s+=$1} END {print s}'

# CI execution time
time python -m pytest tests/

# Flaky test detection
python -m pytest tests/ --reruns=3 -v | grep "RERUN" | wc -l
```

---

## 🚨 ERROR HANDLING MATRIX

| Error Type | Phase | Severity | Resolution Time | Rollback Required |
|------------|-------|----------|-----------------|-------------------|
| Dependency conflict | Any | HIGH | <4 hours | Maybe |
| Coverage regression | Any | MEDIUM | <1 day | No |
| Flaky tests | Any | MEDIUM | <1 day | No |
| CI infrastructure | Any | HIGH | <4 hours | Maybe |
| Threshold premature raise | Any | HIGH | <1 hour | Yes |
| Performance regression | 24-25 | HIGH | <1 day | Maybe |
| Security vulnerability | 25 | CRITICAL | <4 hours | Yes |

### Escalation Path
1. **Agent Self-Healing** (0-2 iterations): Agent attempts fixes
2. **Document & Continue** (2-5 iterations): Document issue, continue if non-blocking
3. **Escalate to Human** (>5 iterations): Comment on PR with issue details

---

## 📚 AFTERMMATH TAGGING SYSTEM

### Tags for Analysis
- `#PhaseXWeekY`: Identify analysis period
- `#CoverageGain`: Highlight coverage improvements
- `#LessonsLearned`: Key insights
- `#PatternDiscovered`: Reusable patterns
- `#ErrorHandled`: Resolved issues
- `#RiskMitigated`: Risk management
- `#FlakeyTest`: Test stability issues
- `#PerformanceIssue`: Speed/resource concerns

### AfterMath Analysis Storage
- Weekly: `.codex/plans/PHASE_X_WEEK_Y_AFTERMATH.md`
- Phase-level: `.codex/plans/PHASE_X_AFTERMATH_ANALYSIS.md`
- Consolidated: `.codex/cognitive_brain/COVERAGE_JOURNEY_AFTERMATH.md`

---

## 🎯 COGNITIVE BRAIN INTEGRATION

### Files to Update Per Phase
1. `.codex/plans/COVERAGE_THRESHOLD_ROADMAP.md` - Mark phase complete
2. `.codex/results.md` - Add phase results
3. `.codex/action_log.ndjson` - Append actions
4. `.codex/cognitive_brain/PHASE_X_STATUS.md` - Create status doc
5. `.codex/change_log.md` - Document changes

### Update Template
```json
{
  "timestamp": "YYYY-MM-DDTHH:MM:SSZ",
  "actor": "coverage-roadmap-agent",
  "phase": "X",
  "action": "completed",
  "coverage": "X%",
  "tests_added": Y,
  "duration": "Z weeks",
  "status": "success"
}
```

---

## 📞 CONTINUATION PROTOCOL

### After Phase 23
Post comment:
```markdown
@copilot Phase 23 complete! Continue with Phase 24 using PLANSET_PHASE_24_COVERAGE_50.md
```

### After Phase 24
Post comment:
```markdown
@copilot Phase 24 complete! Continue with Phase 25 (PRODUCTION READY) using PLANSET_PHASE_25_COVERAGE_70.md
```

### After Phase 25
Post comment:
```markdown
@copilot Phase 25 complete - 70% PRODUCTION READY coverage achieved! 🎉

Review completion summary and determine if Phase 26+ (path to 100%) is needed based on business requirements.
```

---

## ✅ FINAL CHECKLIST

Before starting each phase:
- [ ] Previous phase complete and validated
- [ ] AfterMath analysis reviewed
- [ ] CI health verified
- [ ] Prerequisites met
- [ ] PLANSET reviewed
- [ ] Agent activated

During phase execution:
- [ ] Follow PDA loop weekly
- [ ] Report progress regularly
- [ ] Update cognitive brain files
- [ ] Monitor CI health
- [ ] Document lessons learned

After phase completion:
- [ ] AfterMath analysis created
- [ ] Threshold raised and validated
- [ ] CI green for required runs
- [ ] Documentation updated
- [ ] Continuation prompt posted

---

**Status**: ✅ READY FOR EXECUTION  
**Owner**: @mbaetiong  
**Agent**: Coverage Roadmap Agent  
**Next Action**: Activate Phase 23 when ready
