# PHASE 10 POST-RELEASE: API Interface Fixes - Execution Plan

**Status**: Groundwork Complete → Execution Phase Commencing  
**Start Time**: 2026-07-17 19:50 UTC  
**Target Completion**: 2026-07-20 14:00 UTC (estimated)

## Execution Sequence

### Fix #1: WorkflowParser Module Consolidation (Priority 1 - BLOCKING)
**Status**: Starting NOW  
**Estimated Time**: 2 hours  
**Risk**: LOW (module relocation, no behavior change)

**Steps**:
1. Move `./services/workflow/parser.py` → `./mutants/services/workflow/parser.py`
2. Move `./services/workflow/types.py` → `./mutants/services/workflow/types.py`
3. Move `./services/workflow/inventory.py` → `./mutants/services/workflow/inventory.py`
4. Update test imports from `services.workflow` → `src.services.workflow`
5. Verify all 60 tests in test_parser_comprehensive.py PASS
6. Check test_inventory.py tests PASS

**Blocked By**: None  
**Blocks**: Fix #2, #3, #4, #5, #7, #8, #9

---

### Fix #2: SessionDB Query Methods (Priority 2 - BLOCKING)
**Status**: Waiting for #1  
**Estimated Time**: 1 hour  
**Risk**: LOW (new methods, backward compatible)

**Methods to Add**:
- `query_all() -> list[dict]`
- `query_by_pr_number(pr_number: int) -> list[dict]`
- `query_by_branch(branch: str) -> list[dict]`
- `query_by_agent_name(agent_name: str) -> list[dict]`
- `query_sessions(filters: dict, limit: int, offset: int) -> list[dict]`

**Verify**: test_session_db.py tests PASS, test_codex_e2e_comprehensive.py tests PASS

**Blocked By**: #1  
**Blocks**: #6, #7

---

### Fix #3: WorkflowRun Constructor Parameter Mapping (Priority 3)
**Status**: Waiting for #1  
**Estimated Time**: 3 hours  
**Risk**: MEDIUM (type changes, validation logic)

**Steps**:
1. Choose primary WorkflowRun: `services.github.types.WorkflowRun`
2. Create adapter/converter from dict to proper types
3. Update `services.workflow.parser.parse_workflow_run()` to use converters
4. Ensure enum fields properly converted (RunStatus, RunConclusion)

**Verify**: Constructor tests PASS

**Blocked By**: #1  
**Blocks**: #5, #9

---

### Fix #4: WorkflowRun Type Consistency (Priority 4)
**Status**: Waiting for #3  
**Estimated Time**: 2 hours  
**Risk**: MEDIUM (dataclass to Pydantic conversion)

**Steps**:
1. Convert `aries_serpent_core.cognitive.workflow_optimizer.WorkflowRun` to Pydantic
2. Add field mapping for `run_id` → `id`, `workflow_name` → `name`
3. Support JSON serialization/deserialization
4. Create conversion from github.types.WorkflowRun

**Verify**: workflow_optimizer tests PASS

**Blocked By**: #3  
**Blocks**: None (supporting role)

---

### Fix #5: WorkflowRun Enum Field Requirements (Priority 5)
**Status**: Waiting for #3  
**Estimated Time**: 1 hour  
**Risk**: LOW (enum conversion, straightforward)

**Steps**:
1. Update parser to convert string status → RunStatus enum
2. Update parser to convert string conclusion → RunConclusion enum
3. Add validation for valid enum values
4. Handle None cases

**Verify**: GitHub integration tests PASS

**Blocked By**: #3  
**Blocks**: None

---

### Fix #6: SessionDB Archive Query API (Priority 6)
**Status**: Waiting for #2  
**Estimated Time**: 2 hours  
**Risk**: LOW (new methods, archive-specific)

**Methods to Add**:
- `query_archived_sessions(filters: dict, limit: int, offset: int) -> list[dict]`
- `query_by_archive_date_range(start: datetime, end: datetime) -> list[dict]`
- `get_archive_stats(detailed: bool = False) -> dict`

**Verify**: Archive tests PASS

**Blocked By**: #2  
**Blocks**: None

---

### Fix #7: WorkflowInput Enum Standardization (Priority 7)
**Status**: Waiting for #1  
**Estimated Time**: 1 hour  
**Risk**: LOW (enum replacement, backward compatible)

**Steps**:
1. Replace root `InputType` class with enum from src/
2. Update parser to use correct enum
3. Update type hints in WorkflowInput

**Verify**: Workflow parsing tests PASS

**Blocked By**: #1  
**Blocks**: None

---

### Fix #8: WorkflowJob Alias Field Collision (Priority 8)
**Status**: Waiting for #1  
**Estimated Time**: 0.5 hours  
**Risk**: LOW (Pydantic config fix)

**Steps**:
1. Update WorkflowJob.Config for Pydantic v2 compatibility
2. Verify `if` alias works with `populate_by_name`
3. Test model creation from dict with "if" key

**Verify**: Job creation tests PASS

**Blocked By**: #1  
**Blocks**: None

---

### Fix #9: parse_file Cache Handling (Priority 9)
**Status**: Waiting for #1  
**Estimated Time**: 1 hour  
**Risk**: LOW (cache consistency)

**Steps**:
1. Verify cache stores/retrieves compatible types
2. Add type validation on cache hit
3. Clear cache on incompatible types
4. Add cache statistics tracking

**Verify**: Parser cache tests PASS

**Blocked By**: #1  
**Blocks**: None

---

## Progress Tracking

| Fix | Status | Time Spent | Est. Remaining | Completion % |
|-----|--------|-----------|-----------------|--------------|
| #1 | STARTING | 0m | 2h | 0% |
| #2 | PENDING | 0m | 1h | 0% |
| #3 | PENDING | 0m | 3h | 0% |
| #4 | PENDING | 0m | 2h | 0% |
| #5 | PENDING | 0m | 1h | 0% |
| #6 | PENDING | 0m | 2h | 0% |
| #7 | PENDING | 0m | 1h | 0% |
| #8 | PENDING | 0m | 0.5h | 0% |
| #9 | PENDING | 0m | 1h | 0% |
| **TOTAL** | | **0m** | **14h** | **0%** |

---

## Execution Notes

- Updates will be made in-place with atomic commits
- Each fix will be tested immediately after application
- No rollbacks unless test suite fails
- Full regression test run after all 9 fixes complete

---

## Success Criteria (Execution Complete)

- [ ] All 9 mismatches fixed
- [ ] test_parser_comprehensive.py: 60/60 PASS (currently 1/60)
- [ ] test_session_db.py: 100% PASS
- [ ] test_codex_e2e_comprehensive.py: 100% PASS
- [ ] Phase 7a integration tests: 95%+ PASS (currently ~60%)
- [ ] Phase 4-6 tests: 100% PASS (no regressions)
- [ ] Zero new test failures introduced
- [ ] Full groundwork + execution report generated

---

**Next**: Begin Fix #1 - WorkflowParser Module Consolidation
