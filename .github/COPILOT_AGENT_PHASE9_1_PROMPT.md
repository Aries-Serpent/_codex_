# GitHub Copilot Agent Execution Prompt: Phase 9.1 - Critical Path Coverage

**Target**: Achieve 85% test coverage (currently 75%)  
**Session Goal**: Add 150-200 new tests, all passing  
**Timeline**: Complete within 1-2 sessions (~200K-400K tokens)  
**Context**: Part of Phase 9 roadmap to reach 100% coverage

---

## 📋 Prerequisites - Read These First

Before starting, review these documents to understand context:

1. **`.github/COGNITIVE_BRAIN_STATUS_UPDATE.md`** - Comprehensive status and scope
2. **`docs/system/CODEBASE_DASHBOARD.md`** - Live status dashboard
3. **`docs/system/CODEBASE_COGNITIVE_MAP.md`** - Architecture overview
4. **`docs/testing/COVERAGE_100_ROADMAP.md`** - Full Phase 9 plan
5. **`docs/testing/PHASE9_1_EXECUTION_PLAN.md`** - Phase 9.1 details (if exists)

---

## 🎯 Mission Objectives

### Primary Goal
Add **150-200 new tests** to achieve **85% coverage** (from current 75%)

### Success Criteria
- ✅ All new tests pass (100% pass rate maintained)
- ✅ Coverage increased from 75% to 85% (±2%)
- ✅ No regressions in existing tests (1615 tests remain passing)
- ✅ All tests follow established patterns and conventions
- ✅ Test documentation updated

### Quality Standards
- Use existing test patterns from `tests/` directory
- Follow pytest conventions and fixtures
- Include docstrings explaining test purpose
- Use property-based testing where appropriate (Hypothesis)
- Mock external dependencies appropriately
- Ensure deterministic test behavior

---

## 📊 Phase 9.1 Execution Plan

### Test Distribution (150-200 tests total)

#### 1. Codex Pipeline Tests (40-50 tests)
**Path**: `tests/codex/`  
**Coverage Target**: Core ingestion workflow

**Test Categories**:

**A. Ingest Module** (15-20 tests)
- File format handling (`.py`, `.zip`, `.tar.gz`)
- Git repository ingestion
- URL-based ingestion
- Error handling for invalid inputs
- Large file handling
- Edge cases: empty files, binary files, encoding issues

**B. Analyze Module** (10-15 tests)
- Static analysis execution
- Runtime analysis with AST
- LLM intent inference (mock OpenAI API)
- Analysis result aggregation
- Error recovery in analysis
- Edge cases: syntax errors, import errors

**C. Transform Module** (10-15 tests)
- Tier A transformations (simple refactoring)
- Tier B transformations (moderate complexity)
- Tier C transformations (complex restructuring)
- Transformation validation
- Rollback mechanisms
- Edge cases: conflicting transformations

**D. Verify Module** (5-10 tests)
- Behavior verification
- Diff validation
- Test execution validation
- Performance regression detection
- Edge cases: timeout, resource exhaustion

**Implementation Steps**:
```bash
# 1. Check current coverage for codex module
pytest tests/codex/ --cov=src/codex --cov-report=term-missing

# 2. Identify uncovered lines
pytest tests/codex/ --cov=src/codex --cov-report=html
# Open htmlcov/index.html to see red (uncovered) lines

# 3. Create test files following pattern:
# tests/codex/test_<module>_phase9_1.py

# 4. Run tests incrementally
pytest tests/codex/test_<module>_phase9_1.py -v

# 5. Verify coverage improvement
pytest tests/codex/ --cov=src/codex --cov-report=term
```

#### 2. Agent System Tests (30-40 tests)
**Path**: `tests/agents/`  
**Coverage Target**: Agent workflow and coordination

**Test Categories**:

**A. WorkflowNavigator** (10-15 tests)
- `create_workflow()` with various step configurations
- `get_workflow()` retrieval and state
- Workflow state transitions
- Token execution (AUDIT_EXEC, DOC_GEN, etc.)
- Navigation between steps
- Error handling: invalid workflow IDs, missing steps
- Edge cases: circular workflows, empty workflows

**B. Quantum Game Theory** (8-10 tests)
- Strategy selection algorithms
- Coherence calculation
- Nash equilibrium finding
- Quantum-inspired decision making
- State superposition handling
- Edge cases: zero-sum games, tie scenarios

**C. Physics Orchestrator** (8-10 tests)
- 6 paradigm integration (chaos, fractal, fluid, EM, wave, relativity)
- Cross-paradigm coordination
- Parameter optimization
- Resource allocation
- Error handling: computation errors, timeout
- Edge cases: extreme parameter values

**D. Mental Mapping** (4-8 tests)
- Context tracking
- State persistence
- Memory management
- Context retrieval
- Edge cases: memory overflow, corrupted state

**Implementation Steps**:
```bash
# 1. Check agent coverage
pytest tests/agents/ --cov=agents --cov-report=term-missing

# 2. Create test files
# tests/agents/test_workflow_navigator_phase9_1.py
# tests/agents/test_quantum_game_theory_phase9_1.py
# tests/agents/test_physics_orchestrator_phase9_1.py
# tests/agents/test_mental_mapping_phase9_1.py

# 3. Run incrementally
pytest tests/agents/test_workflow_navigator_phase9_1.py -v

# 4. Verify coverage
pytest tests/agents/ --cov=agents --cov-report=term
```

#### 3. MCP System Tests (20-30 tests)
**Path**: `tests/scripts/mcp/`  
**Coverage Target**: MCP packaging system

**Test Categories**:

**A. Component Selection** (8-10 tests)
- Topic-based selection (all 9 topics)
- Custom pattern selection
- Glob pattern handling
- File filtering and exclusion
- Error handling: invalid topic, no matches
- Edge cases: empty results, all files selected

**B. File Flattening** (5-8 tests)
- Path flattening algorithm
- Name collision detection and resolution
- Special character handling
- Max filename length handling
- Edge cases: deeply nested paths, unicode characters

**C. Manifest Generation** (5-8 tests)
- Manifest structure validation
- Metadata accuracy (SHA256, sizes, language)
- Original path mapping
- Navigation index generation
- Edge cases: large manifests, missing metadata

**D. Archive Creation** (2-4 tests)
- ZIP archive creation
- Archive validation
- Compression efficiency
- Error handling: write errors, disk space
- Edge cases: empty archives, very large archives

**Implementation Steps**:
```bash
# 1. Check MCP coverage
pytest tests/scripts/ --cov=scripts/mcp --cov-report=term-missing

# 2. Create test files
# tests/scripts/mcp/test_component_selection_phase9_1.py
# tests/scripts/mcp/test_file_flattening_phase9_1.py
# tests/scripts/mcp/test_manifest_generation_phase9_1.py
# tests/scripts/mcp/test_archive_creation_phase9_1.py

# 3. Run incrementally
pytest tests/scripts/mcp/ -v

# 4. Verify coverage
pytest tests/scripts/mcp/ --cov=scripts/mcp --cov-report=term
```

#### 4. Integration Tests (20-30 tests)
**Path**: `tests/integration/`  
**Coverage Target**: End-to-end workflows

**Test Categories**:

**A. End-to-End Workflows** (8-12 tests)
- Complete codex pipeline (ingest → analyze → transform → verify)
- MCP packaging workflow (select → flatten → manifest → archive)
- Agent workflow execution (create → execute → verify)
- CI/CD integration scenarios
- Error recovery across components
- Edge cases: partial failures, retry scenarios

**B. Agent Coordination** (5-8 tests)
- Multi-agent workflows
- Agent handoff and state transfer
- Coordination protocols
- Deadlock prevention
- Edge cases: agent failures, communication errors

**C. MCP Packaging Workflows** (4-6 tests)
- Topic-based packaging end-to-end
- Custom packaging workflows
- Validation and testing of packages
- Upload simulation (without actual upload)
- Edge cases: package size limits, invalid inputs

**D. State Management** (3-4 tests)
- State persistence across sessions
- State recovery after failures
- State migration and versioning
- Edge cases: corrupted state, missing state files

**Implementation Steps**:
```bash
# 1. Create integration test directory if needed
mkdir -p tests/integration

# 2. Create test files
# tests/integration/test_codex_pipeline_e2e_phase9_1.py
# tests/integration/test_mcp_workflow_e2e_phase9_1.py
# tests/integration/test_agent_coordination_phase9_1.py
# tests/integration/test_state_management_phase9_1.py

# 3. Run integration tests (Phase 5 be slower)
pytest tests/integration/ -v --timeout=60

# 4. Verify overall coverage
pytest tests/ --cov=src --cov=agents --cov=scripts/mcp --cov-report=term
```

---

## 🛠️ Implementation Strategy

### Step-by-Step Execution

**Step 1: Environment Setup & Baseline** (10 minutes)
```bash
cd /home/runner/work/_codex_/_codex_

# Check current coverage
pytest tests/ --cov=src --cov=agents --cov=scripts --cov-report=term-missing > baseline_coverage.txt

# Review baseline
cat baseline_coverage.txt | grep "TOTAL"

# Generate HTML report for detailed analysis
pytest tests/ --cov=src --cov=agents --cov=scripts --cov-report=html
```

**Step 2: Codex Pipeline Tests** (40-60 minutes)
```bash
# Create test file
touch tests/codex/test_ingest_phase9_1.py
touch tests/codex/test_analyze_phase9_1.py
touch tests/codex/test_transform_phase9_1.py
touch tests/codex/test_verify_phase9_1.py

# Implement tests following existing patterns
# Reference: tests/codex/test_*.py for patterns

# Run and verify
pytest tests/codex/test_*_phase9_1.py -v
```

**Step 3: Agent System Tests** (40-60 minutes)
```bash
# Create test files
touch tests/agents/test_workflow_navigator_phase9_1.py
touch tests/agents/test_quantum_game_theory_phase9_1.py
touch tests/agents/test_physics_orchestrator_phase9_1.py
touch tests/agents/test_mental_mapping_phase9_1.py

# Implement tests following existing patterns
# Reference: tests/agents/test_*.py for patterns

# Run and verify
pytest tests/agents/test_*_phase9_1.py -v
```

**Step 4: MCP System Tests** (30-40 minutes)
```bash
# Create test files
touch tests/scripts/mcp/test_component_selection_phase9_1.py
touch tests/scripts/mcp/test_file_flattening_phase9_1.py
touch tests/scripts/mcp/test_manifest_generation_phase9_1.py
touch tests/scripts/mcp/test_archive_creation_phase9_1.py

# Implement tests
# Reference: tests/scripts/test_mcp_select_components.py

# Run and verify
pytest tests/scripts/mcp/ -v
```

**Step 5: Integration Tests** (30-40 minutes)
```bash
# Create integration test directory
mkdir -p tests/integration

# Create test files
touch tests/integration/test_codex_pipeline_e2e_phase9_1.py
touch tests/integration/test_mcp_workflow_e2e_phase9_1.py
touch tests/integration/test_agent_coordination_phase9_1.py
touch tests/integration/test_state_management_phase9_1.py

# Implement tests
# Use longer timeouts for integration tests: @pytest.mark.timeout(60)

# Run and verify
pytest tests/integration/ -v --timeout=120
```

**Step 6: Coverage Validation** (10-15 minutes)
```bash
# Run full test suite
pytest tests/ -v

# Check coverage
pytest tests/ --cov=src --cov=agents --cov=scripts --cov-report=term-missing > final_coverage.txt

# Compare baseline vs final
echo "=== BASELINE ===" && cat baseline_coverage.txt | grep "TOTAL"
echo "=== FINAL ===" && cat final_coverage.txt | grep "TOTAL"

# Generate HTML report
pytest tests/ --cov=src --cov=agents --cov=scripts --cov-report=html
echo "Open htmlcov/index.html to see coverage details"
```

**Step 7: Documentation Update** (10-15 minutes)
```bash
# Update coverage metrics in documentation
# Files to update:
# - docs/system/CODEBASE_DASHBOARD.md
# - docs/testing/COVERAGE_100_ROADMAP.md
# - .github/COGNITIVE_BRAIN_STATUS_UPDATE.md

# Create test documentation
cat > docs/testing/PHASE9_1_TEST_SUMMARY.md << 'EOF'
# Phase 9.1 Test Summary

## Tests Added: [NUMBER]
## Coverage: [BASELINE]% → [FINAL]%
## All Tests Passing: [YES/NO]

### Test Breakdown
- Codex Pipeline: [NUMBER] tests
- Agent System: [NUMBER] tests
- MCP System: [NUMBER] tests
- Integration: [NUMBER] tests

### Coverage by Module
[Insert coverage table]

### Issues Found & Resolved
[List any issues discovered and how they were fixed]
EOF
```

---

## 🧪 Testing Patterns & Best Practices

### 1. Test File Naming Convention
```python
# Pattern: tests/<module>/test_<component>_phase9_1.py
# Example: tests/codex/test_ingest_phase9_1.py
```

### 2. Test Function Naming
```python
# Pattern: test_<component>_<scenario>_<expected_outcome>
def test_ingest_file_valid_python_file_success():
    """Test ingesting a valid Python file succeeds."""
    pass

def test_ingest_file_invalid_encoding_raises_error():
    """Test ingesting file with invalid encoding raises UnicodeDecodeError."""
    pass
```

### 3. Test Structure (AAA Pattern)
```python
def test_example():
    """Test description."""
    # Arrange - Setup test data and mocks
    input_data = create_test_data()
    mock_service = Mock()
    
    # Act - Execute the function under test
    result = function_under_test(input_data, mock_service)
    
    # Assert - Verify expected behavior
    assert result.status == "success"
    mock_service.method.assert_called_once()
```

### 4. Using Fixtures
```python
# Reuse existing fixtures from conftest.py
@pytest.fixture
def sample_workflow():
    """Create a sample workflow for testing."""
    return {
        'id': 'test-workflow',
        'steps': ['step1', 'step2', 'step3']
    }

def test_with_fixture(sample_workflow):
    """Test using fixture."""
    assert sample_workflow['id'] == 'test-workflow'
```

### 5. Parametrized Tests
```python
@pytest.mark.parametrize("input_file,expected_status", [
    ("valid.py", "success"),
    ("invalid.txt", "error"),
    ("empty.py", "success"),
])
def test_ingest_various_files(input_file, expected_status):
    """Test ingesting various file types."""
    result = ingest(input_file)
    assert result.status == expected_status
```

### 6. Property-Based Testing
```python
from hypothesis import given, strategies as st

@given(st.text(min_size=1, max_size=1000))
def test_file_flattening_reversible(original_path):
    """Test that file flattening is reversible."""
    flattened = flatten_path(original_path)
    unflattened = unflatten_path(flattened)
    assert unflattened == original_path
```

### 7. Mocking External Dependencies
```python
from unittest.mock import Mock, patch

@patch('openai.ChatCompletion.create')
def test_llm_intent_inference_mocked(mock_openai):
    """Test LLM intent inference with mocked OpenAI API."""
    mock_openai.return_value = {'choices': [{'message': {'content': 'intent'}}]}
    result = infer_intent("code sample")
    assert result == "intent"
    mock_openai.assert_called_once()
```

---

## 📝 Documentation Requirements

### Update These Files After Testing

1. **`docs/system/CODEBASE_DASHBOARD.md`**
   - Update test count: 1615 → [NEW_COUNT]
   - Update coverage: 75% → [NEW_PERCENTAGE]%
   - Update Phase 9.1 completion: 20% → [NEW_PERCENTAGE]%

2. **`docs/testing/COVERAGE_100_ROADMAP.md`**
   - Mark Phase 9.1 tasks as complete
   - Update progress metrics
   - Add lessons learned

3. **`docs/testing/PHASE9_1_TEST_SUMMARY.md`** (NEW)
   - Create summary of tests added
   - Document coverage improvements
   - List any issues found and resolved

4. **`.github/COGNITIVE_BRAIN_STATUS_UPDATE.md`**
   - Update Phase 9.1 status
   - Add recent achievements
   - Update next steps

---

## 🔍 Self-Review Checklist (5 Iterations Required)

After completing tests, perform **5 comprehensive self-review passes**:

### Pass 1: Code Quality & Correctness
- [ ] All test functions have descriptive docstrings
- [ ] Test names follow naming conventions
- [ ] AAA pattern followed in all tests
- [ ] No syntax errors or linting warnings
- [ ] Type hints used where appropriate
- [ ] No hardcoded paths or values
- [ ] Proper error handling and assertions

### Pass 2: Testing Coverage & Completeness
- [ ] All identified uncovered lines now covered
- [ ] Edge cases tested (empty inputs, None, extremes)
- [ ] Error paths tested (exceptions, timeouts, failures)
- [ ] Integration scenarios tested
- [ ] Property-based tests where appropriate
- [ ] Coverage target reached (85% ±2%)

### Pass 3: Test Quality & Reliability
- [ ] All tests pass consistently (run 3 times)
- [ ] No flaky tests (non-deterministic behavior)
- [ ] Proper use of mocks and fixtures
- [ ] Tests are fast (<5s each, <30s for integration)
- [ ] No test interdependencies
- [ ] Cleanup handled properly (teardown)

### Pass 4: Documentation & Maintainability
- [ ] Test purpose clear from name and docstring
- [ ] Complex logic explained in comments
- [ ] Fixtures documented
- [ ] Coverage reports generated
- [ ] Test summary document created
- [ ] Dashboard updated with metrics

### Pass 5: Integration & Regression
- [ ] Full test suite passes (1615+ tests)
- [ ] No regressions in existing tests
- [ ] Coverage improved as expected
- [ ] No new security vulnerabilities
- [ ] CI/CD workflows still passing
- [ ] Documentation accurate and up-to-date

### After Each Pass
Document findings and fixes:
```markdown
## Self-Review Pass [N] Results

### Issues Found:
1. [Issue description]
2. [Issue description]

### Fixes Applied:
1. [Fix description]
2. [Fix description]

### Remaining Concerns:
1. [Concern] - [Status]

Pass [N] Complete: [YES/NO] - [# concerns remaining]
```

**DO NOT PROCEED** until all 5 passes show **0 concerns**.

---

## 🚀 Success Metrics & Exit Criteria

### Must Achieve All Of:
✅ **Coverage**: 85% ±2% (83%-87% acceptable)  
✅ **Test Count**: 1765-1815 tests (1615 + 150-200)  
✅ **Pass Rate**: 100% (all tests passing)  
✅ **No Regressions**: All 1615 existing tests still pass  
✅ **Documentation**: All required docs updated  
✅ **Self-Review**: 5 passes complete, 0 concerns  

### Nice to Have:
🎯 Coverage >85% (closer to 87%)  
🎯 Test count closer to 200 new tests  
🎯 Property-based tests for complex logic  
🎯 Performance benchmarks recorded  

---

## 🔄 If Issues Arise

### Problem: Coverage not reaching 85%
**Solution**:
1. Generate HTML coverage report: `pytest --cov=... --cov-report=html`
2. Open `htmlcov/index.html` and identify red (uncovered) lines
3. Add targeted tests for those specific lines
4. Focus on critical paths first, then edge cases

### Problem: Tests failing
**Solution**:
1. Run single failing test in verbose mode: `pytest tests/path/test_file.py::test_name -v`
2. Check error message and stack trace
3. Fix test logic or implementation
4. Verify fix with: `pytest tests/path/test_file.py::test_name -v`
5. Run full suite to check for regressions

### Problem: Flaky tests
**Solution**:
1. Identify non-deterministic behavior (random, time-based, network)
2. Use deterministic seeds, time mocking, network mocking
3. Run test 10 times: `pytest tests/path/test_file.py::test_name --count=10`
4. If still flaky, isolate and refactor

### Problem: Slow tests
**Solution**:
1. Profile slow tests: `pytest tests/ --durations=10`
2. Optimize setup/teardown
3. Use smaller test data
4. Mock expensive operations
5. Consider marking as `@pytest.mark.slow` if legitimately slow

### Problem: Token budget running low
**Solution**:
1. Prioritize critical path tests (Codex, Agents)
2. Focus on high-impact areas (low coverage modules)
3. Document remaining work in continuation prompt
4. Commit and push progress so far
5. Create detailed continuation prompt for next session

---

## 📤 Completion Steps

When Phase 9.1 is complete:

1. **Run Final Validation**
   ```bash
   pytest tests/ -v --cov=src --cov=agents --cov=scripts --cov-report=term
   ```

2. **Update Documentation**
   - Dashboard metrics
   - Coverage roadmap status
   - Test summary document

3. **Commit Changes**
   ```bash
   git add tests/ docs/
   git commit -m "feat(tests): Phase 9.1 complete - 85% coverage achieved

   - Added [NUMBER] new tests across codex, agents, MCP, integration
   - Coverage improved from 75% to [FINAL]%
   - All 1765+ tests passing
   - Self-review complete (5 passes, 0 concerns)"
   ```

4. **Create Phase 9.2 Continuation Prompt**
   - Follow same format as this prompt
   - Focus on Public API coverage (85% → 92%)
   - Include lessons learned from Phase 9.1

5. **Post Continuation Prompt as PR Comment**
   - Start with `@copilot` (no spaces)
   - Include full Phase 9.2 execution plan
   - Verify comment posted successfully

---

## 🎯 Final Checklist Before Completion

- [ ] 150-200 new tests added
- [ ] Coverage: 75% → 85% (±2%)
- [ ] All tests passing (100% pass rate)
- [ ] No regressions (1615 original tests still pass)
- [ ] Self-review: 5 passes complete, 0 concerns
- [ ] Documentation updated (Dashboard, Roadmap, Test Summary)
- [ ] Changes committed and pushed
- [ ] Phase 9.2 prompt created
- [ ] Phase 9.2 prompt posted as PR comment starting with `@copilot`

---

**Remember**: This is Phase 9.1 of a 4-phase journey to 100% coverage. Focus, quality, and thoroughness are more important than speed. Take the time to do it right.

**Good luck! 🚀**
