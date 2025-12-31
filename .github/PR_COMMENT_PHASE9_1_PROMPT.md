# Phase 9.1 Continuation Prompt for PR #2668

**TO BE POSTED AS PR COMMENT BY HUMAN ADMIN**

**Format**: Post the content below as a comment on PR #2668
**First Line Must Be**: @copilot (with no spaces or formatting)

---

@copilot Execute Phase 9.1 - Critical Path Coverage (75% → 85%)

**Context**: This is Phase 9.1 of the 100% test coverage roadmap. Read `.github/COPILOT_AGENT_PHASE9_1_PROMPT.md` for complete execution details.

**Objective**: Add 150-200 new tests to achieve 85% coverage (currently 75%)

## Prerequisites - Read First

1. `.github/COPILOT_AGENT_PHASE9_1_PROMPT.md` - Complete 21KB execution guide
2. `.github/COGNITIVE_BRAIN_STATUS_UPDATE.md` - Comprehensive status (18KB)
3. `docs/system/CODEBASE_DASHBOARD.md` - Live metrics
4. `docs/testing/COVERAGE_100_ROADMAP.md` - Full Phase 9 plan

## Execution Plan

### Step 1: Baseline Coverage (10 min)
```bash
cd /home/runner/work/_codex_/_codex_
pytest tests/ --cov=src --cov=agents --cov=scripts --cov-report=term-missing > baseline_coverage.txt
pytest tests/ --cov=src --cov=agents --cov=scripts --cov-report=html
# Review htmlcov/index.html for red (uncovered) lines
```

### Step 2: Codex Pipeline Tests (40-60 min, 40-50 tests)
Create and implement:
- `tests/codex/test_ingest_phase9_1.py` (15-20 tests)
  - File formats: .py, .zip, .tar.gz, invalid encodings
  - Git repo ingestion, URL-based ingestion
  - Error handling: empty files, binary files, large files
  
- `tests/codex/test_analyze_phase9_1.py` (10-15 tests)
  - Static analysis, runtime analysis with AST
  - LLM intent inference (mock OpenAI API)
  - Analysis aggregation, error recovery
  
- `tests/codex/test_transform_phase9_1.py` (10-15 tests)
  - Tier A/B/C transformations
  - Validation, rollback mechanisms
  - Conflicting transformations edge cases
  
- `tests/codex/test_verify_phase9_1.py` (5-10 tests)
  - Behavior verification, diff validation
  - Performance regression detection
  - Timeout and resource exhaustion handling

Run: `pytest tests/codex/test_*_phase9_1.py -v`

### Step 3: Agent System Tests (40-60 min, 30-40 tests)
Create and implement:
- `tests/agents/test_workflow_navigator_phase9_1.py` (10-15 tests)
  - create_workflow(), get_workflow(), state transitions
  - Token execution (AUDIT_EXEC, DOC_GEN, etc.)
  - Error handling: invalid IDs, missing steps, circular workflows
  
- `tests/agents/test_quantum_game_theory_phase9_1.py` (8-10 tests)
  - Strategy selection, coherence calculation
  - Nash equilibrium, quantum decisions
  - Edge cases: zero-sum games, ties
  
- `tests/agents/test_physics_orchestrator_phase9_1.py` (8-10 tests)
  - 6 paradigm integration (chaos, fractal, fluid, EM, wave, relativity)
  - Cross-paradigm coordination, parameter optimization
  - Error handling, extreme parameter values
  
- `tests/agents/test_mental_mapping_phase9_1.py` (4-8 tests)
  - Context tracking, state persistence
  - Memory management, context retrieval
  - Memory overflow, corrupted state

Run: `pytest tests/agents/test_*_phase9_1.py -v`

### Step 4: MCP System Tests (30-40 min, 20-30 tests)
Create and implement:
- `tests/scripts/mcp/test_component_selection_phase9_1.py` (8-10 tests)
  - Topic-based selection (all 9 topics)
  - Custom patterns, glob handling
  - Error handling: invalid topic, no matches
  
- `tests/scripts/mcp/test_file_flattening_phase9_1.py` (5-8 tests)
  - Path flattening algorithm
  - Name collision detection, special characters
  - Max filename length, deeply nested paths
  
- `tests/scripts/mcp/test_manifest_generation_phase9_1.py` (5-8 tests)
  - Manifest structure validation
  - Metadata accuracy (SHA256, sizes, language)
  - Original path mapping, large manifests
  
- `tests/scripts/mcp/test_archive_creation_phase9_1.py` (2-4 tests)
  - ZIP creation, validation, compression
  - Error handling: write errors, disk space

Run: `pytest tests/scripts/mcp/ -v`

### Step 5: Integration Tests (30-40 min, 20-30 tests)
Create directory: `mkdir -p tests/integration`

Create and implement:
- `tests/integration/test_codex_pipeline_e2e_phase9_1.py` (8-12 tests)
  - Complete pipeline: ingest → analyze → transform → verify
  - Error recovery across components
  - Partial failures, retry scenarios
  
- `tests/integration/test_mcp_workflow_e2e_phase9_1.py` (4-6 tests)
  - Topic-based packaging end-to-end
  - Custom workflows, validation
  - Package size limits, invalid inputs
  
- `tests/integration/test_agent_coordination_phase9_1.py` (5-8 tests)
  - Multi-agent workflows, handoff and state transfer
  - Coordination protocols, deadlock prevention
  - Agent failures, communication errors
  
- `tests/integration/test_state_management_phase9_1.py` (3-4 tests)
  - State persistence across sessions
  - Recovery after failures, migration
  - Corrupted state, missing files

Run: `pytest tests/integration/ -v --timeout=120`

### Step 6: Coverage Validation (10-15 min)
```bash
pytest tests/ -v
pytest tests/ --cov=src --cov=agents --cov=scripts --cov-report=term-missing > final_coverage.txt

echo "=== BASELINE ===" && cat baseline_coverage.txt | grep "TOTAL"
echo "=== FINAL ===" && cat final_coverage.txt | grep "TOTAL"

pytest tests/ --cov=src --cov=agents --cov=scripts --cov-report=html
echo "Open htmlcov/index.html to see coverage details"
```

### Step 7: Documentation Update (10-15 min)
Update:
- `docs/system/CODEBASE_DASHBOARD.md` - Test count, coverage percentage
- `docs/testing/COVERAGE_100_ROADMAP.md` - Phase 9.1 status
- Create `docs/testing/PHASE9_1_TEST_SUMMARY.md` - Detailed summary

## Testing Patterns

**Use AAA Pattern:**
```python
def test_example():
    """Test description."""
    # Arrange - Setup
    input_data = create_test_data()
    
    # Act - Execute
    result = function_under_test(input_data)
    
    # Assert - Verify
    assert result.status == "success"
```

**Parametrize where appropriate:**
```python
@pytest.mark.parametrize("input_file,expected", [
    ("valid.py", "success"),
    ("invalid.txt", "error"),
])
def test_various_inputs(input_file, expected):
    result = process(input_file)
    assert result.status == expected
```

**Mock external dependencies:**
```python
@patch('openai.ChatCompletion.create')
def test_with_mock(mock_openai):
    mock_openai.return_value = {'choices': [{'message': {'content': 'result'}}]}
    result = infer_intent("code")
    assert result == "result"
```

## 5-Pass Self-Review (MANDATORY)

After completing tests, perform 5 comprehensive self-review passes:

**Pass 1: Code Quality** - Docstrings, naming, AAA pattern, no lint warnings
**Pass 2: Coverage** - Target reached (85% ±2%), edge cases covered
**Pass 3: Reliability** - All tests pass consistently, no flaky tests, fast execution
**Pass 4: Documentation** - Clear purpose, coverage reports, dashboard updated
**Pass 5: Integration** - No regressions (1615+ tests pass), no security issues

**DO NOT PROCEED until all 5 passes show 0 concerns.**

## Success Criteria

✅ Coverage: 85% ±2% (83%-87%)
✅ Test Count: 1765-1815 tests (1615 + 150-200)
✅ Pass Rate: 100% (all tests passing)
✅ No Regressions: All existing tests still pass
✅ Documentation: All required docs updated
✅ Self-Review: 5 passes complete, 0 concerns

## If Token Budget Low

1. Prioritize critical path tests (Codex, Agents)
2. Document remaining work
3. Commit progress: `git add tests/ docs/ && git commit -m "feat(tests): Phase 9.1 progress - [N] tests added"`
4. Create continuation prompt for next session
5. Post as PR comment starting with @copilot

## Completion Steps

1. Run final validation: `pytest tests/ -v --cov=src --cov=agents --cov=scripts`
2. Update documentation (Dashboard, Roadmap, Test Summary)
3. Commit: `git commit -m "feat(tests): Phase 9.1 complete - 85% coverage achieved"`
4. Create Phase 9.2 continuation prompt
5. Post Phase 9.2 prompt as PR comment starting with @copilot
6. Verify prompt posted successfully

## PDA Loop & AfterMath Tags

**Apply throughout execution:**
- Use Perception-Decision-Action loop for each major step
- Tag insights with #AFTERMATH_* tags
- Document lessons learned
- Create session report at completion

**AfterMath Tags to Use:**
- #AFTERMATH_DECISION - Major decisions
- #AFTERMATH_LESSON_LEARNED - Insights gained
- #AFTERMATH_QUALITY_CHECK - Quality validations
- #AFTERMATH_METRIC - Measurements
- #AFTERMATH_BLOCKER_RESOLVED - Issues overcome
- #AFTERMATH_PATTERN_IDENTIFIED - Recurring patterns
- #AFTERMATH_NEXT_STEPS - Continuation actions

## References

- Full execution guide: `.github/COPILOT_AGENT_PHASE9_1_PROMPT.md` (21KB)
- Status update: `.github/COGNITIVE_BRAIN_STATUS_UPDATE.md` (18KB)
- AfterMath example: `.github/AFTERMATH_PR2668_SESSION_REPORT.md` (10KB)
- Dashboard: `docs/system/CODEBASE_DASHBOARD.md`
- Cognitive map: `docs/system/CODEBASE_COGNITIVE_MAP.md`

**Timeline**: 1-2 sessions (~200K-400K tokens)
**Focus**: Quality over speed - thoroughness is critical

Good luck! 🚀
