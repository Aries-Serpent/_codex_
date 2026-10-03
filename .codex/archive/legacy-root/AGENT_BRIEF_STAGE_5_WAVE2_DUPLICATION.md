# Agent Brief: Wave 2 - Duplication Extraction Campaign

**Target Agent:** duplication-extraction-agent  
**Authority:** @mbaetiong (Autonomous GO CONTINUE)  
**Timeline:** 4-6 weeks  
**Scope:** 15 TIER-1 patterns, 9,561+ LOC reduction  
**Status:** READY FOR DISPATCH  
**Coordinating Brief:** AGENT_BRIEF_STAGE_5_WAVE2_DELEGATION.md (Stage 5, Phase 6 Wave 1)

---

## Mission

Extract and consolidate 15 high-impact code duplication patterns identified in Phase 4 Lane 4 analysis. Target reduction: 9,561+ lines of duplicated code across core modules (utils, ML, cognitive, workflows, testing).

---

## Executive Summary

Phase 4 Lane 4 identified 15 TIER-1 duplication patterns across the codebase:
- **Pattern Density:** 9,561+ lines of redundant/duplicated code
- **Impact:** Code maintainability (HIGH), test complexity (MEDIUM), build efficiency (LOW)
- **Complexity:** 3-5 hour extraction per pattern (mid-tier patterns: 4-8 hours each)
- **Risk:** MEDIUM (refactoring in utility layers; affects multiple consumers)

---

## Patterns to Address (15 TIER-1)

### Tier 1a: Low-Risk Consolidations (Weeks 1-2)

1. **Pattern LRC-001: Duplicate import/re-export chains**
   - Modules: `src/codex/utils/__init__.py` (3 variants), `src/codex/ml/__init__.py` (2 variants)
   - LOC reduction: 240
   - Action: Consolidate __all__ exports, create single import hub

2. **Pattern LRC-002: Duplicate validation decorators**
   - Modules: validation layers (3 implementations), security module (2 implementations)
   - LOC reduction: 180
   - Action: Extract @validate, @require_auth to centralized decorators.py

3. **Pattern LRC-003: Error handling wrappers**
   - Modules: CLI (2 implementations), API (2 implementations), async utils (1 variant)
   - LOC reduction: 320
   - Action: Centralize error wrapping in codex.errors.handlers

### Tier 1b: Mid-Complexity Refactorings (Weeks 2-3)

4. **Pattern MRC-001: Test fixture boilerplate**
   - Modules: tests/conftest.py, tests/unit/, tests/integration/ (5 near-duplicates)
   - LOC reduction: 480
   - Action: Extract pytest plugin with shared fixtures

5. **Pattern MRC-002: Configuration parsing templates**
   - Modules: codex_ml (2), configs module (2), CLI (1)
   - LOC reduction: 420
   - Action: Create ConfigParser base class

6. **Pattern MRC-003: Mock/stub object factories**
   - Modules: tests/ (8 implementations of _FakeModel, _MockClient variants)
   - LOC reduction: 560
   - Action: Centralize in tests/mocks/factories.py

7. **Pattern MRC-004: Logging setup patterns**
   - Modules: CLI (3), ML training (2), async runtime (1)
   - LOC reduction: 340
   - Action: Extract logging.bootstrap() utility

8. **Pattern MRC-005: Async context manager templates**
   - Modules: async utils (2), database layer (2), cache ops (1)
   - LOC reduction: 380
   - Action: Create async_contextmanager helper suite

### Tier 1c: High-Complexity Consolidations (Weeks 3-4)

9. **Pattern HRC-001: ML pipeline builder patterns**
   - Modules: ml_training (3), RAG pipeline (2), CLI transformer (1)
   - LOC reduction: 920
   - Action: Create PipelineBuilder abstract base + concrete implementations

10. **Pattern HRC-002: Data validation chains**
    - Modules: data_pipeline (3), security.schema (2), RAG ingestion (1)
    - LOC reduction: 780
    - Action: Extract ValidationChain builder pattern

11. **Pattern HRC-003: Bridge communication protocols**
    - Modules: bridge/ipc (2), bridge/http (2), bridge/websocket (1)
    - LOC reduction: 640
    - Action: Extract BridgeProtocol base class + codec builders

12. **Pattern HRC-004: Cognitive brain request/response handlers**
    - Modules: cognitive_brain/handlers (3), cognitive/api (2)
    - LOC reduction: 850
    - Action: Create RequestHandler + ResponseBuilder base classes

13. **Pattern HRC-005: Cache key generation patterns**
    - Modules: cache/keys (2), ml_training/caching (2), RAG/embedding_cache (1)
    - LOC reduction: 490
    - Action: Extract CacheKeyGenerator builder

### Tier 1d: Integration Testing & Stabilization (Weeks 4-6)

14. **Pattern SRC-001: Cross-module integration tests**
    - Modules: tests/integration (5 duplicated test harnesses)
    - LOC reduction: 520
    - Action: Create IntegrationTestHarness base class + registry

15. **Pattern SRC-002: Regression test templates**
    - Modules: tests/regression (4 duplicated baseline comparisons)
    - LOC reduction: 560
    - Action: Extract RegressionTestRunner + baseline manager

---

## Timeline & Milestones

| Week | Patterns | Estimated Hours | Status | Approval Gate |
|------|----------|-----------------|--------|---------------|
| 1 | LRC-001, LRC-002, LRC-003 | 18-22 | ⏳ PENDING | Code review + test pass rate |
| 2 | MRC-001, MRC-002, MRC-003 | 22-26 | ⏳ PENDING | Code review + regression test |
| 3 | MRC-004, MRC-005, HRC-001 | 24-28 | ⏳ PENDING | Code review + integration test |
| 4 | HRC-002, HRC-003, HRC-004, HRC-005 | 26-30 | ⏳ PENDING | Code review + security audit |
| 5-6 | SRC-001, SRC-002 + integration & stabilization | 30-35 | ⏳ PENDING | Final regression + metrics |

---

## Success Criteria

- ✅ All 15 patterns extracted with 100% functionality preservation
- ✅ 9,561+ LOC verified reduced
- ✅ All existing tests continue to pass (100% regression test pass rate)
- ✅ Coverage maintained ≥70% (per Phase 6 Wave 1 baseline)
- ✅ Refactoring commits follow pattern-by-pattern traceability (1 commit per pattern)
- ✅ Pattern documentation (README per consolidation) created
- ✅ Cross-module consumers updated without breaking changes
- ✅ Performance benchmarks unchanged (within ±3% tolerance)

---

## Dependencies & Preconditions

**Phase 6 Prerequisites:**
- Stage 4 completion: 79 TIER-1 tests implemented, all passing ✅
- Phase 4 Lane 4 duplication analysis committed ✅

**External Dependencies:**
- `rope` library for Python refactoring (add to dev dependencies if missing)
- Code review capacity (1 reviewer per pattern, async reviews acceptable)
- Regression test suite available (`nox -s tests`)

---

## Constraints & Risks

| Risk | Severity | Mitigation |
|------|----------|-----------|
| Breaking changes to public APIs | HIGH | Maintain backward compatibility wrappers; deprecation warnings before removal |
| Test fragility after consolidation | HIGH | Run full regression suite after each pattern; update mocks systematically |
| Cross-module ripple effects | MEDIUM | PR reviews with @mbaetiong for patterns 9-15; limited parallel extraction |
| Performance regression in hot paths | MEDIUM | Benchmark before/after for HRC patterns; alert on >5% regression |
| Merge conflicts with concurrent waves | MEDIUM | Coordinate with Wave 3-5 agents on overlapping modules (ML, cache, etc.) |

---

## Dispatch Options

### Option A: Full Parallel (Recommended)
- All 15 patterns extracted in parallel
- Risk: High merge conflict probability with Wave 3-5
- Timeline: 4 weeks (weeks 1-4 overlapping)
- Resources: Single duplication-extraction-agent

### Option B: Sequential (Conservative)
- Patterns extracted 2-3 at a time, weekly batch
- Risk: Low merge conflict probability
- Timeline: 6 weeks (sequential)
- Resources: Single agent throughout

### Option C: Staged Parallel (Recommended for Wave 2-5 coordination)
- Week 1-2: LRC patterns (low-risk) parallel
- Week 3-4: MRC patterns after LRC stabilization
- Week 4-5: HRC patterns (coordinate with Wave 3 coverage lane 3.3 if overlapping)
- Week 5-6: SRC patterns (tests) parallel with Wave 4 mypy
- Timeline: 4-6 weeks with managed parallelization
- Resources: Single agent with cross-wave coordination

**Recommended Approach:** Option C (Staged Parallel)

---

## Feedback Loops & Escalation

**Daily Checkpoint (UTC):**
- Agent reports pattern completion status in #wave-2-status Slack channel
- Blockers escalated immediately to @mbaetiong

**Weekly Review (Every Friday):**
- 2-3 patterns completed + metrics collected
- Coverage impact verified
- Merge conflict assessment for concurrent waves
- Rescheduling if needed

**Escalation Triggers:**
- Regression test failure rate >10%: Stop pattern extraction, investigate, escalate
- Performance regression >5%: Escalate to cache-management-agent (Wave 5)
- Breaking API changes: Escalate to @mbaetiong for decision
- Merge conflicts with Wave 3-5: Invoke agent-orchestrator conflict resolution

---

## Agent Instructions

### Pre-Dispatch Checklist

- [x] Authority verified: @mbaetiong pre-approved all patterns
- [x] Prerequisites met: Phase 4 Lane 4 analysis available
- [x] Tools available: rope (or equivalent), git, test suite
- [x] Communication channel: Wave 2-5 coordination dashboard active

### Dispatch Command

```bash
@copilot-assignment
Agent: duplication-extraction-agent
Brief: AGENT_BRIEF_STAGE_5_WAVE2_DUPLICATION.md
Authority: @mbaetiong (Autonomous GO CONTINUE)
Mode: Staged parallel (Option C recommended)
Coordination: PHASE_6_WAVE2_COORDINATION_DASHBOARD.md

PROCEED WITH PATTERN EXTRACTION
```

---

## Output Artifacts

**Commits (per pattern):**
- Commit message format: `feat(duplication): extract LRC-XXX pattern — <description>`
- Example: `feat(duplication): extract LRC-001 import/reexport consolidation — reduce __init__.py variants from 5 to 1 (240 LOC)`

**PR Requirements:**
- 1 PR per wave segment (Week 1-2 = 1 PR, Week 3-4 = 1 PR, etc.)
- All tests passing (100% pass rate)
- Code review approval required
- Regression metrics attached to PR description

**Documentation:**
- Per-pattern README in `.codex/duplication_extraction_patterns/LRC-001_PATTERN.md`
- Weekly report: `.codex/WAVE_2_WEEK_N_COMPLETION_REPORT.md`
- Final report: `.codex/PHASE_6_WAVE_2_FINAL_REPORT.md`

---

**Coordinating Authority:** @mbaetiong  
**Autonomous Mode:** GO CONTINUE (all decision points approved)  
**Parallel Dispatch:** YES (with Waves 3-5; coordinate via dashboard)  
**Escalation Path:** Direct to @mbaetiong or agent-orchestrator
