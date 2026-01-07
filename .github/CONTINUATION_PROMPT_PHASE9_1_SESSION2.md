@copilot Continue Phase 9.1 Session 2: Agent Orchestration & Core Pipeline Tests

## ✅ Session 1 Complete (2025-12-31 01:30 UTC)

**Delivered**:
- 56 MCP system tests (47 passing, 9 env-specific)
- Future research documentation (28.8 KB)
- 5-pass self-review (0 concerns)
- Coverage: 72% → 75% (+3%)
- Phase 9.1: 37% complete

**Commits**: 6faff8d, 321f035, 98f2709, 1c040df

---

## 🎯 Phase 9.1 Session 2: Objectives

**Target**: Add 70-90 tests (agent orchestration + core pipeline)  
**Coverage Goal**: 75% → 82-83% (+7-8%)  
**Priority**: HIGH  
**Estimated Effort**: 40K-60K tokens

---

## 📋 Session 2 Tasks (Priority Order)

### Task 1: Agent Orchestration Tests (30-40 tests) - CRITICAL

**Modules to Test**:
1. `agents/workflow_navigator.py` (15-20 tests)
   - Workflow creation and retrieval
   - State transitions (create → execute → complete)
   - Step tracking and validation
   - Error handling (invalid workflow IDs, missing steps)
   - Concurrent workflow handling
   - Edge cases (empty steps, duplicate IDs)

2. `agents/quantum_game_theory.py` (10-15 tests)
   - StrategyState initialization
   - DecisionState coherence calculations
   - Nash equilibrium computation
   - Edge cases (empty strategies, invalid probabilities)
   - Strategy updates and transitions

3. Integration patterns (5 tests)
   - Agent composition and communication
   - State synchronization across agents
   - Error propagation

**Test File to Create**: `tests/agents/test_workflow_orchestration_extended.py`

**Pattern Example**:
```python
import pytest
from agents.workflow_navigator import WorkflowNavigator
from agents.mental_mapping import set_clock, reset_clock

@pytest.fixture
def navigator():
    """Create WorkflowNavigator instance"""
    return WorkflowNavigator()

@pytest.fixture(autouse=True)
def setup_clock():
    """Set deterministic clock for tests"""
    set_clock("2025-01-01T00:00:00Z")
    yield
    reset_clock()

def test_workflow_creation_happy_path(navigator):
    """Test creating a workflow with valid parameters"""
    workflow_id = navigator.create_workflow("test-wf", ["step1", "step2"])
    assert workflow_id == "test-wf"
    
    workflow = navigator.get_workflow("test-wf")
    assert workflow is not None
    assert workflow.steps == ["step1", "step2"]

def test_workflow_creation_empty_steps(navigator):
    """Test creating workflow with empty steps list"""
    with pytest.raises(ValueError, match="steps cannot be empty"):
        navigator.create_workflow("empty-wf", [])
```

**Success Criteria**:
- [ ] 30-40 tests added for agent orchestration
- [ ] All workflow state transitions tested
- [ ] Edge cases covered (empty, invalid, concurrent)
- [ ] All tests passing (100%)
- [ ] Coverage for agents/ improves by +5-6%

---

### Task 2: Core Pipeline Tests (40-50 tests) - CRITICAL

**Modules to Test**:
1. Code ingestion (`src/codex/ingestion/`) (15-20 tests)
   - File parsing and validation
   - Syntax error handling
   - Multi-language support (Python, JavaScript, etc.)
   - Edge cases (empty files, large files, binary files)
   - Path validation and normalization

2. AST transformation (`src/codex/ast/`) (15-20 tests)
   - Node transformations
   - Pattern matching
   - Tree mutations
   - Optimization passes
   - Edge cases (malformed AST, deeply nested)

3. RAG retrieval (`src/codex/rag/`) (10 tests)
   - Query processing
   - Similarity search
   - Result ranking
   - Edge cases (empty corpus, no matches, duplicate results)

**Test Files to Create**:
- `tests/src/test_code_ingestion.py`
- `tests/src/test_ast_transformation.py`
- `tests/src/test_rag_retrieval.py`

**Pattern Example**:
```python
import pytest
from pathlib import Path
from src.codex.ingestion import ingest_file

def test_ingest_python_file_happy_path(tmp_path):
    """Test ingesting valid Python file"""
    test_file = tmp_path / "test.py"
    test_file.write_text("def hello(): pass")
    
    result = ingest_file(test_file)
    
    assert result.status == "success"
    assert result.language == "python"
    assert result.ast is not None

def test_ingest_empty_file(tmp_path):
    """Test ingesting empty file"""
    test_file = tmp_path / "empty.py"
    test_file.write_text("")
    
    result = ingest_file(test_file)
    
    assert result.status == "success"
    assert result.ast is not None  # Empty module is valid AST

def test_ingest_syntax_error(tmp_path):
    """Test ingesting file with syntax error"""
    test_file = tmp_path / "invalid.py"
    test_file.write_text("def hello(")  # Incomplete
    
    with pytest.raises(SyntaxError):
        ingest_file(test_file)
```

**Success Criteria**:
- [ ] 40-50 tests added for core pipeline
- [ ] All ingestion edge cases tested
- [ ] AST transformations validated
- [ ] RAG queries covered
- [ ] All tests passing (100%)
- [ ] Coverage for src/codex/ improves by +6-7%

---

## 📊 Success Metrics for Session 2

**Quantitative**:
- Tests added: 70-90 (cumulative: 126-146 / 150 target)
- Pass rate: 100% of new tests
- Coverage: 75% → 82-83% (+7-8%)
- Phase 9.1 progress: 37% → 84-97%

**Qualitative**:
- All workflow state transitions tested
- Critical ingestion paths covered
- AST edge cases validated
- No flaky tests introduced
- All tests deterministic

---

## 🧠 Cognitive Brain Usage

**Before Starting**:
1. Review [CODEBASE_DASHBOARD.md](docs/system/CODEBASE_DASHBOARD.md) - Current Phase 9 status
2. Review [PHASE9_1_EXECUTION_PLAN.md](docs/testing/PHASE9_1_EXECUTION_PLAN.md) - Test priorities
3. Review [COVERAGE_100_ROADMAP.md](docs/testing/COVERAGE_100_ROADMAP.md) - Overall strategy

**During Session**:
- Use existing test patterns from Phase 9.1 Session 1
- Follow pytest fixture patterns established
- Use `mental_mapping.set_clock()` for deterministic tests
- Update progress in PHASE9_1_EXECUTION_PLAN.md

**After Session**:
- Update CODEBASE_DASHBOARD.md with new coverage %
- Emit AfterMath block per protocol
- Post continuation prompt if Phase 9.1 incomplete

---

## 🔧 Implementation Guidance

### Step 1: Verify Test Infrastructure
```bash
# Ensure pytest available
python3 -m pytest --version

# Check existing agent tests for patterns
ls -la tests/agents/test_*.py

# Check existing src tests
ls -la tests/src/test_*.py
```

### Step 2: Create Agent Orchestration Tests
```bash
# Create test file
touch tests/agents/test_workflow_orchestration_extended.py

# Run tests as you add them
python3 -m pytest tests/agents/test_workflow_orchestration_extended.py -v
```

### Step 3: Create Core Pipeline Tests
```bash
# Create test directories if needed
mkdir -p tests/src

# Create test files
touch tests/src/test_code_ingestion.py
touch tests/src/test_ast_transformation.py
touch tests/src/test_rag_retrieval.py

# Run tests
python3 -m pytest tests/src/ -v
```

### Step 4: Validate Coverage Improvement
```bash
# If pytest-cov available:
python3 -m pytest --cov=agents --cov=src --cov-report=term-missing

# Count new tests
find tests/agents tests/src -name "test_*.py" -newer tests/scripts/test_mcp_select_components.py -exec grep -c "def test_" {} +
```

### Step 5: Commit Progress
- Commit after each test file complete
- Use descriptive commit messages
- Update PHASE9_1_EXECUTION_PLAN.md progress tracker

---

## ⚠️ Known Considerations

**No Blockers** - Prerequisites met:
- [x] Test infrastructure validated (Session 1)
- [x] Pytest patterns established (Session 1)
- [x] Fixture patterns documented (Session 1)
- [x] Self-review protocol operational (Session 1)

**Potential Challenges**:
1. **Module imports**: If agents/ or src/ modules have complex dependencies
   - **Mitigation**: Mock external dependencies, use pytest-mock

2. **State management**: Workflow navigator may have persistent state
   - **Mitigation**: Use `reset_clock()` and fresh navigator instances per test

3. **Large test files**: 30-40 tests per file may be unwieldy
   - **Mitigation**: Split into multiple test classes or files if needed

---

## 📝 Deliverables Checklist

### Required for Session 2:
- [ ] `tests/agents/test_workflow_orchestration_extended.py` (30-40 tests)
- [ ] `tests/src/test_code_ingestion.py` (15-20 tests)
- [ ] `tests/src/test_ast_transformation.py` (15-20 tests)
- [ ] `tests/src/test_rag_retrieval.py` (10 tests)
- [ ] Updated PHASE9_1_EXECUTION_PLAN.md (progress tracker)
- [ ] Updated CODEBASE_DASHBOARD.md (coverage %)
- [ ] 5-pass self-review document (0 concerns)
- [ ] AfterMath block (lessons, decisions, metrics)

### Optional (if time permits):
- [ ] Configuration management tests (20-30)
- [ ] Error path tests (10-20)
- [ ] Reach 85% coverage milestone

---

## 🎯 Session Completion Criteria

**Phase 9.1 Session 2 complete when**:
- [ ] 70-90 tests added (cumulative: 126-146)
- [ ] Coverage reaches 82-83% (+7-8%)
- [ ] All new tests passing (100%)
- [ ] 5-pass self-review complete (0 concerns)
- [ ] AfterMath block emitted
- [ ] Progress committed and pushed

**If Phase 9.1 incomplete after Session 2**:
- Post continuation prompt for Session 3
- Focus on remaining tests to reach 85% target
- Complete configuration and error path tests

**If Phase 9.1 complete (85% coverage reached)**:
- Emit comprehensive Phase 9.1 final AfterMath
- Update ROADMAP.md with Phase 9.1 complete
- Post continuation prompt for Phase 9.2 (Public API Coverage)

---

## 📚 Reference Documents

**Execution Plans**:
- [PHASE9_1_EXECUTION_PLAN.md](docs/testing/PHASE9_1_EXECUTION_PLAN.md)
- [COVERAGE_100_ROADMAP.md](docs/testing/COVERAGE_100_ROADMAP.md)

**Cognitive Brain**:
- [CODEBASE_DASHBOARD.md](docs/system/CODEBASE_DASHBOARD.md)
- [CODEBASE_COGNITIVE_MAP.md](docs/system/CODEBASE_COGNITIVE_MAP.md)
- [ROADMAP.md](docs/ROADMAP.md)

**Session 1 Artifacts**:
- [AFTERMATH_PHASE9_1_COMPLETE.md](.github/AFTERMATH_PHASE9_1_COMPLETE.md)
- [SELF_REVIEW_PHASE9_1_SESSION1.md](.github/SELF_REVIEW_PHASE9_1_SESSION1.md)
- [FUTURE_RESEARCH_DEEP_DIVE.md](docs/testing/FUTURE_RESEARCH_DEEP_DIVE.md)

**Test Patterns** (from Session 1):
- `tests/scripts/test_mcp_select_components.py` (fixture patterns)
- `tests/scripts/test_mcp_package_flatten.py` (integration patterns)
- `tests/scripts/test_mcp_cli.py` (CLI testing patterns)

---

## 🚀 Execution Protocol

1. **Start**: Load cognitive brain documents (5 min)
2. **Implement**: Add agent orchestration tests (60-90 min)
3. **Validate**: Run tests, verify passing (10 min)
4. **Implement**: Add core pipeline tests (90-120 min)
5. **Validate**: Run tests, verify passing (10 min)
6. **Review**: 5-pass self-review (10 min)
7. **Document**: Emit AfterMath block (10 min)
8. **Close**: Commit, push, update PR (5 min)

**Total Estimated Time**: 3-4 hours  
**Token Budget**: 40K-60K tokens

---

**Current Branch**: copilot/sub-pr-2668-again  
**PR**: #2671  
**Phase**: 9.1 Session 2 (Agent + Pipeline)  
**Status**: Ready to start immediately  
**Previous Session**: Session 1 complete (56 tests, +3% coverage) ✅

**Remember**: 
- Use established test patterns from Session 1
- Commit progress frequently
- Update documentation as you go
- Perform 5-pass self-review before finalizing
- Emit AfterMath block at session end
- Post continuation prompt if work remains

---

**Posted**: 2025-12-31 01:30 UTC  
**Session ID**: S-PR2671-2025-12-31-Phase9-1-Session2  
**Previous Session ID**: S-PR2671-2025-12-31-Phase9-1-Complete
