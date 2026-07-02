# PR #5190 Remediation — Phase B Execution Plan

**Date**: 2026-07-02T01:24:22Z  
**Campaign**: Track 2 (Fix Track) — RAG Coverage Remediation  
**Decision**: Remediate RAG module coverage from 34.63% → ≥95%  
**Authority**: D-mode autonomous execution with GO CONTINUE authorization  

---

## 📋 Phase B Delegation Status

### Active Agents (Parallel Execution)

#### 1. ✅ unified-coverage-agent (Gap Analysis)
- **Agent ID**: unified-coverage-agent-gap-ana
- **Task**: Comprehensive RAG module coverage gap analysis
- **Deliverables**:
  - Detailed gap report (public functions/classes per module)
  - Priority matrix (coverage impact, complexity, criticality)
  - Test skeleton templates
  - Roadmap to ≥95% in 3 phases (96h total)
- **Output Location**: `.codex/RAG_COVERAGE_GAP_ANALYSIS.md`
- **Status**: 🔄 RUNNING

#### 2. ✅ autonomous-test-healer-agent (Test Skeletons)
- **Agent ID**: autonomous-test-healer-rag-ske
- **Task**: Auto-generate test skeleton files for 0% coverage modules
- **Target Modules**:
  - Cache layer: distributed_cache, embedding_cache, query_cache
  - Providers: openai, anthropic, vertex
  - Benchmarks: all modules
- **Deliverables**:
  - Valid test files (importable, no parse errors)
  - Test function templates with TODOs
  - Mock/fixture definitions
  - Coverage markers for tracking
- **Output Location**: `tests/rag/` + `.codex/RAG_TEST_SKELETONS_CREATED.md`
- **Status**: 🔄 RUNNING

#### 3. ✅ ci-auto-healer-agent (Workflow Failures)
- **Agent ID**: ci-auto-healer-workflow-fixes
- **Task**: Fix remaining CI workflow failures
- **Issues**:
  - Metrics collector NoneType (phase-8-3-perf-monitor.yml)
  - Secrets baseline enforcer (2 failures)
  - Admin token scope (T-03) if fixable
- **Deliverables**:
  - Root cause analysis
  - Code fixes with validation
  - Test results
- **Output Location**: `.codex/CI_WORKFLOW_FIXES_SUMMARY.md`
- **Status**: 🔄 RUNNING

#### 4. ✅ mypy-manager-agent (Type Errors)
- **Agent ID**: mypy-manager-type-errors
- **Task**: Resolve mypy type error regressions (122 → ≤121)
- **Scope**:
  - Identify regression errors
  - Fix type annotations
  - Update baseline if necessary (with justification)
- **Deliverables**:
  - List of fixed errors with commit SHAs
  - Baseline changes documentation
  - Verification results
- **Output Location**: `.codex/MYPY_REGRESSION_FIXES.md`
- **Status**: 🔄 RUNNING

#### 5. ⏳ link-validator-agent (Documentation Links)
- **Agent ID**: link-validator-broken-links
- **Task**: Fix broken documentation links
- **Scope**: All broken links in `docs/` and `.github/workflows/`
- **Deliverables**:
  - Broken links list (categorized)
  - Fixes applied per link
  - Validation results (100% pass target)
- **Output Location**: `.codex/LINK_VALIDATION_FIXES.md`
- **Status**: 🔴 QUEUED (waiting for concurrent limit)
- **Action**: Will auto-trigger when slot becomes available

---

## 🎯 Phase B Timeline Estimate

| Phase | Task | Duration | Gate |
|-------|------|----------|------|
| **B.1** | Gap analysis + test skeletons + CI fixes | 2-4 hours | Complete in parallel |
| **B.2** | Type error resolution | 1-2 hours | Pass mypy baseline |
| **B.3** | Link validation fixes | 1-2 hours | All links pass |
| **B.4** | Results aggregation | 1 hour | All agents complete |

**Expected Phase B Completion**: 2026-07-02 ~8:00Z (6-8 hours from start)

---

## 📊 Success Criteria

### Each Agent Must Deliver
- ✅ Comprehensive analysis/fixes documented
- ✅ Code valid and tested locally
- ✅ Output stored in `.codex/` (tracked, not /tmp)
- ✅ Clear next steps for Phase C

### Phase B Success Threshold
- ✅ All 5 agents complete without escalation
- ✅ All CI fixes validated
- ✅ Test skeleton files created and importable
- ✅ Coverage gap analysis provides Phase 2.2 direction
- ✅ Mypy and link validation pass

---

## 🔄 Phase C Dependency Chain

Once Phase B completes:

1. **C.1 - Coverage Re-validation** (1 hour):
   - Use Phase B gap analysis to prioritize test development
   - Re-run coverage with test skeletons
   - Verify improvement toward ≥95%

2. **C.2 - CI Validation** (1 hour):
   - Confirm all Phase B fixes hold under full test suite
   - Verify no new failures introduced

3. **C.3 - Documentation Update** (1 hour):
   - Update `CHANGELOG.md` with coverage remediation
   - Document decision rationale (Track 2 choice)
   - Prepare Tier 2 documentation work brief

4. **C.4 - Tier 2 Work Unblocked**:
   - Queue `unified-doc-agent` for governance documentation
   - Queue `documentation-quality-agent` for retention policy QA
   - Release to contributors

---

## 📝 Accountability Tracking

### This Session
- Commit: `chore: Initiate PR #5190 post-merge remediation — Track 2 (Fix) with parallel agent delegation`
- Branch: `copilot/post-merge-session-pr-5190`
- PR Status: Post-merge work (no new PR created, working within current branch)

### Next Updates Required
- **After Phase B completes**: Call `engine-tools-report_progress` with Phase B results
- **Before Phase C starts**: Update `AGENT_ACCOUNTABILITY_REPORT.md` with agent outcomes
- **After all phases complete**: Update `CHANGELOG.md` with full remediation summary

### REQ-4/REQ-5 Compliance
- AGENT_ACCOUNTABILITY_REPORT.md will be updated in Phase C completion commit
- CHANGELOG.md will be updated in Phase C completion commit
- Both will satisfy `session_wrapup_autofix.py --check` requirements

---

## 🚨 Risk Assessment

### Low Risk
- All agents are specialized for their domains
- Parallel execution reduces timeline
- Each agent stores outputs in `.codex/` for tracking
- No merge conflicts expected (working in branch)

### Contingency Triggers
- ❌ If agent fails: Re-run with escalation details
- ❌ If timeline exceeds 12 hours: Pause and reassess
- ❌ If any Phase B output invalid: Manual remediation

---

## 📌 Decision Rationale (Track 2)

**Why Fix Track (not Fast Track)?**
- PR #5190 explicitly states ≥95% coverage objective
- Current 34.63% is baseline state, not aligned with PR intent
- Full remediation demonstrates completion of PR goals
- Governance work (Tier 2) blocks without coverage resolution

**Why Parallel Agents?**
- 5 independent tasks can run concurrently (per memory: "Aggressively use task tool")
- Reduces 5-7 day estimate to ~6-8 hours for Phase B
- D-mode authorization: "always GO continue" at decision points
- User preference: "Maximize Custom Agent Delegation"

**Next Lane Activation**:
After Phase B completes → Proceed immediately to Phase C (no waiting)
After Phase C completes → Proceed immediately to Phase D (Tier 2 docs)

---

**Status**: 🟢 **PHASE B ACTIVE** — 4 agents running, 1 queued  
**Last Updated**: 2026-07-02T01:24:22Z  
**Next Checkpoint**: Phase B completion notification + progress update
