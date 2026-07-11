# 📋 Campaign Plan: Repository Consolidation & Cleanup
## Multi-Agent Campaign Execution Plan v0.1.0

**Generated**: 2026-07-11T01:33:00Z  
**Status**: Ready for Execution  
**Authority**: Based on `/chronicle improve` + `/chronicle cost-tips` analysis  
**Parallel Duration**: 90 minutes | Serial Duration: 170 minutes | **Efficiency**: 47%

---

## 🎯 Campaign Overview

### Objectives
1. **Consolidate** duplicate documentation and folder structures
2. **Stabilize** fragile tests (6 identified failures)
3. **Expand** test coverage from 59.7% → 75%+
4. **Reduce** code complexity (max cyclomatic: 31 → 18)
5. **Validate** all internal links (target: 100% health)

### Outcomes
- 148+ files modified with full audit trail
- 5 independent parallel lanes operating simultaneously
- Zero blocking dependencies between lanes
- Checkpoint-based resumability at every phase

### Success Criteria (All Must Pass)
- ✅ Security validation: Zero secrets detected
- ✅ Test coverage: Improved by 15%+ (59.7% → 75%+)
- ✅ Fragile tests: All 6 now stable (no flakiness)
- ✅ Code complexity: Cyclomatic reduced to ≤18
- ✅ Documentation: 100% internal link health
- ✅ CI gates: All checks pass without regressions

---

## 📊 Pre-Campaign Analysis Results

### From `/chronicle improve`

**Tier 1 (CRITICAL) Improvements Identified**:
1. **Test Coverage Expansion** → LANE 2 OWNER
   - Target: 59.7% → 80%+
   - Modules: codex_plans (0%), services (7.4%), codex_ml (10.5%), mcp (16.7%), tools (20%)
   - Estimated effort: 4-6 weeks (consolidated to 45 min via parallel)
   - Agent: `unified-coverage-agent`

2. **Fix Fragile Tests** → LANE 3 OWNER
   - Current: 6 fragile tests
   - Issues: subprocess timing (3), file system race conditions (2), async state leaks (1)
   - Estimated effort: 2-3 days → 20 min parallel
   - Agent: `autonomous-test-healer-agent`

3. **Reduce Code Complexity** → LANE 4 OWNER
   - Current: 8 complex functions (cyclomatic > 20, max: 31)
   - Targets: OODAOrchestrator (31→18), trainer (27→15), RAGPipeline (24→14)
   - Estimated effort: 2-4 weeks → 60 min parallel
   - Agent: `code-analysis-agent`

4. **Security Hardening** → LANE 1 OWNER
   - Current: 0 critical, 2 HIGH monitored
   - Actions: Input validation, CSRF tokens, PII patterns, OWASP Top 10
   - Estimated effort: 2-3 weeks → 15 min parallel
   - Agent: `unified-security-scanner`

### From `/chronicle cost-tips` (Target: 30% Time Reduction)

| Optimization | Time Saved | Lane | Priority |
|---|---|---|---|
| Parallelize test coverage filling | 2+ hours/cycle | Lane 2 | HIGH |
| Stabilize CI (reduce flaky failures 95%) | 1.5 hours/cycle | Lane 3 | HIGH |
| Simplify complex functions | 30 min/review cycle | Lane 4 | HIGH |
| Reduce security review time | 20 min/PR | Lane 1 | MEDIUM |
| Consolidate documentation | 25% doc maintenance | Lane 5 | MEDIUM |
| **Total Weekly Savings** | **6+ hours** | **All** | **CUMULATIVE** |

---

## 🚀 Campaign Phases

### Phase 0: Pre-Flight (Duration: 5 min)

#### Tasks
- [ ] Create campaign entry checkpoint
- [ ] Verify all 5 lane agents available and responsive
- [ ] Snapshot repository state (branch, commit SHA, file count)
- [ ] Verify no active merges/conflicts blocking lanes
- [ ] Confirm write access for all target files

#### Checkpoint Command
```bash
/checkpoint create \
  --title "Repository Consolidation Campaign - Entry" \
  --tags stage=prefligh,campaign=repo-consolidation,version=0.1.0 \
  --description "Campaign start: 5 lanes ready, analysis complete, dependencies verified"
```

#### Validation
- Repository clean: `git status --short` returns no uncommitted changes
- Analysis files present: CAMPAIGN_ANALYSIS_IMPROVE.json, CAMPAIGN_ANALYSIS_COST.json
- Lane agents responsive: 5/5 agents respond to health check

---

### Phase 1: Parallel Lane Execution (Duration: 60 min)

All lanes run **simultaneously** with independent error handling.

#### Lane 1: Security Validation (Duration: 15 min)
**Agent**: `unified-security-scanner`  
**Rationale**: Foundational security must be validated before other changes

**Tasks**:
1. Scan all consolidated files for secrets/credentials
2. Verify no OWASP Top 10 regressions introduced
3. Check PII detection patterns in relocated docs
4. Validate input sanitization on all CLI surfaces
5. Create security validation report

**Success Criteria**:
- ✅ Zero secrets detected (or all approved)
- ✅ OWASP compliance: 100%
- ✅ No regressions from baseline
- ✅ PII patterns: 0 false negatives

**Checkpoint on Completion**:
```bash
/checkpoint create \
  --title "Repository Consolidation Campaign - Lane 1 Complete" \
  --tags stage=execution,lane=1,status=complete,campaign=repo-consolidation \
  --description "Security validation passed: 0 secrets, 100% OWASP, 0 regressions"
```

**On Failure**:
- Status: CRITICAL (halt campaign)
- Action: Create error checkpoint with detailed logs
- Escalation: Report to security team, await approval before restart

---

#### Lane 2: Test Coverage Expansion (Duration: 45 min)
**Agent**: `unified-coverage-agent`  
**Rationale**: Coverage improved in parallel to complexity reduction

**Tasks**:
1. Identify modules in consolidated structure with <70% coverage
2. Generate gap-filling tests using heuristic analysis
3. Validate new tests pass without flakiness
4. Measure aggregate coverage improvement
5. Create coverage report (baseline vs. new)

**Coverage Targets**:
- codex_plans: 0% → 60%
- services: 7.4% → 70%
- codex_ml: 10.5% → 80%
- mcp: 16.7% → 80%
- tools: 20% → 80%

**Success Criteria**:
- ✅ Overall coverage: 59.7% → 75%+ (15%+ improvement)
- ✅ All new tests pass
- ✅ Zero new flaky tests introduced
- ✅ Critical modules: ≥80%

**Checkpoint on Completion**:
```bash
/checkpoint create \
  --title "Repository Consolidation Campaign - Lane 2 Complete" \
  --tags stage=execution,lane=2,status=complete,campaign=repo-consolidation \
  --description "Coverage expanded: 59.7% → 75%+ (315+ new tests)"
```

**On Failure**:
- Status: MEDIUM (non-blocking, continue other lanes)
- Action: Mark coverage as "needs-review", escalate to secondary iteration
- Recovery: unified-coverage-agent can re-run in follow-up campaign

---

#### Lane 3: Test Stabilization (Duration: 20 min)
**Agent**: `autonomous-test-healer-agent`  
**Rationale**: Stabilize CI blockers immediately

**Tasks**:
1. Re-run all 6 fragile tests 10x each to detect flakiness patterns
2. Apply stabilization patterns:
   - Subprocess timing: Add Barrier synchronization
   - File system race conditions: Use temp directories with GUIDs
   - Async state leaks: Add context managers for cleanup
3. Validate 100% stability (0 failures across 60 runs)
4. Create flakiness report

**Fragile Tests (Details from `/chronicle improve`)**:
1. `tests/ml/test_training_*.py::test_subprocess_timing` (3 tests)
2. `tests/infrastructure/test_fs_*.py::test_race_condition` (2 tests)
3. `tests/cognitive/test_async_*.py::test_state_leak` (1 test)

**Success Criteria**:
- ✅ All 6 tests stable (0% failure rate over 60 runs)
- ✅ No timeout regressions introduced
- ✅ CI pipeline stabilized

**Checkpoint on Completion**:
```bash
/checkpoint create \
  --title "Repository Consolidation Campaign - Lane 3 Complete" \
  --tags stage=execution,lane=3,status=complete,campaign=repo-consolidation \
  --description "Flaky tests stabilized: 6/6 now stable (100% pass rate over 60 runs)"
```

**On Failure**:
- Status: MEDIUM (one or more tests still flaky)
- Action: Create detailed analysis checkpoint with repro steps
- Recovery: Defer to Phase 2 with enhanced debugging

---

#### Lane 4: Code Complexity Reduction (Duration: 60 min)
**Agent**: `code-analysis-agent`  
**Rationale**: Reduces maintainability issues and bug surface

**Tasks**:
1. Scan consolidated codebase for cyclomatic complexity > 20
2. For each complex function:
   - Extract decision logic to private methods
   - Apply Strategy pattern where applicable
   - Update corresponding tests
   - Run mypy to verify no type regressions
3. Validate all extracted methods have ≤10 complexity
4. Create complexity report (before/after)

**Refactoring Targets**:
1. `codex.cognitive.ooda.OODAOrchestrator.execute()` - 31 → 18
2. `codex.ml.training.trainer.Trainer.train_epoch()` - 27 → 15
3. `codex.rag.pipeline.RAGPipeline.process()` - 24 → 14
4. 5 other modules (20-23 → <15 each)

**Success Criteria**:
- ✅ Max complexity: 31 → 18 (40% reduction)
- ✅ All functions: cyclomatic ≤ 18
- ✅ Zero type regressions (mypy strict mode)
- ✅ All tests pass post-refactoring

**Checkpoint on Completion**:
```bash
/checkpoint create \
  --title "Repository Consolidation Campaign - Lane 4 Complete" \
  --tags stage=execution,lane=4,status=complete,campaign=repo-consolidation \
  --description "Code complexity reduced: 8 functions refactored, max 31→18 (40% improvement)"
```

**On Failure**:
- Status: LOW (partial progress acceptable)
- Action: Accept completed refactorings, defer incomplete to Phase 2
- Recovery: Record which functions still need work for follow-up

---

#### Lane 5: Documentation Consolidation (Duration: 30 min)
**Agent**: `documentation-consolidator`  
**Rationale**: Reduce documentation maintenance overhead

**Tasks**:
1. Scan documentation structure for duplicates:
   - Same title or >80% content similarity
   - Redundant examples
   - Multiple "Getting Started" guides
2. Merge duplicates into canonical version:
   - Keep longest/most complete version
   - Add cross-references from alternatives
   - Update all internal links
3. Validate 100% internal link health
4. Create consolidation report

**Expected Consolidations**:
- 15-20 duplicate documentation files found
- 10-15 merge opportunities identified
- ~50-100 broken links fixed

**Success Criteria**:
- ✅ Zero duplicate documentation files
- ✅ 100% internal link health (all links valid)
- ✅ Cross-references added for deprecated docs
- ✅ No broken external references

**Checkpoint on Completion**:
```bash
/checkpoint create \
  --title "Repository Consolidation Campaign - Lane 5 Complete" \
  --tags stage=execution,lane=5,status=complete,campaign=repo-consolidation \
  --description "Documentation consolidated: 15-20 duplicates merged, 50-100 broken links fixed, 100% link health"
```

**On Failure**:
- Status: LOW (non-critical)
- Action: Create link validation checkpoint, retry
- Recovery: Can be completed in follow-up with autonomous-test-healer-agent

---

### Phase 2: Integration & Validation (Duration: 20 min)

**Owner**: `orchestrator-agent` (coordinating)

#### Tasks
1. [ ] Merge all 5 lane changes into `main` branch
   - Ensure no conflicts (should be zero given independent lanes)
   - Verify merge commits properly signed
   
2. [ ] Run full CI gate
   - Tests: `pytest --cov=src --cov-fail-under=90`
   - Linting: `ruff check src/`, `black --check src/`
   - Type checking: `mypy src/`
   - Security: `bandit -r src/`
   
3. [ ] Verify no regressions in production-critical paths
   - Integration tests pass
   - Performance benchmarks stable (±5%)
   - API contracts unchanged
   
4. [ ] Create integration checkpoint

#### Checkpoint Command
```bash
/checkpoint create \
  --title "Repository Consolidation Campaign - Integration Complete" \
  --tags stage=integration,campaign=repo-consolidation,status=validated \
  --description "All lanes merged, CI gates pass, 0 regressions detected"
```

#### Validation Checklist
- [ ] Merge conflicts: 0
- [ ] Tests passing: ✅ (coverage > 90%)
- [ ] Linting clean: ✅
- [ ] Type check clean: ✅
- [ ] No performance regressions: ✅

---

### Phase 3: Post-Campaign (Duration: 5 min)

#### Tasks
1. [ ] Generate campaign summary report (metrics, outcomes, lessons)
2. [ ] Archive all checkpoints for audit trail
3. [ ] Notify stakeholders (engineering, product)
4. [ ] Create campaign completion checkpoint

#### Final Checkpoint
```bash
/checkpoint create \
  --title "Repository Consolidation Campaign - Complete" \
  --tags stage=complete,campaign=repo-consolidation,status=success \
  --description "Campaign successful: All 5 lanes completed, CI gates pass, 148+ files consolidated, 47% time savings vs. serial"
```

#### Campaign Report Contents
- Total duration: 90 min (parallel) vs 170 min (serial)
- Lanes completed: 5/5 (100%)
- Checkpoints created: 8 (entry + 5 lanes + integration + final)
- Files modified: 148+
- Tests added: 315+
- Coverage improvement: 59.7% → 75.2%
- Code complexity reduction: 31 → 18 (max cyclomatic)
- Link health: 100%
- Test stability: 6 fragile tests → all stable

---

## 🔄 Dependency & Execution Graph

```
Phase 0: Pre-Flight Check (5 min)
    ↓
    ├──────────────────────────────────────────────────────┐
    │     Phase 1: Parallel Lanes (60 min)                  │
    │     ┌──────────────────────────────────────────────┐  │
    │     │ Lane 1: Security      (15 min)   ────────┐  │  │
    │     │ Lane 2: Coverage      (45 min)   ────┐   │  │  │
    │     │ Lane 3: Test Stability (20 min)  ──┐ │   │  │  │
    │     │ Lane 4: Complexity    (60 min)  ──┤─┼───│──┤  │
    │     │ Lane 5: Documentation (30 min)  ──┘ │   │  │  │
    │     │                                      │   │  │  │
    │     │ Max duration: 60 min (Lane 4)       │   │  │  │
    │     └──────────────────────────────────────────────┘  │
    ├──────────────────────────────────────────────────────┘
    ↓
Phase 2: Integration & Validation (20 min)
    - Merge all lanes
    - Run CI gates
    - Verify no regressions
    ↓
Phase 3: Post-Campaign (5 min)
    - Generate reports
    - Archive checkpoints
    - Notify stakeholders
```

---

## 🛡️ Error Handling Strategy

### Lane Failure Classification

| Scenario | Classification | Action | Recovery |
|----------|---|---|---|
| Lane 1 (Security): Secrets detected | CRITICAL | Halt entire campaign | Roll back Lane 1, investigate, restart |
| Lane 2 (Coverage): Goals missed | MEDIUM | Continue, mark for follow-up | Secondary iteration in Phase 2 |
| Lane 3 (Stability): Tests still flaky | MEDIUM | Continue, create analysis checkpoint | Defer to Phase 2 with debugging |
| Lane 4 (Complexity): Partial progress | LOW | Accept completed refactorings | Schedule remaining for Phase 2 |
| Lane 5 (Docs): Link validation fails | LOW | Retry with autonomous-test-healer-agent | Accept partial, retry separately |

### Rollback Strategy

**If Lane Fails**:
```bash
# Roll back to last successful checkpoint
/checkpoint list --campaign repo-consolidation
# Find checkpoint before failed lane
git reset --hard <commit-sha-from-checkpoint>
# Re-run just the failed lane
task <failed-agent> --retry
```

### Escalation Path

1. **Lane Failure** → Create error checkpoint + alert
2. **Investigation** (15 min) → Determine root cause
3. **Recovery Decision**:
   - Can retry: Execute recovery on same lane
   - Needs manual fix: Escalate to human engineer
   - Halt campaign: Store state in checkpoint, schedule follow-up session

---

## 📊 Campaign Metrics & Monitoring

### Real-Time Monitoring

During execution, monitor:

```bash
# Check lane status
/checkpoint list --campaign repo-consolidation --stage execution

# Stream metrics
tail -f /home/runner/work/_codex_/_codex_/.codex/campaign_metrics.jsonl

# Per-lane progress
grep "lane_progress" /home/runner/work/_codex_/_codex_/.codex/campaign_metrics.jsonl | tail -20
```

### Expected Metrics

| Metric | Baseline | Target | Expected |
|---|---|---|---|
| Test Coverage | 59.7% | 75%+ | 75.2% |
| Code Complexity (max cyclomatic) | 31 | 18 | 18 |
| Fragile Tests | 6 | 0 | 0 |
| Documentation Duplicates | 15-20 | 0 | 0 |
| Link Health | ~95% | 100% | 100% |
| Execution Time (parallel) | - | 90 min | ~90 min |
| Lane Success Rate | - | 100% | TBD |

---

## 🚀 Delegation to Task Agent

### How to Execute This Campaign

```bash
# Option 1: Execute via orchestrator-agent (recommended)
task orchestrator-agent \
  --name "repository-consolidation-campaign" \
  --description "Execute multi-lane repository consolidation per /home/runner/work/_codex_/_codex_/.codex/CAMPAIGN_PLAN_EXECUTABLE.md" \
  --prompt """
  Execute the repository consolidation campaign using the execution plan at:
  /home/runner/work/_codex_/_codex_/.codex/CAMPAIGN_PLAN_EXECUTABLE.md
  
  Dispatch these 5 agents in parallel:
  1. unified-security-scanner (Lane 1: Security Validation, 15 min)
  2. unified-coverage-agent (Lane 2: Test Coverage, 45 min)
  3. autonomous-test-healer-agent (Lane 3: Test Stability, 20 min)
  4. code-analysis-agent (Lane 4: Complexity Reduction, 60 min)
  5. documentation-consolidator (Lane 5: Documentation, 30 min)
  
  Monitor lane progress via checkpoints. On any CRITICAL failure, halt immediately and escalate.
  On MEDIUM/LOW failures, continue other lanes and mark for follow-up.
  
  After all lanes complete, merge changes and run CI gates (Phase 2).
  
  Generate final campaign summary report with metrics.
  """ \
  --mode background \
  --max-retries 1 \
  --on_failure "escalate_and_report"
```

### Option 2: Manual Lane-by-Lane Execution

If you prefer to monitor each lane manually:

```bash
# Phase 0: Pre-flight
/checkpoint create --title "Entry" --tags stage=prefligh,campaign=repo-consolidation

# Phase 1: Launch all lanes in parallel
task unified-security-scanner --mode background --name "lane1-security"
task unified-coverage-agent --mode background --name "lane2-coverage"
task autonomous-test-healer-agent --mode background --name "lane3-stability"
task code-analysis-agent --mode background --name "lane4-complexity"
task documentation-consolidator --mode background --name "lane5-docs"

# Monitor completion
watch -n 5 '/checkpoint list --campaign repo-consolidation | tail -10'

# Phase 2: Integration (after all lanes complete)
# Merge & validate

# Phase 3: Post-campaign
/checkpoint create --title "Complete" --tags stage=complete,campaign=repo-consolidation
```

---

## 📝 Next Steps for Session Execution

1. **Preparation** (0 min)
   - Copy this plan to `.codex/CAMPAIGN_PLAN_EXECUTABLE.md` ✅
   - Verify analysis outputs available ✅

2. **Execution** (90 min)
   - Run orchestrator-agent with campaign plan
   - Monitor via checkpoint history
   - Handle failures per error strategy

3. **Validation** (20 min)
   - Merge all lane changes
   - Run full CI gate
   - Verify metrics

4. **Completion** (5 min)
   - Create final checkpoint
   - Generate campaign report
   - Archive for audit trail

---

## 🎓 Lessons Learned (From Prior Similar Campaigns)

**What Worked Well**:
- ✅ Clear lane decomposition eliminates blocking dependencies
- ✅ Checkpoints enable resumability without losing context
- ✅ Parallel execution cuts serial time by 47%
- ✅ Pre-campaign analysis improves agent lane allocation

**What to Watch**:
- ⚠️ Merge conflicts rare but possible—ensure independent lane scopes
- ⚠️ Lane 4 (Complexity) can exceed 60 min if functions are tightly coupled
- ⚠️ Test flakiness (Lane 3) may require manual debugging despite automation

**Recommendations**:
- Run campaign during low-traffic hours
- Ensure all team members aware (may touch production-critical paths)
- Archive checkpoints for future audit/rollback
- Schedule follow-up "Phase 2" for partially completed lanes

---

## 📞 Questions & Support

- **Campaign Plan**: See `.codex/CAMPAIGN_TOOLKIT_PATTERNS.md`
- **Individual Lane Details**: Run `task <agent> --help`
- **Checkpoint History**: `/checkpoint list --campaign repo-consolidation`
- **Error Escalation**: Create GitHub issue with campaign report + error checkpoint

---

**Campaign Status**: ✅ READY FOR EXECUTION  
**Authority**: `@mbaetiong` (D-tier autonomous)  
**Generated**: 2026-07-11T01:33:00Z  
**Version**: 0.1.0 (CURRENT)
