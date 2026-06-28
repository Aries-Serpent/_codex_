# Agent Brief: Wave 3 - Coverage Gap Remediation (Parallel Lanes)

**Target Agent:** unified-coverage-agent  
**Authority:** @mbaetiong (Autonomous GO CONTINUE)  
**Mode:** Parallel lanes (3 concurrent)  
**Timeline:** 53-67 hours per lane  
**Total Estimated:** 160 tests, 60-80% coverage per lane  
**Status:** READY FOR DISPATCH  
**Coordinating Brief:** AGENT_BRIEF_STAGE_5_WAVE2_DELEGATION.md (Stage 5, Phase 6 Wave 1)

---

## Mission

Implement TIER-2 coverage specifications to raise ML systems from current baseline (8-10%) to ≥70% coverage across 3 parallel lanes. Estimated 160 total tests (50-70 per lane) targeting machine learning training, CLI interface, and data pipeline modules.

---

## Executive Summary

Phase 6 Wave 1 established 79 TIER-1 tests with 70%+ coverage baseline. Wave 3 focuses on eliminating ML system coverage gaps identified in Phase 5 analysis:

| Lane | Module | Current Coverage | Target | Gap | Estimated Tests | Timeline |
|------|--------|-------------------|--------|-----|-----------------|----------|
| **3.1** | ML Training Pipeline | 9.4% | 60-80% | 50-71% | 50 | 53 hours |
| **3.2** | ML CLI Interface | 10% | 60-80% | 50-70% | 40 | 48 hours |
| **3.3** | ML Data Pipeline | 8.6% | 60-80% | 51-71% | 70 | 67 hours |

**Total Coverage Impact:** +4-6% overall repository coverage (estimate based on ML modules' weight in codebase)

---

## Lane 3.1: ML Training Pipeline Coverage

**Module Target:** `src/codex/ml/training.py`, `src/codex/ml/train_*.py` (4 files)  
**Current Coverage:** 9.4%  
**Target Coverage:** 60-80%  
**Estimated Tests:** 50  
**Timeline:** 53 hours  
**Status:** READY FOR DISPATCH

### Current Coverage Gaps

- `fit()` method with various optimization strategies: 0% coverage
- Early stopping callback logic: 0% coverage
- Loss tracking and metric computation: 5% coverage
- Model checkpointing and recovery: 2% coverage
- Hyperparameter sweeps: 8% coverage
- Distributed training mode (if applicable): 0% coverage

### Test Specifications (50 Tests)

| Category | Count | Examples | Estimated Hours |
|----------|-------|----------|-----------------|
| Unit: Optimization strategies | 8 | SGD, Adam, AdamW variants | 6 |
| Unit: Loss functions | 6 | CrossEntropy, MSE, custom | 5 |
| Unit: Callbacks | 8 | EarlyStopping, LearningRateScheduler | 6 |
| Unit: Metrics tracking | 5 | Precision, recall, F1, AUC | 4 |
| Integration: Pipeline flow | 8 | train→validate→checkpoint cycle | 12 |
| Error paths: Invalid configs | 5 | Missing model, bad device, etc. | 8 |
| Edge cases: Boundary conditions | 4 | Empty batches, single sample, NaN handling | 6 |
| **Subtotal** | **50** | | **53 hours** |

### Success Criteria for Lane 3.1

- ✅ 50 tests implemented, 100% pass rate
- ✅ Training pipeline coverage: 60-80%
- ✅ All optimization paths tested (SGD, Adam, etc.)
- ✅ Callback system fully tested
- ✅ No regression in Phase 6 Wave 1 baseline tests

---

## Lane 3.2: ML CLI Interface Coverage

**Module Target:** `src/codex/cli/ml_*.py`, `src/codex/ml/cli.py`  
**Current Coverage:** 10%  
**Target Coverage:** 60-80%  
**Estimated Tests:** 40  
**Timeline:** 48 hours  
**Status:** READY FOR DISPATCH

### Current Coverage Gaps

- Train command with various flags: 15% coverage
- Evaluate command parsing: 5% coverage
- Export/deploy commands: 0% coverage
- Help text and argument validation: 0% coverage
- Error message generation: 8% coverage
- Configuration file loading: 3% coverage

### Test Specifications (40 Tests)

| Category | Count | Examples | Estimated Hours |
|----------|-------|----------|-----------------|
| Unit: Argument parsing | 8 | train, evaluate, export with flags | 6 |
| Unit: Config validation | 6 | Valid/invalid YAML, JSON configs | 5 |
| Unit: Help text generation | 4 | Commands, subcommands, options | 2 |
| Integration: Full CLI workflows | 12 | train→eval→export sequences | 20 |
| Error paths: Invalid inputs | 6 | Bad paths, wrong types, missing args | 8 |
| Edge cases: Special characters | 4 | Spaces, quotes, unicode in paths | 5 |
| **Subtotal** | **40** | | **48 hours** |

### Success Criteria for Lane 3.2

- ✅ 40 tests implemented, 100% pass rate
- ✅ CLI interface coverage: 60-80%
- ✅ All CLI commands tested (train, eval, export, etc.)
- ✅ Argument validation fully covered
- ✅ Error messages tested and correct

---

## Lane 3.3: ML Data Pipeline Coverage

**Module Target:** `src/codex/ml/data.py`, `src/codex/ml/preprocessing.py`, `src/codex/data/*.py` (5+ files)  
**Current Coverage:** 8.6%  
**Target Coverage:** 60-80%  
**Estimated Tests:** 70  
**Timeline:** 67 hours  
**Status:** READY FOR DISPATCH

### Current Coverage Gaps

- Data loader implementations: 5% coverage
- Data augmentation transforms: 0% coverage
- Preprocessing pipelines: 3% coverage
- Batch sampling strategies: 0% coverage
- Data validation and sanitization: 8% coverage
- Caching and persistence layer: 1% coverage

### Test Specifications (70 Tests)

| Category | Count | Examples | Estimated Hours |
|----------|-------|----------|-----------------|
| Unit: Data loaders | 12 | CSVLoader, JSONLoader, ImageLoader, TextLoader | 14 |
| Unit: Transforms | 10 | Normalization, augmentation, filtering | 12 |
| Unit: Preprocessing | 10 | Tokenization, embedding, scaling | 12 |
| Unit: Sampling strategies | 8 | RandomSampler, StratifiedSampler, SequentialSampler | 9 |
| Unit: Validation logic | 8 | Schema validation, dtype checks, range checks | 10 |
| Integration: Full pipeline | 15 | Load→preprocess→augment→batch sequences | 18 |
| Error paths: Invalid data | 5 | Corrupted files, mismatched schemas, missing values | 8 |
| Edge cases: Boundary conditions | 2 | Empty datasets, single row, NaN/inf values | 4 |
| **Subtotal** | **70** | | **89 hours** |

*Note: 89-hour estimate for Lane 3.3 exceeds 67-hour target due to complexity. Recommend prioritizing integration tests (15) and core loaders (12) for MVP coverage, with additional tests scheduled for post-Wave 3.*

**Revised Lane 3.3:** 
- **MVP (50 tests):** Loaders (12) + Transforms (8) + Preprocessing (8) + Sampling (8) + Validation (8) + Integration (6) = 50 tests, 53-60 hours
- **Extended (70 tests):** Add 10 integration + 10 additional edge cases/performance tests (60-70 hours)

### Success Criteria for Lane 3.3

- ✅ 50-70 tests implemented, 100% pass rate
- ✅ Data pipeline coverage: 60-80%
- ✅ All loaders tested with real and synthetic data
- ✅ Augmentation/preprocessing transforms fully covered
- ✅ Error handling validated for corrupt data

---

## Parallel Lane Coordination

### Resource Allocation

| Resource | Lane 3.1 | Lane 3.2 | Lane 3.3 | Coordination |
|----------|----------|----------|----------|--------------|
| Agent | unified-coverage-agent | unified-coverage-agent | unified-coverage-agent | agent-orchestrator (optional) |
| Commits | 3-4 PRs | 2-3 PRs | 4-5 PRs | Weekly sync PR |
| CI/CD | Standard (90 min) | Standard (90 min) | Extended (120 min) | Parallel workflows |
| Reviews | 1 reviewer | 1 reviewer | 1 reviewer | Async reviews accepted |

### Timeline & Milestones

```
Lane 3.1: ════════════════════════════════════════════════════════════════════ (53 hours)
Lane 3.2: ════════════════════════════════════════════════════════ (48 hours)
Lane 3.3: ════════════════════════════════════════════════════════════════════════════════ (67 hours)
          |------Week 1------|------Week 2------|------Week 3------|------Future------|
```

**Staggered Start Option:** If CI resource constraints detected, stagger lane starts:
- T+0: Lane 3.2 (fastest, 48h) - CLI tests have fewest dependencies
- T+12h: Lane 3.1 (53h) - Training tests can run independently
- T+24h: Lane 3.3 (67h) - Data pipeline can start after dependency check

---

## Success Criteria (Overall Wave 3)

- ✅ All 3 lanes completed with 160 total tests
- ✅ Each lane ≥70% coverage verified
- ✅ 100% test pass rate across all lanes
- ✅ No regression in Phase 6 Wave 1 baseline (79 tests still passing)
- ✅ Overall repository coverage improved by +3-5% points
- ✅ Per-lane metrics documented and committed
- ✅ Cross-lane integration tests where applicable

---

## Dependencies & Preconditions

**Phase 6 Prerequisites:**
- Stage 4 completion: 79 TIER-1 tests implemented, all passing ✅
- ML modules stabilized and functional ✅

**External Dependencies:**
- pytest fixtures from conftest.py
- ML model artifacts (pre-trained weights if needed)
- Sample data for loaders (CSV, JSON, image samples)
- Pandas, NumPy, PyTorch (or equiv.) installed

**Phase 3-5 Reference Data:**
- Coverage baseline from Phase 5 ML analysis ✅
- TIER-2 module specifications available ✅

---

## Constraints & Risks

| Risk | Severity | Mitigation |
|------|----------|-----------|
| Slow test execution (ML tests expensive) | HIGH | Use fixtures with cached models; mock external data; mark expensive tests with @pytest.mark.slow |
| Merge conflicts (3 parallel lanes) | MEDIUM | Stagger PRs by 1-2 days; coordinate via dashboard |
| Coverage ceiling (asymptotic diminishing returns) | MEDIUM | Target 70-80%, accept 70%+ as acceptable; don't over-test |
| GPU resource constraints (if testing CUDA) | MEDIUM | Use CPU-only mode for CI; add optional GPU tests for local |
| Interaction with Wave 2 duplication extraction | MEDIUM | Coordinate on shared ML modules; Wave 2 can extract common test fixtures |

---

## Dispatch Options

### Option A: Full Parallel (Recommended)
- All 3 lanes execute simultaneously
- Risk: Medium (CI queue backup possible)
- Timeline: 67 hours (3 days + buffer)
- Recommended approach for @mbaetiong's timeline

### Option B: Sequential (Conservative)
- Lanes executed one at a time (1-2 days each)
- Risk: Low (minimal CI contention)
- Timeline: 10-12 days
- Not recommended (extends Wave 3 timeline)

### Option C: Staggered Parallel (Recommended)
- Lane 3.2 starts first (48h, fastest)
- Lane 3.1 starts after 12h (53h)
- Lane 3.3 starts after 24h (67h)
- Risk: Low (distributed CI load)
- Timeline: 72-80 hours (4 days) with buffer
- Recommended for sustained CI throughput

**Recommended Approach:** Option C (Staggered Parallel)

---

## Agent Instructions

### Pre-Dispatch Checklist

- [x] Authority verified: @mbaetiong pre-approved Wave 3
- [x] Lane specifications complete and documented
- [x] Test templates and fixtures prepared
- [x] CI/CD pipelines configured for parallel execution
- [x] Communication channels active (dashboard)

### Dispatch Command

```bash
@copilot-assignment
Agent: unified-coverage-agent
Brief: AGENT_BRIEF_STAGE_5_WAVE3_COVERAGE.md
Authority: @mbaetiong (Autonomous GO CONTINUE)
Mode: Parallel lanes (3 concurrent, staggered start recommended)
Lanes:
  - Lane 3.1: ML Training Pipeline (50 tests, 53 hours)
  - Lane 3.2: ML CLI Interface (40 tests, 48 hours)
  - Lane 3.3: ML Data Pipeline (50-70 tests, 53-67 hours)
Coordination: PHASE_6_WAVE2_COORDINATION_DASHBOARD.md

PROCEED WITH PARALLEL COVERAGE REMEDIATION
```

---

## Output Artifacts

**Commits (per lane, grouped into 1-2 PRs):**
- Format: `feat(coverage): Lane 3.X — <component> coverage to 70%+ (<N> tests)`
- Example: `feat(coverage): Lane 3.1 — ML training pipeline coverage to 74% (50 tests, 53h)`

**PRs:**
- 1 PR per lane (or 1 combined PR if preferred)
- All tests passing (100% pass rate)
- Coverage metrics attached (per-file breakdown)
- Cross-lane sync PR at end (consolidate metrics)

**Documentation:**
- Per-lane report: `.codex/WAVE_3_LANE_3X_COMPLETION_REPORT.md`
- Coverage dashboard: `.codex/WAVE_3_COVERAGE_METRICS.json`
- Final report: `.codex/PHASE_6_WAVE_3_FINAL_REPORT.md`

---

**Coordinating Authority:** @mbaetiong  
**Autonomous Mode:** GO CONTINUE (all decision points approved)  
**Parallel Dispatch:** YES (3 lanes concurrent; coordinate via dashboard)  
**Escalation Path:** Direct to @mbaetiong or agent-orchestrator
